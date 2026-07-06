# AgentForge — Tests MCP Tools

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agentforge_core.types import ToolResult
from agentforge_mcp import MCPToolRegistry


class TestMCPToolRegistry:
    """Tests pour MCPToolRegistry (mocké)."""

    @pytest.fixture
    def adapter(self):
        """Fixture retournant un registre MCP avec serveur factice."""
        return MCPToolRegistry(servers=[{"command": "echo", "args": ["test"]}])

    @pytest.mark.asyncio
    async def test_list_tools_empty_servers(self):
        """list_tools() sans serveur doit retourner []."""
        adapter = MCPToolRegistry(servers=[])
        tools = await adapter.list_tools()
        assert tools == []

    @pytest.mark.asyncio
    async def test_execute_no_servers(self):
        """execute() sans serveur connecté doit retourner un échec."""
        adapter = MCPToolRegistry(servers=[])
        result = await adapter.execute("test_tool", {})
        assert result.success is False

    @pytest.mark.asyncio
    async def test_execute_with_mock_session(self, adapter):
        """execute() avec session mockée doit retourner un résultat."""
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.content = [MagicMock(text="Résultat du test")]
        mock_result.isError = False
        mock_session.call_tool = AsyncMock(return_value=mock_result)

        adapter._sessions = [mock_session]
        result = await adapter.execute("test_tool", {"arg": "val"})

        assert result.success is True
        assert result.content == "Résultat du test"

    @pytest.mark.asyncio
    async def test_list_tools_with_mock(self, adapter):
        """list_tools() avec session mockée doit retourner les outils."""
        mock_session = AsyncMock()
        mock_tool = MagicMock()
        mock_tool.name = "get_weather"
        mock_tool.description = "Outil météo"
        mock_tool.inputSchema = {"type": "object", "properties": {"city": {"type": "string"}}}
        mock_session.list_tools = AsyncMock(return_value=MagicMock(tools=[mock_tool]))

        adapter._sessions = [mock_session]
        adapter._tools_cache = None
        tools = await adapter.list_tools()

        assert len(tools) == 1
        assert tools[0]["function"]["name"] == "get_weather"

    @pytest.mark.asyncio
    async def test_cache_works(self, adapter):
        """list_tools() doit utiliser le cache après le premier appel."""
        mock_session = AsyncMock()
        adapter._sessions = [mock_session]
        adapter._tools_cache = [{"type": "function", "function": {"name": "cached_tool"}}]

        tools = await adapter.list_tools()
        assert tools[0]["function"]["name"] == "cached_tool"
        mock_session.list_tools.assert_not_called()
