from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import admin, agents, config, executions, health
from app.core.logging import configure_logging
from app.services.execution_store import execution_store
from app.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level)
    execution_store.initialize()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        docs_url='/api/v1/docs',
        openapi_url='/api/v1/openapi.json',
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.include_router(health.router, prefix='/api/v1', tags=['health'])
    app.include_router(config.router, prefix='/api/v1', tags=['config'])
    app.include_router(agents.router, prefix='/api/v1', tags=['agents'])
    app.include_router(executions.router, prefix='/api/v1', tags=['executions'])
    app.include_router(admin.router, tags=['admin'])
    return app


app = create_app()
