from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .state import create_initial_state
from .workflow import build_graph


app = FastAPI(
    title="AI Solutions Agency OS",
    version="0.2.0",
    description="Starter API for orchestrating a multi-agent AI solutions workflow.",
)


class RunDealRequest(BaseModel):
    customer_name: str = Field(..., min_length=1)
    customer_input_raw: str = Field(..., min_length=1)
    industry: str = "unknown"
    company_size: str = "unknown"
    geo: str = "unknown"
    currency: str = "USD"
    thread_id: str = "demo-thread-1"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "AI Solutions Agency OS",
        "status": "running",
        "docs": "/docs",
    }


@app.post("/run-deal")
def run_deal(payload: RunDealRequest) -> dict:
    state = create_initial_state(
        customer_name=payload.customer_name,
        customer_input_raw=payload.customer_input_raw,
        industry=payload.industry,
        company_size=payload.company_size,
        geo=payload.geo,
        currency=payload.currency,
    )

    graph = build_graph()
    result = graph.invoke(
        state,
        config={"configurable": {"thread_id": payload.thread_id}},
    )
    return result
