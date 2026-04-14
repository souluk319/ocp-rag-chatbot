# 07_toc_aware_book — TOC-aware book

## Goal

`backup_and_restore` 문서를 다른 shaping 순서로 재구성해서 reader-grade book 후보를 만든다.

## Source

- slug: `backup_and_restore`
- title: `Backup and restore`
- input: `data\gold_manualbook_ko\playbooks\backup_and_restore.json`

## Pipeline Steps

1. Raw HTML
2. section tree
3. toc-aware composition
4. Markdown final

## Tech Stack

- Python (`.venv\Scripts\python.exe`)
- `translation_draft_generation.generate_translation_drafts`
- `reader_grade_pipeline.ensure_translation_manifest`
- markdown post-processing

## Notes

- 이 폴더의 `output.md` 가 사용자 비교 대상이다.
- `meta.json` 은 trial 메타데이터만 남긴다.
