# AgentForge — Plan de Développement Complet

> **De la v0.1 à la v1.0** — Guide pas à pas pour construire le framework agentique modulaire.

---

## Table des matières

1. [Structure du projet](#1-structure-du-projet)
2. [v0.1 — Core + Ports + Adapters par défaut](#2-v01--core--ports--adapters-par-défaut)
3. [v0.2 — Adapters LLM + API FastAPI](#3-v02--adapters-llm--api-fastapi)
4. [v0.3 — Adapters Mémoire Production](#4-v03--adapters-mémoire-production)
5. [v0.4 — Tools MCP + Trace + Eval](#5-v04--tools-mcp--trace--eval)
6. [v0.5 — Orchestration avancée + Event Bus](#6-v05--orchestration-avancée--event-bus)
7. [v1.0 — Stabilisation, Documentation, Exemples](#7-v10--stabilisation-documentation-exemples)
8. [Annexes](#8-annexes)

---

## 1. Structure du projet

Arbre complet à créer. Chaque dossier et fichier est détaillé dans les sections suivantes.

```
agentforge/
│
├── README.md                          # Présentation du projet (existant)
├── PLAN.md                            # Ce fichier — guide de développement
├── LICENSE                            # Licence MIT ou Apache 2.0
├── pyproject.toml                     # Projet racine (monorepo)
├── CONTRIBUTING.md                    # Règles de contribution
├── ARCHITECTURE.md                    # Raisonnement de conception détaillé
├── Systeme.png                        # Schéma d'architecture de référence
│
├── core/                              # Le noyau — zéro dépendance lourde
│   ├── pyproject.toml
│   ├── agentforge_core/
│   │   ├── __init__.py
│   │   ├── _version.py
│   │   │
│   │   ├── ports/                     # 11 interfaces abstraites
│   │   │   ├── __init__.py
│   │   │   ├── llm_port.py
│   │   │   ├── orchestration_port.py
│   │   │   ├── working_memory_port.py
│   │   │   ├── semantic_memory_port.py
│   │   │   ├── episodic_memory_port.py
│   │   │   ├── procedural_memory_port.py
│   │   │   ├── tool_registry_port.py
│   │   │   ├── event_bus_port.py
│   │   │   ├── trace_port.py
│   │   │   ├── eval_port.py
│   │   │   └── analytics_port.py
│   │   │
│   │   ├── lifecycle/                 # 5 phases du run
│   │   │   ├── __init__.py
│   │   │   ├── run_context.py
│   │   │   ├── hydrate_context.py
│   │   │   ├── loop_controller.py
│   │   │   ├── persist_stage.py
│   │   │   ├── trace_stage.py
│   │   │   └── eval_stage.py
│   │   │
│   │   ├── loop/                      # Boucle de raisonnement
│   │   │   ├── __init__.py
│   │   │   ├── planner.py
│   │   │   ├── executor.py
│   │   │   ├── reflector.py
│   │   │   └── verifier.py
│   │   │
│   │   ├── registry/                  # Résolution d'adapters
│   │   │   ├── __init__.py
│   │   │   └── adapter_registry.py
│   │   │
│   │   ├── config/                    # Configuration déclarative
│   │   │   ├── __init__.py
│   │   │   ├── schema.py
│   │   │   └── loader.py
│   │   │
│   │   ├── errors.py                  # Erreurs du domaine
│   │   └── types.py                   # Types partagés (dataclasses)
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py
│       ├── contract_tests/            # Tests de conformité pour adapters
│       │   ├── __init__.py
│       │   ├── test_llm_port_contract.py
│       │   ├── test_memory_ports_contract.py
│       │   └── test_tool_registry_contract.py
│       ├── test_lifecycle.py
│       ├── test_loop.py
│       └── test_config.py
│
├── adapters/                          # Un package indépendant par technologie
│   ├── adapters-llm-litellm/
│   ├── adapters-llm-openai-compatible/
│   ├── adapters-orchestration-langgraph/
│   ├── adapters-orchestration-temporal/
│   ├── adapters-orchestration-minimal/
│   ├── adapters-memory-redis/
│   ├── adapters-memory-inmemory/
│   ├── adapters-memory-qdrant/
│   ├── adapters-memory-postgres-pgvector/
│   ├── adapters-memory-sqlite/
│   ├── adapters-tools-mcp/
│   ├── adapters-eventbus-nats/
│   ├── adapters-eventbus-inprocess/
│   ├── adapters-trace-langfuse/
│   ├── adapters-trace-opentelemetry/
│   ├── adapters-eval-ragas/
│   ├── adapters-eval-deepeval/
│   └── adapters-analytics-clickhouse/
│
├── recipes/                           # Configs prêtes à l'emploi
│   ├── recipe-minimal.yaml
│   ├── recipe-startup.yaml
│   └── recipe-enterprise.yaml
│
├── api/
│   └── adapters-api-fastapi/
│       ├── pyproject.toml
│       ├── agentforge_api/
│       │   ├── __init__.py
│       │   ├── main.py
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── chat_completions.py
│       │   │   └── health.py
│       │   └── openai_schema_adapter.py
│       └── tests/
│           ├── __init__.py
│           └── test_api.py
│
├── examples/
│   ├── example-minimal-agent/
│   │   ├── README.md
│   │   ├── main.py
│   │   └── config.yaml
│   ├── example-support-agent-mcp-tools/
│   │   ├── README.md
│   │   ├── main.py
│   │   └── config.yaml
│   └── example-multi-tenant-saas/
│       ├── README.md
│       ├── main.py
│       └── config.yaml
│
├── docs/
│   ├── ports-reference.md
│   ├── adapters-matrix.md
│   ├── configuration-guide.md
│   ├── memory-model.md
│   ├── loop-and-guardrails.md
│   └── llmops-and-eval.md
│
└── deployment/
    ├── docker-compose.minimal.yaml
    ├── docker-compose.enterprise.yaml
    └── kubernetes/
        ├── base/
        │   ├── deployment.yaml
        │   ├── service.yaml
        │   └── configmap.yaml
        └── overlays/
            ├── dev/
            │   └── kustomization.yaml
            ├── staging/
            │   └── kustomization.yaml
            └── prod/
                └── kustomization.yaml
```

---

## 2. v0.1 — Core + Ports + Adapters par défaut

> **Objectif** : Framework minimal mais fonctionnel — un agent capable de répondre à une question simple sans aucune dépendance externe.

### 2.1 Projet racine — `pyproject.toml`

**Fichier** : `pyproject.toml` (racine)

Configuration du monorepo avec [PEP 660](https://peps.python.org/pep-0660/) (editables). Déclarer :
- Nom : `agentforge`
- Version : `0.1.0`
- Licence MIT
- Auteur
- Description courte
- `[tool.setuptools.packages.find]` avec `where = ["core", "adapters/*", "api/*"]`

### 2.2 Types partagés — `core/agentforge_core/types.py`

Définir les dataclasses fondamentales utilisées par tous les ports :

| Classe | Champs | Description |
|---|---|---|
| `Message` | `role: str`, `content: str`, `tool_calls: list[ToolCall]`, `timestamp: datetime` | Un message dans l'historique |
| `ToolCall` | `id: str`, `name: str`, `arguments: dict` | Appel d'outil |
| `ToolResult` | `tool_call_id: str`, `content: str`, `success: bool` | Résultat d'un outil |
| `RunContext` | `run_id: str`, `user_query: str`, `messages: list[Message]`, `working_memory: dict`, `tool_results: list[ToolResult]`, `status: RunStatus`, `metadata: dict` | État complet d'un run |
| `RunStatus` | Enum: `PENDING, HYDRATING, RUNNING, COMPLETED, FAILED, BLOCKED` | Statut du run |
| `Span` | `name: str`, `start_time: datetime`, `end_time: datetime`, `attributes: dict` | Une span de tracing |
| `EvalResult` | `score: float`, `verdict: str`, `diagnosis: str`, `passed: bool` | Résultat d'évaluation |
| `AdapterDeclaration` | `port: str`, `name: str`, `version: str`, `class_ref: str` | Déclaration d'adapter |

### 2.3 Erreurs du domaine — `core/agentforge_core/errors.py`

Hiérarchie d'erreurs :

```
AgentForgeError (Base)
├── PortNotImplementedError       # Aucun adapter trouvé pour un port
├── AdapterNotFoundError          # Adapter déclaré mais pas installé
├── ConfigurationError            # Fichier de config invalide
├── LLMError                      # Erreur LLM (timeout, rate limit, etc.)
├── ToolExecutionError            # Échec d'exécution d'outil
├── MemoryError                   # Erreur de stockage mémoire
├── GuardrailViolationError       # Violation d'une règle d'arrêt
└── ContractViolationError        # Adapter ne respecte pas le contrat
```

### 2.4 Ports — 11 interfaces abstraites

Chaque port est une **classe abstraite** (ABC) avec méthodes `@abstractmethod`. Aucune implémentation concrète.

#### 2.4.1 `llm_port.py` — `LLMPort`

```python
class LLMPort(ABC):
    @abstractmethod
    async def complete(self, messages: list[Message], tools: list[dict] | None = None) -> Message:
        """Appelle le LLM et retourne une réponse."""
        ...

    @abstractmethod
    async def stream(self, messages: list[Message], tools: list[dict] | None = None):
        """Appelle le LLM en streaming, yield des deltas."""
        ...
```

#### 2.4.2 `orchestration_port.py` — `OrchestrationPort`

```python
class OrchestrationPort(ABC):
    @abstractmethod
    async def run(self, context: RunContext) -> Message:
        """Exécute la boucle de raisonnement complète."""
        ...

    @abstractmethod
    async def should_stop(self, state: dict) -> bool:
        """Vérifie si la boucle doit s'arrêter."""
        ...
```

#### 2.4.3 `working_memory_port.py` — `WorkingMemoryPort`

```python
class WorkingMemoryPort(ABC):
    @abstractmethod
    async def get(self, run_id: str) -> dict:
        """Récupère le contexte d'un run."""
        ...

    @abstractmethod
    async def set(self, run_id: str, context: dict) -> None:
        """Stocke le contexte d'un run."""
        ...

    @abstractmethod
    async def delete(self, run_id: str) -> None:
        """Supprime le contexte d'un run (fin de run)."""
        ...
```

#### 2.4.4 `semantic_memory_port.py` — `SemanticMemoryPort`

```python
class SemanticMemoryPort(ABC):
    @abstractmethod
    async def search(self, query: str, top_k: int = 5, filters: dict | None = None) -> list[dict]:
        """Recherche sémantique dans les faits stockés."""
        ...

    @abstractmethod
    async def upsert(self, fact: dict) -> None:
        """Ajoute ou met à jour un fait."""
        ...

    @abstractmethod
    async def delete(self, fact_id: str) -> None:
        """Supprime un fait."""
        ...
```

#### 2.4.5 `episodic_memory_port.py` — `EpisodicMemoryPort`

```python
class EpisodicMemoryPort(ABC):
    @abstractmethod
    async def search_hybrid(self, query: str, since: datetime | None = None, top_k: int = 10) -> list[dict]:
        """Recherche dans l'historique des conversations."""
        ...

    @abstractmethod
    async def append(self, event: Message) -> None:
        """Ajoute un message à l'historique."""
        ...

    @abstractmethod
    async def get_history(self, session_id: str, limit: int = 50) -> list[Message]:
        """Récupère l'historique d'une session."""
        ...
```

#### 2.4.6 `procedural_memory_port.py` — `ProceduralMemoryPort`

```python
class ProceduralMemoryPort(ABC):
    @abstractmethod
    async def load(self, skill_name: str) -> str:
        """Charge le contenu d'une compétence."""
        ...

    @abstractmethod
    async def list_skills(self) -> list[str]:
        """Liste les compétences disponibles."""
        ...
```

#### 2.4.7 `tool_registry_port.py` — `ToolRegistryPort`

```python
class ToolRegistryPort(ABC):
    @abstractmethod
    async def list_tools(self) -> list[dict]:
        """Retourne les schémas d'outils disponibles (format OpenAI)."""
        ...

    @abstractmethod
    async def execute(self, name: str, args: dict) -> ToolResult:
        """Exécute un outil par son nom."""
        ...
```

#### 2.4.8 `event_bus_port.py` — `EventBusPort`

```python
class EventBusPort(ABC):
    @abstractmethod
    async def publish(self, topic: str, event: dict) -> None:
        """Publie un événement sur un topic."""
        ...

    @abstractmethod
    async def subscribe(self, topic: str, handler: callable) -> None:
        """Souscrit à un topic avec un handler."""
        ...
```

#### 2.4.9 `trace_port.py` — `TracePort`

```python
class TracePort(ABC):
    @abstractmethod
    async def record(self, run_id: str, spans: list[Span]) -> None:
        """Enregistre une trace complète pour un run."""
        ...
```

#### 2.4.10 `eval_port.py` — `EvalPort`

```python
class EvalPort(ABC):
    @abstractmethod
    async def evaluate(self, run_trace: dict) -> EvalResult:
        """Évalue la qualité d'un run."""
        ...
```

#### 2.4.11 `analytics_port.py` — `AnalyticsPort`

```python
class AnalyticsPort(ABC):
    @abstractmethod
    async def ingest(self, metrics: dict) -> None:
        """Ingère des métriques."""
        ...

    @abstractmethod
    async def query(self, filters: dict) -> list[dict]:
        """Interroge les métriques agrégées."""
        ...
```

### 2.5 Lifecycle — 5 phases du run

#### 2.5.1 `run_context.py` — `RunContext`

Classe concrète qui encapsule l'état complet d'un run. Utilise les types de `types.py`.

- `run_id: str` — UUID généré à chaque run
- `user_query: str` — Prompt utilisateur original
- `messages: list[Message]` — Messages échangés
- `working_memory: dict` — Contexte assemblé (phase 1)
- `tool_results: list[ToolResult]` — Résultats des tool calls
- `status: RunStatus` — Statut actuel
- `metadata: dict` — Métadonnées (timestamps, tokens, etc.)
- `session_id: str | None` — ID de session pour la mémoire épisodique
- `max_iterations: int = 20` — Guardrail : nombre max d'itérations
- `token_budget: int = 100000` — Guardrail : budget tokens
- `timeout_seconds: int = 120` — Guardrail : timeout

Méthodes :
- `add_message(msg: Message)` — Ajoute un message et met à jour le compteur de tokens
- `add_tool_result(result: ToolResult)` — Ajoute un résultat d'outil
- `is_exhausted() -> bool` — Vérifie si un guardrail est atteint
- `to_dict() -> dict` — Sérialisation pour tracing

#### 2.5.2 `hydrate_context.py` — Phase 1

```python
class ContextHydrator:
    def __init__(self, semantic_memory: SemanticMemoryPort,
                 episodic_memory: EpisodicMemoryPort,
                 procedural_memory: ProceduralMemoryPort):
        ...

    async def hydrate(self, context: RunContext) -> None:
        """Interroge les 3 mémoires et peuple working_memory."""
        # 1. Charger l'historique épisodique de la session
        # 2. Rechercher les faits sémantiques pertinents
        # 3. Charger les compétences procédurales
        # 4. Assembler le tout dans working_memory
```

Détail des étapes :
1. **Mémoire épisodique** : `episodic_memory.get_history(session_id)` → derniers messages
2. **Mémoire sémantique** : `semantic_memory.search(user_query)` → faits pertinents
3. **Mémoire procédurale** : `procedural_memory.list_skills()` → instructions actives
4. **Assemblage** : construire un prompt système enrichi dans `working_memory["system_prompt"]`

#### 2.5.3 `loop_controller.py` — Phase 2

```python
class LoopController:
    def __init__(self, orchestration: OrchestrationPort):
        ...

    async def execute(self, context: RunContext) -> Message:
        """Exécute la boucle via l'orchestrateur avec guardrails."""
        # 1. Vérifier guardrails avant de commencer
        # 2. Déléguer à orchestration.run(context)
        # 3. Vérifier guardrails après chaque itération
        # 4. Retourner la réponse finale
```

Guardrails implémentés :
- **Max itérations** : `context.max_iterations` — stop si dépassé
- **Budget tokens** : `context.token_budget` — stop si dépassé
- **Timeout** : `context.timeout_seconds` — stop si dépassé
- **Contenu sensible** : détection de mots interdits (optionnel)

#### 2.5.4 `persist_stage.py` — Phase 3

```python
class PersistStage:
    def __init__(self, episodic_memory: EpisodicMemoryPort,
                 semantic_memory: SemanticMemoryPort):
        ...

    async def persist(self, context: RunContext) -> None:
        """Sauvegarde les messages et déclenche la consolidation."""
        # 1. Sauvegarder tous les nouveaux messages dans episodic_memory
        # 2. Compter le nombre de nouveaux échanges
        # 3. Si > seuil N, déclencher consolidation asynchrone :
        #    - Résumer les échanges
        #    - Extraire les faits
        #    - Upsert dans semantic_memory
```

#### 2.5.5 `trace_stage.py` — Phase 4

```python
class TraceStage:
    def __init__(self, trace_port: TracePort):
        ...

    async def trace(self, context: RunContext) -> None:
        """Émet une trace complète du run (asynchrone, ne bloque pas)."""
        # 1. Construire les spans à partir du contexte
        # 2. Enregistrer via trace_port.record()
        # 3. Ne jamais bloquer la réponse utilisateur
```

#### 2.5.6 `eval_stage.py` — Phase 5

```python
class EvalStage:
    def __init__(self, eval_port: EvalPort):
        ...

    async def evaluate(self, context: RunContext) -> EvalResult:
        """Évalue la qualité du run (tâche de fond)."""
        # 1. Construire la trace d'évaluation
        # 2. Appeler eval_port.evaluate()
        # 3. Gate : si score < seuil → Diagnose
        # 4. Si fix trouvé → Release (nouvelle version de l'adapter)
```

### 2.6 Loop — Boucle de raisonnement

#### 2.6.1 `planner.py` — `Planner`

```python
class Planner(ABC):
    @abstractmethod
    async def plan(self, context: RunContext) -> list[str]:
        """Décompose l'objectif en étapes."""
        ...
```

Implémentation par défaut (intégrée) :
- Utilise le LLM pour décomposer la requête en étapes
- Retourne une liste d'actions à exécuter

#### 2.6.2 `executor.py` — `Executor`

```python
class Executor(ABC):
    @abstractmethod
    async def execute(self, context: RunContext, step: str) -> ToolResult | Message:
        """Exécute une étape (tool call ou réponse LLM)."""
        ...
```

Implémentation par défaut :
- Si l'étape nécessite un outil → `tool_registry.execute()`
- Sinon → `llm.complete()` pour générer une réponse

#### 2.6.3 `reflector.py` — `Reflector`

```python
class Reflector(ABC):
    @abstractmethod
    async def reflect(self, context: RunContext, result: ToolResult) -> str | None:
        """Analyse le résultat et décide de la prochaine action."""
        ...
```

Implémentation par défaut :
- Vérifie si le résultat est complet
- Si erreur → suggère une correction
- Si succès → passe à l'étape suivante

#### 2.6.4 `verifier.py` — `Verifier`

```python
class Verifier(ABC):
    @abstractmethod
    async def verify(self, context: RunContext, final_response: Message) -> bool:
        """Vérifie que la réponse répond à la requête."""
        ...
```

Implémentation par défaut :
- Vérifie que la réponse n'est pas vide
- Vérifie que tous les outils appelés ont un résultat
- Option : utiliser le LLM comme juge pour valider la pertinence

### 2.7 Registry — `adapter_registry.py`

```python
class AdapterRegistry:
    """Registre central de découverte et résolution des adapters."""

    def __init__(self):
        self._declarations: dict[str, list[AdapterDeclaration]] = {}
        self._instances: dict[str, object] = {}

    def register(self, declaration: AdapterDeclaration) -> None:
        """Enregistre une déclaration d'adapter."""
        ...

    def resolve(self, config: dict) -> None:
        """Résout tous les ports selon la configuration."""
        # 1. Lire la config pour chaque port
        # 2. Trouver la déclaration correspondante
        # 3. Instancier l'adapter
        # 4. Stocker dans _instances
        ...

    def get(self, port_name: str) -> object:
        """Retourne l'instance d'adapter pour un port."""
        ...
```

Mécanisme d'auto-déclaration :
- Chaque package `adapters-*` appelle `registry.register()` à l'import
- Utilisation d'entrées `entry_points` dans `pyproject.toml` (setuptools)

### 2.8 Config — `schema.py` et `loader.py`

#### `schema.py`

Schéma de validation (JSON Schema ou Pydantic) pour les fichiers de recette :

```yaml
# Structure attendue d'une recette
agent:
  name: str
  version: str

ports:
  llm:
    adapter: str          # ex: "litellm", "openai-compatible"
    config: dict          # paramètres spécifiques à l'adapter
  orchestration:
    adapter: str
    config: dict
  working_memory:
    adapter: str
    config: dict
  semantic_memory:
    adapter: str
    config: dict
  episodic_memory:
    adapter: str
    config: dict
  procedural_memory:
    adapter: str
    config: dict
  tool_registry:
    adapter: str
    config: dict
  event_bus:
    adapter: str
    config: dict
  trace:
    adapter: str
    config: dict
  eval:
    adapter: str
    config: dict
  analytics:
    adapter: str
    config: dict
    enabled: bool          # false = désactivé (pas d'erreur si non résolu)

guardrails:
  max_iterations: int = 20
  token_budget: int = 100000
  timeout_seconds: int = 120
```

#### `loader.py`

```python
class ConfigLoader:
    @staticmethod
    def load(path: str) -> dict:
        """Charge et valide un fichier YAML/JSON de configuration."""
        ...

    @staticmethod
    def merge(base: dict, override: dict) -> dict:
        """Fusionne deux configurations (override gagne)."""
        ...
```

### 2.9 Adapters par défaut (embarqués dans le core)

Ces adapters sont inclus directement dans le package `agentforge_core` pour permettre un fonctionnement "zéro dépendance externe".

#### 2.9.1 `adapters-orchestration-minimal/`

Implémente `OrchestrationPort` avec une boucle synchrone simple :

```
adapter_orchestration_minimal/
├── __init__.py
├── minimal_orchestrator.py    # OrchestrationPort
└── loop.py                    # Planner + Executor + Reflector + Verifier intégrés
```

**Logique** :
1. Appeler `Planner.plan()` → obtenir les étapes
2. Pour chaque étape, appeler `Executor.execute()`
3. Après chaque exécution, appeler `Reflector.reflect()`
4. Si le réflecteur renvoie une correction, ré-exécuter
5. Quand toutes les étapes sont faites, appeler `Verifier.verify()`
6. Si vérification échoue, boucler (max N fois)

#### 2.9.2 `adapters-memory-inmemory/`

Implémente `WorkingMemoryPort` avec un simple `dict` en mémoire :

```
adapter_memory_inmemory/
├── __init__.py
└── inmemory_working_memory.py    # WorkingMemoryPort
```

#### 2.9.3 `adapters-memory-sqlite/`

Implémente `SemanticMemoryPort` et `EpisodicMemoryPort` avec SQLite + extension vectorielle (sqlite-vec ou similaire) :

```
adapter_memory_sqlite/
├── __init__.py
├── sqlite_semantic_memory.py     # SemanticMemoryPort
├── sqlite_episodic_memory.py     # EpisodicMemoryPort
└── migrations/
    ├── 0001_init_semantic.sql
    └── 0002_init_episodic.sql
```

**Schéma SQL** :
```sql
-- Mémoire sémantique
CREATE TABLE semantic_facts (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    embedding BLOB,
    metadata TEXT,           -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Mémoire épisodique
CREATE TABLE episodic_messages (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    tool_calls TEXT,         -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_episodic_session ON episodic_messages(session_id);
```

#### 2.9.4 `adapters-eventbus-inprocess/`

Implémente `EventBusPort` avec un simple dispatcher in-process :

```
adapter_eventbus_inprocess/
├── __init__.py
└── inprocess_event_bus.py    # EventBusPort
```

#### 2.9.5 Adapters procédurale et outils par défaut

- **ProceduralMemory** : charge des fichiers `.md` depuis un dossier local
- **ToolRegistry** : aucun outil par défaut (vide, les outils sont ajoutés via MCP plus tard)
- **Trace** : écrit dans un fichier JSON local
- **Eval** : toujours `score=1.0, verdict="passed"` (passe-partout)
- **Analytics** : désactivé par défaut (no-op)

### 2.10 Recette minimale — `recipes/recipe-minimal.yaml`

```yaml
agent:
  name: minimal-agent
  version: "0.1.0"

ports:
  llm:
    adapter: minimal         # Utilise un LLM factice pour les tests
    config: {}
  orchestration:
    adapter: minimal
    config: {}
  working_memory:
    adapter: inmemory
    config: {}
  semantic_memory:
    adapter: sqlite
    config:
      db_path: ":memory:"
  episodic_memory:
    adapter: sqlite
    config:
      db_path: ":memory:"
  procedural_memory:
    adapter: default
    config:
      skills_path: "./skills"
  tool_registry:
    adapter: default
    config: {}
  event_bus:
    adapter: inprocess
    config: {}
  trace:
    adapter: default
    config:
      output_path: "./traces"
  eval:
    adapter: default
    config: {}
  analytics:
    adapter: default
    enabled: false

guardrails:
  max_iterations: 10
  token_budget: 50000
  timeout_seconds: 60
```

### 2.11 Tests v0.1

#### Contract tests — `core/tests/contract_tests/`

Tests génériques que tout adapter doit passer :

- `test_llm_port_contract.py` :
  - `test_complete_returns_message`
  - `test_complete_accepts_tools`
  - `test_stream_yields_deltas`

- `test_memory_ports_contract.py` :
  - `test_working_memory_set_get_delete`
  - `test_semantic_memory_search_upsert`
  - `test_episodic_memory_append_get_history`

- `test_tool_registry_contract.py` :
  - `test_list_tools_returns_schemas`
  - `test_execute_valid_tool`
  - `test_execute_invalid_tool_raises`

#### Tests unitaires

- `test_lifecycle.py` :
  - `test_hydrate_context_queries_all_memories`
  - `test_loop_controller_applies_guardrails`
  - `test_persist_stage_saves_messages`
  - `test_trace_stage_emits_trace`
  - `test_eval_stage_scores_run`

- `test_loop.py` :
  - `test_planner_decomposes_goal`
  - `test_executor_runs_tool_call`
  - `test_reflector_analyzes_result`
  - `test_verifier_validates_response`

- `test_config.py` :
  - `test_load_valid_yaml`
  - `test_load_invalid_yaml_raises`
  - `test_merge_configs`

### 2.12 Livrables v0.1

- [ ] `pyproject.toml` racine
- [ ] `core/pyproject.toml`
- [ ] `core/agentforge_core/types.py`
- [ ] `core/agentforge_core/errors.py`
- [ ] 11 fichiers de ports dans `core/agentforge_core/ports/`
- [ ] 6 fichiers de lifecycle dans `core/agentforge_core/lifecycle/`
- [ ] 4 fichiers de loop dans `core/agentforge_core/loop/`
- [ ] `core/agentforge_core/registry/adapter_registry.py`
- [ ] `core/agentforge_core/config/schema.py`
- [ ] `core/agentforge_core/config/loader.py`
- [ ] 5 adapters par défaut (minimal, inmemory, sqlite, inprocess, default)
- [ ] `recipes/recipe-minimal.yaml`
- [ ] Tests unitaires et contract tests
- [ ] Le package s'installe avec `pip install -e .`
- [ ] Un agent minimal peut répondre à une question simple

---

## 3. v0.2 — Adapters LLM + API FastAPI

> **Objectif** : Connecter de vrais LLM et exposer l'agent via une API REST compatible OpenAI.

### 3.1 Adapter LLM LiteLLM — `adapters-llm-litellm/`

```
adapters-llm-litellm/
├── pyproject.toml
├── agentforge_litellm/
│   ├── __init__.py
│   └── litellm_adapter.py      # LLMPort → LiteLLM
└── tests/
    ├── __init__.py
    └── test_litellm_adapter.py
```

**Dépendances** : `litellm`, `core`

**Implémentation** :
- `complete()` → appelle `litellm.completion()`
- `stream()` → appelle `litellm.completion(stream=True)`, yield des tokens
- Support multi-provider (OpenAI, Anthropic, Google, Ollama, etc.) via LiteLLM
- Configuration : `model: str`, `api_key: str`, `temperature: float`, `max_tokens: int`

### 3.2 Adapter LLM OpenAI-compatible — `adapters-llm-openai-compatible/`

```
adapters-llm-openai-compatible/
├── pyproject.toml
├── agentforge_openai/
│   ├── __init__.py
│   └── openai_adapter.py       # LLMPort → OpenAI SDK
└── tests/
    ├── __init__.py
    └── test_openai_adapter.py
```

**Dépendances** : `openai`, `core`

**Implémentation** :
- Utilise le SDK OpenAI directement
- Support `base_url` pour les APIs compatibles (vLLM, Ollama, etc.)
- Gestion des erreurs (rate limit, timeout, authentication)

### 3.3 API FastAPI — `api/adapters-api-fastapi/`

#### 3.3.1 `pyproject.toml`

**Dépendances** : `fastapi`, `uvicorn`, `pydantic`, `core`, adapters LLM

#### 3.3.2 `main.py`

```python
class AgentForgeAPI:
    """Application FastAPI principale."""

    def __init__(self, config_path: str):
        self.config = ConfigLoader.load(config_path)
        self.registry = AdapterRegistry()
        self.registry.resolve(self.config)
        self.app = FastAPI()
        self._setup_routes()

    def _setup_routes(self):
        """Monte les routeurs."""
        ...

    def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Lance le serveur."""
        uvicorn.run(self.app, host=host, port=port)
```

#### 3.3.3 `routes/chat_completions.py`

Endpoint `POST /v1/chat/completions` (compatible OpenAI) :

```python
@router.post("/v1/chat/completions")
async def chat_completion(request: ChatCompletionRequest):
    """Endpoint compatible OpenAI."""
    # 1. Traduire la requête OpenAI → RunContext
    # 2. Exécuter le lifecycle complet
    # 3. Traduire la réponse → format OpenAI
    # 4. Retourner la réponse
```

**Support** :
- `messages` (system, user, assistant, tool)
- `tools` et `tool_choice`
- `stream: true` (SSE)
- `temperature`, `max_tokens`, `top_p`
- `user` (pour session_id)

#### 3.3.4 `routes/health.py`

```python
@router.get("/health")
async def health():
    """Endpoint de health check."""
    return {"status": "ok", "version": "0.2.0"}
```

#### 3.3.5 `openai_schema_adapter.py`

Conversion bidirectionnelle entre schéma OpenAI et objets internes :

```python
class OpenAISchemaAdapter:
    @staticmethod
    def to_run_context(request: dict) -> RunContext:
        """Convertit une requête OpenAI en RunContext."""
        ...

    @staticmethod
    def to_openai_response(message: Message) -> dict:
        """Convertit une réponse interne en réponse OpenAI."""
        ...

    @staticmethod
    def to_openai_stream(deltas: list[str]) -> Generator:
        """Convertit un stream interne en SSE OpenAI."""
        ...
```

### 3.4 Recette startup — `recipes/recipe-startup.yaml`

```yaml
agent:
  name: startup-agent
  version: "0.2.0"

ports:
  llm:
    adapter: litellm
    config:
      model: gpt-4o-mini
      temperature: 0.7
      max_tokens: 4096
  orchestration:
    adapter: minimal
    config: {}
  working_memory:
    adapter: inmemory
    config: {}
  semantic_memory:
    adapter: sqlite
    config:
      db_path: "./data/semantic.db"
  episodic_memory:
    adapter: sqlite
    config:
      db_path: "./data/episodic.db"
  procedural_memory:
    adapter: default
    config:
      skills_path: "./skills"
  tool_registry:
    adapter: default
    config: {}
  event_bus:
    adapter: inprocess
    config: {}
  trace:
    adapter: default
    config:
      output_path: "./traces"
  eval:
    adapter: default
    config: {}
  analytics:
    adapter: default
    enabled: false

guardrails:
  max_iterations: 20
  token_budget: 100000
  timeout_seconds: 120
```

### 3.5 Tests v0.2

- Tests d'intégration LLM (mockés)
- Tests API FastAPI (httpx + pytest)
- Test de conformité OpenAI (`/v1/chat/completions`)
- Test de streaming SSE

### 3.6 Livrables v0.2

- [ ] `adapters-llm-litellm/` complet avec tests
- [ ] `adapters-llm-openai-compatible/` complet avec tests
- [ ] `api/adapters-api-fastapi/` complet avec tests
- [ ] `recipes/recipe-startup.yaml`
- [ ] L'API répond sur `/v1/chat/completions`
- [ ] Compatible avec n'importe quel client OpenAI (LangChain, IDE, curl)

---

## 4. v0.3 — Adapters Mémoire Production

> **Objectif** : Remplacer SQLite par des bases de données production (Redis, Qdrant, PostgreSQL) pour la persistance et la recherche sémantique.

### 4.1 Adapter Redis — `adapters-memory-redis/`

```
adapters-memory-redis/
├── pyproject.toml
├── agentforge_redis/
│   ├── __init__.py
│   ├── redis_working_memory.py    # WorkingMemoryPort
│   └── redis_episodic_memory.py   # EpisodicMemoryPort
└── tests/
    ├── __init__.py
    └── test_redis_memory.py
```

**Dépendances** : `redis[hiredis]`, `core`

**Implémentation** :
- `WorkingMemoryPort` : utilise `redis.setex()` avec TTL (durée du run)
- `EpisodicMemoryPort` : utilise Redis Lists ou RedisJSON pour l'historique
- Support cluster Redis et sentinel

### 4.2 Adapter Qdrant — `adapters-memory-qdrant/`

```
adapters-memory-qdrant/
├── pyproject.toml
├── agentforge_qdrant/
│   ├── __init__.py
│   └── qdrant_semantic_memory.py   # SemanticMemoryPort
└── tests/
    ├── __init__.py
    └── test_qdrant_semantic.py
```

**Dépendances** : `qdrant-client`, `core`

**Implémentation** :
- `SemanticMemoryPort` : stockage vectoriel avec Qdrant
- Support embeddings via LiteLLM ou modèle local
- Filtres metadata, pagination, scoring

### 4.3 Adapter PostgreSQL/pgvector — `adapters-memory-postgres-pgvector/`

```
adapters-memory-postgres-pgvector/
├── pyproject.toml
├── agentforge_postgres/
│   ├── __init__.py
│   ├── pg_semantic_memory.py      # SemanticMemoryPort
│   ├── pg_episodic_memory.py      # EpisodicMemoryPort
│   ├── migrations/
│   │   ├── 0001_init_semantic.sql
│   │   └── 0002_init_episodic.sql
│   └── connection_pool.py
└── tests/
    ├── __init__.py
    └── test_postgres_memory.py
```

**Dépendances** : `psycopg[binary]`, `pgvector`, `core`

**Implémentation** :
- `SemanticMemoryPort` : table avec colonne `vector(1536)` pour embeddings OpenAI, index IVFFlat ou HNSW
- `EpisodicMemoryPort` : table JSONB pour l'historique
- Connection pooling avec `psycopg.Pool`
- Migrations versionnées (Alembic)

### 4.4 Mise à jour recette startup

`recipes/recipe-startup.yaml` est mis à jour pour utiliser PostgreSQL au lieu de SQLite.

### 4.5 Tests v0.3

- Tests d'intégration avec Redis (via redis mock ou testcontainers)
- Tests d'intégration avec Qdrant (via qdrant-client embed)
- Tests d'intégration avec PostgreSQL (via testcontainers ou pgmock)
- Contract tests sur chaque adapter

### 4.6 Livrables v0.3

- [ ] `adapters-memory-redis/` complet avec tests
- [ ] `adapters-memory-qdrant/` complet avec tests
- [ ] `adapters-memory-postgres-pgvector/` complet avec tests
- [ ] Mise à jour de `recipe-startup.yaml`
- [ ] Tous les adapters passent les contract tests

---

## 5. v0.4 — Tools MCP + Trace + Eval

> **Objectif** : Ajouter les outils via MCP (Model Context Protocol), le tracing avec Langfuse, et l'évaluation avec Ragas/DeepEval.

### 5.1 Adapter Tools MCP — `adapters-tools-mcp/`

```
adapters-tools-mcp/
├── pyproject.toml
├── agentforge_mcp/
│   ├── __init__.py
│   ├── mcp_tool_registry.py      # ToolRegistryPort
│   └── mcp_client.py             # Client MCP (stdio ou SSE)
└── tests/
    ├── __init__.py
    └── test_mcp_tools.py
```

**Dépendances** : `mcp`, `core`

**Implémentation** :
- Se connecte à des serveurs MCP via stdio ou SSE
- Découvre les outils disponibles (list_tools)
- Exécute les outils (execute)
- Supporte les notifications et le streaming de résultats
- Configuration : `servers: list[{command, args, url}]`

### 5.2 Adapter Trace Langfuse — `adapters-trace-langfuse/`

```
adapters-trace-langfuse/
├── pyproject.toml
├── agentforge_langfuse/
│   ├── __init__.py
│   └── langfuse_trace.py         # TracePort
└── tests/
    ├── __init__.py
    └── test_langfuse_trace.py
```

**Dépendances** : `langfuse`, `core`

**Implémentation** :
- Crée une trace Langfuse par run
- Ajoute des spans pour chaque phase (hydrate, loop, persist, etc.)
- Ajoute des spans pour chaque tool call
- Enrichit avec des scores (feedback, évaluation)
- Configuration : `public_key`, `secret_key`, `host`

### 5.3 Adapter Trace OpenTelemetry — `adapters-trace-opentelemetry/`

```
adapters-trace-opentelemetry/
├── pyproject.toml
├── agentforge_otel/
│   ├── __init__.py
│   └── otel_trace.py             # TracePort
└── tests/
    ├── __init__.py
    └── test_otel_trace.py
```

**Dépendances** : `opentelemetry-api`, `opentelemetry-sdk`, `core`

**Implémentation** :
- Exporte les traces au format OTLP
- Compatible avec Jaeger, Zipkin, Grafana Tempo
- Configuration : `endpoint`, `headers`, `service_name`

### 5.4 Adapter Eval Ragas — `adapters-eval-ragas/`

```
adapters-eval-ragas/
├── pyproject.toml
├── agentforge_ragas/
│   ├── __init__.py
│   └── ragas_eval.py             # EvalPort
└── tests/
    ├── __init__.py
    └── test_ragas_eval.py
```

**Dépendances** : `ragas`, `core`

**Implémentation** :
- Évalue la qualité des réponses avec les métriques Ragas
- Métriques : faithfulness, answer_relevancy, context_precision, etc.
- Configuration : `metrics: list[str]`, `llm_provider`

### 5.5 Adapter Eval DeepEval — `adapters-eval-deepeval/`

```
adapters-eval-deepeval/
├── pyproject.toml
├── agentforge_deepeval/
│   ├── __init__.py
│   └── deepeval_eval.py          # EvalPort
└── tests/
    ├── __init__.py
    └── test_deepeval_eval.py
```

**Dépendances** : `deepeval`, `core`

**Implémentation** :
- Évalue avec les métriques DeepEval
- Support G-Eval, summarization, hallucination, etc.
- Configuration : `metrics: list[str]`, `threshold: float`

### 5.6 Tests v0.4

- Tests MCP avec serveur MCP factice
- Tests Langfuse avec mock HTTP
- Tests Ragas/DeepEval avec données synthétiques

### 5.7 Livrables v0.4

- [ ] `adapters-tools-mcp/` complet avec tests
- [ ] `adapters-trace-langfuse/` complet avec tests
- [ ] `adapters-trace-opentelemetry/` complet avec tests
- [ ] `adapters-eval-ragas/` complet avec tests
- [ ] `adapters-eval-deepeval/` complet avec tests

---

## 6. v0.5 — Orchestration avancée + Event Bus

> **Objectif** : Support des workflows complexes (LangGraph, Temporal) et communication asynchrone (NATS).

### 6.1 Adapter Orchestration LangGraph — `adapters-orchestration-langgraph/`

```
adapters-orchestration-langgraph/
├── pyproject.toml
├── agentforge_langgraph/
│   ├── __init__.py
│   ├── langgraph_orchestrator.py    # OrchestrationPort
│   └── graph_builder.py            # Construction du graphe
└── tests/
    ├── __init__.py
    └── test_langgraph_orchestrator.py
```

**Dépendances** : `langgraph`, `langchain-core`, `core`

**Implémentation** :
- Construit un graphe LangGraph à partir des composants du core
- Noeuds : Planner, Executor, Reflector, Verifier
- Arêtes conditionnelles basées sur les décisions du Reflector/Verifier
- Checkpointing pour reprise sur erreur
- Support du streaming de états intermédiaires

### 6.2 Adapter Orchestration Temporal — `adapters-orchestration-temporal/`

```
adapters-orchestration-temporal/
├── pyproject.toml
├── agentforge_temporal/
│   ├── __init__.py
│   ├── temporal_orchestrator.py     # OrchestrationPort
│   ├── workflows/
│   │   ├── agent_workflow.py
│   │   └── consolidate_workflow.py
│   └── activities/
│       ├── llm_activity.py
│       ├── memory_activity.py
│       └── tool_activity.py
└── tests/
    ├── __init__.py
    └── test_temporal_orchestrator.py
```

**Dépendances** : `temporalio`, `core`

**Implémentation** :
- Workflow Temporal pour l'exécution complète d'un run
- Activités pour chaque étape (LLM, mémoire, outils)
- Support du mode "continue-as-new" pour les runs longs
- Gestion des timeouts et retries au niveau Temporal
- Configuration : `host`, `namespace`, `task_queue`

### 6.3 Adapter Event Bus NATS — `adapters-eventbus-nats/`

```
adapters-eventbus-nats/
├── pyproject.toml
├── agentforge_nats/
│   ├── __init__.py
│   └── nats_event_bus.py           # EventBusPort
└── tests/
    ├── __init__.py
    └── test_nats_event_bus.py
```

**Dépendances** : `nats-py`, `core`

**Implémentation** :
- Publie/souscrit via NATS JetStream
- Topics : `agent.run.{run_id}`, `agent.eval.{run_id}`, `agent.analytics`
- Support du pub/sub durable avec JetStream
- Configuration : `servers: list[str]`, `stream: str`

### 6.4 Adapter Analytics ClickHouse — `adapters-analytics-clickhouse/`

```
adapters-analytics-clickhouse/
├── pyproject.toml
├── agentforge_clickhouse/
│   ├── __init__.py
│   ├── clickhouse_analytics.py     # AnalyticsPort
│   └── migrations/
│       └── 0001_init_analytics.sql
└── tests/
    ├── __init__.py
    └── test_clickhouse_analytics.py
```

**Dépendances** : `clickhouse-driver`, `core`

**Implémentation** :
- Table de métriques agrégées (latence, tokens, scores, etc.)
- Requêtes OLAP pour tableaux de bord
- Configuration : `host`, `port`, `database`, `table`

### 6.5 Recette enterprise — `recipes/recipe-enterprise.yaml`

```yaml
agent:
  name: enterprise-agent
  version: "0.5.0"

ports:
  llm:
    adapter: litellm
    config:
      model: gpt-4o
      temperature: 0.3
      max_tokens: 8192
  orchestration:
    adapter: temporal
    config:
      host: temporal:7233
      namespace: agentforge
      task_queue: agent-tasks
  working_memory:
    adapter: redis
    config:
      host: redis:6379
      ttl_seconds: 3600
  semantic_memory:
    adapter: qdrant
    config:
      host: qdrant:6333
      collection: semantic_memory
      embedding_size: 1536
  episodic_memory:
    adapter: postgres
    config:
      dsn: postgresql://user:pass@postgres:5432/agentforge
      pool_size: 10
  procedural_memory:
    adapter: default
    config:
      skills_path: "./skills"
  tool_registry:
    adapter: mcp
    config:
      servers:
        - command: npx
          args: ["-y", "@modelcontextprotocol/server-filesystem", "./data"]
  event_bus:
    adapter: nats
    config:
      servers: ["nats:4222"]
      stream: agentforge
  trace:
    adapter: langfuse
    config:
      public_key: "${LANGFUSE_PUBLIC_KEY}"
      secret_key: "${LANGFUSE_SECRET_KEY}"
      host: https://langfuse.example.com
  eval:
    adapter: ragas
    config:
      metrics: ["faithfulness", "answer_relevancy"]
      threshold: 0.7
  analytics:
    adapter: clickhouse
    enabled: true
    config:
      host: clickhouse:9000
      database: agentforge
      table: run_metrics

guardrails:
  max_iterations: 50
  token_budget: 500000
  timeout_seconds: 600
```

### 6.6 Tests v0.5

- Tests LangGraph avec graphe mocké
- Tests Temporal avec serveur de test Temporal
- Tests NATS avec serveur NATS embarqué
- Tests ClickHouse avec mock SQL

### 6.7 Livrables v0.5

- [ ] `adapters-orchestration-langgraph/` complet avec tests
- [ ] `adapters-orchestration-temporal/` complet avec tests
- [ ] `adapters-eventbus-nats/` complet avec tests
- [ ] `adapters-analytics-clickhouse/` complet avec tests
- [ ] `recipes/recipe-enterprise.yaml`
- [ ] `deployment/docker-compose.enterprise.yaml`

---

## 7. v1.0 — Stabilisation, Documentation, Exemples

> **Objectif** : Release stable et utilisable par des développeurs tiers.

### 7.1 Contract tests complets

- Tous les adapters (v0.1 à v0.5) passent les contract tests
- Ajout de tests de performance (benchmarks)
- Ajout de tests de résilience (timeout, reconnexion, rate limiting)
- Matrice de compatibilité documentée

### 7.2 Documentation complète

#### `docs/ports-reference.md`

Spécification exhaustive de chaque port :
- Signatures exactes des méthodes
- Types attendus (entrée/sortie)
- Garanties (thread-safety, idempotence, atomicité)
- Cas d'erreur et exceptions levées
- Exemples d'utilisation

#### `docs/adapters-matrix.md`

Tableau comparatif de tous les adapters :

| Port | Adapter | Latence | Scalabilité | Coût | Complexité |
|---|---|---|---|---|---|
| LLM | LiteLLM | Moyenne | Haute | Faible | Faible |
| LLM | OpenAI | Faible | Haute | Moyen | Faible |
| Orchestration | Minimal | Très faible | Faible | Nul | Nulle |
| Orchestration | LangGraph | Faible | Moyenne | Nul | Moyenne |
| Orchestration | Temporal | Moyenne | Très haute | Nul | Haute |
| Memory | In-memory | Très faible | Très faible | Nul | Nulle |
| Memory | Redis | Très faible | Haute | Faible | Faible |
| Memory | SQLite | Faible | Faible | Nul | Faible |
| Memory | PostgreSQL | Faible | Haute | Moyen | Moyenne |
| Memory | Qdrant | Faible | Haute | Moyen | Faible |

#### `docs/configuration-guide.md`

Guide complet pour écrire une configuration :
- Structure du fichier YAML
- Tous les champs disponibles
- Variables d'environnement (syntaxe `${VAR_NAME}`)
- Exemples de surcharge
- Validation et debugging

#### `docs/memory-model.md`

Document détaillant le modèle des 3 mémoires :
- **Procédurale** : compétences, instructions, skills
- **Sémantique** : faits, connaissances, profil utilisateur
- **Épisodique** : historique, conversations, événements
- Stratégie de consolidation (Summarizer Agent)
- Seuils et déclencheurs

#### `docs/loop-and-guardrails.md`

Document détaillant la boucle de raisonnement :
- Cycle Planner/Executor/Reflector/Verifier
- Conditions d'arrêt (max itérations, budget tokens, timeout)
- Stratégies de fallback
- Gestion des erreurs

#### `docs/llmops-and-eval.md`

Document détaillant LLM Ops :
- Cycle Trace → Eval → Gate → Diagnose/Release
- Métriques d'évaluation
- Stratégies de gate (strict, permissive, pondérée)
- Boucle de feedback

### 7.3 Exemples complets

#### `example-minimal-agent/`

Agent minimal avec recette minimale :
- Fichier `main.py` (20-30 lignes)
- Fichier `config.yaml` (recette minimale)
- README expliquant comment lancer

#### `example-support-agent-mcp-tools/`

Agent de support avec outils MCP :
- Connexion à un CRM via MCP
- Planification de rendez-vous
- Recherche dans la base de connaissances
- Fichier `main.py` complet
- Fichier `config.yaml` (recette startup)

#### `example-multi-tenant-saas/`

Agent SaaS multi-tenant :
- Isolation par `tenant_id`
- Rate limiting par tenant
- Analytics par tenant
- Déploiement Kubernetes
- Fichier `main.py` complet
- Fichier `config.yaml` (recette enterprise)

### 7.4 Déploiement

#### `deployment/docker-compose.minimal.yaml`

```yaml
version: "3.8"
services:
  agentforge:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./recipes:/app/recipes
      - ./data:/app/data
    command: uvicorn agentforge_api.main:app --host 0.0.0.0 --port 8000
```

#### `deployment/docker-compose.enterprise.yaml`

Services : agentforge, redis, qdrant, postgres, temporal, nats, langfuse, clickhouse

#### `deployment/kubernetes/`

- `base/deployment.yaml` — Déploiement principal
- `base/service.yaml` — Service Kubernetes
- `base/configmap.yaml` — Configuration
- `overlays/dev/`, `overlays/staging/`, `overlays/prod/` — Kustomize overlays

### 7.5 CI/CD

Configuration GitHub Actions (`.github/workflows/`) :
- `ci.yml` — Tests à chaque push
- `publish.yml` — Publication sur PyPI (core + adapters)
- `docs.yml` — Génération et déploiement de la documentation

### 7.6 Livrables v1.0

- [ ] Contract tests passent pour tous les adapters
- [ ] Documentation complète (6 fichiers dans `docs/`)
- [ ] 3 exemples autonomes et fonctionnels
- [ ] Déploiement Docker Compose (minimal + enterprise)
- [ ] Manifests Kubernetes
- [ ] CI/CD pipelines
- [ ] Packages publiés sur PyPI

---

## 8. Annexes

### 8.1 Dépendances par version

| Version | Nouvelles dépendances | Complexité |
|---|---|---|
| v0.1 | Aucune (stdlib only) | ⭐ |
| v0.2 | `litellm`, `openai`, `fastapi`, `uvicorn`, `pydantic` | ⭐⭐ |
| v0.3 | `redis`, `qdrant-client`, `psycopg`, `pgvector` | ⭐⭐⭐ |
| v0.4 | `mcp`, `langfuse`, `opentelemetry-*`, `ragas`, `deepeval` | ⭐⭐⭐ |
| v0.5 | `langgraph`, `temporalio`, `nats-py`, `clickhouse-driver` | ⭐⭐⭐⭐⭐ |
| v1.0 | Aucune nouvelle (stabilisation) | ⭐ |

### 8.2 Ordre de priorité des fichiers à coder

Pour chaque version, l'ordre recommandé :

1. **Types et erreurs** (fondation)
2. **Ports** (contrats)
3. **Lifecycle** (orchestration des phases)
4. **Loop** (raisonnement)
5. **Registry** (résolution)
6. **Config** (configuration)
7. **Adapters par défaut** (implémentations embarquées)
8. **Recettes** (configs YAML)
9. **Tests** (validation)
10. **Adapters externes** (packages séparés)

### 8.3 Principes de codage

- **Tout est typé** : utilisation stricte de type hints Python
- **Tout est async** : toutes les méthodes des ports sont `async def`
- **Tests d'abord** : écrire les contract tests avant les adapters
- **Documentation as code** : docstrings complètes sur chaque méthode
- **Pas de dépendances cachées** : chaque adapter déclare ses dépendances dans son `pyproject.toml`
- **Versionnement sémantique** : `major.minor.patch` (breaking = major)

### 8.4 Glossaire

| Terme | Définition |
|---|---|
| **Port** | Interface abstraite définissant un contrat (ABC) |
| **Adapter** | Implémentation concrète d'un port |
| **Recipe** | Fichier YAML de configuration déclarative |
| **Run** | Exécution complète d'une requête utilisateur |
| **Lifecycle** | Les 5 phases d'exécution d'un run |
| **Loop** | Boucle de raisonnement Planner/Executor/Reflector/Verifier |
| **Working Memory** | Contexte éphémère du run en cours |
| **Semantic Memory** | Faits durables et connaissances |
| **Episodic Memory** | Historique des conversations |
| **Procedural Memory** | Compétences et instructions |
| **Guardrail** | Règle d'arrêt (max itérations, budget tokens, timeout) |
| **Gate** | Mécanisme de validation (score ≥ seuil → release)
| **Consolidation** | Transformation de l'épisodique vers la sémantique |
| **Contract Test** | Test partagé que tout adapter doit passer |

---

> **Prochaine étape** : Prêt à commencer la v0.1 ! 🚀
