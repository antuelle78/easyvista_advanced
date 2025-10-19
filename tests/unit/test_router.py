# tests/unit/test_router.py
import pytest
import os
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    api_key = os.getenv("EASYVISTA_TOOL_API_KEY")
    headers = {"X-API-KEY": api_key}
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/v1/health", headers=headers)
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# TODO: Add more unit tests for the router
