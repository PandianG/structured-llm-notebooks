# RunPod Cloud GPU Setup Guide for DSPy Fine-tuning

> Use this guide to fine-tune Llama 3.1 8B (or similar) on RunPod cloud GPUs for the DSPy Week 6 notebook.

---

## Why RunPod?

- **No local GPU required** — works from any laptop
- **Pay-per-hour** — ~$2-5/hour for A6000/L40, ~$1-2/hour for RTX A5000
- **Pre-built PyTorch templates** — CUDA drivers pre-installed
- **VS Code tunnel support** — develop remotely

---

## Step 1: Create a RunPod Account

1. Go to [runpod.io](https://www.runpod.io)
2. Sign up and add payment method
3. Top up with $10-20 (sufficient for several hours of training)

---

## Step 2: Deploy a GPU Pod

1. Go to **Console → GPU Pods → Deploy**
2. Select a template:
   - **Recommended:** `PyTorch 2.5 + CUDA 12.4` (or latest)
3. Select GPU:
   - **Budget:** RTX A5000 (16GB VRAM) — ~$1.20/hour
   - **Recommended:** RTX A6000 (48GB VRAM) — ~$2.50/hour
   - **Fast:** L40 (48GB VRAM) — ~$3.00/hour
4. Set disk size: **50GB** minimum
5. Click **Deploy**

---

## Step 3: Connect to Your Pod

### Option A: JupyterLab (Browser)
- Click **Connect** → **JupyterLab**
- Upload the DSPy finetuning notebook
- Run cells directly

### Option B: SSH + VS Code
```bash
# Get SSH command from RunPod UI (Connect → SSH)
ssh root@xxx.runpod.io -p 12345

# Or use VS Code Remote-SSH extension
# 1. Install "Remote - SSH" extension
# 2. Add Host to ~/.ssh/config:
#    Host runpod
#        HostName xxx.runpod.io
#        User root
#        Port 12345
#        IdentityFile ~/.ssh/id_rsa
# 3. Connect: code --remote ssh-remote+runpod /workspace
```

---

## Step 4: Install Dependencies

```bash
# Inside the pod terminal
pip install uv

# Clone your repo (or upload via JupyterLab)
git clone https://github.com/sourangshupal/llm-engineering-toolkit.git

cd llm-engineering-toolkit
uv sync --all-extras

# Install unsloth for efficient fine-tuning
pip install unsloth
```

---

## Step 5: Run the Fine-tuning Notebook

```bash
# Start Jupyter
uv run jupyter lab --ip=0.0.0.0 --port=8888 --no-browser

# Open the provided URL in your local browser
```

Open `notebooks/06_dspy/06_finetuning.ipynb` and run all cells.

---

## Step 6: Download the Fine-tuned Model

```bash
# After training completes, export to HuggingFace format or GGUF
# Example: export to GGUF for local inference
python -c "
from unsloth import FastLanguageModel
model, tokenizer = FastLanguageModel.from_pretrained('outputs/llama3.1-8b-dspy')
model.save_pretrained_gguf('outputs/llama3.1-8b-dspy.gguf', tokenizer)
"

# Download to local machine
scp -P 12345 root@xxx.runpod.io:/workspace/llm-libraries/outputs/llama3.1-8b-dspy.gguf ./
```

---

## Cost Estimate

| Task | GPU | Time | Cost |
|------|-----|------|------|
| Fine-tune Llama 3.1 8B (QLoRA) | A6000 | 1-2 hours | $2.50-5.00 |
| Fine-tune Llama 3.1 8B (QLoRA) | A5000 | 2-3 hours | $2.40-3.60 |
| Export to GGUF | Any | 10 min | ~$0.50 |

**Total: ~$3-6 for a complete fine-tuning run**

---

## Tips

- **Use `unsloth`** — 2x faster training, 70% less VRAM
- **Save checkpoints every 100 steps** — resume if pod preempted
- **Stop pod when done** — charges accrue while running
- **Use Spot/Interruptible instances** — 50% cheaper but may terminate

---

## Alternative Cloud Providers

| Provider | Cheapest GPU | Price/hour | Link |
|----------|-------------|------------|------|
| RunPod | RTX A5000 | ~$1.20 | [runpod.io](https://runpod.io) |
| Lambda Labs | RTX A6000 | ~$1.10 | [lambdalabs.com](https://lambdalabs.com) |
| Vast.ai | RTX 3090 | ~$0.50 | [vast.ai](https://vast.ai) |
| Google Colab | T4 (free tier) | $0 | [colab.research.google.com](https://colab.research.google.com) |

---

## Troubleshooting

**OOM during training?**
- Reduce `per_device_train_batch_size` to 1
- Increase `gradient_accumulation_steps`
- Use `max_seq_length=2048` instead of 4096

**Pod won't start?**
- Check CUDA compatibility: `nvidia-smi`
- Reinstall torch with correct CUDA: `pip install torch --index-url https://download.pytorch.org/whl/cu124`

**Slow SSH connection?**
- Use RunPod's **Proxy** feature (browser-based terminal)
- Or use VS Code tunnels: `code tunnel` inside the pod
