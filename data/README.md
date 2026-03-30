# Data Layout

Tracked data in Git should stay limited to manifests, templates, and placeholders.

Working directories:

- `raw/` for collected source snapshots kept out of Git
- `normalized/` for parsed text prepared for indexing
- `views/` for generated HTML citation documents kept out of Git
- `manifests/` for tracked schema examples and source manifests
- `packages/` for outbound, inbound, approved, and archived closed-network transfer bundles

Do not commit generated corpora or built indexes to this branch.
