# Stage 5 Direct Runtime Check

- Generated at: `2026-04-01T02:59:53Z`
- Base URL: `http://127.0.0.1:8000`
- Health: `{"status_code": 200, "ok": true, "body": {"ok": true, "company_base_url_configured": true, "chat_model_configured": true, "embedding_model_configured": true, "embedding_dimensions": 1024, "company_token_configured": false, "opendocuments_base_url_configured": true, "default_chat_mode": "operations", "local_chat_fallback": false, "forward_client_auth": false, "runtime_mode": "company-only", "missing_required_keys": [], "missing_gateway_keys": [], "active_index_id": "s15c-core", "active_manifest_path": "C:\\Users\\soulu\\cywell\\ocp-rag-chatbot\\data\\staging\\s15c\\manifests\\staged-manifest.json", "active_document_count": 1201}}`
- Passed cases: `5/5`

| Case | Korean response | Citations | First viewer | Status |
| --- | --- | ---: | --- | --- |
| `오픈시프트가 뭐야` | `true` | `2` | `pass` | `pass` |
| `OCP가 뭐야` | `true` | `2` | `pass` | `pass` |
| `업데이트 전에 확인해야 할 사항은 무엇인가요?` | `true` | `2` | `pass` | `pass` |
| `방화벽 설정에서 어떤 포트를 열어야 하나요?` | `true` | `3` | `pass` | `pass` |
| `disconnected/oc-mirror 관련 문서는 어디를 보면 되나요?` | `true` | `3` | `pass` | `pass` |

## Notes

- This check hits `localhost:8000` directly and does not modify app logic.
- Each case records Korean response presence, citation count, and the first viewer reachability.
- A case passes only when all three are true.

## Case Details

### def-01
- Query: `오픈시프트가 뭐야`
- Status: `pass`
- Korean response: `True`
- Citation count: `2`
- First viewer reachable: `True`
- Viewer URL: `http://127.0.0.1:8000/viewer/openshift-docs-core-validation/architecture/architecture.html`
- Answer preview: [기준 버전: OpenShift 4.x]

OpenShift Container Platform(OCP)는 Red Hat이 제공하는 엔터프라이즈 Kubernetes 플랫폼입니다.
애플리케이션 배포뿐 아니라 클러스터 설치, 업데이트, 네트워킹, 보안, 모니터링 같은 운영 기능을 공식적으로 제공합니다.
공식 문서에서는 "OpenShift Container Platform is a platform for developing and r
- Error: ``

### def-02
- Query: `OCP가 뭐야`
- Status: `pass`
- Korean response: `True`
- Citation count: `2`
- First viewer reachable: `True`
- Viewer URL: `http://127.0.0.1:8000/viewer/openshift-docs-core-validation/architecture/architecture.html`
- Answer preview: [기준 버전: OpenShift 4.x]

OCP는 OpenShift Container Platform의 약자입니다.
OpenShift Container Platform(OCP)는 Red Hat이 제공하는 엔터프라이즈 Kubernetes 플랫폼입니다.
애플리케이션 배포뿐 아니라 클러스터 설치, 업데이트, 네트워킹, 보안, 모니터링 같은 운영 기능을 공식적으로 제공합니다.
공식 문서에서는 "OpenShift Container P
- Error: ``

### ops-01
- Query: `업데이트 전에 확인해야 할 사항은 무엇인가요?`
- Status: `pass`
- Korean response: `True`
- Citation count: `2`
- First viewer reachable: `True`
- Viewer URL: `http://127.0.0.1:8000/viewer/openshift-docs-core-validation/architecture/architecture.html`
- Answer preview: [기준 버전: OpenShift 4.x]
[주의: 운영 영향이 있는 작업일 수 있으므로 적용 전에 현재 클러스터 버전과 공식 문서를 다시 확인하세요.]

[unverified] Based on the provided context, there is **no specific documentation available** to detail the exact steps or requirements for updating OpenSh
- Error: ``

### ops-02
- Query: `방화벽 설정에서 어떤 포트를 열어야 하나요?`
- Status: `pass`
- Korean response: `True`
- Citation count: `3`
- First viewer reachable: `True`
- Viewer URL: `http://127.0.0.1:8000/viewer/openshift-docs-core-validation/architecture/architecture.html`
- Answer preview: [기준 버전: OpenShift 4.x]

[unverified] Based on the context provided, it is **not possible** to provide precise configuration instructions for opening specific firewall ports for OpenShift 4.x. [unverified] The provided context explicitly sta
- Error: ``

### ops-03
- Query: `disconnected/oc-mirror 관련 문서는 어디를 보면 되나요?`
- Status: `pass`
- Korean response: `True`
- Citation count: `3`
- First viewer reachable: `True`
- Viewer URL: `http://127.0.0.1:8000/viewer/openshift-docs-core-validation/architecture/architecture.html`
- Answer preview: [기준 버전: OpenShift 4.x]
[주의: 운영 영향이 있는 작업일 수 있으므로 적용 전에 현재 클러스터 버전과 공식 문서를 다시 확인하세요.]

[unverified] 제공된 문맥에는 **disconnected/oc-mirror** 또는 **disconnected mirroring**에 대한 관련 문서가 포함되어 있지 않습니다. [unverified] *   **결측 정보**: 요청하신 주제 (source archit
- Error: ``
