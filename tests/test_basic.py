"""Basic tests for fast_json_repair."""

import json
import pytest
from fast_json_repair import repair_json, loads


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


if __name__ == "__main__":
    # Run basic tests
    test_single_quotes()
    test_unquoted_keys()
    test_python_literals()
    test_trailing_commas()
    test_missing_brackets()
    test_loads_function()
    test_unicode()
    test_return_objects()
    test_empty_input()
    print("✅ All tests passed!")
