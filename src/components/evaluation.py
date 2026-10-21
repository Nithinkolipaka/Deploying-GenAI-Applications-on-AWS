# ─────────────────────────────────────────────────────────────────────────────
# evaluation.py — AI Quality Evaluators (Tone, Knowledge, Resolution)
#
# WHAT THIS FILE DOES:
#   Contains three separate AI evaluation chains, each scoring a different
#   aspect of a customer support call on a scale of 1 to 5.
#
#   1. Tone & Empathy   — Was the agent polite and empathetic?
#   2. Knowledge Accuracy — Did the agent give correct, clear information?
#   3. Resolution Quality — Did the agent actually solve the customer's problem?
#
# WHY THREE SEPARATE CHAINS?
#   Each evaluation focuses on a different skill. Keeping them separate means:
#   - You can run only the ones needed for each call type (see router.py)
#   - Each prompt is focused and gives better AI results
#   - You can update one without affecting the others
#
# WHY PromptTemplate?
#   Lets you write a reusable prompt with placeholders ({transcript}).
#   The same prompt structure works for every call — just swap the transcript.
#
# WHY PydanticOutputParser?
#   Converts the AI's plain text response into a structured Python object
#   with typed fields (score as int, reasoning as str). This avoids errors
#   from trying to extract values manually from unstructured text.
#
# BEST PRACTICE:
#   Keep the scoring criteria clear in the prompt. The AI performs better
#   when you explicitly list what to look for (bullet points help).
#
# WHEN TO USE THIS:
#   These chains are called by the pipeline for each transcript after
#   classification and routing have decided which evaluations to run.
# ─────────────────────────────────────────────────────────────────────────────

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────────────────
# Tone & Empathy Evaluation
# ─────────────────────────────────────────────────────────────────────────────

class ToneEvaluation(BaseModel):
    """Holds the AI's tone evaluation result."""
    score: int = Field(description="Score from 1 (very poor) to 5 (excellent)")
    reasoning: str = Field(description="Brief explanation for the score given")


def get_tone_chain(llm):
    """
    Builds a chain that evaluates the agent's tone and empathy.
    Returns a ToneEvaluation object with a score and reasoning.
    """
    parser = PydanticOutputParser(pydantic_object=ToneEvaluation)

    prompt = PromptTemplate(
        template="""
You are a QA evaluator for customer support calls.

Evaluate the agent's tone and empathy in the following transcript.

Consider:
- Did the agent acknowledge the customer's issue?
- Was the tone polite and professional?
- Did the agent show empathy?

Transcript:
{transcript}

{format_instructions}
""",
        input_variables=["transcript"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser


# ─────────────────────────────────────────────────────────────────────────────
# Knowledge Accuracy Evaluation
# ─────────────────────────────────────────────────────────────────────────────

class KnowledgeEvaluation(BaseModel):
    """Holds the AI's knowledge accuracy evaluation result."""
    score: int = Field(description="Score from 1 (very poor) to 5 (excellent)")
    reasoning: str = Field(description="Brief explanation for the score given")


def get_knowledge_chain(llm):
    """
    Builds a chain that evaluates the accuracy and clarity of the agent's answers.
    Returns a KnowledgeEvaluation object with a score and reasoning.
    """
    parser = PydanticOutputParser(pydantic_object=KnowledgeEvaluation)

    prompt = PromptTemplate(
        template="""
You are a QA evaluator for customer support calls.

Evaluate the agent's knowledge accuracy and clarity.

Consider:
- Did the agent provide correct and relevant information?
- Was the explanation clear and easy to understand?
- Did the agent avoid vague or misleading statements?

IMPORTANT:
- If the transcript does not contain enough information, give a moderate score (2 or 3) and explain why.

Transcript:
{transcript}

{format_instructions}
""",
        input_variables=["transcript"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser


# ─────────────────────────────────────────────────────────────────────────────
# Resolution Quality Evaluation
# ─────────────────────────────────────────────────────────────────────────────

class ResolutionEvaluation(BaseModel):
    """Holds the AI's resolution quality evaluation result."""
    score: int = Field(description="Score from 1 (very poor) to 5 (excellent)")
    reasoning: str = Field(description="Brief explanation for the score given")


def get_resolution_chain(llm):
    """
    Builds a chain that evaluates whether the agent resolved the customer's issue.
    Returns a ResolutionEvaluation object with a score and reasoning.
    """
    parser = PydanticOutputParser(pydantic_object=ResolutionEvaluation)

    prompt = PromptTemplate(
        template="""
You are a QA evaluator for customer support calls.

Evaluate the resolution quality of the agent.

Consider:
- Did the agent fully resolve the customer's issue?
- Were next steps clearly communicated?
- Did the agent confirm resolution before ending?

Transcript:
{transcript}

{format_instructions}
""",
        input_variables=["transcript"],
        partial_variables={
            "format_instructions": parser.get_format_instructions()
        }
    )

    return prompt | llm | parser