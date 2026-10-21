# ─────────────────────────────────────────────────────────────────────────────
# reporting.py — Final Report Generator
#
# WHAT THIS FILE DOES:
#   After all evaluations are done, this generates a human-readable summary
#   and a list of improvement recommendations for each call.
#
# WHY A SEPARATE REPORTING STEP?
#   The evaluation steps give raw scores and reasoning. The reporting step
#   combines all of that into a polished, actionable summary — like a manager
#   reviewing the scores and writing feedback for the agent.
#
# WHY PromptTemplate?
#   Lets you write a consistent prompt structure that works for every call.
#   The {evaluation_output} placeholder is filled in with the actual scores
#   at runtime.
#
# WHY PydanticOutputParser?
#   Ensures the AI returns a structured object with a "summary" string and
#   a "recommendations" list — not just free-form text we'd have to parse manually.
#
# BEST PRACTICE:
#   Tell the AI clearly what NOT to do (e.g., "Do not repeat scores").
#   Negative instructions help prevent repetitive or low-quality output.
#
# WHEN TO USE THIS:
#   This is the last step in the pipeline. Run it after all evaluation scores
#   have been collected for a call.
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class FinalReport(BaseModel):
    """Holds the AI-generated final report for a single call."""
    summary: str = Field(description="A short, clear summary of how the agent performed overall")
    recommendations: list[str] = Field(description="A list of specific actions the agent can take to improve")


def get_final_report_chain(llm):
    """
    Builds a chain that generates a performance summary and improvement tips.
    Returns a FinalReport object with a summary and list of recommendations.
    """
    parser = PydanticOutputParser(pydantic_object=FinalReport)

    prompt = PromptTemplate(
        template="""
You are a QA manager reviewing customer support calls.

Based on the evaluation results below, generate:

1. A concise summary of the agent's performance
2. A list of actionable recommendations for improvement

Evaluation Data:
{evaluation_output}

IMPORTANT:
- Be specific and practical
- Do not repeat scores
- Focus on improvement

{format_instructions}
""",
        input_variables=["evaluation_output"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser
