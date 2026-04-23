create extension if not exists pgcrypto;
create extension if not exists "uuid-ossp";

create table organizations (
  org_id uuid primary key default gen_random_uuid(),
  org_name text not null,
  org_code text unique,
  status text not null default 'active' check (status in ('active','inactive')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table jurisdictions (
  jurisdiction_id uuid primary key default gen_random_uuid(),
  jurisdiction_code text not null unique,
  jurisdiction_name text not null,
  parent_jurisdiction_id uuid references jurisdictions(jurisdiction_id),
  jurisdiction_type text not null check (jurisdiction_type in ('global','multilateral','country','subnational','regional')),
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table industries (
  industry_id uuid primary key default gen_random_uuid(),
  industry_code text not null unique,
  industry_name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table users (
  user_id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(org_id),
  auth_subject text not null unique,
  email text not null unique,
  display_name text not null,
  status text not null default 'active' check (status in ('active','suspended','disabled')),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table roles (
  role_id uuid primary key default gen_random_uuid(),
  role_name text not null unique,
  description text,
  created_at timestamptz not null default now()
);

create table user_roles (
  user_id uuid not null references users(user_id) on delete cascade,
  role_id uuid not null references roles(role_id) on delete cascade,
  assigned_at timestamptz not null default now(),
  assigned_by uuid references users(user_id),
  primary key (user_id, role_id)
);

create table sources (
  source_id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(org_id),
  source_name text not null,
  canonical_org_name text,
  base_domain text not null,
  jurisdiction_id uuid not null references jurisdictions(jurisdiction_id),
  source_type text not null check (
    source_type in ('rss','api','web','filing','gazette','statistics','procurement','exchange')
  ),
  officiality_class text not null check (
    officiality_class in ('official','official_attributable','licensed_official_lineage')
  ),
  status text not null default 'draft' check (
    status in ('draft','pending_validation','pending_review','approved_active','suspended','retired','rejected')
  ),
  polling_profile jsonb not null default '{}'::jsonb,
  parser_profile jsonb not null default '{}'::jsonb,
  sensitivity_profile jsonb not null default '{}'::jsonb,
  notes text,
  created_by uuid references users(user_id),
  updated_by uuid references users(user_id),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index idx_sources_status on sources(status);
create index idx_sources_jurisdiction on sources(jurisdiction_id);
create index idx_sources_base_domain on sources(base_domain);

create table source_approval_records (
  approval_id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(source_id) on delete cascade,
  decision text not null check (decision in ('approved','rejected','suspended','reactivated')),
  decision_reason text,
  submitted_by uuid references users(user_id),
  decided_by uuid references users(user_id),
  evidence jsonb not null default '{}'::jsonb,
  effective_from timestamptz,
  effective_to timestamptz,
  created_at timestamptz not null default now()
);

create table fetched_documents (
  fetched_document_id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(source_id),
  fetch_url text not null,
  canonical_url text not null,
  http_status integer,
  fetched_at timestamptz not null default now(),
  publication_at timestamptz,
  content_type text,
  content_length bigint,
  content_hash text not null,
  raw_object_uri text not null,
  snapshot_object_uri text not null,
  signature_detected boolean not null default false,
  fetch_metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  unique (source_id, canonical_url, content_hash)
);

create table parsed_documents (
  parsed_document_id uuid primary key default gen_random_uuid(),
  fetched_document_id uuid not null unique references fetched_documents(fetched_document_id) on delete cascade,
  title text,
  issuing_body text,
  doc_type text,
  language_code text,
  parser_version text not null,
  ocr_required boolean not null default false,
  parse_quality_score numeric(5,4),
  structure jsonb not null default '{}'::jsonb,
  publication_at timestamptz,
  created_at timestamptz not null default now()
);

create table evidence_objects (
  evidence_object_id uuid primary key default gen_random_uuid(),
  parsed_document_id uuid not null references parsed_documents(parsed_document_id) on delete cascade,
  chunk_id text not null,
  page_no integer,
  span_start integer,
  span_end integer,
  evidence_type text not null check (evidence_type in ('text','table','figure','metadata')),
  normalized_text text not null,
  evidence_hash text not null,
  source_confidence numeric(5,4),
  extraction_confidence numeric(5,4),
  preserved_object_uri text,
  created_at timestamptz not null default now(),
  unique (parsed_document_id, chunk_id)
);

create table signal_categories (
  signal_category_id uuid primary key default gen_random_uuid(),
  category_code text not null unique,
  category_name text not null,
  is_active boolean not null default true,
  created_at timestamptz not null default now()
);

create table signals (
  signal_id uuid primary key default gen_random_uuid(),
  org_id uuid references organizations(org_id),
  jurisdiction_id uuid not null references jurisdictions(jurisdiction_id),
  industry_id uuid not null references industries(industry_id),
  signal_category_id uuid not null references signal_categories(signal_category_id),
  title text not null,
  signal_status text not null check (
    signal_status in (
      'discovered','parsed','classified','drafted','evidence_bound','confidence_evaluated',
      'review_required','auto_publishable','approved','published','blocked','superseded'
    )
  ),
  novelty_score numeric(5,4),
  materiality_band text check (materiality_band in ('low','medium','high','critical')),
  urgency_band text check (urgency_band in ('routine','elevated','urgent','immediate')),
  summary_fact text,
  source_document_count integer not null default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table recommendations (
  recommendation_id uuid primary key default gen_random_uuid(),
  signal_id uuid not null references signals(signal_id) on delete cascade,
  audience_type text not null check (audience_type in ('business','government')),
  recommendation_status text not null check (
    recommendation_status in ('draft','review_required','approved','rejected','published','blocked')
  ),
  fact_block jsonb not null default '[]'::jsonb,
  interpretation_block jsonb not null default '[]'::jsonb,
  recommendation_block jsonb not null default '[]'::jsonb,
  caveats jsonb not null default '[]'::jsonb,
  constraints_block jsonb not null default '[]'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table approval_workflows (
  workflow_record_id uuid primary key default gen_random_uuid(),
  entity_type text not null check (entity_type in ('source','signal','recommendation','report','knowledge')),
  entity_id uuid not null,
  state text not null check (
    state in ('queued','in_review','returned_for_rework','escalated','approved','rejected','expired')
  ),
  assigned_to uuid references users(user_id),
  sla_due_at timestamptz,
  policy_snapshot jsonb not null default '{}'::jsonb,
  started_at timestamptz not null default now(),
  completed_at timestamptz
);

create table reports (
  report_id uuid primary key default gen_random_uuid(),
  report_type text not null check (
    report_type in ('signal_brief','weekly_digest','monthly_strategy_update','quarterly_sector_outlook')
  ),
  audience_type text not null check (audience_type in ('business','government','executive_internal')),
  period_start date,
  period_end date,
  status text not null check (status in ('draft','review_required','approved','rendered','delivered','failed')),
  artifact_uri text,
  artifact_hash text,
  render_input_hash text,
  created_by uuid references users(user_id),
  created_at timestamptz not null default now()
);

create table knowledge_objects (
  knowledge_object_id uuid primary key default gen_random_uuid(),
  object_type text not null check (
    object_type in ('approved_pattern','source_note','scenario_template','approved_interpretation','approved_recommendation')
  ),
  title text not null,
  content jsonb not null,
  approval_workflow_id uuid references approval_workflows(workflow_record_id),
  status text not null check (status in ('candidate','approved','superseded','expired','rejected')),
  valid_from timestamptz not null default now(),
  valid_to timestamptz,
  supersedes_id uuid references knowledge_objects(knowledge_object_id),
  created_at timestamptz not null default now()
);

create table audit_events (
  audit_event_id uuid primary key default gen_random_uuid(),
  occurred_at timestamptz not null default now(),
  actor_type text not null check (actor_type in ('user','service','workflow','system')),
  actor_id text not null,
  action_type text not null,
  entity_type text not null,
  entity_id text not null,
  request_id text,
  event_payload jsonb not null default '{}'::jsonb,
  hash_prev text,
  hash_self text not null
);

create table delivery_receipts (
  delivery_receipt_id uuid primary key default gen_random_uuid(),
  entity_type text not null check (entity_type in ('alert','digest','report')),
  entity_id uuid not null,
  channel text not null check (channel in ('email','dashboard','webhook','download')),
  recipient text,
  delivery_status text not null check (delivery_status in ('queued','sent','delivered','opened','clicked','failed')),
  provider_message_id text,
  created_at timestamptz not null default now(),
  delivered_at timestamptz
);
