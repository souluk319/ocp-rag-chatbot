# Format Support Matrix

> Legacy reference only. 현재 기준선이 아니며, format 관련 현재 계약은 루트 active rule set 과 parsed artifact 계약을 우선한다.

## Purpose

이 문서는 customer-pack intake가 어떤 포맷을 실제로 `capture -> normalize -> canonical book`까지 처리하는지, 어디서 review/degraded로 내려가는지, 무엇을 아직 거부하는지 잠근다.

## Current Truth

아래 표기만 쓴다.

- `supported`
  - capture, normalize, canonical section, provenance가 모두 나온다.
- `supported_with_review`
  - canonical section은 나오지만 OCR/구조 복원 품질 때문에 사람 검토가 먼저 필요하다.
- `rejected`
  - 현재 계약상 intake에서 명시적으로 거부한다.

## Support Table

| Input Kind | Source Type | Status | Capture Strategy | Normalize Route | Notes |
|---|---|---|---|---|---|
| Website / HTML | `web` | `supported` | `docs_redhat_html_single_v1` or local text/html capture | `extract_sections(html)` | 실제 URL과 local UTF-8 html/text를 수용한다. binary는 거부한다. |
| PDF (text) | `pdf` | `supported` | `pdf_text_extract_v1` | `docling markdown -> pypdf pages/outlines` | text-first PDF는 canonical section과 provenance를 만든다. |
| PDF (scan) | `pdf` | `supported_with_review` | `pdf_text_extract_v1` | `docling OCR -> canonical section` | OCR 경로를 타며 품질이 낮으면 review/degraded 판단이 붙는다. |
| Markdown | `md` | `supported` | `markdown_text_capture_v1` | heading/code-aware text normalization | heading hierarchy와 fenced code를 보존한다. |
| AsciiDoc | `asciidoc` | `supported` | `asciidoc_text_capture_v1` | heading/code-aware text normalization | section hierarchy를 canonical section으로 만든다. |
| Plain Text | `txt` | `supported` | `plain_text_capture_v1` | numeric heading + plain text normalization | structured heading이 없으면 title 중심 fallback section이 된다. |
| Word (`.docx`) | `docx` | `supported` | `docx_structured_capture_v1` | `python-docx -> structured markdown-like text -> canonical section` | heading/table를 살리고 paragraph를 section text로 묶는다. |
| PowerPoint (`.pptx`) | `pptx` | `supported` | `pptx_slide_capture_v1` | `python-pptx -> slide/title/text/table extraction -> canonical section` | slide별로 section을 만들고 text/table을 보존한다. |
| Excel (`.xlsx`) | `xlsx` | `supported` | `xlsx_sheet_capture_v1` | `openpyxl -> sheet/table extraction -> canonical section` | worksheet별 section과 tagged table text를 만든다. |
| Image (`.png/.jpg/.jpeg`) | `image` | `supported_with_review` | `image_ocr_capture_v1` | `docling OCR -> markdown -> canonical section` | OCR 품질에 따라 review가 필요하다. |
| CSV | 없음 | `rejected` | 없음 | 없음 | 표 구조와 provenance contract가 아직 없다. |
| ZIP / archive bundle | 없음 | `rejected` | 없음 | 없음 | 다중 파일 routing contract가 아직 없다. |
| Legacy Office (`.doc`, `.ppt`, `.xls`) | 없음 | `rejected` | 없음 | 없음 | binary legacy parser contract가 없다. |

## Mandatory Review Rules

- `pdf scan`과 `image OCR`은 기본적으로 `supported_with_review`다.
- OCR 결과에 heading/path/command 구분이 약하면 `quality_status != ready`로 내려야 한다.
- 포맷이 수용되더라도 `canonical section = 0`이면 즉시 실패다.

## Customer Self-Service Rebuild Scope

고객 자체 rebuild 범위는 아래와 정확히 일치해야 한다.

- `supported`
  - customer self-service rebuild 허용
- `supported_with_review`
  - rebuild 는 허용하지만 결과는 review-needed 또는 degraded 로 내려갈 수 있다.
- `rejected`
  - self-service rebuild 범위 밖이다.

즉 `scan PDF`, `image OCR` 은 self-service 에서도 올릴 수 있지만, review 없이 바로 production-ready 라고 말하지 않는다.

## Explicit Non-Promise

- `어떤 파일이든 완벽히 플레이북이 된다`고 말하지 않는다.
- `표/도표/레이아웃이 원본과 100% 동일하게 복원된다`고 말하지 않는다.
- `OCR 결과가 무조건 production-ready`라고 말하지 않는다.
