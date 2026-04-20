# Book Factory UI / Interaction Spec

Date: 2026-04-20  
Product: PlayBookStudio (PBS)  
Scope: `Playbook Library > Repository > Book Factory`

## 1. Goal

`Book Factory`는 단순 업로드 패널이 아니라, 다음 두 입력 lane을 같은 생산 surface 안에서 처리하는 공장으로 동작해야 한다.

1. `Tools Docs Upload`
2. `User Docs Upload`

핵심 목표는 이 둘을 한 화면 경험 안에서 자연스럽게 묶는 것이다.

- `Tools Docs Upload`
  - 챗봇이 답하지 못한 질문을 source request로 받아
  - 공식 `GitHub AsciiDoc` / 공식 `HTML-single manual` 후보를 찾고
  - 사용자가 원하는 원천소스를 대기열에 저장한 뒤
  - `딸깍`으로 Playbook 생산까지 이어지게 한다.

- `User Docs Upload`
  - 기존 업로드 기능을 유지하되
  - 같은 공장 surface 안에서 파이프라인과 로그까지 함께 보여준다.

## 2. Locked UX Direction

UI 기준은 아래로 고정한다.

- 익숙하지만 약간 더 정제된 디테일
- 새 문법 invent 하지 않는다
- 현재 `Playbook Library` 페이지 미감과 위계를 해치지 않는다
- 설명을 늘리는 대신 `눈에 보이는 흐름`을 만든다

즉:

- 과한 대시보드화 금지
- 과한 장식 금지
- 정보 위계와 단계감은 선명하게
- 버튼과 리스트는 사람이 바로 이해할 수 있게

## 3. Layout Decision

`Knowledge Ingestion Pipeline`라는 별도 덩어리는 더 이상 독립 surface가 아니다.

이제 구조는 아래로 고정한다.

### Repository Page

`Repository` view 안에 `Book Factory`가 들어간다.

### Book Factory section order

1. `Book Factory hub`
   - `Tools Docs Upload`
   - `User Docs Upload`
   - 현재 mode 상태

2. `Always-visible pipeline panel`
   - Book Factory 바로 아래
   - click-to-open 아님
   - 상시 노출

3. `Book Factory work area`
   - `Source Requests` 접이식 패널
   - `Download List` 접이식 패널
   - `Book Factory Assistant` 패널

4. 필요 시 보조 영역
   - advanced repo search
   - saved source candidates
   - user library / uploaded drafts

## 4. Pipeline Panel

파이프라인 패널은 `Book Factory` 아래에 항상 붙는다.

### Why

- 지금 구조에서 가장 와닿는 건 `단계 + 로그` 조합이다
- 사용자는 pipeline이 실제로 돌고 있다는 걸 눈으로 확인해야 한다
- 공식문서 생산과 유저문서 생산 모두 이 visual language를 공유하는 게 좋다

### Shared rule

같은 시각화 컴포넌트를 lane별로 재사용한다.

- `Tools Docs Upload` mode
- `User Docs Upload` mode

단, 단계 텍스트는 우리 tier 개념으로 고정한다.

### Fixed stage vocabulary

1. `Bronze`
2. `Silver`
3. `Gold`
4. `Judge`

### Lane-specific meaning

#### Tools Docs Upload

- `Bronze`: 원천 바인딩
- `Silver`: 구조화 초안 생성
- `Gold`: 플레이북 · 코퍼스 생성
- `Judge`: 라이브러리 합류 검증

#### User Docs Upload

- `Bronze`: file intake / source capture
- `Silver`: normalize / structured wiki
- `Gold`: playbook / corpus materialization
- `Judge`: user library ready

### Logs

파이프라인 패널 하단 로그창은 유지한다.

이 로그는 아래 둘을 모두 보여주는 공통 관측면이다.

- 공식문서 생산 로그
- 유저문서 생산 로그

### Queue semantics

중요 규칙:

- `Download List` 저장 상태는 아직 `생산 시작 전`이다
- 따라서 `목록 저장`만으로는 pipeline stage가 점등하지 않는다
- `생산` 버튼을 누른 뒤부터 pipeline 점등이 시작된다

즉:

- `Download List` = 준비영역
- `Pipeline` = 생산 실행 상태

이 둘을 섞어 보여주지 않는다.

### Pipeline mode toggle

`Book Factory Pipeline`에는 `자동 / 수동` 토글을 둔다.

#### 자동

- `딸깍 -> 끝까지 생산`
- 시연용 기본 실행 모드

#### 수동

- 단계별 완성 데이터를 볼 수 있다
- 다음 단계에서 적용될 규칙 제안이 checklist로 뜬다
- 사용자는 체크박스를 눌러 기존 할일 리스트를 수정할 수 있다
- 리스트 맨 아래에는 `추가 요구 입력` 면을 둔다

중요한 점:

- `수동`은 공장 제어권을 보여주는 모드여야 한다
- 이름만 있고 실질 제어가 없는 UI는 금지한다

### Manual mode scope

초기 수동 모드는 아래 3개를 대상으로 한다.

1. 현재 단계 산출물 preview
2. 다음 단계 규칙 checklist
3. 사용자 추가 요구 입력

구현 우선순위는:

1. `단계별 산출물 보기`
2. `체크리스트 수정`
3. `추가 요구 입력용 심플 챗봇`

순으로 간다.

## 5. Mode Buttons and Supported Inputs Strip

`Tools Docs Upload`와 `User Docs Upload`는 mode button이다.

버튼을 누르면 아래 확장자 strip의 활성 상태가 바뀐다.

### Tools Docs Upload active state

활성:

- `AsciiDoc`
- `HTML`

비활성:

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `MD`
- `TXT`
- `Image`

### User Docs Upload active state

활성:

- `PDF`
- `DOCX`
- `PPTX`
- `XLSX`
- `MD`
- `TXT`
- `AsciiDoc`
- `HTML`
- `Image`

중요한 건 `지원 여부를 시각적으로 이해시키는 것`이지, 확장자 strip 자체를 복잡하게 설명하는 게 아니다.

## 6. Source Requests

`Source Requests`는 Book Factory 안에 들어간다.

### Form factor

- 지금보다 작아도 된다
- 접었다 펼 수 있어야 한다
- queue 개수가 헤더에서 바로 보여야 한다

### Content

챗봇이 자료 부족으로 저장한 질문 목록이다.

각 row는 아래를 가진다.

- 질문 본문
- 저장 시각
- 필요 시 경고/메모 1개
- 오른쪽 액션 버튼: `문의하기`

### Important interaction

현재처럼 row 전체가 search trigger가 되는 방식은 축소한다.

이제 명시적 액션은 `문의하기` 버튼이다.

## 7. Book Factory Assistant

Book Factory 안에 심플한 assistant를 둔다.

이 assistant는 범용 챗봇이 아니라 `source finder assistant`다.

### Assistant role

답변하지 못한 질문에 대해 필요한 공식 원천소스를 찾아준다.

### Input sources

1. `Source Requests`에서 넘어온 질문
2. 사용자가 직접 입력한 질문/키워드

### Output target

assistant는 아래 두 종류만 찾으면 된다.

1. `Red Hat GitHub repository` 안의 관련 `AsciiDoc`
2. `공식 홈페이지 manual`의 관련 `html-single`

### Naming rule

출력 이름은 사람 눈높이의 쉬운 문장으로 바꾼다.

예시:

- `호스팅 컨트롤 플레인 공식 깃허브 문서`
- `호스팅 컨트롤 플레인 공식 웹페이지 매뉴얼`

복잡한 internal label을 그대로 노출하지 않는다.

## 8. Download List

assistant가 찾은 원천소스는 바로 생산하지 않고 `Download List`로 보낼 수 있어야 한다.

### Download List rules

- 접이식 패널
- Book Factory 안에 배치
- source option을 하나 또는 둘 다 저장 가능
- 목록에서 원본 링크를 다시 열 수 있어야 함
- 목록에서 바로 `딸깍 생산` 가능
- 저장 상태만으로는 pipeline이 진행된 것처럼 보이면 안 됨

### User behavior

사용자는:

1. 질문을 선택하거나 직접 입력
2. assistant 결과 2개 확인
3. 원하는 원천소스를 download list에 저장
4. download list에서 생산 실행

이 흐름을 한 눈에 이해해야 한다.

## 9. Production Flow for Tools Docs Upload

UI 기준 flow는 아래다.

1. source request 발생
2. `문의하기`
3. assistant가 두 원천소스 후보 제시
4. 하나 또는 둘 다 `Download List`에 저장
5. `생산` 실행
6. Playbook Library에 새 책 합류

이 흐름은 내일 시연의 핵심 루프다.

### State separation rule

`Download List`와 `Pipeline`은 다르다.

- `Download List` = 원천소스 선택과 저장
- `Pipeline` = 실제 생산 진행상태

따라서:

- 저장만 했을 때 `Silver`가 켜지지 않는다
- `생산`을 눌렀을 때부터 `Bronze -> Silver -> Gold -> Judge`가 진행된다

## 10. Production Flow for User Docs Upload

기존 flow는 유지한다.

1. 파일 업로드
2. capture
3. normalize
4. user library ready

단, 이 모든 시각화와 로그는 이제 `Book Factory` 안에서 보인다.

## 11. Non-goals for This Packet

이번 packet에서는 아래를 목표로 하지 않는다.

- 고유명사 사전 학습의 완성
- assistant를 범용 대화형 agent로 만드는 것
- 새로운 백엔드 AI 시스템 재설계
- UI 전체 theme 변경
- raw repository search를 제품 핵심 surface로 승격

이번 packet의 핵심은:

- `Book Factory`를 제품적으로 말이 되게 재배치
- `Tools Docs Upload` 경험을 시연 가능한 수준으로 닫기

## 12. Acceptance Criteria

### Pass

아래가 되면 pass다.

1. `Book Factory` 바로 아래에 pipeline panel이 항상 보인다
2. `Tools Docs Upload` / `User Docs Upload` 버튼에 따라 extension strip 활성 상태가 달라진다
3. `Source Requests`는 접고 펼 수 있다
4. 각 source request row 오른쪽에 `문의하기` 버튼이 있다
5. assistant가 공식 레포 / 공식 홈페이지 두 종류의 source option을 보여준다
6. option을 `Download List`에 저장할 수 있다
7. `Download List`에서 직접 생산이 가능하다
8. 생산 후 새 책이 Library 리스트에 합류한다
9. user upload lane도 같은 Book Factory pipeline visualization을 쓴다
10. `Download List` 저장만으로는 pipeline stage가 점등하지 않는다
11. `생산` 클릭 이후에만 단계 점등이 시작된다
12. `자동 / 수동` 토글이 보인다
13. `수동` mode에서는 단계 산출물과 다음 단계 checklist를 볼 수 있다

### Fail

아래면 fail이다.

- pipeline panel이 mode에 따라 사라진다
- source request가 여전히 큰 클릭형 리스트로만 남는다
- assistant가 후보 2종을 분명하게 못 보여준다
- download list 없이 즉시 생산만 강제한다
- queue 저장만 했는데 pipeline이 진행된 것처럼 보인다
- tools/user mode 차이가 visually 드러나지 않는다
- Book Factory가 기존 Repository UI보다 더 복잡하고 낯설게 느껴진다
- `수동` mode가 이름만 있고 실질 제어가 없다

## 13. Current Implementation Direction

이번 구현은 아래 방향으로 간다.

- backend 추가 재설계 최소화
- 이미 있는 `official_candidates` 검색 결과 재사용
- frontend state로
  - assistant
  - source requests
  - download list
  - pipeline mode
  를 연결
- raw repo search는 보조 기능으로 남기되, 핵심 primary surface는 `assistant + download list + production loop`

## 14. One-line Product Message

`PBS Book Factory는 답하지 못한 질문을 버리지 않고, 공식 원천소스를 찾아 Playbook Library의 새 책으로 생산하는 공장이다.`
