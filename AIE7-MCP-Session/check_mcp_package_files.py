import os
import langchain_mcp_adapters

# Get the package directory
package_dir = os.path.dirname(langchain_mcp_adapters.__file__)

print("🔍 Checking langchain_mcp_adapters package structure")
print("=" * 60)
print(f"Package directory: {package_dir}")
print("\nFiles in package directory:")

# List all files in the package directory
for item in os.listdir(package_dir):
    item_path = os.path.join(package_dir, item)
    if os.path.isfile(item_path):
        print(f"  📄 {item}")
    elif os.path.isdir(item_path) and not item.startswith('__'):
        print(f"  📁 {item}/")
        # List files in subdirectory
        try:
            for subitem in os.listdir(item_path):
                if subitem.endswith('.py') and not subitem.startswith('__'):
                    print(f"     - {subitem}")
        except:
            pass

# Try to find the actual modules
print("\nTrying specific imports:")
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    print("✅ Successfully imported MultiServerMCPClient from langchain_mcp_adapters.client")
except ImportError as e:
    print(f"❌ Could not import MultiServerMCPClient: {e}")

try:
    from langchain_mcp_adapters.tools import load_mcp_tools
    print("✅ Successfully imported load_mcp_tools from langchain_mcp_adapters.tools")
except ImportError as e:
    print(f"❌ Could not import load_mcp_tools: {e}")