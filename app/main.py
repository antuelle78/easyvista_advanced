from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
import httpx

from app.api.router import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.state.http_client = httpx.AsyncClient(timeout=30)
    logging.info("EasyVista JSON‑RPC service started, HTTP client initialized.")
    yield
    # Shutdown
    await app.state.http_client.aclose()
    logging.info("EasyVista JSON-RPC service stopped, HTTP client closed.")

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="EasyVista JSON‑RPC Wrapper",
    description="Production‑grade JSON‑RPC interface for EasyVista",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
