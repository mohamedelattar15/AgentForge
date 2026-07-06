# AgentForge Core — Erreurs du domaine
# Hiérarchie d'erreurs pour tout le framework.


class AgentForgeError(Exception):
    """Erreur de base pour tout le framework AgentForge."""
    pass


class PortNotImplementedError(AgentForgeError):
    """Aucun adapter trouvé pour un port donné."""
    def __init__(self, port_name: str) -> None:
        super().__init__(f"Aucun adapter implémentant le port '{port_name}' n'a été trouvé.")
        self.port_name = port_name


class AdapterNotFoundError(AgentForgeError):
    """Adapter déclaré dans la config mais pas installé."""
    def __init__(self, adapter_name: str, port_name: str) -> None:
        super().__init__(
            f"Adapter '{adapter_name}' pour le port '{port_name}' déclaré mais pas installé."
        )
        self.adapter_name = adapter_name
        self.port_name = port_name


class ConfigurationError(AgentForgeError):
    """Erreur dans le fichier de configuration."""
    def __init__(self, message: str, path: str | None = None) -> None:
        msg = f"Erreur de configuration : {message}"
        if path:
            msg += f" (fichier : {path})"
        super().__init__(msg)
        self.path = path


class LLMError(AgentForgeError):
    """Erreur lors de l'appel au LLM."""
    def __init__(self, message: str, provider: str | None = None) -> None:
        msg = f"Erreur LLM : {message}"
        if provider:
            msg += f" (provider : {provider})"
        super().__init__(msg)
        self.provider = provider


class ToolExecutionError(AgentForgeError):
    """Échec d'exécution d'un outil."""
    def __init__(self, tool_name: str, message: str) -> None:
        super().__init__(f"Erreur d'exécution de l'outil '{tool_name}' : {message}")
        self.tool_name = tool_name


class MemoryError(AgentForgeError):
    """Erreur de stockage mémoire."""
    def __init__(self, memory_type: str, message: str) -> None:
        super().__init__(f"Erreur mémoire ({memory_type}) : {message}")
        self.memory_type = memory_type


class GuardrailViolationError(AgentForgeError):
    """Violation d'une règle de guardrail."""
    def __init__(self, guardrail: str, limit: int, current: int) -> None:
        super().__init__(
            f"Guardrail '{guardrail}' violé : limite={limit}, actuel={current}"
        )
        self.guardrail = guardrail
        self.limit = limit
        self.current = current


class ContractViolationError(AgentForgeError):
    """Un adapter ne respecte pas le contrat du port."""
    def __init__(self, port_name: str, adapter_name: str, detail: str) -> None:
        super().__init__(
            f"Violation de contrat : l'adapter '{adapter_name}' "
            f"ne respecte pas le port '{port_name}' : {detail}"
        )
        self.port_name = port_name
        self.adapter_name = adapter_name
