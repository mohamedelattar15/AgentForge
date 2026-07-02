# AgentForge

**Un framework modulaire pour construire des agents IA modernes — Harness, Loop, Memory, LLM Ops, Eval — avec une architecture Ports & Adapters permettant de brancher n'importe quelle stack technique sans jamais toucher au cœur du système.**

---

## 1. Objectif du projet

La plupart des projets d'agents IA mélangent deux choses qui devraient rester séparées : la **logique générique** d'un agent (comment il assemble son contexte, comment il boucle sur des outils, comment il s'auto-évalue) et les **choix technologiques** (quel LLM, quel vector store, quel orchestrateur).

Résultat : chaque équipe réécrit le même moteur d'agent, couplé en dur à sa stack du moment (LangGraph + Redis + Qdrant aujourd'hui, autre chose demain), et rien n'est réutilisable d'un projet à l'autre.

**AgentForge** résout ce problème en fournissant :

1. **Un cœur (`core`) stable et minimal** qui implémente l'architecture d'agent moderne — Harness, Loop, Memory (procédurale/sémantique/épisodique), LLM Ops, Eval — sous forme de **contrats abstraits (ports)**, jamais de dépendances concrètes.
2. **Une bibliothèque d'adapters interchangeables** — un par technologie (Redis, Qdrant, PostgreSQL, LangGraph, Temporal, Langfuse, Ragas...) — chacun installable indépendamment et remplaçable sans changement de code métier.
3. **Un mécanisme de composition par configuration déclarative**, permettant d'assembler un agent complet — de la stack la plus légère (zéro dépendance externe) à la stack la plus lourde (Kubernetes + Temporal + ClickHouse) — sans écrire de code d'orchestration.

**Le but final** : que n'importe quel développeur puisse importer AgentForge dans un projet totalement différent (support client, assistant interne, automatisation métier...), choisir sa stack via un fichier de config, et obtenir un agent conforme à l'architecture standard — traçable, évaluable, et amélioré en continu — sans jamais réécrire le moteur.

---

## 2. Philosophie architecturale

### 2.1 Ports & Adapters (architecture hexagonale) appliquée à l'agent

Chaque brique du schéma d'architecture n'est pas "une techno", c'est un **port** : une interface qui décrit *ce que le composant doit faire*, jamais *comment*. Les technologies concrètes (Redis, Qdrant, LangGraph, Temporal...) sont des **adapters** — des implémentations remplaçables du port correspondant.

```
                     ┌─────────────────────────────┐
                     │   Fichier de configuration   │
                     │   (choix des adapters)       │
                     └──────────────┬───────────────┘
                                    │ résolution au runtime
                                    ▼
   ┌────────────────────────────────────────────────────────────┐
   │                         CORE (ports)                        │
   │   LLMPort · OrchestrationPort · MemoryPorts (x3) · ToolPort │
   │   TracePort · EvalPort · EventBusPort                       │
   └───────────────┬───────────────────────────┬─────────────────┘
                    │ implémente                │ implémente
                    ▼                           ▼
       ┌─────────────────────┐      ┌─────────────────────────┐
       │  Adapters "légers"   │      │  Adapters "entreprise"   │
       │  (défaut, embarqué)  │      │  (packages optionnels)   │
       │  in-memory, SQLite   │      │  Redis, Qdrant, Postgres │
       │  LiteLLM local       │      │  LangGraph, Temporal,    │
       │                      │      │  Langfuse, ClickHouse... │
       └─────────────────────┘      └─────────────────────────┘
```

### 2.2 Principe non négociable

> **Aucune ligne dans `core/` ne doit importer un SDK, un driver, ou un nom de produit.**
> Le `core` ne connaît que des contrats. Toute dépendance concrète vit exclusivement dans un package `adapters-*`.

Ce principe est ce qui garantit la réutilisabilité : le framework reste identique quel que soit le contexte de déploiement, seule la config change.

### 2.3 L'architecture d'agent moderne conservée à l'identique

Le framework respecte fidèlement les 5 phases du cycle de vie identifiées dans le schéma de référence :

1. **Hydratation du contexte** — assemblage de la Working Memory à partir des 3 mémoires (procédurale, sémantique, épisodique)
2. **Boucle d'exécution (Loop)** — Planner → Executor (tool calls) → Reflector → Verifier, avec guardrails de sortie
3. **Persistance** — sauvegarde des messages, consolidation différée vers la mémoire sémantique
4. **Traçage** — une trace systématique par run, découplée de la latence utilisateur
5. **Évaluation asynchrone** — eval-as-judge, diagnostic, gate, release du fix

---

## 3. Vue d'ensemble du repository

```
agentforge/
├── README.md
├── LICENSE
├── pyproject.toml
├── CONTRIBUTING.md
├── ARCHITECTURE.md
│
├── core/                              # Le noyau — zéro dépendance lourde
│   ├── agentforge_core/
│   │   ├── __init__.py
│   │   ├── ports/
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
│   │   ├── lifecycle/
│   │   │   ├── run_context.py
│   │   │   ├── hydrate_context.py
│   │   │   ├── loop_controller.py
│   │   │   ├── persist_stage.py
│   │   │   ├── trace_stage.py
│   │   │   └── eval_stage.py
│   │   ├── loop/
│   │   │   ├── planner.py
│   │   │   ├── executor.py
│   │   │   ├── reflector.py
│   │   │   └── verifier.py
│   │   ├── registry/
│   │   │   └── adapter_registry.py
│   │   ├── config/
│   │   │   ├── schema.py
│   │   │   └── loader.py
│   │   └── errors.py
│   └── tests/
│       └── contract_tests/            # Tests de conformité pour tout adapter
│           ├── test_llm_port_contract.py
│           ├── test_memory_ports_contract.py
│           └── test_tool_registry_contract.py
│
├── adapters/                          # Un package indépendant par technologie
│   ├── adapters-llm-litellm/
│   ├── adapters-llm-openai-compatible/
│   ├── adapters-orchestration-langgraph/
│   ├── adapters-orchestration-temporal/
│   ├── adapters-orchestration-minimal/   # défaut, embarqué dans core
│   ├── adapters-memory-redis/
│   ├── adapters-memory-inmemory/         # défaut, embarqué dans core
│   ├── adapters-memory-qdrant/
│   ├── adapters-memory-postgres-pgvector/
│   ├── adapters-memory-sqlite/           # défaut, embarqué dans core
│   ├── adapters-tools-mcp/
│   ├── adapters-eventbus-nats/
│   ├── adapters-eventbus-inprocess/      # défaut, embarqué dans core
│   ├── adapters-trace-langfuse/
│   ├── adapters-trace-opentelemetry/
│   ├── adapters-eval-ragas/
│   ├── adapters-eval-deepeval/
│   └── adapters-analytics-clickhouse/
│
├── recipes/                           # Combinaisons prêtes à l'emploi (config only)
│   ├── recipe-minimal.yaml            # zéro dépendance externe
│   ├── recipe-startup.yaml            # LiteLLM + Postgres/pgvector + Langfuse
│   └── recipe-enterprise.yaml         # stack complète type Kubernetes
│
├── api/
│   └── adapters-api-fastapi/
│       ├── agentforge_api/
│       │   ├── main.py
│       │   ├── routes/
│       │   │   ├── chat_completions.py    # façade OpenAI-compatible
│       │   │   └── health.py
│       │   └── openai_schema_adapter.py
│       └── README.md
│
├── examples/
│   ├── example-minimal-agent/
│   ├── example-support-agent-mcp-tools/
│   └── example-multi-tenant-saas/
│
├── docs/
│   ├── ports-reference.md             # spécification détaillée de chaque port
│   ├── adapters-matrix.md             # tableau de compatibilité port ↔ adapters
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
        └── overlays/
```

---

## 4. Contenu détaillé des fichiers et dossiers

### 4.1 `core/agentforge_core/ports/` — Les contrats invariants

Chaque fichier définit **une seule interface abstraite**, sans aucune implémentation. C'est la partie du framework qui ne doit quasiment jamais changer une fois stabilisée (versionnée en `major` en cas de breaking change).

| Fichier | Rôle du port | Méthodes conceptuelles exposées |
|---|---|---|
| `llm_port.py` | Contrat vers n'importe quel LLM | `complete(messages, tools?) → response`, `stream(messages) → deltas` |
| `orchestration_port.py` | Contrat de la boucle d'exécution | `run(run_context) → final_reply`, `should_stop(state) → bool` |
| `working_memory_port.py` | Contexte RAM éphémère du run | `get(run_id) → context`, `set(run_id, context)` |
| `semantic_memory_port.py` | Faits durables, profil utilisateur | `search(query, top_k, filters) → results`, `upsert(fact)` |
| `episodic_memory_port.py` | Historique daté des conversations | `search_hybrid(query, since, top_k) → results`, `append(event)` |
| `procedural_memory_port.py` | Compétences / instructions (Skill.md) | `load(skill_name) → text`, `list_skills() → names` |
| `tool_registry_port.py` | Catalogue d'outils exécutables | `list_tools() → schemas`, `execute(name, args) → result` |
| `event_bus_port.py` | Communication asynchrone interne | `publish(topic, event)`, `subscribe(topic, handler)` |
| `trace_port.py` | Émission d'une trace par run | `record(run_id, spans)` |
| `eval_port.py` | Scoring / jugement de qualité | `evaluate(run_trace) → score, verdict` |
| `analytics_port.py` | Agrégation à grande échelle | `ingest(metrics)`, `query(filters) → aggregates` |

### 4.2 `core/agentforge_core/lifecycle/` — Le cycle de vie en 5 phases

Ce module orchestre les phases décrites dans le schéma de référence, en n'appelant **que des ports**, jamais des adapters directement.

- `run_context.py` — objet représentant l'état complet d'un run (prompt utilisateur, historique, mémoire hydratée, résultat des tool calls, statut).
- `hydrate_context.py` — Phase 1 : interroge les 3 ports mémoire, assemble la Working Memory.
- `loop_controller.py` — Phase 2 : délègue au `OrchestrationPort` choisi, applique les guardrails (nombre max d'itérations, budget tokens, timeout).
- `persist_stage.py` — Phase 3 : sauvegarde les messages via `episodic_memory_port`, déclenche la consolidation différée (Summarizer Agent) au-delà d'un seuil `N` de nouveaux échanges.
- `trace_stage.py` — Phase 4 : émet systématiquement une trace via `trace_port`, de façon asynchrone (ne bloque jamais la réponse à l'utilisateur).
- `eval_stage.py` — Phase 5 : déclenche `eval_port` en tâche de fond, applique le mécanisme Gate → Diagnose/Release décrit dans l'architecture.

### 4.3 `core/agentforge_core/loop/` — Décomposition du raisonnement

- `planner.py` — contrat de planification : décompose l'objectif en étapes.
- `executor.py` — contrat d'exécution : réalise les tool calls planifiés.
- `reflector.py` — contrat de réflexion : analyse le résultat d'une étape avant de continuer.
- `verifier.py` — contrat de vérification : valide que la réponse finale répond réellement à la demande avant de sortir de la boucle.

### 4.4 `core/agentforge_core/registry/adapter_registry.py`

Mécanisme central de **découverte et résolution des adapters**. Chaque package `adapters-*` s'auto-déclare au chargement ("je fournis une implémentation de `SemanticMemoryPort`"). Le registre lit la configuration et instancie le bon adapter pour chaque port, au démarrage de l'agent.

### 4.5 `core/agentforge_core/config/`

- `schema.py` — schéma de validation du fichier de configuration (quels champs sont obligatoires, quels ports doivent être résolus).
- `loader.py` — charge un fichier YAML/JSON et produit un objet de configuration validé, consommé par le registre d'adapters.

### 4.6 `core/tests/contract_tests/`

Suite de tests **partagée**, appliquée à tout adapter revendiquant implémenter un port donné. Garantit qu'un adapter Redis et un adapter in-memory pour `WorkingMemoryPort` se comportent de façon strictement équivalente du point de vue du core. C'est ce qui empêche la dérive de comportement entre stacks différentes.

### 4.7 `adapters/` — Un package par technologie

Chaque sous-dossier est un **package Python installable indépendamment**, avec sa propre liste de dépendances. Structure type d'un adapter (exemple : `adapters-memory-postgres-pgvector/`) :

```
adapters-memory-postgres-pgvector/
├── pyproject.toml                 # dépend de core + psycopg + pgvector
├── agentforge_postgres/
│   ├── semantic_store.py          # implémente SemanticMemoryPort
│   ├── episodic_store.py          # implémente EpisodicMemoryPort
│   ├── migrations/                # schéma versionné (Alembic ou équivalent)
│   │   ├── 0001_init_semantic.sql
│   │   └── 0002_init_episodic.sql
│   └── connection_pool.py
└── tests/
    └── test_conformance.py        # exécute les contract_tests du core
```

Adapters prévus dans la v1 :

| Port | Adapters disponibles | Statut |
|---|---|---|
| LLM | LiteLLM (multi-provider), OpenAI-compatible générique | Prioritaire |
| Orchestration | Minimal (défaut), LangGraph, Temporal | Prioritaire |
| Working Memory | In-memory (défaut), Redis | Prioritaire |
| Semantic Memory | SQLite+vecteurs (défaut), Qdrant, PostgreSQL+pgvector | Prioritaire |
| Episodic Memory | SQLite (défaut), PostgreSQL | Prioritaire |
| Tools | MCP | Prioritaire |
| Event Bus | In-process (défaut), NATS | Secondaire |
| Trace | Fichier local (défaut), Langfuse, OpenTelemetry | Secondaire |
| Eval | Juge LLM simple (défaut), Ragas, DeepEval | Secondaire |
| Analytics | Désactivé (défaut), ClickHouse | Optionnel |

### 4.8 `recipes/` — Compositions prêtes à l'emploi

Fichiers **de configuration uniquement**, aucun code. Décrivent quel adapter utiliser pour chaque port.

- `recipe-minimal.yaml` — tous les ports résolus vers leurs adapters par défaut embarqués (aucune dépendance externe, pour du test local en 30 secondes).
- `recipe-startup.yaml` — LiteLLM + PostgreSQL/pgvector (mémoire unifiée) + Langfuse, sans Kubernetes ni Temporal.
- `recipe-enterprise.yaml` — la stack complète : LangGraph, Redis, Qdrant, PostgreSQL, Temporal, NATS, Langfuse, ClickHouse, Ragas+DeepEval.

### 4.9 `api/adapters-api-fastapi/`

Façade HTTP du framework, exposée en **API compatible OpenAI** (`/v1/chat/completions`), pour que l'agent assemblé soit consommable comme "un modèle" par n'importe quel client déjà habitué à ce standard (LangChain, IDE, autre agent...).

- `main.py` — point d'entrée FastAPI, charge la config, initialise le registre d'adapters.
- `routes/chat_completions.py` — traduit une requête HTTP au format OpenAI vers un `run_context`, invoque le cycle de vie du core, traduit la réponse en retour.
- `openai_schema_adapter.py` — conversion bidirectionnelle entre les objets internes du core et le schéma OpenAI (messages, tool_calls, streaming SSE).

### 4.10 `examples/`

Projets complets et autonomes montrant l'usage du framework dans des contextes différents, pour prouver la réutilisabilité :

- `example-minimal-agent/` — agent Q&A simple, recette minimale, zéro dépendance externe.
- `example-support-agent-mcp-tools/` — agent avec outils MCP (CRM, planification), recette "startup".
- `example-multi-tenant-saas/` — agent multi-tenant avec isolation par `tenant_id`, recette "enterprise".

### 4.11 `docs/`

- `ports-reference.md` — spécification exhaustive de chaque interface (signatures conceptuelles, garanties, cas d'erreur attendus).
- `adapters-matrix.md` — tableau de compatibilité et de trade-offs (latence, scalabilité, coût opérationnel) par adapter.
- `configuration-guide.md` — comment écrire un fichier de recette, comment surcharger un adapter.
- `memory-model.md` — détail du modèle des 3 mémoires et de la stratégie de consolidation.
- `loop-and-guardrails.md` — détail du cycle Planner/Executor/Reflector/Verifier et des conditions d'arrêt.
- `llmops-and-eval.md` — détail du cycle Trace → Eval → Gate → Diagnose/Release.

### 4.12 `deployment/`

- `docker-compose.minimal.yaml` — lance uniquement l'API + le core (aucune infra externe).
- `docker-compose.enterprise.yaml` — lance Redis, Qdrant, PostgreSQL, Temporal, NATS, Langfuse, ClickHouse en local pour tester la stack complète.
- `kubernetes/` — manifestes de déploiement en production pour la recette enterprise, organisés en `base/` (commun) + `overlays/` (par environnement).

---

## 5. Diagramme de composition au runtime

```
1. Chargement de la recette (recipes/*.yaml)
         │
         ▼
2. adapter_registry résout chaque port → instancie l'adapter concret
         │
         ▼
3. Un run arrive (via API FastAPI, façade OpenAI-compatible)
         │
         ▼
4. lifecycle exécute les 5 phases en n'appelant que les PORTS :
   hydrate_context → loop_controller → persist_stage → trace_stage → eval_stage
         │
         ▼
5. Le core ne sait jamais s'il tourne sur "recipe-minimal" ou "recipe-enterprise" —
   le comportement est identique, seule la performance/scalabilité change.
```

---

## 6. Principes de gouvernance du projet

- **Stabilité des ports > vitesse d'ajout de fonctionnalités.** Tout changement de signature d'un port est un breaking change versionné en `major`.
- **Aucun adapter n'est un citoyen de seconde zone.** Chaque adapter doit passer la suite de `contract_tests` du core avant d'être accepté dans le monorepo.
- **Le core ne dépasse jamais un budget de dépendances minimal** (aucun SDK de provider, aucun driver de base de données).
- **Chaque nouveau port proposé doit démontrer au moins 2 adapters distincts** avant d'être intégré, pour valider que l'abstraction n'est pas biaisée par une seule implémentation.
- **Documentation as contract** : `docs/ports-reference.md` fait foi ; toute divergence entre un adapter et cette spec est un bug.

---

## 7. Roadmap indicative

| Phase | Contenu |
|---|---|
| v0.1 | `core` + ports stabilisés + adapters par défaut (in-memory, SQLite, minimal) + recette minimale |
| v0.2 | Adapters LLM (LiteLLM, OpenAI-compatible) + façade API FastAPI compatible OpenAI |
| v0.3 | Adapters mémoire production (Redis, Qdrant, PostgreSQL/pgvector) + recette startup |
| v0.4 | Adapter Tools (MCP) + Trace (Langfuse) + Eval (Ragas, DeepEval) |
| v0.5 | Adapters orchestration avancée (LangGraph, Temporal) + Event Bus (NATS) + recette enterprise |
| v1.0 | Contract tests complets sur tous les adapters, documentation stabilisée, exemples multi-tenant |

---

## 8. Licence et contribution

Voir `CONTRIBUTING.md` pour les règles d'ajout d'un nouvel adapter (obligation de passer les contract tests, format de déclaration dans le registre) et `ARCHITECTURE.md` pour la version longue du raisonnement de conception ayant mené à cette structure.
