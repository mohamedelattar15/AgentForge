# LLMOps & Eval — AgentForge

> Cycle Trace → Eval → Gate → Diagnose/Release pour l'amélioration continue.

---

## 1. Le cycle LLM Ops

```
    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │  Trace   │───▶│   Eval   │───▶│   Gate   │───▶│ Release  │
    │ (Phase 4)│    │ (Phase 5)│    │ (décision)│    │ (amélior.)│
    └──────────┘    └──────────┘    └──────────┘    └──────────┘
                          │               │
                          ▼               ▼
                    ┌──────────┐    ┌──────────┐
                    │ Diagnose │    │  Fix     │
                    │ (analyse)│    │(correction)│
                    └──────────┘    └──────────┘
```

**Principe** : Chaque run produit une trace qui est évaluée. Si le score est insuffisant, un diagnostic est émis et un correctif peut être déclenché.

---

## 2. Phase 4 : Trace

**Objectif** : Enregistrer une trace systématique de chaque run, sans impacter la latence perçue par l'utilisateur.

### Données enregistrées

```python
{
    "run_id": "abc123",
    "user_query": "Quel temps fait-il ?",
    "messages": [
        {"role": "user", "content": "Quel temps fait-il ?"},
        {"role": "assistant", "content": "Il fait 15°C à Paris."},
    ],
    "spans": [
        {"name": "hydrate", "start_time": "...", "end_time": "...", "attributes": {...}},
        {"name": "loop", "start_time": "...", "end_time": "...", "attributes": {...}},
        {"name": "persist", "start_time": "...", "end_time": "...", "attributes": {...}},
    ],
    "status": "completed",
    "metadata": {
        "token_count": 150,
        "iteration_count": 2,
        "tool_call_count": 1,
    }
}
```

### Garanties
- **Asynchrone** : le tracing ne bloque jamais la réponse utilisateur
- **Systématique** : chaque run produit exactement une trace
- **Enrichissable** : les métadonnées peuvent être complétées après coup

### Adapters disponibles

| Adapter | Avantage |
|---|---|
| `DefaultTrace` | Simple, fichier JSON local, aucun service requis |
| `LangfuseTrace` | UI complète, scores, feedback, collaboration |
| `OTelTrace` | Standard ouvert, compatible Jaeger/Tempo/Grafana |

---

## 3. Phase 5 : Eval

**Objectif** : Évaluer la qualité de la réponse produite.

### Métriques disponibles

#### Ragas

| Métrique | Description | Score |
|---|---|---|
| `faithfulness` | La réponse est-elle fidèle au contexte ? | 0-1 |
| `answer_relevancy` | La réponse est-elle pertinente ? | 0-1 |
| `context_precision` | Le contexte était-il précis ? | 0-1 |
| `context_recall` | Tout le contexte utile a-t-il été utilisé ? | 0-1 |

#### DeepEval

| Métrique | Description |
|---|---|
| `G-Eval` | Évaluation LLM-as-Judge avec critères personnalisés |
| `AnswerRelevancyMetric` | Pertinence de la réponse |

### Format de retour

```python
EvalResult(
    score=0.85,           # 0.0 à 1.0
    verdict="passed",     # "passed", "needs_improvement", "failed"
    diagnosis="La réponse est fidèle au contexte mais pourrait être plus concise.",
    passed=True,          # True si score >= threshold
)
```

### Configuration

```yaml
ports:
  eval:
    adapter: ragas
    config:
      metrics: ["faithfulness", "answer_relevancy"]
      threshold: 0.7
```

---

## 4. Gate : Mécanisme de décision

**Rôle** : Décider si la réponse est acceptable ou si un correctif est nécessaire.

### Seuils

| Zone | Score | Action |
|---|---|---|
| ✅ Pass | ≥ 0.7 | Release : la réponse est validée |
| ⚠️ Warning | 0.4 - 0.7 | Diagnose : analyser les causes |
| ❌ Fail | < 0.4 | Diagnose + Fix : correction obligatoire |

### Algorithme

```python
if result.score >= GATE_THRESHOLD:  # 0.7
    # Release : la réponse est validée
    return EvalResult(score=..., verdict="passed", passed=True)
else:
    # Diagnose : analyser les causes
    diagnosis = analyze_failure(run_trace)
    return EvalResult(score=..., verdict="needs_improvement",
                      diagnosis=diagnosis, passed=False)
```

---

## 5. Diagnose : Analyse des échecs

**Objectif** : Comprendre pourquoi un run a obtenu un score insuffisant.

### Causes courantes

| Problème | Symptôme | Solution |
|---|---|---|
| Contexte insuffisant | Score de faithfulness bas | Améliorer l'hydratation du contexte |
| Outil mal configuré | Tool call échoué | Vérifier la configuration MCP |
| Prompt flou | Réponse hors-sujet | Améliorer le prompt système |
| Modèle inadapté | Score général bas | Changer de modèle LLM |
| Guardrail trop strict | Run interrompu | Ajuster les seuils |

---

## 6. Release : Amélioration continue

**Objectif** : Boucle de feedback pour améliorer l'agent.

### Actions possibles

1. **Ajustement de configuration** : modifier les paramètres de l'adapter
2. **Amélioration du prompt** : enrichir la mémoire procédurale
3. **Changement d'adapter** : passer à une technologie plus adaptée
4. **Ajout d'outils** : enrichir le registre MCP

### Workflow idéal

```
Run échoué → Trace → Eval → Gate (Fail)
    → Diagnose : "contexte insuffisant"
    → Fix : ajouter des faits sémantiques
    → Nouveau run → Trace → Eval → Gate (Pass) ✅
    → Release : nouvelle version de l'adapter
```

---

## 7. Métriques opérationnelles

### Métriques collectées par ClickHouse

```sql
CREATE TABLE run_metrics (
    run_id String,
    timestamp DateTime,
    status String,
    latency_ms Float64,
    token_count UInt32,
    iteration_count UInt32,
    tool_call_count UInt32,
    eval_score Float64,
    llm_model String,
    ...
) ENGINE = MergeTree()
ORDER BY (timestamp, run_id)
```

### Requêtes utiles

```sql
-- Taux de succès par modèle
SELECT llm_model,
       count() AS total,
       avg(eval_score) AS avg_score
FROM run_metrics
WHERE timestamp >= now() - INTERVAL 7 DAY
GROUP BY llm_model

-- Latence moyenne par orchestrateur
SELECT status,
       avg(latency_ms) AS avg_latency,
       quantile(0.95)(latency_ms) AS p95_latency
FROM run_metrics
GROUP BY status
```
