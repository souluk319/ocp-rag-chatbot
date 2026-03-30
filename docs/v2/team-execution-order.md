# Team Execution Order

## Repositories

- Product repo: `C:\Users\soulu\cywell\ocp-rag-chatbot`
- RAG platform baseline: `C:\Users\soulu\cywell\ocp-rag-v2\OpenDocuments`
- Official document source: `C:\Users\soulu\cywell\openshift-docs`

## Team roles

- Lead Architect / PM
- OCP / Air-gapped Infrastructure Engineer
- RAG / Search Engineer
- LLM Serving / Backend Engineer
- OCP Operations SME
- QA / Evaluation / Red Team
- UI / UX Engineer
- Data / Document Onboarding Engineer

## Order of work

### Phase 1. Lock the data boundary

Owners:
- Lead Architect / PM
- Data / Document Onboarding Engineer
- OCP Operations SME

Tasks:
- treat `openshift-docs` as the primary official source
- exclude non-target product lines for the first pass
- finalize the first ingestion subset
- finalize metadata and source manifests in `configs/`

Authoritative scope reference:
- `docs/v2/source-scope.md`

Current rule:
- the active ingest slice starts with the `P0 validation slice`
- the first operator-facing scope should promote toward the `first operational release target`
- P1 and P2 remain planned expansion sets, not default ingest targets

Exit criteria:
- source scope is fixed
- include and exclude paths are documented
- manifest format is fixed

### Phase 2. Build the onboarding pipeline

Owners:
- Data / Document Onboarding Engineer
- RAG / Search Engineer

Tasks:
- mirror or sync the selected source directories
- normalize source files into indexable text
- generate metadata manifests
- package the normalized set for local validation

Exit criteria:
- we can reproduce the same normalized corpus from source
- each document carries source, version, category, language, and trust metadata

### Phase 3. Validate OpenDocuments with a small slice

Owners:
- RAG / Search Engineer
- LLM Serving / Backend Engineer

Tasks:
- use the local OpenDocuments workspace as the platform baseline
- ingest a small OCP subset first
- confirm query, citation, and streaming behavior
- avoid UI customization in this phase

Relevant OpenDocuments areas:
- `packages/cli`
- `packages/core`
- `packages/server`
- `packages/web`

Exit criteria:
- a small OCP corpus can be indexed
- a question can be answered with sources
- the system works without touching the old v1 code

### Phase 4. Lock the backend to the company model endpoint

Owners:
- LLM Serving / Backend Engineer
- Lead Architect / PM

Tasks:
- configure OpenDocuments model settings for a single company endpoint
- prevent accidental fallback to local or public providers
- define the first internal runtime config

Observed configuration points in OpenDocuments:
- `packages/core/src/config/schema.ts`
- `packages/core/src/config/defaults.ts`
- `packages/server/src/bootstrap.ts`

Exit criteria:
- v2 assumes one approved internal model endpoint
- backend startup path is documented

### Phase 5. Add OCP retrieval policy

Owners:
- RAG / Search Engineer
- OCP Operations SME
- LLM Serving / Backend Engineer

Tasks:
- apply official-doc priority
- apply version preference rules
- define operations mode behavior
- keep answers grounded and conservative

Exit criteria:
- retrieval policy is documented
- source trust ordering is documented
- version handling is documented

### Phase 6. Build evaluation before UI work

Owners:
- QA / Evaluation / Red Team
- OCP Operations SME
- RAG / Search Engineer

Tasks:
- define the first operations question set
- define answer acceptance rules
- define citation and version-safety checks
- define red-team prompts

Exit criteria:
- the assistant has a measurable acceptance bar

### Phase 7. Design the air-gapped update loop

Owners:
- OCP / Air-gapped Infrastructure Engineer
- Data / Document Onboarding Engineer
- LLM Serving / Backend Engineer

Tasks:
- collect changes outside the closed network
- generate an approval bundle
- import the bundle inside
- rebuild indexes
- keep rollback points

Exit criteria:
- update flow is documented and repeatable

### Phase 8. Touch UI last

Owners:
- UI / UX Engineer
- RAG / Search Engineer

Tasks:
- keep the default OpenDocuments UI in phase 1
- add only minimal OCP-specific UX after search quality is acceptable

Do not start with:
- a custom frontend rewrite
- branding work
- visual polish

## Current next moves

1. keep `docs/v2/source-scope.md` as the single source of truth for corpus boundary changes
2. add section-aware chunking and stable section metadata
3. add citation click-through metadata such as `viewer_url`
4. validate OpenDocuments against the normalized P0 subset
5. freeze the first evaluation checklist from `docs/v2/evaluation-spec.md`
