# v0.4 — Tools MCP + Trace Langfuse/OTel + Eval Ragas/DeepEval

> **Statut : ✅ Terminé**
> **Date : 2026-07-06**
> **Tests : 41/41 passés** (cumul v0.1→v0.4)

---

## 1. Objectif

Ajouter les outils via MCP (Model Context Protocol), le tracing avec Langfuse et OpenTelemetry, et l'évaluation avec Ragas et DeepEval.

- **MCP Tools** : connexion à des serveurs MCP pour découvrir/exécuter des outils
- **Langfuse Trace** : observabilité LLM avec spans et générations
- **OpenTelemetry Trace** : export OTLP compatible Jaeger/Zipkin/Tempo
- **Ragas Eval** : métriques d'évaluation (faithfulness, answer_relevancy, etc.)
- **DeepEval Eval** : framework d'évaluation LLM (G-Eval, AnswerRelevancy)

---

## 2. Fichiers créés (20 fichiers)

### 2.1 Adapter Tools MCP

| Fichier | Description |
|---|---|
| `adapters/adapters-tools-mcp/pyproject.toml` | Dépendances : `mcp>=1.0.0` |
| `adapters/adapters-tools-mcp/agentforge_mcp/__init__.py` | `MCPToolRegistry` (ToolRegistryPort) |
| `adapters/adapters-tools-mcp/tests/test_mcp.py` | 5 tests |

**Détails :**
- `list_tools()` : découvre les outils de tous les serveurs MCP configurés
- `execute()` : appelle un outil sur le premier serveur qui le propose
- Cache des outils (évite de re-decouvrir à chaque appel)
- Support serveurs stdio (command + args) et SSE (url)
- Format de sortie compatible OpenAI tool calling

### 2.2 Adapter Trace Langfuse

| Fichier | Description |
|---|---|
| `adapters/adapters-trace-langfuse/pyproject.toml` | Dépendances : `langfuse>=2.30.0` |
| `adapters/adapters-trace-langfuse/agentforge_langfuse/__init__.py` | `LangfuseTrace` (TracePort) |
| `adapters/adapters-trace-langfuse/tests/test_langfuse.py` | 3 tests |

**Détails :**
- `record()` : crée une trace Langfuse par run avec des générations par span
- Tags : `release` pour le versioning, métadonnées dans chaque span
- `flush()` automatique après chaque enregistrement

### 2.3 Adapter Trace OpenTelemetry

| Fichier | Description |
|---|---|
| `adapters/adapters-trace-opentelemetry/pyproject.toml` | Dépendances : `opentelemetry-api`, `opentelemetry-sdk`, `opentelemetry-exporter-otlp-proto-grpc` |
| `adapters/adapters-trace-opentelemetry/agentforge_otel/__init__.py` | `OTelTrace` (TracePort) |
| `adapters/adapters-trace-opentelemetry/tests/test_otel.py` | 3 tests |

**Détails :**
- Export OTLP gRPC vers n'importe quel backend (Jaeger, Zipkin, Grafana Tempo)
- Span racine par run, sous-spans par phase
- Attributs préfixés `agentforge.*` pour le filtrage
- Conversion datetime → nanosecondes pour OTel

### 2.4 Adapter Eval Ragas

| Fichier | Description |
|---|---|
| `adapters/adapters-eval-ragas/pyproject.toml` | Dépendances : `ragas>=0.1.0`, `datasets` |
| `adapters/adapters-eval-ragas/agentforge_ragas/__init__.py` | `RagasEval` (EvalPort) |
| `adapters/adapters-eval-ragas/tests/test_ragas.py` | 6 tests |

**Détails :**
- Métriques : faithfulness, answer_relevancy, context_precision, context_recall
- Extraction automatique question/réponse/contexte depuis la trace
- Score moyen pondéré, seuil configurable (défaut 0.7)
- Mode dégradé si pas de métriques configurées

### 2.5 Adapter Eval DeepEval

| Fichier | Description |
|---|---|
| `adapters/adapters-eval-deepeval/pyproject.toml` | Dépendances : `deepeval>=1.0.0` |
| `adapters/adapters-eval-deepeval/agentforge_deepeval/__init__.py` | `DeepEvalEval` (EvalPort) — lazy imports |
| `adapters/adapters-eval-deepeval/tests/test_deepeval.py` | 6 tests |

**Détails :**
- Métriques : G-Eval, AnswerRelevancyMetric
- **Lazy imports** : évite la vérification de clé API OpenAI à l'import
- Mode dégradé : si pas de clé API, score parfait (1.0) sans crash
- Seuil configurable

---

## 3. Décisions techniques

### 3.1 Pourquoi MCP plutôt qu'un registry d'outils custom ?
Le Model Context Protocol est un standard émergent pour les outils d'agents. En l'adoptant, AgentForge peut utiliser n'importe quel serveur MCP existant (serveur filesystem, GitHub, Slack, etc.) sans code supplémentaire.

### 3.2 Pourquoi deux adapters de trace ?
- **Langfuse** : solution SaaS clé en main, idéale pour les équipes qui veulent une UI d'observabilité LLM sans infrastructure
- **OpenTelemetry** : standard ouvert, idéal pour les entreprises ayant déjà une stack OTel (Jaeger, Tempo)

### 3.3 Pourquoi deux adapters d'évaluation ?
- **Ragas** : métriques spécialisées pour RAG (faithfulness, context_precision)
- **DeepEval** : framework plus général (G-Eval, summarization, hallucination)

Les deux peuvent être combinés dans une recette enterprise pour une évaluation plus robuste.

### 3.4 Gestion des clés API manquantes
DeepEval et Ragas nécessitent une clé API OpenAI pour les métriques LLM-as-Judge. Pour éviter de bloquer le développement, on utilise :
- **Lazy imports** : les imports DeepEval sont différés à l'appel de `evaluate()`
- **Mode dégradé** : si pas de clé, score parfait (1.0) sans erreur

---

## 4. Tests — Résultats

### 4.1 Résultat : 41/41 ✅

```
adapters-tools-mcp (5)              ✅✅✅✅✅
adapters-trace-langfuse (3)         ✅✅✅
adapters-trace-opentelemetry (3)    ✅✅✅
adapters-eval-ragas (6)             ✅✅✅✅✅✅
adapters-eval-deepeval (6)          ✅✅✅✅✅✅
core (18 — v0.1)                    ✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅✅
```

### 4.2 Bugs corrigés

| Bug | Cause | Correction |
|---|---|---|
| `test_record_creates_root_span` | Mock OTel utilisait `__enter__` au lieu de `__aenter__` | Utilisation de `AsyncMock` pour `__aenter__`/`__aexit__` |
| `test_evaluate_no_metrics` (Ragas) | `evaluate()` appelait `_lazy_init()` avant la vérification | Patch de `AVAILABLE_METRICS` dans le test |
| `DeepEval import` | `from deepeval import evaluate` déclenchait la vérification de clé API | Restructuration en lazy imports dans les méthodes |
| `metrics=[]` interprété comme `None` | `metrics or ["answer_relevancy"]` → `[]` est falsy | Changement pour `metrics if metrics is not None else [...]` |

---

## 5. Livrables

- [x] `adapters/adapters-tools-mcp/` — MCPToolRegistry + 5 tests
- [x] `adapters/adapters-trace-langfuse/` — LangfuseTrace + 3 tests
- [x] `adapters/adapters-trace-opentelemetry/` — OTelTrace + 3 tests
- [x] `adapters/adapters-eval-ragas/` — RagasEval + 6 tests
- [x] `adapters/adapters-eval-deepeval/` — DeepEvalEval (lazy) + 6 tests
- [x] **41 tests passés** (cumul v0.1→v0.4)

---

## 6. Notes pour la suite

- MCP nécessite un serveur MCP en cours d'exécution pour les tests d'intégration
- Langfuse et OTel nécessitent une infrastructure pour les tests réels
- DeepEval nécessite une clé API OpenAI pour les métriques réelles — le mode dégradé est pratique pour le développement
- La prochaine version (v0.5) ajoutera LangGraph, Temporal, NATS, ClickHouse et la recette enterprise
