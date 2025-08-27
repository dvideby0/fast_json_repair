# fast_json_repair

[![PyPI version](https://badge.fury.io/py/fast-json-repair.svg)](https://pypi.org/project/fast-json-repair/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance JSON repair library for Python, powered by Rust. This is a drop-in replacement for [json_repair](https://github.com/mangiucugna/json_repair) with significant performance improvements.

## 🙏 Attribution

This library is a **Rust port** of the excellent [json_repair](https://github.com/mangiucugna/json_repair) library created by [Stefano Baccianella](https://github.com/mangiucugna). The original Python implementation is a brilliant solution for fixing malformed JSON from Large Language Models (LLMs), and this port aims to bring the same functionality with improved performance.

**All credit for the original concept, logic, and implementation goes to Stefano Baccianella.** This Rust port maintains API compatibility with the original library while leveraging Rust's performance benefits.

If you find this library useful, please also consider starring the [original json_repair repository](https://github.com/mangiucugna/json_repair).

## Features

- 📦 **Available on PyPI**: `pip install fast-json-repair`
- 🚀 **Rust Performance**: Core repair logic implemented in Rust for maximum speed
- 🔧 **Automatic Repair**: Fixes common JSON errors automatically
- 🐍 **Python Compatible**: Works with Python 3.11+
- 🔄 **Drop-in Replacement**: Compatible API with the original json_repair library
- ⚡ **Fast JSON Parsing**: Uses orjson for JSON parsing operations

## Compatibility with Original json_repair

### ✅ Included Features
- **`repair_json()`** - Main repair function with all parameters:
  - `return_objects` - Return parsed Python objects instead of JSON string
  - `skip_json_loads` - Skip initial JSON validation for better performance  
  - `ensure_ascii` - Control Unicode escaping in output
  - `indent` - Format output with indentation
- **`loads()`** - Convenience function for loading broken JSON directly to Python objects
- **All repair capabilities**:
  - Single quotes → double quotes
  - Unquoted keys → quoted keys
  - Python literals (True/False/None) → JSON literals (true/false/null)
  - Trailing commas removal
  - Missing commas addition
  - Auto-closing unclosed brackets/braces
  - Escape sequence handling
  - Unicode support

### ❌ Not Included (By Design)
- **File operations** (`load()`, `from_file()`) - Use Python's built-in file handling + repair_json()
- **CLI tool** - This is a library-only implementation
- **Streaming support** (`stream_stable` parameter) - Not yet implemented
- **Custom JSON encoder parameters** - Uses orjson's optimized defaults

### 🔄 Differences
- **Number parsing**: Unquoted numbers are parsed as numbers (not strings)
- **Performance**: 5x faster average, up to 15x for large objects
- **Dependencies**: Requires `orjson` instead of standard `json` library

## Installation

### Quick Install

```bash
pip install fast-json-repair
```

### Install from GitHub Releases

Download pre-built wheels from the [Releases page](https://github.com/dvideby0/fast_json_repair/releases):

```bash
# For macOS (Intel)
pip install https://github.com/dvideby0/fast_json_repair/releases/download/v0.1.2/fast_json_repair-0.1.2-cp311-abi3-macosx_10_12_x86_64.whl

# For macOS (Apple Silicon)  
pip install https://github.com/dvideby0/fast_json_repair/releases/download/v0.1.2/fast_json_repair-0.1.2-cp311-abi3-macosx_11_0_arm64.whl

# For Linux x86_64
pip install https://github.com/dvideby0/fast_json_repair/releases/download/v0.1.2/fast_json_repair-0.1.2-cp311-abi3-manylinux_2_17_x86_64.whl

# For Linux ARM64 (AWS Graviton)
pip install https://github.com/dvideby0/fast_json_repair/releases/download/v0.1.2/fast_json_repair-0.1.2-cp311-abi3-manylinux_2_17_aarch64.whl

# For Windows
pip install https://github.com/dvideby0/fast_json_repair/releases/download/v0.1.2/fast_json_repair-0.1.2-cp311-abi3-win_amd64.whl
```

### Build from Source

<details>
<summary>Click to expand build instructions</summary>

#### Prerequisites
- Python 3.11 or higher
- Rust toolchain (`curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`)

#### Build Steps

```bash
# Clone the repository
git clone https://github.com/dvideby0/fast_json_repair.git
cd fast_json_repair

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install build dependencies
pip install maturin orjson

# Build and install the package
maturin develop --release
```

</details>

## Usage

```python
from fast_json_repair import repair_json, loads

# Fix broken JSON
broken = "{'name': 'John', 'age': 30}"  # Single quotes
fixed = repair_json(broken)
print(fixed)  # {"age":30,"name":"John"}

# Parse directly to Python object
data = loads("{'key': 'value'}")
print(data)  # {'key': 'value'}

# Handle Unicode properly
text = "{'message': '你好世界'}"
result = repair_json(text, ensure_ascii=False)
print(result)  # {"message":"你好世界"}

# Format with indentation
formatted = repair_json("{'a': 1}", indent=2)
```

## What it repairs

- **Single quotes** → Double quotes
- **Unquoted keys** → Quoted keys
- **Python literals** → JSON equivalents (True→true, False→false, None→null)
- **Trailing commas** → Removed
- **Missing commas** → Added
- **Extra commas** → Removed
- **Unclosed brackets/braces** → Auto-closed
- **Escape sequences** → Properly handled
- **Unicode characters** → Preserved or escaped based on settings

## API Reference

### `repair_json(json_string, **kwargs)`

Repairs invalid JSON and returns valid JSON string.

**Parameters:**
- `json_string` (str): The potentially invalid JSON string to repair
- `return_objects` (bool): If True, return parsed Python object instead of JSON string
- `skip_json_loads` (bool): If True, skip initial validation for better performance
- `ensure_ascii` (bool): If True, escape non-ASCII characters in output
- `indent` (int): Number of spaces for indentation (None for compact output)

**Returns:** 
- str or object: Repaired JSON string or parsed Python object

### `loads(json_string, **kwargs)`

Repairs and parses invalid JSON string to Python object.

**Parameters:**
- `json_string` (str): The potentially invalid JSON string to repair and parse
- `**kwargs`: Additional arguments passed to repair_json

**Returns:**
- object: The parsed Python object

## Performance

This Rust-based implementation provides significant performance improvements over the pure Python original.

### Fast Path Optimization

The library automatically uses the fastest path when possible:

**Fast Path (uses `orjson` for serialization):**
- Valid JSON input
- `ensure_ascii=False` 
- `indent` is either `None` (compact) or `2`

**Fallback Path (uses stdlib `json`):**
- Valid JSON input with `ensure_ascii=True`
- Valid JSON input with `indent` values other than `None` or `2`

**Repair Path (uses Rust implementation):**
- Any invalid JSON that needs repair
- Always respects `ensure_ascii` and `indent` settings

For maximum performance with valid JSON:
```python
# Fastest - uses orjson throughout
result = repair_json(valid_json, ensure_ascii=False, indent=2)

# Slower - falls back to json.dumps for formatting
result = repair_json(valid_json, ensure_ascii=True)  # ASCII escaping
result = repair_json(valid_json, indent=4)  # Custom indentation
```

### Benchmark Results

Comprehensive comparison of fast_json_repair vs json_repair across 20 test cases (10 invalid JSON, 10 valid JSON) with both `ensure_ascii` settings:

| Test Case | fast_json_repair (ms) | json_repair (ms) | Speedup |
|-----------|----------------------|------------------|---------|
| **Invalid JSON (needs repair)** | | | |
| Simple quotes (ascii=T) | 0.018 | 0.030 | 🚀 1.7x |
| Simple quotes (ascii=F) | 0.018 | 0.029 | 🚀 1.6x |
| Medium nested (ascii=T) | 0.064 | 0.178 | 🚀 2.8x |
| Medium nested (ascii=F) | 0.062 | 0.184 | 🚀 3.0x |
| Large array 1000 (ascii=T) | 1.093 | 2.154 | 🚀 2.0x |
| Large array 1000 (ascii=F) | 1.051 | 2.160 | 🚀 2.1x |
| Deep nesting 50 (ascii=T) | 0.139 | 0.372 | 🚀 2.7x |
| Deep nesting 50 (ascii=F) | 0.133 | 0.368 | 🚀 2.8x |
| Large object 500 (ascii=T) | 1.717 | 28.194 | 🚀 **16.4x** |
| Large object 500 (ascii=F) | 1.702 | 28.570 | 🚀 **16.8x** |
| Complex mixed (ascii=T) | 0.105 | 0.365 | 🚀 3.5x |
| Complex mixed (ascii=F) | 0.102 | 0.366 | 🚀 3.6x |
| Very large 5000 (ascii=T) | 103.896 | 509.603 | 🚀 **4.9x** |
| Very large 5000 (ascii=F) | 102.053 | 506.772 | 🚀 **5.0x** |
| Long strings 10K (ascii=T) | 0.568 | 3.399 | 🚀 **6.0x** |
| Long strings 10K (ascii=F) | 0.576 | 3.430 | 🚀 **6.0x** |
| **Valid JSON (fast path)** | | | |
| Small ASCII (ascii=T) | 0.003 | 0.004 | 🚀 1.4x |
| Small ASCII (ascii=F) | 0.002 | 0.005 | 🚀 2.8x |
| Nested structure (ascii=T) | 0.006 | 0.008 | 🚀 1.3x |
| Nested structure (ascii=F) | 0.003 | 0.010 | 🚀 3.1x |
| Large array 1000 (ascii=T) | 0.747 | 0.887 | 🚀 1.2x |
| Large array 1000 (ascii=F) | 0.431 | 0.938 | 🚀 2.2x |
| Large object 500 (ascii=T) | 0.518 | 0.558 | 🚀 1.1x |
| Large object 500 (ascii=F) | 0.277 | 0.555 | 🚀 2.0x |

**Overall: 5.1x faster** across all test cases

**Key Insights:**
- 🚀 = fast_json_repair is faster (all test cases)
- **Invalid JSON repair**: 2-17x faster
- **Valid JSON with ensure_ascii=False**: 2-3x faster (uses orjson fast path)
- **Valid JSON with ensure_ascii=True**: 1.1-1.4x faster
- **Best performance gains**: Large objects (16x), long strings (6x), complex structures (5x)

### Performance Advantages

- **Large JSON documents**: 5-15x faster for documents with many keys/values
- **Deeply nested structures**: 2-3x faster with consistent performance
- **Documents with many errors**: Scales better with number of repairs needed
- **Memory efficiency**: Lower memory footprint due to Rust's zero-cost abstractions

Run `python benchmark.py` to test performance on your system.

## Differences from original json_repair

- Core repair logic implemented in Rust for performance
- Uses orjson instead of standard json library
- Numbers in unquoted values are parsed as numbers (not strings)
- Focused on string repair only (no file operations in core library)

## AWS Deployment

This library works perfectly on AWS Linux systems. Pre-built wheels are available for:
- **x86_64** (standard EC2 instances like t2, t3, m5, c5)
- **ARM64/aarch64** (Graviton instances like t4g, m6g, c6g)

### Quick Deploy to AWS

```bash
# Simply install from PyPI (works on all architectures)
pip install fast-json-repair

# The correct wheel for your architecture will be automatically selected:
# - x86_64 instances: manylinux_2_17_x86_64 wheel
# - ARM64/Graviton instances: manylinux_2_17_aarch64 wheel
```

### Building Linux Wheels (Cross-compilation from macOS)

```bash
# Install build tools
cargo install cargo-zigbuild
brew install zig

# Add Linux targets
rustup target add x86_64-unknown-linux-gnu
rustup target add aarch64-unknown-linux-gnu

# Build Linux x86_64 wheel
maturin build --release --target x86_64-unknown-linux-gnu --zig

# Build Linux ARM64 wheel (for AWS Graviton)
maturin build --release --target aarch64-unknown-linux-gnu --zig
```

### AWS Lambda Deployment

Create a Lambda layer:
```bash
mkdir -p lambda-layer/python
pip install -t lambda-layer/python/ target/wheels/fast_json_repair-*.whl orjson
cd lambda-layer && zip -r fast_json_repair_layer.zip python
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions.

## Development

```bash
# Run tests
python test_repair.py

# Build for current platform
maturin develop

# Build release wheels
maturin build --release
```

## License

MIT License (same as original json_repair)

## Credits & Acknowledgments

### Original Author
- **[Stefano Baccianella](https://github.com/mangiucugna)** - Creator of the original [json_repair](https://github.com/mangiucugna/json_repair) library
  - Original concept and algorithm design
  - Python implementation that this library is based on
  - Comprehensive test cases and edge case handling

### This Rust Port
- Performance optimization through Rust implementation
- Maintains full API compatibility with the original
- Uses [PyO3](https://pyo3.rs/) for Python bindings
- Uses [orjson](https://github.com/ijl/orjson) for fast JSON parsing

### Special Thanks
A huge thank you to Stefano Baccianella for creating json_repair and making it open source. This library wouldn't exist without the original brilliant implementation that has helped countless developers handle malformed JSON from LLMs.

If you appreciate this performance-focused port, please also show support for the [original json_repair project](https://github.com/mangiucugna/json_repair) that made it all possible.
