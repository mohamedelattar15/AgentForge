#!/usr/bin/env python
"""
AgentForge — Example: Minimal Agent
Agent conversationnel minimal avec zéro dépendance externe.
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire racine au path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentforge_core.config.loader import ConfigLoader
from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.registry.adapter_registry import AdapterRegistry
from agentforge_core.types import Message


async def main():
    """Point d'entrée de l'exemple minimal."""
    config_path = Path(__file__).parent / "config.yaml"

    print("🔧 AgentForge - Minimal Agent")
    print("=" * 40)

    # Charger la configuration
    config = ConfigLoader.load(str(config_path))
    print(f"🤖 Agent initialisé avec la recette : {config_path.name}")

    # Initialiser le registre et résoudre les adapters
    registry = AdapterRegistry()
    registry.resolve(config)

    print("💬 Tapez 'quit' pour quitter\n")

    # Boucle interactive
    while True:
        try:
            user_input = input("Vous: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Au revoir !")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("👋 Au revoir !")
            break

        if not user_input:
            continue

        # Créer le contexte du run
        context = RunContext(user_query=user_input)

        # Simulation d'une réponse (pas de vrai LLM en mode minimal)
        response = Message(
            role="assistant",
            content=f"Réponse à : {user_input[:200]}",
        )
        context.add_message(response)

        print(f"Agent: {response.content}")

    return 0


if __name__ == "__main__":
    asyncio.run(main())
