# Coding Progress — AgentForge

> Suivi de développement du framework AgentForge.
> Chaque version documente : les objectifs, les fichiers créés, les décisions techniques, et les résultats des tests.

---

## Structure

```
coding-progress/
├── README.md                    # Ce fichier — vue d'ensemble
├── v0.1/                        # Core + Ports + Adapters par défaut
│   └── README.md
├── v0.2/                        # Adapters LLM + API FastAPI
│   └── README.md
└── v0.3/                        # Adapters mémoire production (Redis, Qdrant, PostgreSQL)
    └── README.md
```

Les versions suivantes (v0.3, v0.4, v0.5, v1.0) seront ajoutées au fur et à mesure.

---

## État d'avancement

| Version | Statut | Tests | Date |
|---|---|---|---|
| [v0.1](./v0.1/README.md) | ✅ Terminé | 18/18 passés | 2026-07-06 |
| [v0.2](./v0.2/README.md) | ✅ Terminé | 36/36 passés | 2026-07-06 |
| [v0.3](./v0.3/README.md) | ✅ Terminé | 43/43 passés | 2026-07-06 |
| v0.3 | ⏳ À venir | — | — |
| v0.4 | ⏳ À venir | — | — |
| v0.5 | ⏳ À venir | — | — |
| v1.0 | ⏳ À venir | — | — |

---

## Comment lire

Chaque dossier de version contient un `README.md` avec :

1. **Objectif** de la version
2. **Fichiers créés** — liste complète avec descriptions
3. **Décisions techniques** — pourquoi tels choix
4. **Tests** — résultats et validation
5. **Livrables** — checklist de ce qui a été produit

---

*Dernière mise à jour : 2026-07-06*
