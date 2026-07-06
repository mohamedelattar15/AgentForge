# AgentForge Core — Contract Tests : ToolRegistryPort
# Tests partagés que tout adapter ToolRegistry doit passer.

from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from agentforge_core.ports.tool_registry_port import ToolRegistryPort


class ToolRegistryContractTests:
    """Tests de conformité pour tout adapter ToolRegistryPort."""

    @pytest.mark.asyncio
    async def test_list_tools_returns_list(self, adapter: "ToolRegistryPort"):
        """list_tools() doit retourner une liste."""
        tools = await adapter.list_tools()
        assert isinstance(tools, list)

    @pytest.mark.asyncio
    async def test_execute_invalid_tool(self, adapter: "ToolRegistryPort"):
        """execute() avec un outil inconnu doit retourner un échec."""
        result = await adapter.execute("tool_inconnu", {})
        assert result.success is False
