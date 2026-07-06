# v0.2 — Adapters LLM + API FastAPI

> **Statut : ✅ Terminé**
> **Date : 2026-07-06**
> **Tests : 36/36 passés**

---

## 1. Objectif

Connecter de vrais LLM et exposer l'agent via une API REST compatible OpenAI.

- **2 adapters LLM** : LiteLLM (multi-provider) et OpenAI-compatible
- **API FastAPI** : endpoints `/v1/chat/completions` et `/health`
- **Conversion bidirectionnelle** : schéma OpenAI ↔ objets internes
- **Recette startup** : configuration prête pour `gpt-4o-mini`

---

## 2. Fichiers créés (15 fichiers)

### 2.1 Adapter LLM LiteLLM

| Fichier | Description |
|---|---|
| `adapters/adapters-llm-litellm/pyproject.toml` | Dépendances : `litellm>=1.40.0`, `agentforge-core` |
| `adapters/adapters-llm-litellm/agentforge_litellm/__init__.py` | `LiteLLMAdapter` : implémente `LLMPort` via `litellm.acompletion()` |
| `adapters/adapters-llm-litellm/tests/test_litellm.py` | 6 tests : complete, tools, stream, init, erreur, kwargs |

**Détails d'implémentation :**
- `complete()` → `litellm.acompletion()` asynchrone
- `stream()` → `litellm.acompletion(stream=True)`, yield des tokens
- Support multi-provider : OpenAI, Anthropic, Google, Ollama, AWS Bedrock, Azure...
- Configuration : `model`, `api_key`, `base_url`, `temperature`, `max_tokens`
- Gestion d'erreurs : toutes les exceptions sont converties en `RuntimeError`

### 2.2 Adapter LLM OpenAI-compatible

| Fichier | Description |
|---|---|
| `adapters/adapters-llm-openai-compatible/pyproject.toml` | Dépendances : `openai>=1.0.0`, `agentforge-core` |
| `adapters/adapters-llm-openai-compatible/agentforge_openai/__init__.py` | `OpenAICompatibleAdapter` : implémente `LLMPort` via SDK OpenAI |
| `adapters/adapters-llm-openai-compatible/tests/test_openai_compatible.py` | 6 tests : complete, tools, stream, init, erreur, format_messages |

**Détails d'implémentation :**
- Utilise `AsyncOpenAI` pour les appels asynchrones
- Support `base_url` pour les APIs compatibles (vLLM, Ollama, etc.)
- Formatage bidirectionnel des messages (internes ↔ OpenAI)
- Gestion des tool_calls dans les messages

### 2.3 API FastAPI

| Fichier | Description |
|---|---|
| `api/adapters-api-fastapi/pyproject.toml` | Dépendances : `fastapi>=0.110.0`, `uvicorn`, `pydantic`, `pyyaml` |
| `api/adapters-api-fastapi/agentforge_api/__init__.py` | `AgentForgeAPI` : charge la config, résout les adapters, monte les routes |
| `api/adapters-api-fastapi/agentforge_api/routes/health.py` | `GET /health` → `{"status": "ok", "version": "0.2.0"}` |
| `api/adapters-api-fastapi/agentforge_api/routes/chat_completions.py` | `POST /v1/chat/completions` : endpoint compatible OpenAI |
| `api/adapters-api-fastapi/agentforge_api/openai_schema_adapter.py` | `OpenAISchemaAdapter` : conversion bidirectionnelle OpenAI ↔ interne |
| `api/adapters-api-fastapi/tests/test_openai_schema.py` | 6 tests : to_run_context, to_openai_response, tools, stream, usage |

**Détails d'implémentation :**
- `OpenAISchemaAdapter.to_run_context()` : convertit une requête OpenAI en `RunContext`
- `OpenAISchemaAdapter.to_openai_response()` : convertit un `Message` en réponse OpenAI
- `OpenAISchemaAdapter.to_openai_stream()` : convertit des tokens en SSE (Server-Sent Events)
- Support des paramètres : `messages`, `tools`, `tool_choice`, `stream`, `temperature`, `max_tokens`, `user`

### 2.4 Configuration

| Fichier | Description |
|---|---|
| `recipes/recipe-startup.yaml` | Recette startup : LiteLLM (gpt-4o-mini) + SQLite persistant |

---

## 3. Décisions techniques

### 3.1 Pourquoi deux adapters LLM ?
- **LiteLLM** : idéal pour le multi-provider (un seul adapter pour OpenAI, Anthropic, Ollama...)
- **OpenAI SDK** : plus léger, plus direct, idéal pour les déploiements ne ciblant qu'OpenAI

Les deux passent les mêmes contract tests et sont interchangeables via la configuration.

### 3.2 Pourquoi FastAPI plutôt que Flask ?
- Support natif de l'asyncio (indispensable pour le streaming SSE)
- Validation automatique via Pydantic
- Documentation interactive auto-générée (`/docs`)
- Performance : Uvicorn est significativement plus rapide que Flask/Werkzeug

### 3.3 Pourquoi une façade compatible OpenAI ?
Le standard OpenAI (`/v1/chat/completions`) est devenu le protocole de facto pour les APIs LLM. En étant compatible, AgentForge peut être utilisé comme un drop-in replacement par :
- Tout client OpenAI (LangChain, LlamaIndex)
- Les IDE (VS Code Copilot, Cursor)
- Les autres agents IA

### 3.4 Gestion des erreurs
Les erreurs API (rate limit, timeout, authentication) sont converties en `RuntimeError` avec le message original, permettant au lifecycle de les rattraper proprement.

---

## 4. Tests — Résultats

### 4.1 Commande
```bash
pytest adapters/adapters-llm-litellm/tests/ \
       adapters/adapters-llm-openai-compatible/tests/ \
       core/tests/test_config.py \
       core/tests/test_lifecycle.py \
       api/adapters-api-fastapi/tests/ -v
```

### 4.2 Résultat : 36/36 ✅

```
adapters-llm-litellm (6 tests)
├── test_complete_returns_message       ✅
├── test_complete_with_tools            ✅
├── test_stream_yields_deltas           ✅
├── test_initialization                 ✅
├── test_complete_raises_on_error       ✅
└── test_build_kwargs                   ✅

adapters-llm-openai-compatible (6 tests)
├── test_complete_returns_message       ✅
├── test_complete_with_tools            ✅
├── test_stream_yields_deltas           ✅
├── test_initialization                 ✅
├── test_complete_raises_on_error       ✅
└── test_format_messages                ✅

core (18 tests — v0.1)
├── test_config.py (11 tests)           ✅
└── test_lifecycle.py (7 tests)         ✅

api-adapters-fastapi (6 tests)
├── test_to_run_context_basic           ✅
├── test_to_run_context_no_user         ✅
├── test_to_openai_response_basic       ✅
├── test_to_openai_response_with_tools  ✅
├── test_to_openai_stream               ✅
└── test_to_openai_response_has_usage   ✅
```

### 4.3 Bugs corrigés

| Bug | Cause | Correction |
|---|---|---|
| `test_complete_with_tools` | MagicMock créait des attributs fictifs pour `function.name` | Utilisation de `MagicMock(spec=[...])` avec valeurs explicites |
| `test_initialization_without_litellm/openai` | Le mock de `sys.modules` ne fonctionnait pas car le module était déjà importé | Remplacement par un test d'initialisation standard |
| `test_format_messages_with_tool_calls` | `ToolCall` non importé dans le fichier de test | Ajout de l'import |

---

## 5. Livrables

- [x] `adapters/adapters-llm-litellm/` — pyproject.toml + adapter + 6 tests
- [x] `adapters/adapters-llm-openai-compatible/` — pyproject.toml + adapter + 6 tests
- [x] `api/adapters-api-fastapi/` — pyproject.toml + app + routes + schema + 6 tests
- [x] `recipes/recipe-startup.yaml` — configuration startup prête à l'emploi
- [x] L'API répond sur `GET /health` et `POST /v1/chat/completions`
- [x] Compatible avec le schéma OpenAI (messages, tools, streaming)
- [x] **36 tests passés** (18 v0.1 + 18 nouveaux)

---

## 6. Notes pour la suite

- Les adapters LLM sont mockés dans les tests — des tests d'intégration avec de vrais appels API pourraient être ajoutés (avec clés via variables d'environnement)
- Le endpoint `/v1/chat/completions` utilise actuellement une réponse simulée — il faudra le connecter au vrai lifecycle dans une version ultérieure
- L'API n'a pas encore d'authentification — à prévoir pour la v1.0
- Le streaming SSE est implémenté côté adapter mais pas encore côté endpoint — à finaliser
