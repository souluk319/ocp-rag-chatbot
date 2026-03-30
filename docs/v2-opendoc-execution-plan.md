# OCP RAG v2 Execution Plan

## Goal

Build an OCP operations assistant chatbot for closed-network environments by moving from the custom Python RAG pipeline to an OpenDocuments-based v2 architecture.

## Project Direction

- Keep the existing Python-based implementation as v1 reference.
- Build v2 on top of OpenDocuments as the RAG platform.
- Treat official OCP documentation and approved internal documents as primary knowledge sources.
- Support a controlled document update flow for closed-network deployment.

## Repository Strategy

- Main repository: `ocp-rag-chatbot`
- Legacy branch: `release/v1` to preserve the current implementation
- Rewrite branch: `rewrite/opendoc-v2`
- Daily progress should be visible through branch commits and a future draft PR

## Data Sources

### Primary

- `openshift/openshift-docs`
- existing sanitized corpus under `data/`
- approved internal OCP operations guides

### Secondary

- selected Red Hat documentation exports when source content is not available in repo form
- internal FAQ, training materials, and troubleshooting notes

## Architecture Principles

- Separate application code from document source repositories.
- Preserve source metadata such as product, version, category, language, and collection time.
- Prefer official documentation when ranking results.
- Keep ingestion, normalization, indexing, and deployment steps reproducible.
- Use approval-based document refresh before reindexing content for closed-network use.

## Initial Workstreams

### 1. Repository and Workflow Setup

- protect v1 as a stable baseline
- keep v2 development isolated on `rewrite/opendoc-v2`
- document working conventions for GitHub and editor workspace usage

### 2. Data Intake Design

- define source manifest format
- define metadata schema
- define normalization rules for official and internal documents
- decide how external repositories are mirrored into the workspace

### 3. OpenDocuments Validation

- verify local startup and configuration path
- index a small OCP document subset
- confirm answer quality, citation behavior, and Korean query handling

### 4. OCP-Specific Policy Layer

- Korean response rules
- operations mode vs study mode
- version priority rules
- source trust ordering

### 5. Closed-Network Update Flow

- sync documents from an external collection environment
- generate change reports and approved transfer bundles
- import approved bundles into the closed network
- rebuild indexes and retain rollback points

## First Implementation Targets

1. freeze and label the current v1 baseline
2. write the v2 repository and data layout
3. define source and metadata manifests
4. validate OpenDocuments with a small OCP sample set
5. design the closed-network document refresh path

## Immediate Next Tasks

1. create `release/v1` from current stable main
2. add a draft PR workflow note for `rewrite/opendoc-v2`
3. define a concrete folder layout for app, ingest, configs, and indexes
4. list the first document sources to onboard
5. bootstrap the first OpenDocuments-based validation run

## Success Criteria

- v1 remains recoverable and understandable
- v2 can answer core OCP operations questions with citations
- document onboarding is repeatable
- closed-network refresh steps are documented
- daily progress is visible in GitHub without merging unstable work into `main`
