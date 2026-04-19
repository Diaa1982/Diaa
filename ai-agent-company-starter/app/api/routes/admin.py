from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.services.execution_store import execution_store
from app.services.registry import get_agent, list_agents

router = APIRouter()
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def root() -> HTMLResponse:
    return HTMLResponse('<meta http-equiv="refresh" content="0; url=/admin">')


@router.get('/admin', response_class=HTMLResponse)
def admin_dashboard(request: Request) -> HTMLResponse:
    settings = get_settings()
    if not settings.admin_enabled:
        raise HTTPException(status_code=404, detail='Admin UI is disabled.')
    return templates.TemplateResponse(
        'dashboard.html',
        {
            'request': request,
            'settings': settings,
            'agents': list_agents(),
            'recent_executions': execution_store.list(limit=20),
        },
    )


@router.get('/admin/agents/{agent_id}', response_class=HTMLResponse)
def admin_agent_detail(request: Request, agent_id: str) -> HTMLResponse:
    settings = get_settings()
    if not settings.admin_enabled:
        raise HTTPException(status_code=404, detail='Admin UI is disabled.')
    try:
        agent = get_agent(agent_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='Agent not found') from exc
    return templates.TemplateResponse(
        'agent_detail.html',
        {
            'request': request,
            'settings': settings,
            'agent': agent,
        },
    )
