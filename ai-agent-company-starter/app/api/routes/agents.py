from fastapi import APIRouter, HTTPException, Query

from app.config import get_settings
from app.models.agents import AgentDetail, AgentSummary, ManifestResponse, PromptUpdateRequest, PromptUpdateResponse
from app.services.registry import get_agent, list_agents, load_manifest, update_agent_prompt

router = APIRouter()


@router.get('/manifest', response_model=ManifestResponse)
def manifest() -> ManifestResponse:
    data = load_manifest()
    agents = [AgentSummary(**{
        'id': a['id'],
        'phase': a['phase'],
        'name': a['name'],
        'role_title': a['role_title'],
        'activate_when': a['activate_when'],
        'purpose': a['purpose'],
    }) for a in data['agents']]
    return ManifestResponse(
        name=data['name'],
        version=data['version'],
        default_phase=data['default_phase'],
        agent_count=len(agents),
        agents=agents,
    )


@router.get('/agents')
def agents(phase: str | None = Query(default=None)) -> dict:
    items = list_agents(phase=phase)
    return {'count': len(items), 'items': items}


@router.get('/agents/{agent_id}', response_model=AgentDetail)
def agent_detail(agent_id: str) -> AgentDetail:
    try:
        data = get_agent(agent_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='Agent not found') from exc
    return AgentDetail(**data)


@router.put('/agents/{agent_id}/prompt', response_model=PromptUpdateResponse)
def edit_agent_prompt(agent_id: str, body: PromptUpdateRequest) -> PromptUpdateResponse:
    settings = get_settings()
    if not settings.admin_write_enabled:
        raise HTTPException(status_code=403, detail='Prompt editing is disabled in this environment.')
    try:
        updated = update_agent_prompt(agent_id, body.prompt_text)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='Agent not found') from exc
    return PromptUpdateResponse(agent_id=updated['agent_id'], prompt_path=updated['prompt_path'], updated=True)
