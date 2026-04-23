# Solution Architecture

## Architecture style
Event-driven modular backend with durable orchestration and strict provenance controls.

## Service boundaries
### Control plane
- source registry
- approvals
- governance
- taxonomy administration
- IAM
- policy engine

### Data plane
- fetchers
- connectors
- raw snapshot storage
- OCR
- parsing
- evidence generation
- search indexing

### Reasoning plane
- classification
- signal detection
- materiality scoring
- recommendation drafting
- confidence evaluation

### Delivery plane
- alerts
- digests
- reports
- dashboard feeds
- audit exports

## Sequence summary
1. Source proposed
2. Source validated and approved
3. Scheduler issues ingestion jobs
4. Fetcher stores raw source snapshot
5. Document processor extracts text or OCR derivative
6. Parser normalizes content into canonical structure
7. Taxonomy assigns jurisdiction / industry / category
8. Signal engine detects material event
9. Evidence service binds claims to evidence objects
10. Recommendation service drafts bounded outputs
11. Confidence engine evaluates routing threshold
12. Workflow routes to auto-publish or human review
13. Renderer creates alert/report artifacts
14. Notification service distributes approved outputs
15. Audit service stores immutable event history

## Core workflows
- source_approval_workflow
- source_poll_workflow
- document_ingestion_workflow
- signal_pipeline_workflow
- approval_workflow
- report_generation_workflow
- knowledge_promotion_workflow

## Failure handling
- retries with exponential backoff
- dead-letter queues by event class
- idempotency on all external side-effect endpoints
- source health degradation flags
- blocked publish on evidence integrity failure

## Recommended repository usage
- use this file for service ownership, workflow design, state machines, and backlog planning
