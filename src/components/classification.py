# ─────────────────────────────────────────────────────────────────────────────
# classification.py — Call Type Classifier
#
# WHAT THIS FILE DOES:
#   Reads a customer support transcript and asks the AI to classify it into
#   one of the predefined call types (e.g., billing, claims, complaint).
#
# WHY PromptTemplate?
#   PromptTemplate lets you create a reusable text template with placeholders
#   like {transcript} and {labels}. Instead of writing the full prompt every
#   time, you just fill in the blanks. This keeps prompts clean and consistent.
#
# WHY PydanticOutputParser?
#   After the AI responds, we need to turn its text into a proper Python object
#   with typed fields. PydanticOutputParser does this automatically by telling
#   the AI exactly what format to respond in, then parsing the result.
#   This prevents errors from messy or unexpected AI responses.
#
# WHY Pydantic BaseModel + Field?
#   BaseModel defines the structure of the AI's output like a form.
#   Field lets you describe what each field means — this description is
#   sent to the AI so it knows what to fill in. Think of it as a typed schema.
#
# BEST PRACTICE:
#   Always use structured output (Pydantic) instead of parsing raw text.
#   It makes your code much more reliable and easier to debug.
#
# WHEN TO USE THIS:
#   Use this as the first step in the pipeline to label each call before
#   running specific evaluations on it.
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# This defines the shape of what we expect the AI to return
class ClassificationOutput(BaseModel):
    call_type: str = Field(description="Type of customer call (e.g., billing, complaint)")
    confidence: float = Field(description="How confident the AI is — a number between 0 and 1")


def get_classification_chain(llm, config):
    """
    Builds and returns the classification chain.

    The chain works like a pipeline:
      PromptTemplate → LLM → PydanticOutputParser
    Each step passes its output to the next step automatically.
    """

    # Parser converts the AI's text response into a ClassificationOutput object
    parser = PydanticOutputParser(pydantic_object=ClassificationOutput)

    # The prompt tells the AI what to do and what format to respond in
    prompt = PromptTemplate(
        template="""
You are a call classification assistant.

Classify the following customer support transcript into one of these categories:
{labels}

Transcript:
{transcript}

{format_instructions}
""",
        input_variables=["transcript"],
        partial_variables={
            # These values are fixed at chain creation time (not per call)
            "format_instructions": parser.get_format_instructions(),
            "labels": config["classification"]["labels"]
        }
    )

    # Chain: fill in the prompt → send to AI → parse the result
    classification_chain = prompt | llm | parser
    return classification_chain