# AgentForge — Adapter Analytics ClickHouse
# Implémente AnalyticsPort via ClickHouse (OLAP).

import json
from datetime import datetime, timezone

from agentforge_core.ports.analytics_port import AnalyticsPort

try:
    from clickhouse_driver import Client as CHClient
    from clickhouse_driver.errors import ServerException
except ImportError:
    CHClient = None  # type: ignore
    ServerException = None  # type: ignore


class ClickHouseAnalytics(AnalyticsPort):
    """Analytique via ClickHouse — agrégation de métriques à grande échelle.

    Stocke les métriques d'exécution (latence, tokens, scores) dans une table
    OLAP optimisée pour les requêtes d'agrégation et les tableaux de bord.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 9000,
        database: str = "agentforge",
        table: str = "run_metrics",
        user: str = "default",
        password: str = "",
    ) -> None:
        """Initialise le client ClickHouse.

        Args:
            host: Hôte ClickHouse.
            port: Port natif ClickHouse (9000, pas HTTP).
            database: Nom de la base de données.
            table: Nom de la table de métriques.
            user: Utilisateur ClickHouse.
            password: Mot de passe.
        """
        if CHClient is None:
            raise ImportError("clickhouse-driver est requis. Installez : pip install clickhouse-driver")

        self._host = host
        self._port = port
        self._database = database
        self._table = table
        self._user = user
        self._password = password
        self._client: CHClient | None = None

    def _get_client(self) -> CHClient:
        """Retourne le client ClickHouse (connecte si nécessaire).

        Returns:
            CHClient: Client connecté.
        """
        if self._client is None:
            self._client = CHClient(
                host=self._host,
                port=self._port,
                user=self._user,
                password=self._password,
            )
            self._init_database()
        return self._client

    def _init_database(self) -> None:
        """Crée la base et la table si elles n'existent pas."""
        client = self._client
        assert client is not None

        client.execute(f"CREATE DATABASE IF NOT EXISTS {self._database}")

        client.execute(f"""
            CREATE TABLE IF NOT EXISTS {self._database}.{self._table} (
                run_id String,
                timestamp DateTime,
                agent_version String,
                user_query String,
                status String,
                latency_ms Float64,
                token_count UInt32,
                iteration_count UInt32,
                tool_call_count UInt32,
                eval_score Float64,
                llm_model String,
                session_id String,
                metadata String
            ) ENGINE = MergeTree()
            ORDER BY (timestamp, run_id)
        """)

    async def ingest(self, metrics: dict) -> None:
        """Ingère des métriques dans ClickHouse.

        Args:
            metrics: Dictionnaire de métriques.
        """
        client = self._get_client()

        row = {
            "run_id": metrics.get("run_id", ""),
            "timestamp": datetime.now(timezone.utc),
            "agent_version": metrics.get("agent_version", "0.5.0"),
            "user_query": metrics.get("user_query", ""),
            "status": metrics.get("status", ""),
            "latency_ms": float(metrics.get("latency_ms", 0)),
            "token_count": int(metrics.get("token_count", 0)),
            "iteration_count": int(metrics.get("iteration_count", 0)),
            "tool_call_count": int(metrics.get("tool_call_count", 0)),
            "eval_score": float(metrics.get("eval_score", 0.0)),
            "llm_model": metrics.get("llm_model", ""),
            "session_id": metrics.get("session_id", ""),
            "metadata": json.dumps(metrics.get("metadata", {})),
        }

        client.execute(
            f"INSERT INTO {self._database}.{self._table} VALUES",
            [row],
        )

    async def query(self, filters: dict) -> list[dict]:
        """Interroge les métriques agrégées.

        Args:
            filters: Filtres (period, status, model...).

        Returns:
            list[dict]: Résultats agrégés.
        """
        client = self._get_client()

        conditions = ["1 = 1"]
        params: dict = {}

        if "period" in filters:
            period = filters["period"]
            if period == "24h":
                conditions.append("timestamp >= now() - INTERVAL 24 HOUR")
            elif period == "7d":
                conditions.append("timestamp >= now() - INTERVAL 7 DAY")
            elif period == "30d":
                conditions.append("timestamp >= now() - INTERVAL 30 DAY")

        if "status" in filters:
            conditions.append("status = %(status)s")
            params["status"] = filters["status"]

        if "model" in filters:
            conditions.append("llm_model = %(model)s")
            params["model"] = filters["model"]

        where_clause = " AND ".join(conditions)

        rows = client.execute(f"""
            SELECT
                count() AS total_runs,
                avg(latency_ms) AS avg_latency,
                avg(token_count) AS avg_tokens,
                avg(eval_score) AS avg_score,
                sum(tool_call_count) AS total_tool_calls
            FROM {self._database}.{self._table}
            WHERE {where_clause}
        """, params)

        if rows:
            row = rows[0]
            return [{
                "total_runs": row[0],
                "avg_latency_ms": float(row[1]) if row[1] else 0,
                "avg_tokens": float(row[2]) if row[2] else 0,
                "avg_eval_score": float(row[3]) if row[3] else 0,
                "total_tool_calls": row[4],
            }]

        return []
