# AgentForge — Adapter Tools MCP
# Implémente ToolRegistryPort via le Model Context Protocol.

import json
from typing import Any

from agentforge_core.ports.tool_registry_port import ToolRegistryPort
from agentforge_core.types import ToolResult

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
except ImportError:
    ClientSession = None  # type: ignore
    StdioServerParameters = None
    stdio_client = None


class MCPToolRegistry(ToolRegistryPort):
    """Registre d'outils via MCP (Model Context Protocol).

    Se connecte à des serveurs MCP via stdio ou SSE,
    découvre les outils disponibles et les exécute.
    """

    def __init__(
        self,
        servers: list[dict] | None = None,
    ) -> None:
        """Initialise le registre MCP.

        Args:
            servers: Liste de configurations de serveurs MCP.
                Chaque serveur : {"command": str, "args": list[str], "url": str}
        """
        if ClientSession is None:
            raise ImportError("mcp est requis. Installez : pip install mcp")

        self._servers = servers or []
        self._sessions: list[Any] = []
        self._tools_cache: list[dict] | None = None

    async def _connect_servers(self) -> None:
        """Connecte tous les serveurs MCP configurés."""
        for server in self._servers:
            command = server.get("command")
            args = server.get("args", [])

            if command:
                params = StdioServerParameters(command=command, args=args)
                stdio_transport = await stdio_client(params)
                read, write = stdio_transport
                session = ClientSession(read, write)
                await session.initialize()
                self._sessions.append(session)

    async def list_tools(self) -> list[dict]:
        """Liste tous les outils disponibles depuis tous les serveurs MCP.

        Returns:
            list[dict]: Schémas d'outils au format OpenAI tool calling.
        """
        if self._tools_cache is not None:
            return self._tools_cache

        if not self._sessions:
            await self._connect_servers()

        tools: list[dict] = []
        for session in self._sessions:
            result = await session.list_tools()
            for tool in result.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema or {"type": "object", "properties": {}},
                    },
                })

        self._tools_cache = tools
        return tools

    async def execute(self, name: str, args: dict) -> ToolResult:
        """Exécute un outil via MCP.

        Args:
            name: Nom de l'outil.
            args: Arguments d'appel.

        Returns:
            ToolResult: Résultat de l'exécution.
        """
        if not self._sessions:
            await self._connect_servers()

        for session in self._sessions:
            try:
                result = await session.call_tool(name, args)
                content = result.content[0].text if result.content else ""
                return ToolResult(
                    tool_call_id=name,
                    content=content,
                    success=not result.isError,
                )
            except Exception:
                continue

        return ToolResult(
            tool_call_id=name,
            content=f"Outil '{name}' introuvable sur aucun serveur MCP.",
            success=False,
        )
