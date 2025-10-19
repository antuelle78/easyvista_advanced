from fastapi import Request, Security, HTTPException
from fastapi.security import APIKeyHeader
import httpx
from app.core.config import settings

API_KEY_NAME = "X-API-KEY"
API_KEY = settings.EASYVISTA_TOOL_API_KEY

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_http_client(request: Request) -> httpx.AsyncClient:
    """
    Dependency to get the shared httpx.AsyncClient instance.
    """
    return request.app.state.http_client

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Dependency to validate the API key.
    """
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not configured on server")
    if api_key == API_KEY:
        return api_key
    else:
        raise HTTPException(status_code=401, detail="Invalid API Key")