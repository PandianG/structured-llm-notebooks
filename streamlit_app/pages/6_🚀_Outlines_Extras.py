"""Page 6 — Outlines Extras: format types, regex DSL, batch, CFG statements."""

import ipaddress
import re
import sys
import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import ui  # noqa: E402

st.set_page_config(page_title="6 · Outlines Extras", page_icon="🚀", layout="wide")
ui.inject_css()

st.title("🚀 Outlines: Beyond the Basics")
st.markdown(
    """
Page 5 showed the guarantee. This page tours what you can *do* with it: built-in
format types (credit cards that pass Luhn!), a readable regex builder, batch
generation, and grammars for whole languages. All demos run on the **local model** —
free, and the only place token masking is possible.
"""
)

ui.render_sidebar()

LOCAL_MODEL_NOTE = (
    "These demos load the local model (~1 GB, cached after first download) — "
    "token-level masking is not exposed by hosted APIs."
)


def local_model():
    m = ui.get_outlines_local_model()
    if m is None:
        st.error("Local model failed to load.")
        st.stop()
    return m


# ---------------------------------------------------------------------------
# Demo 1 — format-type gallery
# ---------------------------------------------------------------------------
ui.section(
    "1 · Format-type gallery: built-in masks, real validation",
    "Pick a type, generate a value, then watch Python validate it *independently* — "
    "ISO parsing for dates, strict parsing for UUIDs and IPs, regexes for the rest.",
)
ui.explain(
    "What's happening",
    "These aren't prompts. Each `outlines.types` entry compiles to a token mask (regex "
    "or grammar) that encodes the format's *rules* — so a `uuid4` can only ever be a "
    "valid version-4 UUID, and a `date` always parses as ISO 8601.",
)


VALIDATORS = {
    "email": (r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "strict email regex"),
    "date": ("%Y-%m-%d", "ISO date parse"),
    "datetime": ("%Y-%m-%d %H:%M:%S", "ISO datetime parse"),
    "time": ("%H:%M:%S", "ISO time parse"),
    "uuid4": ("uuid.UUID(value).version == 4", "UUID v4 structure"),
    "semver": (r"^\d+\.\d+\.\d+(-[0-9A-Za-z.-]+)?(\+[0-9A-Za-z.-]+)?$", "semver regex"),
    "ipv4": ("ipaddress.IPv4Address(value)", "IPv4 parse"),
    "hex_color": (r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$", "hex color regex"),
    "e164": (r"^\+[1-9]\d{7,14}$", "E.164 regex"),
    "mac_address": (r"^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$", "MAC-48 regex"),
}

TYPE_PROMPTS = {
    "email": "Generate a short support team email address",
    "date": "Generate a project deadline date",
    "datetime": "Generate a meeting timestamp",
    "time": "Generate a meeting start time",
    "uuid4": "Generate a unique identifier for a database row",
    "semver": "Generate a version number for a software release",
    "ipv4": "Generate an IP address for a home router",
    "hex_color": "Generate a brand color in hex",
    "e164": "Generate an international phone number",
    "mac_address": "Generate a MAC address for a network card",
}


def validate(fmt: str, value: str) -> bool:
    rule = VALIDATORS[fmt][0]
    try:
        if rule.startswith("%"):
            datetime.strptime(value, rule)
            return True
        if rule.startswith("uuid."):
            return uuid.UUID(value).version == 4
        if rule.startswith("ipaddress"):
            ipaddress.IPv4Address(value)
            return True
        return bool(re.match(rule, value))
    except (ValueError, TypeError):
        return False


fmt = st.selectbox("Format type", list(VALIDATORS))
col_gen, col_val = st.columns(2)

with col_gen:
    if st.button("🎰 Generate", type="primary"):
        import outlines.types as types

        with st.spinner("Generating on local model (CPU)…"):
            try:
                m = local_model()
                # max_new_tokens: give the small model room to finish — the default
                # cap truncates long masked outputs (e.g. uuid4) mid-token.
                value = m(TYPE_PROMPTS[fmt], getattr(types, fmt), max_new_tokens=96)
            except Exception as e:  # noqa: BLE001
                ui.api_error(e)
                st.stop()
        st.session_state["fmt_value"] = value
        st.session_state["fmt_type"] = fmt

if "fmt_value" in st.session_state:
    value = st.session_state["fmt_value"]
    ok = validate(st.session_state["fmt_type"], value)
    col_gen.code(value, language=None)
    col_gen.metric(
        f"Independent validation ({VALIDATORS[st.session_state['fmt_type']][1]})",
        "✅ PASS" if ok else "❌ FAIL",
    )
ui.try_this(
    "Generate an e164 phone number and a uuid4 — then validate them by hand against the rules."
)

with st.expander("🤔 Where are credit_card and isbn? (an honest limitation)"):
    st.markdown(
        """
Checksum-based formats like `credit_card` (Luhn) and `isbn` exist in
`outlines.types`, but their masks explode the finite-automaton state budget
(`Failed to build DFA: number of DFA states exceeds limit`) — the compiled mask
would be larger than memory allows. Mask compilation is powerful, not magic:
it works when the validity rule is expressible as a *finite pattern*, not a
global arithmetic checksum. For checksum formats, generate the structure and
validate the checksum afterwards — or use a library that can.
        """
    )

# ---------------------------------------------------------------------------
# Demo 2 — regex DSL builder
# ---------------------------------------------------------------------------
ui.section(
    "2 · Regex DSL: compose patterns, readably",
    "Build patterns from typed building blocks — `integer`, `exactly(n)`, `either(...)`, "
    "`optional(...)` — instead of hand-writing escaped regex soup.",
)
ui.explain(
    "What's happening",
    "`outlines.types` ships a mini-DSL where each piece knows how to render itself to a "
    "regex. Concatenate pieces and the composed term becomes the token mask. Readable "
    "intent, machine-exact output.",
)

pattern_choice = st.selectbox(
    "Pattern to build",
    ["Order ID: ORD-1234-A", "License key: AB12-CD34", "Count phrase: 3 cats"],
)

if st.button("🔧 Build & generate"):
    import outlines.types as types

    m = local_model()

    if pattern_choice == "Order ID: ORD-1234-A":
        term = "ORD-" + types.Regex(r"\d").exactly(4) + "-" + types.either("A", "B")
        prompt = "Generate an order ID"
        check = re.compile(r"^ORD-\d{4}-[AB]$")
    elif pattern_choice == "License key: AB12-CD34":
        term = types.Regex(r"[A-Z]{2}\d{2}") + "-" + types.Regex(r"[A-Z]{2}\d{2}")
        prompt = "Generate a license key"
        check = re.compile(r"^[A-Z]{2}\d{2}-[A-Z]{2}\d{2}$")
    else:
        term = types.integer.exactly(1) + " " + types.either("cat", "dog") + types.optional("s")
        prompt = "How many pets do you have?"
        check = re.compile(r"^\d (cat|dog)s?$")

    st.markdown("**The composed term — a readable tree that compiles to the mask:**")
    st.code(str(term), language=None)

    outputs = []
    with st.spinner("Generating samples…"):
        for i in range(3):
            try:
                out = m(f"{prompt} (sample {i + 1})", term, max_new_tokens=48)
            except Exception as e:  # noqa: BLE001
                ui.api_error(e)
                st.stop()
            outputs.append({"output": out, "matches": bool(check.match(out))})
    df = pd.DataFrame(outputs)
    st.dataframe(df, width="stretch")
    st.metric("Match rate", f"{df['matches'].sum()}/{len(df)}", delta="guaranteed")
ui.try_this(
    "Note how `optional('s')` handles both singular and plural — composition beats escaping."
)

# ---------------------------------------------------------------------------
# Demo 3 — batch generation
# ---------------------------------------------------------------------------
ui.section(
    "3 · Batch generation with `model.batch`",
    "Many prompts, one schema, one call. Batching amortizes mask compilation and "
    "tokenization across the whole set.",
)
ui.explain(
    "What's happening",
    "Each constrained prompt needs its logits processor compiled from the schema. With "
    "`.batch(...)`, Outlines compiles once and runs the prompts together — the "
    "per-item guarantee is identical, the overhead is divided.",
)

batch_prompts = st.multiselect(
    "Prompts",
    [
        "Name a laptop model and its price",
        "Name a wireless mouse and its price",
        "Name a mechanical keyboard and its price",
        "Name a monitor and its price",
        "Name a USB-C hub and its price",
    ],
    default=["Name a laptop model and its price", "Name a wireless mouse and its price"],
)


if st.button("📦 Generate batch"):
    from pydantic import BaseModel, Field

    class ProductItem(BaseModel):
        name: str = Field(description="Product name")
        price_usd: float = Field(gt=0, description="Price in USD")

    m = local_model()
    try:
        with st.spinner(f"Batch-generating {len(batch_prompts)} items on CPU…"):
            results = m.batch(batch_prompts, ProductItem, max_new_tokens=64)
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    items = [ProductItem.model_validate_json(r) for r in results]
    st.dataframe(
        pd.DataFrame(
            [{"prompt": p, **it.model_dump()} for p, it in zip(batch_prompts, items, strict=False)]
        ),
        width="stretch",
    )
    st.success(f"All {len(items)} items validated against the ProductItem schema in one batch.")
ui.try_this("Select all five prompts — watch that it takes about the same time as two.")

# ---------------------------------------------------------------------------
# Demo 4 — CFG: valid Python statements
# ---------------------------------------------------------------------------
ui.section(
    "4 · CFG: generate *programs*, provably valid",
    "Regex can't do nesting. Grammars can — here a tiny language of Python assignments, "
    "with `compile()` as the judge.",
)
ui.explain(
    "What's happening",
    "A context-free grammar accepts recursive rules (`expr` inside `expr`), so it can "
    "describe languages like JSON, SQL, or Python — not just patterns. Outlines parses "
    "the grammar (via llguidance), builds a mask that only walks valid derivations, and "
    "the result compiles by construction.",
)

PY_STMT_GRAMMAR = r"""
    start: stmt
    stmt: NAME "=" expr
    expr: term
        | expr "+" term
        | expr "-" term
        | expr "*" term
        | expr "/" term
    term: NUMBER
        | NAME
        | "(" expr ")"
    # NAME is deliberately bounded: an open-ended regex lets a small model ramble
    # inside the token forever without ever emitting "=" — a *model* quality issue,
    # not a grammar one. Bounded, the derivation must complete.
    NAME: /[a-zA-Z_][a-zA-Z0-9_]{0,9}/
    NUMBER: /[0-9]+(\.[0-9]+)?/
"""

stmt_prompt = st.text_input(
    "Prompt", value="Write a Python assignment that computes the area of a circle"
)

if st.button("🧬 Generate Python"):
    from outlines.types import CFG

    m = local_model()
    try:
        with st.spinner("Generating on local model…"):
            result = m(stmt_prompt, CFG(PY_STMT_GRAMMAR), max_new_tokens=96)
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    st.code(result, language="python")
    if "=" not in result:
        st.warning(
            "The model only produced a valid *prefix* of the grammar (an unterminated "
            "name). With small models this happens — see the bounded-NAME note in the "
            "grammar. Try again or lower the temperature."
        )
    else:
        try:
            compile(result, "<outlines-generated>", "exec")
            st.success("✅ `compile()` accepted it — syntactically valid Python by construction.")
        except SyntaxError as e:  # pragma: no cover - should be impossible
            st.error(f"Parse failed?! {e}")
    with st.expander("Show the grammar"):
        st.code(PY_STMT_GRAMMAR, language="lark")
ui.try_this("Compare with page 5's arithmetic grammar — CFGs scale where regexes can't.")

st.caption(LOCAL_MODEL_NOTE)
