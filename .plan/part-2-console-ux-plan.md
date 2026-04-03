# Part 2. Console UX Plan

## Chapter 2.1 목표

사용자가 “멈췄다”, “근거가 안 보인다”, “문서를 같이 보기 어렵다”라고 느끼는 지점을 줄여서 시연과 실사용 모두에서 신뢰감을 올린다.

## Chapter 2.2 Workstream A: 대기 상태 재설계

### 현재 문제

- 실제 응답은 스트리밍되지만, 사용자는 텍스트만 바뀌는 정적 상태로 인식하기 쉽다.
- 대기 중 단계, 진행감, 다음 액션에 대한 시각적 피드백이 약하다.

### 계획

- `pending card`를 실제 렌더링 경로에 연결한다.
- 단계별 상태를 `질문 분석 -> 검색 -> 근거 조립 -> 답변 생성 -> citation 정리`로 고정한다.
- 진행 바, live shimmer, 현재 단계 라벨, 상세 메시지를 함께 노출한다.
- 장시간 단계에서는 “지금 느린 이유”를 짧게 설명한다.

### 완료 기준

- 1초 이상 대기 시 정적 텍스트만 보이지 않는다.
- 사용자가 현재 어느 단계인지 항상 알 수 있다.
- 중단/재시도 행동이 명확하다.

## Chapter 2.3 Workstream B: Citation 과 Source Tag 재배치

### 현재 문제

- citation card는 있으나 answer 본문과 출처 인지가 분리되어 있다.
- 사용자는 “이 답이 어느 파일 기반인지”를 바로 못 읽는다.

### 계획

- 답변 헤더에 `source tag strip`을 붙인다.
- 태그 최소 단위는 `book_slug`, 문서명, section 수준으로 잡는다.
- citation 카드 상단에는 `파일`, `섹션`, `근거 수`를 짧게 요약한다.
- ops 모드에서는 명령어 답변 위에 `근거 문서 태그`를 먼저 보여준다.

### 완료 기준

- 각 답변 카드에서 본문 읽기 전 출처 파일을 알 수 있다.
- citation card와 answer tag가 서로 어긋나지 않는다.

## Chapter 2.4 Workstream C: 같은 화면 문서 뷰어

### 현재 문제

- 내부 viewer는 존재하지만 사용자 경험은 새 탭 오픈이다.
- trace 패널과 문서 패널이 분리되어 있지 않다.

### 계획

- 우측 패널을 `Trace / Sources / Document` 3탭 구조로 재구성한다.
- citation 클릭 시 새 탭 대신 `Document` 탭이 열린다.
- 문서 탭은 section anchor 이동, 현재 citation 하이라이트, 이전/다음 citation 이동을 지원한다.
- 선택적으로 `새 탭 열기`는 보조 행동으로 남긴다.

### 완료 기준

- 기본 동작은 same-page viewer다.
- 채팅과 근거 문서를 동시에 볼 수 있다.
- citation 클릭 후 사용자가 길을 잃지 않는다.

## Chapter 2.5 테스트 영향

- pending UI 렌더링 상태 테스트
- generating 중 duplicate send 방지 테스트
- citation 클릭 시 same-page panel open 테스트
- source tag 렌더링 스냅샷 테스트
- 오류/중단/재생성 UX 테스트
