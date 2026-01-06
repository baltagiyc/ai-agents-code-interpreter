"""
State definition for the Reflexion Agent.

The Reflexion Agent learns from its mistakes by storing lessons in memory
and using them to improve subsequent attempts.
"""
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

from schema import AnswerQuestion, ReviseAnswer


class ReflexionState(TypedDict):
    """
    State for the Reflexion Agent workflow.
    
    This state tracks:
    - The conversation messages
    - The user's original question
    - The current answer being refined
    - The reflection memory (lessons learned from previous attempts)
    - Attempt count and success status
    - Search results from executed queries
    """
    
    # Messages (conversation history) - accumulates with add_messages
    messages: Annotated[list[BaseMessage], add_messages]
    
    # The original user question
    user_question: str
    
    # Current answer (AnswerQuestion or ReviseAnswer object)
    current_answer: AnswerQuestion | ReviseAnswer | None
    
    # Reflection memory - stores lessons learned from failures
    reflexion_memory: List[str]
    
    # Number of attempts made
    attempt_count: int
    
    # Whether the current answer is successful (evaluated)
    is_successful: bool
    
    # Search results from executed queries
    search_results: List[dict] | None

