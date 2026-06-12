from typing import TypedDict, Annotated, List, Optional, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class AgentState(TypedDict):
    """
    智能体状态定义。
    messages: 对话历史记录
    intent: 当前分类的用户意图 (例如: "search_flight"查机票, "book_flight"订机票, "chat"闲聊)
    current_flight_query: 可选数据，用于存储机票搜索的参数（如出发地、时间等）
    booking_context: 可选数据，用于存储当前订票的进度和相关上下文信息
    user_id: 用户唯一标识，用于获取或关联用户专属的上下文信息
    """
    messages: Annotated[List[AnyMessage], add_messages]
    intent: Optional[str]
    current_flight_query: Optional[dict]
    booking_context: Optional[dict]
    user_id: str
