from __future__ import annotations

import os
from typing import Optional

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Calculate project root dynamically: [PROJECT_ROOT]/src/app/config.py -> go up 2 levels
_CONFIG_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(_CONFIG_DIR, "..", ".."))


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        validation_alias="CORS_ORIGINS",
    )

    dataset_id: str = Field(
        default="ManikaSaini/zomato-restaurant-recommendation",
        validation_alias="DATASET_ID",
    )
    data_path: str = Field(
        default="./data/processed/restaurants.parquet",
        validation_alias="DATA_PATH",
    )

    budget_low_max: float = Field(default=500, validation_alias="BUDGET_LOW_MAX")
    budget_medium_max: float = Field(default=1500, validation_alias="BUDGET_MEDIUM_MAX")

    hf_home: str = Field(
        default="./data/raw/hf_cache",
        validation_alias="HF_HOME",
    )

    max_candidates: int = Field(default=30, validation_alias="MAX_CANDIDATES", ge=1, le=200)

    llm_provider: str = Field(default="groq", validation_alias="LLM_PROVIDER")
    groq_api_key: Optional[str] = Field(default=None, validation_alias="GROQ_API_KEY")
    llm_api_key: Optional[str] = Field(default=None, validation_alias="LLM_API_KEY")
    llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        validation_alias="LLM_MODEL",
    )
    llm_temperature: float = Field(default=0.3, validation_alias="LLM_TEMPERATURE", ge=0.0, le=2.0)
    llm_timeout_seconds: float = Field(default=60.0, validation_alias="LLM_TIMEOUT_SECONDS", gt=0)
    llm_max_retries: int = Field(default=1, validation_alias="LLM_MAX_RETRIES", ge=0, le=5)
    llm_json_mode: bool = Field(default=True, validation_alias="LLM_JSON_MODE")

    @model_validator(mode="after")
    def resolve_paths(self) -> Settings:
        if not os.path.isabs(self.data_path):
            self.data_path = os.path.abspath(os.path.join(PROJECT_ROOT, self.data_path))
        if not os.path.isabs(self.hf_home):
            self.hf_home = os.path.abspath(os.path.join(PROJECT_ROOT, self.hf_home))
        return self


def get_settings() -> Settings:
    return Settings()

