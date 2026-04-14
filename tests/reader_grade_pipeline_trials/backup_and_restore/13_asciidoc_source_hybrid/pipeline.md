# 13_asciidoc_source_hybrid — AsciiDoc source driven hybrid

## Goal

`docs.redhat` HTML이나 기존 gold JSON이 아니라, `openshift-docs` 원문 AsciiDoc에서 직접 reader-grade book 후보를 만든다.

## Source

- source tree: `tmp_source/openshift-docs-enterprise-4.20/backup_and_restore`
- assembly:
  - `backup_and_restore/index.adoc`
  - `backup_and_restore/control_plane_backup_and_restore/backing-up-etcd.adoc`
  - `backup_and_restore/control_plane_backup_and_restore/disaster_recovery/scenario-2-restoring-cluster-state.adoc`
- modules:
  - `modules/backup-etcd.adoc`
  - `modules/dr-restoring-cluster-state-about.adoc`
  - `modules/manually-restoring-cluster-etcd-backup.adoc`

## Pipeline Steps

1. AsciiDoc assembly와 핵심 modules 를 직접 읽는다.
2. control plane backup / restore 경로만 남기고 OADP application backup 은 제외한다.
3. admonition, prerequisites, procedures, code blocks 를 유지한다.
4. reader-grade 구조로 재배열한다.
5. 최종 `md`로 정리한다.

## Tech Stack

- Git sparse checkout
- AsciiDoc source reading
- markdown assembly
- reader-grade hybrid shaping

## Notes

- 이 결과는 `source-first` 품질 비교용이다.
- 목적은 `영문 AsciiDoc 원문이 더 좋은 입력인지` 확인하는 것이다.
