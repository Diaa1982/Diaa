from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.models.executions import ExecutionListResponse, ExecutionRecord, ExecutionRequest, ExecutionResponse
from app.services.execution_store import execution_store
from app.services.executor import execution_service

router = APIRouter()


def _to_record(item: dict) -> ExecutionRecord:
    return ExecutionRecord(
        execution_id=item['execution_id'],
        agent_id=item['agent_id'],
        mode=item['mode'],
        status=item['status'],
        task=item['task'],
        context=item['context'],
        output_text=item.get('output_text', ''),
        rendered_prompt_preview=item.get('rendered_prompt_preview', ''),
        error_text=item.get('error_text', ''),
        created_at=datetime.fromisoformat(item['created_at']),
        updated_at=datetime.fromisoformat(item['updated_at']),
    )


@router.post('/executions', response_model=ExecutionResponse)
async def create_execution(body: ExecutionRequest) -> ExecutionResponse:
    result = await execution_service.execute(
        agent_id=body.agent_id,
        task=body.task,
        context=body.context,
        mode=body.mode,
    )
    return ExecutionResponse(
        execution_id=result['execution_id'],
        agent_id=result['agent_id'],
        mode=result['mode'],
        status=result['status'],
        created_at=datetime.fromisoformat(result['created_at']),
        updated_at=datetime.fromisoformat(result['updated_at']),
        output_text=result.get('output_text', ''),
        rendered_prompt_preview=result.get('rendered_prompt_preview', ''),
    )


@router.get('/executions', response_model=ExecutionListResponse)
def list_executions(limit: int = Query(default=50, le=200, ge=1)) -> ExecutionListResponse:
    items = [_to_record(item) for item in execution_store.list(limit=limit)]
    return ExecutionListResponse(count=len(items), items=items)


@router.get('/executions/{execution_id}', response_model=ExecutionRecord)
def get_execution(execution_id: str) -> ExecutionRecord:
    item = execution_store.get(execution_id)
    if not item:
        raise HTTPException(status_code=404, detail='Execution not found')
    return _to_record(item)


@router.post('/executions/{execution_id}/retry', response_model=ExecutionResponse)
async def retry_execution(execution_id: str) -> ExecutionResponse:
    try:
        result = await execution_service.retry(execution_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail='Execution not found') from exc
    return ExecutionResponse(
        execution_id=result['execution_id'],
        agent_id=result['agent_id'],
        mode=result['mode'],
        status=result['status'],
        created_at=datetime.fromisoformat(result['created_at']),
        updated_at=datetime.fromisoformat(result['updated_at']),
        output_text=result.get('output_text', ''),
        rendered_prompt_preview=result.get('rendered_prompt_preview', ''),
    )
