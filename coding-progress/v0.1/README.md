# v0.1 — Core + Ports + Adapters par défaut

> **Statut : ✅ Terminé**
> **Date : 2026-07-06**
> **Tests : 18/18 passés**

---

## 1. Objectif

Framework minimal mais fonctionnel — un agent capable de répondre à une question simple sans **aucune dépendance externe**.

Principes clés :
- **Zéro dépendance lourde** dans le core (stdlib only)
- **Architecture Ports & Adapters** — 11 interfaces abstraites
- **5 phases du lifecycle** — Hydrate → Loop → Persist → Trace → Eval
- **Boucle de raisonnement** — Planner → Executor → Reflector → Verifier
- **Configuration déclarative** via fichiers YAML

---

## 2. Fichiers créés (52 fichiers)

### 2.1 Projet racine

| Fichier | Description |
|---|---|
| `pyproject.toml` | Configuration monorepo (setuptools, pytest, ruff, mypy) |

### 2.2 Core — Types et Erreurs

| Fichier | Description |
|---|---|
| `core/agentforge_core/types.py` | 7 dataclasses : Message, ToolCall, ToolResult, RunStatus, Span, EvalResult, AdapterDeclaration |
| `core/agentforge_core/errors.py` | 9 classes d'erreur : AgentForgeError, PortNotImplementedError, AdapterNotFoundError, ConfigurationError, LLMError, ToolExecutionError, MemoryError, GuardrailViolationError, ContractViolationError |
| `core/agentforge_core/_version.py` | Version unique `0.1.0` |

### 2.3 Core — 11 Ports (interfaces abstraites)

| Fichier | Port | Méthodes |
|---|---|---|
| `ports/llm_port.py` | LLMPort | `complete()`, `stream()` |
| `ports/orchestration_port.py` | OrchestrationPort | `run()`, `should_stop()` |
| `ports/working_memory_port.py` | WorkingMemoryPort | `get()`, `set()`, `delete()` |
| `ports/semantic_memory_port.py` | SemanticMemoryPort | `search()`, `upsert()`, `delete()` |
| `ports/episodic_memory_port.py` | EpisodicMemoryPort | `search_hybrid()`, `append()`, `get_history()` |
| `ports/procedural_memory_port.py` | ProceduralMemoryPort | `load()`, `list_skills()` |
| `ports/tool_registry_port.py` | ToolRegistryPort | `list_tools()`, `execute()` |
| `ports/event_bus_port.py` | EventBusPort | `publish()`, `subscribe()` |
| `ports/trace_port.py` | TracePort | `record()` |
| `ports/eval_port.py` | EvalPort | `evaluate()` |
| `ports/analytics_port.py` | AnalyticsPort | `ingest()`, `query()` |

### 2.4 Core — Lifecycle (5 phases)

| Fichier | Phase | Rôle |
|---|---|---|
| `lifecycle/run_context.py` | — | RunContext (dataclass avec guardrails) |
| `lifecycle/hydrate_context.py` | 1 | ContextHydrator : interroge les 3 mémoires, assemble la Working Memory |
| `lifecycle/loop_controller.py` | 2 | LoopController : exécute la boucle avec guardrails (max_iterations, token_budget, timeout) |
| `lifecycle/persist_stage.py` | 3 | PersistStage : sauvegarde les messages, consolidation différée (seuil N=10) |
| `lifecycle/trace_stage.py` | 4 | TraceStage : émet une trace asynchrone |
| `lifecycle/eval_stage.py` | 5 | EvalStage : score → gate → diagnose/release (seuil 0.7) |

### 2.5 Core — Loop (boucle de raisonnement)

| Fichier | Rôle |
|---|---|
| `loop/planner.py` | Planner (ABC) : décompose l'objectif en étapes |
| `loop/executor.py` | Executor (ABC) : exécute une étape (tool call ou LLM) |
| `loop/reflector.py` | Reflector (ABC) : analyse le résultat et suggère une correction |
| `loop/verifier.py` | Verifier (ABC) : valide la réponse finale |

### 2.6 Core — Registry et Config

| Fichier | Description |
|---|---|
| `registry/adapter_registry.py` | AdapterRegistry : déclaration, résolution et instanciation des adapters |
| `config/schema.py` | Validation du schéma de configuration (champs requis, types) |
| `config/loader.py` | ConfigLoader : charge et fusionne les fichiers YAML/JSON |

### 2.7 Adapters par défaut (5)

| Fichier | Port implémenté | Description |
|---|---|---|
| `adapters/adapters-default/__init__.py` | ProceduralMemory, ToolRegistry, Trace, Eval, Analytics | 5 adapters "passe-partout" : fichiers .md, outils vides, trace JSON, eval toujours passé, analytics no-op |
| `adapters/adapters-orchestration-minimal/__init__.py` | OrchestrationPort | MinimalOrchestrator : boucle synchrone Planner→Executor→Reflector→Verifier |
| `adapters/adapters-memory-inmemory/__init__.py` | WorkingMemoryPort | InMemoryWorkingMemory : stockage dict en RAM |
| `adapters/adapters-memory-sqlite/__init__.py` | SemanticMemoryPort + EpisodicMemoryPort | SQLiteSemanticMemory + SQLiteEpisodicMemory : tables SQL avec index |
| `adapters/adapters-eventbus-inprocess/__init__.py` | EventBusPort | InProcessEventBus : dispatcher in-process synchrone |

### 2.8 Tests (7 fichiers)

| Fichier | Description |
|---|---|
| `core/tests/conftest.py` | Mocks pour tous les ports (LLM, WorkingMemory, SemanticMemory, EpisodicMemory, ToolRegistry) |
| `core/tests/test_config.py` | 11 tests : schema validation + config loader |
| `core/tests/test_lifecycle.py` | 7 tests : RunContext (initialization, messages, guardrails, sérialisation) |
| `core/tests/contract_tests/test_llm_port_contract.py` | Tests de conformité LLMPort (à hériter par les adapters) |
| `core/tests/contract_tests/test_memory_ports_contract.py` | Tests de conformité MemoryPorts (à hériter par les adapters) |
| `core/tests/contract_tests/test_tool_registry_contract.py` | Tests de conformité ToolRegistryPort (à hériter par les adapters) |

### 2.9 Configuration

| Fichier | Description |
|---|---|
| `recipes/recipe-minimal.yaml` | Recette zéro dépendance externe (tous les adapters par défaut) |

---

## 3. Décisions techniques

### 3.1 Pourquoi `stdlib only` dans le core ?
Le principe fondamental du README : *"Aucune ligne dans core/ ne doit importer un SDK, un driver, ou un nom de produit."* Le core ne contient que des ABC et des dataclasses.

### 3.2 Pourquoi SQLite pour les adapters par défaut ?
SQLite est disponible dans la stdlib Python, ne nécessite aucune installation, et supporte assez de fonctionnalités pour le développement local et les tests.

### 3.3 Pourquoi `asyncio` partout ?
Toutes les méthodes des ports sont `async def` pour permettre :
- Le non-blocage des appels LLM (qui peuvent prendre 10+ secondes)
- Le tracing asynchrone (Phase 4 ne bloque jamais la réponse)
- La scalabilité future (Temporal, NATS)

### 3.4 Pourquoi des contract tests séparés ?
Les contract tests (`core/tests/contract_tests/`) sont conçus pour être **hérités** par chaque adapter. Cela garantit que tous les adapters d'un même port se comportent de façon strictement équivalente.

---

## 4. Tests — Résultats

### 4.1 Commande
```bash
pytest core/tests/test_config.py core/tests/test_lifecycle.py -v
```

### 4.2 Résultat : 18/18 ✅

```
TestConfigSchema::test_valid_minimal_config          ✅
TestConfigSchema::test_missing_agent_field           ✅
TestConfigSchema::test_missing_ports_field           ✅
TestConfigSchema::test_invalid_port_name             ✅
TestConfigSchema::test_port_without_adapter          ✅
TestConfigSchema::test_disabled_port_without_adapter ✅
TestConfigLoader::test_load_valid_yaml               ✅
TestConfigLoader::test_load_valid_json               ✅
TestConfigLoader::test_load_file_not_found           ✅
TestConfigLoader::test_load_invalid_extension        ✅
TestConfigLoader::test_merge_configs                 ✅
TestRunContext::test_default_initialization          ✅
TestRunContext::test_add_message                     ✅
TestRunContext::test_add_tool_result                 ✅
TestRunContext::test_is_exhausted_max_iterations     ✅
TestRunContext::test_is_exhausted_token_budget       ✅
TestRunContext::test_is_not_exhausted                ✅
TestRunContext::test_to_dict                         ✅
```

### 4.3 Bug corrigé
- `test_add_message` : le commentaire indiquait 3 mots mais le test attendait 2 → corrigé à 3

---

## 5. Livrables

- [x] `pyproject.toml` racine (monorepo)
- [x] `core/agentforge_core/types.py` — 7 dataclasses
- [x] `core/agentforge_core/errors.py` — 9 classes d'erreur
- [x] 11 ports dans `core/agentforge_core/ports/`
- [x] 6 fichiers de lifecycle dans `core/agentforge_core/lifecycle/`
- [x] 4 fichiers de loop dans `core/agentforge_core/loop/`
- [x] `core/agentforge_core/registry/adapter_registry.py`
- [x] `core/agentforge_core/config/schema.py` + `loader.py`
- [x] 5 adapters par défaut (default, minimal, inmemory, sqlite, inprocess)
- [x] `recipes/recipe-minimal.yaml`
- [x] 18 tests unitaires passés
- [x] 3 fichiers de contract tests
- [x] Le package s'installe avec `pip install -e .`

---

## 6. Notes pour la suite

- Les contract tests dans `core/tests/contract_tests/` nécessitent une fixture `adapter` pour être exécutés — ils sont conçus pour être hérités par les vrais adapters dans les versions ultérieures
- Le `ConfigLoader.load()` nécessite PyYAML pour les fichiers `.yaml` — prévoir une dépendance optionnelle
- L'adapter SQLite utilise une recherche textuelle `LIKE` basique — l'ajout de sqlite-vec améliorera la recherche sémantique en v0.3
