# ─────────────────────────────────────────────────────────────────────────────
# config_loader.py — Settings & Environment Loader
#
# WHAT THIS FILE DOES:
#   Loads two things every time the app starts:
#   1. Environment variables from the .env file (API keys, provider choice)
#   2. App settings from config/config.json (model names, labels, score range)
#
# WHY load_dotenv()?
#   load_dotenv() reads the .env file and makes all the key=value pairs
#   available as environment variables in Python via os.getenv().
#   This is the standard way to keep secrets out of your source code.
#
# WHY A SEPARATE config.json FILE?
#   Non-secret settings like model names, labels, and score ranges belong in
#   config.json — not in .env (which is for secrets) and not hard-coded
#   inside Python files (which makes them hard to change without editing code).
#   Keeping config in a JSON file lets you change settings without touching code.
#
# BEST PRACTICE:
#   Always separate secrets (.env) from settings (config.json).
#   Never hard-code API keys or model names directly in Python files.
#
# WHEN TO USE THIS:
#   Called at the start of the pipeline in both main.py and inference.py.
# ─────────────────────────────────────────────────────────────────────────────

import os
import json
from dotenv import load_dotenv


def load_config(config_path: str = "config/config.json") -> dict:
    """
    Loads environment variables from .env and returns config settings from JSON.

    Returns:
        A dictionary with all app settings (llm model names, labels, score range).

    Raises:
        FileNotFoundError: if config.json does not exist at the given path.
    """

    # Load .env file so that os.getenv() can read the API keys and LLM_PROVIDER
    load_dotenv()

    # Check that the config file actually exists before trying to open it
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at {config_path}")

    # Read and parse the JSON config file into a Python dictionary
    with open(config_path, "r") as f:
        config = json.load(f)

    return config