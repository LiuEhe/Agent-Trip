from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    """
    Agent state definition.
    messages: conversation history
    intent: current classified intent ("search_flight", "book_flight", "chat")
    current_flight_query: optional data storing flight search parameters
    booking_context: optional data storing current booking progress
    user_id: user ID to fetch user context
    """
    messages: Annotated[List[AnyMessage], add_messages]
    intent: Optional[str]
    current_flight_query: Optional[dict]
    booking_context: Optional[dict]
    user_id: str
