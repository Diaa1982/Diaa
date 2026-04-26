#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
SERVICE_NAME="${3:-ai-agent-company-starter}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./scripts/gcloud_first_deploy.sh <PROJECT_ID> [REGION] [SERVICE_NAME]"
  exit 1
fi

if ! command -v gcloud >/dev/null 2>&1; then
  echo "gcloud CLI is required but was not found in PATH."
  exit 1
fi

gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --allow-unauthenticated \
  --set-env-vars APP_ENV=dev,DEBUG=false,ADMIN_ENABLED=true,ADMIN_WRITE_ENABLED=false,DEFAULT_EXECUTION_MODE=mock,DATABASE_URL=sqlite:////tmp/agent_platform_data/executions.db
