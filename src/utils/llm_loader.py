# ─────────────────────────────────────────────────────────────────────────────
# llm_loader.py — AI Model Loader
#
# WHAT THIS FILE DOES:
#   Reads the LLM_PROVIDER environment variable and connects to the correct
#   AI model — either OpenAI (GPT) or Google Gemini.
#   Returns a ready-to-use LLM object that all chains can share.
#
# WHY ChatOpenAI and ChatGoogleGenerativeAI?
#   These are LangChain wrappers around the OpenAI and Google Gemini APIs.
#   Instead of writing raw API calls (handling headers, JSON, retries yourself),
#   LangChain wraps everything into a simple object you just call with .invoke().
#   Switching between providers becomes as easy as changing one env variable.
#
# WHY temperature=0.3?
#   Temperature controls how creative vs. predictable the AI's responses are.
#   - 0.0 = always picks the most likely word (very consistent, robotic)
#   - 1.0 = more creative, varied (less predictable)
#   For evaluation tasks, we want consistency, so 0.3 is a good balance.
#   This value is set in config.json so you can adjust it without code changes.
#
# WHY READ FROM ENVIRONMENT VARIABLES?
#   API keys should never be hard-coded. Reading from os.getenv() means
#   the key stays in your .env file (or AWS Secrets Manager in production)
#   and is never visible in your source code.
#
# BEST PRACTICE:
#   Always raise a clear error if required environment variables are missing.
#   This tells the user exactly what to set up instead of a confusing crash.
#
# WHEN TO USE THIS:
#   Called at the start of both main.py and inference.py to get the LLM object.
# ─────────────────────────────────────────────────────────────────────────────

import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI


def load_llm(config: dict):
    """
    Connects to the AI model specified in the LLM_PROVIDER environment variable.

    Supported providers:
      - "openai"  → Uses OpenAI's GPT model (set OPENAI_API_KEY in .env)
      - "gemini"  → Uses Google's Gemini model (set GEMINI_API_KEY in .env)

    Args:
        config: The loaded configuration dictionary (from config.json).

    Returns:
        A LangChain-compatible LLM object ready for use in chains.

    Raises:
        ValueError: If LLM_PROVIDER is not set or is not a supported value.
    """

    # Read which AI provider to use from the environment
    provider = os.getenv("LLM_PROVIDER")

    if provider is None:
        raise ValueError(
            "LLM_PROVIDER is not set. "
            "Please add LLM_PROVIDER=openai or LLM_PROVIDER=gemini to your .env file."
        )

    provider = provider.lower()

    if provider == "openai":
        # Connect to OpenAI using the API key from OPENAI_API_KEY env variable
        return ChatOpenAI(
            model=config["llm"]["openai_model"],
            temperature=config["llm"]["temperature"]
        )

    elif provider == "gemini":
        # Connect to Google Gemini using the API key from GEMINI_API_KEY env variable
        return ChatGoogleGenerativeAI(
            model=config["llm"]["gemini_model"],
            temperature=config["llm"]["temperature"]
        )

    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER: '{provider}'. "
            "Supported options are: 'openai' or 'gemini'."
        )