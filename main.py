# ─────────────────────────────────────────────────────────────────────────────
# main.py — Command-Line Entry Point
#
# WHAT THIS FILE DOES:
#   This is the script you run directly from the terminal to process transcripts.
#   It loads your data, sets up the AI chains, runs them through the pipeline,
#   and saves the final evaluated output to an Excel file.
#
# WHEN TO USE THIS:
#   Use this when you want to run the full pipeline from the command line
#   without starting a web server. Great for testing or batch processing.
#   Run it with: python main.py
#
# HOW IT WORKS (step by step):
#   1. Load settings from config.json and environment variables (.env)
#   2. Load the transcripts spreadsheet from the data/ folder
#   3. Connect to the AI model (OpenAI or Gemini)
#   4. Build AI chains for: classification, tone, knowledge, resolution, reporting
#   5. Run each transcript through all steps in order
#   6. Save the final results to data/output.xlsx
# ─────────────────────────────────────────────────────────────────────────────

from src.utils.config_loader import load_config
from src.utils.data_loader import load_transcripts
from src.utils.llm_loader import load_llm
from src.utils.helpers import save_dataframe

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


def main():
    # Step 1: Load settings from config.json and secrets from .env
    config = load_config()
    df = load_transcripts()

    # Step 2: Connect to the AI model defined in your .env file
    llm = load_llm(config)

    # Step 3: Build AI chains — each chain handles one specific evaluation task
    classification_chain = get_classification_chain(llm, config)
    tone_chain = get_tone_chain(llm)
    knowledge_chain = get_knowledge_chain(llm)
    resolution_chain = get_resolution_chain(llm)
    final_chain = get_final_report_chain(llm)

    # Step 4: Run the pipeline — each function adds new columns to the DataFrame
    df = run_classification(df, classification_chain)   # Classify each call
    df = apply_routing(df)                              # Decide which evaluations to run
    df = apply_evaluations(df, tone_chain, knowledge_chain, resolution_chain)  # Score each call
    df = apply_final_reports(df, final_chain)           # Generate summary + recommendations

    # Step 5: Save the final output to an Excel file
    save_dataframe(df)

    print("✅ Pipeline executed successfully!")


if __name__ == "__main__":
    main()