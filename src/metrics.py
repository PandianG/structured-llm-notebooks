"""
Shared metrics and evaluation utilities.
Works with DSPy, Braintrust, and standalone evaluation.
"""

from typing import Any

# ---------------------------------------------------------------------------
# Simple string metrics
# ---------------------------------------------------------------------------


def exact_match(pred: str, gold: str) -> float:
    """Return 1.0 if prediction exactly matches gold, else 0.0."""
    return 1.0 if pred.strip().lower() == gold.strip().lower() else 0.0


def contains_match(pred: str, gold: str) -> float:
    """Return 1.0 if gold is a substring of prediction (case-insensitive)."""
    return 1.0 if gold.strip().lower() in pred.strip().lower() else 0.0


def f1_score(pred: str, gold: str) -> float:
    """Compute token-level F1 between prediction and gold."""
    pred_tokens = set(pred.lower().split())
    gold_tokens = set(gold.lower().split())
    if not pred_tokens or not gold_tokens:
        return 0.0
    overlap = len(pred_tokens & gold_tokens)
    precision = overlap / len(pred_tokens)
    recall = overlap / len(gold_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * (precision * recall) / (precision + recall)


# ---------------------------------------------------------------------------
# DSPy-compatible metrics
# ---------------------------------------------------------------------------


def dspy_exact_match(example, prediction, trace=None) -> float:
    """DSPy metric: exact match on 'answer' field."""
    return exact_match(
        getattr(prediction, "answer", str(prediction)),
        getattr(example, "answer", example.get("answer", "")),
    )


def dspy_contains_match(example, prediction, trace=None) -> float:
    """DSPy metric: check if gold answer appears in prediction."""
    pred = getattr(prediction, "answer", str(prediction))
    gold = getattr(example, "answer", example.get("answer", ""))
    return contains_match(pred, gold)


def dspy_f1_metric(example, prediction, trace=None) -> float:
    """DSPy metric: token F1."""
    pred = getattr(prediction, "answer", str(prediction))
    gold = getattr(example, "answer", example.get("answer", ""))
    return f1_score(pred, gold)


def dspy_length_constraint(example, prediction, trace=None, max_words: int = 50) -> float:
    """DSPy metric: reward concise answers."""
    pred = getattr(prediction, "answer", str(prediction))
    word_count = len(pred.split())
    return 1.0 if word_count <= max_words else max(0.0, 1.0 - (word_count - max_words) / 100)


# ---------------------------------------------------------------------------
# Braintrust-compatible scorers
# ---------------------------------------------------------------------------


def word_count_score(
    input: Any, output: str, expected: str | None = None, **kwargs
) -> dict[str, Any]:
    """Braintrust code scorer: reward conciseness."""
    word_count = len(output.split())
    if word_count <= 50:
        score = 1.0
    elif word_count <= 100:
        score = 0.5
    else:
        score = 0.0
    return {"name": "conciseness", "score": score, "metadata": {"word_count": word_count}}


def contains_keyword_score(
    input: Any, output: str, expected: str | None = None, keywords: list | None = None, **kwargs
) -> dict[str, Any]:
    """Braintrust code scorer: check if output contains required keywords."""
    if keywords is None:
        keywords = []
    output_lower = output.lower()
    found = [kw for kw in keywords if kw.lower() in output_lower]
    score = len(found) / len(keywords) if keywords else 1.0
    return {
        "name": "keyword_coverage",
        "score": score,
        "metadata": {"found": found, "required": keywords},
    }


# ---------------------------------------------------------------------------
# Promptfoo assertion helpers
# ---------------------------------------------------------------------------


def promptfoo_contains(value: str) -> dict[str, Any]:
    """Generate a Promptfoo 'contains' assertion."""
    return {"type": "contains", "value": value}


def promptfoo_not_contains(value: str) -> dict[str, Any]:
    """Generate a Promptfoo 'not-contains' assertion."""
    return {"type": "not-contains", "value": value}


def promptfoo_regex(pattern: str) -> dict[str, Any]:
    """Generate a Promptfoo 'regex' assertion."""
    return {"type": "regex", "value": pattern}


def promptfoo_is_json() -> dict[str, Any]:
    """Generate a Promptfoo 'is-json' assertion."""
    return {"type": "is-json"}


def promptfoo_llm_rubric(criteria: str, weight: float = 1.0) -> dict[str, Any]:
    """Generate a Promptfoo 'llm-rubric' assertion."""
    return {"type": "llm-rubric", "value": criteria, "weight": weight}


def promptfoo_latency(threshold_ms: int) -> dict[str, Any]:
    """Generate a Promptfoo 'latency' assertion."""
    return {"type": "latency", "threshold": threshold_ms}


# ---------------------------------------------------------------------------
# Instructor / Pydantic helpers
# ---------------------------------------------------------------------------


def validate_invoice_total(items: list, subtotal: float, tax_rate: float, total: float) -> bool:
    """Business logic validator: check invoice math."""
    from typing import cast

    expected_subtotal = cast(
        float,
        sum(cast(int, item["quantity"]) * cast(float, item["unit_price"]) for item in items),
    )
    expected_total = expected_subtotal * (1 + tax_rate)
    return abs(subtotal - expected_subtotal) < 0.01 and abs(total - expected_total) < 0.01
