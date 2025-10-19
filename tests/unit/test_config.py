# tests/unit/test_config.py
import pytest
from pydantic import ValidationError, BaseSettings, Field, AnyHttpUrl

def test_settings_missing_env_vars(tmp_path, monkeypatch):
    """
    Tests that the application fails to start if required environment
    variables are missing.
    """
    # Unset the environment variable to ensure the test is isolated from the host
    monkeypatch.delenv("EASYVISTA_URL", raising=False)

    # Create a temporary .env file that is missing the EASYVISTA_URL
    env_content = """
EASYVISTA_API_KEY=your_api_key
EASYVISTA_ACCOUNT_ID=your_account_id
EASYVISTA_TOOL_API_KEY=a-very-secret-api-key
"""
    env_file = tmp_path / ".env"
    env_file.write_text(env_content)

    with pytest.raises(ValidationError):
        # Define a temporary Settings class for this test
        class TempSettings(BaseSettings):
            EASYVISTA_URL: AnyHttpUrl = Field(..., env="EASYVISTA_URL")
            EASYVISTA_API_KEY: str = Field(..., env="EASYVISTA_API_KEY")
            EASYVISTA_ACCOUNT_ID: str = Field(..., env="EASYVISTA_ACCOUNT_ID")
            EASYVISTA_TOOL_API_KEY: str = Field(..., env="EASYVISTA_TOOL_API_KEY")

        # Instantiate the class, passing the temporary .env file directly
        TempSettings(_env_file=env_file)
