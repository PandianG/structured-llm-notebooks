"""Page 3 — Instructor Extras: features beyond the notebooks."""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # allow `shared` imports

from shared import models, ui  # noqa: E402

import src.config as config  # noqa: E402

st.set_page_config(page_title="3 · Instructor Extras", page_icon="🚀", layout="wide")
ui.inject_css()

st.title("🚀 Instructor: Beyond the Basics")
st.markdown(
    """
Page 2 showed the core loop. This page covers the features that make Instructor
pleasant in real applications: lists, missing data, raw completions, and swappable
**modes** — the same `response_model` code working through completely different
mechanisms.
"""
)

ui.render_sidebar()
model_name = config.get_openai_model()

# ---------------------------------------------------------------------------
# Demo 1 — create_iterable: extract a LIST of objects
# ---------------------------------------------------------------------------
ui.section(
    "1 · Extracting lists with `create_iterable`",
    "Give the model a paragraph containing several entities and get back typed objects, "
    "one by one — no “split the JSON array yourself” code.",
)
ui.explain(
    "What's happening",
    "One schema, N objects. Instructor asks for a top-level JSON list, validates each "
    "element against your Pydantic model as it arrives, and yields objects lazily. "
    "If one element fails validation, the retry loop re-asks — your loop only ever "
    "sees valid items.",
)

default_people = """Team roster:
- Jason is 25 and lives in Austin
- Priya, 31, is based in London
- Marco is 28 and moved to Toronto
"""
text = st.text_area("Text with several people", value=default_people, height=130)

if st.button("👥 Extract all people", type="primary"):
    client = ui.get_instructor("openai")
    ui.show_code(
        "The exact code that runs",
        """users = client.create_iterable(
    messages=[{"role": "user", "content": text}],
    response_model=Person,   # one schema...
)
for user in users:           # ...many validated objects
    print(user)""",
    )
    try:
        with st.spinner("Extracting…"):
            people = list(
                client.create_iterable(
                    model=model_name,
                    messages=[{"role": "user", "content": text}],
                    response_model=models.Person,
                )
            )
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    st.success(f"Extracted {len(people)} validated Person objects:")
    st.dataframe(pd.DataFrame([p.model_dump() for p in people]), width="stretch")
ui.try_this("Add a 6th person, or remove everyone's city — what happens to `city`?")

# ---------------------------------------------------------------------------
# Demo 2 — instructor.Maybe: graceful absence
# ---------------------------------------------------------------------------
ui.section(
    "2 · Graceful absence with `instructor.Maybe(Person)`",
    "Real documents often *don't* contain the thing you're looking for. `Maybe` turns a "
    "validation error into an explicit, typed “no” — complete with the model's own reason.",
)
ui.explain(
    "What's happening",
    "`Maybe(Person)` (a function call, not a subscript) wraps your model in a container "
    "with `result: Person | None`, plus `error: bool` and `message`. When the info isn't "
    "there, the model fills `message` with *why* — Instructor validates that instead of "
    "crashing. A typed version of Python's `None`, at the schema level.",
)

col_a, col_b = st.columns(2)
with col_a:
    text_with = st.text_input("Text WITH a person", value="Alice, 30, lives in New York")
with col_b:
    text_without = st.text_input(
        "Text WITHOUT a person",
        value="The quarterly revenue grew 12% year over year.",
    )

if st.button("🔍 Run both through Maybe"):
    import instructor

    client = ui.get_instructor("openai")
    ui.show_code(
        "The exact code that runs",
        """MaybePerson = instructor.Maybe(Person)   # a function call, not [Person]

answer = client.create(
    messages=[{"role": "user", "content": text}],
    response_model=MaybePerson,   # wrapper with result + error + message
)
if answer.result is not None:
    print(answer.result.name)
else:
    print(f"No person found: {answer.message}")""",
    )
    results = {}
    try:
        with st.spinner("Checking both texts…"):
            for label, txt in (("WITH person", text_with), ("WITHOUT person", text_without)):
                answer = client.create(
                    model=model_name,
                    messages=[{"role": "user", "content": txt}],
                    response_model=instructor.Maybe(models.Person),
                )
                results[label] = answer
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    for label, answer in results.items():
        if answer.result is not None:
            st.success(f"**{label}** → `result` set, person: `{answer.result.model_dump_json()}`")
        else:
            st.info(
                f"**{label}** → `result=None`, model says: “{answer.message}” "
                "— a typed “no”, no exception thrown."
            )
ui.try_this("Give ambiguous text: “someone named maybe Alex?” — which way does it lean?")

# ---------------------------------------------------------------------------
# Demo 3 — create_with_completion: see the raw completion
# ---------------------------------------------------------------------------
ui.section(
    "3 · `create_with_completion`: never lose the raw model output",
    "Sometimes you need the untouched completion — token counts for billing, the model's "
    "reasoning, or an audit trail. Instructor hands it back alongside the object.",
)
ui.explain(
    "What's happening",
    "Instructor never hides the model. `create_with_completion` returns a tuple: the "
    "validated Pydantic object **and** the provider's original completion object. "
    "Log it, count tokens, inspect the exact string the model produced — everything "
    "a plain SDK call would give you, minus the parsing pain.",
)

if st.button("🧾 Extract + keep raw completion"):
    client = ui.get_instructor("openai")
    ui.show_code(
        "The exact code that runs",
        """person, completion = client.create_with_completion(
    messages=[{"role": "user", "content": "Bob is 25 and from San Francisco"}],
    response_model=Person,
)
completion.usage          # tokens for cost tracking
completion.choices[0].message.content   # the exact string produced""",
    )
    try:
        with st.spinner("Extracting…"):
            person, completion = client.create_with_completion(
                model=model_name,
                messages=[{"role": "user", "content": "Bob is 25 and from San Francisco"}],
                response_model=models.Person,
            )
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Your validated object**")
        st.json(person.model_dump())
    with c2:
        st.markdown("**Token usage (billing)**")
        usage = completion.usage.model_dump() if completion.usage else {}
        st.json(usage)
        st.markdown("**Raw model string**")
        st.code(completion.choices[0].message.content, language=None)
ui.try_this("Re-run on page 2's Anthropic demo — compare `usage` across providers.")

# ---------------------------------------------------------------------------
# Demo 4 — Modes laboratory
# ---------------------------------------------------------------------------
ui.section(
    "4 · Modes laboratory: same schema, different machinery",
    "`response_model` is portable — the *mechanism* underneath is swappable. Run the same "
    "extraction through three modes and confirm the object comes back identical.",
)
ui.explain(
    "What's happening",
    "Instructor can enforce structure with **function/tool calling** (`Mode.TOOLS`), a "
    "**plain JSON system prompt** (`Mode.JSON`), or **markdown-fenced extraction** "
    "(`Mode.MD_JSON`, the classic fallback). The right default depends on the provider — "
    "this swappability is why one Instructor codebase covers 30+ providers.",
)

MODE_NOTES = {
    "TOOLS": "Uses OpenAI function calling. Cleanest; requires tool support.",
    "JSON": "Plain system prompt asking for JSON. Works everywhere, softer guarantee.",
    "MD_JSON": "Extracts JSON from markdown fences. The classic fallback for chatty models.",
}

chosen = st.multiselect(
    "Modes to run",
    list(MODE_NOTES),
    default=["TOOLS", "MD_JSON"],
)
ui.show_code(
    "The exact code that runs",
    """import instructor
from instructor import Mode

mode_client = instructor.from_openai(openai_client, mode=Mode.TOOLS)  # or JSON / MD_JSON
person = mode_client.create(
    messages=[{"role": "user", "content": "Carol, 35, based in Chicago"}],
    response_model=Person,
)   # identical object regardless of mode""",
)

if st.button("🧪 Run selected modes"):
    import instructor
    from instructor import Mode

    results = {}
    try:
        for name in chosen:
            mode_client = instructor.from_openai(config.get_openai_client(), mode=Mode[name])
            with st.spinner(f"Running Mode.{name}…"):
                person = mode_client.create(
                    model=model_name,
                    messages=[{"role": "user", "content": "Carol, 35, based in Chicago"}],
                    response_model=models.Person,
                )
            results[name] = person
    except Exception as e:  # noqa: BLE001
        ui.api_error(e)
        st.stop()

    for name, person in results.items():
        st.success(f"**Mode.{name}** → `{person.model_dump_json()}`  \n_{MODE_NOTES[name]}_")

    if len({p.model_dump_json() for p in results.values()}) == 1 and len(results) > 1:
        st.info("Identical objects across modes — the schema is the contract, not the mechanism.")
ui.try_this(
    "Deselect TOOLS and run only MD_JSON — then imagine the provider is a chatty local model."
)
