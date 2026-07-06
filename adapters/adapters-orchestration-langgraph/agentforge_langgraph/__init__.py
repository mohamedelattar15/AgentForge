# AgentForge — Adapter Orchestration LangGraph
# Implémente OrchestrationPort via LangGraph (graphe d'état).

from typing import Any, Literal

from agentforge_core.lifecycle.run_context import RunContext
from agentforge_core.loop.executor import Executor
from agentforge_core.loop.planner import Planner
from agentforge_core.loop.reflector import Reflector
from agentforge_core.loop.verifier import Verifier
from agentforge_core.ports.orchestration_port import OrchestrationPort
from agentforge_core.types import Message, ToolResult

try:
    from langgraph.graph import StateGraph, END
    from langgraph.checkpoint.memory import MemorySaver
    from typing_extensions import TypedDict
except ImportError:
    StateGraph = None  # type: ignore
    END = None
    MemorySaver = None
    TypedDict = None


class AgentState(TypedDict):
    """État du graphe LangGraph pour l'agent."""
    messages: list[dict]
    steps: list[str]
    current_step: int
    step_results: list[str]
    final_response: str
    retry_count: int
    max_retries: int


class LangGraphOrchestrator(OrchestrationPort):
    """Orchestrateur basé sur LangGraph.

    Construit un graphe avec les noeuds Planner → Executor → Reflector → Verifier,
    avec des arêtes conditionnelles pour les boucles de correction.
    """

    def __init__(
        self,
        planner: Planner | None = None,
        executor: Executor | None = None,
        reflector: Reflector | None = None,
        verifier: Verifier | None = None,
        max_retries: int = 3,
        checkpoint: bool = False,
    ) -> None:
        """Initialise l'orchestrateur LangGraph.

        Args:
            planner: Planificateur.
            executor: Exécuteur.
            reflector: Réflecteur.
            verifier: Vérificateur.
            max_retries: Nombre max de tentatives de vérification.
            checkpoint: Activer le checkpointing (reprise sur erreur).
        """
        if StateGraph is None:
            raise ImportError("langgraph est requis. Installez : pip install langgraph")

        self._planner = planner
        self._executor = executor
        self._reflector = reflector
        self._verifier = verifier
        self._max_retries = max_retries
        self._checkpoint = checkpoint
        self._graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Construit le graphe LangGraph.

        Noeuds : planner, executor, reflector, verifier
        Arêtes : planner → executor → reflector → verifier → END ou executor

        Returns:
            StateGraph: Graphe compilé.
        """
        workflow = StateGraph(AgentState)

        workflow.add_node("planner", self._node_planner)
        workflow.add_node("executor", self._node_executor)
        workflow.add_node("reflector", self._node_reflector)
        workflow.add_node("verifier", self._node_verifier)

        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "executor")
        workflow.add_edge("executor", "reflector")
        workflow.add_conditional_edges(
            "reflector",
            self._route_after_reflector,
            {"executor": "executor", "verifier": "verifier"},
        )
        workflow.add_conditional_edges(
            "verifier",
            self._route_after_verifier,
            {"executor": "executor", END: END},
        )

        if self._checkpoint:
            checkpointer = MemorySaver()
            return workflow.compile(checkpointer=checkpointer)
        return workflow.compile()

    async def _node_planner(self, state: AgentState) -> dict:
        """Noeud planificateur."""
        if self._planner:
            context = RunContext(user_query=state["messages"][-1]["content"] if state["messages"] else "")
            steps = await self._planner.plan(context)
        else:
            steps = ["répondre"]
        return {"steps": steps, "current_step": 0}

    async def _node_executor(self, state: AgentState) -> dict:
        """Noeud exécuteur."""
        step_idx = state["current_step"]
        steps = state["steps"]

        if step_idx >= len(steps):
            return {"final_response": "Toutes les étapes sont terminées."}

        step = steps[step_idx]
        context = RunContext(user_query=state["messages"][-1]["content"] if state["messages"] else "")

        if self._executor:
            result = await self._executor.execute(context, step)
            content = result.content if hasattr(result, "content") else str(result)
        else:
            content = f"Étape '{step}' exécutée par défaut."

        return {
            "current_step": step_idx + 1,
            "step_results": state.get("step_results", []) + [content],
        }

    async def _node_reflector(self, state: AgentState) -> dict:
        """Noeud réflecteur."""
        last_result = state["step_results"][-1] if state["step_results"] else ""

        if self._reflector:
            result = ToolResult(tool_call_id="reflect", content=last_result, success=True)
            correction = await self._reflector.reflect(RunContext(), result)
            if correction:
                return {"step_results": state["step_results"] + [f"Correction: {correction}"]}

        return {}

    async def _node_verifier(self, state: AgentState) -> dict:
        """Noeud vérificateur."""
        response = state.get("final_response", state["step_results"][-1] if state["step_results"] else "")
        msg = Message(role="assistant", content=response)

        if self._verifier:
            is_valid = await self._verifier.verify(RunContext(), msg)
            if not is_valid:
                return {"retry_count": state.get("retry_count", 0) + 1}

        return {}

    def _route_after_reflector(self, state: AgentState) -> Literal["executor", "verifier"]:
        """Route après réflexion : si toutes les étapes sont faites → verifier, sinon → executor."""
        if state["current_step"] >= len(state["steps"]):
            return "verifier"
        return "executor"

    def _route_after_verifier(self, state: AgentState) -> Literal["executor", END]:
        """Route après vérification : si échec et retries < max → executor, sinon → END."""
        if state.get("retry_count", 0) < self._max_retries and not state.get("final_response"):
            return "executor"
        return END

    async def run(self, context: RunContext) -> Message:
        """Exécute la boucle via le graphe LangGraph.

        Args:
            context: Contexte du run.

        Returns:
            Message: Réponse finale.
        """
        initial_state: AgentState = {
            "messages": [{"role": m.role, "content": m.content} for m in context.messages],
            "steps": [],
            "current_step": 0,
            "step_results": [],
            "final_response": "",
            "retry_count": 0,
            "max_retries": self._max_retries,
        }

        config = {"recursion_limit": 100}
        if self._checkpoint:
            config["thread_id"] = context.run_id

        result = await self._graph.ainvoke(initial_state, config)

        final = result.get("final_response") or (result["step_results"][-1] if result.get("step_results") else "")
        return Message(role="assistant", content=final)

    async def should_stop(self, state: dict) -> bool:
        """Vérifie si la boucle doit s'arrêter."""
        return state.get("retry_count", 0) >= self._max_retries
