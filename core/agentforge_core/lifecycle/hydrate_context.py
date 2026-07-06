# AgentForge Core — ContextHydrator
# Phase 1 : Hydratation du contexte — assemble la Working Memory.

from ..ports.procedural_memory_port import ProceduralMemoryPort
from ..ports.semantic_memory_port import SemanticMemoryPort
from ..ports.episodic_memory_port import EpisodicMemoryPort
from .run_context import RunContext


class ContextHydrator:
    """Hydrate le contexte du run en interrogeant les 3 mémoires."""

    def __init__(
        self,
        semantic_memory: SemanticMemoryPort,
        episodic_memory: EpisodicMemoryPort,
        procedural_memory: ProceduralMemoryPort,
    ) -> None:
        """Initialise l'hydrateur avec les 3 ports mémoire.

        Args:
            semantic_memory: Port de mémoire sémantique.
            episodic_memory: Port de mémoire épisodique.
            procedural_memory: Port de mémoire procédurale.
        """
        self._semantic = semantic_memory
        self._episodic = episodic_memory
        self._procedural = procedural_memory

    async def hydrate(self, context: RunContext) -> None:
        """Hydrate le contexte en assemblant la Working Memory.

        1. Charge l'historique épisodique de la session.
        2. Recherche les faits sémantiques pertinents.
        3. Charge les compétences procédurales actives.
        4. Assemble le tout dans context.working_memory.

        Args:
            context: Contexte du run à hydrater.
        """
        context.status = RunStatus.HYDRATING  # noqa: F821

        # 1. Historique épisodique
        history: list = []
        if context.session_id:
            history = await self._episodic.get_history(context.session_id)
        context.working_memory["conversation_history"] = history

        # 2. Faits sémantiques
        semantic_facts = await self._semantic.search(context.user_query)
        context.working_memory["semantic_facts"] = semantic_facts

        # 3. Compétences procédurales
        skills = await self._procedural.list_skills()
        skills_content = {}
        for skill in skills:
            skills_content[skill] = await self._procedural.load(skill)
        context.working_memory["skills"] = skills_content

        # 4. Assemblage du prompt système enrichi
        system_parts = ["Tu es un assistant IA utile et précis."]
        if skills_content:
            system_parts.append(
                "\nCompétences disponibles :\n" +
                "\n---\n".join(
                    f"## {name}\n{content}"
                    for name, content in skills_content.items()
                )
            )
        if semantic_facts:
            facts_text = "\n".join(
                f"- {f.get('content', f)}" for f in semantic_facts
            )
            system_parts.append(f"\nFaits connus sur l'utilisateur :\n{facts_text}")

        context.working_memory["system_prompt"] = "\n\n".join(system_parts)
