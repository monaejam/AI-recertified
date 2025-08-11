import langchain_mcp_adapters
import inspect

print("🔍 Checking langchain_mcp_adapters package contents")
print("=" * 60)

# Check what's available in the package
print("\nAvailable attributes:")
for attr in dir(langchain_mcp_adapters):
    if not attr.startswith('_'):
        print(f"  - {attr}")

# Check if there are any classes
print("\nChecking for classes and functions:")
for name, obj in inspect.getmembers(langchain_mcp_adapters):
    if not name.startswith('_'):
        if inspect.isclass(obj):
            print(f"  Class: {name}")
        elif inspect.isfunction(obj):
            print(f"  Function: {name}")

# Try to import specific modules
print("\nTrying to import submodules:")
try:
    from langchain_mcp_adapters.adapters import MCPToolkit
    print("✅ Found MCPToolkit in langchain_mcp_adapters.adapters")
except ImportError as e:
    print(f"❌ Could not import from adapters: {e}")

try:
    from langchain_mcp_adapters.toolkit import MCPToolkit
    print("✅ Found MCPToolkit in langchain_mcp_adapters.toolkit")
except ImportError as e:
    print(f"❌ Could not import from toolkit: {e}")

# Check the package version and location
print(f"\nPackage location: {langchain_mcp_adapters.__file__}")
if hasattr(langchain_mcp_adapters, '__version__'):
    print(f"Package version: {langchain_mcp_adapters.__version__}")