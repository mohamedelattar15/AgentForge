# AgentForge — Adapters par défaut
# Implémentations embarquées "passe-partout" pour les ports sans adapter dédié.

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ...agentforge_core.ports.procedural_memory_port import ProceduralMemoryPort
from ...agentforge_core.ports.tool_registry_port import ToolRegistryPort
from ...agentforge_core.ports.trace_port import TracePort
from ...agentforge_core.ports.eval_port import EvalPort
from ...agentforge_core.ports.analytics_port import AnalyticsPort
from ...agentforge_core.types import EvalResult, Span, ToolResult


class DefaultProceduralMemory(ProceduralMemoryPort):
    """Mémoire procédurale par défaut — charge des fichiers .md depuis un dossier."""

    def __init__(self, skills_path: str = "./skills") -> None:
        """Initialise avec le chemin vers le dossier des compétences.

        Args:
            skills_path: Chemin vers le dossier contenant les fichiers .md.
        """
        self._skills_path = Path(skills_path)
        self._skills_path.mkdir(parents=True, exist_ok=True)

    async def load(self, skill_name: str) -> str:
        """Charge le contenu d'une compétence.

        Args:
            skill_name: Nom de la compétence (sans extension).

        Returns:
            str: Contenu textuel du fichier .md correspondant.
        """
        filepath = self._skills_path / f"{skill_name}.md"
        if filepath.exists():
            return filepath.read_text(encoding="utf-8")
        return f"Compétence '{skill_name}' non trouvée."

    async def list_skills(self) -> list[str]:
        """Liste les compétences disponibles.

        Returns:
            list[str]: Noms des fichiers .md sans extension.
        """
        return [f.stem for f in self._skills_path.glob("*.md")]


class DefaultToolRegistry(ToolRegistryPort):
    """Registre d'outils par défaut — aucun outil pré-installé."""

    def __init__(self) -> None:
        """Initialise un registre vide."""
        self._tools: list[dict] = []

    async def list_tools(self) -> list[dict]:
        """Liste les outils disponibles.

        Returns:
            list[dict]: Liste vide par défaut.
        """
        return self._tools

    async def execute(self, name: str, args: dict) -> ToolResult:
        """Exécute un outil (toujours en échec par défaut).

        Args:
            name: Nom de l'outil.
            args: Arguments d'appel.

        Returns:
            ToolResult: Résultat d'échec (aucun outil par défaut).
        """
        return ToolResult(
            tool_call_id="",
            content=f"Outil '{name}' non disponible : aucun outil par défaut.",
            success=False,
        )


class DefaultTrace(TracePort):
    """Trace par défaut — écrit dans un fichier JSON local."""

    def __init__(self, output_path: str = "./traces") -> None:
        """Initialise le dossier de sortie des traces.

        Args:
            output_path: Chemin du dossier où écrire les traces.
        """
        self._output_path = Path(output_path)
        self._output_path.mkdir(parents=True, exist_ok=True)

    async def record(self, run_id: str, spans: list[Span]) -> None:
        """Enregistre une trace dans un fichier JSON.

        Args:
            run_id: Identifiant du run.
            spans: Liste des spans à enregistrer.
        """
        trace_data = {
            "run_id": run_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "spans": [
                {
                    "name": s.name,
                    "start_time": s.start_time.isoformat(),
                    "end_time": s.end_time.isoformat(),
                    "attributes": s.attributes,
                }
                for s in spans
            ],
        }
        filepath = self._output_path / f"trace-{run_id}.json"
        filepath.write_text(json.dumps(trace_data, indent=2), encoding="utf-8")


class DefaultEval(EvalPort):
    """Évaluation par défaut — toujours 'passed' (score=1.0)."""

    async def evaluate(self, run_trace: dict) -> EvalResult:
        """Évalue la qualité d'un run (toujours parfait par défaut).

        Args:
            run_trace: Trace complète du run.

        Returns:
            EvalResult: Score parfait (1.0, passed).
        """
        return EvalResult(
            score=1.0,
            verdict="passed",
            diagnosis="Évaluation par défaut : toujours réussie.",
            passed=True,
        )


class DefaultAnalytics(AnalyticsPort):
    """Analytique par défaut — désactivé (no-op)."""

    async def ingest(self, metrics: dict) -> None:
        """Ignore les métriques (no-op).

        Args:
            metrics: Métriques à ingérer (ignorées).
        """
        pass

    async def query(self, filters: dict) -> list[dict]:
        """Retourne une liste vide (no-op).

        Args:
            filters: Filtres de recherche (ignorés).

        Returns:
            list[dict]: Liste vide.
        """
        return []
