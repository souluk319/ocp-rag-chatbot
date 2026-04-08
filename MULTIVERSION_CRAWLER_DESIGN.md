# Multiversion Crawler Design

## 목적

이 문서는 OCP 4.16~4.21 / `ko,en` / `html-single` 기준의 version-aware crawler 설계를 고정한다.
목표는 단순 크롤링이 아니라 아래 두 출력의 공통 입력을 만드는 것이다.

- `corpus artifacts`
- `playbook document / viewer artifacts`

현재 단계 범위는 `18-1 version-aware crawler 설계`다.
즉 source catalog, source fingerprint, update flow, 최소 구현 변경점을 정의한다.

## 설계 원칙

1. source catalog는 처음부터 멀티버전/멀티언어를 담는다.
2. `source_state`와 `content_status`를 분리한다.
3. runtime pack은 멀티버전 catalog의 부분집합만 사용한다.
4. `source_fingerprint`는 로컬 정책이 아니라 upstream source identity만 반영한다.
5. 번역 lane은 제외가 아니라 `en_only -> translated_ko_draft -> approved_ko` 상태 흐름으로 이어진다.

## 용어

- `catalog`: version/language/source 상태를 모두 담는 전체 수집 대상 목록
- `runtime manifest`: 현재 서비스에 실제로 쓰는 승인된 목록
- `source_state`: upstream source 관점의 상태
- `content_status`: 내부 코퍼스/번역/승인 관점의 상태

## 제안 schema

### 1. SourceManifestEntry 확장

현재 [SourceManifestEntry](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/models.py) 를 아래 필드로 확장한다.

필수 identity 필드:

- `product_slug: str`
- `ocp_version: str`
- `docs_language: str`
- `source_kind: str`
- `book_slug: str`
- `source_url: str`
- `viewer_path: str`

권장 source 관측 필드:

- `resolved_source_url: str`
- `resolved_language: str`
- `source_state: str`
- `source_state_reason: str`
- `index_url: str`
- `catalog_source_label: str`

기존 내부 품질/승인 필드는 유지:

- `title`
- `vendor_title`
- `high_value`
- `content_status`
- `citation_eligible`
- `citation_block_reason`
- `viewer_strategy`
- `body_language_guess`
- `hangul_section_ratio`
- `hangul_chunk_ratio`
- `fallback_detected`
- `approval_status`
- `approval_notes`

### 2. source_state 정의

`source_state`는 upstream source availability/shape만 뜻한다.

추천 값:

- `published_native`
- `fallback_to_en`
- `en_only`
- `missing`
- `blocked`

의미:

- `published_native`: 요청한 버전/언어의 문서가 정상 게시됨
- `fallback_to_en`: `ko`로 요청했지만 실제 본문/링크가 영어 fallback
- `en_only`: 해당 버전은 사실상 영어만 제공
- `missing`: index에는 없거나 target page를 찾지 못함
- `blocked`: 접근 실패, 403, robots, 네트워크 정책 등으로 수집 불가

### 3. content_status 유지

`content_status`는 지금처럼 내부 workflow 상태다.

- `approved_ko`
- `translated_ko_draft`
- `mixed`
- `en_only`
- `blocked`
- `unknown`

정리:

- `source_state` = upstream 관측 상태
- `content_status` = 내부 제품 편입 상태

두 필드는 합치지 않는다.

## source_fingerprint 규칙

현재 fingerprint는 `title`, `high_value` 같은 로컬 정책 필드가 섞여 있다.
이건 재수집 기준으로는 약하다.

새 `source_fingerprint`는 아래 조합으로 잡는 것을 권장한다.

- `product_slug`
- `ocp_version`
- `docs_language`
- `source_kind`
- `book_slug`
- `source_url`
- `viewer_path`
- `resolved_language`

제외할 필드:

- `high_value`
- `approval_status`
- `content_status`
- `citation_eligible`
- `title`

이유:

- 위 필드는 로컬 정책/표현 변경이지 upstream source identity가 아니다.
- 이 필드가 바뀌었다고 raw html 재수집이 일어나면 불필요한 churn이 생긴다.

추가로 raw HTML 수준에서는 지금처럼 `raw_html_sha256`를 따로 둔다.

정리:

- `source_fingerprint`: source identity fingerprint
- `raw_html_sha256`: 실제 본문 내용 fingerprint

## catalog 구조

top-level catalog는 version/language 범위를 스스로 설명해야 한다.

추천 top-level payload:

```json
{
  "version": 2,
  "source": "docs.redhat.com html-single catalog",
  "product_slug": "openshift_container_platform",
  "source_kind": "html-single",
  "versions": ["4.16", "4.17", "4.18", "4.19", "4.20", "4.21"],
  "languages": ["ko", "en"],
  "count": 0,
  "entries": []
}
```

runtime approved manifest는 여전히 현재 active pack subset만 담는다.

즉:

- `catalog` = 전체 버전/언어 소스 inventory
- `runtime manifest` = 현재 서비스용 승인 subset

## update flow

### Step 1. catalog enumerate

버전/언어 matrix를 돈다.

- `4.16~4.21`
- `ko`, `en`

각 조합마다:

1. docs index URL 생성
2. index fetch
3. html-single 링크 parse
4. `SourceManifestEntry` 생성

### Step 2. collect & observe

각 entry collect 시:

1. raw html fetch
2. redirect/final URL 확인
3. `resolved_source_url` 저장
4. `body_language_guess` 계산
5. `fallback_detected` 계산
6. `source_state`, `resolved_language` 결정
7. `source_fingerprint`, `raw_html_sha256` 저장

### Step 3. approval lane

collect 후:

- `source_state`
- `body_language_guess`
- `hangul_section_ratio`
- `hangul_chunk_ratio`

를 기준으로 `content_status`를 판정한다.

예:

- `published_native + ko` -> `approved_ko` 후보
- `fallback_to_en` -> `translated_ko_draft` 후보
- `en_only` -> `en_only`

### Step 4. runtime subset selection

active pack 예: `OpenShift 4.20`

runtime manifest는 전체 catalog에서:

- `ocp_version == 4.20`
- `docs_language == ko`
- `approved_ko`

조건을 만족하는 subset을 뽑는다.

이 구조면 이후 4.16~4.21 확장은 catalog 쪽에서 먼저 준비되고,
runtime pack은 선택만 바꾸면 된다.

## 최소 구현 파일 변경 후보

### 필수

- [src/play_book_studio/ingestion/models.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/models.py)
  - `SourceManifestEntry` 확장
  - `source_state` 상수 정의

- [src/play_book_studio/ingestion/manifest.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/manifest.py)
  - version/language matrix enumerate
  - top-level catalog v2 구조
  - new fingerprint 조합
  - update report를 `version/language/book_slug` 기준으로 비교

- [src/play_book_studio/ingestion/collector.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/collector.py)
  - `resolved_source_url`
  - `resolved_language`
  - `source_state`
  - `source_state_reason`
  메타데이터 기록

- [src/play_book_studio/config/settings.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/settings.py)
  - supported versions / languages 설정
  - active pack은 유지하되 catalog 범위를 따로 읽는 설정 추가

- [scripts/build_source_manifest.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/scripts/build_source_manifest.py)
  - `--versions`
  - `--languages`
  - multi-version catalog refresh

### 바로 다음 단계에서 영향 받는 파일

- [src/play_book_studio/ingestion/approval_report.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/approval_report.py)
  - `source_state`와 `content_status`를 같이 보고 판정

- [src/play_book_studio/config/corpus_policy.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/corpus_policy.py)
  - version/language-aware gap 정책 확장

- [manifests/ocp_ko_4_20_html_single.json](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/manifests/ocp_ko_4_20_html_single.json)
  - 단일 버전 manifest에서 multi-version catalog로 역할 전환 또는 별도 global catalog 도입

## 구현 순서 제안

1. `SourceManifestEntry` schema 확장
2. manifest catalog v2 작성
3. collector metadata 확장
4. `build_source_manifest.py` multi-version 옵션 추가
5. approval/report가 새 상태를 이해하게 확장
6. active runtime manifest는 4.20/ko만 유지

## 이번 단계 산출물

18-1이 끝나면 아래가 나와야 한다.

- 버전/언어/source 상태를 담는 catalog schema
- source identity fingerprint 규칙
- update flow
- 최소 구현 파일 목록

이후 18-2에서는 이 source catalog를 입력으로 받아 canonical doc AST를 설계한다.

## 18-1 구현 기준선

현재 코드에 이미 반영한 1차 구현은 아래와 같다.

- [src/play_book_studio/config/settings.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/config/settings.py)
  - `supported_ocp_versions`
  - `supported_docs_languages`
  - `supported_source_kinds`
  - `source_catalog_scope`
  - default source catalog path를 `ocp_multiversion_html_single_catalog.json` 로 전환

- [src/play_book_studio/ingestion/models.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/models.py)
  - `SourceManifestEntry` 에 `product_slug`, `ocp_version`, `docs_language`, `source_kind`
  - `resolved_source_url`, `resolved_language`
  - `source_state`, `source_state_reason`, `catalog_source_label`
  추가

- [src/play_book_studio/ingestion/manifest.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/manifest.py)
  - multi-version catalog build
  - runtime subset selection
  - identity 기반 fingerprint 및 update report

- [src/play_book_studio/ingestion/collector.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/ingestion/collector.py)
  - raw html metadata에 `version/language/resolved_* / source_state` 기록

- [scripts/build_source_manifest.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/scripts/build_source_manifest.py)
  - `--versions`, `--languages` 지원

이 기준선의 의미:

- source catalog는 이제 `global inventory`
- runtime manifest는 `현재 pack subset`
- approval/data-quality/retrieval 런타임은 전역 catalog를 읽더라도 현재 `ocp_version/docs_language` 범위만 본다

## 18-2 연결 메모

다음 단계 AST는 `ingestion`이나 `intake` 안이 아니라 별도 `canonical` 패키지로 올리는 쪽이 맞다.

권장 패키지:

- `src/play_book_studio/canonical/models.py`
- `src/play_book_studio/canonical/html.py`
- `src/play_book_studio/canonical/pdf.py`
- `src/play_book_studio/canonical/validate.py`
- `src/play_book_studio/canonical/project_corpus.py`
- `src/play_book_studio/canonical/project_playbook.py`

핵심 원칙:

- `CanonicalDocumentAst` 가 source of truth
- `NormalizedSection` 은 AST의 corpus projection
- playbook 문서/뷰어는 AST의 playbook projection
