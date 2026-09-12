"""Load ground-truth datasets from data/*.jsonl for the benchmark demos."""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_invoices(n: int) -> list[dict]:
    """First n invoice rows: {raw_text, expected (dict matching Invoice)}."""
    rows = []
    with open(DATA_DIR / "invoices.jsonl") as f:
        for line in f:
            r = json.loads(line)
            rows.append(
                {
                    "raw_text": r["raw_text"],
                    "expected": {
                        "invoice_number": r["invoice_number"],
                        "customer_name": r["customer_name"],
                        "items": r["items"],
                        "subtotal": r["subtotal"],
                        "tax_rate": r["tax_rate"],
                        "total_amount": r["total_amount"],
                        "payment_status": r["payment_status"],
                    },
                }
            )
            if len(rows) >= n:
                break
    return rows


def load_sentiments(n: int) -> list[dict]:
    """First n sentiment rows: {text, expected_label}."""
    rows = []
    with open(DATA_DIR / "sentiment_data.jsonl") as f:
        for line in f:
            r = json.loads(line)
            rows.append({"text": r["text"], "expected_label": r["sentiment"]})
            if len(rows) >= n:
                break
    return rows
