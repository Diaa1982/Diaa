# AI Agent Company Platform

A more complete production-style scaffold for an agent operating model repository.

## What this includes
- FastAPI backend with versioned API routes
- Admin UI for browsing agents, reviewing prompts, editing prompts, and running executions
- Agent execution endpoints with execution history
- Environment-based configuration via `.env`
- SQLite-backed execution persistence
- Existing agent manifest and prompt files preserved as editable assets
- Docker and Cloud Run-ready packaging

## Core capabilities
- Browse manifest and agents
- View full agent prompts and metadata
- Update prompts from the admin UI or API when `ADMIN_WRITE_ENABLED=true`
- Execute an agent in one of these modes:
  - `mock`: deterministic scaffolded output for testing the workflow
  - `prompt_only`: returns the assembled prompt package without calling a model
  - `openai_compatible`: calls a compatible chat-completions endpoint when environment variables are configured
- Persist execution history for audit and review

## Quick start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8080
```

Then open:
- `http://localhost:8080/admin`
- `http://localhost:8080/api/v1/docs`

## Environment variables
See `.env.example`.

Important settings:
- `DEFAULT_EXECUTION_MODE`
- `LLM_PROVIDER`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
- `ADMIN_WRITE_ENABLED`
- `DATABASE_URL`

## Execution modes
### mock
Use this for local validation and workflow testing. It generates structured placeholder outputs without calling an external model.

### prompt_only
Returns the assembled instruction package for the selected agent so you can inspect what would be sent to a model.

### openai_compatible
Sends the assembled system and user prompt to a compatible chat completions API.

Expected variables:
- `LLM_PROVIDER=openai_compatible`
- `LLM_BASE_URL=https://...`
- `LLM_API_KEY=...`
- `LLM_MODEL=...`

## API overview
- `GET /api/v1/health`
- `GET /api/v1/config/public`
- `GET /api/v1/manifest`
- `GET /api/v1/agents`
- `GET /api/v1/agents/{agent_id}`
- `PUT /api/v1/agents/{agent_id}/prompt`
- `POST /api/v1/executions`
- `GET /api/v1/executions`
- `GET /api/v1/executions/{execution_id}`
- `POST /api/v1/executions/{execution_id}/retry`

## Deployment notes
This app is safe to deploy in `mock` mode first. Once the runtime is stable, configure `openai_compatible` mode through environment variables and secrets.

## Deployment gap assessment (current repository state)
### Already implemented
- FastAPI app entrypoint at `app.main:app`.
- Health endpoint at `GET /api/v1/health`.
- Dockerfile for containerized runtime.
- Cloud Run service manifest (`cloudrun.yaml`).
- Initial helper scripts under `scripts/`.

### Missing for local run (fixed)
- `.env.example` was missing but referenced by `scripts/local_run.sh`.
- `docker-compose.yml` was missing for one-command local container run.

### Missing for deployment (fixed)
- Basic CI workflow for dependency install, import validation, app startup + health check, and image build.
- Expanded deployment instructions and explicit required env vars/secrets.

### Unsafe or inconsistent (fixed)
- CORS settings were defined in config but not applied in app middleware.
- Default operational guidance did not include explicit smoke validation commands.

## Local deployment-ready runbook
1. **Create env file**
   ```bash
   cp .env.example .env
   ```
2. **Run with Python**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8080
   ```
3. **Run with Docker Compose**
   ```bash
   cp .env.example .env
   docker compose up --build
   ```
4. **Smoke checks**
   ```bash
   curl -sS http://localhost:8080/api/v1/health
   curl -sS http://localhost:8080/api/v1/config/public
   curl -sS http://localhost:8080/api/v1/agents
   ```

## Cloud Run deployment (dev)
### Prerequisites
- Authenticated `gcloud` CLI.
- A GCP project with billing enabled.
- Artifact Registry and Cloud Run API access.

### Quick deploy command
```bash
./scripts/gcloud_first_deploy.sh <PROJECT_ID> [REGION] [SERVICE_NAME]
```

### Suggested runtime env vars
- `APP_ENV=dev`
- `DEBUG=false`
- `ADMIN_ENABLED=true`
- `ADMIN_WRITE_ENABLED=false`
- `DEFAULT_EXECUTION_MODE=mock` (or `openai_compatible`)
- `DATABASE_URL=sqlite:////tmp/agent_platform_data/executions.db`

### Secrets required when using `openai_compatible`
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`
