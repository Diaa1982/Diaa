#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${1:-}"
PROJECT_NUMBER="${2:-}"
GITHUB_ORG="${3:-}"
REPO_NAME="${4:-}"
SERVICE_ACCOUNT_NAME="${5:-github-cloud-run-deployer}"

if [[ -z "$PROJECT_ID" || -z "$PROJECT_NUMBER" || -z "$GITHUB_ORG" || -z "$REPO_NAME" ]]; then
  echo "Usage: ./scripts/setup_github_wif.sh <PROJECT_ID> <PROJECT_NUMBER> <GITHUB_ORG> <REPO_NAME> [SERVICE_ACCOUNT_NAME]"
  exit 1
fi

gcloud iam service-accounts create "$SERVICE_ACCOUNT_NAME" --project "$PROJECT_ID" || true

gcloud projects add-iam-policy-binding "$PROJECT_ID"   --member "serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"   --role "roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID"   --member "serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"   --role "roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding "$PROJECT_ID"   --member "serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"   --role "roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding "$PROJECT_ID"   --member "serviceAccount:${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"   --role "roles/iam.serviceAccountUser"

gcloud iam workload-identity-pools create "github"   --project="${PROJECT_ID}"   --location="global"   --display-name="GitHub Actions Pool" || true

gcloud iam workload-identity-pools providers create-oidc "repo-provider"   --project="${PROJECT_ID}"   --location="global"   --workload-identity-pool="github"   --display-name="GitHub OIDC Provider"   --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner"   --attribute-condition="assertion.repository=='${GITHUB_ORG}/${REPO_NAME}'"   --issuer-uri="https://token.actions.githubusercontent.com" || true

POOL_NAME=$(gcloud iam workload-identity-pools describe github   --project="${PROJECT_ID}"   --location="global"   --format="value(name)")

gcloud iam service-accounts add-iam-policy-binding   "${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"   --project="${PROJECT_ID}"   --role="roles/iam.workloadIdentityUser"   --member="principalSet://iam.googleapis.com/${POOL_NAME}/attribute.repository/${GITHUB_ORG}/${REPO_NAME}"

echo ""
echo "Add these GitHub repository secrets:"
echo "GCP_WORKLOAD_IDENTITY_PROVIDER=projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/github/providers/repo-provider"
echo "GCP_SERVICE_ACCOUNT=${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
