# Canonical AST Design

## 목적

이 문서는 `고품질 코퍼스 + 사람이 읽는 플레이북 문서`를 같은 원천 구조에서 만들기 위한
canonical AST 설계 기준을 고정한다.

핵심 원칙:

- `canonical AST`가 source of truth
- corpus 출력은 `AST -> corpus projection`
- playbook 문서 출력은 `AST -> playbook projection`
- 현재 `NormalizedSection`은 원본이 아니라 이후 projection 결과가 된다

## 패키지 위치

- [canonical](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical)

구성:

- [models.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/models.py)
- [project_corpus.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_corpus.py)
- [project_playbook.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py)
- [validate.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/validate.py)

## 핵심 모델

### `CanonicalDocumentAst`

- 문서 단위 공통 원천 구조
- source language / display language / translation status / provenance를 함께 가진다

### `CanonicalSectionAst`

- section 단위 공통 구조
- `heading`, `level`, `path`, `anchor`, `semantic_role`, `blocks`

### block 종류

- `ParagraphBlock`
- `PrerequisiteBlock`
- `ProcedureBlock`
- `CodeBlock`
- `NoteBlock`
- `TableBlock`
- `AnchorBlock`

즉 `heading / prerequisite / procedure / code / note-warning / table / anchor`를
typed block으로 들고 있게 된다.

## corpus projection

corpus projection은 [project_corpus.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_corpus.py) 가 맡는다.

현재 flatten 규칙:

- paragraph -> plain text
- prerequisite -> `사전 요구 사항:` + bullet
- procedure -> numbered step
- code -> `[CODE]...[/CODE]`
- note -> `[WARNING]`, `[NOTE]` 같은 label text
- table -> `[TABLE]...[/TABLE]`

즉 retrieval은 flat text를 보되, 원본 의미는 AST에 남긴다.

## playbook projection

playbook projection은 [project_playbook.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/project_playbook.py) 가 맡는다.

여기서는 block marker를 다시 파싱하지 않고,
typed block을 그대로 viewer/문서 렌더링으로 넘기는 구조를 목표로 한다.

## 검증

[validate.py](/C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/src/play_book_studio/canonical/validate.py)는 현재 아래를 검사한다.

- 문서 id/title 누락
- section id 중복
- heading 누락
- empty block section
- duplicate anchor

## 다음 단계

18-2의 다음 구현 순서:

1. HTML -> AST parser
2. PDF -> AST parser
3. AST -> `NormalizedSection` 실제 연결
4. AST -> `CanonicalBook` / viewer artifact 실제 연결
5. 기존 marker 기반 renderer는 fallback로만 유지
