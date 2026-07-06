# AgentForge — Workflow Temporal pour l'agent
# Définition du workflow principal.

from temporalio import workflow


@workflow.defn
class AgentWorkflow:
    """Workflow Temporal pour l'exécution d'un run agent."""

    @workflow.run
    async def run(self, payload: dict) -> dict:
        """Exécute le workflow complet.

        Args:
            payload: Données du run (run_id, user_query, messages).

        Returns:
            dict: Résultat du workflow.
        """
        user_query = payload.get("user_query", "")
        messages = payload.get("messages", [])

        # Phase 1 : Planification
        steps = await workflow.execute_activity(
            "plan-activity",
            user_query,
            start_to_close_timeout=30,
        )

        # Phase 2 : Exécution séquentielle
        results = []
        for step in steps:
            result = await workflow.execute_activity(
                "execute-activity",
                {"step": step, "messages": messages},
                start_to_close_timeout=120,
            )
            results.append(result)

        # Phase 3 : Construction de la réponse
        response = "\n".join(results) if results else "Aucune étape exécutée."

        return {
            "run_id": payload.get("run_id", ""),
            "response": response,
            "steps_completed": len(results),
        }
