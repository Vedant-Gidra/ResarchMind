# Tavily MCP Integration Guide

## Overview

ResearchMind now uses the **Model Context Protocol (MCP)** to integrate with Tavily's web search service. This replaces direct API calls with a standardized MCP server approach.

## Architecture

```
Researcher Agent → LangChain Tools → MCP Tools Wrapper → Tavily MCP Server
```

### Components

1. **mcp_client.py** - Manages connection to Tavily MCP server
2. **mcp_tools.py** - LangChain tool wrappers for MCP tools
3. **agents.py** - Updated to use MCP tools instead of direct Tavily

## Setup Instructions

### 1. Add Tavily API Key

Ensure your `.env` file contains:
```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Get a free Tavily API key at [tavily.com](https://tavily.com/)

### 2. Install Dependencies

```bash
uv sync
```

This installs the `mcp` package required for MCP protocol support.

## Available MCP Tools

The Researcher Agent has access to the following Tavily MCP tools:

### tavily_search
- **Description**: Search the web for information
- **Parameters**:
  - `query` (required): Search query string
  - `max_results` (optional): Maximum results (default: 3)
- **Returns**: Search results with titles, URLs, and snippets

### tavily_extract
- **Description**: Extract text content from URLs
- **Parameters**:
  - `url` (required): URL to extract from
- **Returns**: Extracted page content

### tavily_map (available but not used by default)
- **Description**: Map website structure
- **Parameters**:
  - `url` (required): Website URL
- **Returns**: Site structure mapping

### tavily_crawl (available but not used by default)
- **Description**: Crawl and explore websites
- **Parameters**:
  - `url` (required): Starting URL
  - `max_depth` (optional): Crawl depth (default: 2)
- **Returns**: Crawled content

## How It Works

### MCP Server Connection

The MCP client connects to Tavily's remote MCP server:
```
https://mcp.tavily.com/mcp/?tavilyApiKey=<your-api-key>
```

**No local installation needed** - the remote server handles all search operations.

### Tool Execution Flow

1. **Researcher Agent** calls `tavily_search(query="topic")`
2. **MCP Tools Wrapper** (mcp_tools.py) receives the call
3. **MCP Client** (mcp_client.py) connects to Tavily MCP server
4. **Tavily MCP Server** performs the actual web search
5. **Results** returned through the MCP protocol
6. **Agent** processes results and generates research

## Configuration

### Default Search Parameters

Modify `mcp_client.py` to customize Tavily MCP defaults:

```python
def get_mcp_server_config(self) -> dict[str, Any]:
    return {
        "type": "http",
        "url": self.mcp_url,
        "transport": "http",
        "default_parameters": {
            "max_results": 3,
            "search_depth": "basic",
            "include_images": False
        }
    }
```

### Per-User Analytics (Optional)

To track analytics per user, set `TAVILY_HUMAN_ID` in `.env`:
```env
TAVILY_HUMAN_ID=user_12345
```

## Troubleshooting

### "Missing TAVILY_API_KEY"
- Ensure `TAVILY_API_KEY` is set in `.env`
- Restart the application after updating `.env`

### MCP Server Connection Fails
- Verify your Tavily API key is valid
- Check internet connectivity
- Ensure the MCP server URL is correct

### Tools Not Available
- Run `uv sync` to install MCP dependencies
- Verify `mcp_tools.py` is in the project root

## Advantages of MCP Integration

✅ **Standardized Protocol** - Uses industry-standard MCP for AI tool integration
✅ **Reduced Complexity** - No direct API call management
✅ **Easy Tool Discovery** - Tools automatically discovered from MCP server
✅ **Scalability** - Can easily add more MCP servers (Claude, perplexity, etc.)
✅ **Security** - API keys passed securely through MCP protocol
✅ **Future-Proof** - Compatible with Claude, Cursor, and other MCP clients

## Future Enhancements

- [ ] Add `tavily_extract` to Researcher Agent for deeper content analysis
- [ ] Implement `tavily_crawl` for multi-page research
- [ ] Add dynamic tool discovery from MCP server
- [ ] Support multiple MCP servers (search + code execution + web browsing)

## References

- [Tavily MCP GitHub](https://github.com/tavily-ai/tavily-mcp)
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Tavily API Docs](https://docs.tavily.com/)
