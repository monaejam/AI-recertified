from langchain_mcp_adapters import MCPToolkit
from dotenv import load_dotenv

load_dotenv()

# Test the MCP Toolkit directly
def test_mcp_toolkit():
    print("🧪 Testing MCP Toolkit Integration")
    print("=" * 60)
    
    try:
        # Create the toolkit
        print("Creating MCP Toolkit...")
        toolkit = MCPToolkit(
            server_command=["python", "server.py"]
        )
        
        # Get available tools
        print("\nGetting tools from MCP server...")
        tools = toolkit.get_tools()
        
        print(f"\n✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
            
        # Test each tool
        print("\n" + "=" * 60)
        print("Testing individual tools:")
        
        # Find and test roll_dice
        roll_dice_tool = next((t for t in tools if t.name == "roll_dice"), None)
        if roll_dice_tool:
            print("\n🎲 Testing roll_dice:")
            result = roll_dice_tool.invoke({"notation": "2d6"})
            print(f"Result: {result}")
        
        # Find and test fetch_title
        fetch_title_tool = next((t for t in tools if t.name == "fetch_title"), None)
        if fetch_title_tool:
            print("\n🌐 Testing fetch_title:")
            result = fetch_title_tool.invoke({"url": "https://www.github.com"})
            print(f"Result: {result}")
            
        # Find and test web_search
        web_search_tool = next((t for t in tools if t.name == "web_search"), None)
        if web_search_tool:
            print("\n🔍 Testing web_search:")
            result = web_search_tool.invoke({"query": "Python MCP tutorials"})
            print(f"Result: {result[:200]}...")  # Show first 200 chars
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_mcp_toolkit()