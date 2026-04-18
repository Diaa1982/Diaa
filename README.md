# AI Solutions Agency OS (Python starter)

A production-oriented **starter** for a multi-agent AI solutions company built around:

- **LangGraph** for orchestration
- **shared state** (`DealState`)
- **specialist agent envelopes**
- **stage-gated progression**
- **merge policy**
- **fake mode** for immediate local testing
- **real model adapter** using the OpenAI Python SDK in JSON mode with validation/retry

## What this starter already does

- Runs a full orchestration flow from `lead_intake` to `closed_won_pending_payment`
- Persists and mutates a shared deal state
- Separates:
  - confirmed facts
  - assumptions
  - estimates
  - risks
- Validates specialist outputs with Pydantic models
- Supports a **fake test mode** so you can run it without any API key first

## What this starter is not yet

- Not a finished SaaS product
- Not wired to CRM, billing, proposal generation systems, or document storage
- Not a production UI
- Not a complete legal/compliance control stack

It is the correct **starter operating core**.

## Folder structure

```text
ai_solutions_agency_os/
├── ai_solutions_agency/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── business_case.py
│   │   ├── contract_payment.py
│   │   ├── customer_engagement.py
│   │   ├── discovery.py
│   │   ├── industry_analyst.py
│   │   ├── negotiation.py
│   │   ├── poc_design.py
│   │   ├── proposal_commercial.py
│   │   ├── risk_compliance.py
│   │   └── solution_architect.py
│   ├── __init__.py
│   ├── config.py
│   ├── llm.py
│   ├── merge_policy.py
│   ├── policies.py
│   ├── prompts.py
│   ├── schemas.py
│   ├── state.py
│   └── workflow.py
├── examples/
│   └── sample_deal.json
├── .env.example
├── langgraph.json
├── main.py
├── pyproject.toml
└── README.md
```

## Fastest way to test it now

### Option A — local machine with VS Code or Cursor
1. Create a folder on your machine called `ai_solutions_agency_os`
2. Paste all files from this starter into that folder
3. Open the folder in **VS Code** or **Cursor**
4. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
5. Activate it:
   - macOS / Linux
     ```bash
     source .venv/bin/activate
     ```
   - Windows PowerShell
     ```powershell
     .venv\Scripts\Activate.ps1
     ```
6. Install:
   ```bash
   pip install -e .
   ```
7. Copy `.env.example` to `.env`
8. Keep `USE_FAKE_LLM=true` first
9. Run:
   ```bash
   python main.py
   ```

### Option B — Replit
- Create a new Python repl
- Upload all files preserving the same structure
- Install dependencies from `pyproject.toml`
- Add environment variables from `.env.example`
- Run `python main.py`

### Option C — GitHub + Codespaces
- Create a GitHub repository
- Upload the files preserving the same structure
- Open in Codespaces
- Run the same setup steps:
  ```bash
  pip install -e .
  python main.py
  ```

## How to switch from fake mode to real model mode

In `.env`:

```env
USE_FAKE_LLM=false
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-5.4
```

Then run again:

```bash
python main.py
```

The real adapter uses the OpenAI Python SDK and asks each specialist to return strict JSON which is then validated with Pydantic. If a response is malformed, the adapter retries automatically.

## Where to paste the files

Paste them into **one project folder** with the exact same directory structure shown above.

The most practical locations are:

- **Cursor** if you want AI-assisted development and debugging
- **VS Code** if you want standard local Python development
- **Replit** if you want the fastest cloud test
- **GitHub Codespaces** if you want a clean hosted dev environment

If your goal is **the fastest real test**, use:
1. **Cursor locally**, or
2. **GitHub Codespaces**

## Recommended next implementation layers after this starter

1. CRM integration
2. proposal document generation
3. approval workflow
4. pricing policy engine
5. payment/invoice integration
6. pilot KPI tracker
7. delivery handover pack
8. basic web UI (FastAPI + React)

## Run output

The starter writes a final JSON file to:

```text
./run_output.json
```

That file shows the synthesized final deal state after orchestration.

## LangGraph note

LangGraph’s docs describe graphs in terms of **state, nodes, and edges**, and LangGraph applications are commonly organized around a package folder, dependency file, `.env`, and `langgraph.json`. The docs also highlight persistence/checkpointing for human-in-the-loop and stateful workflows. See the official docs for the current structure and deployment patterns. citeturn566720view1turn566720view2turn566720view3


## API mode

This repo now includes a small FastAPI layer so you can run it as a service.

### Run locally as an API

```bash
pip install -e .
cp .env.example .env
uvicorn ai_solutions_agency.api:app --reload
```

Open:
- API root: `http://127.0.0.1:8000/`
- Health: `http://127.0.0.1:8000/health`
- Swagger UI: `http://127.0.0.1:8000/docs`

### Example API request

```bash
curl -X POST http://127.0.0.1:8000/run-deal   -H "Content-Type: application/json"   -d '{
    "customer_name": "Acme Retail Group",
    "customer_input_raw": "We need AI to improve support and recommendations quickly.",
    "industry": "retail",
    "company_size": "mid-market",
    "geo": "UAE",
    "currency": "AED"
  }'
```

## Docker

```bash
docker build -t ai-solutions-agency-os .
docker run --rm -p 8000:8000 --env-file .env ai-solutions-agency-os
```

## GitHub Actions

A basic CI workflow is included at `.github/workflows/ci.yml`. It:
- installs dependencies
- runs the starter in fake mode
- verifies the API imports
- builds the Docker image
