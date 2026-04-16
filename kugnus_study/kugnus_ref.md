맞아. **이 단계에선 구현보다 레퍼런스 프레이밍이 더 중요해.**  
잘못된 레퍼런스를 잡으면 문서 UX는 예쁜데 검색이 구리고, RAG는 되는데 운영자가 못 쓰는 이상한 플랫폼이 나오기 쉬워요. [atlassian](https://www.atlassian.com/blog/loom/software-documentation-best-practices)

## 레퍼런스 축

레퍼런스는 하나만 보면 안 되고, 최소한 **문서 UX**, **docs-as-code 운영 방식**, **RAG 구조화 방식** 세 축으로 나눠 잡아야 해요. [hyperlint](https://hyperlint.com/blog/5-critical-documentation-best-practices-for-docs-as-code/)
GitBook과 Mintlify 비교에서도 보이듯 GitBook은 협업/비개발자 친화, Mintlify는 개발자 중심 docs-as-code와 빠른 API 문서 경험에 강점이 있어 서로 참조 포인트가 달라요. [gitbook](https://www.gitbook.com/blog/gitbook-vs-mintlify)

## 문서 UX 기준

문서 플랫폼 레퍼런스로는 탐색 구조, breadcrumb, persistent sidebar, TOC, FAQ/트러블슈팅, 템플릿 일관성을 먼저 봐야 해요. [tutorial](https://www.tutorial.ai/b/software-documentation-best-practices)
즉 “예쁜 사이트”가 아니라, 사용자가 **지금 어디 있는지**, **무엇과 연결되는지**, **어떻게 다음 액션으로 가는지**가 드러나는 문서 제품을 레퍼런스로 잡아야 해요. [google.github](https://google.github.io/styleguide/docguide/best_practices.html)

## RAG 기준

RAG 쪽 레퍼런스는 화면보다 코퍼스 구조를 봐야 해요; single-topic chunking, hierarchical chunking, hybrid retrieval, reranking, evaluation 루프 같은 기준이 핵심입니다. [regal](https://www.regal.ai/blog/rag-playbook-structuring-knowledge-bases)
특히 큰 공식 매뉴얼을 다룰수록 문서를 예쁘게 모아놓는 것보다, retrieval-friendly하게 구조화했는지가 실제 성능을 좌우해요. [arxiv](https://arxiv.org/abs/2501.07391)

## 네 플랫폼에 맞는 기준

너 같은 케이스는 “문서 사이트 레퍼런스”만 따라가면 부족하고, **지식 운영 플랫폼 레퍼런스**로 봐야 해요. [augmentcode](https://www.augmentcode.com/guides/10-enterprise-code-documentation-best-practices)
왜냐면 네 목표가 단순 게시가 아니라, 원문 보존·정규화·위키형 브라우징·RAG 질의응답·폐쇄망 학습까지 이어지는 운영체계이기 때문이에요. [hyperlint](https://hyperlint.com/blog/5-critical-documentation-best-practices-for-docs-as-code/)

## 잡는 방법

추천 방식은 이거예요. [chatrag](https://www.chatrag.ai/blog/2026-02-06-7-best-practices-for-rag-implementation-that-actually-improve-your-ai-results)
- **UI 레퍼런스 3개**: 문서 읽기 경험, 정보 구조, 탐색성. [tutorial](https://www.tutorial.ai/b/software-documentation-best-practices)
- **운영 레퍼런스 3개**: Git 연동, 버전관리, 배포/검수 파이프라인. [linkedin](https://www.linkedin.com/learning/creating-technical-documentation-with-github/best-practices-for-collaborative-documentation)
- **RAG 레퍼런스 3개**: chunking, metadata, retrieval, evaluation 방식. [regal](https://www.regal.ai/blog/rag-playbook-structuring-knowledge-bases)

## 추천 프레임

네가 레퍼런스를 고를 때는 “이 서비스 예쁘네”가 아니라 아래 질문으로 걸러야 해요. [redwerk](https://redwerk.com/blog/rag-best-practices/)
- 이 구조가 원문 보존과 정규화 문서 둘 다 수용 가능한가. [hyperlint](https://hyperlint.com/blog/5-critical-documentation-best-practices-for-docs-as-code/)
- 이 탐색 UX가 검색 없이도 학습 흐름을 만들 수 있는가. [atlassian](https://www.atlassian.com/blog/loom/software-documentation-best-practices)
- 이 코퍼스 구조가 RAG에서 청크 단위 정답률을 높이는가. [arxiv](https://arxiv.org/abs/2501.07391)
- 이 운영 방식이 폐쇄망/엔터프라이즈 변경 관리에 맞는가. [augmentcode](https://www.augmentcode.com/guides/10-enterprise-code-documentation-best-practices)

원하면 다음엔 내가 바로 **“너 플랫폼용 레퍼런스 선정표”** 형태로,  
`문서 UX / 데이터 파이프라인 / RAG / 운영관리 / 디자인 시스템`  
이 5축으로 정리해서 구체적으로 뽑아줄게. [chatrag](https://www.chatrag.ai/blog/2026-02-06-7-best-practices-for-rag-implementation-that-actually-improve-your-ai-results)