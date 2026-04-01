# 4.20 Balanced Corpus Build Report

## Scope

- Source mirror: `C:\Users\soulu\cywell\openshift-docs-4.20`
- Source branch: `enterprise-4.20-local`
- Source commit: `683c38e6291e20bf951edff517b15810f5ce7abc`
- Active build profile: `ocp-4.20-balanced`
- Source id: `openshift-docs-4.20-balanced`

## Build basis

This corpus is not built from `main`.

It is built from the official `openshift-docs` repository pinned to the `enterprise-4.20` line through a dedicated local worktree. The build profile intentionally favors installation, update, disconnected, support, and core operations material that matters to OCP field guidance.

## Canonical ingestion behavior

The normalizer now keeps:

- top-level assembly path
- included `modules/...` paths
- include edges with `leveloffset`
- detected `xref:` targets
- section hierarchy
- viewer URL / HTML output
- source git ref / commit lineage

This means the corpus is no longer just a flattened `.adoc -> text` export. It preserves enough structure to explain why a citation came from a specific section and which modules were assembled into the final guide.

## Current build result

- scanned `.adoc` files: `901`
- accepted canonical documents: `869`
- documents with included module paths: `776`
- documents with xref targets: `531`

## Included top-level families

- `architecture`
- `installing/overview`
- `installing/install_config`
- `installing/installing_platform_agnostic`
- `installing/validation_and_troubleshooting`
- `post_installation_configuration`
- `updating`
- `upgrading`
- `disconnected`
- `networking`
- `security`
- `storage`
- `nodes`
- `operators`
- `observability`
- `etcd`
- `backup_and_restore`
- `authentication`
- `machine_configuration`
- `machine_management`
- `registry`
- `support`

## Key exclusions

The balanced profile currently excludes or suppresses:

- `ROSA`
- `OSD`
- `OCM`
- `MicroShift`
- `hosted_control_planes`
- `lightspeed`
- `release_notes`
- `rest_api`
- `web_console`
- `applications`
- `cicd`

It also blocks mixed-product fragments inside otherwise useful directories such as:

- `support/troubleshooting/rosa-*`
- `support/troubleshooting/troubleshooting-osd-*`
- `support/troubleshooting/sd-*`
- `authentication/osd-*`
- `authentication/sd-*`
- `architecture/ocm-*`
- `architecture/mce-*`
- `architecture/rosa-*`
- `architecture/osd-*`
- `networking/.../migrate-from-openshift-sdn-osd`

## Output locations

- Manifest: `C:\Users\soulu\cywell\ocp-rag-chatbot\data\manifests\generated\openshift-docs-4.20-balanced.json`
- Normalized text: `C:\Users\soulu\cywell\ocp-rag-chatbot\data\normalized\openshift-docs-4.20-balanced`
- HTML viewer output: `C:\Users\soulu\cywell\ocp-rag-chatbot\data\views\openshift-docs-4.20-balanced`

## Important boundary

This report only proves that the **4.20 balanced canonical corpus has been built**.

It does **not** mean the live runtime on `localhost:8000` is already serving this corpus. Runtime migration, Golden Set evaluation, and answer-path verification are still separate steps.
