---
status: active
doc_type: feature_expansion_packet
audience:
  - codex
  - engineer
  - product
last_updated: 2026-04-21
canonical_surface_slug: llmwikibook
canonical_surface_display: LLMWikiBook
---

# LLMWikiBook Feature Expansion Packet

## Goal

이 packet 의 목표는 기존 `/studio` 수정이 아니라, `reader-first technical wiki surface` 인 `LLMWikiBook` 페이지를 제품에 기능 증설 형태로 추가·완성하는 것이다.

## Naming Lock

- canonical route 는 `/llmwikibook` 으로 고정한다.
- canonical display name 은 `LLMWikiBook` 으로 고정한다.
- 기존 `studio-v2` 명칭은 더 이상 primary product naming 으로 사용하지 않는다.
- 필요 시 기존 `/studio-v2` 는 호환 alias redirect 로만 남길 수 있다.

## Scope

- `presentation-ui/src/App.tsx`
- `presentation-ui/src/pages/LlmWikiBookPage.tsx`
- `presentation-ui/src/pages/llmWikiBookSupport.ts`
- `presentation-ui/src/pages/llmwikibook/*`
- 위 surface rename 에 따라 불가피하게 바뀌는 import / export / css namespace

## Non-Goals

- 기존 `/studio` surface 수정
- manifest, corpus, runtime contract 수정
- unrelated dirty state 정리
- legacy report 폴더명이나 과거 evidence rename

## Acceptance Criteria

1. `/llmwikibook` 가 새 기능 surface 로 동작한다.
2. page title, route, module naming 의 canonical 기준이 `LLMWikiBook / llmwikibook` 으로 정렬된다.
3. `/studio` 는 무변경으로 유지된다.
4. 기존 `/studio-v2` 가 남는다면 primary route 가 아니라 redirect alias 로만 남는다.
5. frontend build 와 renamed route smoke 가 통과한다.

## Validation Commands

- `npm --prefix presentation-ui run build`
- `GET /llmwikibook`
- 필요 시 `GET /studio-v2` redirect 확인

## Ref Snapshot

- `branch=feat/playbook-upgrade-renewal`
- `head=cac30499eeb5f3f1c9361644e3c2b3572b5c6b8f`
- `base=origin/main@e87fa0c562c5e277305617e1eea36c112aa01b27`

## Baseline Evidence

- prior packet report: `reports/execution_harness/studio_v2_gitbook_reset_20260421/main/final_report.json`
- prior smoke image: `reports/execution_harness/studio_v2_gitbook_reset_20260421/main/studio-v2-smoke-refined-loaded-v2.png`
