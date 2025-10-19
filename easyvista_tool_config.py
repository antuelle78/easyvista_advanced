# easyvista_tool_config.py
import os

# This is the base URL of your EasyVista service
BASE_URL = "http://localhost:8004/api/v1"

# This is the API key required by your service
API_KEY = os.getenv("API_KEY", "a-very-secret-api-key")

# Path to the schema file you generated
TOOLS_JSON_PATH = "./tools.json"

def get_tool_config():
    """
    Returns the configuration for the EasyVista tool,
    which can be integrated with Open-WebUI.
    """
    return {
        "id": "easyvista_tool",
        "name": "EasyVista IT Management",
        "description": "A tool for managing IT tickets and generating reports from EasyVista.",
        "type": "http",
        "endpoint": f"{BASE_URL}/mcp",
        "headers": {
            "X-API-KEY": API_KEY,
            "Content-Type": "application/json",
        },
        "json_rpc_format": True,  # Specifies that the tool uses the JSON-RPC 2.0 format
        "schema_path": TOOLS_JSON_PATH,
    }

if __name__ == "__main__":
    import json
    config = get_tool_config()
    print(json.dumps(config, indent=2))
