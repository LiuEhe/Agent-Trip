from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.tools.flight_tools import search_flight_tool
from langchain_core.messages import SystemMessage, ToolMessage
from app.core.llm import get_chat_llm

def search_flight_node(state: AgentState) -> Dict[str, Any]:
    """Node to execute flight search."""
    tools = [search_flight_tool]
    llm = get_chat_llm(temperature=0).bind_tools(tools)
    
    # We ask the LLM to extract parameters and call the search tool
    system_msg = SystemMessage(content="You are a tool caller. Extract flight details from the user's message and call the search_flight_tool.")
    messages = [system_msg] + state["messages"]
    
    response = llm.invoke(messages)
    
    if response.tool_calls:
        # For simplicity, we directly invoke the tool here instead of routing to a separate ToolNode
        # In a more complex setup, you'd yield the AI message and let LangGraph route to the ToolNode
        tool_call = response.tool_calls[0]
        tool_result = search_flight_tool.invoke(tool_call["args"])
        
        tool_msg = ToolMessage(
            content=str(tool_result),
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        )
        return {"messages": [response, tool_msg]}
    else:
        return {"messages": [response]}
