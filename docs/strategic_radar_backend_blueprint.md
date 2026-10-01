# Governed Multi-Agent Strategic Radar - Backend Blueprint

## 1. Executive Summary

### Vision (Plain English)
Build a governed, evidence-first backend that continuously ingests *official* publications, detects strategic signals, scores materiality and confidence, and generates audience-specific recommendations (business and government) with mandatory human checkpoints for high-impact outputs.

### Architectural Style and Rationale
- **Style**: Event-driven modular microservices + workflow orchestration.
- **Why**:
  - Meets near-real-time alert requirements (6-24h critical window).
  - Supports strict governance with explicit approval gates.
  - Enables phased jurisdiction/industry expansion without monolith rewrites.
  - Preserves provenance through immutable event trails and evidence objects.

### Explicit Assumptions (for unresolved items)
1. **POC industries**: fintech, logistics/trade, healthcare/healthtech.
2. **First-wave jurisdictions**: US, UK, EU institutions, Singapore, UAE (plus IMF/OECD/World Bank packs).
3. **Source onboarding owner**: Governance Board (Policy Lead + Compliance Lead + Platform Admin).
4. **Confidence thresholds**: initial defaults in Section 10; tunable by policy.
5. **Launch outputs mandatory**: dashboard alerts + email alerts + weekly digest PDF + monthly strategy PDF.

---

## 2. Recommended Tech Stack

### Core Backend
- **Language**: Python 3.12 for AI/data workflows; Go for high-throughput ingestion edge (optional in POC).
- **Framework**: FastAPI (Python) for APIs; Pydantic v2 contracts.
- **Why**: Fast iteration, strong typing, async IO, broad OCR/NLP ecosystem.

### Data Stores
- **Relational DB**: PostgreSQL 16 (primary system of record).
- **Document store**: PostgreSQL JSONB in POC; MongoDB optional phase-2 for heavy semi-structured variants.
- **Search**: OpenSearch (full-text + faceted filters across documents/signals).
- **Vector store**: pgvector (POC); migrate to OpenSearch vector or Pinecone at scale.
- **Object storage**: S3-compatible bucket (raw docs, snapshots, rendered PDFs).
- **Event log**: Kafka (MSK/Confluent) for durable domain events.

### Messaging / Workflow
- **Queue semantics**: Kafka topics + retry topics + DLQ topics.
- **Workflow orchestration**: Temporal (strong for human-in-loop + retries + long-running approvals).
- **Scheduler**: Temporal schedules + cron-backed fallback.

### Ingestion / OCR / Parsing
- **Fetch**: Playwright (headless) + HTTP client for static feeds/APIs.
- **Document extraction**: Apache Tika + pdfplumber.
- **OCR**: Tesseract (POC), cloud OCR (AWS Textract / Azure Document Intelligence) for production quality.
- **Language detection/translation readiness**: fastText + translation API optional (ingestion only, output remains English).

### Auth / Security
- **Identity provider**: Keycloak (POC self-managed) or Auth0/Okta (enterprise).
- **AuthN/AuthZ**: OIDC + JWT; OPA (Open Policy Agent) for policy-as-code.
- **Service auth**: mTLS + SPIFFE/SPIRE (phase-2).

### Infrastructure
- **Container orchestration**: Kubernetes (EKS/AKS/GKE).
- **IaC**: Terraform + Helm.
- **Secrets/KMS**: Vault + cloud KMS.

### Observability
- **Metrics**: Prometheus + Grafana.
- **Logs**: OpenTelemetry collector + Loki/Elastic.
- **Tracing**: OpenTelemetry + Jaeger/Tempo.

### AI Integration Pattern
- **Pattern**: Tool-using LLM agents behind deterministic guardrails.
- **Provider**: Model gateway abstraction (OpenAI + fallback provider).
- **Controls**: Citation-required output schema, retrieval-grounded prompting, and post-generation verification.

### POC vs Future-Scale
- **POC**: FastAPI monorepo with modular services deployable as separate pods.
- **Future**: Split hot-path services (ingestion, evidence verification, alerting) into independently scaled deployments.

---

## 3. Backend Architecture

```text
[Clients/UI/API Consumers]
        |
   [API Gateway]
        |
+----------------------------- Control Plane -----------------------------+
| Identity & Access | Admin/Governance | Review/Approval | Audit Service |
+------------------------------------------------------------------------+
        |
+----------------------------- Data Plane --------------------------------+
| Source Registry -> Ingestion -> Fetchers/API Connectors -> Doc Proc    |
| -> OCR -> Normalization/Parsing -> Classification -> Signal Detection   |
| -> Materiality -> Evidence/Provenance -> Recommendation -> Rendering    |
| -> Alerting -> Reports -> Memory/Knowledge                              |
+------------------------------------------------------------------------+
        |
   [Kafka + Temporal + Postgres + OpenSearch + S3]
```

### Module Responsibilities, Inputs, Outputs, Failure Modes
1. **API Gateway**
   - Input: external API calls.
   - Output: routed authenticated requests.
   - Failure: auth failure, rate-limit breach, schema rejection.
2. **Identity and Access Service**
   - Manages users, roles, JWT claims, tenant scoping.
   - Failure: token expiry, role mismatch.
3. **Source Registry Service**
   - Stores source metadata (domain, owner, cadence, jurisdiction, allowed use).
   - Failure: duplicate source, unverifiable official status.
4. **Source Ingestion Service**
   - Creates ingestion jobs from schedules/manual triggers.
   - Failure: over-polling, quota breach, duplicate job dispatch.
5. **Crawler/Fetcher (whitelisted domains)**
   - Fetches HTML/PDF/attachments with robots/ToS controls.
   - Failure: 403, anti-bot, content drift, malformed pages.
6. **Feed/API Connector Service**
   - Ingests RSS/API payloads from official providers.
   - Failure: API contract drift, auth failure, stale feed.
7. **Document Processing Service**
   - Normalizes file formats, extracts text/metadata.
   - Failure: corrupt file, parser errors.
8. **OCR Pipeline**
   - OCR for scanned docs; stores confidence per block.
   - Failure: low OCR quality, language confusion.
9. **Normalization and Parsing Service**
   - Standard document schema; entity/date/jurisdiction extraction.
   - Failure: partial parse, date ambiguity.
10. **Taxonomy/Classification Service**
    - Assigns industry, jurisdiction, signal category labels.
    - Failure: low-confidence classification, multi-label conflict.
11. **Signal Detection Service**
    - Detects material events/changes from parsed docs and diffs.
    - Failure: duplicate signal, missed novelty.
12. **Materiality Scoring Service**
    - Scores impact, urgency, affected actors, regulatory weight.
    - Failure: unstable scoring due sparse evidence.
13. **Evidence/Provenance Service**
    - Links claims -> evidence spans; enforces citation validity.
    - Failure: broken citation pointers, hash mismatch.
14. **Recommendation Engine**
    - Drafts options and actions (never autonomous execution).
    - Failure: unsupported recommendation blocked by verifier.
15. **Audience Rendering Service**
    - Builds business-facing vs government-facing outputs.
    - Failure: wrong template for audience policy tier.
16. **Alerting/Notification Service**
    - Routes alerts via dashboard/email/webhooks.
    - Failure: delivery bounce, duplicate sends.
17. **Review & Approval Workflow Service**
    - Human checkpoints, SLA timers, escalation routing.
    - Failure: stuck approval, missing approver.
18. **Report Generation Service**
    - Weekly/monthly/quarterly PDFs with evidence appendix.
    - Failure: rendering errors, stale data windows.
19. **Memory/Knowledge Service**
    - Stores approved reusable insights; versioned trust states.
    - Failure: contradiction not resolved; unapproved promotion attempt.
20. **Audit/Compliance Logging Service**
    - Immutable append-only event stream for audits.
    - Failure: write lag; tamper detection alarm.
21. **Admin/Governance Service**
    - Policy config, threshold management, sensitive-topic controls.
    - Failure: policy conflict, unsafe configuration rejected.
22. **Scheduler/Orchestrator**
    - Owns end-to-end workflow state and retries.
    - Failure: orphan workflows; automatic rehydration from event log.

---

## 4. End-to-End Data Flow

### A) Source Approval Flow
1. Analyst submits source candidate with domain evidence.
2. Source Validation Agent pre-checks official status signals.
3. Governance workflow routes to approvers.
4. Approved source enters `source_registry` with status `APPROVED_PROD`.
5. Audit event written (`SOURCE_APPROVED`).

### B) Ingestion to Briefing Flow
1. Scheduler emits `IngestionRequested`.
2. Ingestion service creates idempotent job (`job_key = source_id + publication_id`).
3. Fetcher/API connector acquires content -> object store snapshot.
4. Parsing/OCR pipelines produce `parsed_document`.
5. Classification + signal detection produce candidate signals.
6. Materiality + confidence scoring assigns risk tier.
7. Evidence service binds every claim to evidence spans.
8. Recommendation engine drafts actions and implications.
9. Confidence/Risk agent gates: auto-publish vs review queue.
10. Approved alert distributed; report buffers updated.
11. Knowledge promotion only after explicit review workflow.

### Reliability Mechanics
- **Retries**: exponential backoff (e.g., 1m, 5m, 15m, 1h).
- **DLQ**: per-topic dead-letter with triage dashboard.
- **Idempotency**: dedupe keys by `source_doc_fingerprint` + workflow stage.
- **Backpressure**: consumer lag monitors; adaptive polling reduction; priority queues for critical sources.

---

## 5. Multi-Agent / Orchestration Design

### Orchestrator-Led Model
- Temporal workflow is the single controller.
- Agents are stateless workers invoked as deterministic activities where possible.
- No free-form agent-to-agent chat; handoffs only via typed contracts.

### Agent Roles and Boundaries
1. **Source Validation Agent**: validates official provenance metadata; cannot approve source autonomously.
2. **Extraction Agent**: extracts structured fields/spans from docs.
3. **Classification Agent**: industry/jurisdiction/category labels with confidence.
4. **Signal Interpretation Agent**: converts detected changes into implications.
5. **Recommendation Drafting Agent**: proposes options with rationale and prerequisites.
6. **Evidence Verification Agent**: blocks any claim lacking citation.
7. **Policy/Business Audience Adaptation Agent**: tailors tone/content by audience and risk policy.
8. **Confidence/Risk Agent**: computes publish tier and required approvals.
9. **Escalation/Review Agent**: routes to humans, enforces SLAs/escalations.

### Deterministic vs LLM
- **Deterministic mandatory**: source whitelist checks, citation existence, policy gates, approval routing, threshold logic.
- **LLM acceptable**: summarization, implication drafting, alternative action framing.
- **Hard anti-hallucination controls**:
  - output schema requires `claim_id -> evidence_ids[]`.
  - post-checker rejects orphan claims.
  - prompt includes “no evidence, no claim” rule.

---

## 6. Data Model and Storage Design

### Storage Placement
- **Postgres**: users, roles, sources, approvals, signals, recommendations, alerts, reports metadata, confidence scores.
- **S3**: raw files, HTML snapshots, OCR artifacts, rendered reports.
- **OpenSearch**: full-text search over parsed docs and signal summaries.
- **Vector (pgvector)**: embeddings for retrieval over approved evidence summaries only.
- **Kafka**: immutable event stream for workflow state transitions.

### Core Entity Sketch (selected)
```sql
CREATE TABLE sources (
  id UUID PRIMARY KEY,
  domain TEXT NOT NULL,
  source_name TEXT NOT NULL,
  source_type TEXT NOT NULL, -- api/rss/web/gazette
  jurisdiction_id UUID NOT NULL,
  official_status TEXT NOT NULL, -- pending/approved/rejected
  whitelist_pattern TEXT NOT NULL,
  cadence_minutes INT,
  created_at TIMESTAMPTZ NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_sources_jurisdiction_status ON sources(jurisdiction_id, official_status);

CREATE TABLE fetched_documents (
  id UUID PRIMARY KEY,
  source_id UUID NOT NULL,
  publication_url TEXT NOT NULL,
  published_at TIMESTAMPTZ,
  fetched_at TIMESTAMPTZ NOT NULL,
  content_hash TEXT NOT NULL,
  snapshot_uri TEXT NOT NULL,
  mime_type TEXT,
  UNIQUE(source_id, content_hash)
);

CREATE TABLE evidence_objects (
  id UUID PRIMARY KEY,
  fetched_document_id UUID NOT NULL,
  span_ref JSONB NOT NULL,
  evidence_type TEXT NOT NULL, -- fact/table/quote
  extraction_confidence NUMERIC(5,4) NOT NULL,
  signature_verified BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL
);

CREATE TABLE signals (
  id UUID PRIMARY KEY,
  jurisdiction_id UUID NOT NULL,
  industry_id UUID NOT NULL,
  category_id UUID NOT NULL,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  status TEXT NOT NULL, -- draft/reviewed/published/blocked
  materiality_score NUMERIC(5,2) NOT NULL,
  confidence_score NUMERIC(5,2) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL
);
CREATE INDEX idx_signals_filters ON signals(jurisdiction_id, industry_id, category_id, created_at DESC);
```

### Versioning and Lineage
- `version_no` on parsed docs, signals, recommendations.
- `supersedes_id` for corrections.
- Lineage graph edges: document -> evidence -> claim -> recommendation -> alert/report.

---

## 7. Provenance, Traceability, and Evidence Controls

### Provenance Design
- Every claim must include:
  - source ID, document ID, evidence span offsets, retrieval timestamp, hash.
- Evidence ledger is append-only with immutable IDs.

### Fact vs Interpretation vs Recommendation
- `statement_type` enum: `FACT`, `INTERPRETATION`, `RECOMMENDATION`.
- FACT requires direct evidence objects.
- INTERPRETATION requires >=1 fact references.
- RECOMMENDATION requires >=1 interpretation + policy disclaimer.

### Citation Integrity Rules
1. Citation domain must match approved whitelist.
2. Evidence span must exist in stored snapshot.
3. Hash of cited snapshot must match original capture hash.
4. Broken citations force `BLOCKED_OUTPUT` state.

### Evidence Confidence Computation
`evidence_conf = 0.35*source_trust + 0.25*extraction_quality + 0.20*recency + 0.20*cross_source_consistency`

### Preservation for Audit/Replay
- Keep raw snapshot + parsed output + model prompt/response metadata (without sensitive secrets).
- RFC3161 timestamp or cloud signing service for evidence packages.
- WORM/object lock for compliance bucket.

---

## 8. API Design

### API Style
- REST for operational endpoints.
- Webhooks + event streams for downstream systems.

### Representative Endpoints
- `POST /v1/auth/token`
- `POST /v1/sources`
- `POST /v1/sources/{id}/approve`
- `POST /v1/ingestion/trigger`
- `GET /v1/signals`
- `GET /v1/signals/{id}`
- `POST /v1/alerts/{id}/publish`
- `GET /v1/recommendations`
- `POST /v1/reports/generate`
- `POST /v1/approvals/{workflowId}/decision`
- `PUT /v1/admin/policies/confidence-thresholds`
- `POST /v1/feedback`
- `GET /v1/metrics/quality`

### Example: Source Onboarding Request
```json
{
  "source_name": "Monetary Authority Gazette",
  "domain": "mas.gov.sg",
  "source_type": "web",
  "jurisdiction": "SG",
  "official_evidence": ["https://www.mas.gov.sg/..."],
  "requested_by": "user_123"
}
```

### Example: Signal Response
```json
{
  "signal_id": "sig_789",
  "title": "New fintech licensing circular",
  "category": "regulatory_change",
  "materiality_score": 84.2,
  "confidence_score": 88.5,
  "statements": [
    {"type": "FACT", "text": "...", "evidence_ids": ["ev_1", "ev_2"]},
    {"type": "INTERPRETATION", "text": "...", "evidence_ids": ["ev_1"]},
    {"type": "RECOMMENDATION", "text": "...", "evidence_ids": ["ev_1"]}
  ],
  "review_state": "ANALYST_REVIEW_REQUIRED"
}
```

### API Controls
- Pagination: cursor-based (`next_cursor`).
- Filtering: jurisdiction, industry, category, risk tier, date range.
- RBAC enforced per endpoint.
- Rate limits: per user + per tenant + per endpoint class.
- Idempotency keys required on mutating endpoints.

### Webhooks
- `signal.published`, `alert.sent`, `approval.required`, `report.generated`.

---

## 9. Security, Privacy, and Governance

### Access Model
- RBAC baseline: Admin, Governance Reviewer, Analyst, Executive Reader, API Client.
- ABAC overlays: jurisdiction sensitivity, industry scope, clearance level.

### Tenant Isolation (assumption)
- Logical multi-tenancy with tenant_id row-level security in POC.
- Option for physical isolation (separate DB/schema) for government high-sensitivity tenants.

### Security Controls
- TLS 1.2+, mTLS internal.
- AES-256 at rest via KMS.
- Secrets in Vault with short-lived tokens.
- Private subnets; WAF on ingress; admin IP allowlisting + MFA.
- Service-to-service auth with workload identity.

### Data Governance
- Retention: raw docs 7 years (configurable), working artifacts 2 years, logs 1 year hot + archive.
- Deletion: policy-driven purge jobs + legal hold override.
- PII posture: avoid ingestion where possible; detect/redact if present.

### Sensitive Topic Governance
- Mandatory dual-review for defense/sanctions/politically sensitive outputs.
- Jurisdiction-sensitive rules in OPA policies.

### Zero-Trust Defaults
- Deny-by-default network and authorization.
- Least-privilege IAM and scoped tokens.

---

## 10. Quality, Confidence, and Risk Controls

### Confidence Methodology
`overall_conf = 0.40*evidence_conf + 0.25*classification_conf + 0.20*materiality_model_stability + 0.15*cross_source_support`

### Thresholds (initial recommendation)
- **>= 85**: Auto-publish allowed *only* for non-sensitive, non-executive alerts.
- **70-84.99**: Analyst review mandatory.
- **50-69.99**: Executive escalation only with explicit caveats.
- **< 50**: Blocked output.

### False-Positive Reduction
- Duplicate clustering.
- Novelty checks against prior signals.
- Mandatory corroboration for high-impact claims.

### Evidence Sufficiency Checks
- Min evidence objects per material claim: 2 (or 1 if primary legal text).
- Evidence freshness rules by category.

### Anti-Hallucination Controls
- Structured generation with citations.
- Citation resolver verifies span existence.
- LLM output rejected if unsupported.

### Weak/Conflicting Evidence Fallback
- Output status: `INSUFFICIENT_EVIDENCE` with monitoring recommendation only.
- Conflicts trigger `EVIDENCE_CONFLICT_REVIEW` workflow.

---

## 11. Search, Retrieval, and Knowledge Memory

### Session vs Persistent Memory
- **Session memory**: workflow-local context for current run; expires after completion.
- **Persistent memory**: approved knowledge objects reusable across runs.

### Trusted Memory Promotion
- Draft knowledge object -> reviewer approval -> trusted memory index.
- No auto-promotion for policy-sensitive insights.

### Retrieval Strategy
- Hybrid retrieval: filter-first (jurisdiction/industry/date), then lexical + vector blend.
- Sources queried: official docs, prior signals, prior approvals, prior recommendations.

### Vector DB Storage Rules
- Store: sanitized summaries + evidence pointers.
- Do not store: raw confidential docs, unsupported interpretations, rejected outputs.

### Memory Lifecycle
- Expiration policy by category (e.g., regulation 24 months unless superseded).
- Contradiction detector flags stale memory and downgrades trust.

---

## 12. Scheduling and Coverage Strategy

### Pipeline Cadence
- Near-real-time: every 15-60 min for critical regulators.
- Daily: normal sources.
- Weekly/monthly/quarterly: digest and outlook generation.

### Polling by Source Type
- APIs: high-frequency with ETag/If-Modified-Since.
- RSS: moderate polling + dedupe.
- Web pages: change-detection diff snapshots with politeness controls.
- Statistical portals: cadence aligned to release calendar.

### Jurisdiction Pack Model
- Pack includes source list, legal sensitivity tags, taxonomy mappings, approval policy profile.

### First-Wave Rollout (worldwide by design)
- Wave 1: Global institutions + 5 jurisdictions + 3 industries.
- Wave 2: add 10 jurisdictions with reusable pack templates.
- Wave 3: regional expansion by demand.

### Freshness SLAs
- Critical source ingestion lag < 2h.
- Critical signal publication < 24h.
- Normal signal publication < 48h.

---

## 13. Reporting and Delivery

### Delivery Channels
- Dashboard feed API (live signals).
- Email alert templates by risk tier.
- PDF executive briefings with evidence appendix.

### Reporting Cadence
- Weekly digest: top signals, implications, actions.
- Monthly strategy update: trend synthesis + KPI hypotheses.
- Quarterly outlook: scenario implications + sector direction.

### Rendering Pipeline
1. Pull approved signals/recommendations.
2. Apply audience template (business/government).
3. Attach confidence + citations table.
4. Render HTML->PDF.
5. Store artifact + delivery receipt.

### Delivery Auditability
- Track send status, recipient scope, timestamp, report hash.
- Immutable delivery receipt for compliance.

---

## 14. Observability and Operations

### Telemetry
- Structured logs with correlation IDs.
- Distributed traces across workflow stages.
- Metrics per service and per source pack.

### Core SLOs
- Ingestion success rate >= 99% (approved sources).
- Citation integrity >= 99.9%.
- Critical alert latency p95 <= 24h from publication.

### Operational Dashboards
- Source health and outage map.
- Workflow backlog/stuck approvals.
- Model extraction confidence drift.
- Alert relevance/false-positive trend.

### Alerts/Runbooks
- Stuck workflow > SLA -> escalate to operations.
- Source outage > threshold -> switch to degraded mode notice.
- Citation check failure -> auto-block + incident ticket.

---

## 15. Testing and Validation Strategy

### Test Layers
- Unit: parsers, scorers, policy evaluators.
- Integration: service-to-service, DB/search/object storage.
- Contract: API schemas and event contracts.
- E2E: source -> alert/report path.
- Security: SAST/DAST, dependency scans, authZ tests.
- Performance: ingestion throughput + query latency.
- Resilience: chaos tests on queue/db/network disruptions.
- HITL: approval workflow timing/escalation correctness.

### Dataset-Based Evaluation
- Labeled corpora for classification/materiality.
- Citation correctness benchmark (span-level).
- Recommendation usefulness scoring by analyst rubric.

### Adversarial Tests
- Hallucination bait prompts.
- OCR noise and poor scan quality.
- Ambiguous legal wording.
- Duplicate or conflicting official releases.

### UAT Criteria
- Executives: concise briefs, clear confidence, no broken citations.
- Analysts: controllable filters, explainable evidence chain.

---

## 16. DevOps and Deployment

### CI/CD
- Stages: lint -> unit -> integration -> security -> build -> deploy.
- Signed artifacts + SBOM required.

### Environments
- Local: docker compose.
- Dev: shared cluster, synthetic data.
- Staging: production-like with masked real docs.
- Production: hardened, isolated, monitored.

### Deployment Strategy
- Blue/green for API and workflow services.
- Canary for model/prompt changes with shadow evaluation.

### Data Operations
- DB migrations via Alembic with backward-compatible phases.
- Secrets rotation every 90 days or on incident.
- Backups: PITR for Postgres, cross-region snapshot for object store.

### DR Targets
- RPO: 15 minutes.
- RTO: 2 hours for core alerting path.

### Cost Awareness
- POC: managed Postgres + small Kafka + on-demand OCR.
- Production: autoscaling workers, tiered storage, compute quotas by source criticality.

---

## 17. Implementation Roadmap

### Phase 1: Architecture Foundation
- **Objectives**: secure platform skeleton and core contracts.
- **Deliverables**: gateway, auth, base schemas, event bus, orchestration skeleton.
- **Dependencies**: cloud account, IAM, networking.
- **Risks**: policy ambiguity.
- **Acceptance**: authenticated API + traceable workflow hello-world.

### Phase 2: Ingestion and Source Governance
- **Objectives**: approved-source-only intake.
- **Deliverables**: source registry, onboarding workflow, fetchers/connectors.
- **Dependencies**: governance committee decisions.
- **Risks**: source variability.
- **Acceptance**: approved source pack live with audit trail.

### Phase 3: Document Processing and Evidence Services
- **Objectives**: robust parsing/OCR/provenance.
- **Deliverables**: doc pipeline, evidence ledger, citation validator.
- **Dependencies**: object storage + OCR infra.
- **Risks**: poor OCR quality.
- **Acceptance**: end-to-end claim-to-evidence traceability.

### Phase 4: Signal Detection and Recommendation Workflows
- **Objectives**: produce high-quality prioritized outputs.
- **Deliverables**: classification, materiality, recommendation engine.
- **Dependencies**: labeled data and taxonomy.
- **Risks**: false positives.
- **Acceptance**: target precision for high-priority alerts met.

### Phase 5: Human Review and Alerting
- **Objectives**: governance gates and delivery.
- **Deliverables**: approval workflows, escalation rules, alert channels.
- **Dependencies**: reviewer roles/SLAs.
- **Risks**: review bottlenecks.
- **Acceptance**: high-impact outputs cannot bypass review.

### Phase 6: Reporting and Observability
- **Objectives**: executive-grade recurring outputs + operational controls.
- **Deliverables**: digest/report engine, dashboards, SLO alerts.
- **Dependencies**: template sign-off.
- **Risks**: rendering quality.
- **Acceptance**: weekly/monthly reports generated with valid citations.

### Phase 7: Hardening and Launch Readiness
- **Objectives**: production security, resilience, runbooks.
- **Deliverables**: DR drills, penetration test closure, final go-live checklist.
- **Dependencies**: security and governance approvals.
- **Risks**: unresolved sensitive-topic policies.
- **Acceptance**: go/no-go criteria all green.

---

## 18. Recommended Enhancements Beyond the Baseline

### POC-Essential
- Policy-as-code approvals (OPA).
- Duplicate notice clustering.
- Change detection on official pages.
- Analyst annotation layer.
- Executive-safe summary guardrails.

### Phase-2 Recommended
- Source trust scoring with dynamic calibration.
- Multilingual ingestion readiness (English output preserved).
- Explainability ledger UI.
- Evidence conflict resolution assistant.
- Scenario template library.
- Recommendation quality feedback loops.
- Jurisdiction-sensitive rules engine expansion.

---

## 19. Key Risks and Mitigations

1. **Unofficial source contamination** -> strict whitelist + approval workflow + runtime domain enforcement.
2. **Hallucinated citations** -> schema-enforced citations + verifier block + red-team tests.
3. **False executive alerts** -> higher thresholds + mandatory human review for high impact.
4. **OCR/extraction errors** -> confidence gating + manual validation queues for low-quality scans.
5. **Policy sensitivity mishandling** -> sensitive-topic tags + dual approvals + legal/compliance review.
6. **Workflow bottlenecks** -> SLA escalations, backup approver pools, queue prioritization.
7. **Data breaches** -> zero-trust network, encryption, least privilege, continuous audits.
8. **Model drift** -> ongoing eval datasets, canary releases, rollback strategy.
9. **Jurisdiction expansion complexity** -> reusable source pack templates and staged rollout.
10. **Audit failure** -> immutable logs, signed artifacts, periodic replay drills.

---

## 20. Final Recommended Blueprint

### Recommended Target Architecture
A Kubernetes-hosted, event-driven, orchestrator-led backend with strict source governance, evidence ledger, deterministic policy gates, and human-in-loop approvals, delivering traceable alerts/reports for business and government audiences.

### Top 10 Engineering Priorities
1. Source registry + approval pipeline.
2. Immutable evidence/provenance ledger.
3. Reliable ingestion connectors and fetchers.
4. OCR/parsing quality pipeline with confidence metrics.
5. Classification + materiality services.
6. Recommendation engine with citation constraints.
7. Human review workflow and escalation.
8. Alert/report rendering and delivery receipts.
9. Observability with citation integrity monitoring.
10. Disaster recovery and rollback mechanisms.

### Top 10 Governance Priorities
1. Source eligibility policy and ownership.
2. Sensitive-topic handling matrix.
3. Confidence threshold governance.
4. High-impact output approval policy.
5. Trusted memory promotion policy.
6. Role and clearance model.
7. Retention/deletion/legal hold policy.
8. Policy-as-code change control.
9. Audit readiness and evidence replay SOP.
10. Executive distribution rules for low-confidence outputs.

### Top 10 Launch Blockers to Resolve Before Production
1. Final first-wave jurisdictions.
2. Final three launch industries.
3. Formal source onboarding approver RACI.
4. Confidence thresholds per audience/risk tier.
5. Mandatory launch output formats.
6. Sensitive-domain escalation contacts and SLAs.
7. Legal/compliance sign-off on disclaimers.
8. Citation integrity SLO acceptance.
9. DR test pass against RPO/RTO targets.
10. UAT acceptance from analysts and executives.
