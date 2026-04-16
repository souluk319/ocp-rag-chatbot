# W6-E3-T3 REAL DATA VIEWER VALIDATION

- representative set locked from active 29 operational wiki books
- quality axes: paragraph readability, ordered lists, code block separation, figure treatment, relation/atlas usefulness
- chosen books: nodes, advanced_networking, web_console, backup_and_restore, security_and_compliance
- explorer finding: high-risk paths are viewer_blocks.py figure resolution, viewer_page.py figure width, runtime-figures API fallbacks, atlas shelf positional slicing, overlay consistency
- smoke order locked: nodes -> advanced_networking -> web_console -> backup_and_restore -> security_and_compliance
- live fix: mixed 'web console + RBAC + doc locator' query now returns intentional no_answer instead of drifting to web_console customization docs
- live fix: '프로젝트별 권한 문서 경로를 알려줘' returns grounded RBAC doc locator answer pointing to authentication_and_authorization > 사용자 역할 추가
- heuristic scan: nodes/backup_and_restore/security_and_compliance still show many long paragraphs; advanced_networking shows ordered-list and bare-shell shaping risk; web_console is strongest current candidate
- reader-grade fix 1: viewer_blocks now splits long narrative paragraphs into reader-sized chunks before rendering <p> blocks and ordered-list continuations
- reader-grade fix 2: low-signal shell suppression now hides standalone oc/kubectl/ellipsis code blocks while preserving meaningful commands such as oc adm must-gather
- reader-grade fix 3: malformed ordered items whose body is numeric-only (for example '1. 2') are now suppressed instead of rendered as bogus procedure steps
- re-measurement after fix round 1: standalone oc/kubectl blocks = 0 across representative 5, bogus numeric ordered items = 0 across representative 5; main remaining debt is dense paragraph readability

- explorer shortlist: installing_on_any_platform -> machine_configuration -> backup_and_restore -> web_console -> security_and_compliance -> advanced_networking -> authentication_and_authorization -> postinstallation_configuration -> nodes -> disconnected_environments

## 2026-04-16 figure-grouping + table-normalization follow-up
- atlas_canvas figure lane now groups runtime figures into up to 3 visual clusters in Workspace/Library.
- Workspace atlas figure cards support cluster summary, count badge, and representative thumbnail.
- Library preview atlas uses same cluster summary language and thumbnail treatment.
- viewer_blocks.py now pre-normalizes markdown table blocks into [TABLE] before paragraph shaping.
- local nodes render improved to TABLE_COUNT=31, GT240=93, GT320=0, MAX=315.
- live 8765 responses still showed stale raw table output during one smoke path; isolated as backend/runtime-serving inconsistency and kept as open follow-up before closeout.


- 2026-04-16 09:13 KST runtime viewer serving packet complete: active operational wiki 26 books materialized under artifacts/runtime/served_viewers and /playbooks/wiki-runtime/active/nodes/index.html now serves in 0.018s (curl), data-control-room in 2.644s.

