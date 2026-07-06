#!/usr/bin/env python
"""
AgentForge — Example: Support Agent with MCP Tools
Agent de support client avec outils MCP.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from agentforge_core.config.loader import ConfigLoader
from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.lifecycle.hydrate_context import ContextHydrator
from agentforge_core.lifecycle.loop_controller import LoopController
from agentforge_core.registry.adapter_registry import AdapterRegistry
from agentforge_core.types import Message


async def main():
    """Point d'entrée de l'exemple support."""
    config_path = Path(__file__).parent / "config.yaml"
    skills_dir = Path(__file__).parent / "skills"
    skills_dir.mkdir(exist_ok=True)

    print("🎧 AgentForge - Support Agent (MCP Tools)")
    print("=" * 50)

    # Charger la configuration
    config = ConfigLoader.load(str(config_path))
    registry = AdapterRegistry()
    registry.resolve(config)

    # Récupérer les adapters
    hydrator = ContextHydrator(
        semantic_memory=registry.get("semantic_memory"),
        episodic_memory=registry.get("episodic_memory"),
        procedural_memory=registry.get("procedural_memory"),
    )
    controller = LoopController(
        orchestration=registry.get("orchestration"),
    )

    print(f"🤖 Agent de support prêt")
    print(f"📋 Compétences chargées depuis : {skills_dir}")
    print("💬 Tapez 'quit' pour quitter\n")

    session_id = "support-session-1"

    while True:
        try:
            user_input = input("Client: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Merci d'avoir contacté le support !")
            break

        if user_input.lower() in ("quit", "exit", "q"):
            print("👋 Merci d'avoir contacté le support !")
            break

        if not user_input:
            continue

        # Créer et exécuter le run
        context = RunContext(
            user_query=user_input,
            session_id=session_id,
        )

        # Phase 1 : Hydratation
        await hydrator.hydrate(context)

        # Phase 2 : Boucle d'exécution
        response = await controller.execute(context)

        print(f"Support: {response.content}")

        # Sauvegarder le contexte de session
        context.add_message(Message(role="user", content=user_input))
        context.add_message(response)

    return 0


if __name__ == "__main__":
    asyncio.run(main())
