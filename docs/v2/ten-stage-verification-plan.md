# OCP RAG 챗봇 10단계 실행 계획

## 목적

이 문서는 `rewrite/opendoc-v2` 브랜치에서 **검증 우선**으로 작업을 진행하기 위한 운영 기준서다.

핵심 원칙은 아래와 같다.

- 한 번에 감당 가능한 분량으로만 끊어서 진행한다.
- 각 단계는 **약 30분 집중 작업**을 기준으로 설계한다.
- 각 단계는 **구현 -> 테스트 -> 검증 -> 정리**까지 마쳐야 완료다.
- **1단계가 끝나야 2단계를 시작**한다.
- 모든 단계는 반드시 **6명의 도우미 역할**과 함께 수행한다.
- 목표는 문서를 늘리는 것이 아니라 **실제로 돌아가고, 조건에 부합하는 결과물**을 만드는 것이다.

## 공통 팀 구성

모든 단계는 아래 6개 역할을 고정적으로 사용한다.

### 크리에이티브 요원 2명

1. `Creative-A`
   - 질문 재구성, 사용자 관점 시나리오, 예외 케이스 아이디어 담당
2. `Creative-B`
   - 우회 경로, 대체 전략, UX 관점 보강 포인트 담당

### 전문가 2명

1. `Expert-A`
   - 해당 단계의 핵심 기술 구현 담당
2. `Expert-B`
   - 해당 단계의 도메인/아키텍처 검토 담당

### 깐깐한 정리 검사 멤버 2명

1. `Inspector-A`
   - 결과물 경로, 문서, 설정, 실행 순서 정리 담당
2. `Inspector-B`
   - 테스트 증거, 로그, 리포트, 회귀 여부 검증 담당

## 단계 운영 규칙

각 단계는 아래 순서를 반드시 따른다.

1. 목표와 성공 조건 확인
2. 6인 역할 배정
3. 구현
4. 테스트 실행
5. 검증 결과 기록
6. 정리와 문서 반영
7. 다음 단계 진입 여부 판정

각 단계는 아래 네 가지가 모두 있어야 완료로 본다.

- 코드 또는 설정 변경
- 테스트 실행 결과
- 검증 결론
- 정리 문서 또는 리포트 반영

---

## 1단계. 검증 입력 정합성 복구

### 목표

깨진 한국어 fixture, benchmark 질문셋, live smoke 질문셋을 복구해서 **검증 입력 자체를 신뢰 가능한 상태**로 만든다.

### 왜 먼저 해야 하나

질문셋이 깨져 있으면 retrieval, red-team, multiturn, live smoke 결과는 전부 왜곡된다.

### 6인 역할

- `Creative-A`: 사용자 질문을 자연스러운 한국어로 복구
- `Creative-B`: follow-up 질문과 red-team 표현을 다듬음
- `Expert-A`: benchmark 파일 구조와 필드 보존
- `Expert-B`: 기대 문서/카테고리와 질문 의도 정합성 확인
- `Inspector-A`: JSON/JSONL 파싱과 줄 수 확인
- `Inspector-B`: 깨진 문자열이 남아 있지 않은지 재검사

### 작업

- `deployment/live_runtime_smoke_cases.json` 복구
- `eval/benchmarks/p0_retrieval_benchmark_cases.jsonl` 복구
- `eval/benchmarks/p0_red_team_cases.jsonl` 복구
- `eval/benchmarks/p0_multiturn_scenarios.json` 복구

### 완료 기준

- 모든 fixture가 정상 UTF-8 한국어 질문을 가짐
- JSON/JSONL 파싱 통과
- ID, 기대 문서 경로, 기대 source/category, 시나리오 구조는 유지

---

## 2단계. 런타임 경로 진위 검증

### 목표

`bridge -> OpenDocuments -> gateway -> viewer` 경로가 **진짜로 BGE-M3와 회사 LLM 경로를 타는지** 증명한다.

### 왜 중요하나

stub 또는 오래된 경로를 타면 이후 품질 검증 수치가 무의미해진다.

### 6인 역할

- `Creative-A`: 라이브 질문 흐름 시나리오 점검
- `Creative-B`: 실패 시 우회 검증 시나리오 제안
- `Expert-A`: bridge / gateway / runtime config 검증
- `Expert-B`: OpenDocuments 실행 경로와 embed/chat 호출 검증
- `Inspector-A`: health, ready, models, viewer 로그 점검
- `Inspector-B`: 임베딩 차원, 모델명, env 기반 설정 사용 여부 점검

### 작업

- `/health`, `/ready`, `/v1/models` 확인
- live runtime smoke 재실행
- OpenDocuments 로그에 embed probe 실패가 없는지 확인
- gateway와 bridge 로그에서 실제 호출 확인

### 완료 기준

- bridge ready 통과
- OpenDocuments가 실제 openai bridge 경로를 사용
- viewer click-through 유지
- env 기반 모델/임베딩 설정이 로그와 리포트에서 확인됨

---

## 3단계. widened corpus retrieval 실패 원인 해부

### 목표

확장 코퍼스에서 실패하는 retrieval 케이스를 **질문, 메타데이터, source bias, query rewrite** 관점으로 분해한다.

### 왜 중요하나

지금 가장 큰 품질 리스크는 넓은 코퍼스에서 질문이 올바른 문서군으로 가지 않는 것이다.

### 6인 역할

- `Creative-A`: 실패 질문을 사용자 관점으로 재서술
- `Creative-B`: source drift 패턴 가설 제시
- `Expert-A`: benchmark runner와 후보군 분석
- `Expert-B`: source_dir/category/document metadata 분석
- `Inspector-A`: 실패 케이스별 top-k 기록 정리
- `Inspector-B`: 원인 분류표 작성

### 작업

- 실패 케이스별 top-k 후보 추출
- 기대 문서와 실제 문서 비교
- source_dir 과도 쏠림 분석
- follow-up miss와 standalone miss를 분리

### 완료 기준

- 실패 원인이 문서로 정리됨
- 적어도 `question`, `rewrite`, `source_dir`, `document_path`, `citation` 레벨의 원인 분해가 끝남

---

## 4단계. retrieval 보정 1차

### 목표

해부 결과를 바탕으로 **query rewrite, source/category bias, follow-up memory bias**를 1차 보정한다.

### 왜 중요하나

검증만 반복하면 품질은 오르지 않는다. 이 단계에서 실제 retrieval 품질을 끌어올린다.

### 6인 역할

- `Creative-A`: 한국어 질문의 검색 친화 표현 보강
- `Creative-B`: follow-up 재작성 표현 보강
- `Expert-A`: policy/rewrite 로직 수정
- `Expert-B`: source/category weighting 조정
- `Inspector-A`: 코드 변경 범위 정리
- `Inspector-B`: 회귀 위험 포인트 기록

### 작업

- follow-up rewrite 보정
- source_dir/category bias 조정
- 필요한 메타데이터 힌트 보강
- widened corpus 기준의 보수적 답변 규칙 유지

### 완료 기준

- 실패 케이스 일부가 개선됨
- 정책 코드와 검증 결과가 같이 남음
- 기존 통과 케이스가 크게 깨지지 않음

---

## 5단계. Stage 9 retrieval / citation 회귀 검증

### 목표

보정된 retrieval이 widened corpus에서 실제로 개선됐는지 **Stage 9 기준으로 수치 확인**한다.

### 왜 중요하나

policy-prepared retrieval은 현재 품질의 핵심 기준이다.

### 6인 역할

- `Creative-A`: 질문 해석 품질 확인
- `Creative-B`: citation 사용성 점검
- `Expert-A`: Stage 9 policy benchmark 실행
- `Expert-B`: citation alignment 결과 검토
- `Inspector-A`: metric 정리
- `Inspector-B`: 이전 결과 대비 비교표 작성

### 작업

- Stage 9 benchmark 재실행
- `supporting_doc_hit`, `citation_correctness`, `rerank_lift` 비교
- citation viewer 연결 유지 확인

### 완료 기준

- widened corpus 기준 Stage 9 수치가 재산출됨
- citation correctness가 실제 viewer 경로와 함께 검증됨
- 개선/악화 항목이 문서화됨

---

## 6단계. Stage 10 multiturn / red-team 회귀 검증

### 목표

retrieval 보정이 멀티턴과 레드팀 시나리오를 해치지 않았는지 확인한다.

### 왜 중요하나

retrieval만 좋아지고 멀티턴이나 보수성 규칙이 무너지면 운영 도우미로 쓸 수 없다.

### 6인 역할

- `Creative-A`: follow-up 시나리오 품질 점검
- `Creative-B`: red-team 질문 표현 점검
- `Expert-A`: multiturn replay 실행
- `Expert-B`: red-team 평가 실행
- `Inspector-A`: pass/fail와 근거 정리
- `Inspector-B`: go/no-go 초안 작성

### 작업

- multiturn 시나리오 재실행
- red-team 케이스 재실행
- version continuity, topic shift, ungrounded response 확인

### 완료 기준

- 5턴 이상 멀티턴 검증 통과 여부가 명확함
- red-team 결과가 문서화됨
- Stage 10 기준 go/no-go 초안이 작성됨

---

## 7단계. Stage 11 refresh / activate / rollback 재검증

### 목표

확장 코퍼스와 보정된 retrieval 기준으로 **refresh loop가 여전히 안전하게 동작하는지** 확인한다.

### 왜 중요하나

폐쇄망 운영 도우미라면 데이터 갱신, 인덱스 전환, 롤백이 안정적이어야 한다.

### 6인 역할

- `Creative-A`: delta 갱신 시나리오 설계
- `Creative-B`: rollback 실사용 흐름 점검
- `Expert-A`: bundle / reindex / activate 실행
- `Expert-B`: lineage와 source profile 유지 검증
- `Inspector-A`: activation report 정리
- `Inspector-B`: rollback 증거 검토

### 작업

- bundle 생성
- 승인/검증/반입
- reindex
- activate
- rollback

### 완료 기준

- widened corpus 기준 refresh loop 재검증 완료
- activation/rollback 증거 파일이 남음
- source lineage가 유지됨

---

## 8단계. Stage 12 live runtime 품질 재검증

### 목표

실제 HTTP 경로에서 **한국어 질문, 스트리밍, 멀티턴, citation click-through**가 widened corpus 기준으로 돌아가는지 확인한다.

### 왜 중요하나

오프라인 benchmark가 좋아도 실제 서비스 경로가 무너지면 결과물로 인정할 수 없다.

### 6인 역할

- `Creative-A`: 실사용 질문 흐름 확인
- `Creative-B`: citation 클릭 흐름 확인
- `Expert-A`: live smoke 재실행
- `Expert-B`: runtime gateway / bridge 상태 점검
- `Inspector-A`: 로그와 리포트 정리
- `Inspector-B`: fail/pass 판정 기록

### 작업

- live runtime smoke 재실행
- conversation 유지 확인
- follow-up rewrite 확인
- viewer HTML 열림 확인

### 완료 기준

- Stage 12 live runtime overall pass
- source 없는 응답 또는 깨진 citation이 없음
- 리포트와 로그가 함께 남음

---

## 9단계. 저장소 정리와 v2 본체 가시화

### 목표

이 저장소를 처음 보는 사람이 **v2 본체가 어디인지, 생성물은 무엇인지, 검증 자산은 무엇인지** 바로 이해하게 만든다.

### 왜 중요하나

지금은 코드보다 문서/운영/산출물이 더 많이 보여서 길을 잃기 쉽다.

### 6인 역할

- `Creative-A`: README 첫 화면 구조 개선
- `Creative-B`: repo map 구조 제안
- `Expert-A`: docs/eval/deployment 재배치안 적용
- `Expert-B`: 생성물/추적 파일 경계 재정의
- `Inspector-A`: 경로 정리와 링크 점검
- `Inspector-B`: v1 잔재/혼란 요소 재검사

### 작업

- repo map 문서 추가
- README quick start 정리
- `docs/v2` 기준 문서와 이력 문서 경계 정리
- `data`, `indexes`, `workspace`의 성격을 명시

### 완료 기준

- 새로 보는 사람도 v2 본체 경로를 알 수 있음
- 혼란을 주는 경로가 줄어듦
- 정리 결과가 문서에 반영됨

---

## 10단계. 최종 통합 검증과 릴리즈 판정

### 목표

앞선 1~9단계 결과를 바탕으로 **실제 제출/시연 가능한 상태인지 최종 판정**한다.

### 왜 중요하나

부분 통과가 아니라 전체 조건 충족 여부를 마지막에 한 번 더 묶어서 확인해야 한다.

### 6인 역할

- `Creative-A`: 사용자 시연 시나리오 정리
- `Creative-B`: 예상 질문/리뷰 대응 포인트 정리
- `Expert-A`: 전체 런타임 시연
- `Expert-B`: OCP 운영 관점 최종 점검
- `Inspector-A`: 최종 체크리스트 완료 여부 검사
- `Inspector-B`: 남은 리스크와 다음 액션 정리

### 작업

- 전체 실행 경로 최종 점검
- README / runbook / roadmap 최종 정리
- Stage 9~12 결과 요약
- 남은 리스크 명시
- go / conditional go / no-go 판정

### 완료 기준

- 실제 질문, 한국어 답변, citation click-through, 멀티턴, 스트리밍, refresh loop 설명이 가능함
- 최종 요약 문서가 준비됨
- 남은 리스크가 숨김 없이 기록됨

---

## 단계 진행 규칙

- 지금부터는 이 문서 순서대로만 진행한다.
- `1단계 완료 -> 2단계 시작` 규칙을 지킨다.
- 각 단계는 최소한 아래 4가지를 남긴다.
  - 변경 코드 또는 설정
  - 테스트 결과
  - 검증 결론
  - 정리 문서

## 현재 단계 상태

- 1단계. 검증 입력 정합성 복구: 완료
- 다음 활성 단계: **2단계. 런타임 경로 진위 검증**

1단계 완료 근거는 아래 문서와 리포트에 남긴다.

- [stage01-fixture-integrity-report.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/stage01-fixture-integrity-report.md)
- [stage01-fixture-integrity-report.json](/C:/Users/soulu/cywell/ocp-rag-chatbot/data/manifests/generated/stage01-fixture-integrity-report.json)
