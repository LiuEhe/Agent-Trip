from typing import Dict, Any
from app.agent.state import AgentState
from app.agent.prompts.reply_prompt import REPLY_SYSTEM_PROMPT
from langchain_core.messages import SystemMessage
from app.core.llm import get_chat_llm

def reply_node(state: AgentState) -> Dict[str, Any]:
    """Node to generate the final natural language reply."""
    llm = get_chat_llm(temperature=0.5)
    messages = [SystemMessage(content=REPLY_SYSTEM_PROMPT)] + state["messages"]
    
    response = llm.invoke(messages)
    
    return {"messages": [response]}
