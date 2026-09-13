"""
Unified LM configuration for all 6 libraries.

Supports cost-saving toggles: USE_OLLAMA and USE_SMALL_MODEL, and multiple
API providers so students are not tied to a paid OpenAI key:

    LLM_PROVIDER=openai|anthropic|gemini|groq

Gemini (free tier: aistudio.google.com) and Groq (free tier: groq.com) both
work with Instructor, Outlines, and DSPy.
"""

import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ---------------------------------------------------------------------------
# Cost-control toggles
# ---------------------------------------------------------------------------
USE_OLLAMA: bool = os.getenv("USE_OLLAMA", "false").lower() in ("true", "1", "yes")
USE_SMALL_MODEL: bool = os.getenv("USE_SMALL_MODEL", "false").lower() in ("true", "1", "yes")
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# ---------------------------------------------------------------------------
# Provider selection
# ---------------------------------------------------------------------------
VALID_PROVIDERS = ("openai", "anthropic", "gemini", "groq")
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai").lower()
if LLM_PROVIDER not in VALID_PROVIDERS:
    raise ValueError(
        f"LLM_PROVIDER must be one of {VALID_PROVIDERS}, got {LLM_PROVIDER!r}"
    )

# OpenAI-compatible base URLs for providers without a dedicated Outlines/DSPy path
GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GEMINI_BASE_URL: str = os.getenv(
    "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"
)

# ---------------------------------------------------------------------------
# API Keys
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
BRAINTRUST_API_KEY: str | None = os.getenv("BRAINTRUST_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY: str | None = os.getenv("MISTRAL_API_KEY")
COHERE_API_KEY: str | None = os.getenv("COHERE_API_KEY")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
# GEMINI_API_KEY is accepted as an alias for GOOGLE_API_KEY
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY") or GOOGLE_API_KEY

# ---------------------------------------------------------------------------
# Model names (all overridable via .env)
# ---------------------------------------------------------------------------
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.7-flash")
GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

# ---------------------------------------------------------------------------
# Notebook settings
# ---------------------------------------------------------------------------
SAMPLE_SIZE: int = int(os.getenv("SAMPLE_SIZE", "50"))
DSPY_OPTIMIZER_TRIALS: int = int(os.getenv("DSPY_OPTIMIZER_TRIALS", "10"))
INSTRUCTOR_MAX_RETRIES: int = int(os.getenv("INSTRUCTOR_MAX_RETRIES", "3"))
REDTEAM_SAMPLE_SIZE: int = int(os.getenv("REDTEAM_SAMPLE_SIZE", "50"))

# ---------------------------------------------------------------------------
# Provider / model resolution
# ---------------------------------------------------------------------------
_PROVIDER_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY (or GOOGLE_API_KEY)",
    "groq": "GROQ_API_KEY",
}


def get_active_provider() -> str:
    """Return the provider selected via LLM_PROVIDER."""
    return LLM_PROVIDER


def require_api_key(provider: str) -> str:
    """Return the API key for a provider, with a student-friendly error."""
    key = {
        "openai": OPENAI_API_KEY,
        "anthropic": ANTHROPIC_API_KEY,
        "gemini": GEMINI_API_KEY,
        "groq": GROQ_API_KEY,
    }[provider]
    if not key:
        raise ValueError(
            f"No API key found for provider {provider!r}. "
            f"Set {_PROVIDER_KEY_ENV[provider]} in your .env file, "
            "or pick another provider with LLM_PROVIDER in .env."
        )
    return key


def get_model(provider: str | None = None) -> str:
    """Return the model name for a provider, honoring cost-saving toggles."""
    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        return "ollama/llama3.1"
    if provider == "openai":
        return "gpt-4o-mini" if USE_SMALL_MODEL else "gpt-4o"
    if provider == "anthropic":
        return "claude-sonnet-4-6" if USE_SMALL_MODEL else "claude-opus-4-6"
    if provider == "gemini":
        return GEMINI_MODEL
    if provider == "groq":
        return GROQ_MODEL
    raise ValueError(f"Unknown provider: {provider!r}")


def get_openai_model() -> str:
    """Return the OpenAI model name based on cost-saving toggles."""
    return get_model("openai")


def get_anthropic_model() -> str:
    """Return the Anthropic model name based on cost-saving toggles."""
    return get_model("anthropic")


def get_gemini_model() -> str:
    """Return the Gemini model name."""
    return get_model("gemini")


def get_groq_model() -> str:
    """Return the Groq model name."""
    return get_model("groq")


# ---------------------------------------------------------------------------
# DSPy
# ---------------------------------------------------------------------------
def get_dspy_lm(provider: str | None = None):
    """Return a configured DSPy LM for the selected provider."""
    import dspy  # type: ignore[import-not-found]

    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        return dspy.LM("ollama_chat/llama3.1", api_base=OLLAMA_BASE_URL)
    if provider == "gemini":
        return dspy.LM(f"gemini/{get_model('gemini')}", api_key=require_api_key("gemini"))
    if provider == "groq":
        return dspy.LM(f"groq/{get_model('groq')}", api_key=require_api_key("groq"))
    if provider == "anthropic":
        return dspy.LM(
            f"anthropic/{get_model('anthropic')}", api_key=require_api_key("anthropic")
        )
    return dspy.LM(f"openai/{get_model('openai')}", api_key=require_api_key("openai"))


# ---------------------------------------------------------------------------
# Instructor
# ---------------------------------------------------------------------------
_TRANSIENT_MARKERS = (
    "503",
    "unavailable",
    "429",
    "rate limit",
    "rate_limit",
    "500",
    "502",
    "timeout",
    "temporarily",
    "overloaded",
    "connection",
)


def _is_transient(e: Exception) -> bool:
    """True for provider-side transient errors (free tiers 503/429 under load)."""
    msg = str(e).lower()
    return any(marker in msg for marker in _TRANSIENT_MARKERS)


class _RetryingInstructor:
    """Wraps an Instructor client and retries transient API errors.

    instructor's own retry only re-asks on validation failures — a raw 503 from
    Gemini/Groq free tiers fails immediately. This proxy adds outer retries on
    transient provider errors so students don't hit spurious failures.
    """

    def __init__(self, inner, max_retries: int = INSTRUCTOR_MAX_RETRIES):
        self._inner = inner
        self._max_retries = max(1, max_retries)

    # chat / completions / messages all return `self` on the inner client too
    @property
    def chat(self):
        return self

    @property
    def completions(self):
        return self

    @property
    def messages(self):
        return self

    def create(self, *args, **kwargs):
        from tenacity import (
            retry,
            retry_if_exception,
            stop_after_attempt,
            wait_exponential,
        )

        @retry(
            stop=stop_after_attempt(self._max_retries),
            wait=wait_exponential(multiplier=1, min=2, max=20),
            retry=retry_if_exception(_is_transient),
            reraise=True,
        )
        def _call():
            return self._inner.create(*args, **kwargs)

        return _call()

    def __getattr__(self, name):
        return getattr(self._inner, name)


def get_instructor_client(provider: str | None = None):
    """Return an Instructor-patched client. Defaults to LLM_PROVIDER.

    The returned client retries transient provider errors (503/429, common on
    free tiers) up to INSTRUCTOR_MAX_RETRIES times, in addition to instructor's
    own validation retries.
    """
    import instructor

    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        from openai import OpenAI  # type: ignore[import-not-found]

        client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
        return _RetryingInstructor(instructor.from_openai(client))

    if provider == "gemini":
        from google import genai  # type: ignore[import-not-found]
        from instructor.mode import Mode  # type: ignore[import-not-found]
        from instructor.providers.genai import from_genai  # type: ignore[import-not-found]

        client = genai.Client(api_key=require_api_key("gemini"))
        return _RetryingInstructor(
            from_genai(
                client, mode=Mode.GENAI_STRUCTURED_OUTPUTS, model=get_model("gemini")
            )
        )
    if provider == "groq":
        from groq import Groq  # type: ignore[import-not-found]

        return _RetryingInstructor(instructor.from_groq(Groq(api_key=require_api_key("groq"))))
    if provider == "anthropic":
        from anthropic import Anthropic  # type: ignore[import-not-found]

        return _RetryingInstructor(
            instructor.from_anthropic(Anthropic(api_key=require_api_key("anthropic")))
        )
    from openai import OpenAI

    return _RetryingInstructor(instructor.from_openai(OpenAI(api_key=require_api_key("openai"))))


# ---------------------------------------------------------------------------
# Outlines (any OpenAI-compatible endpoint)
# ---------------------------------------------------------------------------
def get_outlines_model(provider: str | None = None):
    """Return an Outlines model for the selected provider.

    Uses each provider's OpenAI-compatible endpoint. Note: token-level
    constraint guarantees depend on the endpoint honoring structured-output
    requests (gpt-oss-120b on Groq does — it's the default GROQ_MODEL).
    For hard guarantees use a local transformers
    model with outlines.from_transformers.
    """
    import outlines  # type: ignore[import-not-found]
    from openai import OpenAI

    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        return outlines.from_openai(
            OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama"),
            "llama3.1",
        )
    if provider == "gemini":
        client = OpenAI(
            base_url=GEMINI_BASE_URL, api_key=require_api_key("gemini")
        )
        return outlines.from_openai(client, get_model("gemini"))
    if provider == "groq":
        client = OpenAI(base_url=GROQ_BASE_URL, api_key=require_api_key("groq"))
        return outlines.from_openai(client, get_model("groq"))
    client = OpenAI(api_key=require_api_key("openai"))
    return outlines.from_openai(client, get_model("openai"))


# ---------------------------------------------------------------------------
# Plain clients
# ---------------------------------------------------------------------------
def get_openai_client(provider: str | None = None):
    """Return a plain OpenAI-compatible client for the selected provider."""
    from openai import OpenAI

    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        return OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    if provider == "gemini":
        return OpenAI(base_url=GEMINI_BASE_URL, api_key=require_api_key("gemini"))
    if provider == "groq":
        return OpenAI(base_url=GROQ_BASE_URL, api_key=require_api_key("groq"))
    if provider == "anthropic":
        raise ValueError("Anthropic has no OpenAI-compatible endpoint; use get_anthropic_client()")
    return OpenAI(api_key=require_api_key("openai"))


def get_async_openai_client(provider: str | None = None):
    """Return a plain async OpenAI-compatible client for the selected provider."""
    from openai import AsyncOpenAI

    provider = provider or LLM_PROVIDER
    if USE_OLLAMA:
        return AsyncOpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    if provider == "gemini":
        return AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=require_api_key("gemini"))
    if provider == "groq":
        return AsyncOpenAI(base_url=GROQ_BASE_URL, api_key=require_api_key("groq"))
    if provider == "anthropic":
        raise ValueError("Anthropic has no OpenAI-compatible endpoint; use get_anthropic_client()")
    return AsyncOpenAI(api_key=require_api_key("openai"))


def get_anthropic_client():
    """Return a plain Anthropic client."""
    from anthropic import Anthropic

    return Anthropic(api_key=require_api_key("anthropic"))


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------
def print_config() -> None:
    """Print current configuration for debugging."""
    print("=" * 50)
    print("LLM Libraries — Configuration")
    print("=" * 50)
    print(f"USE_OLLAMA:        {USE_OLLAMA}")
    print(f"USE_SMALL_MODEL:   {USE_SMALL_MODEL}")
    print(f"OLLAMA_BASE_URL:   {OLLAMA_BASE_URL}")
    print(f"LLM_PROVIDER:      {LLM_PROVIDER}")
    for p in VALID_PROVIDERS:
        print(f"  {p + ' model:':<16} {get_model(p)}")
    print(f"SAMPLE_SIZE:       {SAMPLE_SIZE}")
    print(f"DSPY_TRIALS:       {DSPY_OPTIMIZER_TRIALS}")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
