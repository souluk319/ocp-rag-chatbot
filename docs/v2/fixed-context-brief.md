# OCP RAG v2 실행 기준 요약

이 문서는 매번 작업 시작 전에 먼저 보는 **짧은 고정 컨텍스트**입니다.  
상세 기준은 [C:\Users\soulu\cywell\ocp-rag-chatbot\docs\v2\fixed-context.md](/C:/Users/soulu/cywell/ocp-rag-chatbot/docs/v2/fixed-context.md) 에 있습니다.

## 1. 지금 목표

이 프로젝트의 목표는 **보여주기용 데모가 아니라, 실제로 작동하는 OCP RAG 파이프라인을 설계하고 증명하는 것**입니다.

반드시 만족해야 하는 조건:

1. 공식 Red Hat/OpenShift 문서를 근거로 답한다.
2. `OpenDocuments` 기준 RAG 구조를 실제로 사용한다.
3. 한국어 질문에 한국어로 답한다.
4. 답변에 citation이 붙고, 클릭하면 HTML 원문이 열린다.
5. UI에서 실제 파이프라인 경로를 숨기지 않고 보여준다.
6. 속도보다 정확도가 우선이다.

## 2. 절대 행동 규칙

1. 알아서 판단하지 않는다.
2. 작업 목표나 완료 기준이 모호하면 사용자에게 먼저 묻는다.
3. 내가 이해한 목표/범위/완료 기준을 다시 보고하고 확인받은 뒤에만 작업한다.
4. 사용자가 방향을 못 잡으면 옵션을 제시하고 선택하게 한다.
5. 멋대로 해석한 결과물을 만들지 않는다.
6. 재현해서 증명한 것만 완료라고 말한다.

## 3. 현재 고정된 소스 기준

1. 공식 문서 원천: `openshift-docs`
2. 평가와 코퍼스 재설계의 기준 브랜치: `enterprise-4.20`
3. 고정 worktree 경로: `C:\Users\soulu\cywell\openshift-docs-4.20`
4. 현재 로컬 `main` 기반 코퍼스는 과도기 자산이며, 앞으로의 기준은 4.20이다.

## 4. 코퍼스 설계 핵심

1. `modules/`는 제외 대상이 아니라 **상위 가이드와 함께 읽어야 하는 절차 조각**이다.
2. `include::modules/...` 와 `xref:` 관계를 복원해서 **canonical document model**을 만들어야 한다.
3. 질문 평가와 코퍼스 범위 결정은 감으로 하지 않고 **Golden Set 100**으로 한다.

## 5. Golden Set 고정 기준

1. 파일: [C:\Users\soulu\cywell\ocp-rag-chatbot\eval\benchmarks\golden_set_100.csv](/C:/Users/soulu/cywell/ocp-rag-chatbot/eval/benchmarks/golden_set_100.csv)
2. 기준 브랜치: `enterprise-4.20`
3. 각 항목 포함 정보:
   - 질문
   - 의도/카테고리
   - 기대 출처 범위
   - 기대 정답 형태
4. 성공 기준:
   - 검색 재현율 90% 이상
   - 답변 정확도 85% 이상
   - 환각율 0%
   - 출처 연결 정확도 100%

## 6. 실제 6명 서브에이전트

1. Harvey: 설치/업데이트/운영 질문 설계
2. Turing: 한국어 질문/정답 형태 품질
3. Peirce: 기대 출처 범위 구체화
4. Carver: 평가 가능성, 점수화 기준 검토
5. Banach: 장애/복합 운영/Disconnected 질문
6. Bohr: 범위 밖 질문과 과장 방지

## 7. 오늘의 핵심 원칙

1. 빠르게 보이는 답변보다 **정확한 문서 연결**이 먼저다.
2. fast path나 rescue는 숨기지 않는다.
3. `localhost:8000`에서 직접 보이는 결과와 평가셋 결과가 서로 모순되면 실패로 본다.

## 8. 현재 상태

1. `enterprise-4.20` 기반 Golden Set 100은 확정됐다.
2. `openshift-docs-4.20` worktree를 기준으로 `openshift-docs-4.20-balanced` canonical corpus가 생성됐다.
3. 이 corpus는 `modules/include/xref` lineage를 manifest에 남긴다.
4. 단, `localhost:8000` live runtime은 아직 이 4.20 corpus로 재구축된 상태가 아니다.
