<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/uv-package%20manager-8A2BE2?logo=rocket&logoColor=white" alt="uv package manager">
  <img src="https://img.shields.io/badge/Jupyter-Notebooks-F37626?logo=jupyter&logoColor=white" alt="Jupyter Notebooks">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License: MIT">
</p>

<h1 align="center">
  🧠 Structured LLM Notebooks — Instructor · Outlines · DSPy
</h1>

<p align="center">
  <b>3 Libraries · 14 Notebooks · 40+ Features · Production-Ready</b>
</p>

<p align="center">
  <a href="#-libraries-covered">Libraries</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-cost-control">Cost Control</a> •
  <a href="#-notebook-guide">Notebooks</a> •
  <a href="#-comparison-matrix">Comparison</a>
</p>

---

## 🎯 What Is This?

This repository contains **deep-feature implementations** of the three most important libraries for **structured LLM programming**, designed for:

- 🎓 **Graduate Courses** — Structured 3-module curriculum
- 🏢 **Production Teams** — Reference implementations for extraction and optimization pipelines
- 📺 **Content Creation** — Engaging, practical demos

> **Philosophy:** We don't just show "Hello World" examples. We implement **every major feature** from the official documentation, research papers, and production best practices — with cost controls and real-world patterns.

> **Note:** This repo is a focused extract of the [llm-engineering-toolkit](https://github.com/sourangshupal/llm-engineering-toolkit), covering the structured-output and LLM-programming track only.

---

## 📚 Libraries Covered

| Module | Library | Notebooks | Core Concept | Stars |
|--------|---------|-----------|--------------|-------|
| 1 | 🎯 [**Instructor**](#1-instructor--typed-llm-outputs) | 4 | Typed LLM outputs (lowest barrier) | 12.9K |
| 2 | 🔒 [**Outlines**](#2-outlines--guaranteed-structured-generation) | 4 | Token-level guaranteed structure | 13.8K |
| 3 | 🚀 [**DSPy**](#3-dspy--programming-language-models) | 6 | Optimization + agents (capstone) | 34.2K |

---

## 🗂️ Project Structure

```
structured-llm-notebooks/
├── 📦 pyproject.toml              # uv-managed dependencies
├── 🔒 uv.lock                     # Reproducible lock file
├── 🚀 setup.sh                    # One-command automated setup
├── 🛠️ Makefile                    # Developer shortcuts
├── 📖 README.md                   # This file
├── 🔑 .env.example                # API keys + cost-control toggles
│
├── 📓 notebooks/                  # 14 implementation notebooks
│   ├── 01_instructor/             # 4 notebooks
│   ├── 02_outlines/               # 4 notebooks
│   └── 06_dspy/                   # 6 notebooks
│
├── 🧰 src/                        # Shared Python utilities
│   ├── config.py                  # Unified LM config (OpenAI/Anthropic/Gemini/Groq/Ollama)
│   ├── cost_tracker.py            # Per-notebook cost estimates
│   ├── datasets.py                # Synthetic generators (zero API cost)
│   └── metrics.py                 # Evaluation metrics
│
├── 📊 data/                       # 5 synthetic datasets
│   ├── qa_pairs.jsonl             # 30 QA pairs
│   ├── math_problems.jsonl        # 50 GSM8K-style problems
│   ├── sentiment_data.jsonl       # 100 classification examples
│   ├── rag_contexts.jsonl         # 30 RAG contexts
│   └── invoices.jsonl             # 20 extraction samples
│
└── 🔧 scripts/                    # Setup & deployment helpers
    ├── ollama_setup.sh            # Pull local models (zero-cost mode)
    ├── local_finetune.sh          # Local fine-tuning launcher
    └── runpod_setup.md            # Cloud GPU training guide
```

---

## ⚡ Quick Start

### Prerequisites

- **Python 3.11+**
- **uv** package manager (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- **Ollama** (optional, for free local inference)

### 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/sourangshupal/structured-llm-notebooks.git
cd structured-llm-notebooks

# Run automated setup (installs deps, Jupyter kernel)
make install

# Add your API keys
cp .env.example .env
# Edit .env with your keys

# (Optional) Pull free local models
make ollama-setup

# Start Jupyter Lab
make notebooks
```

Then open [http://localhost:8888](http://localhost:8888) and navigate to `notebooks/01_instructor/`.

### 🧪 Structured LLM Lab (Streamlit App)

Prefer clicking to reading? Launch the **Structured LLM Lab** — a multi-page Streamlit app
with live, hands-on demos: raw prompting vs Instructor, raw generation vs Outlines,
adherence benchmarks on real data, mode switching, streaming UIs, and a head-to-head
comparison of all three libraries.

**Start it with either:**

```bash
make streamlit
# or, without the Makefile:
uv run streamlit run streamlit_app/Home.py
```

Then open **http://localhost:8501** in your browser.

**Requirements:** the app calls real models, so you need at least one provider key in
`.env` (see [API Keys & Providers](#-api-keys--providers)). No OpenAI key? Set
`LLM_PROVIDER=gemini` or `LLM_PROVIDER=groq` — both have free tiers, and the sidebar
shows which keys are connected and which provider is active. Keep `USE_SMALL_MODEL=true`
in `.env` for cheap runs.

**Pages** (use the sidebar to navigate):

| Page | What it demos |
|------|---------------|
| `1❌ Without Instructor` | Raw prompting failure modes — unparseable JSON, no retries, adherence benchmark |
| `2✅ With Instructor` | One-line patching, validators, streaming partial objects, provider switcher (OpenAI/Anthropic/Gemini/Groq) |
| `3🚀 Instructor Extras` | `create_iterable`, `instructor.Maybe`, `create_with_completion`, response-modes laboratory |
| `4❌ Without Outlines` | Why raw generation breaks formats — phone numbers, sentiment labels, JSON |
| `5✅ With Outlines` | Rerun Page 4's benchmarks with guarantees; regex constraints, CFG code generation |
| `6🚀 Outlines Extras` | Built-in format masks, regex DSL, batch generation, provably-valid programs |
| `7⚖️ Head-to-Head` | Same input three ways — raw prompting vs Instructor vs Outlines, side by side |

The sidebar also lets you tune the benchmark sample size and temperature for the raw
demos. Changes to `.env` require a browser refresh (the app reads it at startup).


### Makefile Commands

| Command | Description |
|---------|-------------|
| `make install` | 🔧 First-time setup |
| `make sync` | 🔄 Sync uv dependencies |
| `make ollama-setup` | 🦙 Pull local Ollama models |
| `make notebooks` | 📓 Start Jupyter Lab |
| `make streamlit` | 🧪 Launch the interactive Structured LLM Lab |
| `make fmt` | ✨ Format code with ruff |
| `make lint` | 🔍 Lint code with ruff |
| `make typecheck` | 🏷️ Type check with mypy |
| `make clean` | 🧹 Clean cache files |
| `make cost-report` | 💰 Show full cost report |

---

## 💰 Cost Control

Every notebook includes a **cost estimate cell**. You control costs via `.env`:

| Mode | Setting | Full Course Cost | Speed |
|------|---------|------------------|-------|
| 🏎️ **Premium** (GPT-4o) | Default | ~$30-50 | Fastest |
| 💎 **Cheap** (GPT-4o-mini) | `USE_SMALL_MODEL=true` | ~$3-8 | Fast |
| 🆓 **Free API** (Gemini / Groq) | `LLM_PROVIDER=gemini` or `=groq` | **$0** (free tier) | Very fast |
| 🆓 **Free** (Local) | `USE_OLLAMA=true` | **$0** | CPU/GPU |

### Cost-Saving Tips

```bash
# .env file
USE_SMALL_MODEL=true        # 10x cheaper API calls
USE_OLLAMA=true            # Fully local inference
SAMPLE_SIZE=50             # Reduce dataset size
DSPY_OPTIMIZER_TRIALS=10   # Fewer optimization trials
```

---

## 📓 Notebook Guide

---

### 🎯 1. Instructor — Typed LLM Outputs

> **GitHub:** [instructor-ai/instructor](https://github.com/instructor-ai/instructor) | **Downloads:** 3M+/month
> **Core idea:** The cleanest way to get validated Pydantic objects from any LLM. Patch your existing client with one line.

**Features Implemented:**
- ✅ One-line client patching (`instructor.from_openai`, `from_anthropic`, `from_provider`)
- ✅ 15+ provider support (OpenAI, Anthropic, Google, Mistral, Cohere, Groq, Ollama, vLLM)
- ✅ Automatic validation + retries with error feedback
- ✅ Nested & complex Pydantic schemas
- ✅ Streaming partial objects (`create_partial`, `create_iterable`)
- ✅ Hooks system for logging and cost tracking
- ✅ Field-level validators as prompts
- ✅ Async support (`AsyncOpenAI`)
- ✅ Multimodal extraction (vision + text)
- ✅ Mode system (`TOOLS`, `JSON_SCHEMA`, `ANTHROPIC_TOOLS`)
- ✅ Extended thinking with Claude (`thinking=` parameter)
- ✅ `create_with_completion` for raw + typed output

**Notebooks:**
| # | Title | Runtime |
|---|-------|---------|
| 1.1 | [Core Extraction](notebooks/01_instructor/01_core_extraction.ipynb) | ~25 min |
| 1.2 | [Validators & Self-Correction](notebooks/01_instructor/02_validators.ipynb) | ~40 min |
| 1.3 | [Streaming for Responsive UIs](notebooks/01_instructor/03_streaming.ipynb) | ~45 min |
| 1.4 | [Local Pipeline with Ollama](notebooks/01_instructor/04_local_pipeline.ipynb) | ~50 min |

---

### 🔒 2. Outlines — Guaranteed Structured Generation

> **GitHub:** [dottxt-ai/outlines](https://github.com/dottxt-ai/outlines) | **Stars:** 13.8K
> **Core idea:** Mathematically guaranteed structured generation. The model physically cannot produce invalid output.

**Features Implemented:**
- ✅ Token-level constraint enforcement via finite-state automata (FSA)
- ✅ Pydantic model output — always valid JSON
- ✅ Full JSON Schema spec support
- ✅ Regex-guided generation
- ✅ Context-free grammars (Lark + EBNF)
- ✅ Choice / Enum generation (zero hallucination)
- ✅ Function signature generation (schema from Python function)
- ✅ Vision model support (`Chat` + `Image` inputs)
- ✅ Multi-backend (Transformers, vLLM, Ollama, SGLang, OpenAI)
- ✅ Async & streaming
- ✅ Standalone logits processors (`JSONLogitsProcessor`)
- ✅ vLLM guided decoding integration (`guided_*` params)
- ✅ `outlines-core` Rust library for custom serving

**Notebooks:**
| # | Title | Runtime |
|---|-------|---------|
| 2.1 | [Token-Level Constraints](notebooks/02_outlines/01_token_constraints.ipynb) | ~35 min |
| 2.2 | [Pydantic Production Pipelines](notebooks/02_outlines/02_pydantic_pipeline.ipynb) | ~50 min |
| 2.3 | [CFG Code & SQL Generation](notebooks/02_outlines/03_cfg_codegen.ipynb) | ~45 min |
| 2.4 | [Vision + Structured Output](notebooks/02_outlines/04_vision_structure.ipynb) | ~40 min |

---

### 🚀 3. DSPy — Programming Language Models

> **GitHub:** [stanfordnlp/dspy](https://github.com/stanfordnlp/dspy) | **Stars:** 34.2K
> **Core idea:** Programming — not prompting — language models. Define what the model should do in clean Python. DSPy compiles the best prompt automatically.

**Features Implemented:**
- ✅ Signatures (typed input/output pairs, replacing hand-written prompts)
- ✅ Core modules: `Predict`, `ChainOfThought`, `ProgramOfThought`, `ReAct`, `CodeAct`, `Refine`, `RLM`, `MultiChainComparison`, `BestOfN`, `Parallel`
- ✅ Optimizers: `BootstrapFewShot`, `MIPROv2`, `SIMBA`, `GEPA`, `Ensemble`, `BetterTogether`, `BootstrapFinetune`
- ✅ GEPA (Genetic-Pareto Prompt Evolution) — outperforms RL on benchmarks
- ✅ SIMBA (Stochastic Introspective Mini-Batch Ascent) — best for agents
- ✅ Assertions (`Assert`, `Suggest`) for runtime constraints
- ✅ Multi-LM support (`dspy.LM`, `dspy.context`)
- ✅ RAG pipelines with multi-hop retrieval
- ✅ ReAct agents with MCP tools
- ✅ Evaluation framework (`Evaluate`, `SemanticF1`, `CompleteAndGrounded`)
- ✅ Save/load, streaming, async, caching

**Notebooks:**
| # | Title | Runtime |
|---|-------|---------|
| 3.1 | [Signatures & Core Modules](notebooks/06_dspy/01_signatures_modules.ipynb) | ~20 min |
| 3.2 | [Optimizers: Bootstrap vs MIPROv2](notebooks/06_dspy/02_optimizers.ipynb) | ~45 min |
| 3.3 | [RAG with Assertions](notebooks/06_dspy/03_rag_pipeline.ipynb) | ~60 min |
| 3.4 | [ReAct Agent with Tools](notebooks/06_dspy/04_react_agent.ipynb) | ~45 min |
| 3.5 | [GEPA Optimizer Deep Dive](notebooks/06_dspy/05_gepa_optimizer.ipynb) | ~90 min |
| 3.6 | [Finetuning + BetterTogether](notebooks/06_dspy/06_finetuning.ipynb) | ~4 hours |

---

## 📊 Comparison Matrix

| Dimension | 🎯 Instructor | 🔒 Outlines | 🚀 DSPy |
|-----------|-------------|-------------|---------|
| **Primary job** | Structured extraction | Guaranteed structure | Prompt optimization |
| **Guarantee level** | Validation + retry | Token-level math | Optimized, not guaranteed |
| **Prompt writing** | N/A | N/A | Automated |
| **Works local** | ✅ Full | ✅ Full | ✅ Full |
| **Works API** | ✅ Yes | ✅ Yes | ✅ Yes |
| **RAG support** | Via extraction | N/A | Native |
| **Agent support** | Via extraction | N/A | ReAct, CodeAct, RLM |
| **Streaming** | ✅ Partial[Model] | ✅ Yes | ✅ Yes |
| **Async** | ✅ Full | ✅ Yes | ✅ Yes |
| **Extended thinking** | ✅ Claude only | ❌ No | ❌ No |
| **Multi-language** | Py/TS/Go/Rust | Python only | Python only |
| **Finetuning support** | ❌ No | ❌ No | ✅ BetterTogether |
| **Learning curve** | Very low | Low | High |

---

## 🎓 Recommended Sequencing

### For a Graduate Course

```
Module 1: 🎯 Instructor  → Typed LLM outputs (lowest barrier)
Module 2: 🔒 Outlines    → Token-level constraints vs post-gen validation
Module 3: 🚀 DSPy        → Optimization, SIMBA, GEPA, RLM (capstone module)
```

### For Production (Priority Order)

```
Priority 1: 🎯 Instructor  → Immediate ROI for any extraction pipeline
Priority 2: 🔒 Outlines    → For high-stakes structured output requirements
Priority 3: 🚀 DSPy        → For complex multi-stage pipelines needing optimization
```

---

## 🔑 API Keys & Providers

**No paid OpenAI key? No problem.** Every notebook and the Streamlit app support multiple
providers via one setting in `.env` — pick the one you have a key for:

| Provider | Setting | Default Model | Cost | Get a key at |
|----------|---------|---------------|------|--------------|
| OpenAI | `LLM_PROVIDER=openai` | `gpt-4o` | Paid | [platform.openai.com](https://platform.openai.com) |
| Google Gemini | `LLM_PROVIDER=gemini` | `gemini-3.7-flash` | **Free tier** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| Groq | `LLM_PROVIDER=groq` | `openai/gpt-oss-120b` | **Free tier** | [console.groq.com/keys](https://console.groq.com/keys) |
| Anthropic | `LLM_PROVIDER=anthropic` | `claude-opus-4-6` | Paid | [console.anthropic.com](https://console.anthropic.com) |

```bash
# .env — minimum viable setup for a free run
LLM_PROVIDER=gemini          # or: groq
GEMINI_API_KEY=your-key      # or: GROQ_API_KEY
```

Provider notes:

- **Gemini** — defaults to `gemini-3.7-flash` (launched Aug 13, 2026; free tier in AI Studio).
  `gemini-3.8-flash` (Sept 2, 2026, same pricing, stronger coding/agentic performance) is
  available too — set `GEMINI_MODEL=gemini-3.8-flash` to try it.
- **Groq** — defaults to `openai/gpt-oss-120b`: it supports native structured outputs
  (response schemas), which Instructor and Outlines rely on. Note Groq retired
  `llama-3.3-70b-versatile` from the free tier in Aug 2026, and Llama has no native
  schema support anyway — if you self-host or use enterprise Groq, expect prompt-only
  constraint guarantees there.
- **Instructor** — Gemini uses native structured outputs (`GENAI_STRUCTURED_OUTPUTS`);
  Groq works via `from_groq` (function-calling mode).
- **DSPy** — routes through `dspy.LM`/`litellm` (`gemini/…` or `groq/…` prefixes); no
  extra setup.
- **Outlines** — uses each provider's OpenAI-compatible endpoint. Hard token-level
  guarantees require the endpoint to honor structured outputs (OpenAI and Groq's
  gpt-oss do). For absolute guarantees, use a local model
  (`outlines.from_transformers`) as the notebooks show.
- **Vision notebook** (2.4) needs a vision-capable model — use `openai` or `gemini`.
- You can also override per call in code: `get_instructor_client("gemini")`, `get_model("groq")`, etc.

---

## 🖥️ Hardware Requirements

| Task | Minimum | Recommended | Cloud Alternative |
|------|---------|-------------|-------------------|
| **CPU inference** | 8GB RAM | 16GB RAM | — |
| **GPU inference** | 8GB VRAM | 16GB+ VRAM | RunPod / Lambda |
| **Fine-tuning** | 16GB VRAM | 24GB+ VRAM | RunPod A6000 (~$2.50/hr) |
| **DSPy optimization** | — | — | API only |

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 KrishAI Technologies

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🙏 Acknowledgments

- **Stanford NLP** for DSPy
- **.txt (dottxt-ai)** for Outlines
- **Instructor AI** for Instructor

---

<p align="center">
  <b>Built with ❤️ for the AI engineering community</b>
</p>

<p align="center">
  <a href="#-structured-llm-notebooks--instructor--outlines--dspy">⬆️ Back to Top</a>
</p>
