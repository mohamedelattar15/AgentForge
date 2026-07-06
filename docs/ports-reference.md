# Ports Reference — AgentForge

> Spécification exhaustive de chaque port du framework.
> Les ports sont des classes abstraites (ABC) définies dans `core/agentforge_core/ports/`.

---

## 1. LLMPort (`llm_port.py`)

Contrat pour l'appel à n'importe quel modèle de langage.

```python
class LLMPort(ABC):
    async def complete(self, messages: list[Message], tools: list[dict] | None = None) -> Message
    async def stream(self, messages: list[Message], tools: list[dict] | None = None) -> AsyncGenerator[str, None]
```

### Paramètres

| Paramètre | Type | Description |
|---|---|---|
| `messages` | `list[Message]` | Messages échangés (contexte + historique) |
| `tools` | `list[dict] \| None` | Schémas d'outils au format OpenAI (optionnel) |

### Retour

| Méthode | Retour | Description |
|---|---|---|
| `complete` | `Message` | Réponse complète du LLM |
| `stream` | `AsyncGenerator[str, None]` | Tokens de la réponse en streaming |

### Garanties
- Thread-safe (appels concurrents possibles)
- Timeout : 120 secondes par défaut (configurable)

### Erreurs
- `LLMError` : erreur API (rate limit, timeout, auth)
- `RuntimeError` : erreur générique d'appel

### Adapters disponibles
| Adapter | Détails |
|---|---|
| `LiteLLMAdapter` | Multi-provider (OpenAI, Anthropic, Ollama...) |
| `OpenAICompatibleAdapter` | SDK OpenAI direct, compatible vLLM/Ollama |

---

## 2. OrchestrationPort (`orchestration_port.py`)

Contrat pour la boucle d'exécution (orchestrateur).

```python
class OrchestrationPort(ABC):
    async def run(self, context: RunContext) -> Message
    async def should_stop(self, state: dict) -> bool
```

### Paramètres

| Paramètre | Type | Description |
|---|---|---|
| `context` | `RunContext` | Contexte complet du run (état, mémoires, outils) |
| `state` | `dict` | État courant de la boucle (itération, tokens...) |

### Retour

| Méthode | Retour | Description |
|---|---|---|
| `run` | `Message` | Réponse finale après exécution |
| `should_stop` | `bool` | True si la boucle doit s'arrêter |

### Garanties
- L'appel à `run` est idempotent (même contexte = même résultat)
- `should_stop` est appelée après chaque itération

### Erreurs
- `GuardrailViolationError` : si un guardrail est atteint
- `TimeoutError` : si le temps d'exécution dépasse le timeout

### Adapters disponibles
| Adapter | Détails |
|---|---|
| `MinimalOrchestrator` | Boucle synchrone simple (défaut) |
| `LangGraphOrchestrator` | Graphe d'état avec noeuds Planner→Executor→Reflector→Verifier |
| `TemporalOrchestrator` | Workflow Temporal durable |

---

## 3. WorkingMemoryPort (`working_memory_port.py`)

Contrat pour la mémoire de travail (contexte éphémère du run).

```python
class WorkingMemoryPort(ABC):
    async def get(self, run_id: str) -> dict
    async def set(self, run_id: str, context: dict) -> None
    async def delete(self, run_id: str) -> None
```

### Garanties
- `get` retourne toujours un dict (jamais None)
- `get` sur un run_id inexistant retourne `{}`
- `set` écrase toute valeur existante pour le même run_id
- `delete` est idempotent (supprimer 2x ne cause pas d'erreur)

### Adapters disponibles
| Adapter | Persistance | TTL |
|---|---|---|
| `InMemoryWorkingMemory` | Aucune (RAM) | — |
| `RedisWorkingMemory` | Redis | Configurable (défaut 1h) |

---

## 4. SemanticMemoryPort (`semantic_memory_port.py`)

Contrat pour la mémoire sémantique (faits durables, connaissances).

```python
class SemanticMemoryPort(ABC):
    async def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]
    async def upsert(self, fact: dict) -> None
    async def delete(self, fact_id: str) -> None
```

### Paramètres search

| Paramètre | Type | Défaut | Description |
|---|---|---|---|
| `query` | `str` | — | Texte de recherche |
| `top_k` | `int` | 5 | Nombre maximum de résultats |
| `filters` | `dict \| None` | None | Filtres metadata (ex: `{"source": "web"}`) |

### Retour search
```python
[
    {
        "id": str,
        "content": str,
        "metadata": dict,
        "score": float,       # 0.0 à 1.0
        "created_at": str,    # ISO format
    }
]
```

### Adapters disponibles
| Adapter | Type de recherche |
|---|---|
| `SQLiteSemanticMemory` | Textuelle (LIKE) — défaut |
| `QdrantSemanticMemory` | Vectorielle (cosinus) |
| `PostgresSemanticMemory` | Vectorielle (pgvector, cosinus) |

---

## 5. EpisodicMemoryPort (`episodic_memory_port.py`)

Contrat pour la mémoire épisodique (historique des conversations).

```python
class EpisodicMemoryPort(ABC):
    async def search_hybrid(self, query: str, since: datetime | None = None, top_k: int = 10) -> list[dict]
    async def append(self, event: Message) -> None
    async def get_history(self, session_id: str, limit: int = 50) -> list[Message]
```

### Garanties
- `get_history` retourne les messages triés par date croissante
- `append` est thread-safe (plusieurs appels concurrents possibles)
- `search_hybrid` sans `since` cherche dans tout l'historique

### Adapters disponibles
| Adapter | Stockage |
|---|---|
| `SQLiteEpisodicMemory` | SQLite — défaut |
| `RedisEpisodicMemory` | Redis List |
| `PostgresEpisodicMemory` | PostgreSQL JSONB |

---

## 6. ProceduralMemoryPort (`procedural_memory_port.py`)

Contrat pour la mémoire procédurale (compétences, instructions).

```python
class ProceduralMemoryPort(ABC):
    async def load(self, skill_name: str) -> str
    async def list_skills(self) -> list[str]
```

### Adapter disponible
| Adapter | Source |
|---|---|
| `DefaultProceduralMemory` | Fichiers `.md` dans un dossier local |

---

## 7. ToolRegistryPort (`tool_registry_port.py`)

Contrat pour le catalogue d'outils exécutables.

```python
class ToolRegistryPort(ABC):
    async def list_tools(self) -> list[dict]
    async def execute(self, name: str, args: dict) -> ToolResult
```

### Format de retour list_tools
```python
[
    {
        "type": "function",
        "function": {
            "name": str,
            "description": str,
            "parameters": dict,  # JSON Schema
        }
    }
]
```

### Adapters disponibles
| Adapter | Source des outils |
|---|---|
| `DefaultToolRegistry` | Aucun outil (vide) |
| `MCPToolRegistry` | Serveurs MCP (Model Context Protocol) |

---

## 8. EventBusPort (`event_bus_port.py`)

Contrat pour la communication asynchrone interne.

```python
class EventBusPort(ABC):
    async def publish(self, topic: str, event: dict) -> None
    async def subscribe(self, topic: str, handler: Callable) -> None
```

### Adapters disponibles
| Adapter | Type |
|---|---|
| `InProcessEventBus` | In-process (synchrone) — défaut |
| `NATSEventBus` | NATS JetStream (durable, distribué) |

---

## 9. TracePort (`trace_port.py`)

Contrat pour l'émission de traces (observabilité).

```python
class TracePort(ABC):
    async def record(self, run_id: str, spans: list[Span]) -> None
```

### Adapters disponibles
| Adapter | Destination |
|---|---|
| `DefaultTrace` | Fichier JSON local |
| `LangfuseTrace` | Langfuse (cloud ou auto-hébergé) |
| `OTelTrace` | OpenTelemetry OTLP (Jaeger, Tempo...) |

---

## 10. EvalPort (`eval_port.py`)

Contrat pour l'évaluation de la qualité des runs.

```python
class EvalPort(ABC):
    async def evaluate(self, run_trace: dict) -> EvalResult
```

### Retour
```python
EvalResult(
    score=float,      # 0.0 à 1.0
    verdict=str,      # "passed", "needs_improvement", "failed"
    diagnosis=str,    # Explication du score
    passed=bool,      # True si score >= threshold
)
```

### Adapters disponibles
| Adapter | Méthode |
|---|---|
| `DefaultEval` | Toujours 1.0 (passe-partout) |
| `RagasEval` | Métriques Ragas (faithfulness, answer_relevancy...) |
| `DeepEvalEval` | DeepEval (G-Eval, AnswerRelevancy...) |

---

## 11. AnalyticsPort (`analytics_port.py`)

Contrat pour l'agrégation de métriques à grande échelle.

```python
class AnalyticsPort(ABC):
    async def ingest(self, metrics: dict) -> None
    async def query(self, filters: dict) -> list[dict]
```

### Adapters disponibles
| Adapter | Stockage |
|---|---|
| `DefaultAnalytics` | No-op (désactivé) |
| `ClickHouseAnalytics` | ClickHouse (OLAP) |
