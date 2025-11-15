import os
from typing import Optional

from crewai.tools import BaseTool
from crewai_tools import MCPServerAdapter, ScrapeWebsiteTool, SerperDevTool


def get_tools() -> list[BaseTool]:
    """
    Returns a list of tools available for the marketing posts crew.
    """
    if os.getenv("MCP_SERVER_URL"):
        return _get_tools_mcp()
    return _get_tools_crewai()


def _get_tools_crewai() -> list[BaseTool]:
    return [SerperDevTool(), ScrapeWebsiteTool()]


_server: Optional[MCPServerAdapter] = None


def _get_tools_mcp() -> list[BaseTool]:
    global _server
    if _server is None:
        _server = MCPServerAdapter(dict(url=os.getenv("MCP_SERVER_URL")))
        print(f"Available MCP tools {[tool.name for tool in _server.tools]}")
    return _server.tools
