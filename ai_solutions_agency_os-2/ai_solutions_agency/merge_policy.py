from __future__ import annotations

from typing import Any
from .state import utc_now


PRIMARY_OUTPUT_KEYS = {
    "Discovery & Requirements Agent": "requirements_brief",
    "Industry & Best Practices Analyst": "industry_analysis",
    "Business Case & Estimation Agent": "business_case",
    "POC Design Agent": "poc_plan",
    "Negotiation & Objection Handling Agent": "negotiation_state",
    "Proposal & Commercial Strategy Agent": "commercial_offer",
    "Contract & Payment Agent": "payment_close_path",
}


def merge_agent_output(state: dict[str, Any], agent_output: dict[str, Any]) -> dict[str, Any]:
    state.setdefault("agent_outputs", []).append(agent_output)
    state["updated_at"] = utc_now()

    for item in agent_output.get("facts_added", []):
        state.setdefault("confirmed_facts", []).append(item)

    for item in agent_output.get("assumptions_added", []):
        state.setdefault("assumptions", []).append(item)

    for item in agent_output.get("estimates_added", []):
        state.setdefault("estimates", []).append(item)

    for item in agent_output.get("risks_flagged", []):
        state.setdefault("risks_and_mitigations", []).append(item)

    for question in agent_output.get("questions_raised", []):
        state.setdefault("essential_next_questions", []).append(question)

    name = agent_output.get("agent_name")
    primary_output = agent_output.get("primary_output", {})

    if name == "Customer Engagement Agent":
        buyer_signals = state.setdefault("buyer_signals", {})
        buyer_signals.update(primary_output.get("buyer_signals", {}))

    if name == "Discovery & Requirements Agent":
        state["business_problem"] = primary_output.get("business_problem", {})
        state["requirements_brief"] = primary_output.get("requirements_brief", primary_output)

    if name == "Solution Architect Agent":
        state["solution_options"] = primary_output.get("solution_options", [])
        state["recommended_option"] = primary_output.get("recommended_option", {})

    if name == "Risk, Compliance & Quality Agent":
        state["human_review_flags"] = primary_output.get("human_review_flags", state.get("human_review_flags", []))

    key = PRIMARY_OUTPUT_KEYS.get(name)
    if key and key not in {"requirements_brief"}:
        state[key] = primary_output

    return state
