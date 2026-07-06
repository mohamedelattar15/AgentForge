# Adapters Matrix — AgentForge

> Tableau de compatibilité et de trade-offs pour chaque port et ses adapters.

---

## 1. LLM

| Adapter | Latence | Scalabilité | Coût | Complexité | Providers |
|---|---|---|---|---|---|
| LiteLLM | Moyenne | Haute | Faible | Faible | 100+ (OpenAI, Anthropic, Google, Ollama...) |
| OpenAI-compatible | Faible | Haute | Moyen | Faible | OpenAI, vLLM, Ollama, Azure |

**Recommandation :** LiteLLM pour le multi-provider, OpenAI SDK pour les déploiements ciblant uniquement OpenAI.

---

## 2. Orchestration

| Adapter | Latence | Scalabilité | Coût | Complexité | Reprise |
|---|---|---|---|---|---|
| Minimal | Très faible | Faible | Nul | Nulle | Aucune |
| LangGraph | Faible | Moyenne | Nul | Moyenne | Checkpoint mémoire |
| Temporal | Moyenne | Très haute | Nul | Haute | Durable (historique) |

**Recommandation :** Minimal pour le développement, LangGraph pour les agents complexes, Temporal pour la production résiliente.

---

## 3. Working Memory

| Adapter | Latence | Scalabilité | Persistance | TTL |
|---|---|---|---|---|
| In-memory | Très faible | Très faible | Non | — |
| Redis | Très faible | Haute | Optionnelle (RDB/AOF) | Configurable |

---

## 4. Semantic Memory

| Adapter | Latence | Scalabilité | Type de recherche | Embeddings |
|---|---|---|---|---|
| SQLite | Faible | Faible | Textuelle (LIKE) | Non |
| Qdrant | Faible | Haute | Vectorielle (cosinus) | Oui (configurable) |
| PostgreSQL/pgvector | Faible | Haute | Vectorielle (cosinus) | Oui (configurable) |

**Recommandation :** SQLite pour le développement, Qdrant pour la performance, PostgreSQL pour la solution unifiée.

---

## 5. Episodic Memory

| Adapter | Latence | Scalabilité | Recherche |
|---|---|---|---|
| SQLite | Faible | Faible | Textuelle (LIKE) |
| Redis | Très faible | Haute | Balayage de listes |
| PostgreSQL | Faible | Haute | ILIKE + index |

---

## 6. Procedural Memory

| Adapter | Source | Format |
|---|---|---|
| Default | Dossier local | Fichiers `.md` |

---

## 7. Tool Registry

| Adapter | Source | Protocole |
|---|---|---|
| Default | Aucun | — |
| MCP | Serveurs MCP | stdio ou SSE |

---

## 8. Event Bus

| Adapter | Type | Persistance | Distribué |
|---|---|---|---|
| In-process | Synchrone | Non | Non |
| NATS JetStream | Asynchrone | Oui | Oui |

---

## 9. Trace

| Adapter | Destination | Hébergement | UI |
|---|---|---|---|
| Default | Fichier JSON local | Local | Aucune |
| Langfuse | Langfuse Cloud/Self-hosted | SaaS ou self | Oui |
| OpenTelemetry | OTLP (Jaeger, Tempo) | Self-hosted | Oui (Grafana) |

---

## 10. Eval

| Adapter | Méthode | Clé API requise |
|---|---|---|
| Default | Toujours 1.0 | Non |
| Ragas | LLM-as-Judge | Oui (OpenAI) |
| DeepEval | LLM-as-Judge | Oui (OpenAI) |

---

## 11. Analytics

| Adapter | Stockage | Requêtes |
|---|---|---|
| Default | Aucun (no-op) | — |
| ClickHouse | OLAP columnar | Agrégations temps réel |

---

## Matrice de compatibilité croisée

| Stack | LLM | Orchestration | Working Mem | Semantic Mem | Episodic Mem | Event Bus | Trace | Eval | Analytics |
|---|---|---|---|---|---|---|---|---|---|
| **Minimal** | LiteLLM | Minimal | In-memory | SQLite | SQLite | In-process | Default | Default | Désactivé |
| **Startup** | LiteLLM | Minimal | In-memory | SQLite | SQLite | In-process | Default | Default | Désactivé |
| **Enterprise** | LiteLLM | Temporal | Redis | Qdrant | PostgreSQL | NATS | Langfuse | Ragas | ClickHouse |
