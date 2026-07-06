# AgentForge — API FastAPI : adaptateur de schéma OpenAI
# Conversion bidirectionnelle entre le schéma OpenAI et les objets internes.

import time
from collections.abc import Generator
from uuid import uuid4

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.types import Message, ToolCall


class OpenAISchemaAdapter:
    """Adaptateur de schéma entre OpenAI et les objets internes d'AgentForge."""

    @staticmethod
    def to_run_context(request: dict) -> RunContext:
        """Convertit une requête OpenAI Chat Completion en RunContext.

        Args:
            request: Dictionnaire représentant une requête OpenAI.

        Returns:
            RunContext: Contexte de run initialisé.
        """
        messages = request.get("messages", [])
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                last_user_msg = m.get("content", "")
                break

        context = RunContext(
            user_query=last_user_msg,
            session_id=request.get("user"),
            messages=[Message(role=m["role"], content=m.get("content", "")) for m in messages],
        )

        # Appliquer les paramètres OpenAI comme guardrails
        max_tokens = request.get("max_tokens")
        if max_tokens:
            context.token_budget = max_tokens * 3  # approximation tokens → caractères

        return context

    @staticmethod
    def to_openai_response(message: Message) -> dict:
        """Convertit un Message interne en réponse OpenAI Chat Completion.

        Args:
            message: Message interne à convertir.

        Returns:
            dict: Réponse au format OpenAI.
        """
        choice = {
            "index": 0,
            "message": {
                "role": message.role,
                "content": message.content,
            },
            "finish_reason": "stop",
        }

        if message.tool_calls:
            choice["message"]["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": str(tc.arguments),
                    },
                }
                for tc in message.tool_calls
            ]

        return {
            "id": f"chatcmpl-{uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "agentforge",
            "choices": [choice],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
        }

    @staticmethod
    def to_openai_stream(deltas: list[str]) -> Generator[dict, None, None]:
        """Convertit des tokens de streaming en événements SSE OpenAI.

        Args:
            deltas: Liste de tokens à streamer.

        Yields:
            dict: Événement SSE au format OpenAI.
        """
        for i, delta in enumerate(deltas):
            yield {
                "id": f"chatcmpl-{uuid4().hex[:12]}",
                "object": "chat.completion.chunk",
                "created": int(time.time()),
                "model": "agentforge",
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": delta} if delta else {},
                        "finish_reason": None,
                    }
                ],
            }

        # Dernier chunk : finish_reason = "stop"
        yield {
            "id": f"chatcmpl-{uuid4().hex[:12]}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": "agentforge",
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }
