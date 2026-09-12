#!/bin/bash
# local_finetune.sh — Optional local fine-tuning setup with QLoRA
# Requires: NVIDIA GPU with 16GB+ VRAM (RTX 3090/4090 recommended)

set -e

echo "========================================"
echo "  Local Fine-tuning Setup (Optional)"
echo "========================================"

# Check for GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "❌ nvidia-smi not found. No NVIDIA GPU detected."
    echo "   For CPU-only fine-tuning, use llama.cpp quantization (very slow)."
    echo "   For cloud GPU, see scripts/runpod_setup.md"
    exit 1
fi

echo "✅ GPU detected:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader

# Check VRAM
VRAM=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits | head -n1 | awk '{print int($1)}')
if [ "$VRAM" -lt 16000 ]; then
    echo "⚠️  GPU has less than 16GB VRAM. Fine-tuning may fail or be very slow."
    echo "   Recommended: RTX 3090/4090 (24GB) or better."
    echo "   Cloud alternative: scripts/runpod_setup.md"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install unsloth if not present
if ! python -c "import unsloth" 2>/dev/null; then
    echo ""
    echo "📦 Installing unsloth for efficient fine-tuning..."
    pip install unsloth
fi

echo ""
echo "========================================"
echo "  ✅ Local Fine-tuning Ready!"
echo "========================================"
echo ""
echo "Run the fine-tuning notebook:"
echo "  uv run jupyter lab notebooks/06_dspy/06_finetuning.ipynb"
echo ""
echo "💡 Tips:"
echo "   - Use QLoRA (4-bit) to fit large models in limited VRAM"
echo "   - Reduce batch size to 1 if you get OOM errors"
echo "   - Training takes 1-3 hours depending on dataset size"
echo ""
