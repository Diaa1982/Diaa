from __future__ import annotations

import os
from functools import lru_cache
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv()


class Settings(BaseModel):
    app_env: str = os.getenv("APP_ENV", "local")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    use_fake_llm: bool = os.getenv("USE_FAKE_LLM", "true").lower() == "true"
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5.4")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
