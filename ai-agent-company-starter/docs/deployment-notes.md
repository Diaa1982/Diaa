# Deployment Notes

## Recommended path
1. Validate locally.
2. Deploy once with `gcloud run deploy --source`.
3. Enable GitHub Actions deployment using Workload Identity Federation.
4. Push updates to `main` for repeatable releases.

## GitHub secrets required
- GCP_WORKLOAD_IDENTITY_PROVIDER
- GCP_SERVICE_ACCOUNT

## Environment variables
The current starter only requires:
- PORT (provided automatically by Cloud Run)

## Scaling defaults
See `cloudrun.yaml`:
- minScale: 0
- maxScale: 3
- cpu: 1
- memory: 512Mi
