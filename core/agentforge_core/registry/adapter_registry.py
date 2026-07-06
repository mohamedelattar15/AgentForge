# AgentForge Core — AdapterRegistry
# Mécanisme central de découverte et résolution des adapters.

from ..errors import AdapterNotFoundError, PortNotImplementedError
from ..types import AdapterDeclaration


class AdapterRegistry:
    """Registre central des adapters.

    Gère la déclaration, la résolution et l'instanciation des adapters
    pour chaque port du framework.
    """

    def __init__(self) -> None:
        """Initialise le registre."""
        self._declarations: dict[str, list[AdapterDeclaration]] = {}
        self._instances: dict[str, object] = {}

    def register(self, declaration: AdapterDeclaration) -> None:
        """Enregistre une déclaration d'adapter.

        Args:
            declaration: Déclaration de l'adapter à enregistrer.
        """
        port = declaration.port
        if port not in self._declarations:
            self._declarations[port] = []
        self._declarations[port].append(declaration)

    def resolve(self, config: dict) -> None:
        """Résout tous les ports selon la configuration fournie.

        Pour chaque port configuré, trouve l'adapter déclaré correspondant
        et l'instancie.

        Args:
            config: Configuration dict avec la structure {ports: {port_name: {adapter, config}}}.

        Raises:
            ConfigurationError: Si la config est invalide.
            PortNotImplementedError: Si aucun adapter trouvé pour un port requis.
            AdapterNotFoundError: Si l'adapter déclaré n'est pas enregistré.
        """
        ports_config = config.get("ports", {})

        for port_name, port_config in ports_config.items():
            adapter_name = port_config.get("adapter", "default")
            enabled = port_config.get("enabled", True)

            if not enabled:
                continue

            # Chercher la déclaration
            declarations = self._declarations.get(port_name, [])
            if not declarations:
                raise PortNotImplementedError(port_name)

            # Trouver l'adapter correspondant
            matched = [d for d in declarations if d.name == adapter_name]
            if not matched:
                raise AdapterNotFoundError(adapter_name, port_name)

            # Instancier l'adapter
            declaration = matched[0]
            instance = self._instantiate(declaration, port_config.get("config", {}))
            self._instances[port_name] = instance

    def get(self, port_name: str) -> object:
        """Retourne l'instance d'adapter pour un port.

        Args:
            port_name: Nom du port.

        Returns:
            object: Instance de l'adapter.

        Raises:
            PortNotImplementedError: Si le port n'est pas résolu.
        """
        instance = self._instances.get(port_name)
        if instance is None:
            raise PortNotImplementedError(port_name)
        return instance

    def list_ports(self) -> list[str]:
        """Liste tous les ports actuellement résolus.

        Returns:
            list[str]: Noms des ports résolus.
        """
        return list(self._instances.keys())

    def _instantiate(self, declaration: AdapterDeclaration, config: dict) -> object:
        """Instancie un adapter à partir de sa déclaration.

        Args:
            declaration: Déclaration de l'adapter.
            config: Configuration spécifique à passer à l'instance.

        Returns:
            object: Instance de l'adapter.
        """
        # Import dynamique du module et de la classe
        module_path, class_name = declaration.class_ref.rsplit(".", 1)
        import importlib

        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        return cls(**config)
