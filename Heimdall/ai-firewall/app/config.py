from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    """
    # Define environment variables with their types.
    
    # Placeholders for requested settings
    DATABASE_URL: str = "sqlite:///./firewall.db"
    OPENAI_API_KEY: str | None = None
    
    # You can add more settings here, for example:
    # DEBUG: bool = False
    # ENVIRONMENT: str = "development"

    # Configuration for pydantic-settings to load from a .env file
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        # Allow extra environment variables in the environment to be ignored
        extra="ignore" 
    )

# Create a global instance of Settings to be imported across the app
settings = Settings()
