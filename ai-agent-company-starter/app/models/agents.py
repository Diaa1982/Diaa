from typing import List

from pydantic import BaseModel


class AgentSummary(BaseModel):
    id: str
    phase: str
    name: str
    role_title: str
    activate_when: str
    purpose: str


class AgentDetail(AgentSummary):
    inputs_required: List[str]
    outputs_expected: List[str]
    handoff_destination: List[str]
    escalation_conditions: List[str]
    functions: List[str]
    prompt_path: str
    prompt_text: str


class ManifestResponse(BaseModel):
    name: str
    version: str
    default_phase: str
    agent_count: int
    agents: List[AgentSummary]


class PromptUpdateRequest(BaseModel):
    prompt_text: str


class PromptUpdateResponse(BaseModel):
    agent_id: str
    prompt_path: str
    updated: bool
