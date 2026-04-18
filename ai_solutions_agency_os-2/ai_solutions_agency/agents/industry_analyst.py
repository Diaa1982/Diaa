from __future__ import annotations

from .base import run_agent
from ..merge_policy import merge_agent_output


def industry_analyst_node(state: dict) -> dict:
    envelope = run_agent("Industry & Best Practices Analyst", state)
    return merge_agent_output(state, envelope.model_dump())
