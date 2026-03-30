# Workspace Guide

## Recommended local layout

```text
C:\Users\soulu\cywell\
  ocp-rag-chatbot\
  OpenDocuments\
  openshift-docs\
  internal-ocp-docs\
```

## How to work in Antigravity or VS Code

Open all four folders in one workspace. This makes it easy to compare:

- the main v2 project
- the OpenDocuments platform source
- the official OCP document source
- internal operations documents

Important: opening folders together does not merge their Git histories. Each repository still has its own branch, status, and commit history.

## Git rule of thumb

- commit v2 planning, ingestion scripts, manifests, and deployment work in `ocp-rag-chatbot`
- treat `openshift-docs` as a source mirror, not as the main project
- only modify `OpenDocuments` directly if a platform-level customization is truly required

## Why this matters

The v2 product is one project, but it depends on multiple repositories with different roles:

- `ocp-rag-chatbot` is the product repository
- `OpenDocuments` is the platform baseline
- `openshift-docs` is an official source repository
- `internal-ocp-docs` is an approved internal content source
