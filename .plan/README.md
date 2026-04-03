# OCP RAG Chatbot Planning Set

## 1. 목적

이 폴더는 `AGENTS.md` 기준으로 현재 코드베이스와 사용자 피드백 9개를 실행 가능한 계획 문서로 분해한 결과물이다.

계획의 기본 원칙은 다음과 같다.

- 정답성과 근거성을 우선한다.
- Retrieval 품질과 Answer 품질을 분리해서 본다.
- 큰 변경은 항상 테스트 영향과 함께 적는다.
- 화려함보다 검사 가능한 구조를 우선한다.

## 2. 읽는 순서

1. `part-1-current-state-and-gap-analysis.md`
2. `part-2-console-ux-plan.md`
3. `part-3-echo-multiturn-plan.md`
4. `part-4-sieve-retrieval-and-ingest-plan.md`
5. `part-5-runbook-answer-quality-plan.md`
6. `part-6-redpen-eval-and-release-plan.md`
7. `part-7-roadmap-and-ownership.md`

## 3. 계획 범위

이번 계획은 다음 피드백을 모두 다룬다.

1. 대기 중 체감 속도 개선
2. 멀티턴 10회 이상 안정성
3. 새 탭 대신 같은 화면 문서 뷰어
4. PDF/PPT/HTML 등 업로드형 RAG 확장
5. 업로드 문서의 보기 좋은 규격화 저장
6. 답변별 파일/출처 태그
7. OCP 운영 명령/단축 질문의 빠른 응답
8. 단계별 안내 요청 시 엇나감 방지
9. 문장 단위 유사도 질문에 대한 명확한 설명과 향후 계획

## 4. 현재 문서 세트에서 바로 보아야 할 점

- `AGENTS.md`는 팀 역할과 제품 규칙을 고정한다.
- `PRD.md`는 업로드형 RAG 플랫폼 확장 방향을 이미 포함한다.
- 현재 저장소에는 `EVALS.md`, `TEAM_OPS.md`, `VENDOR_NOTES.md`가 아직 없다.
- 따라서 이번 계획에는 구현 계획뿐 아니라 문서 체계 확장 계획도 포함한다.

## 5. 현재 상태 요약

- 현재 브랜치에는 최근 RAG 안정화 수정이 로컬 변경으로 남아 있다.
- 프론트는 스트리밍 응답, 세션 리셋, follow-up 버튼, inspector 패널의 뼈대가 있다.
- 서버는 세션 히스토리를 20턴까지 유지하지만, 답변 프롬프트는 전체 히스토리 대신 요약된 세션 상태만 사용한다.
- 내부 문서 뷰어 엔드포인트는 있으나, 실제 UI citation 링크는 새 탭을 연다.
- 업로드형 문서 수집 파이프라인은 아직 구현되어 있지 않다.

## 6. 기대 산출물

이 문서 세트의 목표는 다음 두 가지다.

- 팀이 바로 작업을 쪼개서 착수할 수 있는 수준의 로드맵 제공
- 추후 `EVALS.md`, `TEAM_OPS.md`, `VENDOR_NOTES.md`로 분리될 내용의 초안 제공
