from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", protected_namespaces=())

    app_name: str = Field(..., alias="APP_NAME")
    app_env: str = Field("development", alias="APP_ENV")
    host: str = Field("0.0.0.0", alias="HOST")
    port: int = Field(8000, alias="PORT")
    log_level: str = Field("info", alias="LOG_LEVEL")

    openai_api_key: str = Field("", alias="OPENAI_API_KEY")
    gemini_api_key: str = Field("", alias="GEMINI_API_KEY")
    azure_openai_api_key: str = Field("", alias="AZURE_OPENAI_API_KEY")
    azure_openai_endpoint: str = Field("", alias="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_version: str = Field("", alias="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment: str = Field("", alias="AZURE_OPENAI_DEPLOYMENT")
    chat_provider: str = Field("azure_openai", alias="CHAT_PROVIDER")

    model_path: str = Field(..., alias="MODEL_PATH")
    model_image_size: int = Field(224, alias="MODEL_IMAGE_SIZE")
    skin_labels: str = Field(..., alias="SKIN_LABELS")
    allowed_origins: str = Field("http://localhost:5173", alias="ALLOWED_ORIGINS")

    @field_validator("chat_provider")
    @classmethod
    def validate_chat_provider(cls, value: str) -> str:
        accepted = {"azure_openai", "openai", "gemini", "mock"}
        normalized = value.strip().lower()
        if normalized not in accepted:
            raise ValueError(f"CHAT_PROVIDER must be one of: {sorted(accepted)}")
        return normalized

    @property
    def resolved_model_path(self) -> Path:
        path = Path(self.model_path)
        if not path.is_absolute():
            return (BASE_DIR / path).resolve()
        return path

    @property
    def parsed_skin_labels(self) -> list[str]:
        return [item.strip() for item in self.skin_labels.split(",") if item.strip()]

    @property
    def parsed_origins(self) -> list[str]:
        return [item.strip() for item in self.allowed_origins.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    try:
        return Settings()
    except ValidationError as exc:
        raise RuntimeError(f"Invalid backend configuration: {exc}") from exc
