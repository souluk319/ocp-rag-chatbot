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

This trust decision should be justified by:

1. repository ownership under the `openshift` organization
2. repository README text stating that OpenShift documentation is sourced there and published to `docs.openshift.com`

## Scope policy

The source boundary is now applied through the source-profile layer:

- profile catalog: `configs/source-profiles.yaml`
- active profile state: `configs/active-source-profile.yaml`

This means the pipeline can stay stable while the active git ref changes later from validation mode to an approved operator-facing minor.

### P0 validation slice

This is the smallest active slice that must work end to end before we widen the corpus.

Purpose:

- prove that normalization, metadata, indexing, citation, and Korean answering work together
- keep the corpus small enough to diagnose retrieval and grounding issues quickly

- `installing`
- `post_installation_configuration`
- `updating`
- `disconnected`
- `support`

This boundary has already been validated through the local normalization pipeline.

Validation-slice note:

- `support` remains top-level during validation so the pipeline sees realistic troubleshooting material
- exclusion filters are required because `support` is a mixed directory

### First operational release target

Once the validation slice is stable, the first real operator-facing release should widen to the core OCP operations surface.

Purpose:

- cover the most common install, update, troubleshooting, and operations questions from real OCP usage
- move from pipeline validation to operator usefulness

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

### Core validation profile before target minor approval

Before an operator-facing target minor is approved, we still need a wider validation corpus that exercises the real pipeline more aggressively than P0.

That profile is now represented as:

- `ocp-validation-main-core`

Purpose:

- expand retrieval, citation, runtime, and refresh-loop pressure without hard-pinning the system to one minor version too early
- keep the source-profile and lineage layer stable while the real operator-facing target minor is still undecided

Recommended active directories for this profile:

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
- `support`
- `authentication`
- `architecture`
- `machine_configuration`
- `machine_management`
- `web_console`
- `applications`
- `cicd`

Validation-core note:

- `release_notes` remain outside this profile because they are version-sensitive and should follow an approved target minor, not `main`
- `rest_api` also remains outside this profile because it is large, noisy, and better introduced after the core operator-facing corpus is stable

Version rule for the first operational release:

- the release must declare one approved target minor explicitly
- `release_notes` should prefer the current approved target minor only
- broader `4.x` labeling is acceptable for validation, not for operator-facing release guidance
- operator-facing release should use a target-minor source profile instead of continuing to ingest from `main`

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
