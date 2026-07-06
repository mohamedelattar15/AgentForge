# AgentForge — Adapter mémoire Redis
# Implémente WorkingMemoryPort et EpisodicMemoryPort via Redis.

import json
from datetime import datetime, timezone
from typing import Any

from agentforge_core.ports.episodic_memory_port import EpisodicMemoryPort
from agentforge_core.ports.working_memory_port import WorkingMemoryPort
from agentforge_core.types import Message

try:
    import redis.asyncio as aioredis
except ImportError:
    aioredis = None  # type: ignore


class RedisWorkingMemory(WorkingMemoryPort):
    """Mémoire de travail Redis — stockage temporaire avec TTL.

    Chaque run est stocké avec une clé `working:{run_id}` et un TTL
    configurable (par défaut 1 heure). Utilise Redis JSON ou simple string.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        ttl_seconds: int = 3600,
        key_prefix: str = "agentforge:working:",
        **kwargs,
    ) -> None:
        """Initialise la connexion Redis.

        Args:
            host: Hôte Redis.
            port: Port Redis.
            db: Index de base de données Redis.
            password: Mot de passe Redis (optionnel).
            ttl_seconds: Durée de vie des clés en secondes.
            key_prefix: Préfixe des clés Redis.
            **kwargs: Paramètres supplémentaires pour redis.from_url().
        """
        if aioredis is None:
            raise ImportError("redis[asyncio] est requis. Installez : pip install redis[hiredis]")

        self._ttl = ttl_seconds
        self._prefix = key_prefix
        self._redis = aioredis.Redis(
            host=host, port=port, db=db, password=password, **kwargs
        )

    def _key(self, run_id: str) -> str:
        """Construit la clé Redis pour un run_id."""
        return f"{self._prefix}{run_id}"

    async def get(self, run_id: str) -> dict:
        """Récupère le contexte d'un run.

        Args:
            run_id: Identifiant du run.

        Returns:
            dict: Contexte stocké, ou dict vide si inexistant.
        """
        data = await self._redis.get(self._key(run_id))
        if data is None:
            return {}
        return json.loads(data)

    async def set(self, run_id: str, context: dict) -> None:
        """Stocke le contexte d'un run avec TTL.

        Args:
            run_id: Identifiant du run.
            context: Contexte à stocker.
        """
        await self._redis.setex(
            self._key(run_id),
            self._ttl,
            json.dumps(context, default=str),
        )

    async def delete(self, run_id: str) -> None:
        """Supprime le contexte d'un run.

        Args:
            run_id: Identifiant du run.
        """
        await self._redis.delete(self._key(run_id))


class RedisEpisodicMemory(EpisodicMemoryPort):
    """Mémoire épisodique Redis — historique des conversations.

    Stocke les messages dans une Redis List par session.
    Utilise RedisJSON pour les métadonnées structurées si disponible.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        max_history: int = 1000,
        key_prefix: str = "agentforge:episodic:",
        **kwargs,
    ) -> None:
        """Initialise la connexion Redis.

        Args:
            host: Hôte Redis.
            port: Port Redis.
            db: Index de base de données.
            password: Mot de passe (optionnel).
            max_history: Nombre maximum de messages par session.
            key_prefix: Préfixe des clés.
            **kwargs: Paramètres supplémentaires.
        """
        if aioredis is None:
            raise ImportError("redis[asyncio] est requis. Installez : pip install redis[hiredis]")

        self._max_history = max_history
        self._prefix = key_prefix
        self._redis = aioredis.Redis(
            host=host, port=port, db=db, password=password, **kwargs
        )

    def _key(self, session_id: str) -> str:
        """Construit la clé Redis pour une session."""
        return f"{self._prefix}{session_id}"

    async def search_hybrid(
        self,
        query: str,
        since: datetime | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        """Recherche dans l'historique par balayage (Redis ne supporte pas
        la recherche full-text native — on balaie les sessions récentes).

        Args:
            query: Texte de recherche.
            since: Date limite.
            top_k: Nombre maximum de résultats.

        Returns:
            list[dict]: Messages pertinents.
        """
        results: list[dict] = []
        cursor: int = 0
        pattern = f"{self._prefix}*"

        while True:
            cursor, keys = await self._redis.scan(cursor, match=pattern, count=100)
            for key in keys:
                messages = await self._redis.lrange(key, 0, -1)
                for msg_bytes in messages:
                    msg = json.loads(msg_bytes)
                    content = msg.get("content", "")
                    if query.lower() in content.lower():
                        msg_time = msg.get("timestamp")
                        if since and msg_time:
                            msg_dt = datetime.fromisoformat(msg_time)
                            if msg_dt < since:
                                continue
                        results.append(msg)
                        if len(results) >= top_k:
                            return results
            if cursor == 0:
                break

        return results[:top_k]

    async def append(self, event: Message) -> None:
        """Ajoute un message à l'historique d'une session.

        Args:
            event: Message à ajouter.
        """
        session_id = event.tool_calls[0].id if event.tool_calls else "default"
        key = self._key(session_id)

        msg_data = {
            "role": event.role,
            "content": event.content,
            "tool_calls": [vars(tc) for tc in event.tool_calls],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        await self._redis.lpush(key, json.dumps(msg_data, default=str))
        await self._redis.ltrim(key, 0, self._max_history - 1)

    async def get_history(
        self, session_id: str, limit: int = 50
    ) -> list[Message]:
        """Récupère l'historique d'une session.

        Args:
            session_id: Identifiant de la session.
            limit: Nombre maximum de messages.

        Returns:
            list[Message]: Messages de l'historique.
        """
        key = self._key(session_id)
        msg_bytes_list = await self._redis.lrange(key, 0, limit - 1)

        messages: list[Message] = []
        for msg_bytes in msg_bytes_list:
            data = json.loads(msg_bytes)
            messages.append(Message(
                role=data.get("role", "user"),
                content=data.get("content", ""),
                tool_calls=[],
            ))

        return list(reversed(messages))
