#!/usr/bin/env bash
set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================${NC}"
echo -e "${BLUE}  fast_json_repair Development Setup${NC}"
echo -e "${BLUE}======================================${NC}"
echo ""

# Check for uv
echo -e "${YELLOW}📦 Checking for uv...${NC}"
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv is not installed!${NC}"
    echo -e "${YELLOW}Installing uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo -e "${GREEN}✅ uv installed${NC}"
else
    echo -e "${GREEN}✅ uv is already installed ($(uv --version))${NC}"
fi

# Check for Rust
echo ""
echo -e "${YELLOW}🦀 Checking for Rust...${NC}"
if ! command -v cargo &> /dev/null; then
    echo -e "${RED}❌ Rust is not installed!${NC}"
    echo -e "${YELLOW}Installing Rust...${NC}"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source "$HOME/.cargo/env"
    echo -e "${GREEN}✅ Rust installed${NC}"
else
    echo -e "${GREEN}✅ Rust is already installed ($(rustc --version))${NC}"
fi

# Check for required Rust targets (optional for cross-compilation)
echo ""
echo -e "${YELLOW}🎯 Checking Rust targets...${NC}"
TARGETS=("aarch64-unknown-linux-gnu" "x86_64-unknown-linux-gnu")
for target in "${TARGETS[@]}"; do
    if rustup target list | grep -q "$target (installed)"; then
        echo -e "${GREEN}✅ $target already installed${NC}"
    else
        echo -e "${YELLOW}📥 Installing $target...${NC}"
        rustup target add "$target" || echo -e "${YELLOW}⚠️  Optional target $target skipped${NC}"
    fi
done

# Check for zig (optional for cross-compilation)
echo ""
echo -e "${YELLOW}⚡ Checking for zig (optional for cross-compilation)...${NC}"
if command -v zig &> /dev/null; then
    echo -e "${GREEN}✅ zig is installed ($(zig version))${NC}"
else
    echo -e "${YELLOW}⚠️  zig not found - cross-compilation will be limited${NC}"
    echo -e "${YELLOW}   To install zig on macOS: brew install zig${NC}"
    echo -e "${YELLOW}   To install cargo-zigbuild: cargo install cargo-zigbuild${NC}"
fi

# Create virtual environment with uv
echo ""
echo -e "${YELLOW}🐍 Creating virtual environment with uv...${NC}"
if [ -d ".venv" ]; then
    echo -e "${GREEN}✅ .venv already exists${NC}"
else
    uv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}🔌 Activating virtual environment...${NC}"
source .venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"

# Sync dependencies with uv
echo ""
echo -e "${YELLOW}📦 Syncing dependencies with uv...${NC}"
uv sync
echo -e "${GREEN}✅ Dependencies synced${NC}"

# Install development dependencies
echo ""
echo -e "${YELLOW}🛠️  Installing development dependencies...${NC}"
uv pip install maturin pytest pytest-cov black isort mypy ruff json_repair
echo -e "${GREEN}✅ Development dependencies installed${NC}"

# Build the Rust extension in development mode
echo ""
echo -e "${YELLOW}🔧 Building Rust extension (debug mode)...${NC}"
maturin develop
echo -e "${GREEN}✅ Rust extension built and installed${NC}"

# Run a quick test to verify everything works
echo ""
echo -e "${YELLOW}🧪 Running quick verification test...${NC}"
python -c "import fast_json_repair; print(fast_json_repair.repair_json(\"{'test': 'value'}\"))" && \
    echo -e "${GREEN}✅ fast_json_repair is working!${NC}" || \
    echo -e "${RED}❌ Something went wrong with the installation${NC}"

# Print success message and next steps
echo ""
echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  ✨ Setup Complete! ✨${NC}"
echo -e "${GREEN}======================================${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo -e "  1. Activate the environment: ${YELLOW}source .venv/bin/activate${NC}"
echo -e "  2. Run tests: ${YELLOW}pytest tests/${NC}"
echo -e "  3. Run benchmarks: ${YELLOW}python benchmark.py${NC}"
echo -e "  4. Build release: ${YELLOW}maturin develop --release${NC}"
echo ""
echo -e "${BLUE}VS Code:${NC}"
echo -e "  • Open this folder in VS Code"
echo -e "  • The Python interpreter should auto-detect .venv"
echo -e "  • Use ${YELLOW}Cmd+Shift+P${NC} → 'Tasks: Run Task' for build/test tasks"
echo -e "  • Press ${YELLOW}F5${NC} to debug Python tests"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo -e "  • ${YELLOW}maturin develop${NC}         - Build debug version"
echo -e "  • ${YELLOW}maturin develop --release${NC} - Build release version"
echo -e "  • ${YELLOW}maturin build --release${NC}   - Build wheel"
echo -e "  • ${YELLOW}pytest tests/ -v${NC}          - Run all tests"
echo -e "  • ${YELLOW}python benchmark.py${NC}       - Run benchmarks"
echo -e "  • ${YELLOW}cargo clippy${NC}              - Lint Rust code"
echo -e "  • ${YELLOW}cargo fmt${NC}                 - Format Rust code"
echo ""

