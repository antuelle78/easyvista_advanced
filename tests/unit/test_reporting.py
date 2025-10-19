import os
import pytest
import httpx
from httpx import AsyncClient, ASGITransport
from app.main import app
import respx

# Manually load the .env file
with open("/app/.env") as f:
    for line in f:
        if line.strip() and not line.startswith("#"):
            key, value = line.strip().split("=", 1)
            os.environ[key] = value

@pytest.mark.asyncio
@respx.mock
async def test_get_tickets_by_status():
    # Mock the EasyVista API
            account_id = os.getenv("EASYVISTA_ACCOUNT_ID")
            respx.get("http://mock_api:8085/api/v1/tickets", params={"account_id": account_id, "limit": 50, "offset": 0, "status": "Open"}).mock(return_value=httpx.Response(200, json={"tickets": [{"rfc_number": "RFC123", "status": "Open"}]}))
    
            api_key = os.getenv("EASYVISTA_TOOL_API_KEY")
            headers = {"X-API-KEY": api_key}
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                response = await ac.post("/api/v1/mcp", json={
                    "jsonrpc": "2.0",
                    "method": "get_tickets_by_status",
                    "params": {"status": "Open"},
                    "id": 1
                }, headers=headers)
            assert response.status_code == 200
            response_json = response.json()
            assert response_json["result"][0]["status"] == "Open"
