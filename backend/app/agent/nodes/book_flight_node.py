from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.tools.flight_tools import book_flight_tool
from langchain_core.messages import SystemMessage, ToolMessage
from app.core.llm import get_chat_llm

def book_flight_node(state: AgentState) -> Dict[str, Any]:
    """Node to execute flight booking."""
    tools = [book_flight_tool]
    llm = get_chat_llm(temperature=0).bind_tools(tools)
    
    system_msg = SystemMessage(content=f"You are a tool caller. The user ID is {state.get('user_id', 'unknown')}. Call the book_flight_tool with the requested flight number.")
    messages = [system_msg] + state["messages"]
    
    response = llm.invoke(messages)
    
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        # Inject user_id if needed
        args = tool_call["args"]
        if "user_id" not in args:
            args["user_id"] = state.get("user_id")
            
        tool_result = book_flight_tool.invoke(args)
        
        tool_msg = ToolMessage(
            content=str(tool_result),
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        )
        return {"messages": [response, tool_msg]}
    else:
        return {"messages": [response]}
