"""Application settings loaded from environment variables."""
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    app_name: str = "Credit Card Fraud Detection API"
    database_url: str = "sqlite:///./fraud_detection.db"
    model_dir: Path = ROOT_DIR / "artifacts" / "models"
    dataset_path: Path = ROOT_DIR / "data" / "raw" / "creditcard.csv"
    fraud_threshold: float | None = Field(default=None, ge=0, le=1)
    high_risk_threshold: float = Field(default=0.9, ge=0, le=1)
    cors_origins: str = "http://localhost:5173"
    admin_api_key: str = ""
    max_upload_mb: int = Field(default=10, ge=1, le=100)
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FRAUD_", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [value.strip() for value in self.cors_origins.split(",") if value.strip()]


settings = Settings()
