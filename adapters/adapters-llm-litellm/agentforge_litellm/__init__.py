# AgentForge — Adapter LLM LiteLLM
# Implémente LLMPort via LiteLLM (support multi-provider).

from collections.abc import AsyncGenerator

from agentforge_core.ports.llm_port import LLMPort
from agentforge_core.types import Message, ToolCall

try:
    import litellm
except ImportError:
    litellm = None  # type: ignore


class LiteLLMAdapter(LLMPort):
    """Adapter LLM utilisant LiteLLM pour supporter de multiples providers.

    Supporte OpenAI, Anthropic, Google, Ollama, AWS Bedrock, Azure, etc.
    Configuration via le paramètre model (ex: "gpt-4o", "claude-3-opus", "ollama/llama3").
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
        """Initialise l'adapter LiteLLM.

        Args:
            model: Identifiant du modèle (ex: "gpt-4o", "claude-3-sonnet").
            api_key: Clé API (optionnelle, utilise la variable d'env sinon).
            base_url: URL de base personnalisée (pour proxies/compatibles).
            temperature: Température du modèle (0.0 à 1.0).
            max_tokens: Nombre maximum de tokens dans la réponse.
            **kwargs: Paramètres supplémentaires passés à litellm.completion().
        """
        if litellm is None:
            raise ImportError(
                "Le package 'litellm' est requis. Installez-le avec : pip install litellm"
            )

        self._model = model
        self._api_key = api_key
        self._base_url = base_url
        self._temperature = temperature
        self._max_tokens = max_tokens
        self._extra_kwargs = kwargs

    def _build_completion_kwargs(self, messages: list[Message], tools: list[dict] | None = None) -> dict:
        """Construit les arguments d'appel pour litellm.completion().

        Args:
            messages: Liste des messages.
            tools: Schémas d'outils optionnels.

        Returns:
            dict: Arguments formatés pour LiteLLM.
        """
        kwargs: dict = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": self._temperature,
            "max_tokens": self._max_tokens,
        }

        if self._api_key:
            kwargs["api_key"] = self._api_key
        if self._base_url:
            kwargs["base_url"] = self._base_url
        if tools:
            kwargs["tools"] = tools

        kwargs.update(self._extra_kwargs)
        return kwargs

    def _parse_response(self, response) -> Message:
        """Convertit une réponse LiteLLM en Message interne.

        Args:
            response: Réponse brute de litellm.completion().

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
        """Appelle le LLM via LiteLLM et retourne une réponse complète.

        Args:
            messages: Messages échangés.
            tools: Schémas d'outils optionnels.

        Returns:
            Message: Réponse générée.
        """
        kwargs = self._build_completion_kwargs(messages, tools)

        try:
            response = await litellm.acompletion(**kwargs)  # type: ignore
            return self._parse_response(response)
        except Exception as e:
            raise RuntimeError(f"Erreur LiteLLM lors de l'appel à '{self._model}' : {e!s}") from e

    async def stream(self, messages: list[Message], tools: list[dict] | None = None) -> AsyncGenerator[str, None]:
        """Appelle le LLM en streaming via LiteLLM.

        Args:
            messages: Messages échangés.
            tools: Schémas d'outils optionnels.

        Yields:
            str: Tokens de la réponse.
        """
        kwargs = self._build_completion_kwargs(messages, tools)
        kwargs["stream"] = True

        try:
            async for chunk in await litellm.acompletion(**kwargs):  # type: ignore
                delta = chunk.choices[0].delta if chunk.choices else None
                if delta and delta.content:
                    yield delta.content
        except Exception as e:
            raise RuntimeError(f"Erreur streaming LiteLLM : {e!s}") from e
