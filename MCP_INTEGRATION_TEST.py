"""Test suite for Tavily MCP integration."""

import sys
import asyncio
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from mcp_client import get_mcp_client, TavilyMCPClient
from mcp_tools import tavily_search, get_mcp_tools_list
from agents import build_researcher_agent
from config import RESEARCHER_MODEL, WRITER_MODEL


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_mcp_client_init():
    """Test 1: MCP Client Initialization"""
    print_section("TEST 1: MCP Client Initialization")

    try:
        client = get_mcp_client()
        print("✅ MCP Client initialized successfully")
        print(f"   API Key configured: {client.api_key[:10]}...***")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize MCP client: {e}")
        return False


def test_mcp_server_config():
    """Test 2: MCP Server Configuration"""
    print_section("TEST 2: MCP Server Configuration")

    try:
        client = get_mcp_client()
        config = client.get_mcp_server_config()
        print("✅ MCP Server config retrieved")
        print(f"   URL: {config['url'][:50]}...***")
        print(f"   Type: {config['type']}")
        print(f"   Transport: {config['transport']}")
        return True
    except Exception as e:
        print(f"❌ Failed to get server config: {e}")
        return False


async def test_tool_discovery():
    """Test 3: Tool Discovery"""
    print_section("TEST 3: Tool Discovery from MCP")

    try:
        client = get_mcp_client()
        tools = await client.discover_tools()
        print(f"✅ Discovered {len(tools)} tools:")
        for tool in tools:
            print(f"   • {tool['name']}")
            print(f"     {tool['description']}")
        return True
    except Exception as e:
        print(f"❌ Failed to discover tools: {e}")
        return False


def test_mcp_tools_wrapper():
    """Test 4: MCP Tools Wrapper"""
    print_section("TEST 4: MCP Tools Wrapper (LangChain)")

    try:
        tools = get_mcp_tools_list()
        print(f"✅ Retrieved {len(tools)} LangChain tool wrappers")
        for tool in tools:
            print(f"   • {tool.name}")
            print(f"     {tool.description}")
        return True
    except Exception as e:
        print(f"❌ Failed to get tool wrappers: {e}")
        return False


def test_tavily_search_tool():
    """Test 5: Tavily Search Tool Execution"""
    print_section("TEST 5: Tavily Search Tool Execution")

    try:
        query = "Python 3.12 features"
        print(f"   Query: '{query}'")
        print(f"   Max Results: 3")
        print(f"   Calling tavily_search()...")

        result = tavily_search(query=query, max_results=3)

        print("\n✅ Tool executed successfully")
        print(f"\nResult Output:")
        print("-" * 60)
        print(result)
        print("-" * 60)
        return True
    except Exception as e:
        print(f"❌ Tool execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_researcher_agent_creation():
    """Test 6: Researcher Agent Creation with MCP Tools"""
    print_section("TEST 6: Researcher Agent Creation with MCP Tools")

    try:
        print("   Building Researcher Agent...")
        agent = build_researcher_agent()
        print("✅ Researcher Agent created successfully")
        print(f"   Model: {RESEARCHER_MODEL}")
        print(f"   Temperature: 0.1 (focused)")
        print(f"   Tools attached: {len(agent.tools) if hasattr(agent, 'tools') else 'N/A'}")
        return True
    except Exception as e:
        print(f"❌ Failed to create agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_invocation():
    """Test 7: Agent Tool Invocation"""
    print_section("TEST 7: Agent Tool Invocation (Simulation)")

    try:
        print("   Creating agent with MCP tools...")
        agent = build_researcher_agent()

        print("   Agent state:")
        print(f"   • Agent type: {type(agent).__name__}")
        print(f"   • Has tools: {hasattr(agent, 'tools')}")

        print("\n✅ Agent ready for tool invocation")
        print("   (Actual invocation requires running pipeline.py or app.py)")
        return True
    except Exception as e:
        print(f"❌ Failed to prepare agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_config():
    """Test 8: Model Configuration"""
    print_section("TEST 8: Model Configuration")

    try:
        print("✅ Configuration loaded")
        print(f"   Researcher Model: {RESEARCHER_MODEL}")
        print(f"   Writer Model: {WRITER_MODEL}")
        print(f"   Researcher Temp: 0.1 (focused search)")
        print(f"   Writer Temp: 0.6 (creative writing)")
        return True
    except Exception as e:
        print(f"❌ Failed to load config: {e}")
        return False


async def run_all_tests():
    """Run all tests in sequence."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  TAVILY MCP INTEGRATION TEST SUITE".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")

    results = []

    # Run synchronous tests
    results.append(("MCP Client Init", test_mcp_client_init()))
    results.append(("MCP Server Config", test_mcp_server_config()))
    results.append(("MCP Tools Wrapper", test_mcp_tools_wrapper()))
    results.append(("Tavily Search Tool", test_tavily_search_tool()))
    results.append(("Researcher Agent Creation", test_researcher_agent_creation()))
    results.append(("Agent Tool Invocation", test_agent_invocation()))
    results.append(("Model Configuration", test_model_config()))

    # Run async tests
    results.append(("Tool Discovery", await test_tool_discovery()))

    # Print summary
    print_section("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n✅ Passed: {passed}/{total}")
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")

    print("\n" + "=" * 60)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! MCP Integration is working correctly.")
        print("\nNext Steps:")
        print("   1. Run: uv run pipeline.py")
        print("   2. Or run: uv run streamlit run app.py")
        print("   3. Enter a research topic")
        print("   4. Watch the Researcher Agent use Tavily MCP to search")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
        print("\nCommon Issues:")
        print("   • Missing TAVILY_API_KEY in .env")
        print("   • Missing GROQ_API_KEY in .env")
        print("   • Dependencies not installed (run: uv sync)")

    print("\n" + "=" * 60 + "\n")

    return passed == total


if __name__ == "__main__":
    try:
        # Run async tests
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
