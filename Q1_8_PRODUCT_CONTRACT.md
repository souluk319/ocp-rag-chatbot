# Q1-8 제품 계약표

## Current Commercial Truth

이 문서는 고객의 8개 구매 질문을 `제품 수용 기준`, `증거`, `하드 블로커`로 잠그는 단일 기준 문서다.

- 현재 정직한 판매 단계는 `paid_poc_candidate` 다.
- 현재 정직한 범위는 `OpenShift 4.20 validated pack + customer document PoC` 다.
- validated pack 의 고객 출력은 `raw manual mirror` 가 아니라 `manual book + derived playable books` 다.
- raw 문서 수는 playable asset 수의 상한이 아니다. 운영/기술 질문을 제대로 받으려면 파생 북 수가 원문 수를 넘는 것이 정상이다.
- 아래 계약표 중 하나라도 미통과면 `full sale`이 아니라 `paid PoC` 또는 `pilot` 로만 말한다.

## Common Gates

아래 다섯 개는 모든 질문에 공통으로 적용한다.

1. `no_evidence_but_asserted_rate == 0` (`unsupported_assertion_rate`) 이 아니면 계약표 효력이 없다.
2. `clarification_needed_but_answered_rate == 0` (`clarification_required_but_answered`) 이 아니면 애매한 질문 대응은 미통과다.
3. 모든 핵심 답변은 `answer -> source -> version -> anchor` 추적이 가능해야 한다.
4. `unreviewed asset 노출`, `pack/version boundary 흐림`, `forbidden citation` 중 하나라도 나오면 즉시 fail 이다.
5. `persisted_session == true` 와 `audit_trail == true` 가 없으면 enterprise full sale 주장은 금지다.
6. 운영 질문의 출력이 `개요 링크 + 요약` 수준에 머물고, 실행 절차 / 명령어 / 검증 / source trace 가 보이지 않으면 플레이북 제품으로 간주하지 않는다.

## Asset Glossary

- `Source Document`
  - 수집 전/후의 원문 문서 자산
- `Manual Book`
  - 원문 매뉴얼을 canonical section / provenance / quality metadata 와 함께 다시 묶은 책
- `Derived Playbook Asset`
  - `Topic Playbook`, `Operation Playbook`, `Troubleshooting Playbook`, `Policy Overlay Book`, `Synthesized Playbook`
- `Customer Pack`
  - 고객 문서와 고객 정책을 pack boundary 안에서 묶어 노출하는 별도 배포 단위

## Q1-8 Contract Matrix

| Q ID | 구매자 질문 | Audience | Current Truth | Evidence File | Pass Condition | Hard Blocker | Non-Promise / Answer Boundary |
|---|---|---|---|---|---|---|---|
| Q1 | 데이터를 어떻게 정제하고 정규화하나? 파이프라인은 완성됐나? | technical_champion | `manifest -> collect -> normalize -> chunk -> embed -> qdrant` 파이프라인과 source 메타는 있다. 다만 `고객 문서 원문 -> 정규화 -> 플레이북 -> 답변 근거`를 buyer 시점에서 한 번에 증명하는 lineage 표면은 아직 계약으로 잠기지 않았다. | `src/play_book_studio/ingestion/pipeline.py`<br>`src/play_book_studio/ingestion/models.py`<br>`src/play_book_studio/app/source_books.py` | 고객 문서 1개 기준으로 `raw -> normalized section -> playbook section -> answer citation -> source jump`가 추적 가능해야 한다.<br>`heading/code/table` 복원율과 section provenance completeness 기준이 정의돼야 한다. | section provenance 누락<br>원문에서 답변까지 역추적 불가<br>포맷별 품질 기준 없음 | `어떤 문서든 자동으로 완벽히 정규화된다`고 말하지 않는다.<br>`완성된 범용 파이프라인`이라고 말하지 않는다. |
| Q2 | 공식문서 외 운영 응용법과 트러블슈팅은 어떻게 다루나? | enterprise_owner / technical_champion | `official_doc`, `internal_runbook`, `community_blog`, `manual_synthesis`를 담을 메타 구조는 있다. 다만 `manual book / topic playbook / troubleshooting playbook / policy overlay book` 파생 자산 계약과 공식/참고/고객정책 권위 충돌 규칙은 아직 완전히 잠기지 않았다. | `src/play_book_studio/ingestion/pipeline.py`<br>`src/play_book_studio/ingestion/models.py`<br>`src/play_book_studio/ingestion/curated_gold.py` | 답변마다 `공식 여부`, `authority badge`, `review_status`, `updated_at`가 보여야 한다.<br>공식 근거와 참고 근거가 섞여도 역할이 시각적으로 분리돼야 한다.<br>운영 질문은 개요 링크 요약이 아니라 `topic playbook` 또는 `troubleshooting playbook` 블록으로 내려와야 한다.<br>혼합 출처 질의 세트에서 unlabeled citation 이 `0` 이어야 한다. | 참고자료가 공식자료처럼 노출됨<br>authority badge 누락<br>출처 등급 없는 응용 답변<br>파생 플레이북 family 부재 | `공식이 아닌 자료도 거의 같은 신뢰도`라고 말하지 않는다.<br>`100% 신뢰`를 약속하지 않는다. |
| Q3 | 우리 회사 자료와 운영방침을 결합해 답할 수 있나? | enterprise_owner | customer-pack intake 경로와 customer document PoC 계약은 있다. 하지만 `공용 OCP 근거 + 고객사 정책 + 실행 순서`를 한 답변에서 안정적으로 결합하는 policy overlay 는 아직 실증 전이다. | `archive/legacy_reference_docs/CUSTOMER_POC_BUYER_PACKET.md`<br>`src/play_book_studio/app/intake_api.py`<br>`src/play_book_studio/app/source_books.py` | 고객 문서를 별도 pack 으로 올리고, 답변에서 `공식 OCP 근거`, `고객사 정책`, `실행 순서`를 분리해 보여줘야 한다.<br>애매한 질문에서는 clarification 이 먼저 나와야 한다.<br>`unsupported assertion = 0` 이어야 한다. | policy conflict 미해결<br>clarification 없이 단정<br>pack 경계 혼합 | `문서를 넣으면 바로 귀사 표준대로 정확히 답한다`고 말하지 않는다.<br>PoC 없이 policy-grade 품질을 약속하지 않는다. |
| Q4 | 플레이북은 구체적으로 어떤 형태로 볼 수 있나? | enterprise_owner / operator | section 카드, anchor deep-link, source origin, quality status 를 가진 viewer 는 있다. 다만 `Manual Book` 과 `Topic Playbook` 이중 표면, 실행형 블록 레이아웃, 아이콘 액션 기준은 아직 계약으로 잠기지 않았다. | `src/play_book_studio/app/source_books.py`<br>`src/play_book_studio/canonical/project_playbook.py`<br>`src/play_book_studio/app/viewer_page.py` | `Manual Book` 과 `Topic Playbook` 이 시각적으로 구분되어 보여야 한다.<br>`Topic Playbook` 은 `prerequisite -> procedure -> code -> verify -> failure signal -> source trace` 구조를 가져야 한다.<br>코드 블록에는 `copy / wrap / expand` 액션이 있고 icon-first control 로 노출되어야 한다.<br>목차, section, anchor, source URL, version, review status, quality status, citation jump 가 모두 보여야 한다.<br>챗 답변에서 플레이북과 원문으로 바로 이동 가능해야 한다. | 클릭 가능한 source trace 부재<br>version/review 메타 누락<br>manual/topic 구분 부재<br>실행 블록 없는 요약형 viewer | `북을 보여준다`를 막연한 텍스트 출력으로 포장하지 않는다.<br>`개요 링크 + 요약`을 플레이북이라고 부르지 않는다.<br>`완성된 문서 관리 시스템`이라고 말하지 않는다. |
| Q5 | OCR/GraphDB 없이 다양한 확장자에 대응 가능한가? | architect_or_security / technical_champion | 현재 intake 는 `web/html`, `text PDF`, `scan PDF`, `md/asciidoc`, `txt`, `docx`, `pptx`, `xlsx` 를 matrix/API/test 기준으로 다룬다. `scan PDF` 와 `image OCR` 은 `supported_with_review` 또는 `staged` 로 보수적으로 취급한다. Neo4j graph sidecar 는 live runtime 에 연결돼 있지만, 채택 범위는 여전히 evidence-driven 으로 유지한다. | `src/play_book_studio/app/intake_api.py`<br>`src/play_book_studio/intake/normalization/pdf.py`<br>`src/play_book_studio/retrieval/graph_runtime.py`<br>`archive/legacy_reference_docs/FORMAT_SUPPORT_MATRIX.md`<br>`archive/legacy_reference_docs/PARSER_ROUTING_POLICY.md` | `web/html`, `text PDF`, `scan PDF`, `docx`, `pptx`, `xlsx`, `md/asciidoc` 지원 여부를 `Format Support Matrix`로 명시해야 한다.<br>지원 포맷은 canonical AST + provenance 를 내야 하고, 미지원 포맷은 명시적으로 거부해야 한다.<br>OCR 경로는 필수다.<br>GraphDB 채택/비채택은 `유사 절차`, `인접 매뉴얼`, `정책 오버레이`, `provenance traversal` 케이스의 evidence packet 으로 결정해야 한다. | staged/review 경로를 ready 인 것처럼 과장<br>silent fallback 으로 실제 parser/OCR 경로를 숨김<br>포맷별 실패 경계 없음<br>유사 문서 검증 병목 미계측 | `어떤 파일이든 된다`고 말하지 않는다.<br>`GraphDB만 붙이면 해결된다`고 말하지 않는다.<br>`GraphDB가 불필요하다`고 증거 없이 말하지 않는다. |
| Q6 | 공식 매뉴얼 업데이트와 폐쇄망 유지보수는 어떻게 하나? | operator / enterprise_owner | `updated_at` 수집, refresh routine, scheduler 씨앗은 있다. 하지만 buyer-facing `요청형 유지보수`와 `고객 자체 rebuild` 운영 패키지는 아직 문서화가 덜 됐다. | `src/play_book_studio/ingestion/collector.py`<br>`pipelines/foundry_routines.json`<br>`src/play_book_studio/ingestion/foundry_scheduler.py` | `vendor-managed refresh` 와 `customer self-service rebuild` 두 모드 중 최소 하나 이상이 운영 계약으로 정의돼야 한다.<br>`last collected`, `last approved`, `next refresh`, `staleness status`를 보여줘야 한다.<br>개발자 수작업 없이 재현 가능한 rebuild 경로가 있어야 한다. | refresh 가 개발자 ad-hoc 작업에 의존<br>freshness 메타 미노출<br>폐쇄망 self-service 부재 | `실시간 자동 반영`을 약속하지 않는다.<br>`언제든 우리가 알아서 유지해준다`고 두루뭉술하게 말하지 않는다. |
| Q7 | Lightspeed 같은 대체재와 비교/병행은 어떻게 보나? | enterprise_owner / architect_or_security | 현재 저장소에는 Lightspeed 연동 흔적이나 benchmark 가 없다. 따라서 지금 가능한 답은 `무시`가 아니라 `비교/병행/비연동`을 가르는 decision memo 를 만드는 것이다. | `archive/legacy_reference_docs/OWNER_VALUE_CASE.md`<br>`archive/legacy_reference_docs/CUSTOMER_POC_BUYER_PACKET.md`<br>`Q1_8_PRODUCT_CONTRACT.md` | `Lightspeed Decision Memo`가 있어야 한다.<br>비교 질문셋, 병행 가능성, 우리 제품의 차별 범위가 문서로 잠겨야 한다.<br>`왜 우리를 사야 하는가`를 고객 문서/정책/playbook viewer/폐쇄망 self-service 기준으로 설명해야 한다. | benchmark 없이 superiority 주장<br>전략적 선택 근거 부재<br>비교 회피 | `우리가 더 낫다`고 단정하지 않는다.<br>`전략적으로 일부러 안 썼다`고 근거 없이 말하지 않는다. |
| Q8 | 제대로 된 제품이 나올 수 있나? 지금 사도 되나? | enterprise_owner | 현재 truth 는 여전히 `paid_poc_candidate` 다. 최신 runtime answer eval 은 현재 질문셋에서 pass 했고, `customer_document_reference_case_count >= 1`, `persisted_session == true`, `audit_trail == true` 는 코드/리포트/회귀 기준으로 확보했다. 다만 full-sale 승격은 owner scorecard, maintenance scope, buyer-facing 운영 gate 를 더 닫아야 한다. | `OWNER_SCENARIO_SCORECARD.yaml`<br>`archive/legacy_reference_docs/OWNER_VALUE_CASE.md`<br>`../ocp-rag-chatbot-data/answering/answer_eval_report.json`<br>`reports/build_logs/foundry_runs/runtime_report/latest.json` | 아래가 모두 충족될 때만 full sale 로 승격한다.<br>`owner_critical_scenario_pass_rate >= 0.90`<br>`evidence_linked_answer_rate >= 0.95`<br>`unsupported_assertion_rate == 0`<br>`clarification_miss_count == 0`<br>`demo_hard_miss_count == 0`<br>`persisted_session == true`<br>`audit_trail == true`<br>`customer_document_reference_case_count >= 1` | owner scorecard 미충족<br>buyer-facing 운영/유지보수 계약 미완료<br>full-sale gate 미달 | `지금 바로 전사 본판매가 가능하다`고 말하지 않는다.<br>`조금만 다듬으면 된다`고 말하지 않는다. |

## Stop / Promotion Boundary

### Stop

아래 중 하나라도 true 면 `본판매 전환 불가`로 기록한다.

- owner-demo 질문에서 하드미스가 난다.
- `clarification_required_but_answered` 가 남는다.
- `unsupported_assertion` 이 남는다.
- `unreviewed asset` 이 고객-facing 결과로 노출된다.
- `pack/version boundary` 가 흐려진다.
- `persisted_session` 또는 `audit_trail` 이 깨지거나 재현 불가능하다.

### Promotion

아래 순서가 아니면 승격을 인정하지 않는다.

1. `Trust Freeze`
   - `Q1_8_PRODUCT_CONTRACT.md`
   - `Source Authority Policy`
   - `Format Support Matrix`
   - `Closed-Network Update/Maintenance Note`
   - `Lightspeed Decision Memo`
2. `Contractable Paid PoC`
   - 고객 문서 `1~3종`
   - `time-to-first-approved-corpus <= 10 business days`
   - `unsupported_assertion_rate = 0`
   - `demo_hard_miss_count = 0`
3. `Full-Sale Readiness`
   - `persisted_session == true`
   - `audit_trail == true`
   - `customer_document_reference_case_count >= 1`
   - scorecard full-sale gate 충족

## Forbidden Wording

아래 표현은 금지한다.

- `데모에서는 잘 됐다`
- `프롬프트만 조금 더 다듬으면 된다`
- `문서가 많아지면 좋아진다`
- `나중에 붙이면 된다`
- `지금 바로 전사 본판매가 가능하다`
- `어떤 문서든 바로 된다`
- `공식 문서가 아니어도 거의 같은 신뢰도로 답한다`
- `폐쇄망의 9B 모델만으로도 클라우드급 응용력이 보장된다`
