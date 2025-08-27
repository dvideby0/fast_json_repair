"""Comprehensive test suite for fast_json_repair."""

import json
import re
from fast_json_repair import repair_json, loads


# ============================================================================
# BASIC TESTS
# ============================================================================

def test_single_quotes():
    """Test conversion of single quotes to double quotes."""
    result = repair_json("{'key': 'value'}")
    assert json.loads(result) == {"key": "value"}


def test_unquoted_keys():
    """Test handling of unquoted keys."""
    result = repair_json("{key: 'value'}")
    assert json.loads(result) == {"key": "value"}


def test_python_literals():
    """Test conversion of Python literals."""
    result = repair_json("{a: True, b: False, c: None}")
    assert json.loads(result) == {"a": True, "b": False, "c": None}


def test_trailing_commas():
    """Test removal of trailing commas."""
    result = repair_json('{"a": 1, "b": 2,}')
    assert json.loads(result) == {"a": 1, "b": 2}


def test_missing_brackets():
    """Test auto-closing of missing brackets."""
    result = repair_json('{"a": [1, 2')
    parsed = json.loads(result)
    assert parsed == {"a": [1, 2]}


def test_loads_function():
    """Test the loads convenience function."""
    result = loads("{'key': 'value'}")
    assert result == {"key": "value"}


def test_unicode():
    """Test Unicode handling."""
    result = repair_json("{'msg': '你好'}", ensure_ascii=False)
    assert '你好' in result
    
    result_ascii = repair_json("{'msg': '你好'}", ensure_ascii=True)
    assert '\\u' in result_ascii


def test_return_objects():
    """Test return_objects parameter."""
    result = repair_json("{'key': 'value'}", return_objects=True)
    assert isinstance(result, dict)
    assert result == {"key": "value"}


def test_empty_input():
    """Test handling of empty input."""
    assert repair_json("") == "null"
    assert repair_json("   ") == "null"


# ============================================================================
# EDGE CASE TESTS
# ============================================================================

def test_ensure_ascii_true():
    """Test ensure_ascii=True escapes non-ASCII characters."""
    result = repair_json('{"msg": "你好"}', ensure_ascii=True)
    assert '\\u' in result
    assert '你好' not in result
    # Verify it's valid JSON
    parsed = json.loads(result)
    assert parsed['msg'] == '你好'


def test_ensure_ascii_false():
    """Test ensure_ascii=False preserves non-ASCII characters."""
    result = repair_json('{"msg": "你好"}', ensure_ascii=False)
    assert '你好' in result
    assert '\\u' not in result
    parsed = json.loads(result)
    assert parsed['msg'] == '你好'


def test_indent_various():
    """Test various indent values."""
    obj = '{"a": 1, "b": {"c": 2}}'
    
    # No indent (compact)
    result = repair_json(obj, indent=None)
    assert '\n' not in result
    
    # Indent = 2
    result = repair_json(obj, indent=2)
    assert '\n' in result
    assert '  "a"' in result or '  "b"' in result
    
    # Indent = 4
    result = repair_json(obj, indent=4)
    assert '\n' in result
    assert '    "a"' in result or '    "b"' in result


def test_preserve_key_order():
    """Test that key order is preserved (not sorted)."""
    # Create JSON with specific key order
    input_json = '{"z": 1, "a": 2, "m": 3}'
    result = repair_json(input_json)
    
    # Parse and verify order is preserved
    key_pattern = re.findall(r'"([^"]+)":', result)
    assert key_pattern == ['z', 'a', 'm'], f"Expected ['z', 'a', 'm'], got {key_pattern}"


def test_very_deep_nesting():
    """Test handling of very deep nesting."""
    # Create deeply nested JSON (100 levels)
    deep_json = '{"a":' * 100 + '1' + '}' * 100
    result = repair_json(deep_json, return_objects=True)
    assert result is not None
    
    # Verify structure
    current = result
    for _ in range(100):
        assert isinstance(current, dict)
        assert 'a' in current
        current = current['a']
    assert current == 1


def test_max_nesting_exceeded():
    """Test that exceeding max nesting returns null."""
    # Create JSON deeper than max_depth (1000)
    very_deep_json = '{"a":' * 1001 + '1' + '}' * 1001
    # Use skip_json_loads=True to avoid Python's recursion limit in json.dumps
    result = repair_json(very_deep_json, skip_json_loads=True)
    assert result == "null"


def test_invalid_numbers():
    """Test handling of invalid/edge case numbers."""
    # Infinity and NaN should become null
    test_cases = [
        ('{"val": 1e999}', None),  # Overflow to infinity
        ('{"val": -1e999}', None),  # Negative infinity
        ('{"val": 0.0}', 0.0),
        ('{"val": -0.0}', -0.0),
        ('{"val": 1.23e-10}', 1.23e-10),
    ]
    
    for input_str, expected in test_cases:
        result = repair_json(input_str, return_objects=True)
        if expected is None:
            assert result['val'] is None
        else:
            assert result['val'] == expected


def test_control_characters():
    """Test handling of control characters."""
    # Control characters should be escaped
    input_json = '{"text": "line1\\nline2\\ttab\\rcarriage"}'
    result = repair_json(input_json)
    parsed = json.loads(result)
    assert parsed['text'] == "line1\nline2\ttab\rcarriage"
    
    # Ensure control chars are properly escaped in output
    assert '\\n' in result or '\n' not in result.replace('\\n', '')


def test_unicode_escapes():
    """Test handling of unicode escape sequences."""
    test_cases = [
        ('{"text": "\\u0041"}', 'A'),  # Valid unicode
        ('{"text": "\\u4e2d\\u6587"}', '中文'),  # Chinese characters
        ('{"text": "\\u00e9"}', 'é'),  # Accented character
    ]
    
    for input_str, expected in test_cases:
        result = repair_json(input_str, return_objects=True)
        assert result['text'] == expected


def test_mixed_quotes_complex():
    """Test complex mixed quote scenarios."""
    test_cases = [
        ("{'a': \"b's value\"}", {"a": "b's value"}),
        ('{"a": "b\\"s value"}', {"a": 'b"s value'}),
        ("{'a': 'b\\'s value'}", {"a": "b's value"}),
    ]
    
    for input_str, expected in test_cases:
        result = repair_json(input_str, return_objects=True)
        assert result == expected


def test_empty_containers():
    """Test empty arrays and objects."""
    assert repair_json('[]', return_objects=True) == []
    assert repair_json('{}', return_objects=True) == {}
    assert repair_json('[[], {}, [{}]]', return_objects=True) == [[], {}, [{}]]


def test_skip_json_loads_performance():
    """Test skip_json_loads parameter."""
    # Valid JSON with skip_json_loads=True should still work
    valid_json = '{"valid": true}'
    result = repair_json(valid_json, skip_json_loads=True)
    assert json.loads(result) == {"valid": True}
    
    # Invalid JSON should be repaired
    invalid_json = "{'invalid': True}"
    result = repair_json(invalid_json, skip_json_loads=True)
    assert json.loads(result) == {"invalid": True}


def test_large_array():
    """Test handling of large arrays."""
    # Create array with 1000 elements
    large_array = '[' + ','.join(str(i) for i in range(1000)) + ']'
    result = repair_json(large_array, return_objects=True)
    assert len(result) == 1000
    assert result[0] == 0
    assert result[999] == 999


def test_malformed_escapes():
    """Test handling of malformed escape sequences."""
    test_cases = [
        (r'{"text": "\x41"}', {"text": "x41"}),  # Invalid hex escape - \x is treated as literal
        (r'{"text": "\u"}', {"text": "\\u"}),  # Incomplete unicode - preserved as literal
        (r'{"text": "\u00"}', {"text": "\\u00"}),  # Incomplete unicode - preserved as literal
        (r'{"text": "\u00G1"}', {"text": "\\u00G1"}),  # Invalid hex digit - preserved as literal
    ]
    
    for input_str, expected in test_cases:
        result = repair_json(input_str, return_objects=True)
        assert result == expected, f"For input {input_str}: expected {expected}, got {result}"


def test_numeric_strings():
    """Test that numeric-looking strings are handled correctly."""
    test_cases = [
        ('{"val": "123"}', {"val": "123"}),  # String should stay string
        ("{val: '123'}", {"val": "123"}),  # Single quoted string
        ("{val: 123}", {"val": 123}),  # Actual number
        ('{val: "12.34e5"}', {"val": "12.34e5"}),  # Scientific notation string
        ('{val: 12.34e5}', {"val": 12.34e5}),  # Scientific notation number
    ]
    
    for input_str, expected in test_cases:
        result = repair_json(input_str, return_objects=True)
        assert result == expected


# ============================================================================
# MAIN TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tests and report results."""
    import sys
    import traceback
    
    # Collect all test functions
    test_functions = [
        # Basic tests
        test_single_quotes,
        test_unquoted_keys,
        test_python_literals,
        test_trailing_commas,
        test_missing_brackets,
        test_loads_function,
        test_unicode,
        test_return_objects,
        test_empty_input,
        # Edge case tests
        test_ensure_ascii_true,
        test_ensure_ascii_false,
        test_indent_various,
        test_preserve_key_order,
        test_very_deep_nesting,
        test_max_nesting_exceeded,
        test_invalid_numbers,
        test_control_characters,
        test_unicode_escapes,
        test_mixed_quotes_complex,
        test_empty_containers,
        test_skip_json_loads_performance,
        test_large_array,
        test_malformed_escapes,
        test_numeric_strings,
    ]
    
    print("=" * 60)
    print("Running fast_json_repair test suite")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_func.__name__}: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
            failed += 1
        except Exception as e:
            print(f"❌ {test_func.__name__}: Unexpected error: {e}")
            traceback.print_exc()
            failed += 1
    
    print("=" * 60)
    if failed == 0:
        print(f"✅ All {passed} tests passed!")
        return 0
    else:
        print(f"❌ {failed}/{passed + failed} tests failed")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(run_all_tests())
