from __future__ import annotations

from langgraph.graph import StateGraph, START, END

try:
    from langgraph.checkpoint.memory import MemorySaver
except Exception:  # pragma: no cover
    MemorySaver = None  # type: ignore

from .state import DealState, utc_now
from .policies import next_stage, should_escalate_to_human
from .schemas import FinalSummary

from .agents.customer_engagement import customer_engagement_node
from .agents.discovery import discovery_node
from .agents.industry_analyst import industry_analyst_node
from .agents.business_case import business_case_node
from .agents.solution_architect import solution_architect_node
from .agents.poc_design import poc_design_node
from .agents.risk_compliance import risk_compliance_node
from .agents.proposal_commercial import proposal_commercial_node
from .agents.negotiation import negotiation_node
from .agents.contract_payment import contract_payment_node


def orchestrator_node(state: dict) -> dict:
    state["updated_at"] = utc_now()
    state["current_stage"] = next_stage(state)
    state.setdefault("routing_log", []).append(
        {
            "at": state["updated_at"],
            "stage": state["current_stage"],
            "event": "orchestrator_review",
        }
    )
    return state


def route_from_orchestrator(state: dict) -> str:
    if not state.get("buyer_signals") or state.get("buyer_signals", {}).get("intent_score", 0) < 40:
        return "customer_engagement"

    if not state.get("requirements_brief"):
        return "discovery"

    if not state.get("industry_analysis"):
        return "industry_analyst"

    if not state.get("business_case"):
        return "business_case"

    if not state.get("recommended_option"):
        return "solution_architect"

    if not state.get("poc_plan"):
        return "poc_design"

    if not state.get("risks_and_mitigations"):
        return "risk_compliance"

    if not state.get("commercial_offer"):
        return "proposal_commercial"

    if not state.get("negotiation_state"):
        return "negotiation"

    if not state.get("payment_close_path"):
        return "contract_payment"

    return "final_synthesis"


def final_synthesis_node(state: dict) -> dict:
    state["human_review_flags"] = should_escalate_to_human(state)

    summary = FinalSummary(
        deal_id=state["deal_id"],
        customer_name=state["customer_name"],
        current_stage="closed_won_pending_payment",
        business_problem=state.get("business_problem", {}),
        recommended_option=state.get("recommended_option", {}),
        business_case=state.get("business_case", {}),
        poc_plan=state.get("poc_plan", {}),
        risks_and_mitigations=state.get("risks_and_mitigations", []),
        commercial_offer=state.get("commercial_offer", {}),
        payment_close_path=state.get("payment_close_path", {}),
        next_actions=[
            "Confirm customer sponsor",
            "Confirm pilot data access",
            "Issue proposal / contract",
            "Agree KPI baseline before kickoff",
        ],
    )
    state["final_summary"] = summary.model_dump()
    state["current_stage"] = "closed_won_pending_payment"
    state["status"]["proposal_ready"] = True
    state["status"]["contract_ready"] = True
    state["status"]["payment_ready"] = True
    return state


def build_graph():
    graph = StateGraph(DealState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("customer_engagement", customer_engagement_node)
    graph.add_node("discovery", discovery_node)
    graph.add_node("industry_analyst", industry_analyst_node)
    graph.add_node("business_case", business_case_node)
    graph.add_node("solution_architect", solution_architect_node)
    graph.add_node("poc_design", poc_design_node)
    graph.add_node("risk_compliance", risk_compliance_node)
    graph.add_node("proposal_commercial", proposal_commercial_node)
    graph.add_node("negotiation", negotiation_node)
    graph.add_node("contract_payment", contract_payment_node)
    graph.add_node("final_synthesis", final_synthesis_node)

    graph.add_edge(START, "orchestrator")
    graph.add_conditional_edges(
        "orchestrator",
        route_from_orchestrator,
        {
            "customer_engagement": "customer_engagement",
            "discovery": "discovery",
            "industry_analyst": "industry_analyst",
            "business_case": "business_case",
            "solution_architect": "solution_architect",
            "poc_design": "poc_design",
            "risk_compliance": "risk_compliance",
            "proposal_commercial": "proposal_commercial",
            "negotiation": "negotiation",
            "contract_payment": "contract_payment",
            "final_synthesis": "final_synthesis",
        },
    )

    for node in [
        "customer_engagement",
        "discovery",
        "industry_analyst",
        "business_case",
        "solution_architect",
        "poc_design",
        "risk_compliance",
        "proposal_commercial",
        "negotiation",
        "contract_payment",
    ]:
        graph.add_edge(node, "orchestrator")

    graph.add_edge("final_synthesis", END)

    if MemorySaver is not None:
        return graph.compile(checkpointer=MemorySaver())
    return graph.compile()


agent = build_graph()
