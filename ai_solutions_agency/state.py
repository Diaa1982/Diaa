from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, TypedDict


class DealState(TypedDict, total=False):
    deal_id: str
    customer_name: str
    created_at: str
    updated_at: str
    current_stage: str
    customer_input_raw: str
    industry: str
    company_size: str
    geo: str
    currency: str

    stakeholders: list[dict[str, Any]]
    buyer_signals: dict[str, Any]

    confirmed_facts: list[dict[str, Any]]
    assumptions: list[dict[str, Any]]
    estimates: list[dict[str, Any]]

    business_problem: dict[str, Any]
    requirements_brief: dict[str, Any]
    industry_analysis: dict[str, Any]
    business_case: dict[str, Any]
    solution_options: list[dict[str, Any]]
    recommended_option: dict[str, Any]
    poc_plan: dict[str, Any]
    risks_and_mitigations: list[dict[str, Any]]
    commercial_offer: dict[str, Any]
    negotiation_state: dict[str, Any]
    payment_close_path: dict[str, Any]

    essential_next_questions: list[str]
    routing_log: list[dict[str, Any]]
    human_review_flags: list[dict[str, Any]]
    agent_outputs: list[dict[str, Any]]

    status: dict[str, Any]
    final_summary: dict[str, Any]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_initial_state(
    customer_name: str,
    customer_input_raw: str,
    industry: str = "unknown",
    company_size: str = "unknown",
    geo: str = "unknown",
    currency: str = "USD",
) -> DealState:
    now = utc_now()
    return DealState(
        deal_id=f"deal-{int(datetime.now().timestamp())}",
        customer_name=customer_name,
        created_at=now,
        updated_at=now,
        current_stage="lead_intake",
        customer_input_raw=customer_input_raw,
        industry=industry,
        company_size=company_size,
        geo=geo,
        currency=currency,
        stakeholders=[],
        buyer_signals={
            "urgency": "medium",
            "budget_signal": "unknown",
            "authority_signal": "unknown",
            "intent_score": 10,
        },
        confirmed_facts=[],
        assumptions=[],
        estimates=[],
        business_problem={},
        requirements_brief={},
        industry_analysis={},
        business_case={},
        solution_options=[],
        recommended_option={},
        poc_plan={},
        risks_and_mitigations=[],
        commercial_offer={},
        negotiation_state={},
        payment_close_path={},
        essential_next_questions=[],
        routing_log=[],
        human_review_flags=[],
        agent_outputs=[],
        status={
            "proposal_ready": False,
            "contract_ready": False,
            "payment_ready": False,
            "delivery_handover_ready": False,
        },
        final_summary={},
    )
