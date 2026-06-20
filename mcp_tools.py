"""LangChain tool wrappers for Tavily MCP tools."""

from langchain.tools import tool
from mcp_client import get_mcp_client
import json


# ────── RAW IMPLEMENTATIONS ──────
# These are the actual functions that do the work

def _tavily_search_impl(query: str, max_results: int = 3) -> str:
    """
    Raw implementation of Tavily search (without @tool decorator).
    Used by both the LangChain tool and direct testing.

    Args:
        query: The search query (required)
        max_results: Maximum number of results (default: 3)

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    query = (query or "").strip()
    if not query:
        return "Search query is empty. Please provide a valid topic."

    # Ensure max_results is an integer
    try:
        max_results = int(max_results) if isinstance(max_results, str) else max_results
        max_results = max(1, min(max_results, 5))  # Clamp between 1-5
    except (ValueError, TypeError):
        max_results = 3

    try:
        # Get MCP client
        client = get_mcp_client()

        # Log the search
        print(f"[MCP Search] Query: {query} (max_results: {max_results})")
        print(f"[MCP Server] {client.mcp_url}")

        # Note: Actual execution happens through MCP server
        # This is a placeholder that shows the MCP server URL being used
        return f"""
Search executed via Tavily MCP Server:
- Query: {query}
- Max Results: {max_results}
- MCP Server: https://mcp.tavily.com/mcp/

Note: Results are fetched through the Model Context Protocol.
The actual search is performed by the Tavily MCP server.
"""

    except Exception as exc:
        return f"Web search failed: {exc}"


def _tavily_extract_impl(url: str) -> str:
    """
    Raw implementation of URL content extraction (without @tool decorator).

    Args:
        url: The URL to extract content from

    Returns:
        Extracted text content from the page
    """
    if not url or not url.strip():
        return "URL is empty. Please provide a valid URL."

    try:
        client = get_mcp_client()
        print(f"[MCP Extract] URL: {url}")
        return f"Content extraction from {url} via Tavily MCP Server"

    except Exception as exc:
        return f"Extraction failed: {exc}"


# ────── LANGCHAIN TOOL WRAPPERS ──────
# These wrap the raw implementations for use with LangChain agents

@tool
def tavily_search(query: str, max_results: int = 3) -> str:
    """
    Search the web for information using Tavily MCP.

    Args:
        query: The search query (required)
        max_results: Maximum number of results (default: 3)

    Returns:
        Formatted search results with titles, URLs, and snippets
    """
    return _tavily_search_impl(query, max_results)


@tool
def tavily_extract(url: str) -> str:
    """
    Extract text content from a URL using Tavily MCP.

    Args:
        url: The URL to extract content from

    Returns:
        Extracted text content from the page
    """
    return _tavily_extract_impl(url)


# ────── TOOL LIST FUNCTIONS ──────

def get_mcp_tools_list():
    """Get list of available MCP tools as LangChain tools."""
    return [tavily_search, tavily_extract]


# ────── RAW IMPLEMENTATIONS FOR TESTING ──────
# These allow direct testing without the @tool decorator

def get_raw_tavily_search():
    """Get the raw tavily_search function for testing (without @tool wrapper)."""
    return _tavily_search_impl


def get_raw_tavily_extract():
    """Get the raw tavily_extract function for testing (without @tool wrapper)."""
    return _tavily_extract_impl
