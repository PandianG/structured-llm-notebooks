"""
Dataset loaders and synthetic generators.
Provides small, cost-efficient datasets for all notebooks.
"""

import json
import random
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# Synthetic Generators (zero API cost)
# ---------------------------------------------------------------------------


def generate_qa_pairs(n: int = 30, seed: int = 42) -> list[dict[str, Any]]:
    """Generate synthetic QA pairs for testing."""
    random.seed(seed)
    topics = [
        ("RAG", "Retrieval-Augmented Generation combines search with LLMs."),
        ("DSPy", "DSPy is a framework for programming language models."),
        ("Prompt Engineering", "Prompt engineering is the art of writing effective prompts."),
        ("Fine-tuning", "Fine-tuning adapts a pre-trained model to a specific task."),
        ("Vector DB", "Vector databases store embeddings for similarity search."),
        ("Chain-of-Thought", "CoT prompting asks the model to show its reasoning."),
        ("Attention", "Attention mechanisms let models focus on relevant tokens."),
        ("Transformers", "Transformers are neural networks based on self-attention."),
    ]
    qa_pairs = []
    for i in range(n):
        topic, context = random.choice(topics)
        qa_pairs.append(
            {
                "id": i,
                "question": f"What is {topic}?",
                "context": context,
                "expected": context,
                "category": topic.lower().replace(" ", "_"),
                "difficulty": random.choice(["easy", "medium", "hard"]),
            }
        )
    return qa_pairs


def generate_math_problems(n: int = 50, seed: int = 42) -> list[dict[str, Any]]:
    """Generate synthetic math word problems (GSM8K-style)."""
    random.seed(seed)
    problems = []
    for i in range(n):
        a, b, c = random.randint(10, 100), random.randint(2, 10), random.randint(5, 50)
        answer = a * b + c
        problems.append(
            {
                "id": i,
                "question": f"A store sells {a} apples per box. If you buy {b} boxes and already have {c} apples, how many apples do you have in total?",
                "answer": str(answer),
                "difficulty": "easy" if a < 50 else "medium",
            }
        )
    return problems


def generate_sentiment_data(n: int = 100, seed: int = 42) -> list[dict[str, str]]:
    """Generate synthetic sentiment classification examples."""
    random.seed(seed)
    positive = [
        "I love this product! It works perfectly.",
        "Amazing quality and fast shipping.",
        "Best purchase I've made this year.",
        "Highly recommend to everyone.",
        "Fantastic customer service experience.",
    ]
    negative = [
        "Terrible product, broke after one day.",
        "Waste of money, very disappointed.",
        "Poor quality and misleading description.",
        "Never buying from this brand again.",
        "Horrible experience, want a refund.",
    ]
    neutral = [
        "The product is okay, nothing special.",
        "It works as described, average quality.",
        "Received the item on time, standard packaging.",
        "Neither impressed nor disappointed.",
        "Does the job, but could be better.",
    ]
    data = []
    for i in range(n):
        sentiment = random.choice(["positive", "negative", "neutral"])
        text = random.choice(locals()[sentiment])
        data.append({"id": i, "text": text, "sentiment": sentiment})
    return data


def generate_invoice_texts(n: int = 20, seed: int = 42) -> list[dict[str, Any]]:
    """Generate synthetic invoice text for extraction tasks."""
    random.seed(seed)
    invoices = []
    for i in range(n):
        items = []
        num_items = random.randint(1, 4)
        subtotal = 0.0
        for j in range(num_items):
            qty = random.randint(1, 10)
            price = round(random.uniform(10, 500), 2)
            items.append(
                {
                    "description": f"Item {j + 1}",
                    "quantity": qty,
                    "unit_price": price,
                    "total": round(qty * price, 2),
                }
            )
            subtotal += qty * price
        tax_rate = round(random.choice([0.05, 0.10, 0.18, 0.20]), 2)
        total = round(subtotal * (1 + tax_rate), 2)
        invoices.append(
            {
                "id": i,
                "invoice_number": f"INV-{2024000 + i}",
                "customer_name": random.choice(
                    ["John Doe", "Jane Smith", "Acme Corp", "Global Ltd"]
                ),
                "items": items,
                "subtotal": round(subtotal, 2),
                "tax_rate": tax_rate,
                "total_amount": total,
                "payment_status": random.choice(["paid", "pending", "overdue"]),
                "raw_text": f"Invoice #{2024000 + i} for {random.choice(['John Doe', 'Jane Smith', 'Acme Corp', 'Global Ltd'])}. "
                + " ".join(
                    [
                        f"{it['description']} x{it['quantity']} @ ${it['unit_price']:.2f}"
                        for it in items
                    ]
                )
                + f". Tax: {int(tax_rate * 100)}%. Total: ${total:.2f}. Status: {random.choice(['paid', 'pending', 'overdue'])}.",
            }
        )
    return invoices


def generate_rag_contexts(n: int = 30, seed: int = 42) -> list[dict[str, Any]]:
    """Generate synthetic RAG contexts and questions."""
    random.seed(seed)
    contexts = [
        {
            "context": "Our return policy allows items to be returned within 30 days with original receipt. Refunds are processed within 5-7 business days.",
            "question": "What is the return policy?",
            "answer": "Items can be returned within 30 days with original receipt.",
        },
        {
            "context": "Free shipping is available on orders over $50. Standard shipping takes 3-5 business days. Express shipping is available for $15.",
            "question": "How much is express shipping?",
            "answer": "Express shipping costs $15.",
        },
        {
            "context": "Customer support is available Monday-Friday 9am-6pm EST. Email support@company.com or call 1-800-555-0199.",
            "question": "What is the customer support phone number?",
            "answer": "1-800-555-0199",
        },
    ]
    data = []
    for i in range(n):
        base = random.choice(contexts)
        data.append(
            {
                "id": i,
                "context": base["context"],
                "question": base["question"],
                "expected": base["answer"],
                "category": "policy" if "policy" in base["context"].lower() else "shipping",
            }
        )
    return data


# ---------------------------------------------------------------------------
# Load / Save Helpers
# ---------------------------------------------------------------------------


def save_jsonl(data: list[dict], filename: str) -> Path:
    """Save data as JSONL in the data/ directory."""
    path = DATA_DIR / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + "\n")
    return path


def load_jsonl(filename: str) -> list[dict]:
    """Load JSONL from the data/ directory."""
    path = DATA_DIR / filename
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def ensure_datasets() -> None:
    """Generate and save all synthetic datasets if they don't exist."""
    datasets = {
        "qa_pairs.jsonl": generate_qa_pairs(30),
        "math_problems.jsonl": generate_math_problems(50),
        "sentiment_data.jsonl": generate_sentiment_data(100),
        "invoices.jsonl": generate_invoice_texts(20),
        "rag_contexts.jsonl": generate_rag_contexts(30),
    }
    for filename, data in datasets.items():
        path = DATA_DIR / filename
        if not path.exists():
            save_jsonl(data, filename)
            print(f"✅ Generated {filename} ({len(data)} records)")
        else:
            print(f"📦 {filename} already exists ({len(data)} records)")


if __name__ == "__main__":
    ensure_datasets()
