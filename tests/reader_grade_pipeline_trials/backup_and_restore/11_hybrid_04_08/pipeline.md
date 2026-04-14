# 11_hybrid_04_08 — Procedure spine + operator-first opening

## Goal

`backup_and_restore` 문서에서 `04_procedure_code_verify`의 절차 축과 `08_operator_first`의 시작 가이드를 합성해서, reference shadow에 가장 가까운 운영형 북 후보를 만든다.

## Source

- slug: `backup_and_restore`
- base trials:
  - `04_procedure_code_verify`
  - `08_operator_first`
- translated draft input: `data/silver_ko/translation_drafts/playbooks/backup_and_restore.json`

## Pipeline Steps

1. translated draft에서 backup / restore / verify 축을 유지한다.
2. operator-first 방식의 `Start Here`와 `When To Use`를 앞에 둔다.
3. prerequisite 는 bullet checklist 로 압축한다.
4. restore 본문은 raw 장문 대신 핵심 단계와 명령만 남긴다.
5. failure signal 을 마지막에 별도 블록으로 둔다.

## Tech Stack

- Python (`.venv\Scripts\python.exe`)
- `translation_draft_generation.generate_translation_drafts`
- trial composition by markdown assembly
- reader-grade manual shaping

## Notes

- 이 폴더의 `output.md` 가 비교 대상이다.
- 목표는 새 trial 발명보다 `이미 잘 나온 후보 조합`을 합성하는 것이다.
