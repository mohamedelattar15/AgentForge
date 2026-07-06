# AgentForge Core — Tests de configuration

import json
import tempfile
from pathlib import Path

import pytest

from agentforge_core.config.loader import ConfigLoader
from agentforge_core.config.schema import validate_config
from agentforge_core.errors import ConfigurationError


class TestConfigSchema:
    """Tests pour la validation du schéma de configuration."""

    def test_valid_minimal_config(self):
        """Une configuration minimale valide doit passer la validation."""
        config = {
            "agent": {"name": "test-agent", "version": "0.1.0"},
            "ports": {
                "llm": {"adapter": "minimal", "config": {}},
                "orchestration": {"adapter": "minimal", "config": {}},
            },
        }
        validate_config(config)  # ne doit pas lever d'exception

    def test_missing_agent_field(self):
        """Une config sans 'agent' doit lever ConfigurationError."""
        config = {"ports": {}}
        with pytest.raises(ConfigurationError, match="agent"):
            validate_config(config)

    def test_missing_ports_field(self):
        """Une config sans 'ports' doit lever ConfigurationError."""
        config = {"agent": {"name": "test", "version": "0.1.0"}}
        with pytest.raises(ConfigurationError, match="ports"):
            validate_config(config)

    def test_invalid_port_name(self):
        """Un nom de port inconnu doit lever ConfigurationError."""
        config = {
            "agent": {"name": "test", "version": "0.1.0"},
            "ports": {"invalid_port": {"adapter": "test"}},
        }
        with pytest.raises(ConfigurationError, match="inconnu"):
            validate_config(config)

    def test_port_without_adapter(self):
        """Un port sans champ 'adapter' doit lever ConfigurationError."""
        config = {
            "agent": {"name": "test", "version": "0.1.0"},
            "ports": {"llm": {"config": {}}},
        }
        with pytest.raises(ConfigurationError, match="adapter"):
            validate_config(config)

    def test_disabled_port_without_adapter(self):
        """Un port désactivé n'a pas besoin de champ 'adapter'."""
        config = {
            "agent": {"name": "test", "version": "0.1.0"},
            "ports": {
                "llm": {"adapter": "test", "config": {}},
                "analytics": {"enabled": False},
            },
        }
        validate_config(config)  # ne doit pas lever d'exception


class TestConfigLoader:
    """Tests pour le chargement des fichiers de configuration."""

    def test_load_valid_yaml(self):
        """Charger un fichier YAML valide doit retourner un dict."""
        yaml_content = """
agent:
  name: test-agent
  version: "0.1.0"
ports:
  llm:
    adapter: minimal
    config: {}
"""
        with tempfile.NamedTemporaryFile(
            suffix=".yaml", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(yaml_content)
            tmp_path = f.name

        try:
            config = ConfigLoader.load(tmp_path)
            assert config["agent"]["name"] == "test-agent"
            assert config["ports"]["llm"]["adapter"] == "minimal"
        finally:
            Path(tmp_path).unlink()

    def test_load_valid_json(self):
        """Charger un fichier JSON valide doit retourner un dict."""
        json_content = json.dumps({
            "agent": {"name": "test-agent", "version": "0.1.0"},
            "ports": {"llm": {"adapter": "minimal", "config": {}}},
        })
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write(json_content)
            tmp_path = f.name

        try:
            config = ConfigLoader.load(tmp_path)
            assert config["agent"]["name"] == "test-agent"
        finally:
            Path(tmp_path).unlink()

    def test_load_file_not_found(self):
        """Charger un fichier inexistant doit lever ConfigurationError."""
        with pytest.raises(ConfigurationError, match="introuvable"):
            ConfigLoader.load("/chemin/inexistant.yaml")

    def test_load_invalid_extension(self):
        """Charger un fichier avec extension non supportée doit lever une erreur."""
        with tempfile.NamedTemporaryFile(
            suffix=".toml", mode="w", delete=False, encoding="utf-8"
        ) as f:
            f.write("[tool]\nkey = 'value'")
            tmp_path = f.name

        try:
            with pytest.raises(ConfigurationError, match="supporté"):
                ConfigLoader.load(tmp_path)
        finally:
            Path(tmp_path).unlink()

    def test_merge_configs(self):
        """La fusion de deux configurations doit fonctionner récursivement."""
        base = {
            "agent": {"name": "base-agent", "version": "0.1.0"},
            "ports": {"llm": {"adapter": "minimal", "config": {"model": "default"}}},
        }
        override = {
            "ports": {"llm": {"config": {"model": "gpt-4"}}},
        }
        merged = ConfigLoader.merge(base, override)
        assert merged["agent"]["name"] == "base-agent"
        assert merged["ports"]["llm"]["adapter"] == "minimal"
        assert merged["ports"]["llm"]["config"]["model"] == "gpt-4"
