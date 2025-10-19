import pytest
import asyncio
import httpx
from app.main import app

@pytest.fixture(scope="session", autouse=True)
def http_client_lifespan():
    app.state.http_client = httpx.AsyncClient(timeout=10)
    yield
    asyncio.run(app.state.http_client.aclose())
