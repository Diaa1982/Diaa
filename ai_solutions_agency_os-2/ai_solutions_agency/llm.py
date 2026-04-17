from __future__ import annotations

import json
from typing import Any, Type

from pydantic import BaseModel, ValidationError
from openai import OpenAI

from .config import get_settings


class LLMAdapter:
    def generate_structured(
        self,
        agent_name: str,
        prompt: str,
        state: dict[str, Any],
        response_model: Type[BaseModel],
    ) -> BaseModel:
        raise NotImplementedError


class FakeLLMAdapter(LLMAdapter):
    def generate_structured(
        self,
        agent_name: str,
        prompt: str,
        state: dict[str, Any],
        response_model: Type[BaseModel],
    ) -> BaseModel:
        payload = fake_payload(agent_name, state)
        return response_model.model_validate(payload)


class OpenAILLMAdapter(LLMAdapter):
    def __init__(self) -> None:
        settings = get_settings()
        self.model = settings.openai_model
        self.client = OpenAI(api_key=settings.openai_api_key)

    def generate_structured(
        self,
        agent_name: str,
        prompt: str,
        state: dict[str, Any],
        response_model: Type[BaseModel],
    ) -> BaseModel:
        schema_json = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        state_json = json.dumps(state, ensure_ascii=False, indent=2)

        full_prompt = f"""
System role:
{prompt}

Task:
Return ONLY valid JSON that conforms to this JSON Schema:
{schema_json}

Current shared state:
{state_json}
""".strip()

        last_error = None
        for _ in range(3):
            response = self.client.responses.create(
                model=self.model,
                input=full_prompt,
            )
            raw = getattr(response, "output_text", "") or ""
            raw = raw.strip()

            try:
                data = json.loads(raw)
                return response_model.model_validate(data)
            except (json.JSONDecodeError, ValidationError) as exc:
                last_error = exc
                full_prompt = (
                    full_prompt
                    + "\n\nYour prior response did not validate. Return ONLY valid JSON matching the schema."
                )

        raise RuntimeError(f"Model output could not be validated after retries: {last_error}")


def get_llm_adapter() -> LLMAdapter:
    settings = get_settings()
    if settings.use_fake_llm:
        return FakeLLMAdapter()
    return OpenAILLMAdapter()


def fake_payload(agent_name: str, state: dict[str, Any]) -> dict[str, Any]:
    stage = state.get("current_stage", "lead_intake")

    if agent_name == "Customer Engagement Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Lead shows practical need with medium urgency and likely value potential.",
            "facts_added": [
                {"item": "Customer wants AI to improve support and recommendations", "source": "customer", "confidence": "high"}
            ],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "buyer_signals": {
                    "urgency": "high",
                    "budget_signal": "unknown",
                    "authority_signal": "moderate",
                    "intent_score": 55
                }
            },
            "risks_flagged": [],
            "questions_raised": ["What systems currently hold support and product data?"],
            "recommended_next_agent": "Discovery & Requirements Agent",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "Discovery & Requirements Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Structured discovery completed from raw input.",
            "facts_added": [
                {"item": "Customer support is slow", "source": "customer", "confidence": "high"},
                {"item": "Product recommendations are weak", "source": "customer", "confidence": "high"}
            ],
            "assumptions_added": [
                {"item": "Customer likely uses a CRM or ticketing platform", "basis": "Common retail support operations", "confidence": "medium"}
            ],
            "estimates_added": [],
            "primary_output": {
                "business_problem": {
                    "problem_statement": "Support responsiveness and product relevance are underperforming.",
                    "target_outcome": "Improve service speed, recommendation relevance, and measurable customer experience outcomes."
                },
                "requirements_brief": {
                    "current_state": "Manual or weakly automated support and recommendation workflows.",
                    "future_state": "AI-assisted support and AI-driven recommendation capability with pilot-first rollout.",
                    "constraints": ["Limited baseline data", "Need practical short-term value"],
                    "success_metrics": ["Response time reduction", "Deflection improvement", "Conversion lift"]
                }
            },
            "risks_flagged": [],
            "questions_raised": ["Do you have historical ticket and product interaction data?"],
            "recommended_next_agent": "Industry & Best Practices Analyst",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "Industry & Best Practices Analyst":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Industry context inferred conservatively.",
            "facts_added": [],
            "assumptions_added": [
                {"item": "Retail customer support volumes are likely variable and campaign-sensitive", "basis": "Retail benchmark pattern", "confidence": "medium"},
                {"item": "Recommendation value depends on product catalog and interaction data quality", "basis": "Retail AI best practice", "confidence": "high"}
            ],
            "estimates_added": [
                {"metric": "Potential support handling efficiency improvement", "value": "10-25%", "range_low": 10, "range_high": 25, "basis": "Conservative benchmark range"}
            ],
            "primary_output": {
                "operating_model_hypothesis": "Retail service plus digital commerce support model.",
                "likely_ai_use_cases": ["Support triage", "Response drafting", "Recommendation ranking"],
                "constraints": ["Data quality", "Integration maturity", "Adoption readiness"]
            },
            "risks_flagged": [
                {"risk": "Weak data readiness may reduce pilot quality", "severity": "medium", "likelihood": "medium", "mitigation": "Start with narrow pilot and baseline capture"}
            ],
            "questions_raised": [],
            "recommended_next_agent": "Business Case & Estimation Agent",
            "human_review_required": False,
            "confidence": "medium"
        }

    if agent_name == "Business Case & Estimation Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Business case drafted with scenario logic.",
            "facts_added": [],
            "assumptions_added": [
                {"item": "Pilot baseline can be established within 2-4 weeks", "basis": "Common pilot design practice", "confidence": "medium"}
            ],
            "estimates_added": [
                {"metric": "Potential payback period", "value": "6-12 months", "range_low": 6, "range_high": 12, "basis": "Assumption-based scenario estimate"}
            ],
            "primary_output": {
                "baseline_problem": "Slow response and weak recommendation quality create service and revenue leakage.",
                "value_drivers": ["Faster resolution", "Agent productivity", "Conversion improvement"],
                "scenario_low": {"summary": "Operational efficiency gains only"},
                "scenario_base": {"summary": "Efficiency gains plus moderate commercial uplift"},
                "scenario_upside": {"summary": "Strong service uplift plus measurable conversion impact"},
                "roi_summary": "Positive ROI is plausible if baseline volumes justify automation scope.",
                "payback_summary": "Likely within a year under a controlled pilot-to-scale path.",
                "assumption_sensitivity": "Moderate to high sensitivity to data quality and adoption."
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "Solution Architect Agent",
            "human_review_required": False,
            "confidence": "medium"
        }

    if agent_name == "Solution Architect Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Solution options designed and recommended option selected.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "solution_options": [
                    {
                        "name": "Lean support copilot",
                        "scope": ["Ticket triage", "Response drafting"],
                        "fit": "Fastest path to value"
                    },
                    {
                        "name": "Balanced CX AI stack",
                        "scope": ["Support copilot", "Recommendation engine pilot"],
                        "fit": "Best balance of value and feasibility"
                    }
                ],
                "recommended_option": {
                    "name": "Balanced CX AI stack",
                    "why": "Addresses both service performance and recommendation weakness with phased delivery.",
                    "phases": ["Pilot support copilot", "Add recommendation pilot", "Scale after KPI validation"]
                }
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "POC Design Agent",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "POC Design Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Pilot path defined.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "objective": "Validate service improvement and feasibility using a narrow support pilot first.",
                "timeline": "6 weeks",
                "scope": ["Ticket triage", "Response drafting for selected use cases"],
                "kpis": ["Response time", "Agent productivity", "Draft acceptance rate"],
                "success_thresholds": ["10% faster handling", "Usable draft rate above agreed threshold"],
                "decision_gate": "Proceed to wider rollout only if pilot meets KPI and risk thresholds"
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "Risk, Compliance & Quality Agent",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "Risk, Compliance & Quality Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Risk review completed.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "human_review_flags": [
                    {
                        "reason": "Data governance sign-off required before scale-up",
                        "threshold": "Any customer data used in production-like workflow",
                        "severity": "medium"
                    }
                ]
            },
            "risks_flagged": [
                {"risk": "Personal data handling during pilot", "severity": "high", "likelihood": "medium", "mitigation": "Use approved data controls and masked datasets where possible"},
                {"risk": "Knowledge-base quality may reduce output quality", "severity": "medium", "likelihood": "high", "mitigation": "Curate pilot knowledge set before go-live"}
            ],
            "questions_raised": [],
            "recommended_next_agent": "Proposal & Commercial Strategy Agent",
            "human_review_required": True,
            "confidence": "high"
        }

    if agent_name == "Proposal & Commercial Strategy Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Commercial offer prepared.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "offer_type": "Paid pilot",
                "scope": ["Discovery validation", "Support pilot implementation", "KPI measurement"],
                "deliverables": ["Pilot configuration", "KPI dashboard", "Scale recommendation"],
                "assumptions": ["Customer provides access to required systems and SMEs"],
                "exclusions": ["Full enterprise rollout", "Long-term managed service"],
                "timeline": "6-8 weeks",
                "pricing_structure": {"model": "Fixed fee for pilot, scale phase separately priced"},
                "payment_milestones": ["40% on kickoff", "40% on pilot go-live", "20% on final readout"]
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "Negotiation & Objection Handling Agent",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "Negotiation & Objection Handling Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Negotiation position prepared.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "likely_objections": ["Price", "Proof of value", "Integration concern"],
                "responses": [
                    "Use pilot-first commercial structure.",
                    "Tie continuation to KPI gates.",
                    "Limit scope before offering discount."
                ],
                "red_lines": ["No unconditional outcome guarantee", "No unpriced enterprise rollout"]
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "Contract & Payment Agent",
            "human_review_required": False,
            "confidence": "high"
        }

    if agent_name == "Contract & Payment Agent":
        return {
            "agent_name": agent_name,
            "stage": stage,
            "summary": "Close path prepared.",
            "facts_added": [],
            "assumptions_added": [],
            "estimates_added": [],
            "primary_output": {
                "contract_status": "Ready for drafting",
                "approval_requirements": ["Commercial approval", "Data governance confirmation"],
                "invoice_trigger": "Signed pilot agreement",
                "payment_terms": "40/40/20 milestone-based",
                "kickoff_prerequisites": ["Named customer sponsor", "Data access confirmation", "Pilot KPI baseline agreement"]
            },
            "risks_flagged": [],
            "questions_raised": [],
            "recommended_next_agent": "",
            "human_review_required": False,
            "confidence": "high"
        }

    raise ValueError(f"Unsupported agent for fake payload: {agent_name}")
