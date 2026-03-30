# OCP Operations Assistant v2

This branch is a clean rewrite of the project for a new closed-network OCP operations assistant chatbot.

The previous Python RAG pipeline, legacy web UI, and old local corpus have been intentionally removed from this branch. The legacy system is preserved on `release/v1` and the `v1.0` tag.

## v2 goals

- Build on top of OpenDocuments instead of the custom v1 pipeline
- Rebuild data onboarding from scratch with official and approved internal sources
- Support Korean operations answers with citations and conservative grounding
- Add an approval-based document refresh path for air-gapped environments

## Development model

This repository is the main v2 project. External repositories stay separate and are referenced as inputs:

- `../OpenDocuments`
- `../openshift-docs`
- `../internal-ocp-docs`

Use a multi-root workspace in Antigravity or VS Code so these folders can be opened together without mixing their Git histories.

## Repository layout

```text
app/           thin integration layer and product-specific code
configs/       source manifests, metadata schema, retrieval policy examples
data/          tracked placeholders for manifests and local working directories
deployment/    closed-network deployment notes and bundle flow
docs/v2/       rewrite-specific planning and workspace guidance
eval/          evaluation plan and question-set ownership
indexes/       generated indexes kept out of Git except for placeholders
ingest/        document onboarding pipeline notes
```

## Immediate milestones

1. Define the source manifest and metadata schema
2. Mirror official OCP documentation into the workspace
3. Validate a minimal OpenDocuments-based ingestion and query flow
4. Define closed-network bundle packaging and approval checkpoints
5. Create the first OCP operations evaluation set

## Design docs

- `docs/v2/architecture-blueprint.md`
- `docs/v2/plan.md`
- `docs/v2/team-execution-order.md`
- `docs/v2/workspace-guide.md`

## Branch rules

- `main` remains the stable line until v2 is ready
- `release/v1` stores the legacy implementation
- `rewrite/opendoc-v2` is the only branch for this rewrite
- Do not reintroduce the v1 runtime into this branch
