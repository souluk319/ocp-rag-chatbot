# Play Book Studio

OpenShift 4.20 문서를 기반으로 답변과 근거 문서를 함께 제공하는 플레이북 제품이다.

현재 기준:
- 제품 범위: `OpenShift 4.20`
- 핵심 결과물: `RAG용 고품질 코퍼스`, `유저용 고품질 매뉴얼북`
- 현재 브랜치 목적: `시연 가능한 제품 품질 확보`

## 유지 문서

루트 문서는 아래 다섯 개만 유지한다.

- [README.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/README.md)
- [PRODUCT_BRIEF.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PRODUCT_BRIEF.md)
- [PRODUCT_ROADMAP.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PRODUCT_ROADMAP.md)
- [QUICKSTART.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/QUICKSTART.md)
- [FILE_ROLE_GUIDE.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/FILE_ROLE_GUIDE.md)

설계 메모, 백로그, 감사 문서는 루트 기준선에서 제거했다.

## 구조

```text
.
├─ manifests/
├─ scripts/
├─ src/
│  └─ play_book_studio/
├─ tests/
├─ play_book.cmd
├─ README.md
├─ PRODUCT_BRIEF.md
├─ PRODUCT_ROADMAP.md
├─ QUICKSTART.md
└─ FILE_ROLE_GUIDE.md
```

무거운 산출물은 보통 repo 밖 [ocp-rag-chatbot-data](C:/Users/soulu/cywell/ocp-play-studio/ocp-rag-chatbot-data)에 둔다.

## 실행 진입점

기준 진입점은 `play_book.cmd` 하나다.

```powershell
play_book.cmd ui
play_book.cmd ask --query "Route와 Ingress 차이를 설명해줘"
play_book.cmd eval
play_book.cmd runtime
```

실행 순서는 [QUICKSTART.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/QUICKSTART.md), 제품 정의는 [PRODUCT_BRIEF.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PRODUCT_BRIEF.md), 날짜별 목표는 [PRODUCT_ROADMAP.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/PRODUCT_ROADMAP.md), 파일 역할은 [FILE_ROLE_GUIDE.md](C:/Users/soulu/cywell/ocp-play-studio/ocp-play-studio/FILE_ROLE_GUIDE.md)를 본다.
