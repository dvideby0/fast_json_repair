# Deployment Guide for AWS Linux

This guide explains how to deploy `fast_json_repair` to AWS Linux systems.

## Prerequisites

- Python 3.11+ on your AWS instance
- pip installed

## Option 1: Build Linux Wheel Locally (Recommended)

### Using Docker (No Linux machine required)

1. Install Docker on your development machine
2. Build the Linux wheel:

```bash
# Build manylinux wheel that works on most Linux distributions
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build \
  --release \
  --out dist \
  --target x86_64-unknown-linux-gnu \
  --manylinux 2014

# For ARM64 AWS instances (Graviton)
docker run --rm -v $(pwd):/io ghcr.io/pyo3/maturin build \
  --release \
  --out dist \
  --target aarch64-unknown-linux-gnu \
  --manylinux 2014
```

3. Upload the wheel from `dist/` to your AWS instance
4. Install on AWS:

```bash
pip install fast_json_repair-*.whl orjson
```

## Option 2: Build on AWS Instance

### Install build dependencies on AWS Linux 2/2023:

```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source $HOME/.cargo/env

# Install Python development headers
sudo yum install python3-devel gcc -y

# Install maturin
pip install maturin orjson
```

### Build and install:

```bash
# Clone your repository
git clone https://github.com/dvideby0/fast_json_repair.git
cd fast_json_repair

# Build and install
maturin develop --release
```

## Option 3: Use Pre-built Wheels from CI/CD

If you set up GitHub Actions (see `.github/workflows/build.yml`):

1. Push a tag to trigger the build:
```bash
git tag v0.1.0
git push origin v0.1.0
```

2. Download the Linux wheel from GitHub Releases
3. Install on AWS:
```bash
pip install fast_json_repair-0.1.0-cp311-abi3-manylinux_2_17_x86_64.whl orjson
```

## Option 4: Include in requirements.txt (After PyPI publish)

Once published to PyPI with Linux wheels:

```txt
# requirements.txt
fast_json_repair>=0.1.0
orjson>=3.10.0
```

Then deploy normally:
```bash
pip install -r requirements.txt
```

## Docker Deployment

For containerized deployments, add to your Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install build dependencies (only needed if building from source)
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# If using pre-built wheel
COPY dist/fast_json_repair-*.whl /tmp/
RUN pip install /tmp/fast_json_repair-*.whl orjson

# Or if installing from source
COPY . /app
WORKDIR /app
RUN pip install maturin && maturin build --release && \
    pip install target/wheels/*.whl orjson
```

## AWS Lambda Deployment

For Lambda functions:

1. Build a manylinux wheel (Option 1)
2. Create a Lambda layer:

```bash
mkdir -p lambda-layer/python
pip install -t lambda-layer/python/ dist/fast_json_repair-*.whl orjson
cd lambda-layer
zip -r fast_json_repair_layer.zip python
```

3. Upload the layer to AWS Lambda
4. Attach the layer to your Lambda function

## Verification

Test the installation on your AWS instance:

```python
from fast_json_repair import repair_json

# Test repair
broken = "{'key': 'value'}"
fixed = repair_json(broken)
print(f"Repaired: {fixed}")
```

## Architecture Compatibility

| AWS Instance Type | Architecture | Wheel Target |
|------------------|--------------|--------------|
| t2, t3, m5, c5   | x86_64      | x86_64-unknown-linux-gnu |
| t4g, m6g, c6g    | ARM64       | aarch64-unknown-linux-gnu |

## Troubleshooting

### "No module named 'fast_json_repair._fast_json_repair'"
- Ensure you're using the correct wheel for your architecture
- Check Python version compatibility (requires 3.11+)

### "GLIBC version not found"
- Use manylinux2014 wheels for better compatibility
- Or build directly on the target system

### Performance on AWS

For best performance on AWS:
- Use larger instance types for JSON processing workloads
- Consider using ARM64 (Graviton) instances for better price/performance
- Enable SSE4.2 optimizations if available (x86_64)
