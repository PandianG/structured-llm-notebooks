#!/bin/bash
# ollama_setup.sh — Pull local models for zero-cost mode
set -e

echo "========================================"
echo "  Ollama — Pulling Local Models"
echo "========================================"

if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed."
    echo "   Install from: https://ollama.com/"
    exit 1
fi

MODELS=(
    "llama3.1"
    "qwen2.5"
    "phi4"
    "gemma2:9b"
)

for model in "${MODELS[@]}"; do
    echo ""
    echo "📥 Pulling $model..."
    ollama pull "$model"
    echo "✅ $model ready"
done

echo ""
echo "========================================"
echo "  ✅ All Local Models Ready!"
echo "========================================"
echo ""
echo "Set USE_OLLAMA=true in .env to use these models."
echo ""
