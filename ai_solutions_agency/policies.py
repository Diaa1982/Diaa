from __future__ import annotations

from typing import Any


STAGES = [
    "lead_intake",
    "discovery",
    "qualification",
    "business_case",
    "solution_design",
    "poc_definition",
    "proposal",
    "negotiation",
    "closed_won_pending_payment",
    "paid",
    "closed_lost",
    "delivery_handover",
]


def next_stage(state: dict[str, Any]) -> str:
    stage = state.get("current_stage", "lead_intake")

    if stage == "lead_intake" and state.get("requirements_brief"):
        return "discovery"

    if stage == "discovery" and state.get("buyer_signals", {}).get("intent_score", 0) >= 40:
        return "qualification"

    if stage == "qualification" and state.get("business_case"):
        return "business_case"

    if stage == "business_case" and state.get("recommended_option"):
        return "solution_design"

    if stage == "solution_design" and state.get("poc_plan"):
        return "poc_definition"

    if stage in {"solution_design", "poc_definition"} and state.get("commercial_offer"):
        return "proposal"

    if stage == "proposal" and state.get("negotiation_state"):
        return "negotiation"

    if stage == "negotiation" and state.get("payment_close_path"):
        return "closed_won_pending_payment"

    return stage


def should_escalate_to_human(state: dict[str, Any]) -> list[dict[str, str]]:
    flags: list[dict[str, str]] = []

    if len(state.get("assumptions", [])) >= 8:
        flags.append(
            {
                "reason": "High assumption dependency",
                "threshold": "8 or more assumptions captured",
                "severity": "medium",
            }
        )

    for risk in state.get("risks_and_mitigations", []):
        if risk.get("severity") in {"high", "critical"}:
            flags.append(
                {
                    "reason": "High-severity delivery or compliance risk",
                    "threshold": risk.get("severity", "high"),
                    "severity": risk.get("severity", "high"),
                }
            )

    return flags
