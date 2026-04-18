from __future__ import annotations

from typing import Any

from ..llm import get_llm_adapter
from ..prompts import AGENT_PROMPTS
from ..schemas import AgentEnvelope


def run_agent(agent_name: str, state: dict[str, Any]) -> AgentEnvelope:
    adapter = get_llm_adapter()
    prompt = AGENT_PROMPTS[agent_name]
    return adapter.generate_structured(
        agent_name=agent_name,
        prompt=prompt,
        state=state,
        response_model=AgentEnvelope,
    )
