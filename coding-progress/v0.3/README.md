# v0.3 — Adapters Mémoire Production

> **Statut : ✅ Terminé**
> **Date : 2026-07-06**
> **Tests : 43/43 passés**

---

## 1. Objectif

Remplacer SQLite par des bases de données production pour la persistance et la recherche sémantique.

- **Redis** : mémoire de travail (WorkingMemory) + historique (EpisodicMemory)
- **Qdrant** : mémoire sémantique vectorielle (SemanticMemory)
- **PostgreSQL/pgvector** : mémoire sémantique + historique (SemanticMemory + EpisodicMemory)

---

## 2. Fichiers créés (18 fichiers)

### 2.1 Adapter Redis

| Fichier | Description |
|---|---|
| `adapters/adapters-memory-redis/pyproject.toml` | Dépendances : `redis[hiredis]>=5.0.0` |
| `adapters/adapters-memory-redis/agentforge_redis/__init__.py` | `RedisWorkingMemory` (WorkingMemoryPort) + `RedisEpisodicMemory` (EpisodicMemoryPort) |
| `adapters/adapters-memory-redis/tests/test_redis.py` | 9 tests : set/get, delete, TTL, key_prefix, append, history, search |

**Détails d'implémentation :**
- `RedisWorkingMemory` : stockage avec `setex()` et TTL configurable (défaut 1h)
- `RedisEpisodicMemory` : Redis List avec `lpush` + `ltrim` (max_history configurable)
- Clés préfixées : `agentforge:working:{run_id}`, `agentforge:episodic:{session_id}`
- Support Redis asynchrone via `redis.asyncio`

### 2.2 Adapter Qdrant

| Fichier | Description |
|---|---|
| `adapters/adapters-memory-qdrant/pyproject.toml` | Dépendances : `qdrant-client>=1.9.0` |
| `adapters/adapters-memory-qdrant/agentforge_qdrant/__init__.py` | `QdrantSemanticMemory` (SemanticMemoryPort) |
| `adapters/adapters-memory-qdrant/tests/test_qdrant.py` | 6 tests : upsert/search, delete, filters, empty, embedding |

**Détails d'implémentation :**
- Collection auto-créée avec `VectorParams` (Distance.COSINE)
- Embedding de fallback basé sur hash MD5 (⚠️ développement uniquement)
- Filtres metadata via `FieldCondition` + `MatchValue`
- Support AsyncQdrantClient natif

### 2.3 Adapter PostgreSQL/pgvector

| Fichier | Description |
|---|---|
| `adapters/adapters-memory-postgres-pgvector/pyproject.toml` | Dépendances : `psycopg[binary]>=3.2.0`, `psycopg-pool>=3.2.0` |
| `adapters/adapters-memory-postgres-pgvector/agentforge_postgres/__init__.py` | `PostgresSemanticMemory` + `PostgresEpisodicMemory` + `PostgresConnectionPool` |
| `adapters/adapters-memory-postgres-pgvector/agentforge_postgres/migrations/0001_init_semantic.sql` | Table semantic_facts avec vector + index IVFFlat |
| `adapters/adapters-memory-postgres-pgvector/agentforge_postgres/migrations/0002_init_episodic.sql` | Table episodic_messages avec index session + timestamp |
| `adapters/adapters-memory-postgres-pgvector/tests/test_postgres.py` | 10 tests : pool, upsert, search, delete, embedding, append, history |

**Détails d'implémentation :**
- `PostgresConnectionPool` : pool de connexions asynchrone (psycopg_pool)
- `PostgresSemanticMemory` : recherche cosinus via `<=>` operator, index IVFFlat
- `PostgresEpisodicMemory` : recherche ILIKE, index sur session_id et timestamp
- Schéma auto-créé (`CREATE TABLE IF NOT EXISTS`, `CREATE EXTENSION IF NOT EXISTS vector`)
- Gestion propre des connexions (get/put pool)

---

## 3. Décisions techniques

### 3.1 Pourquoi trois adapters mémoire différents ?

Chaque technologie a des forces différentes :

| Technologie | Idéal pour | Latence | Persistance |
|---|---|---|---|
| **Redis** | Working Memory (volatile, TTL) | Très faible | Optionnelle (RDB/AOF) |
| **Qdrant** | Recherche sémantique vectorielle | Faible | Oui (sur disque) |
| **PostgreSQL** | Mémoire unifiée (tout-en-un) | Moyenne | Oui (transactionnelle) |

L'utilisateur choisit selon son besoin : une stack Redis+Qdrant pour la performance, ou PostgreSQL seul pour la simplicité.

### 3.2 Pourquoi un embedding de fallback (hash) ?

Qdrant et PostgreSQL/pgvector nécessitent des vecteurs d'embedding. En développement, on ne veut pas dépendre d'une API d'embedding (OpenAI, etc.). Le hash MD5 produit un vecteur déterministe — assez bon pour les tests, mais **toujours à remplacer en production**.

### 3.3 Pourquoi psycopg plutôt que asyncpg ?

- `psycopg` v3 a un support natif de l'asyncio
- Meilleure compatibilité avec pgvector
- Pool de connexions intégré (`psycopg_pool`)
- Plus maintenu et documenté

### 3.4 Gestion des connexions PostgreSQL

Toutes les méthodes suivent le pattern :
```python
conn = await self._pool_mgr.get_connection()
try:
    # ... requêtes ...
finally:
    await self._pool_mgr.put_connection(conn)
```
Garantit qu'une connexion est toujours libérée, même en cas d'erreur.

---

## 4. Tests — Résultats

### 4.1 Commande
```bash
pytest adapters/adapters-memory-redis/tests/ \
       adapters/adapters-memory-qdrant/tests/ \
       adapters/adapters-memory-postgres-pgvector/tests/ \
       core/tests/test_config.py \
       core/tests/test_lifecycle.py -v
```

### 4.2 Résultat : 43/43 ✅

```
adapters-memory-redis (9 tests)
├── RedisWorkingMemory (5)              ✅✅✅✅✅
└── RedisEpisodicMemory (4)             ✅✅✅✅

adapters-memory-qdrant (6 tests)
└── QdrantSemanticMemory (6)            ✅✅✅✅✅✅

adapters-memory-postgres-pgvector (10 tests)
├── PostgresConnectionPool (2)          ✅✅
├── PostgresSemanticMemory (5)          ✅✅✅✅✅
└── PostgresEpisodicMemory (3)          ✅✅✅

core (18 tests — v0.1)
├── test_config.py (11)                 ✅✅✅✅✅✅✅✅✅✅✅
└── test_lifecycle.py (7)               ✅✅✅✅✅✅✅
```

### 4.3 Bugs corrigés

| Bug | Cause | Correction |
|---|---|---|
| `AsyncPool` inexistant | `psycopg` 3.3.x a renommé `AsyncPool` en `AsyncConnectionPool` | Utilisation de `psycopg_pool.AsyncConnectionPool` |
| `mock_conn.cursor()` coroutine | Le mock ne gérait pas `async with` | Ajout de `__aenter__`/`__aexit__` sur les mocks |
| ImportError au `__init__` | Le `try/except` catchait psycopg avant vérification | Correction des imports + installation de `psycopg-pool` |

---

## 5. Livrables

- [x] `adapters/adapters-memory-redis/` — pyproject.toml + adapter (2 ports) + 9 tests
- [x] `adapters/adapters-memory-qdrant/` — pyproject.toml + adapter (1 port) + 6 tests
- [x] `adapters/adapters-memory-postgres-pgvector/` — pyproject.toml + adapter (2 ports) + pool + migrations + 10 tests
- [x] Tous les adapters sont testés (mockés)
- [x] **43 tests passés** (18 v0.1 + 18 v0.2 + 25 nouveaux)

---

## 6. Notes pour la suite

- Les embeddings de fallback (MD5 hash) sont à remplacer par un vrai modèle d'embedding en production (OpenAI, sentence-transformers, etc.)
- Les tests d'intégration avec de vraies instances Redis/Qdrant/PostgreSQL peuvent être ajoutés via testcontainers
- L'index IVFFlat dans PostgreSQL est configurable via `lists=100` — à ajuster selon le volume de données
- Pour Qdrant, la collection est créée automatiquement au premier appel — prévoir une option de configuration avancée
- La prochaine version (v0.4) ajoutera Tools MCP, Trace Langfuse/OpenTelemetry, et Eval Ragas/DeepEval
