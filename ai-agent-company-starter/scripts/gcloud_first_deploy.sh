#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
REGION="${2:-us-central1}"
SERVICE_NAME="${3:-ai-agent-company-starter}"

if [[ -z "$PROJECT_ID" ]]; then
  echo "Usage: ./scripts/gcloud_first_deploy.sh <PROJECT_ID> [REGION] [SERVICE_NAME]"
  exit 1
fi

gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
gcloud run deploy "$SERVICE_NAME" --source . --region "$REGION" --allow-unauthenticated
