# Publishing Guide

This guide explains how to publish `fast_json_repair` to PyPI.

## Prerequisites

1. PyPI account: https://pypi.org/account/register/
2. Test PyPI account (optional): https://test.pypi.org/account/register/
3. PyPI API token: https://pypi.org/manage/account/token/

## Step 1: Update Package Information

Edit `pyproject.toml`:
- Update author name and email
- Update version number (follow semantic versioning)
- Update GitHub URLs with your username

## Step 2: Build Wheels

### Option A: Use GitHub Actions (Recommended)

1. Push your code to GitHub
2. Create a new release/tag:
   ```bash
   git tag v0.1.0
   git push origin v0.1.0
   ```
3. GitHub Actions will automatically build wheels for all platforms
4. Download wheels from the GitHub Release

### Option B: Build Locally

Build wheels for your current platform:
```bash
maturin build --release
```

For Linux wheels (requires Docker):
```bash
# x86_64 Linux
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build \
  --release --out dist --target x86_64-unknown-linux-gnu --zig

# ARM64 Linux  
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build \
  --release --out dist --target aarch64-unknown-linux-gnu --zig
```

## Step 3: Test on Test PyPI (Optional but Recommended)

1. Upload to Test PyPI:
   ```bash
   pip install twine
   twine upload --repository testpypi dist/*
   ```

2. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ fast-json-repair
   ```

## Step 4: Publish to PyPI

### Using twine (Manual)

```bash
# Upload all wheels
twine upload dist/*

# Or if using API token
twine upload -u __token__ -p pypi-YOUR-API-TOKEN dist/*
```

### Using maturin (Direct)

```bash
# Requires MATURIN_PYPI_TOKEN environment variable
export MATURIN_PYPI_TOKEN=pypi-YOUR-API-TOKEN
maturin upload dist/*
```

### Using GitHub Actions (Automated)

1. Add your PyPI token as a GitHub secret:
   - Go to Settings → Secrets → Actions
   - Add new secret: `PYPI_API_TOKEN`

2. The workflow will automatically publish when you create a release

## Step 5: Verify Installation

After publishing, wait a few minutes and test:

```bash
pip install fast-json-repair
python -c "from fast_json_repair import repair_json; print(repair_json('{\"test\": true}'))"
```

## Version Management

- **Patch version** (0.1.x): Bug fixes, performance improvements
- **Minor version** (0.x.0): New features, backward compatible
- **Major version** (x.0.0): Breaking changes

Update version in:
- `pyproject.toml`
- `Cargo.toml`
- `python/fast_json_repair/__init__.py` (`__version__`)

## Checklist Before Publishing

- [ ] All tests pass (`python tests/test_basic.py`)
- [ ] Benchmark runs successfully (`python benchmark.py`)
- [ ] Version numbers updated
- [ ] README is up to date
- [ ] GitHub repository is public
- [ ] Wheels built for all platforms
- [ ] Tested on Test PyPI (optional)
- [ ] PyPI API token ready

## Post-Publishing

1. Create GitHub Release with changelog
2. Update README installation instructions
3. Announce on social media/forums if desired

## Troubleshooting

### "Package already exists"
- Increment version number
- Delete old builds: `rm -rf dist/ build/`

### "Invalid wheel"
- Ensure using manylinux wheels for Linux
- Check Python version compatibility

### "Module not found after install"
- Check if wheels were built correctly
- Verify package structure in wheel

## Support

For issues with publishing, check:
- PyPI documentation: https://packaging.python.org/
- Maturin documentation: https://maturin.rs/
- PyO3 documentation: https://pyo3.rs/
