from functools import lru_cache
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = Field(default='AI Agent Company Platform', alias='APP_NAME')
    app_version: str = Field(default='0.2.0', alias='APP_VERSION')
    app_env: str = Field(default='local', alias='APP_ENV')
    debug: bool = Field(default=True, alias='DEBUG')
    host: str = Field(default='0.0.0.0', alias='HOST')
    port: int = Field(default=8080, alias='PORT')
    log_level: str = Field(default='INFO', alias='LOG_LEVEL')

    agents_manifest_path: str = Field(default='agents/manifest.json', alias='AGENTS_MANIFEST_PATH')
    global_rules_path: str = Field(default='docs/global-operating-rules.md', alias='GLOBAL_RULES_PATH')
    data_dir: str = Field(default='/tmp/agent_platform_data', alias='DATA_DIR')
    database_url: str = Field(default='sqlite:////tmp/agent_platform_data/executions.db', alias='DATABASE_URL')

    admin_enabled: bool = Field(default=True, alias='ADMIN_ENABLED')
    admin_write_enabled: bool = Field(default=False, alias='ADMIN_WRITE_ENABLED')
    cors_origins: List[str] | str = Field(default='*', alias='CORS_ORIGINS')

    default_execution_mode: str = Field(default='mock', alias='DEFAULT_EXECUTION_MODE')
    llm_provider: str = Field(default='none', alias='LLM_PROVIDER')
    llm_model: str = Field(default='', alias='LLM_MODEL')
    llm_base_url: str = Field(default='', alias='LLM_BASE_URL')
    llm_api_key: str = Field(default='', alias='LLM_API_KEY')
    llm_temperature: float = Field(default=0.2, alias='LLM_TEMPERATURE')
    llm_max_tokens: int = Field(default=1500, alias='LLM_MAX_TOKENS')

    @field_validator('cors_origins', mode='before')
    @classmethod
    def parse_cors_origins(cls, value):
        if isinstance(value, str):
            if value.strip() == '*':
                return ['*']
            return [item.strip() for item in value.split(',') if item.strip()]
        return value

    @property
    def base_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def manifest_path(self) -> Path:
        return (self.base_dir / self.agents_manifest_path).resolve()

    @property
    def rules_file_path(self) -> Path:
        return (self.base_dir / self.global_rules_path).resolve()

    @property
    def sqlite_path(self) -> Path:
        if self.database_url.startswith('sqlite:////'):
            return Path('/' + self.database_url.replace('sqlite:////', '', 1)).resolve()
        if self.database_url.startswith('sqlite:///'):
            return (self.base_dir / self.database_url.replace('sqlite:///', '', 1)).resolve()
        raise ValueError('Only sqlite DATABASE_URL is supported in this scaffold.')


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.data_dir).mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
