from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Secure AI Insights Assistant"
    api_key: str = Field(default="dev-internal-key", alias="ASSISTANT_API_KEY")
    ollama_api_key: str | None = Field(default=None, alias="OLLAMA_API_KEY")
    database_path: Path = Field(default=Path(__file__).resolve().parents[1] / "data" / "assistant.db")
    csv_dir: Path = Field(default=Path(__file__).resolve().parents[1] / "data" / "csv")
    pdf_dir: Path = Field(default=Path(__file__).resolve().parents[1] / "data" / "pdf")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


if __name__ == "__main__":
    settings = get_settings()

    print("Config loaded successfully")
    print("App Name:", settings.app_name)
    print("Ollama Key Exists:", bool(settings.ollama_api_key))
    print("Database Path:", settings.database_path)