from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.nodes.intent_node import intent_node
from app.agent.nodes.search_flight_node import search_flight_node
from app.agent.nodes.book_flight_node import book_flight_node
from app.agent.nodes.reply_node import reply_node
from langgraph.checkpoint.memory import MemorySaver

def route_intent(state: AgentState) -> str:
    """Determine the next node based on intent."""
    intent = state.get("intent")
    if intent == "search_flight":
        return "search_flight"
    elif intent == "book_flight":
        return "book_flight"
    else:
        return "reply"

def build_agent_graph(checkpointer=None):
    """Build and compile the LangGraph for the flight booking agent."""
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent", intent_node)
    workflow.add_node("search_flight", search_flight_node)
    workflow.add_node("book_flight", book_flight_node)
    workflow.add_node("reply", reply_node)
    
    # Define edges
    workflow.add_edge(START, "intent")
    
    # Conditional edge based on intent
    workflow.add_conditional_edges(
        "intent",
        route_intent,
        {
            "search_flight": "search_flight",
            "book_flight": "book_flight",
            "reply": "reply"
        }
    )
    
    # After action nodes, generate a final reply
    workflow.add_edge("search_flight", "reply")
    workflow.add_edge("book_flight", "reply")
    
    # After reply, end the graph
    workflow.add_edge("reply", END)
    
    # Compile with memory (checkpointing)
    if checkpointer is None:
        checkpointer = MemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)
    
    return graph
