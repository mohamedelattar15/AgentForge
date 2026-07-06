# Example: Multi-Tenant SaaS Agent

> Agent SaaS multi-tenant avec isolation complète.
> Utilise la recette enterprise : Temporal, Redis, Qdrant, PostgreSQL, NATS, ClickHouse.

---

## Description

Cet exemple montre un agent SaaS multi-tenant avec :
- **Isolation des données** par `tenant_id` (mémoires séparées)
- **Rate limiting** par tenant
- **Analytics** par tenant (ClickHouse)
- **Déploiement Kubernetes**

## Architecture

```
                    ┌──────────────┐
                    │   API Layer   │
                    │  FastAPI      │
                    └──────┬───────┘
                           │ tenant_id
              ┌────────────┼────────────┐
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Tenant A  │ │ Tenant B  │ │ Tenant C  │
        │ (isolation)│ │ (isolation)│ │ (isolation)│
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              └────────────┼────────────┘
                           ▼
                    ┌──────────────┐
                    │   Temporal   │
                    │  (workflows) │
                    └──────────────┘
```

## Prérequis

- Python 3.11+
- Docker & Docker Compose (pour l'infrastructure)
- AgentForge + tous les adapters installés

## Déploiement

```bash
# Démarrer l'infrastructure
docker-compose -f ../../deployment/docker-compose.enterprise.yaml up -d

# Lancer l'agent
cd examples/example-multi-tenant-saas
python main.py
```
