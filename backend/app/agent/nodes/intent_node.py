from typing import Dict, Any
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from app.agent.state import AgentState
from app.agent.prompts.intent_prompt import INTENT_SYSTEM_PROMPT
import json

def intent_node(state: AgentState) -> Dict[str, Any]:
    """Node to classify the user's intent."""
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    messages = [SystemMessage(content=INTENT_SYSTEM_PROMPT)] + state["messages"]
    
    response = llm.invoke(messages)
    
    # Simple JSON parsing, assuming LLM outputs valid JSON
    try:
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3]
        intent_data = json.loads(content)
        intent = intent_data.get("intent", "chat")
    except Exception:
        intent = "chat"
        
    return {"intent": intent}
