#!/usr/bin/env python3
"""Performance benchmark comparing fast_json_repair (Rust) with original json_repair (Python)."""

import time
import json
import statistics
from typing import List, Tuple, Dict, Any
import random
import string

# Import both libraries
import fast_json_repair
import json_repair

def generate_broken_json_samples() -> List[Tuple[str, str]]:
    """Generate various types of broken AND valid JSON for comprehensive testing."""
    samples = []
    
    # 1. Simple single quote issues (small)
    samples.append((
        "Simple quotes",
        "{'name': 'John', 'age': 30, 'city': 'New York'}"
    ))
    
    # 2. Medium nested structure with multiple issues
    medium_nested = """
    {
        'users': [
            {'id': 1, 'name': 'Alice', active: True, 'tags': ['admin', 'user']},
            {'id': 2, 'name': 'Bob', active: False, 'tags': ['user']},
            {'id': 3, 'name': 'Charlie', active: None, 'tags': ['moderator', 'user']}
        ],
        'metadata': {
            'total': 3,
            'page': 1,
            last_updated: '2024-01-01'
        }
    }
    """
    samples.append(("Medium nested", medium_nested))
    
    # 3. Large array with trailing commas
    large_array = "[" + ",".join([f"{i}" for i in range(1000)]) + ",]"
    samples.append(("Large array (1000 items)", large_array))
    
    # 4. Deep nesting with missing brackets
    def create_deep_nested(depth: int) -> str:
        result = "{"
        for i in range(depth):
            result += f"'level_{i}': {{"
        result += "'data': 'deep'"
        # Intentionally missing closing brackets
        return result
    
    samples.append(("Deep nesting (50 levels)", create_deep_nested(50)))
    
    # 5. Large object with many keys
    large_obj_items = []
    for i in range(500):
        key = f"key_{i}"
        value = random.choice([
            f"'string_{i}'",
            str(random.randint(0, 1000)),
            "True", "False", "None"
        ])
        large_obj_items.append(f"{key}: {value}")
    large_obj = "{" + ", ".join(large_obj_items) + ",}"
    samples.append(("Large object (500 keys)", large_obj))
    
    # 6. Complex mixed issues
    complex_json = """
    {
        users: [
            {id: 1, name: 'Alice', email: "alice@example.com", active: True, score: 95.5,},
            {id: 2, name: 'Bob', email: "bob@example.com", active: False, score: 87.3,},
            {id: 3, name: 'Charlie', email: "charlie@example.com", active: True, score: 92.1,}
        ],
        'settings': {
            'theme': 'dark',
            notifications: {
                email: True,
                push: False,
                sms: None
            },
            'preferences': [
                'option1',
                'option2',
                'option3',
            ]
        },
        metadata: {
            version: '1.0.0',
            'timestamp': 1234567890,
            tags: ['production', 'v1', 'stable',],
        }
    """
    samples.append(("Complex mixed issues", complex_json))
    
    # 7. Very large JSON with multiple issues (stress test)
    very_large_items = []
    for i in range(5000):
        item = {
            'id': i,
            'name': ''.join(random.choices(string.ascii_letters, k=10)),
            'value': random.random(),
            'active': random.choice(['True', 'False', 'None']),
            'tags': [f"'tag_{j}'" for j in range(random.randint(1, 5))]
        }
        # Convert to broken JSON string
        item_str = str(item).replace("'", "")
        very_large_items.append(item_str)
    very_large = "[" + ", ".join(very_large_items) + ",]"
    samples.append(("Very large array (5000 items)", very_large))
    
    # 8. Unicode and special characters
    unicode_json = """
    {
        'message': '你好世界',
        'emoji': '😀🎉🚀',
        'special': 'Line\\nbreak\\ttab',
        data: {
            'japanese': '日本語',
            'korean': '한국어',
            'arabic': 'العربية',
            numbers: [1, 2, 3,],
        }
    }
    """
    samples.append(("Unicode and special chars", unicode_json))
    
    # 9. Extremely long string values
    long_string = ''.join(random.choices(string.ascii_letters + string.digits, k=10000))
    long_string_json = f"{{'data': '{long_string}', 'count': 10000,}}"
    samples.append(("Long string values (10K chars)", long_string_json))
    
    # 10. Many missing commas
    no_commas = """
    {
        "a": 1 "b": 2 "c": 3 "d": 4 "e": 5
        "f": 6 "g": 7 "h": 8 "i": 9 "j": 10
        "k": {"nested": true "value": 42}
        "l": [1 2 3 4 5]
    }
    """
    samples.append(("Missing commas", no_commas))
    
    # ===== VALID JSON SAMPLES (test fast path performance) =====
    
    # 11. Valid small ASCII JSON
    valid_small = json.dumps({
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "active": True
    })
    samples.append(("VALID: Small ASCII", valid_small))
    
    # 12. Valid small Unicode JSON
    valid_unicode = json.dumps({
        "name": "张三",
        "message": "你好世界",
        "emoji": "😀🎉",
        "japanese": "こんにちは"
    })
    samples.append(("VALID: Small Unicode", valid_unicode))
    
    # 13. Valid nested structure
    valid_nested = json.dumps({
        "users": [
            {"id": 1, "name": "Alice", "active": True, "score": 95.5},
            {"id": 2, "name": "Bob", "active": False, "score": 87.3}
        ],
        "metadata": {
            "total": 2,
            "page": 1,
            "last_updated": "2024-01-01T00:00:00Z"
        }
    })
    samples.append(("VALID: Nested structure", valid_nested))
    
    # 14. Valid large array
    valid_large_arr = json.dumps([
        {"id": i, "value": f"item_{i}", "active": i % 2 == 0}
        for i in range(1000)
    ])
    samples.append(("VALID: Large array (1000)", valid_large_arr))
    
    # 15. Valid deep nesting
    def create_valid_deep(depth):
        if depth == 0:
            return {"value": "deep"}
        return {"level": create_valid_deep(depth - 1)}
    valid_deep = json.dumps(create_valid_deep(50))
    samples.append(("VALID: Deep nesting (50)", valid_deep))
    
    # 16. Valid large object
    valid_large_obj = json.dumps({
        f"key_{i}": {
            "value": f"value_{i}",
            "index": i,
            "active": i % 2 == 0
        }
        for i in range(500)
    })
    samples.append(("VALID: Large object (500)", valid_large_obj))
    
    # 17. Valid very large array
    valid_very_large = json.dumps(list(range(5000)))
    samples.append(("VALID: Very large (5000)", valid_very_large))
    
    # 18. Valid Unicode-heavy content
    valid_unicode_heavy = json.dumps({
        "chinese": "这是一个很长的中文句子，包含许多汉字。",
        "japanese": "これは日本語の長い文章です。",
        "korean": "이것은 긴 한국어 문장입니다.",
        "arabic": "هذه جملة عربية طويلة",
        "emojis": "😀😃😄😁😆😅🤣😂🙂🙃😉😊",
        "mixed": "Hello 世界 🌍"
    })
    samples.append(("VALID: Unicode-heavy", valid_unicode_heavy))
    
    # 19. Valid long strings
    valid_long_str = json.dumps({
        "description": "x" * 10000,
        "metadata": {"length": 10000}
    })
    samples.append(("VALID: Long string (10K)", valid_long_str))
    
    # 20. Valid mixed types
    valid_mixed = json.dumps({
        "string": "test",
        "number": 42.5,
        "boolean": True,
        "null": None,
        "array": [1, 2, 3],
        "object": {"nested": True}
    })
    samples.append(("VALID: Mixed types", valid_mixed))
    
    return samples

def benchmark_library(repair_func, samples: List[Tuple[str, str]], runs: int = 10, ensure_ascii: bool = True) -> Dict[str, List[float]]:
    """Benchmark a repair function with multiple runs."""
    results = {}
    
    for name, broken_json in samples:
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            try:
                repaired = repair_func(broken_json, ensure_ascii=ensure_ascii)
                # Verify it's valid JSON
                json.loads(repaired)
            except Exception as e:
                print(f"  ⚠️  Error in {name}: {e}")
                times.append(float('inf'))
                continue
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds
        
        results[name] = times
    
    return results

def print_results(rust_results: Dict[str, List[float]], python_results: Dict[str, List[float]]):
    """Print benchmark results in a nice table format."""
    print("\n" + "="*100)
    print("PERFORMANCE BENCHMARK: fast_json_repair (Rust) vs json_repair (Python)")
    print("="*100)
    
    # Separate valid and invalid JSON tests
    invalid_tests = {k: v for k, v in rust_results.items() if not k.startswith("VALID:")}
    valid_tests = {k: v for k, v in rust_results.items() if k.startswith("VALID:")}
    
    total_rust_time = 0
    total_python_time = 0
    
    # Helper function to print a section
    def print_section(tests, section_name):
        nonlocal total_rust_time, total_python_time
        
        if not tests:
            return
            
        print(f"\n📍 {section_name}:")
        print("-"*100)
        print(f"{'Test Case':<35} | {'Rust (ms)':<20} | {'Python (ms)':<20} | {'Speedup':<15}")
        print("-"*100)
        
        for test_name in tests.keys():
            rust_times = [t for t in tests[test_name] if t != float('inf')]
            python_times = [t for t in python_results[test_name] if t != float('inf')] if python_results and test_name in python_results else []
            
            if rust_times and python_times:
                rust_mean = statistics.mean(rust_times)
                rust_std = statistics.stdev(rust_times) if len(rust_times) > 1 else 0
                python_mean = statistics.mean(python_times)
                python_std = statistics.stdev(python_times) if len(python_times) > 1 else 0
                speedup = python_mean / rust_mean if rust_mean > 0 else 0
                
                total_rust_time += rust_mean
                total_python_time += python_mean
                
                rust_str = f"{rust_mean:.3f} ± {rust_std:.3f}"
                python_str = f"{python_mean:.3f} ± {python_std:.3f}"
                speedup_str = f"{speedup:.2f}x faster"
                
                # Color code based on speedup
                if speedup >= 2:
                    speedup_str = f"🚀 {speedup_str}"
                elif speedup >= 1.5:
                    speedup_str = f"⚡ {speedup_str}"
                
                # Clean up test name for display
                display_name = test_name.replace("VALID: ", "")
                print(f"{display_name:<35} | {rust_str:<20} | {python_str:<20} | {speedup_str:<15}")
            elif rust_times:
                # Only Rust results available
                rust_mean = statistics.mean(rust_times)
                rust_std = statistics.stdev(rust_times) if len(rust_times) > 1 else 0
                rust_str = f"{rust_mean:.3f} ± {rust_std:.3f}"
                display_name = test_name.replace("VALID: ", "")
                print(f"{display_name:<35} | {rust_str:<20} | {'N/A':<20} | {'N/A':<15}")
                total_rust_time += rust_mean
    
    # Print both sections
    print_section(invalid_tests, "INVALID JSON (needs repair)")
    print_section(valid_tests, "VALID JSON (fast path)")
    
    print("\n" + "-"*100)
    
    # Overall statistics
    if total_rust_time > 0 and total_python_time > 0:
        overall_speedup = total_python_time / total_rust_time
        print(f"{'TOTAL':<35} | {total_rust_time:.3f} ms{'':<11} | {total_python_time:.3f} ms{'':<11} | {overall_speedup:.2f}x faster")
        print("="*100)
        
        print(f"\n📊 Summary:")
        print(f"  • Rust implementation is {overall_speedup:.2f}x faster overall")
        print(f"  • Total time saved: {total_python_time - total_rust_time:.2f} ms")
        print(f"  • Percentage improvement: {((total_python_time - total_rust_time) / total_python_time * 100):.1f}%")

def print_combined_results(rust_ascii_true, rust_ascii_false, python_ascii_true, python_ascii_false, samples):
    """Print all benchmark results in a single unified table."""
    print("\n" + "=" * 120)
    print("COMPREHENSIVE BENCHMARK RESULTS: fast_json_repair vs json_repair")
    print("=" * 120)
    
    # Table header
    print(f"{'Test Case':<45} {'fast_json_repair (ms)':<20} {'json_repair (ms)':<20} {'Speedup':<15}")
    print("-" * 120)
    
    total_rust_time = 0
    total_python_time = 0
    row_count = 0
    
    for test_name, _ in samples:
        # Clean up test name
        display_name = test_name.replace("VALID: ", "")
        
        # Test with ensure_ascii=True
        if test_name in rust_ascii_true:
            rust_times_true = [t for t in rust_ascii_true[test_name] if t != float('inf')]
            python_times_true = [t for t in python_ascii_true.get(test_name, []) if t != float('inf')]
            
            if rust_times_true:
                rust_mean_true = statistics.median(rust_times_true)
                rust_str_true = f"{rust_mean_true:.3f}"
                total_rust_time += rust_mean_true
                
                if python_times_true:
                    python_mean_true = statistics.median(python_times_true)
                    python_str_true = f"{python_mean_true:.3f}"
                    speedup_true = python_mean_true / rust_mean_true if rust_mean_true > 0 else 0
                    total_python_time += python_mean_true
                    
                    # Simple emoji: faster or slower
                    if speedup_true >= 1.0:
                        speedup_str_true = f"🚀 {speedup_true:.2f}x"
                    else:
                        speedup_str_true = f"🐌 {speedup_true:.2f}x"
                else:
                    python_str_true = "N/A"
                    speedup_str_true = "N/A"
                
                print(f"{display_name + ' (ascii=T)':<45} {rust_str_true:<20} {python_str_true:<20} {speedup_str_true:<15}")
                row_count += 1
        
        # Test with ensure_ascii=False
        if test_name in rust_ascii_false:
            rust_times_false = [t for t in rust_ascii_false[test_name] if t != float('inf')]
            python_times_false = [t for t in python_ascii_false.get(test_name, []) if t != float('inf')]
            
            if rust_times_false:
                rust_mean_false = statistics.median(rust_times_false)
                rust_str_false = f"{rust_mean_false:.3f}"
                total_rust_time += rust_mean_false
                
                if python_times_false:
                    python_mean_false = statistics.median(python_times_false)
                    python_str_false = f"{python_mean_false:.3f}"
                    speedup_false = python_mean_false / rust_mean_false if rust_mean_false > 0 else 0
                    total_python_time += python_mean_false
                    
                    # Simple emoji: faster or slower
                    if speedup_false >= 1.0:
                        speedup_str_false = f"🚀 {speedup_false:.2f}x"
                    else:
                        speedup_str_false = f"🐌 {speedup_false:.2f}x"
                else:
                    python_str_false = "N/A"
                    speedup_str_false = "N/A"
                
                print(f"{display_name + ' (ascii=F)':<45} {rust_str_false:<20} {python_str_false:<20} {speedup_str_false:<15}")
                row_count += 1
        
        # Add separator between different test cases for readability
        if row_count % 2 == 0:
            print()
    
    # Summary
    print("-" * 120)
    if total_python_time > 0:
        overall_speedup = total_python_time / total_rust_time if total_rust_time > 0 else 0
        print(f"{'TOTAL':<45} {total_rust_time:.1f} ms{'':<12} {total_python_time:.1f} ms{'':<12} {overall_speedup:.2f}x")
        print("=" * 120)
        
        print(f"\n📊 Summary:")
        print(f"  • fast_json_repair is {overall_speedup:.2f}x faster overall")
        print(f"  • Total time saved: {total_python_time - total_rust_time:.1f} ms")
        print(f"  • Percentage improvement: {((total_python_time - total_rust_time) / total_python_time * 100):.1f}%")
    else:
        print(f"{'TOTAL':<45} {total_rust_time:.1f} ms")
        print("=" * 120)
    
    print("\n📝 Legend:")
    print("  • (ascii=T) = ensure_ascii=True")
    print("  • (ascii=F) = ensure_ascii=False")  
    print("  • 🚀 = fast_json_repair is faster")
    print("  • 🐌 = fast_json_repair is slower")
    print("  • Speedup shows how many times faster fast_json_repair is vs json_repair")

def main():
    print("🔄 Generating test samples...")
    samples = generate_broken_json_samples()
    
    invalid_count = sum(1 for name, _ in samples if not name.startswith("VALID:"))
    valid_count = sum(1 for name, _ in samples if name.startswith("VALID:"))
    print(f"📝 Running benchmarks on {len(samples)} test cases:")
    print(f"   - {invalid_count} invalid JSON (needs repair)")
    print(f"   - {valid_count} valid JSON (tests fast path)")
    print("  Each test is run 10 times, showing median time")
    
    # Warm-up runs
    print("\n⏳ Warming up...")
    for _, sample in samples[:3]:
        fast_json_repair.repair_json(sample)
        try:
            json_repair.repair_json(sample)
        except:
            pass
    
    # Run all benchmarks
    print("\n🏃 Running benchmarks...")
    print("  • fast_json_repair with ensure_ascii=True")
    rust_results_ascii_true = benchmark_library(fast_json_repair.repair_json, samples, runs=10, ensure_ascii=True)
    
    print("  • fast_json_repair with ensure_ascii=False")
    rust_results_ascii_false = benchmark_library(fast_json_repair.repair_json, samples, runs=10, ensure_ascii=False)
    
    print("  • json_repair with ensure_ascii=True")
    python_results_ascii_true = {}
    try:
        python_results_ascii_true = benchmark_library(json_repair.repair_json, samples, runs=10, ensure_ascii=True)
    except:
        print("    ⚠️  json_repair not available")
    
    print("  • json_repair with ensure_ascii=False")
    python_results_ascii_false = {}
    try:
        python_results_ascii_false = benchmark_library(json_repair.repair_json, samples, runs=10, ensure_ascii=False)
    except:
        print("    ⚠️  json_repair not available")
    
    # Print combined results in a single table
    print_combined_results(
        rust_results_ascii_true, 
        rust_results_ascii_false,
        python_results_ascii_true,
        python_results_ascii_false,
        samples
    )

if __name__ == "__main__":
    main()
