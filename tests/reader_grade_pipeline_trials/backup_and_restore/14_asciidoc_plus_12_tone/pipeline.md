# 14_asciidoc_plus_12_tone — AsciiDoc source with 12-style tone

## Goal

`13_asciidoc_source_hybrid`의 source cleanliness에 `12_refined_hybrid`의 톤앤매너와 구조를 얹어서, AsciiDoc source-first 라인이 실제로 더 나은지 확인한다.

## Source

- base source trial:
  - `13_asciidoc_source_hybrid`
- target tone / structure:
  - `12_refined_hybrid`

## Pipeline Steps

1. AsciiDoc assembly와 modules 에서 control plane backup / restore 정보만 추린다.
2. `12_refined_hybrid`의 문단 리듬, heading 구조, verification/failure 배치를 적용한다.
3. AsciiDoc source에서 나온 경고와 prerequisite 의미를 유지한다.
4. 최종 `md`로 다시 조립한다.

## Tech Stack

- Git sparse checkout
- AsciiDoc source reading
- hybrid markdown assembly
- reference-aligned tone shaping

## Notes

- 이 결과는 `입력 품질`과 `최종 톤앤매너`를 분리해서 보는 실험이다.
- `12`보다 나은지, 아니면 source만 달라졌을 뿐인지 비교하면 된다.
