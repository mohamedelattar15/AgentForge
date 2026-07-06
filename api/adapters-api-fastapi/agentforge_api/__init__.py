# AgentForge — API FastAPI
# Point d'entrée principal — charge la config, initialise le registre, monte les routes.

from fastapi import FastAPI

from agentforge_core.config.loader import ConfigLoader
from agentforge_core.registry.adapter_registry import AdapterRegistry

from .routes.chat_completions import router as chat_router
from .routes.health import router as health_router


class AgentForgeAPI:
    """Application FastAPI principale d'AgentForge.

    Charge la configuration, résout les adapters via le registre,
    et expose une API compatible OpenAI.
    """

    def __init__(self, config_path: str) -> None:
        """Initialise l'application.

        Args:
            config_path: Chemin vers le fichier de configuration YAML.
        """
        self.config_path = config_path
        self.config = ConfigLoader.load(config_path)
        self.registry = AdapterRegistry()

        # Résoudre les adapters
        self.registry.resolve(self.config)

        # Créer l'application FastAPI
        self.app = FastAPI(
            title="AgentForge API",
            version=self.config.get("agent", {}).get("version", "0.2.0"),
            description="API compatible OpenAI pour AgentForge",
        )
        self._setup_routes()

    def _setup_routes(self) -> None:
        """Monte les routeurs sur l'application."""
        self.app.include_router(health_router)
        self.app.include_router(chat_router)

    def run(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """Lance le serveur HTTP.

        Args:
            host: Adresse d'écoute.
            port: Port d'écoute.
        """
        import uvicorn
        uvicorn.run(self.app, host=host, port=port)


# Point d'entrée direct : python -m agentforge_api.main
if __name__ == "__main__":
    import sys

    config_path = sys.argv[1] if len(sys.argv) > 1 else "recipes/recipe-startup.yaml"
    api = AgentForgeAPI(config_path)
    api.run()
