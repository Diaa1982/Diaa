# Technical Specification

## Zero-cost technical stack
- Python 3.12
- FastAPI
- PostgreSQL
- OpenSearch
- MinIO
- NATS JetStream
- Temporal OSS
- Keycloak OSS
- OPA
- Apache Tika
- Tesseract + OCRmyPDF
- OpenTelemetry + Prometheus + Grafana + Loki
- Kubernetes
- NGINX Ingress
- SQLAlchemy 2.x
- Alembic
- Pydantic v2

## API standard
- base path: /api/v1
- JSON only
- UUID identifiers
- UTC timestamps
- request and response correlation IDs
- idempotency keys for mutating operations with side effects

## Core endpoints
- GET /me
- POST /sources
- GET /sources
- GET /sources/{source_id}
- PATCH /sources/{source_id}
- POST /source-approvals/{source_id}/decision
- POST /ingestion/run
- GET /documents/fetched
- GET /documents/parsed/{parsed_document_id}
- GET /signals
- GET /signals/{signal_id}
- GET /recommendations/{recommendation_id}
- GET /approvals/inbox
- POST /approvals/{workflow_record_id}/decision
- POST /reports
- GET /reports
- GET /reports/{report_id}
- GET /knowledge
- POST /feedback
- GET /metrics/operational

## Mandatory controls
- no approved output without evidence-linked fact claims
- no source ingestion without approval
- no recommendation publish without citation integrity pass
- no sensitive government-facing recommendation without human review
- no memory promotion without approval completion

## Storage split
### PostgreSQL
- users, roles, sources, approvals, documents metadata, signals, recommendations, workflows, audit refs, delivery receipts

### OpenSearch
- document chunks, evidence search, signal search, approved knowledge retrieval

### MinIO
- raw snapshots, OCR derivatives, report artifacts, audit bundles

## Build order
1. source registry
2. approvals
3. ingestion
4. parsing / OCR
5. evidence model
6. signal engine
7. recommendation and confidence layer
8. reporting and alerts
