# AgentForge — Adapter LLM OpenAI-compatible
# Implémente LLMPort via le SDK OpenAI (compatible OpenAI, vLLM, Ollama, etc.).

from collections.abc import AsyncGenerator

from agentforge_core.ports.llm_port import LLMPort
from agentforge_core.types import Message, ToolCall

try:
    from openai import AsyncOpenAI
    from openai.types.chat import ChatCompletionMessageToolCall
except ImportError:
    AsyncOpenAI = None  # type: ignore


class OpenAICompatibleAdapter(LLMPort):
    """Adapter LLM utilisant le SDK OpenAI.

    Compatible avec OpenAI, Azure OpenAI, vLLM, Ollama, et toute API
    implémentant le protocole OpenAI.
    """

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        api_key: str | None = None,
        base_url: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **kwargs,
    ) -> None:
        """Initialise l'adapter OpenAI-compatible.

        Args:
            model: Identifiant du modèle.
            api_key: Clé API (utilise OPENAI_API_KEY env var si non fournie).
            base_url: URL de base (ex: "http://localhost:8000/v1" pour vLLM/Ollama).
            temperature: Température du modèle.
            max_tokens: Nombre maximum de tokens.
            **kwargs: Paramètres supplémentaires passés au client OpenAI.
        """
        if AsyncOpenAI is None:
            raise ImportError(
                "Le package 'openai' est requis. Installez-le avec : pip install openai"
            )

        self._model = model
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._extra_kwargs = kwargs

        client_kwargs = {}
        if api_key:
            client_kwargs["api_key"] = api_key
        if base_url:
            client_kwargs["base_url"] = base_url

        self._client = AsyncOpenAI(**client_kwargs)

    def _format_messages(self, messages: list[Message]) -> list[dict]:
        """Convertit les messages internes au format OpenAI.

        Args:
            messages: Messages internes.

        Returns:
            list[dict]: Messages au format OpenAI.
        """
        formatted = []
        for m in messages:
            msg: dict = {"role": m.role, "content": m.content}
            if m.tool_calls:
                msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.name, "arguments": str(tc.arguments)},
                    }
                    for tc in m.tool_calls
                ]
            formatted.append(msg)
        return formatted

    def _parse_response(self, response) -> Message:
        """Convertit une réponse OpenAI en Message interne.

        Args:
            response: Réponse brute de openai.chat.completions.create().

        Returns:
            Message: Message formaté.
        """
        choice = response.choices[0]
        content = choice.message.content or ""

        tool_calls = []
        if choice.message.tool_calls:
            for tc in choice.message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=tc.function.arguments,
                ))

        return Message(
            role="assistant",
            content=content,
            tool_calls=tool_calls,
        )

    async def complete(self, messages: list[Message], tools: list[dict] | None = None) -> Message:
        """Appelle le LLM et retourne une réponse complète.

        Args:
            messages: Messages échangés.
            tools: Schémas d'outils optionnels.

        Returns:
            Message: Réponse générée.
        """
        kwargs = {
            "model": self._model,
            "messages": self._format_messages(messages),
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        kwargs.update(self._extra_kwargs)

        try:
            response = await self._client.chat.completions.create(**kwargs)
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(
                f"Erreur OpenAI lors de l'appel à '{self._model}' : {e!s}"
            ) from e

    async def stream(self, messages: list[Message], tools: list[dict] | None = None) -> AsyncGenerator[str, None]:
        """Appelle le LLM en streaming.

        Args:
            messages: Messages échangés.
            tools: Schémas d'outils optionnels.

        Yields:
            str: Tokens de la réponse.
        """
        kwargs = {
            "model": self._model,
            "messages": self._format_messages(messages),
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
            "stream": True,
        }
        if tools:
            kwargs["tools"] = tools

        kwargs.update(self._extra_kwargs)

        try:
            stream = await self._client.chat.completions.create(**kwargs)
            async for chunk in stream:
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            raise RuntimeError(f"Erreur streaming OpenAI : {e!s}") from e
