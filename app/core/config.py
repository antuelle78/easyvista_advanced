# app/core/config.py
import os
from pathlib import Path
from pydantic import BaseSettings, Field, AnyHttpUrl

class Settings(BaseSettings):
    """
    Manages the application's settings and environment variables.
    """
    EASYVISTA_URL: AnyHttpUrl = Field(..., env="EASYVISTA_URL")
    EASYVISTA_API_KEY: str = Field(..., env="EASYVISTA_API_KEY")
    EASYVISTA_ACCOUNT_ID: str = Field(..., env="EASYVISTA_ACCOUNT_ID")
    EASYVISTA_TOOL_API_KEY: str = Field(..., env="EASYVISTA_TOOL_API_KEY")

    # Path handling
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    
    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()