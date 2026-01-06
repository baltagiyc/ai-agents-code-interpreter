from typing import List
from pydantic import BaseModel, Field


class Reflection(BaseModel):
    missing: str = Field(description="critique of what is missing")
    superfluous: str = Field(description="critique of what is superfluous")


class AnswerQuestion(BaseModel):
    """Answer the question"""

    answer: str = Field(description="around 250 words detailed answer to the question")
    reflection: Reflection = Field(description="your reflection on the initial answer")
    search_queries: List[str] = Field(
        default=[],
        description="1-3 search queries for researching improvements to address the critique of your current answer",
    )


class ReviseAnswer(AnswerQuestion):
    """Revise your original answer to your question."""

    references: List[str] = Field(
        default=[],
        description="Citations motivating your updated answer.",
    )
