# v0.5 — Orchestration avancée + Event Bus + Analytics

> **Statut : ✅ Terminé**
> **Date : 2026-07-06**
> **Tests : 34/34 passés** (v0.5 uniquement)

---

## 1. Objectif

Support des workflows complexes (LangGraph, Temporal), communication asynchrone (NATS), et analytique OLAP (ClickHouse).

- **LangGraph** : graphe d'état avec noeuds Planner→Executor→Reflector→Verifier
- **Temporal** : workflows durables avec activités, retries, timeouts
- **NATS** : event bus asynchrone avec JetStream pour la persistance
- **ClickHouse** : analytique OLAP pour les métriques d'exécution
- **Recette enterprise** : stack complète avec docker-compose

---

## 2. Fichiers créés (25 fichiers)

### 2.1 Adapter Orchestration LangGraph

| Fichier | Description |
|---|---|
| `adapters/adapters-orchestration-langgraph/pyproject.toml` | Dépendances : `langgraph>=0.2.0`, `langchain-core>=0.3.0` |
| `adapters/adapters-orchestration-langgraph/agentforge_langgraph/__init__.py` | `LangGraphOrchestrator` (OrchestrationPort) avec graphe StateGraph |
| `adapters/adapters-orchestration-langgraph/tests/test_langgraph.py` | 4 tests |

**Détails :**
- Graphe : `planner → executor → reflector → verifier → END`
- Arêtes conditionnelles : `reflector` peut renvoyer vers `executor` si correction
- `verifier` peut renvoyer vers `executor` si échec (max_retries configurable)
- Checkpointing optionnel via `MemorySaver` pour reprise sur erreur
- `recursion_limit` à 100 pour les runs complexes

### 2.2 Adapter Orchestration Temporal

| Fichier | Description |
|---|---|
| `adapters/adapters-orchestration-temporal/pyproject.toml` | Dépendances : `temporalio>=1.7.0` |
| `adapters/adapters-orchestration-temporal/agentforge_temporal/__init__.py` | `TemporalOrchestrator` (OrchestrationPort) |
| `adapters/adapters-orchestration-temporal/agentforge_temporal/workflows/__init__.py` | `AgentWorkflow` — workflow Temporal principal |
| `adapters/adapters-orchestration-temporal/agentforge_temporal/activities/__init__.py` | 5 activités : plan, execute, llm, memory, tool |
| `adapters/adapters-orchestration-temporal/tests/test_temporal.py` | 3 tests |

**Détails :**
- Workflow avec 3 phases : planification → exécution séquentielle → réponse
- 5 activités : `plan_activity`, `execute_activity`, `llm_activity`, `memory_activity`, `tool_activity`
- Timeouts configurables par activité (30s plan, 120s execute)
- Configuration : `host`, `namespace`, `task_queue`, `workflow_timeout`

### 2.3 Adapter Event Bus NATS

| Fichier | Description |
|---|---|
| `adapters/adapters-eventbus-nats/pyproject.toml` | Dépendances : `nats-py>=2.9.0` |
| `adapters/adapters-eventbus-nats/agentforge_nats/__init__.py` | `NATSEventBus` (EventBusPort) avec JetStream |
| `adapters/adapters-eventbus-nats/tests/test_nats.py` | 4 tests |

**Détails :**
- Publication sur topics : `agent.{topic}`
- Stream JetStream automatiquement créé : `agent.>` (tous les sujets)
- Subscription durable avec consumer prefix configurable
- Fallback NATS core si JetStream non disponible
- Sérialisation JSON des événements

### 2.4 Adapter Analytics ClickHouse

| Fichier | Description |
|---|---|
| `adapters/adapters-analytics-clickhouse/pyproject.toml` | Dépendances : `clickhouse-driver>=0.2.6` |
| `adapters/adapters-analytics-clickhouse/agentforge_clickhouse/__init__.py` | `ClickHouseAnalytics` (AnalyticsPort) |
| `adapters/adapters-analytics-clickhouse/agentforge_clickhouse/migrations/0001_init_analytics.sql` | Table MergeTree avec 13 colonnes |
| `adapters/adapters-analytics-clickhouse/tests/test_clickhouse.py` | 5 tests |

**Détails :**
- Table `run_metrics` avec 13 colonnes (latency_ms, token_count, eval_score, etc.)
- Moteur MergeTree ordonné par `(timestamp, run_id)`
- Requêtes d'agrégation : total_runs, avg_latency, avg_tokens, avg_score
- Filtres : period (24h, 7d, 30d), status, model
- Base et table auto-créées

### 2.5 Déploiement

| Fichier | Description |
|---|---|
| `recipes/recipe-enterprise.yaml` | Configuration complète : Temporal + Redis + Qdrant + PostgreSQL + NATS + Langfuse + ClickHouse |
| `deployment/docker-compose.minimal.yaml` | Stack minimale (API uniquement) |
| `deployment/docker-compose.enterprise.yaml` | 7 services : agentforge, redis, qdrant, postgres, temporal, nats, clickhouse |
| `deployment/kubernetes/base/` | Structure Kustomize (base + dev/staging/prod overlays) |

---

## 3. Décisions techniques

### 3.1 LangGraph vs Temporal

| Critère | LangGraph | Temporal |
|---|---|---|
| **Complexité** | Faible (bibliothèque Python) | Élevée (serveur + SDK) |
| **Persistance** | Optionnelle (MemorySaver) | Intégrée (historique des workflows) |
| **Reprise** | Checkpoint en mémoire | Durable (reprise après crash) |
| **Scalabilité** | Mono-process | Distribuée |
| **Cas d'usage** | Dev rapide, agents simples | Production, runs longs, résilience |

### 3.2 Pourquoi NATS plutôt que Kafka/RabbitMQ ?
NATS est plus léger, plus facile à déployer (un seul binaire), et son mode JetStream offre de la persistance sans la complexité de Kafka. Idéal pour la communication entre composants d'un agent.

### 3.3 Pourquoi ClickHouse pour l'analytique ?
ClickHouse est optimisé pour les requêtes OLAP (agrégations sur de grands volumes). La table `run_metrics` peut stocker des millions de runs et répondre aux requêtes de dashboard en millisecondes.

### 3.4 Architecture docker-compose enterprise
Les 7 services sont interconnectés :
- `agentforge` dépend de tous les autres
- `temporal` dépend de `postgres` pour son stockage
- Volumes nommés pour la persistance des données
- Healthchecks pour la synchronisation des démarrages

---

## 4. Tests — Résultats

### 4.1 Résultat : 34/34 ✅

```
adapters-orchestration-langgraph (4)    ✅✅✅✅
adapters-orchestration-temporal (3)     ✅✅✅
adapters-eventbus-nats (4)              ✅✅✅✅
adapters-analytics-clickhouse (5)       ✅✅✅✅✅
core (18 — v0.1)                        ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
```

### 4.2 Bugs corrigés

| Bug | Cause | Correction |
|---|---|---|
| `RunContext` import dans `orchestration_port.py` | Importé depuis `types.py` au lieu de `lifecycle/run_context.py` | Correction du chemin d'import |
| `should_stop()` sans await | Méthode async testée sans `await` | Ajout de `await` dans les tests |
| `workflow_method` inexistant | N'existe pas dans temporalio 1.7+ | Suppression de l'import inutile |
| NATS MagicMock non awaitable | `jetstream()` retournait un MagicMock au lieu d'AsyncMock | Correction de la gestion d'erreur dans `_connect()` + AsyncMock dans les tests |

---

## 5. Livrables

- [x] `adapters/adapters-orchestration-langgraph/` — LangGraphOrchestrator + 4 tests
- [x] `adapters/adapters-orchestration-temporal/` — TemporalOrchestrator + workflows + activities + 3 tests
- [x] `adapters/adapters-eventbus-nats/` — NATSEventBus + 4 tests
- [x] `adapters/adapters-analytics-clickhouse/` — ClickHouseAnalytics + migration + 5 tests
- [x] `recipes/recipe-enterprise.yaml` — Stack complète
- [x] `deployment/docker-compose.minimal.yaml` — Stack minimale
- [x] `deployment/docker-compose.enterprise.yaml` — 7 services
- [x] `deployment/kubernetes/` — Structure Kustomize
- [x] **34 tests passés** (v0.5)

---

## 6. Notes pour la suite

- LangGraph nécessite `langgraph` et `langchain-core` — dépendances lourdes mais puissantes
- Temporal nécessite un serveur Temporal en cours d'exécution pour les tests d'intégration
- NATS JetStream nécessite NATS avec l'option `-js` activée
- ClickHouse utilise le port natif 9000 (pas le port HTTP 8123)
- La v1.0 ajoutera la documentation complète, les exemples, et la stabilisation
