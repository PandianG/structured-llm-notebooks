"""The deliberately fragile raw prompts used in the "without library" demos.

These are intentionally weak: no few-shot, no schema reinforcement, no stop
sequences. That is the point — students watch them fail.
"""

PERSON_SCHEMA_HINT = 'Return ONLY JSON: {"name": string, "age": int, "city": string}'

INVOICE_SCHEMA_HINT = (
    "Return ONLY JSON with keys: invoice_number, customer_name, items "
    "(list of description/quantity/unit_price/total), subtotal, tax_rate, "
    "total_amount, payment_status"
)

SENTIMENT_SYSTEM = (
    "Classify the sentiment of the text as positive, negative, or neutral. "
    "Reply with just the label."
)

PHONE_SYSTEM = "Generate one US phone number in the format XXX-XXXX. Reply with just the number."


def raw_extract_prompt(schema_hint: str, text: str) -> list[dict[str, str]]:
    """The exact message list a naive developer would send."""
    return [
        {"role": "system", "content": schema_hint},
        {"role": "user", "content": f"Extract: {text}"},
    ]
