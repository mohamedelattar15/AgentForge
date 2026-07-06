# AgentForge Core — Config Loader
# Chargement et validation des fichiers de configuration YAML/JSON.

from pathlib import Path

from .schema import validate_config
from ..errors import ConfigurationError

try:
    import yaml

    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class ConfigLoader:
    """Chargeur de configuration — lit, valide et fusionne les fichiers."""

    @staticmethod
    def load(path: str) -> dict:
        """Charge et valide un fichier de configuration YAML/JSON.

        Args:
            path: Chemin vers le fichier de configuration.

        Returns:
            dict: Configuration validée.

        Raises:
            ConfigurationError: Si le fichier est introuvable, invalide ou mal formaté.
        """
        filepath = Path(path)
        if not filepath.exists():
            raise ConfigurationError(f"Fichier introuvable", path=path)

        content = filepath.read_text(encoding="utf-8")
        ext = filepath.suffix.lower()

        if ext in (".yaml", ".yml"):
            if not HAS_YAML:
                raise ConfigurationError(
                    "PyYAML n'est pas installé. Installez-le avec : pip install pyyaml",
                    path=path,
                )
            config = yaml.safe_load(content)
        elif ext == ".json":
            import json

            config = json.loads(content)
        else:
            raise ConfigurationError(
                f"Format non supporté : '{ext}'. Utilisez .yaml, .yml ou .json.",
                path=path,
            )

        if not isinstance(config, dict):
            raise ConfigurationError(
                "Le fichier de configuration doit contenir un dictionnaire racine.",
                path=path,
            )

        validate_config(config)
        return config

    @staticmethod
    def merge(base: dict, override: dict) -> dict:
        """Fusionne deux configurations (override gagne, récursif).

        Args:
            base: Configuration de base.
            override: Configuration à fusionner (prioritaire).

        Returns:
            dict: Configuration fusionnée.
        """
        result = base.copy()

        for key, value in override.items():
            if (
                key in result
                and isinstance(result[key], dict)
                and isinstance(value, dict)
            ):
                result[key] = ConfigLoader.merge(result[key], value)
            else:
                result[key] = value

        return result
