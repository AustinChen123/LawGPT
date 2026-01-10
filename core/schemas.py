import operator
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage

class AgentState(TypedDict):
    """
    Represents the state of our agent.
    Moved here to avoid circular dependencies.
    """
    messages: Annotated[Sequence[BaseMessage], operator.add]
    documents: Annotated[list[dict], operator.add]
    intent: str # 'legal_query' or 'general_chat'
