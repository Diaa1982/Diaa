from __future__ import annotations

from .base import run_agent
from ..merge_policy import merge_agent_output


def business_case_node(state: dict) -> dict:
    envelope = run_agent("Business Case & Estimation Agent", state)
    return merge_agent_output(state, envelope.model_dump())
