"""
Unified LM configuration for all 6 libraries.
Supports cost-saving toggles: USE_OLLAMA and USE_SMALL_MODEL.
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
# API Keys
# ---------------------------------------------------------------------------
OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY: str | None = os.getenv("ANTHROPIC_API_KEY")
BRAINTRUST_API_KEY: str | None = os.getenv("BRAINTRUST_API_KEY")
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY")
MISTRAL_API_KEY: str | None = os.getenv("MISTRAL_API_KEY")
COHERE_API_KEY: str | None = os.getenv("COHERE_API_KEY")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

# ---------------------------------------------------------------------------
# Notebook settings
# ---------------------------------------------------------------------------
SAMPLE_SIZE: int = int(os.getenv("SAMPLE_SIZE", "50"))
DSPY_OPTIMIZER_TRIALS: int = int(os.getenv("DSPY_OPTIMIZER_TRIALS", "10"))
INSTRUCTOR_MAX_RETRIES: int = int(os.getenv("INSTRUCTOR_MAX_RETRIES", "3"))
REDTEAM_SAMPLE_SIZE: int = int(os.getenv("REDTEAM_SAMPLE_SIZE", "50"))


def get_openai_model() -> str:
    """Return the OpenAI model name based on cost-saving toggles."""
    if USE_OLLAMA:
        return "ollama/llama3.1"
    if USE_SMALL_MODEL:
        return "gpt-4o-mini"
    return "gpt-4o"


def get_anthropic_model() -> str:
    """Return the Anthropic model name based on cost-saving toggles."""
    if USE_SMALL_MODEL:
        return "claude-sonnet-4-6"  # adjust per latest naming
    return "claude-opus-4-6"


def get_dspy_lm():
    """Return a configured DSPy LM."""
    import dspy  # type: ignore[import-untyped]

    if USE_OLLAMA:
        return dspy.LM("ollama_chat/llama3.1", api_base=OLLAMA_BASE_URL)
    if USE_SMALL_MODEL:
        return dspy.LM("openai/gpt-4o-mini", api_key=OPENAI_API_KEY)
    return dspy.LM("openai/gpt-4o", api_key=OPENAI_API_KEY)


def get_instructor_client(provider: str = "openai"):
    """Return an Instructor-patched client."""
    import instructor

    if USE_OLLAMA:
        from openai import OpenAI

        client = OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
        return instructor.from_openai(client)

    if provider == "openai":
        from openai import OpenAI

        return instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
    if provider == "anthropic":
        from anthropic import Anthropic

        return instructor.from_anthropic(Anthropic(api_key=ANTHROPIC_API_KEY))

    # Auto-detect via from_provider
    model_name = (
        get_openai_model() if provider == "openai" else f"anthropic/{get_anthropic_model()}"
    )
    return instructor.from_provider(model_name)


def get_openai_client():
    """Return a plain OpenAI client."""
    from openai import OpenAI

    if USE_OLLAMA:
        return OpenAI(base_url=f"{OLLAMA_BASE_URL}/v1", api_key="ollama")
    return OpenAI(api_key=OPENAI_API_KEY)


def get_anthropic_client():
    """Return a plain Anthropic client."""
    from anthropic import Anthropic

    return Anthropic(api_key=ANTHROPIC_API_KEY)


def print_config() -> None:
    """Print current configuration for debugging."""
    print("=" * 50)
    print("LLM Libraries — Configuration")
    print("=" * 50)
    print(f"USE_OLLAMA:        {USE_OLLAMA}")
    print(f"USE_SMALL_MODEL:   {USE_SMALL_MODEL}")
    print(f"OLLAMA_BASE_URL:   {OLLAMA_BASE_URL}")
    print(f"OpenAI model:      {get_openai_model()}")
    print(f"Anthropic model:   {get_anthropic_model()}")
    print(f"SAMPLE_SIZE:       {SAMPLE_SIZE}")
    print(f"DSPY_TRIALS:       {DSPY_OPTIMIZER_TRIALS}")
    print("=" * 50)


if __name__ == "__main__":
    print_config()
