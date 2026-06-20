"""MCP client for Tavily search integration."""

import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()


class TavilyMCPClient:
    """Client to interact with Tavily MCP server for web search."""

    def __init__(self):
        """Initialize Tavily MCP client with API key."""
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "Missing TAVILY_API_KEY. Add it to your .env file to use Tavily MCP."
            )
        self.mcp_url = f"https://mcp.tavily.com/mcp/?tavilyApiKey={self.api_key}"
        self.tools = []

    def get_mcp_server_config(self) -> dict[str, Any]:
        """
        Get MCP server configuration for connecting to Tavily MCP server.

        Returns dict compatible with mcp.ClientSession or langchain MCP integration.
        """
        return {
            "type": "http",
            "url": self.mcp_url,
            "transport": "http",
        }

    async def discover_tools(self) -> list[dict]:
        """
        Discover available tools from Tavily MCP server.

        Returns list of available tool definitions including:
        - tavily_search: Web search with 2-3 results
        - tavily_extract: Extract content from URLs
        - tavily_map: Map website structure
        - tavily_crawl: Crawl websites
        """
        # In a real implementation, this would connect to the MCP server
        # and discover tools dynamically. For now, we return the known tools.
        self.tools = [
            {
                "name": "tavily_search",
                "description": "Search the web for information using Tavily. Returns titles, URLs, and snippets (max 3 results).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results (default: 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "tavily_extract",
                "description": "Extract text content from a URL.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to extract content from"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "tavily_map",
                "description": "Map the structure of a website.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL of the website to map"
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "tavily_crawl",
                "description": "Crawl and explore a website systematically.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to start crawling from"
                        },
                        "max_depth": {
                            "type": "integer",
                            "description": "Maximum crawl depth (default: 2)",
                            "default": 2
                        }
                    },
                    "required": ["url"]
                }
            }
        ]
        return self.tools

    def get_tools_for_agent(self) -> list[dict]:
        """Get tools formatted for LangChain agent integration."""
        return self.tools if self.tools else []


# Initialize the client (lazy loaded)
_mcp_client = None


def get_mcp_client() -> TavilyMCPClient:
    """Get or create MCP client instance."""
    global _mcp_client
    if _mcp_client is None:
        _mcp_client = TavilyMCPClient()
    return _mcp_client


async def get_mcp_tools_for_researcher():
    """
    Get MCP tools for the Researcher Agent.

    Returns list of LangChain-compatible tool objects.
    """
    client = get_mcp_client()
    tools = await client.discover_tools()
    # Filter to search tool only for researcher
    return [t for t in tools if t["name"] == "tavily_search"]
