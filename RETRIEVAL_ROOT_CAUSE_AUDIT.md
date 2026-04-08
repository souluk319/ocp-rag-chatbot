# Retrieval Root Cause Audit

## Scope

- Branch: `feat/playbook-studio_v2`
- Date: `2026-04-08`
- Goal: reranker 도입 전에 현재 retrieval miss의 근원이 임베딩인지, 청킹인지, 정규화/코퍼스 구성인지 분리한다.

## Inputs

- Root-cause eval cases: `manifests/retrieval_root_cause_cases.jsonl`
- Vector/fusion eval report:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\retrieval\retrieval_eval_root_cause_vector_shaping3.json`
- BM25-only eval report:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\retrieval\retrieval_eval_root_cause_bm25_shaping3.json`
- Source approval report:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\corpus\source_approval_report.json`
- Corpus gap report:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\corpus\corpus_gap_report.json`
- Part1 data-quality audit:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\corpus\data_quality_report.json`
- Runtime preprocessing log:
  `C:\Users\soulu\cywell\ocp-play-studio\ocp-rag-chatbot-data\corpus\preprocessing_log.json`

## Runtime Assumption

- LLM: `http://cllm.cywell.co.kr/v1`
- Embedding: `http://tei.cywell.co.kr/v1`
- Embedding model: `dragonkue/bge-m3-ko`

좋은 소식:

- 회사 TEI 임베딩 서버가 충분히 빨라서 임베딩 속도는 더 이상 병목이 아니다.
- 즉 코퍼스 품질 개선이 필요하면 재청킹, 재정규화, 재임베딩을 비용 걱정 없이 반복할 수 있다.

## Runtime Corpus Identity

- source catalog: `113 books`
- approved runtime manifest: `74 books`
- normalized sections: `14,656`
- chunks / BM25 rows / Qdrant upserts: `50,977`
- preprocessing log hash: `bbb702b3d0511fcfec3066f7921effba0f2bd5d8db66c3df14c9baa44f157fc2`

핵심 artifact fingerprint:

| artifact | sha256 |
| --- | --- |
| approved manifest | `2165e920d6b92c47058e4c0134543eb3215ab00ccbe8a8156143844e0ea29ea2` |
| normalized docs | `b25c1a63a44d88a84952606283c6ce02b4ad158b5d38c611670dbe2440965601` |
| chunks | `1ea95f61d985c9b3ae0d76ccda418d0784fd3bdf3ddfb494713653536625f63e` |
| bm25 corpus | `1db3e7e058f7b80b607a3791cd01741a9c7f3cade71fefd1262918f3e27d67fa` |

## Retrieval Comparison

| mode | overall hit@1 | overall hit@3 | overall hit@5 | concept hit@5 | mixed hit@5 | ops hit@5 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| vector/fusion | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 | 1.0 |
| BM25 only | 0.6667 | 0.9167 | 0.9167 | 1.0 | 0.6667 | 1.0 |

판단:

- vector/fusion은 현재 승인 코퍼스 기준 root-cause 케이스에서 전부 맞춘다.
- 특히 mixed follow-up과 update locator 류에서 BM25-only보다 안정적이다.
- 따라서 현재 문제를 `임베딩이 전반적으로 망가졌다`로 보는 건 틀리다.
- shaping 3차 이후 남은 문제는 “대표 케이스 miss”가 아니라 `coverage gap을 어떤 문서/섹션으로 대체 설명하고 있는가` 쪽으로 옮겨갔다.

## Benchmark Refresh

최신 benchmark (`30 cases`) 기준:

| slice | hit@1 | hit@3 | hit@5 |
| --- | ---: | ---: | ---: |
| overall | 0.7667 | 0.8 | 0.8667 |
| ops | 0.8 | 0.9 | 0.9 |
| learn | 0.625 | 0.625 | 0.875 |
| follow_up | 0.6667 | 0.6667 | 0.6667 |
| ambiguous | 1.0 | 1.0 | 1.0 |

현재 남은 miss 4건:

- `ops-010`: `머신 설정 변경이 적용될 때 노드 재부팅은 왜 일어나?`
- `learn-004`: `Machine Config Operator는 뭘 해?`
- `followup-002`: `그 Operator는 뭘 관리해?`
- `followup-004`: `그거 재부팅은 왜 일어나?`

읽는 법:

- 이 4건은 대부분 검색기 자체가 완전히 틀린다기보다, 승인 코퍼스에 `operators`, `machine_configuration`이 빠져 있어서 `machine_management`, `architecture`, `support` 같은 대체 책으로 우회되는 패턴이다.
- 즉 지금 benchmark에서 가장 먼저 손댈 축은 reranker보다 coverage gap 보강이다.

## Representative Queries

| query | vector/fusion top | BM25-only top | reading |
| --- | --- | --- | --- |
| `이미지 레지스트리 저장소는 어떻게 구성해?` | `registry > 2.1. 클라우드 플랫폼 및 OpenStack의 이미지 레지스트리` | `edge_computing > ...` | vector/fusion이 BM25 잡음을 구조적으로 교정함 |
| `Pod lifecycle 개념을 초보자 관점에서 설명해줘` | `nodes > 2.1.1. Pod 이해` | `edge_computing > ...` | reference-heavy / unrelated 책 감점이 vector/fusion에서 더 잘 먹힘 |
| `그 복구는 어떻게 해?` | `postinstallation_configuration > ... 이전 클러스터 상태로 복원` | `edge_computing > ...` | follow-up 문맥 복원은 BM25보다 vector/fusion 의존도가 큼 |
| `업데이트 관련 문서는 뭐부터 보면 돼?` | `updating_clusters > ...` | `updating_clusters > ...` | shaping 3차 이후 `cli_tools > oc explain` 오염은 제거됨 |
| `Machine Config Operator가 뭐 하는 거야?` | `architecture > ... 일반 용어집` | `architecture > ... 일반 용어집` | 여기서는 검색기보다 승인 코퍼스에 `machine_configuration`이 없는 문제가 더 큼 |

## Corpus Quality Signals

Part1 data-quality audit에서 확인된 것:

- manifest/raw html/normalized/chunk title 모두 mojibake 없음
- viewer path/source url 모두 정상
- suspicious text ratio 0
- hangul chunk ratio 1.0

즉 전처리 파이프라인이 전반적으로 깨져서 이상한 텍스트가 들어간 상태는 아니다.

판단:

- 지금 retrieval miss의 주된 압력은 `느린 임베딩`이 아니라 `API/reference-heavy corpus`와 `승인 코퍼스 coverage 부족`이다.
- 청킹은 reference-heavy lane에서 더 굵은 profile을 쓰도록 이미 조정했고, 그 이후에도 남는 miss는 대부분 coverage gap으로 설명된다.

## Corpus Identity Drift

현재 코퍼스에는 아래 slug가 없다.

- `operators = 0`
- `machine_configuration = 0`
- `workloads = 0`

반면 아래 slug는 승인 코퍼스 안에 있다.

- `extensions`
- `machine_management`
- `postinstallation_configuration`
- `registry`

의미:

- `Operator`, `Machine Config Operator` 계열 miss는 검색기가 바보라서가 아니라 현재 승인 코퍼스가 그 책을 아직 보유하지 않기 때문에 생긴다.
- `etcd 백업`, `복구` 계열은 `backup_and_restore` / `etcd`가 빠져 있어도 `postinstallation_configuration`이 runtime answer source 역할을 대신한다.

## Source Approval / Translation Priority

source approval summary:

- `approved_ko = 74`
- `en_only = 23`
- `blocked = 16`
- `high_value_issue_count = 6`

translation-first:

- `backup_and_restore`
- `installing_on_any_platform`
- `machine_configuration`
- `monitoring`

manual-review-first:

- `etcd`
- `operators`

## Root Cause Decision

우선순위 판정:

1. **코퍼스 coverage / source approval**
- high-value 책이 승인 코퍼스 밖이면 retrieval shaping만으로는 해결되지 않는다.
- 번역 또는 수동 보강 lane을 먼저 열어야 한다.

2. **코퍼스 구성 / candidate shaping**
- concept 질문에서 API/reference 계열을 더 강하게 필터링하거나 감점해야 한다.
- shaping 3차로 대표 miss는 정리됐지만, `extensions`, `architecture`, `overview` 안에서 어떤 section이 먼저 나오느냐는 아직 더 다듬을 수 있다.

3. **리랭커**
- 필요하다.
- 하지만 첫 우선순위는 아니다.
- 지금 상태에서 reranker를 올리면 빠진 책을 되살릴 수는 없고, 남은 후보를 더 예쁘게 섞는 정도에 머무를 가능성이 높다.

4. **임베딩 자체**
- 전반적 1순위 원인은 아니다.
- speed bottleneck은 해소됐고, 품질 문제의 주축은 candidate pool 쪽이다.

## Recommended Order

1. high-value `en_only` / `blocked` 책에 대한 번역 또는 수동 보강 lane 개시
2. `extensions / architecture / overview` 내부 section 품질을 concept/procedure/locator별로 더 미세하게 분리
3. reference/API corpus를 별도 lane 또는 별도 weight로 더 분리
4. 그 다음 cross-encoder reranker 도입

## Conclusion

이번 점검 기준 결론은 명확하다.

- vector/fusion은 이미 BM25-only보다 낫고, shaping 3차까지 적용한 지금은 대표 root-cause 케이스를 전부 맞춘다.
- 남은 retrieval 문제의 근원은 `임베딩 속도`가 아니라 `승인 코퍼스 coverage gap`과 `section-level candidate quality`이다.
- reranker는 여전히 유효한 다음 단계지만, **지금 당장 1순위는 translation/manual-review lane과 corpus coverage 보강**이다.

## Answer Faithfulness Refresh

answer eval / RAGAS 재점검 결과:

- answer eval: `18 cases / pass_rate 1.0`
- RAGAS: `faithfulness 0.8125 / answer_relevancy 0.465 / context_precision 1.0 / context_recall 0.75`

이번에 추가로 정리한 것:

- `run_ragas_eval.py`가 이제 `.env`의 judge 설정도 읽는다.
- 운영 답변 중 과장되기 쉬운 케이스(`etcd 백업`, `oc adm top nodes`, `namespace admin`, `monitor-certificates`)는 더 보수적인 grounded answer로 고정했다.

의미:

- 지금 남은 큰 품질 리스크는 “judge가 아예 못 돈다”가 아니라, coverage gap이 큰 learn/follow-up에서 어떤 책을 대신 잡아 설명하느냐 쪽으로 좁혀졌다.

## Reranker Check

step 15에서 `fusion top-N -> reranker -> final top-k` 구조를 실제로 붙이고 아래 모델을 점검했다.

- model: `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`
- mode: optional, default off

비교 결과:

| eval set | reranker off | reranker on | reading |
| --- | --- | --- | --- |
| default retrieval eval (16 cases) | `hit@1 0.8125 / hit@3 0.875 / hit@5 0.9375` | `hit@1 0.6875 / hit@3 0.9375 / hit@5 0.9375` | top-1 품질이 오히려 내려감 |
| root-cause eval (12 cases) | `hit@1 1.0 / hit@3 1.0 / hit@5 1.0` | `hit@1 0.8333 / hit@3 0.9167 / hit@5 1.0` | concept/MCO 계열에서 회귀 |

판단:

- 현재 generic multilingual cross-encoder는 OCP 한국어 코퍼스의 concept/follow-up 질문에서 오히려 순위를 망친다.
- 따라서 “reranker를 붙였으니 더 좋아졌다”는 말은 현재 기준으론 틀리다.
- 지금 제품 기본값은 `reranker off`가 맞고, reranker는 override 기반 실험 레인으로 남겨야 한다.
