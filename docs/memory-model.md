# Memory Model — AgentForge

> Modèle des 3 mémoires et stratégie de consolidation.

---

## 1. Architecture des 3 mémoires

```
                    ┌─────────────────────────┐
                    │     Working Memory       │
                    │   (contexte du run)      │
                    │   éphémère, volatil      │
                    └───────────┬─────────────┘
                                │ hydratation (Phase 1)
              ┌─────────────────┼─────────────────┐
              ▼                 ▼                  ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │  Procédurale  │   │  Sémantique   │   │  Épisodique   │
    │  (savoir-faire)│   │  (faits)      │   │  (historique) │
    │  Skills.md    │   │  Connaissances│   │  Conversations│
    │  Instructions │   │  Profil user  │   │  Événements   │
    └──────────────┘   └──────────────┘   └──────────────┘
```

---

## 2. Mémoire Procédurale

**Rôle** : Stocke les compétences et instructions (savoir-faire).

**Contenu typique** :
- Fichiers `.md` décrivant des procédures
- Instructions système (prompts système)
- Règles métier

**Adapter par défaut** : `DefaultProceduralMemory`
- Source : dossier `./skills/`
- Format : fichiers Markdown (`.md`)
- Chargement : par nom de compétence

**Exemple de fichier skill** (`skills/assistant.md`) :
```markdown
# Compétence : Assistant

Tu es un assistant IA spécialisé dans l'aide aux développeurs.
- Réponds en français
- Donne des exemples de code quand c'est pertinent
- Explique les concepts simplement
```

---

## 3. Mémoire Sémantique

**Rôle** : Stocke les faits durables et les connaissances (savoir).

**Contenu typique** :
- Profil utilisateur (préférences, historique)
- Faits extraits des conversations
- Connaissances du domaine

**Opérations** :
- `search(query, top_k, filters)` → recherche par similarité
- `upsert(fact)` → ajout ou mise à jour
- `delete(fact_id)` → suppression

**Structure d'un fait** :
```python
{
    "id": "uuid_unique",
    "content": "L'utilisateur préfère Python pour le ML",
    "metadata": {"source": "consolidation", "confidence": 0.9},
    "embedding": [0.1, 0.2, ...],  # optionnel
}
```

**Adapters disponibles** :
| Adapter | Type | Idéal pour |
|---|---|---|
| SQLite | Textuelle | Développement local |
| Qdrant | Vectorielle | Recherche sémantique performante |
| PostgreSQL/pgvector | Vectorielle | Solution unifiée avec l'épisodique |

---

## 4. Mémoire Épisodique

**Rôle** : Stocke l'historique daté des conversations.

**Contenu typique** :
- Messages échangés (user + assistant)
- Appels d'outils et résultats
- Événements système

**Opérations** :
- `append(event)` → ajouter un message
- `get_history(session_id, limit)` → historique d'une session
- `search_hybrid(query, since, top_k)` → recherche dans l'historique

**Adapters disponibles** :
| Adapter | Stockage | Idéal pour |
|---|---|---|
| SQLite | Tables SQL | Développement local |
| Redis | Lists | Haute performance, TTL |
| PostgreSQL | JSONB | Solution unifiée, requêtes avancées |

---

## 5. Cycle de vie des mémoires pendant un run

### Phase 1 : Hydratation
```
1. Charger l'historique épisodique de la session
2. Rechercher les faits sémantiques pertinents
3. Charger les compétences procédurales
4. Assembler → Working Memory
```

### Phase 3 : Persistance
```
1. Sauvegarder les messages dans la mémoire épisodique
2. Compter le nombre de nouveaux échanges
3. Si > seuil N (défaut: 10) → consolidation
```

---

## 6. Consolidation

**Déclencheur** : après N nouveaux échanges (10 par défaut).

**Processus** :
1. Extraire les derniers messages échangés
2. Générer un résumé
3. Extraire les faits pertinents
4. Upsert dans la mémoire sémantique

**Stratégie actuelle** :
```python
# Simplifié : résumé textuel des échanges
fact = {
    "id": f"consolidated-{run_id}",
    "content": f"Résumé de la session {session_id}:\n{échanges}",
    "metadata": {"source": "consolidation", "session_id": session_id},
}
await semantic_memory.upsert(fact)
```

**Améliorations futures** :
- Utiliser un LLM pour résumer (Summarizer Agent)
- Extraction structurée des entités et relations
- Scoring de confiance pour chaque fait extrait
- Consolidation asynchrone (ne bloque pas la réponse)
