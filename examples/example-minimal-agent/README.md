# Example: Minimal Agent

> Agent minimal avec zéro dépendance externe.
> Utilise la recette minimale et les adapters par défaut embarqués.

---

## Description

Cet exemple montre comment créer et exécuter un agent AgentForge avec **aucune dépendance externe** (pas de base de données, pas de LLM, pas de serveur).

L'agent utilise :
- **Orchestration** : MinimalOrchestrator (boucle synchrone)
- **Mémoires** : In-memory + SQLite
- **LLM** : Aucun (réponse simulée)

## Prérequis

- Python 3.11+
- AgentForge installé : `pip install -e .`

## Fichiers

```
example-minimal-agent/
├── main.py          # Point d'entrée
├── config.yaml      # Configuration minimale
└── README.md        # Ce fichier
```

## Utilisation

```bash
cd examples/example-minimal-agent
python main.py
```

## Exemple de sortie

```
🔧 AgentForge - Minimal Agent
=============================
🤖 Agent initialisé avec la recette : config.yaml
💬 Tapez 'quit' pour quitter

Vous: Bonjour !
Agent: Réponse à : Bonjour !

Vous: Quel temps fait-il ?
Agent: Réponse à : Quel temps fait-il ?

Vous: quit
👋 Au revoir !
```
