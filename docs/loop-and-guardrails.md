# Loop and Guardrails — AgentForge

> Détail du cycle Planner/Executor/Reflector/Verifier et des conditions d'arrêt.

---

## 1. La boucle de raisonnement

```
                    ┌─────────────┐
                    │   Planner    │
                    │  (décompose) │
                    └──────┬──────┘
                           │ étapes
                           ▼
                    ┌─────────────┐
              ┌─────│  Executor   │─────┐
              │     │ (exécute)   │     │
              │     └──────┬──────┘     │
              │            │ résultat   │
              │            ▼            │
              │     ┌─────────────┐     │
              └─────│  Reflector  │─────┘
                    │ (analyse)   │
                    └──────┬──────┘
                           │ si toutes les étapes faites
                           ▼
                    ┌─────────────┐
              ┌─────│  Verifier   │─────┐
              │     │ (valide)    │     │
              │     └──────┬──────┘     │
              │            │            │
              │ si échec   │ si valide  │ si réussi
              └────────────┘            │
                                        ▼
                                 ┌─────────────┐
                                 │  Réponse    │
                                 │  finale     │
                                 └─────────────┘
```

---

## 2. Planner

**Rôle** : Décomposer l'objectif utilisateur en une séquence d'étapes.

```python
class Planner(ABC):
    async def plan(self, context: RunContext) -> list[str]:
        """Retourne une liste d'étapes à exécuter."""
```

**Stratégies d'implémentation** :
- **Par défaut** : retourne `["répondre"]` (pas de planification)
- **LLM-based** : utilise le LLM pour décomposer la requête
- **Règle métier** : pattern matching sur le type de requête

**Exemple de planification LLM** :
```
Requête : "Quel est le prix de l'action Apple et envoie un email à Paul"
Étapes : [
    "1. Rechercher le prix actuel de l'action Apple",
    "2. Envoyer un email à Paul avec le prix",
]
```

---

## 3. Executor

**Rôle** : Exécuter une étape (tool call ou réponse LLM).

```python
class Executor(ABC):
    async def execute(self, context: RunContext, step: str) -> ToolResult | Message:
        """Exécute une étape planifiée."""
```

**Logique de décision** :
1. Analyser l'étape pour déterminer l'outil nécessaire
2. Si un outil correspond → `tool_registry.execute(name, args)`
3. Sinon → `llm.complete(messages)` pour générer une réponse

---

## 4. Reflector

**Rôle** : Analyser le résultat d'une étape et décider de la suite.

```python
class Reflector(ABC):
    async def reflect(self, context: RunContext, result: ToolResult) -> str | None:
        """Retourne une correction si nécessaire, None si OK."""
```

**Cas traités** :
- **Succès** : l'étape est valide → passer à la suivante
- **Erreur outil** : résultat invalide → suggérer une correction
- **Données incomplètes** : besoin de plus d'informations → nouvelle étape

---

## 5. Verifier

**Rôle** : Valider que la réponse finale répond à la requête.

```python
class Verifier(ABC):
    async def verify(self, context: RunContext, final_response: Message) -> bool:
        """True si la réponse est valide, False sinon."""
```

**Vérifications effectuées** :
1. La réponse n'est pas vide
2. Tous les outils appelés ont un résultat
3. La réponse est cohérente avec la requête
4. Option : LLM-as-Judge pour la qualité

---

## 6. Guardrails

Règles d'arrêt qui protègent contre les boucles infinies et la consommation excessive de ressources.

### 6.1 Max Iterations

```yaml
guardrails:
  max_iterations: 20  # Arrêt après 20 itérations
```

**Déclencheur** : `context.metadata.iteration_count >= context.max_iterations`
**Action** : Arrêt de la boucle, message d'avertissement

### 6.2 Token Budget

```yaml
guardrails:
  token_budget: 100000  # Arrêt après 100k tokens
```

**Déclencheur** : `context.metadata.token_count >= context.token_budget`
**Action** : Arrêt de la boucle, message d'avertissement

### 6.3 Timeout

```yaml
guardrails:
  timeout_seconds: 120  # Arrêt après 2 minutes
```

**Déclencheur** : `asyncio.wait_for()` lève `TimeoutError`
**Action** : Arrêt de la boucle, message d'expiration

### 6.4 Ordre de vérification

1. Avant chaque itération : vérifier `is_exhausted()`
2. Pendant l'exécution : `asyncio.wait_for(timeout)`
3. Après l'exécution : vérifier à nouveau `is_exhausted()`

---

## 7. Stratégies de fallback

En cas d'échec d'une étape :

| Situation | Fallback |
|---|---|
| Tool call échoué | Retenter avec des paramètres corrigés (Reflector) |
| LLM indisponible | Passer à un modèle de fallback |
| Timeout dépassé | Retourner un message partiel |
| Tous les fallbacks épuisés | Message d'erreur explicite à l'utilisateur |

---

## 8. Exemple de flux complet

```
1. Utilisateur : "Quel temps fait-il à Paris et à Londres ?"

2. Planner → ["météo Paris", "météo Londres"]

3. Executor("météo Paris") → ToolCall(get_weather, city="Paris")
   → ToolResult(content="15°C, ensoleillé")

4. Reflector → OK, résultat valide

5. Executor("météo Londres") → ToolCall(get_weather, city="Londres")
   → ToolResult(content="10°C, pluvieux")

6. Reflector → OK, toutes les étapes faites

7. Verifier → la réponse couvre les 2 villes ? Oui ✅

8. Réponse finale : "À Paris il fait 15°C et ensoleillé, 
   à Londres il fait 10°C et pluvieux."
```
