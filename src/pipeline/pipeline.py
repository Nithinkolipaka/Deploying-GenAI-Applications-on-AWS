# ─────────────────────────────────────────────────────────────────────────────
# pipeline.py — Core Pipeline Logic
#
# WHAT THIS FILE DOES:
#   Contains the actual step-by-step functions that process call transcripts
#   through the AI evaluation pipeline. Each function handles one stage:
#
#   Stage 1 — Classification:  Label each call (billing, complaint, etc.)
#   Stage 2 — Evaluation:      Score each call on tone, knowledge, resolution
#   Stage 3 — Final Report:    Generate a summary and improvement tips
#
# WHY SEPARATE FUNCTIONS FOR EACH STAGE?
#   Keeping each stage as its own function makes the code easier to test,
#   debug, and reuse. You can run just one stage at a time if needed.
#
# WHY tqdm?
#   tqdm shows a progress bar in the terminal so you can see how many calls
#   have been processed. It's especially helpful when running hundreds of rows.
#   Without it, the script would appear frozen with no feedback.
#
# WHY TRY/EXCEPT IN EACH LOOP?
#   AI calls can sometimes fail (timeout, bad format, etc.). Wrapping each call
#   in try/except means one bad row won't crash the whole pipeline.
#   The failed row gets None values so you can spot and fix it later.
#
# WHY df.merge()?
#   We process results separately and then merge them back into the main
#   DataFrame using "call_id" as the key. This keeps the data clean and avoids
#   issues with modifying a DataFrame while iterating over it.
#
# BEST PRACTICE:
#   Always catch errors inside row-by-row loops. Log the error so you know
#   which row failed, and continue processing the rest.
#
# WHEN TO USE THIS:
#   These functions are called by inference.py (for the API) and main.py
#   (for command-line usage).
# ─────────────────────────────────────────────────────────────────────────────

import pandas as pd
from tqdm import tqdm


# ─────────────────────────────────────────────────────────────────────────────
# Stage 1 — Classification
# ─────────────────────────────────────────────────────────────────────────────

def run_classification(df: pd.DataFrame, classification_chain):
    """
    Sends each transcript to the AI to classify the call type.

    Adds two new columns to the DataFrame:
      - predicted_call_type: e.g., "billing", "complaint"
      - confidence: AI's confidence score between 0 and 1
    """
    results = []

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Classifying Calls"):
        try:
            output = classification_chain.invoke({
                "transcript": row["transcript"]
            })

            results.append({
                "call_id": row["call_id"],
                "predicted_call_type": output.call_type,
                "confidence": output.confidence
            })

        except Exception as e:
            # Log the error and store None so the pipeline can continue
            print(f"❌ Error at row {i}: {e}")

            results.append({
                "call_id": row["call_id"],
                "predicted_call_type": None,
                "confidence": None
            })

    # Merge classification results back into the original DataFrame
    results_df = pd.DataFrame(results)
    df = df.merge(results_df, on="call_id")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Stage 2 — Evaluations
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluations(transcript, eval_plan, tone_chain, knowledge_chain, resolution_chain):
    """
    Runs only the relevant evaluation checks for a single transcript.

    eval_plan is a list like ["tone_empathy", "resolution_quality"] — only
    the checks listed here will be run. This avoids unnecessary AI calls.

    Returns a dict with results for each check that was run.
    """
    results = {}

    if "tone_empathy" in eval_plan:
        try:
            tone_result = tone_chain.invoke({"transcript": transcript})
            results["tone"] = tone_result.model_dump()
        except Exception as e:
            results["tone"] = {"error": str(e)}

    if "knowledge_accuracy" in eval_plan:
        try:
            knowledge_result = knowledge_chain.invoke({"transcript": transcript})
            results["knowledge"] = knowledge_result.model_dump()
        except Exception as e:
            results["knowledge"] = {"error": str(e)}

    if "resolution_quality" in eval_plan:
        try:
            resolution_result = resolution_chain.invoke({"transcript": transcript})
            results["resolution"] = resolution_result.model_dump()
        except Exception as e:
            results["resolution"] = {"error": str(e)}

    return results


def apply_evaluations(df, tone_chain, knowledge_chain, resolution_chain):
    """
    Applies evaluation logic to every row in the DataFrame.

    Each row must already have an 'evaluation_plan' column (set by router.py).
    Adds an 'evaluation_output' column containing the scores and reasoning.
    """
    evaluation_outputs = []

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Running Evaluations"):
        output = run_evaluations(
            transcript=row["transcript"],
            eval_plan=row["evaluation_plan"],
            tone_chain=tone_chain,
            knowledge_chain=knowledge_chain,
            resolution_chain=resolution_chain
        )

        evaluation_outputs.append({
            "call_id": row["call_id"],
            "evaluation_output": output
        })

    eval_df = pd.DataFrame(evaluation_outputs)

    # Merge evaluation results back into the main DataFrame
    df = df.merge(eval_df, on="call_id")

    return df


# ─────────────────────────────────────────────────────────────────────────────
# Stage 3 — Final Reporting
# ─────────────────────────────────────────────────────────────────────────────

def generate_final_report(evaluation_output, final_chain):
    """
    Generates a performance summary and improvement tips for a single call.

    Takes the evaluation scores as input and returns a summary + recommendations.
    """
    try:
        result = final_chain.invoke({
            "evaluation_output": evaluation_output
        })

        return {
            "summary": result.summary,
            "recommendations": result.recommendations
        }

    except Exception as e:
        # Return None values if the report generation fails for this row
        return {
            "summary": None,
            "recommendations": None,
            "error": str(e)
        }


def apply_final_reports(df, final_chain):
    """
    Applies final report generation to every row in the DataFrame.

    Adds 'summary' and 'recommendations' columns to the DataFrame.
    """
    final_outputs = []

    for i, row in tqdm(df.iterrows(), total=len(df), desc="Generating Final Reports"):
        output = generate_final_report(
            evaluation_output=row["evaluation_output"],
            final_chain=final_chain
        )

        final_outputs.append({
            "call_id": row["call_id"],
            "summary": output.get("summary"),
            "recommendations": output.get("recommendations")
        })

    final_df = pd.DataFrame(final_outputs)

    # Merge final report results back into the main DataFrame
    df = df.merge(final_df, on="call_id")

    return df