# AgentForge — Adapter mémoire sémantique Qdrant
# Implémente SemanticMemoryPort via Qdrant (base vectorielle).

import json
from uuid import uuid4

from agentforge_core.ports.semantic_memory_port import SemanticMemoryPort

try:
    from qdrant_client import AsyncQdrantClient
    from qdrant_client.models import (
        Distance,
        PointStruct,
        ScoredPoint,
        VectorParams,
        Filter as QdrantFilter,
        FieldCondition,
        MatchValue,
    )
except ImportError:
    AsyncQdrantClient = None  # type: ignore
    Distance = None
    PointStruct = None
    ScoredPoint = None
    VectorParams = None
    QdrantFilter = None
    FieldCondition = None
    MatchValue = None


class QdrantSemanticMemory(SemanticMemoryPort):
    """Mémoire sémantique vectorielle via Qdrant.

    Stocke les faits avec des embeddings pour la recherche par similarité.
    Supporte les filtres metadata, la pagination, et le scoring.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        collection: str = "semantic_memory",
        embedding_size: int = 1536,
        distance: str = "Cosine",
        api_key: str | None = None,
        prefer_grpc: bool = False,
    ) -> None:
        """Initialise le client Qdrant.

        Args:
            host: Hôte Qdrant.
            port: Port HTTP/gRPC.
            collection: Nom de la collection.
            embedding_size: Taille des vecteurs d'embedding.
            distance: Métrique de distance (Cosine, Dot, Euclid).
            api_key: Clé API Qdrant Cloud (optionnelle).
            prefer_grpc: Utiliser gRPC si disponible.
        """
        if AsyncQdrantClient is None:
            raise ImportError("qdrant-client est requis. Installez : pip install qdrant-client")

        self._collection = collection
        self._embedding_size = embedding_size

        self._client = AsyncQdrantClient(
            host=host,
            port=port,
            api_key=api_key,
            prefer_grpc=prefer_grpc,
        )

    async def _ensure_collection(self) -> None:
        """Crée la collection si elle n'existe pas."""
        collections = await self._client.get_collections()
        existing = [c.name for c in collections.collections]

        if self._collection not in existing:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=VectorParams(
                    size=self._embedding_size,
                    distance=Distance.COSINE if Distance else None,
                ),
            )

    def _simple_embed(self, text: str) -> list[float]:
        """Génère un embedding simple basé sur la fréquence des caractères.

        NOTE: Ceci est un embedding de fallback pour le développement.
        En production, utilisez un vrai modèle d'embedding (OpenAI, etc.).

        Args:
            text: Texte à encoder.

        Returns:
            list[float]: Vecteur d'embedding.
        """
        import hashlib

        # Embedding déterministe basé sur le hash du texte
        # NE PAS UTILISER EN PRODUCTION — remplacez par un vrai modèle
        vector = [0.0] * self._embedding_size
        words = text.split()
        for i, word in enumerate(words[:self._embedding_size]):
            h = hashlib.md5(word.encode()).hexdigest()
            vector[i] = (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1
        return vector

    async def search(
        self, query: str, top_k: int = 5, filters: dict | None = None
    ) -> list[dict]:
        """Recherche des faits par similarité vectorielle.

        Args:
            query: Texte de recherche.
            top_k: Nombre maximum de résultats.
            filters: Filtres metadata (ex: {"source": "web"}).

        Returns:
            list[dict]: Faits pertinents avec score.
        """
        await self._ensure_collection()
        query_vector = self._simple_embed(query)

        qdrant_filter = None
        if filters:
            conditions = [
                FieldCondition(
                    key=f"metadata.{k}",
                    match=MatchValue(value=v),
                )
                for k, v in filters.items()
            ]
            qdrant_filter = QdrantFilter(must=conditions) if FieldCondition else None

        results = await self._client.search(
            collection_name=self._collection,
            query_vector=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
        )

        return [
            {
                "id": hit.id,
                "content": hit.payload.get("content", ""),
                "metadata": json.loads(hit.payload.get("metadata", "{}")),
                "score": hit.score,
            }
            for hit in results
        ]

    async def upsert(self, fact: dict) -> None:
        """Ajoute ou met à jour un fait.

        Args:
            fact: Dictionnaire avec 'id', 'content', optionnellement 'metadata'.
        """
        await self._ensure_collection()
        fact_id = fact.get("id", uuid4().hex)
        content = fact.get("content", "")
        metadata = json.dumps(fact.get("metadata", {}))
        vector = self._simple_embed(content)

        point = PointStruct(
            id=fact_id,
            vector=vector,
            payload={
                "content": content,
                "metadata": metadata,
            },
        )

        await self._client.upsert(
            collection_name=self._collection,
            points=[point],
        )

    async def delete(self, fact_id: str) -> None:
        """Supprime un fait.

        Args:
            fact_id: Identifiant du fait à supprimer.
        """
        await self._ensure_collection()
        await self._client.delete(
            collection_name=self._collection,
            points_selector=[fact_id],
        )
