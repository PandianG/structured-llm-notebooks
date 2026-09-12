#!/bin/bash
# setup.sh — Automated project setup for Structured LLM Notebooks
set -e

echo "========================================"
echo "  Structured LLM Notebooks — Project Setup"
echo "========================================"

# Check for uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "✅ uv version: $(uv --version)"

# Sync dependencies
echo ""
echo "📦 Installing Python dependencies (this may take a few minutes)..."
uv sync --all-extras

echo ""
echo "📦 Installing Jupyter kernel..."
uv run python -m ipykernel install --user --name "structured-llm-notebooks" --display-name "Structured LLM Notebooks"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "   Please edit .env and add your API keys."
fi

# Check for Ollama
echo ""
if command -v ollama &> /dev/null; then
    echo "✅ Ollama found: $(ollama --version)"
    echo "   Run './scripts/ollama_setup.sh' to pull local models."
else
    echo "⚠️  Ollama not found. Install from https://ollama.com/ for zero-cost local inference."
fi

echo ""
echo "========================================"
echo "  ✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your API keys"
echo "  2. Run 'make ollama-setup' to pull local models (optional)"
echo "  3. Run 'make notebooks' to start Jupyter Lab"
echo "  4. Open notebooks/01_instructor/ to begin"
echo ""
echo "💰 Cost-saving tips:"
echo "   - Set USE_SMALL_MODEL=true in .env for 10x cheaper API calls"
echo "   - Set USE_OLLAMA=true in .env for free local inference"
echo ""
