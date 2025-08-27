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
    """Generate various types of broken JSON for testing."""
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
    
    return samples

def benchmark_library(repair_func, samples: List[Tuple[str, str]], runs: int = 10) -> Dict[str, List[float]]:
    """Benchmark a repair function with multiple runs."""
    results = {}
    
    for name, broken_json in samples:
        times = []
        for _ in range(runs):
            start = time.perf_counter()
            try:
                repaired = repair_func(broken_json)
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
    print(f"{'Test Case':<35} | {'Rust (ms)':<20} | {'Python (ms)':<20} | {'Speedup':<15}")
    print("-"*100)
    
    total_rust_time = 0
    total_python_time = 0
    
    for test_name in rust_results.keys():
        rust_times = [t for t in rust_results[test_name] if t != float('inf')]
        python_times = [t for t in python_results[test_name] if t != float('inf')]
        
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
            
            print(f"{test_name:<35} | {rust_str:<20} | {python_str:<20} | {speedup_str:<15}")
    
    print("-"*100)
    
    # Overall statistics
    if total_rust_time > 0 and total_python_time > 0:
        overall_speedup = total_python_time / total_rust_time
        print(f"{'TOTAL':<35} | {total_rust_time:.3f} ms{'':<11} | {total_python_time:.3f} ms{'':<11} | {overall_speedup:.2f}x faster")
        print("="*100)
        
        print(f"\n📊 Summary:")
        print(f"  • Rust implementation is {overall_speedup:.2f}x faster overall")
        print(f"  • Total time saved: {total_python_time - total_rust_time:.2f} ms")
        print(f"  • Percentage improvement: {((total_python_time - total_rust_time) / total_python_time * 100):.1f}%")

def main():
    print("🔄 Generating test samples...")
    samples = generate_broken_json_samples()
    
    print(f"📝 Running benchmarks on {len(samples)} test cases...")
    print("  Each test is run 10 times, showing mean ± std deviation")
    
    # Warm-up runs
    print("\n⏳ Warming up...")
    for _, sample in samples[:3]:
        fast_json_repair.repair_json(sample)
        json_repair.repair_json(sample)
    
    # Run benchmarks
    print("🏃 Running Rust implementation benchmarks...")
    rust_results = benchmark_library(fast_json_repair.repair_json, samples, runs=10)
    
    print("🏃 Running Python implementation benchmarks...")
    python_results = benchmark_library(json_repair.repair_json, samples, runs=10)
    
    # Print results
    print_results(rust_results, python_results)
    
    # Test correctness (ensure both produce valid JSON)
    print("\n✅ Correctness check:")
    all_correct = True
    for name, broken_json in samples[:5]:  # Check first 5 for brevity
        rust_output = fast_json_repair.repair_json(broken_json)
        python_output = json_repair.repair_json(broken_json)
        
        try:
            rust_parsed = json.loads(rust_output)
            python_parsed = json.loads(python_output)
            print(f"  ✓ {name}: Both produce valid JSON")
        except Exception as e:
            print(f"  ✗ {name}: Error - {e}")
            all_correct = False
    
    if all_correct:
        print("\n🎉 All correctness checks passed!")
    
    print("\n💡 Note: Results may vary based on system load and hardware.")
    print("   Run multiple times for more accurate measurements.")

if __name__ == "__main__":
    main()
