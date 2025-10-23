# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-10-23

### 🚀 Performance
- **MAJOR**: 19.7x faster overall performance (up from 5.1x)
- **Large objects (500+ keys)**: 67.7x faster (up from 16.4x)
- **Long strings (10K+ chars)**: 110.2x faster (up from 6.0x)
- **Very large arrays (5000+ items)**: 20.4x faster (up from 5.0x)
- Removed unnecessary key sorting in object formatting (O(n log n) → O(n))
- Added string capacity hints to reduce memory allocations

### 🐛 Bug Fixes
- Fixed key ordering in formatted JSON (now preserves insertion order instead of alphabetically sorting)
- Fixed PyO3 deprecation warning (`py.allow_threads()` → `py.detach()`)

### ✅ Testing
- Added 6 new test cases (30 total tests)
- Added regression test for key order preservation
- Added tests for missing commas, multiple trailing commas
- Added tests for invalid input type handling
- Added tests for special numeric values
- Added tests for completely invalid input handling

### 📚 Documentation
- Updated README with new benchmark results
- Added OPTIMIZATION_REVIEW.md with detailed performance analysis
- Enhanced development workflow documentation

### 🛠️ Development
- Added `uv` support for fast dependency management
- Added comprehensive VS Code workspace configuration (33 tasks)
- Added automated `setup.sh` script
- Added `.editorconfig` for consistent code formatting
- Added `pyproject.toml` tool configurations (black, isort, pytest, ruff)

### 🔄 Changes
- Minimum supported versions unchanged (Python 3.11-3.14, Rust 1.70+)
- No breaking API changes - fully backward compatible with 0.1.x

## [0.1.3] - Previous Release

See git history for earlier changes.

---

[0.2.0]: https://github.com/dvideby0/fast_json_repair/compare/v0.1.3...v0.2.0

