# AgentForge Core — Config Schema
# Schéma de validation pour les fichiers de configuration (recettes).

from typing import Any

from ..errors import ConfigurationError

# Schéma définissant les champs attendus et leurs types
REQUIRED_TOP_LEVEL_FIELDS = {"agent", "ports"}
REQUIRED_AGENT_FIELDS = {"name", "version"}
REQUIRED_PORT_FIELDS = {"adapter"}
VALID_PORT_NAMES = {
    "llm", "orchestration", "working_memory", "semantic_memory",
    "episodic_memory", "procedural_memory", "tool_registry",
    "event_bus", "trace", "eval", "analytics",
}
VALID_GUARDRAIL_FIELDS = {
    "max_iterations", "token_budget", "timeout_seconds",
}


def validate_config(config: dict) -> None:
    """Valide une configuration complète.

    Vérifie la structure, les champs requis et les types.

    Args:
        config: Configuration à valider.

    Raises:
        ConfigurationError: Si la configuration est invalide.
    """
    # Vérifier les champs de premier niveau
    missing = REQUIRED_TOP_LEVEL_FIELDS - set(config.keys())
    if missing:
        raise ConfigurationError(f"Champs obligatoires manquants : {missing}")

    # Valider la section agent
    agent = config["agent"]
    if not isinstance(agent, dict):
        raise ConfigurationError("La section 'agent' doit être un dictionnaire.")
    missing_agent = REQUIRED_AGENT_FIELDS - set(agent.keys())
    if missing_agent:
        raise ConfigurationError(
            f"Champs obligatoires manquants dans 'agent' : {missing_agent}"
        )

    # Valider la section ports
    ports = config["ports"]
    if not isinstance(ports, dict):
        raise ConfigurationError("La section 'ports' doit être un dictionnaire.")

    for port_name, port_config in ports.items():
        if port_name not in VALID_PORT_NAMES:
            raise ConfigurationError(f"Nom de port inconnu : '{port_name}'")

        if not isinstance(port_config, dict):
            raise ConfigurationError(
                f"La configuration du port '{port_name}' doit être un dictionnaire."
            )

        # Vérifier les champs requis du port (sauf si désactivé)
        if port_config.get("enabled", True):
            missing_port = REQUIRED_PORT_FIELDS - set(port_config.keys())
            if missing_port:
                raise ConfigurationError(
                    f"Champs obligatoires manquants pour le port "
                    f"'{port_name}' : {missing_port}"
                )

    # Valider la section guardrails (optionnelle)
    guardrails = config.get("guardrails", {})
    if not isinstance(guardrails, dict):
        raise ConfigurationError("La section 'guardrails' doit être un dictionnaire.")

    for field in guardrails:
        if field not in VALID_GUARDRAIL_FIELDS:
            raise ConfigurationError(f"Champ guardrail inconnu : '{field}'")


def validate_port_config(port_name: str, config: dict) -> None:
    """Valide la configuration d'un port spécifique.

    Args:
        port_name: Nom du port.
        config: Configuration du port.

    Raises:
        ConfigurationError: Si la configuration est invalide.
    """
    if port_name not in VALID_PORT_NAMES:
        raise ConfigurationError(f"Nom de port inconnu : '{port_name}'")
    if not isinstance(config, dict):
        raise ConfigurationError(
            f"La configuration du port '{port_name}' doit être un dictionnaire."
        )
