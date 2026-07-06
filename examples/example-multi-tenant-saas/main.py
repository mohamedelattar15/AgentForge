#!/usr/bin/env python
"""
AgentForge — Example: Multi-Tenant SaaS Agent
Agent SaaS multi-tenant avec isolation des données et rate limiting.
"""

import asyncio
import time
from collections import defaultdict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentforge_core.config.loader import ConfigLoader
from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.registry.adapter_registry import AdapterRegistry
from agentforge_core.types import Message


class RateLimiter:
    """Rate limiter simple par tenant."""

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self._max = max_requests
        self._window = window_seconds
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def is_allowed(self, tenant_id: str) -> bool:
        """Vérifie si le tenant peut faire une requête."""
        now = time.time()
        window_start = now - self._window

        # Nettoyer les entrées expirées
        self._buckets[tenant_id] = [
            t for t in self._buckets[tenant_id] if t > window_start
        ]

        if len(self._buckets[tenant_id]) >= self._max:
            return False

        self._buckets[tenant_id].append(now)
        return True


class MultiTenantAgent:
    """Agent SaaS multi-tenant."""

    def __init__(self, config_path: str):
        self.config = ConfigLoader.load(config_path)
        self.registry = AdapterRegistry()
        self.registry.resolve(self.config)
        self.rate_limiter = RateLimiter(max_requests=10)

        # Taux par tenant (requêtes/minute)
        self.tenant_limits = {
            "free": 5,
            "pro": 50,
            "enterprise": 500,
        }

    async def handle_request(self, tenant_id: str, plan: str, query: str) -> str:
        """Traite une requête pour un tenant.

        Args:
            tenant_id: Identifiant du tenant.
            plan: Plan d'abonnement (free, pro, enterprise).
            query: Question de l'utilisateur.

        Returns:
            str: Réponse.
        """
        # Rate limiting
        limit = self.tenant_limits.get(plan, 5)
        limiter = RateLimiter(max_requests=limit)
        if not limiter.is_allowed(tenant_id):
            return f"⛔ Rate limit atteint ({limit} req/min). Passez au plan supérieur."

        # Créer le contexte avec isolation
        context = RunContext(
            user_query=query,
            session_id=f"{tenant_id}-{plan}",
            metadata={
                "tenant_id": tenant_id,
                "plan": plan,
            },
        )

        # Réponse simulée (avec vrai LLM, utiliser le lifecycle complet)
        response = Message(
            role="assistant",
            content=f"[Tenant: {tenant_id} | Plan: {plan}] Réponse à : {query[:100]}",
        )

        return response.content


async def main():
    """Point d'entrée de l'exemple multi-tenant."""
    config_path = Path(__file__).parent / "config.yaml"

    print("🏢 AgentForge - Multi-Tenant SaaS Agent")
    print("=" * 50)

    agent = MultiTenantAgent(str(config_path))

    # Simulation de requêtes multi-tenant
    tenants = [
        ("tenant-alpha", "enterprise", "Quel est le chiffre d'affaires du Q3 ?"),
        ("tenant-beta", "pro", "Crée un rapport de ventes"),
        ("tenant-gamma", "free", "Bonjour !"),
        ("tenant-alpha", "enterprise", "Analyse les tendances du marché"),
    ]

    print("\n📊 Simulation de requêtes multi-tenant :\n")

    for tenant_id, plan, query in tenants:
        print(f"▶  [{tenant_id}] ({plan}) {query}")
        response = await agent.handle_request(tenant_id, plan, query)
        print(f"✓  {response}\n")

    # Test rate limiting
    print("⏱  Test de rate limiting (plan free = 5 req/min)...")
    for i in range(7):
        response = await agent.handle_request("tenant-gamma", "free", f"Requête #{i + 1}")
        print(f"   Requête #{i + 1}: {response[:50]}...")

    return 0


if __name__ == "__main__":
    asyncio.run(main())
