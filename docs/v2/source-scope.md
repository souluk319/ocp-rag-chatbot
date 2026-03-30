# v2 Source Scope

## Purpose

This document is the single source of truth for the official document boundary used by v2.

It exists to prevent scope drift between:

- `docs/v2/architecture-blueprint.md`
- `docs/v2/team-execution-order.md`
- `configs/source-manifest.yaml`
- `ingest/normalize_openshift_docs.py`

## Authoritative source

- official repository: `C:\Users\soulu\cywell\openshift-docs`
- upstream origin: `https://github.com/openshift/openshift-docs`
- source format: `.adoc`

We treat this repository as the official authoring source for public OCP documentation.

## Scope policy

### P0 validation slice

This is the smallest active slice that must work end to end before we widen the corpus.

- `installing`
- `post_installation_configuration`
- `updating`
- `disconnected`
- `support`

This boundary has already been validated through the local normalization pipeline.

### First operational release target

Once the validation slice is stable, the first real operator-facing release should widen to the core OCP operations surface.

- `installing`
- `post_installation_configuration`
- `updating`
- `upgrading`
- `backup_and_restore`
- `networking`
- `security`
- `storage`
- `nodes`
- `operators`
- `observability`
- `etcd`
- `disconnected`
- `registry`
- `cli_reference`
- `support/troubleshooting`
- selected `release_notes` documents for the current target version

This is the recommended first-release scope even though the currently validated ingest slice is still smaller.

### P1 immediate expansion

Add these only after P0 indexing, citation, and Korean answer quality are acceptable.

- `authentication`
- `architecture`
- `machine_configuration`
- `machine_management`
- `web_console`
- `applications`
- `cicd`
- selected `rest_api` families with direct operational value

### P2 later expansion

Add these after retrieval quality and citation click-through are stable.

- remaining `release_notes`
- broader `rest_api`
- specialized platform areas such as `service_mesh`, `serverless`, `virt`, and `windows_containers`

## Global exclusions

These top-level product lines must not enter the OCP-first corpus.

- `osd_*`
- `rosa_*`
- `microshift_*`
- `cloud_experts_*`
- `ocm`
- `hosted_control_planes`
- `lightspeed`
- `migration_toolkit_for_containers`
- `contributing_to_docs`

These content helper directories are not ingest targets.

- `modules`
- `snippets`
- `_topic_maps`
- `_images`
- `_templates`
- `_attributes`
- `_stylesheets`
- `_javascripts`
- `_converters`
- `_gemfiles`

## Mixed-directory path exclusions

Some top-level directories, especially `support`, contain mixed product content.

The normalization pipeline must exclude any path containing one of these fragments:

- `/rosa-`
- `/rosa_`
- `-rosa-`
- `_rosa_`
- `/osd-`
- `/osd_`
- `-osd-`
- `_osd_`
- `/microshift-`
- `/microshift_`
- `-microshift-`
- `_microshift_`
- `/support/remote_health_monitoring/`
- `/support/troubleshooting/rosa-`
- `/support/troubleshooting/troubleshooting-osd-`
- `/support/troubleshooting/sd-`

If a new mixed-path family is discovered during validation, this document and the source manifest must be updated together.

## Inclusion rule

The first working corpus should prefer:

- installation and configuration guidance
- update and disconnected procedures
- troubleshooting material that clearly targets OCP

The first working corpus should avoid:

- community-only content
- hosted or managed-service operating guides
- product families outside OCP
- helper modules that are not user-readable documents

## Promotion rule

A directory or path family may move from planned scope into active scope only when:

1. normalization succeeds without mixed-product contamination
2. metadata remains stable and reproducible
3. citation click-through still works
4. retrieval quality does not regress on the baseline evaluation set

## Current validated result

Using the current validation-slice filters, the normalization pipeline produced:

- scanned `.adoc` files: `296`
- accepted documents: `281`
- excluded by path fragment: ROSA, OSD, `remote_health_monitoring`, and `sd-` support content

This result is the current baseline and should be refreshed whenever the source boundary changes.
