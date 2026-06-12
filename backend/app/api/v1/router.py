from __future__ import annotations

from uuid import uuid4

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage


api_router = APIRouter()


class ChatMessageIn(BaseModel):
    role: str = Field(..., description="message role: user or system")
    content: str = Field(..., description="message content")


class AgentChatRequest(BaseModel):
    messages: list[ChatMessageIn] = Field(default_factory=list)
    user_id: str | None = Field(default=None)
    thread_id: str | None = Field(default=None)


class AgentChatResponse(BaseModel):
    thread_id: str
    output: dict


def _serialize_messages(messages: list) -> list[dict]:
    serialized = []
    for message in messages:
        role = "assistant"
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, SystemMessage):
            role = "system"
        elif isinstance(message, AIMessage):
            role = "assistant"
        serialized.append({"role": role, "content": getattr(message, "content", str(message))})
    return serialized


@api_router.get("/health")
async def health_check():
    return {"status": "ok"}


@api_router.post("/agent/chat", response_model=AgentChatResponse)
async def agent_chat(payload: AgentChatRequest, request: Request):
    graph = getattr(request.app.state, "agent_graph", None)
    if graph is None:
        return AgentChatResponse(thread_id="", output={"error": "agent graph not initialized"})

    thread_id = payload.thread_id or payload.user_id or str(uuid4())
    messages = []
    for item in payload.messages:
        role = item.role.lower()
        if role == "system":
            messages.append(SystemMessage(content=item.content))
        else:
            messages.append(HumanMessage(content=item.content))

    if not messages:
        messages = [HumanMessage(content="")]

    result = await graph.ainvoke(
        {
            "messages": messages,
            "intent": None,
            "current_flight_query": None,
            "booking_context": None,
            "user_id": payload.user_id or "anonymous",
        },
        config={"configurable": {"thread_id": thread_id}},
    )
    output = dict(result)
    if "messages" in output:
        output["messages"] = _serialize_messages(output["messages"])
    return AgentChatResponse(thread_id=thread_id, output=output)
