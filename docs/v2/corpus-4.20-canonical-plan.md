# OCP 4.20 Canonical Corpus Plan

## 목적

이 문서는 `enterprise-4.20` 기준 OCP 코퍼스를 어떻게 구성할지, 특히 `modules/` 와 `xref` 관계를 어떻게 canonical model로 복원할지를 정의합니다.

## 고정 소스

1. 공식 원천: `openshift-docs`
2. 고정 브랜치: `enterprise-4.20`
3. 고정 worktree: `C:\Users\soulu\cywell\openshift-docs-4.20`
4. 현재 고정 커밋: `683c38e6291e20bf951edff517b15810f5ce7abc`

## 왜 modules가 중요한가

`openshift-docs`는 절차형 설명을 상위 가이드 한 파일에 다 쓰지 않습니다.

실제 구조는 보통 아래와 같습니다.

1. 상위 문서가 존재한다.
2. 상위 문서가 `include::modules/...` 로 절차 조각을 불러온다.
3. 중간중간 `xref:` 로 관련 가이드나 후속 절차를 연결한다.

따라서 `modules/` 를 단순 제외하면:

1. 절차가 끊긴다.
2. 검색 결과가 단편적인 조각만 반환될 수 있다.
3. 답변이 중간에서 뚝 끊기거나 선후관계가 사라질 수 있다.

## canonical model 원칙

1. 상위 문서를 기준 문서로 본다.
2. `include::modules/...` 로 포함된 module은 상위 문서의 section tree 안으로 병합한다.
3. module 단독 경로도 lineage로 보존한다.
4. `xref:` 는 연관 문서 링크로 저장한다.
5. chunk는 가능한 한 section 경계를 보존한다.
6. procedure 성격의 section은 단계 순서를 유지한다.
7. citation은
   - 상위 문서 경로
   - section anchor
   - 관련 module lineage
   를 함께 추적할 수 있어야 한다.

## 추천 산출 구조

각 canonical document는 최소 아래 필드를 가져야 합니다.

1. `document_id`
2. `top_level_path`
3. `git_ref`
4. `source_commit`
5. `section_id`
6. `section_title`
7. `heading_hierarchy`
8. `assembled_text`
9. `included_modules[]`
10. `xref_targets[]`
11. `viewer_url`
12. `source_url`

## retrieval 관점 요구사항

1. chunk는 상위 문서 문맥을 잃지 않아야 한다.
2. module 조각만 단독으로 검색되어도 상위 가이드로 다시 연결될 수 있어야 한다.
3. `xref` 로 이어지는 후속 절차가 있으면 trace나 citation에서 보여줄 수 있어야 한다.
4. 설치/업데이트/disconnected 절차는 특히 순서가 중요하므로 canonical model이 끊기면 안 된다.

## 다음 단계

1. `enterprise-4.20` 기준 균형 코퍼스 범위 고정
2. `modules/` 포함 관계 파서 규칙 설계
3. `xref` 관계 저장 규칙 설계
4. canonical normalized corpus 생성
5. Golden Set 100으로 정확도 측정
