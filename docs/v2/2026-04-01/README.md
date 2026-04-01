# 2026-04-01 작업 계획

오늘 작업은 [fixed-context-brief.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context-brief.md)를 먼저 보고, 필요할 때 [fixed-context.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context.md)를 참고한다.

## 오늘 목표

오늘의 목적은 단순히 기능을 몇 개 더 붙이는 것이 아니다.

**심사자가 바로 보게 될 문제를 먼저 제거하고, 실제로 돌아가는 OCP 운영 도우미 챗봇을 안정적으로 만드는 것**이 오늘의 목적이다.

특히 아래 네 가지를 우선한다.

1. 기본 질문 대응
2. 한글 인코딩/문구 깨짐 제거
3. citation 과 HTML 원문 연결 안정화
4. `localhost:8000` 기준 실제 동작 안정화

## 오늘 작업 방식

- 사용자는 숫자만 입력한다.
- 각 숫자는 해당 단계 하나만 수행한다.
- 각 단계는 구현, 테스트, 검증, 정리까지 끝나야 완료로 본다.
- 단계가 끝나면 결과를 짧게 브리핑한다.
- 다음 단계는 사용자가 다음 숫자를 줄 때 시작한다.

## 오늘 총 단계 수

오늘은 **총 8단계**로 진행한다.

1. [1단계 - 기본 질문 구조 복구](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-01-basic-questions.md)
2. [2단계 - UI와 스트리밍 한글 복구](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-02-korean-ui-streaming.md)
3. [3단계 - 로컬 런타임 경로 고정](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-03-runtime-lock.md)
4. [4단계 - citation 클릭과 viewer 정합성](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-04-citation-viewer.md)
5. [5단계 - raw retrieval baseline 개선](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-05-raw-retrieval.md)
6. [6단계 - widened corpus 회귀 검증](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-06-regression.md)
7. [7단계 - 실런타임과 실코퍼스 정합성](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-07-runtime-corpus-integrity.md)
8. [8단계 - 심사용 핵심 질문 세트 고정](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-08-demo-readiness.md)

## 현재 상태

- 1단계 완료: [stage-01-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-01-report.md)
- 2단계 완료: [stage-02-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-02-report.md)
- 3단계 완료: [stage-03-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-03-report.md)
- 4단계 완료: [stage-04-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/2026-04-01/stage-04-report.md)
- 다음 활성 단계: 5단계

## 공통 팀 구성

모든 단계는 아래 6명을 기준으로 수행한다.

- Ramanujan: 질문 해석 및 검색 전략 설계
- Arendt: 한국어 응답 / UX 문구 설계
- Peirce: 공식 데이터 / 문서 구조 검증
- Gibbs: 런타임 / 통합 구현
- Feynman: 재현 테스트 / 실패 검증
- Russell: 구조 / 문서 / 정합성 감사

각 단계 문서에는 이 6명이 해당 단계에서 무엇을 맡는지 다시 적어둔다.
