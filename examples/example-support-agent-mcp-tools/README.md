# Example: Support Agent with MCP Tools

> Agent de support client avec outils MCP (CRM, planification, recherche).
> Utilise la recette startup avec LiteLLM et SQLite.

---

## Description

Cet exemple montre un agent de support client capable de :
- Rechercher des informations dans une base de connaissances via MCP
- Planifier des rendez-vous
- Consulter un CRM
- Maintenir le contexte de la conversation

## Prérequis

- Python 3.11+
- AgentForge installé : `pip install -e ".[yaml]"`
- LiteLLM : `pip install -e ./adapters/adapters-llm-litellm`
- Un serveur MCP en cours d'exécution

## Structure

```
example-support-agent-mcp-tools/
├── main.py              # Point d'entrée
├── config.yaml          # Configuration startup + MCP
├── skills/              # Compétences procédurales
│   └── support.md       # Instructions pour le support
└── README.md            # Ce fichier
```

## Utilisation

```bash
# 1. Démarrer un serveur MCP (ex: filesystem)
npx @modelcontextprotocol/server-filesystem ./data &

# 2. Lancer l'agent
cd examples/example-support-agent-mcp-tools
python main.py
```

## Compétences

Le fichier `skills/support.md` contient les instructions pour l'agent de support :
- Politique de remboursement
- Procédure de planification
- Escalade vers un humain
