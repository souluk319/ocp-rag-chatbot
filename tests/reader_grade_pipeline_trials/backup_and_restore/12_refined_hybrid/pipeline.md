# 12_refined_hybrid — Reference-aligned refined hybrid

## Goal

`11_hybrid_04_08`을 기준으로 모범답안의 구조와 깊이에 더 가깝게 맞춘다.

## Source

- slug: `backup_and_restore`
- base sources:
  - `11_hybrid_04_08`
  - reference structure from `archive/root_contracts/backup_and_restore_reader_grade_shadow.md`

## Pipeline Steps

1. `Start Here`와 `When To Use`를 유지한다.
2. `Before You Begin`을 접근 권한, 백업 산출물, 중요 규칙으로 분해한다.
3. `Back Up etcd Data`는 절차와 산출물을 함께 남긴다.
4. `Restore`는 실제 수동 복구 순서대로 깊이를 늘린다.
5. `Verify`와 `Failure Signals`를 마지막에 분리한다.

## Tech Stack

- Python (`.venv\Scripts\python.exe`)
- translated draft playbook input
- trial composition by markdown assembly
- reference-aligned manual shaping

## Notes

- 이 폴더의 `output.md`가 `backup_and_restore`의 현재 최고 후보다.
- 목표는 새 기법 발명이 아니라 reference 구조에 최대한 가깝게 맞추는 것이다.
