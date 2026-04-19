from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get('/config/public')
def public_config() -> dict:
    settings = get_settings()
    return {
        'app_name': settings.app_name,
        'app_version': settings.app_version,
        'app_env': settings.app_env,
        'admin_enabled': settings.admin_enabled,
        'admin_write_enabled': settings.admin_write_enabled,
        'default_execution_mode': settings.default_execution_mode,
        'llm_provider': settings.llm_provider,
    }
