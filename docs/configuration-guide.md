# Configuration Guide — AgentForge

> Comment écrire et personnaliser un fichier de configuration (recette).

---

## 1. Structure du fichier YAML

```yaml
agent:
  name: mon-agent
  version: "1.0.0"

ports:
  llm:
    adapter: litellm
    config:
      model: gpt-4o-mini
      temperature: 0.7
      max_tokens: 4096

guardrails:
  max_iterations: 20
  token_budget: 100000
  timeout_seconds: 120
```

---

## 2. Section `agent`

Informations générales sur l'agent.

| Champ | Type | Requis | Défaut | Description |
|---|---|---|---|---|
| `name` | `string` | Oui | — | Nom de l'agent |
| `version` | `string` | Oui | — | Version sémantique |

---

## 3. Section `ports`

Configuration de chaque port. Structure type :

```yaml
ports:
  nom_du_port:
    adapter: nom_de_l'adapter    # Requis
    enabled: true                # Optionnel (défaut: true)
    config:                      # Optionnel
      key: value
```

### Ports disponibles

| Port | Adapters disponibles |
|---|---|
| `llm` | `litellm`, `openai-compatible` |
| `orchestration` | `minimal`, `langgraph`, `temporal` |
| `working_memory` | `inmemory`, `redis` |
| `semantic_memory` | `sqlite`, `qdrant`, `postgres` |
| `episodic_memory` | `sqlite`, `redis`, `postgres` |
| `procedural_memory` | `default` |
| `tool_registry` | `default`, `mcp` |
| `event_bus` | `inprocess`, `nats` |
| `trace` | `default`, `langfuse`, `otel` |
| `eval` | `default`, `ragas`, `deepeval` |
| `analytics` | `default`, `clickhouse` |

### Désactiver un port

```yaml
ports:
  analytics:
    enabled: false    # Pas d'erreur si non résolu
```

---

## 4. Section `guardrails`

Règles d'arrêt de la boucle d'exécution.

| Champ | Type | Défaut | Description |
|---|---|---|---|
| `max_iterations` | `int` | 20 | Nombre maximum d'itérations |
| `token_budget` | `int` | 100000 | Budget maximum de tokens |
| `timeout_seconds` | `int` | 120 | Timeout maximum en secondes |

---

## 5. Variables d'environnement

Utilisez la syntaxe `${VAR_NAME}` dans les fichiers YAML :

```yaml
ports:
  llm:
    adapter: litellm
    config:
      api_key: "${OPENAI_API_KEY}"
  trace:
    adapter: langfuse
    config:
      public_key: "${LANGFUSE_PUBLIC_KEY}"
      secret_key: "${LANGFUSE_SECRET_KEY}"
```

---

## 6. Exemples de configuration

### Minimal (zéro dépendance)

```yaml
agent:
  name: minimal-agent
  version: "0.1.0"
ports:
  llm:
    adapter: minimal
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
    config: {}
  tool_registry:
    adapter: default
    config: {}
  event_bus:
    adapter: inprocess
    config: {}
  trace:
    adapter: default
    config: {}
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

### Startup (LiteLLM + SQLite)

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

### Enterprise (stack complète)

Voir `recipes/recipe-enterprise.yaml`.

---

## 7. Validation et debugging

### Validation automatique
Au chargement, la configuration est validée par `ConfigLoader.load()` :
- Champs requis vérifiés
- Noms de ports valides
- Types corrects

### Erreurs courantes

| Erreur | Cause | Solution |
|---|---|---|
| `Fichier introuvable` | Chemin incorrect | Vérifier le chemin |
| `Champ obligatoire manquant` | Section `agent` ou `ports` absente | Ajouter la section |
| `Nom de port inconnu` | Port mal orthographié | Vérifier la liste des ports |
| `Adapter non trouvé` | Package adapter non installé | `pip install adapters-...` |
