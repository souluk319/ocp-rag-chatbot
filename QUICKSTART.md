# Quickstart

시연 준비 기준 최소 순서만 적는다.

## 1. 런타임 확인

```powershell
play_book.cmd runtime
```

확인 항목:
- LLM
- embedding
- Qdrant
- corpus / retrieval / answering / runtime 경로

## 2. UI 실행

```powershell
play_book.cmd ui
```

브라우저:
- `http://127.0.0.1:8765`

## 3. 기본 확인 질문

```powershell
play_book.cmd ask --query "OpenShift에서 Route와 Ingress 차이를 운영 관점에서 설명해줘"
play_book.cmd ask --query "특정 namespace에만 admin 권한 주려면 어떤 명령을 써?"
play_book.cmd ask --query "클러스터 전체 노드 CPU와 메모리 사용량을 한 번에 보려면?"
```

## 4. 시연 기준

질문 하나마다 아래 네 개를 확인한다.

1. 답변이 질문을 정면으로 받는가
2. citation이 붙는가
3. 오른쪽 참조 패널이 열리는가
4. 문서가 실제로 읽히는가

## 5. 지금 하지 말 것

- 멀티버전 실험
- 번역 lane 확장 실험
- 구조개편
- 대규모 코퍼스 재빌드

시연 전에는 `시연 질문 통과`만 본다.
