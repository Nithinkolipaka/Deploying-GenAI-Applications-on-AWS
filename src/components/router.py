# ─────────────────────────────────────────────────────────────────────────────
# router.py — Evaluation Router
#
# WHAT THIS FILE DOES:
#   Looks at the call type (e.g., "billing", "complaint") and decides which
#   evaluation checks to run for that call. Not every call needs every check.
#
# WHY DO WE NEED ROUTING?
#   Different call types need different evaluations:
#   - A billing call → check if the agent gave correct info and resolved it
#   - A complaint call → check if the agent was empathetic and resolved it
#   - A general query → just check if the info was accurate
#   This avoids running unnecessary evaluations and keeps costs low.
#
# BEST PRACTICE:
#   Use routing logic to keep your pipeline efficient. Only run the evaluations
#   that make sense for each situation.
#
# WHEN TO USE THIS:
#   Called after classification. The result of routing tells the pipeline which
#   evaluation chains to run for each individual call.
# ─────────────────────────────────────────────────────────────────────────────


def route_call(call_type: str) -> list:
    """
    Given a call type, returns the list of evaluations to run.

    Returns a list of evaluation names. Possible values:
      - "tone_empathy"       → Check if agent was polite and empathetic
      - "knowledge_accuracy" → Check if agent gave correct information
      - "resolution_quality" → Check if agent resolved the issue
    """

    if call_type == "billing":
        # Billing calls need accurate info and a clear resolution
        return ["knowledge_accuracy", "resolution_quality"]

    elif call_type == "claims":
        # Claims need both accurate info and a resolved outcome
        return ["knowledge_accuracy", "resolution_quality"]

    elif call_type == "complaint":
        # Complaints are sensitive — empathy and resolution both matter
        return ["tone_empathy", "resolution_quality"]

    elif call_type == "general_query":
        # For simple questions, only check if the answer was accurate
        return ["knowledge_accuracy"]

    else:
        # Default fallback — run at least one check for any unknown type
        return ["knowledge_accuracy"]


def apply_routing(df):
    """
    Adds an 'evaluation_plan' column to the DataFrame.

    Each row gets a list of evaluations to run based on its call type.
    This column is used by the pipeline to decide which chains to invoke.
    """
    df["evaluation_plan"] = df["predicted_call_type"].apply(route_call)
    return df