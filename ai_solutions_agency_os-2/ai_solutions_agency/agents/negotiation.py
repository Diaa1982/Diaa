from __future__ import annotations

from .base import run_agent
from ..merge_policy import merge_agent_output


def negotiation_node(state: dict) -> dict:
    envelope = run_agent("Negotiation & Objection Handling Agent", state)
    return merge_agent_output(state, envelope.model_dump())
