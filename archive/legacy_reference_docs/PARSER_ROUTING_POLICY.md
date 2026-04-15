# Parser Routing Policy

> Legacy reference only. 현재 기준선이 아니며, parser 관련 현재 계약은 루트 active rule set 과 parsed artifact 계약을 우선한다.

## Purpose

이 문서는 customer-pack intake에서 입력 포맷이 어떤 parser/OCR 경로를 타는지, 어디서 degraded/review로 내려가는지, 어떤 경우 즉시 거부하는지 고정한다.

## Routing Order

### 1. `web`

- 입력
  - 실제 `http/https` URL
  - local UTF-8 text/html file
- capture
  - Red Hat docs면 `html-single` 선호
  - 아니면 raw HTML/text capture
- normalize
  - `extract_sections(html)`
- reject
  - PDF/docx/pptx/xlsx/image 같은 binary를 `web`로 선언한 경우

### 2. `pdf`

- capture
  - binary copy or remote download
- normalize
  1. `docling markdown`
  2. 품질이 나쁘거나 text가 비면 `docling OCR`
  3. 그래도 실패하면 `pypdf pages + outline`
- degraded/review
  - OCR 경로를 탔거나 low-quality text signal이 감지되면 review 우선
- reject
  - section을 하나도 만들지 못한 경우

### 3. `md` / `asciidoc` / `txt`

- capture
  - UTF-8 text만 허용
- normalize
  - heading hierarchy / numeric heading / fenced code를 canonical section으로 변환
- reject
  - binary file을 text source로 속여 넣은 경우
  - UTF-8 decode 실패

### 4. `docx`

- capture
  - binary copy or remote download
- normalize
  - `python-docx`
  - heading style -> section heading
  - paragraph -> body
  - table -> tagged table text
- degraded/review
  - heading style가 거의 없고 giant paragraph 덩어리만 있으면 review 권고

### 5. `pptx`

- capture
  - binary copy or remote download
- normalize
  - `python-pptx`
  - slide title -> section heading
  - shape text -> body
  - slide table -> tagged table text
- degraded/review
  - slide title 부재 시 `Slide N` fallback 사용, review 권고

### 6. `xlsx`

- capture
  - binary copy or remote download
- normalize
  - `openpyxl`
  - worksheet -> section
  - cell grid -> tagged table text
- degraded/review
  - merged-cell heavy sheet, chart-only sheet, mostly empty sheet는 review 권고

### 7. `image`

- capture
  - binary copy or remote download
- normalize
  - `docling OCR`
  - OCR markdown -> canonical section
- degraded/review
  - image OCR은 기본 review 대상
  - heading/path/command 구분이 약하면 degraded
- reject
  - OCR 결과가 비었거나 canonical section이 0인 경우

## Hard Rules

- `silent fallback` 금지
  - route가 바뀌면 trace나 error에서 드러나야 한다.
- `fake support` 금지
  - parser가 없으면 supported라고 쓰지 않는다.
- `binary-as-text` 금지
  - mimetype/extension이 binary면 text path에서 즉시 거부한다.
- `canonical section 0` 금지
  - capture 성공만으로 완료라고 말하지 않는다.

## Output Contract

모든 supported route는 최소 아래를 남겨야 한다.

- `source_type`
- `capture_strategy`
- `canonical_book_path`
- `normalized_section_count`
- `source_uri`
- `viewer_path`
- `source trace`

## Self-Service Rebuild Alignment

- `web/html`, `text PDF`, `md`, `asciidoc`, `txt`, `docx`, `pptx`, `xlsx` 는 self-service rebuild 범위에 포함된다.
- `scan PDF`, `image OCR` 은 self-service 에서도 수용하지만 `review-needed` 또는 `degraded` 상태를 거칠 수 있다.
- `csv`, `zip`, legacy Office 는 self-service rebuild 범위 밖이다.

## Current Gaps

- `csv` dedicated table contract 없음
- legacy Office binary parser 없음
- multi-file archive/zip routing 없음
- heavy layout fidelity는 아직 contract 범위 밖
