-- Playbook Library Blueprint Schema (PostgreSQL)
-- Purpose: document ingestion -> conversion -> structured playbook -> quality gate -> retrieval/chat

create extension if not exists vector;

create table if not exists documents (
  id uuid primary key,
  tenant_id uuid not null,
  file_name text not null,
  file_ext text not null,
  mime_type text,
  file_size bigint not null,
  sha256 char(64) not null,
  storage_url text not null,
  source_url text,
  uploaded_by text not null,
  uploaded_at timestamptz not null default now(),
  status text not null check (status in ('uploaded','converted','structured','rejected','published')),
  unique (tenant_id, sha256)
);

create index if not exists idx_documents_tenant_status on documents(tenant_id, status);

create table if not exists conversions (
  id uuid primary key,
  document_id uuid not null references documents(id) on delete cascade,
  converter text not null,
  converter_version text,
  started_at timestamptz not null default now(),
  finished_at timestamptz,
  success boolean not null default false,
  error_code text,
  error_message text,
  markdown text,
  raw_text text,
  metadata jsonb not null default '{}'::jsonb
);

create index if not exists idx_conversions_document on conversions(document_id);

create table if not exists playbooks (
  id uuid primary key,
  tenant_id uuid not null,
  document_id uuid not null references documents(id) on delete cascade,
  version int not null default 1,
  title text not null,
  summary text,
  domain text,
  service text,
  severity_default text,
  tags text[] not null default '{}',
  owner text,
  review_cycle_days int default 90,
  expires_at timestamptz,
  status text not null check (status in ('draft','review','approved','published','archived')),
  json jsonb not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  unique (tenant_id, document_id, version)
);

create index if not exists idx_playbooks_tenant_status on playbooks(tenant_id, status);
create index if not exists idx_playbooks_json_gin on playbooks using gin (json);

create table if not exists playbook_sections (
  id uuid primary key,
  playbook_id uuid not null references playbooks(id) on delete cascade,
  section_type text not null,
  step_no int,
  title text,
  content text not null,
  content_tsv tsvector generated always as (to_tsvector('simple', coalesce(content,''))) stored,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_sections_playbook on playbook_sections(playbook_id);
create index if not exists idx_sections_tsv on playbook_sections using gin(content_tsv);

create table if not exists embeddings (
  id uuid primary key,
  section_id uuid not null references playbook_sections(id) on delete cascade,
  model text not null,
  dim int not null,
  embedding vector(1536) not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_embeddings_section on embeddings(section_id);

create table if not exists quality_reports (
  id uuid primary key,
  playbook_id uuid not null references playbooks(id) on delete cascade,
  evaluator text not null,
  total_score int not null check (total_score between 0 and 100),
  status text not null check (status in ('rejected','needs_review','approved')),
  hard_failures jsonb not null default '[]'::jsonb,
  warnings jsonb not null default '[]'::jsonb,
  rubric_scores jsonb not null,
  created_at timestamptz not null default now()
);

create index if not exists idx_quality_playbook on quality_reports(playbook_id, created_at desc);

create table if not exists review_tasks (
  id uuid primary key,
  tenant_id uuid not null,
  playbook_id uuid not null references playbooks(id) on delete cascade,
  reason text not null,
  priority text not null default 'normal' check (priority in ('low','normal','high')),
  assignee text,
  status text not null default 'open' check (status in ('open','in_progress','resolved','rejected')),
  created_at timestamptz not null default now(),
  resolved_at timestamptz
);

create index if not exists idx_review_tasks_tenant_status on review_tasks(tenant_id, status, priority);
