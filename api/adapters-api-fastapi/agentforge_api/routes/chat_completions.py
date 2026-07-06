# AgentForge — API FastAPI : endpoint /v1/chat/completions
# Endpoint compatible OpenAI pour interagir avec l'agent.

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.types import Message

from ..openai_schema_adapter import OpenAISchemaAdapter

router = APIRouter()


class ChatCompletionRequest(BaseModel):
    """Requête compatible OpenAI Chat Completion."""
    model: str = "default"
    messages: list[dict]
    temperature: float | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    stream: bool = False
    tools: list[dict] | None = None
    tool_choice: str | dict | None = None
    user: str | None = None


class ChatCompletionResponse(BaseModel):
    """Réponse compatible OpenAI Chat Completion."""
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[dict]
    usage: dict | None = None


@router.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """Endpoint compatible OpenAI pour les conversations.

    Convertit la requête OpenAI en RunContext, exécute le lifecycle
    complet de l'agent, et retourne une réponse au format OpenAI.

    Args:
        request: Requête au format Chat Completion OpenAI.

    Returns:
        ChatCompletionResponse: Réponse formatée OpenAI.

    Raises:
        HTTPException: Si l'exécution échoue.
    """
    # 1. Accéder au registre via l'état de l'application
    from fastapi import Request as FastAPIRequest
    from fastapi.concurrency import run_in_threadpool

    # Note: le registry est accessible via app.state dans une vraie app
    # Ici on utilise un simple adaptateur pour la démo

    # 2. Convertir la requête OpenAI → RunContext
    context = OpenAISchemaAdapter.to_run_context(request.model_dump())

    # 3. Exécuter le lifecycle complet
    # (Dans une vraie implémentation, on utiliserait le registry)
    try:
        # Simulation : retourner un message simple basé sur le dernier message
        last_msg = request.messages[-1]["content"] if request.messages else ""
        response_msg = Message(
            role="assistant",
            content=f"Réponse à : {last_msg[:100]}",
        )

        # 4. Convertir la réponse → format OpenAI
        response = OpenAISchemaAdapter.to_openai_response(response_msg)
        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
