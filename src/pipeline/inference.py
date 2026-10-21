# ─────────────────────────────────────────────────────────────────────────────
# inference.py — Full Pipeline Runner (Used by the API)
#
# WHAT THIS FILE DOES:
#   This is the single function that the API (app.py) calls to run the
#   entire evaluation pipeline on an uploaded file.
#   It sets up everything (config, LLM, chains) and runs all pipeline stages.
#
# WHY A SEPARATE inference.py?
#   main.py is for running the pipeline from the command line.
#   inference.py is for running it from the web API (app.py).
#   Keeping them separate follows the principle of separation of concerns —
#   each entry point sets up and runs the pipeline in its own way.
#
# HOW IT WORKS:
#   1. Load settings from config.json and environment variables
#   2. Connect to the AI model
#   3. Build all evaluation chains
#   4. Run classification → routing → evaluation → final report
#   5. Return the final DataFrame to the API for download
#
# BEST PRACTICE:
#   Load config and LLM inside the function (not at module level) so every
#   request gets fresh settings. This is important in long-running API servers.
#
# WHEN TO USE THIS:
#   This function is called automatically by app.py when a user uploads a file
#   to the /evaluate-file endpoint.
# ─────────────────────────────────────────────────────────────────────────────

from src.utils.config_loader import load_config
from src.utils.llm_loader import load_llm

from src.components.classification import get_classification_chain
from src.components.router import apply_routing
from src.components.evaluation import (
    get_tone_chain,
    get_knowledge_chain,
    get_resolution_chain
)
from src.components.reporting import get_final_report_chain

from src.pipeline.pipeline import (
    run_classification,
    apply_evaluations,
    apply_final_reports
)


def run_full_pipeline(df):
    """
    Runs the complete QA evaluation pipeline on a DataFrame of transcripts.

    Expected input: a DataFrame with at least 'call_id' and 'transcript' columns.
    Returns: the same DataFrame with added evaluation columns (scores, summary, etc.)
    """

    # Load app settings and AI model credentials
    config = load_config()
    llm = load_llm(config)

    # Build all the AI chains needed for evaluation
    classification_chain = get_classification_chain(llm, config)
    tone_chain = get_tone_chain(llm)
    knowledge_chain = get_knowledge_chain(llm)
    resolution_chain = get_resolution_chain(llm)
    final_chain = get_final_report_chain(llm)

    # Run each pipeline stage in order
    df = run_classification(df, classification_chain)   # Label each call type
    df = apply_routing(df)                              # Decide which checks to run
    df = apply_evaluations(                             # Score tone, knowledge, resolution
        df,
        tone_chain,
        knowledge_chain,
        resolution_chain
    )
    df = apply_final_reports(df, final_chain)           # Generate summary + tips

    return df