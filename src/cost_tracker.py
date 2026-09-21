"""
Cost tracker — per-notebook cost estimation and warnings.
Helps users understand API costs before running expensive cells.
"""

from typing import Any

# Pricing per 1K tokens (input + output averaged)
# These are rough estimates as of May 2026 — update as needed.
MODEL_PRICING: dict[str, float] = {
    "gpt-4o": 0.005,
    "gpt-4o-mini": 0.0005,
    "claude-opus-4-6": 0.015,
    "claude-sonnet-4-6": 0.003,
    "ollama/llama3.1": 0.0,
    "ollama/qwen2.5": 0.0,
    "ollama/phi4": 0.0,
}

NOTEBOOK_ESTIMATES: dict[str, dict[str, Any]] = {
    # Instructor
    "01_instructor/01_core_extraction.ipynb": {
        "calls": 10,
        "tokens_per_call": 2,
        "description": "Basic extraction with Instructor",
    },
    "01_instructor/02_validators.ipynb": {
        "calls": 15,
        "tokens_per_call": 3,
        "description": "Auto-retry with validators",
    },
    "01_instructor/03_streaming.ipynb": {
        "calls": 8,
        "tokens_per_call": 2,
        "description": "Streaming partial objects",
    },
    "01_instructor/04_local_pipeline.ipynb": {
        "calls": 20,
        "tokens_per_call": 2,
        "description": "Local Ollama pipeline",
    },
    # Outlines
    "02_outlines/01_token_constraints.ipynb": {
        "calls": 20,
        "tokens_per_call": 2,
        "description": "Token-level structured generation",
    },
    "02_outlines/02_pydantic_pipeline.ipynb": {
        "calls": 25,
        "tokens_per_call": 3,
        "description": "Pydantic extraction pipeline",
    },
    "02_outlines/03_cfg_codegen.ipynb": {
        "calls": 15,
        "tokens_per_call": 2,
        "description": "CFG-guided code/SQL generation",
    },
    "02_outlines/04_vision_structure.ipynb": {
        "calls": 10,
        "tokens_per_call": 5,
        "description": "Vision + structured output",
    },
    # Guidance
    "03_guidance/01_constrained_gen.ipynb": {
        "calls": 15,
        "tokens_per_call": 2,
        "description": "Token-level control with Guidance",
    },
    "03_guidance/02_cfg_sql.ipynb": {
        "calls": 20,
        "tokens_per_call": 2,
        "description": "CFG for SQL generation",
    },
    "03_guidance/03_agent_logic.ipynb": {
        "calls": 12,
        "tokens_per_call": 2,
        "description": "Python-native agent logic",
    },
    "03_guidance/04_benchmark_showdown.ipynb": {
        "calls": 100,
        "tokens_per_call": 2,
        "description": "Structured output benchmark (expensive)",
    },
    # Promptfoo
    "04_promptfoo/01_first_eval.ipynb": {
        "calls": 20,
        "tokens_per_call": 1,
        "description": "First eval suite",
    },
    "04_promptfoo/02_rag_testing.ipynb": {
        "calls": 30,
        "tokens_per_call": 2,
        "description": "RAG pipeline testing",
    },
    "04_promptfoo/03_redteam.ipynb": {
        "calls": 50,
        "tokens_per_call": 2,
        "description": "Red team scan (expensive)",
    },
    "04_promptfoo/04_custom_judge.ipynb": {
        "calls": 25,
        "tokens_per_call": 2,
        "description": "Custom LLM-as-judge",
    },
    # Braintrust
    "05_braintrust/01_first_experiment.ipynb": {
        "calls": 15,
        "tokens_per_call": 2,
        "description": "First Braintrust experiment",
    },
    "05_braintrust/02_ab_testing.ipynb": {
        "calls": 30,
        "tokens_per_call": 2,
        "description": "Prompt A/B testing",
    },
    "05_braintrust/03_custom_judge.ipynb": {
        "calls": 25,
        "tokens_per_call": 2,
        "description": "Custom scorer calibration",
    },
    "05_braintrust/04_agent_tracing.ipynb": {
        "calls": 15,
        "tokens_per_call": 2,
        "description": "Agent tracing",
    },
    "05_braintrust/05_ci_integration.ipynb": {
        "calls": 10,
        "tokens_per_call": 1,
        "description": "CI integration",
    },
    # DSPy
    "06_dspy/01_signatures_modules.ipynb": {
        "calls": 15,
        "tokens_per_call": 2,
        "description": "Signatures and core modules",
    },
    "06_dspy/02_optimizers.ipynb": {
        "calls": 60,
        "tokens_per_call": 3,
        "description": "DSPy optimizers (expensive)",
    },
    "06_dspy/03_rag_pipeline.ipynb": {
        "calls": 25,
        "tokens_per_call": 3,
        "description": "RAG with assertions",
    },
    "06_dspy/04_react_agent.ipynb": {
        "calls": 20,
        "tokens_per_call": 3,
        "description": "ReAct agent",
    },
    "06_dspy/05_gepa_optimizer.ipynb": {
        "calls": 80,
        "tokens_per_call": 3,
        "description": "GEPA optimizer (very expensive)",
    },
    "06_dspy/06_finetuning.ipynb": {
        "calls": 10,
        "tokens_per_call": 2,
        "description": "BetterTogether finetuning",
    },
    "06_dspy/07_module_catalog.ipynb": {
        "calls": 40,
        "tokens_per_call": 2,
        "description": "DSPy module catalog — all 13 modules",
    },
    "06_dspy/08_embeddings.ipynb": {
        "calls": 4,
        "tokens_per_call": 1,
        "description": "Embeddings: hosted + local + custom",
    },
    "06_dspy/09_optimizer_catalog.ipynb": {
        "calls": 90,
        "tokens_per_call": 2,
        "description": "Optimizer catalog — all 14 optimizers",
    },
    "06_dspy/10_adapters_evaluation.ipynb": {
        "calls": 25,
        "tokens_per_call": 2,
        "description": "Adapters + evaluation metrics",
    },
    "06_dspy/11_primitives_tools.ipynb": {
        "calls": 12,
        "tokens_per_call": 3,
        "description": "Primitives + retrieval/code tools",
    },
    "06_dspy/12_gepa_deep_dive.ipynb": {
        "calls": 60,
        "tokens_per_call": 3,
        "description": "GEPA complete implementation (deep dive)",
    },
    # Webinar — From Prompts to Programs
    "00_webinar/Demo_1_Instructor_and_Outlines.ipynb": {
        "calls": 35,
        "tokens_per_call": 3,
        "description": "Instructor + Outlines, with/without comparisons",
    },
    "00_webinar/Demo_2_DSPy.ipynb": {
        "calls": 25,
        "tokens_per_call": 3,
        "description": "DSPy, with/without comparisons + BootstrapFewShot",
    },
}


def estimate_cost(notebook_path: str, model: str = "gpt-4o") -> float:
    """Estimate cost in USD for a notebook."""
    from typing import cast

    info = NOTEBOOK_ESTIMATES.get(notebook_path)
    if not info:
        return 0.0
    price = MODEL_PRICING.get(model, 0.005)
    calls = cast(int, info["calls"])
    tokens_per_call = cast(int, info["tokens_per_call"])
    cost = calls * tokens_per_call * price
    return cost


def print_cost_warning(notebook_path: str, model: str = "gpt-4o") -> None:
    """Print a cost warning before running a notebook."""
    cost = estimate_cost(notebook_path, model)
    mini_cost = estimate_cost(notebook_path, "gpt-4o-mini")
    info = NOTEBOOK_ESTIMATES.get(notebook_path, {})

    print("💰 COST ESTIMATE")
    print("-" * 40)
    print(f"Notebook:  {notebook_path}")
    print(f"Task:      {info.get('description', 'N/A')}")
    print(f"Calls:     ~{info.get('calls', 'N/A')}")
    print()
    print(f"With GPT-4o:       ${cost:.2f} USD")
    print(f"With GPT-4o-mini:  ${mini_cost:.2f} USD (10x cheaper)")
    print("With Ollama:       $0.00 USD (free, local)")
    print()
    print("💡 TIP: Set USE_SMALL_MODEL=true or USE_OLLAMA=true in .env to save money.")
    print("-" * 40)


def full_report() -> None:
    """Print cost report for all notebooks."""
    print("=" * 60)
    print("LLM Libraries — Full Cost Report")
    print("=" * 60)

    total_gpt4 = 0.0
    total_mini = 0.0

    for path, _info in sorted(NOTEBOOK_ESTIMATES.items()):
        cost_gpt4 = estimate_cost(path, "gpt-4o")
        cost_mini = estimate_cost(path, "gpt-4o-mini")
        total_gpt4 += cost_gpt4
        total_mini += cost_mini
        print(f"{path:50s}  GPT-4o: ${cost_gpt4:6.2f}  Mini: ${cost_mini:6.2f}")

    print("=" * 60)
    print(f"{'TOTAL':50s}  GPT-4o: ${total_gpt4:6.2f}  Mini: ${total_mini:6.2f}")
    print("=" * 60)
    print()
    print("💡 With Ollama (local): $0.00 for everything!")
    print("💡 With GPT-4o-mini: ~90% cheaper than GPT-4o")


if __name__ == "__main__":
    full_report()
