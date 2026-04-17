from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


ConfidenceLevel = Literal["high", "medium", "low"]
Severity = Literal["low", "medium", "high", "critical"]
Likelihood = Literal["low", "medium", "high"]


class FactItem(BaseModel):
    item: str
    source: Literal["customer", "document", "benchmark", "inference"] = "inference"
    confidence: ConfidenceLevel = "medium"


class AssumptionItem(BaseModel):
    item: str
    basis: str
    confidence: ConfidenceLevel = "medium"


class EstimateItem(BaseModel):
    metric: str
    value: str | float | int
    range_low: float | int | None = None
    range_high: float | int | None = None
    basis: str


class RiskItem(BaseModel):
    risk: str
    severity: Severity = "medium"
    likelihood: Likelihood = "medium"
    mitigation: str


class ReviewFlag(BaseModel):
    reason: str
    threshold: str
    severity: Severity = "medium"


class AgentEnvelope(BaseModel):
    agent_name: str
    stage: str
    summary: str
    facts_added: list[FactItem] = Field(default_factory=list)
    assumptions_added: list[AssumptionItem] = Field(default_factory=list)
    estimates_added: list[EstimateItem] = Field(default_factory=list)
    primary_output: dict[str, Any] = Field(default_factory=dict)
    risks_flagged: list[RiskItem] = Field(default_factory=list)
    questions_raised: list[str] = Field(default_factory=list)
    recommended_next_agent: str = ""
    human_review_required: bool = False
    confidence: ConfidenceLevel = "medium"


class FinalSummary(BaseModel):
    deal_id: str
    customer_name: str
    current_stage: str
    business_problem: dict[str, Any] = Field(default_factory=dict)
    recommended_option: dict[str, Any] = Field(default_factory=dict)
    business_case: dict[str, Any] = Field(default_factory=dict)
    poc_plan: dict[str, Any] = Field(default_factory=dict)
    risks_and_mitigations: list[dict[str, Any]] = Field(default_factory=list)
    commercial_offer: dict[str, Any] = Field(default_factory=dict)
    payment_close_path: dict[str, Any] = Field(default_factory=dict)
    next_actions: list[str] = Field(default_factory=list)
