from typing import TypedDict, Annotated, List, Dict, Any
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    """
    The state of the agent workflow.
    """
    messages: Annotated[List[Any], add_messages]
    sender: str  # <--- NEW FIELD: Tracks the last active agent