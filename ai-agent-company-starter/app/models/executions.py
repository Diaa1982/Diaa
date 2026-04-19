from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ExecutionRequest(BaseModel):
    agent_id: str
    task: str = Field(..., description='What the selected agent is being asked to do.')
    context: Dict[str, Any] = Field(default_factory=dict)
    mode: Optional[str] = None


class ExecutionResponse(BaseModel):
    execution_id: str
    agent_id: str
    mode: str
    status: str
    created_at: datetime
    updated_at: datetime
    output_text: str
    rendered_prompt_preview: str


class ExecutionRecord(BaseModel):
    execution_id: str
    agent_id: str
    mode: str
    status: str
    task: str
    context: Dict[str, Any]
    output_text: str = ''
    rendered_prompt_preview: str = ''
    error_text: str = ''
    created_at: datetime
    updated_at: datetime


class ExecutionListResponse(BaseModel):
    count: int
    items: List[ExecutionRecord]
