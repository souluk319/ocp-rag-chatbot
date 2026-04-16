# Ingress 및 로드 밸런싱

## OpenShift Container Platform에서 서비스 노출 및 외부 트래픽 관리

이 문서에서는 OpenShift Container Platform에서 경로를 구성하고, 인그레스 트래픽을 관리하고, 다양한 로드 밸런싱 솔루션을 구현하는 방법을 설명합니다.

### 1.1. 기본 경로 생성

암호화되지 않은 HTTP가 있는 경우 경로 오브젝트를 사용하여 기본 경로를 만들 수 있습니다.

#### 1.1.1. HTTP 기반 경로 생성

다음 절차에 따라 `hello-openshift` 애플리케이션을 예제로 사용하여 웹 애플리케이션에 대한 간단한 HTTP 기반 경로를 생성할 수 있습니다.

공용 URL에서 애플리케이션을 호스팅할 경로를 생성할 수 있습니다. 경로는 애플리케이션의 네트워크 보안 구성에 따라 보안 또는 비보안일 수 있습니다. HTTP 기반 경로는 기본 HTTP 라우팅 프로토콜을 사용하고 안전하지 않은 애플리케이션 포트에 서비스를 노출하는 비보안 경로입니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

관리자로 로그인했습니다.

포트에서 트래픽을 수신하는 포트와 TCP 끝점을 노출하는 웹 애플리케이션이 있습니다.

프로세스

다음 명령을 실행하여 `hello-openshift` 라는 프로젝트를 생성합니다.

```shell-session
$ oc new-project hello-openshift
```

다음 명령을 실행하여 프로젝트에 Pod를 생성합니다.

```shell-session
$ oc create -f https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json
```

다음 명령을 실행하여 `hello-openshift` 라는 서비스를 생성합니다.

```shell-session
$ oc expose pod/hello-openshift
```

다음 명령을 실행하여 `hello-openshift` 애플리케이션에 대한 비보안 경로를 생성합니다.

```shell-session
$ oc expose svc hello-openshift
```

검증

생성한 `경로` 리소스가 있는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get routes -o yaml hello-openshift
```

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: hello-openshift
spec:
  host: www.example.com
  port:
    targetPort: 8080
  to:
    kind: Service
    name: hello-openshift
```

다음과 같습니다.

`host`

서비스를 가리키는 별칭 DNS 레코드를 지정합니다. 이 필드는 유효한 DNS 이름(예: `www.example.com`)일 수 있습니다. DNS 이름은 DNS952 하위 도메인 규칙을 따라야 합니다. 지정하지 않으면 경로 이름이 자동으로 생성됩니다.

`targetPort`

이 경로가 가리키는 서비스에서 선택한 Pod의 대상 포트를 지정합니다.

참고

기본 수신 도메인을 표시하려면 다음 명령을 실행합니다.

```shell-session
$ oc get ingresses.config/cluster -o jsonpath={.spec.domain}
```

#### 1.1.2. 경로 기반 라우터

경로 기반 라우터는 URL과 비교할 수 있는 경로 구성 요소를 지정하며 이를 위해 라우트의 트래픽이 HTTP 기반이어야 합니다. 따라서 동일한 호스트 이름을 사용하여 여러 경로를 제공할 수 있으며 각각 다른 경로가 있습니다. 라우터는 가장 구체적인 경로를 기반으로 하는 라우터와 일치해야 합니다.

다음 표에서는 경로 및 액세스 가능성을 보여줍니다.

| 경로 | 비교 대상 | 액세스 가능 |
| --- | --- | --- |
| www.example.com/test | www.example.com/test | 제공됨 |
| www.example.com | 없음 |
| www.example.com/test 및 www.example.com | www.example.com/test | 제공됨 |
| www.example.com | 제공됨 |
| www.example.com | www.example.com/text | 예 (경로가 아닌 호스트에 의해 결정됨) |
| www.example.com | 제공됨 |

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-unsecured
spec:
  host: www.example.com
  path: "/test"
  to:
    kind: Service
    name: service-name
```

1. 경로는 경로 기반 라우터에 대해 추가된 유일한 속성입니다.

참고

라우터가 해당 경우 TLS를 종료하지 않고 요청 콘텐츠를 읽을 수 없기 때문에 패스스루 TLS를 사용할 때 경로 기반 라우팅을 사용할 수 없습니다.

#### 1.1.3. Ingress 컨트롤러 샤딩의 경로 생성

경로를 사용하면 URL에서 애플리케이션을 호스팅할 수 있습니다. Ingress 컨트롤러 분할은 들어오는 트래픽 부하를 일련의 Ingress 컨트롤러 간에 균형을 유지하는 데 도움이 됩니다. 특정 Ingress 컨트롤러로 트래픽을 분리할 수도 있습니다. 예를 들어, 회사 A는 하나의 Ingress 컨트롤러로, 회사 B는 다른 Ingress 컨트롤러로 이동합니다.

다음 절차에서는 `hello-openshift` 애플리케이션을 예로 사용하여 Ingress 컨트롤러 샤딩에 대한 경로를 생성하는 방법을 설명합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로젝트 관리자로 로그인했습니다.

포트에서 트래픽을 수신하는 포트와 HTTP 또는 TLS 끝점을 노출하는 웹 애플리케이션이 있습니다.

분할을 위해 Ingress 컨트롤러를 구성했습니다.

프로세스

다음 명령을 실행하여 `hello-openshift` 라는 프로젝트를 생성합니다.

```shell-session
$ oc new-project hello-openshift
```

다음 명령을 실행하여 프로젝트에 Pod를 생성합니다.

```shell-session
$ oc create -f https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json
```

다음 명령을 실행하여 `hello-openshift` 라는 서비스를 생성합니다.

```shell-session
$ oc expose pod/hello-openshift
```

`hello-openshift-route.yaml` 이라는 경로 정의를 생성합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    type: sharded
  name: hello-openshift-edge
  namespace: hello-openshift
spec:
  subdomain: hello-openshift
  tls:
    termination: edge
  to:
    kind: Service
    name: hello-openshift
```

1. 레이블 키와 해당 라벨 값이 모두 Ingress 컨트롤러에 지정된 라벨 값과 일치해야 합니다. 이 예에서 Ingress 컨트롤러에는 레이블 키와 값 `type: sharded` 가 있습니다.

2. 경로는 `하위 도메인` 필드의 값을 사용하여 노출됩니다. `하위 도메인` 필드를 지정하는 경우 호스트 이름을 설정되지 않은 상태로 두어야 합니다. `host` 및 `subdomain` 필드를 모두 지정하면 경로는 `host` 필드의 값을 사용하고 하위 도메인 필드를 무시합니다.

다음 명령을 실행하여 `hello-openshift-route.yaml` 을 사용하여 `hello-openshift` 애플리케이션에 대한 경로를 생성합니다.

```shell-session
$ oc -n hello-openshift create -f hello-openshift-route.yaml
```

검증

다음 명령을 사용하여 경로 상태를 가져옵니다.

```shell-session
$ oc -n hello-openshift get routes/hello-openshift-edge -o yaml
```

생성된 `Route` 리소스는 다음과 유사해야 합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    type: sharded
  name: hello-openshift-edge
  namespace: hello-openshift
spec:
  subdomain: hello-openshift
  tls:
    termination: edge
  to:
    kind: Service
    name: hello-openshift
status:
  ingress:
  - host: hello-openshift.<apps-sharded.basedomain.example.net>
    routerCanonicalHostname: router-sharded.<apps-sharded.basedomain.example.net>
    routerName: sharded
```

1. Ingress 컨트롤러 또는 라우터의 호스트 이름은 을 사용하여 경로를 노출합니다. `host` 필드의 값은 Ingress 컨트롤러에서 자동으로 결정하고 해당 도메인을 사용합니다. 이 예에서 Ingress 컨트롤러의 도메인은 < `apps-sharded.basedomain.example.net>입니다`.

2. Ingress 컨트롤러의 호스트 이름입니다. 호스트 이름이 설정되지 않은 경우 경로는 하위 도메인을 대신 사용할 수 있습니다. 하위 도메인을 지정하면 경로를 노출하는 Ingress 컨트롤러의 도메인을 자동으로 사용합니다. 여러 Ingress 컨트롤러에서 경로를 노출하면 경로가 여러 URL에서 호스팅됩니다.

3. Ingress 컨트롤러의 이름입니다. 이 예에서 Ingress 컨트롤러에는 `shard된` 이름이 있습니다.

#### 1.1.4. Ingress 오브젝트를 통해 경로 생성

일부 에코시스템 구성 요소는 Ingress 리소스와 통합되지만 경로 리소스와는 통합되지 않습니다. 이러한 경우를 처리하기 위해 OpenShift Container Platform에서는 Ingress 오브젝트가 생성될 때 관리형 경로 오브젝트를 자동으로 생성합니다. 이러한 경로 오브젝트는 해당 Ingress 오브젝트가 삭제될 때 삭제됩니다.

프로세스

OpenShift Container Platform 콘솔에서 또는 아래 명령을 입력하여 Ingress 오브젝트를 정의합니다.

```shell
oc create
```

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: secret-ca-cert
spec:
  rules:
  - host: www.example.com
    http:
      paths:
      - backend:
          service:
            name: frontend
            port:
              number: 443
        path: /
        pathType: Prefix
  tls:
  - hosts:
    - www.example.com
    secretName: example-com-tls-certificate
```

1. `Ingress` 에는 `Route` 에 대한 필드가 없으므로 `route.openshift.io/termination` 주석을 사용하여 `spec.tls.termination` 필드를 구성할 수 있습니다. 허용되는 값은 `edge`, `passthrough`, `reencrypt` 입니다.

다른 모든 값은 자동으로 무시됩니다. 주석 값이 설정되지 않으면 `edge` 가 기본 경로입니다.

기본 엣지 경로를 구현하려면 TLS 인증서 세부 정보를 템플릿 파일에 정의해야 합니다.

3. `Ingress` 오브젝트로 작업할 때는 경로를 사용할 때와 달리 명시적 호스트 이름을 지정해야 합니다.

< `host_name>.<cluster_ingress_domain` > 구문(예: `apps.openshiftdemos.com`)을 사용하여 `*.<cluster_ingress_domain` > 와일드카드 DNS 레코드 및 클러스터에 대한 인증서를 제공할 수 있습니다. 그렇지 않으면 선택한 호스트 이름에 대한 DNS 레코드가 있는지 확인해야 합니다.

`route.openshift.io/termination` 주석에 `passthrough` 값을 지정하는 경우 `path` 를 `''` 로 설정하고 spec에서 `pathType` 을 `ImplementationSpecific` 으로 설정합니다.

```yaml
spec:
    rules:
    - host: www.example.com
      http:
        paths:
        - path: ''
          pathType: ImplementationSpecific
          backend:
            service:
              name: frontend
              port:
                number: 443
```

```shell-session
$ oc apply -f ingress.yaml
```

2. Ingress 오브젝트에서 `route.openshift.io/destination-ca-certificate-secret` 을 사용하여 사용자 정의 대상 인증서(CA)로 경로를 정의할 수 있습니다. 이 주석은 생성된 경로에 삽입될 kubernetes 시크릿 secret `secret-ca-cert` 를 참조합니다.

Ingress 오브젝트에서 대상 CA를 사용하여 경로 오브젝트를 지정하려면 시크릿의 `data.tls.crt` 지정자에 PEM 인코딩 형식으로 인증서를 사용하여 `kubernetes.io/tls` 또는 `Opaque` 유형 시크릿을 생성해야 합니다.

노드를 나열합니다.

```shell-session
$ oc get routes
```

결과에는 이름이 `frontend-` 로 시작하는 자동 생성 경로가 포함됩니다.

```shell-session
NAME             HOST/PORT         PATH    SERVICES    PORT    TERMINATION          WILDCARD
frontend-gnztq   www.example.com           frontend    443     reencrypt/Redirect   None
```

이 경로를 살펴보면 다음과 같습니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend-gnztq
  ownerReferences:
  - apiVersion: networking.k8s.io/v1
    controller: true
    kind: Ingress
    name: frontend
    uid: 4e6c59cc-704d-4f44-b390-617d879033b6
spec:
  host: www.example.com
  path: /
  port:
    targetPort: https
  tls:
    certificate: |
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
    insecureEdgeTerminationPolicy: Redirect
    key: |
      -----BEGIN RSA PRIVATE KEY-----
      [...]
      -----END RSA PRIVATE KEY-----
    termination: reencrypt
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
  to:
    kind: Service
    name: frontend
```

### 1.2. 경로 보안

HSTS(HTTP Strict Transport Security)로 경로를 보호할 수 있습니다.

#### 1.2.1. HSTS(HTTP Strict Transport Security)

HSTS(HTTP Strict Transport Security) 정책은 라우트 호스트에서 HTTPS 트래픽만 허용됨을 브라우저 클라이언트에 알리는 보안 강화 정책입니다. 또한 HSTS는 HTTP 리디렉션을 사용하지 않고 HTTPS 전송 신호를 통해 웹 트래픽을 최적화합니다. HSTS는 웹사이트와의 상호 작용을 가속화하는 데 유용합니다.

HSTS 정책이 적용되면 HSTS는 사이트의 HTTP 및 HTTPS 응답에 Strict Transport Security 헤더를 추가합니다. 경로에서 `insecureEdgeTerminationPolicy` 값을 사용하여 HTTP를 HTTPS로 리디렉션할 수 있습니다.

HSTS를 적용하면 클라이언트는 요청을 전송하기 전에 HTTP URL의 모든 요청을 HTTPS로 변경하여 리디렉션이 필요하지 않습니다.

클러스터 관리자는 다음을 수행하도록 HSTS를 구성할 수 있습니다.

경로당 HSTS 활성화

라우팅당 HSTS 비활성화

도메인당 HSTS 시행, 도메인 집합 또는 도메인과 함께 네임스페이스 라벨 사용

중요

HSTS는 보안 경로(엣지 종료 또는 재암호화)에서만 작동합니다. HTTP 또는 패스스루(passthrough) 경로에서는 구성이 유효하지 않습니다.

#### 1.2.1.1. 라우팅당 HSTS(HTTP Strict Transport Security) 활성화

HSTS(HTTP Strict Transport Security)는 HAProxy 템플릿에 구현되고 `haproxy.router.openshift.io/hsts_header` 주석이 있는 에지 및 재암호화 경로에 적용됩니다.

사전 요구 사항

프로젝트에 대한 관리자 권한이 있는 사용자로 클러스터에 로그인했습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

경로에서 HSTS를 활성화하려면 `haproxy.router.openshift.io/hsts_header` 값을 에지 종료 또는 재암호화 경로에 추가합니다. tool을 사용하여 다음 명령을 실행하여 이 작업을 수행할 수 있습니다.

```shell
oc annotate
```

명령을 올바르게 실행하려면 `haproxy.router.openshift.io/hsts_header` 경로 주석의 username(`;`)이 큰따옴표(`""`)로 묶여 있는지 확인합니다.

```shell-session
$ oc annotate route <route_name> -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header=max-age=31536000;\
includeSubDomains;preload"
```

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  annotations:
    haproxy.router.openshift.io/hsts_header: max-age=31536000;includeSubDomains;preload
# ...
spec:
  host: def.abc.com
  tls:
    termination: "reencrypt"
    ...
  wildcardPolicy: "Subdomain"
# ...
```

1. 필수 항목입니다. `Max-age` 는 HSTS 정책이 적용되는 시간(초)을 측정합니다. `0` 으로 설정하면 정책이 무효화됩니다.

2. 선택 사항: 포함되는 경우 `includeSubDomains` 는 호스트의 모든 하위 도메인에 호스트와 동일한 HSTS 정책이 있어야 함을 알려줍니다.

3. 선택 사항: `max-age` 가 0보다 크면 `haproxy.router.openshift.io/hsts_header` 에 `preload` 를 추가하여 외부 서비스에서 이 사이트를 HSTS 사전 로드 목록에 포함할 수 있습니다. 예를 들어 Google과 같은 사이트는 `preload` 가 설정된 사이트 목록을 구성할 수 있습니다.

그런 다음 브라우저는 이 목록을 사용하여 사이트와 상호 작용하기 전에 HTTPS를 통해 통신할 수 있는 사이트를 결정할 수 있습니다. `preload` 를 설정하지 않으면 브라우저가 HTTPS를 통해 사이트와 상호 작용하여 헤더를 가져와야 합니다.

#### 1.2.1.2. 라우팅당 HSTS(HTTP Strict Transport Security) 비활성화

경로당 HSTS(HTTP Strict Transport Security)를 비활성화하려면 경로 주석에서 `max-age` 값을 `0` 으로 설정할 수 있습니다.

사전 요구 사항

프로젝트에 대한 관리자 권한이 있는 사용자로 클러스터에 로그인했습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

HSTS를 비활성화하려면 다음 명령을 입력하여 경로 주석의 `max-age` 값을 `0` 으로 설정합니다.

```shell-session
$ oc annotate route <route_name> -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=0"
```

작은 정보

다음 YAML을 적용하여 구성 맵을 만들 수 있습니다.

```yaml
metadata:
  annotations:
    haproxy.router.openshift.io/hsts_header: max-age=0
```

네임스페이스의 모든 경로에 대해 HSTS를 비활성화하려면 다음 명령을 입력합니다.

```shell-session
$ oc annotate route --all -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=0"
```

검증

모든 경로에 대한 주석을 쿼리하려면 다음 명령을 입력합니다.

```shell-session
$ oc get route  --all-namespaces -o go-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'
```

```shell-session
Name: routename HSTS: max-age=0
```

#### 1.2.1.3. 도메인별 HSTS(HTTP Strict Transport Security) 적용

도메인당 HSTS(HTTP Strict Transport Security)를 적용하여 보안 경로에 `requiredHSTSPolicies` 레코드를 Ingress 사양에 추가하여 HSTS 정책 구성을 캡처합니다.

HSTS를 적용하도록 `requiredHSTSPolicy` 를 구성하는 경우 규정 준수 HSTS 정책 주석을 사용하여 새로 생성된 경로를 구성해야 합니다.

참고

준수하지 않는 HSTS 경로를 사용하여 업그레이드된 클러스터를 처리하려면 소스에서 매니페스트를 업데이트하고 업데이트를 적용할 수 있습니다.

참고

다음 명령또는 아래 명령을 사용하여 이러한 명령의 API에서 주석을 수락하지 않기 때문에 HSTS를 적용하는 도메인에 경로를 추가할 수 없습니다.

```shell
oc expose route
```

```shell
oc create route
```

중요

HSTS는 전역적으로 모든 경로에 HSTS를 요청하더라도 비보안 또는 비 TLS 경로에 적용할 수 없습니다.

사전 요구 사항

프로젝트에 대한 관리자 권한이 있는 사용자로 클러스터에 로그인했습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

필요에 따라 다음 명령을 실행하고 필드를 업데이트하여 Ingress 구성 YAML을 편집합니다.

```shell-session
$ oc edit ingresses.config.openshift.io/cluster
```

```yaml
apiVersion: config.openshift.io/v1
kind: Ingress
metadata:
  name: cluster
spec:
  domain: 'hello-openshift-default.apps.username.devcluster.openshift.com'
  requiredHSTSPolicies:
  - domainPatterns:
    - '*hello-openshift-default.apps.username.devcluster.openshift.com'
    - '*hello-openshift-default2.apps.username.devcluster.openshift.com'
    namespaceSelector:
      matchLabels:
        myPolicy: strict
    maxAge:
      smallestMaxAge: 1
      largestMaxAge: 31536000
    preloadPolicy: RequirePreload
    includeSubDomainsPolicy: RequireIncludeSubDomains
  - domainPatterns:
    - 'abc.example.com'
    - '*xyz.example.com'
    namespaceSelector:
      matchLabels: {}
    maxAge: {}
    preloadPolicy: NoOpinion
    includeSubDomainsPolicy: RequireNoIncludeSubDomains
```

1. 필수 항목입니다. `requiredHSTSPolicies` 는 순서대로 검증되고 일치하는 첫 번째 `domainPatterns` 가 적용됩니다.

2. 필수 항목입니다. 하나 이상의 `domainPatterns` 호스트 이름을 지정해야 합니다. 도메인 수를 나열할 수 있습니다. 다른 `domainPatterns` 에 대한 적용 옵션의 여러 섹션을 포함할 수 있습니다.

3. 선택 사항: `namespaceSelector` 를 포함하는 경우 경로가 있는 프로젝트의 레이블과 일치하여 경로에 설정된 HSTS 정책을 적용해야 합니다. `namespaceSelector` 만 일치하고 `domainPatterns` 와 일치하지 않는 경로는 검증되지 않습니다.

4. 필수 항목입니다. `Max-age` 는 HSTS 정책이 적용되는 시간(초)을 측정합니다. 이 정책 설정을 사용하면 최소 및 최대 `max-age` 를 적용할 수 있습니다.

`largestMaxAge` 값은 `0` 에서 `2147483647` 사이여야 합니다. 지정되지 않은 상태로 둘 수 있습니다. 즉, 상한이 적용되지 않습니다.

`smallestMaxAge` 값은 `0` 에서 `2147483647` 사이여야 합니다. 문제 해결을 위해 HSTS를 비활성화하려면 `0` 을 입력합니다. HSTS를 비활성화하지 않으려면 `1` 을 입력합니다. 지정되지 않은 상태로 둘 수 있습니다. 즉, 더 낮은 제한이 적용되지 않습니다.

5. 선택 사항: `haproxy.router.openshift.io/hsts_header` 에 `preload` 를 포함하면 외부 서비스에서 이 사이트를 HSTS 사전 로드 목록에 포함할 수 있습니다. 그런 다음 브라우저는 이 목록을 사용하여 사이트와 상호 작용하기 전에 HTTPS를 통해 통신할 수 있는 사이트를 결정할 수 있습니다.

`preload` 를 설정하지 않으면 브라우저가 헤더를 얻기 위해 사이트와 한 번 이상 상호 작용해야 합니다. 다음 중 하나로 `preload` 를 설정할 수 있습니다.

`RequirePreload`: `RequiredHSTSPolicy` 에 `preload` 가 필요합니다.

`RequireNoPreload`: `RequiredHSTSPolicy` 에서 `preload` 를 금지합니다.

`NoOpinion`: `preload` 는 `RequiredHSTSPolicy` 에 중요하지 않습니다.

6. 선택 사항: `includeSubDomainsPolicy` 는 다음 중 하나를 사용하여 설정할 수 있습니다.

`RequireIncludeSubDomains`: `includeSubDomains` 는 `RequiredHSTSPolicy` 에 필요합니다.

`RequireNoIncludeSubDomains`: `includeSubDomains` 는 `RequiredHSTSPolicy` 에서 금지합니다.

`NoOpinion`: `includeSubDomains` 는 `RequiredHSTSPolicy` 와 관련이 없습니다.

다음 명령을 입력하여 클러스터 또는 특정 네임스페이스에 HSTS를 적용할 수 있습니다.

```shell
oc annotate command
```

클러스터의 모든 경로에 HSTS를 적용하려면 다음 명령을 입력합니다. 예를 들면 다음과 같습니다.

```shell
oc annotate command
```

```shell-session
$ oc annotate route --all --all-namespaces --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"
```

특정 네임스페이스의 모든 경로에 HSTS를 적용하려면 다음 명령을 입력합니다. 예를 들면 다음과 같습니다.

```shell
oc annotate command
```

```shell-session
$ oc annotate route --all -n my-namespace --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"
```

검증

구성한 HSTS 정책을 검토할 수 있습니다. 예를 들면 다음과 같습니다.

필요한 HSTS 정책에 대한 `maxAge` 세트를 검토하려면 다음 명령을 입력합니다.

```shell-session
$ oc get clusteroperator/ingress -n openshift-ingress-operator -o jsonpath='{range .spec.requiredHSTSPolicies[*]}{.spec.requiredHSTSPolicies.maxAgePolicy.largestMaxAge}{"\n"}{end}'
```

모든 경로에서 HSTS 주석을 검토하려면 다음 명령을 입력합니다.

```shell-session
$ oc get route  --all-namespaces -o go-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'
```

```shell-session
Name: <_routename_> HSTS: max-age=31536000;preload;includeSubDomains
```

### 1.3. 경로 구성

주석, 헤더, 쿠키 등을 사용하여 경로 구성을 사용자 지정할 수 있습니다.

#### 1.3.1. 경로 시간 초과 구성

SLA(Service Level Availability) 목적에 필요한 낮은 시간 초과 또는 백엔드가 느린 경우 높은 시간 초과가 필요한 서비스가 있는 경우 기존 경로에 대한 기본 시간 초과를 구성할 수 있습니다.

중요

OpenShift Container Platform 클러스터 앞에 사용자 관리 외부 로드 밸런서를 구성한 경우 사용자 관리 외부 로드 밸런서의 시간 초과 값이 경로의 시간 초과 값보다 높습니다. 이 구성으로 인해 클러스터가 사용하는 네트워크를 통한 네트워크 정체 문제가 발생하지 않습니다.

사전 요구 사항

실행 중인 클러스터에 배포된 Ingress 컨트롤러가 필요합니다.

프로세스

아래 명령을 사용하여 경로에 시간 초과를 추가합니다.

```shell
oc annotate
```

```shell-session
$ oc annotate route <route_name> \
    --overwrite haproxy.router.openshift.io/timeout=<timeout><time_unit>
```

1. 지원되는 시간 단위는 마이크로초(us), 밀리초(ms), 초(s), 분(m), 시간(h) 또는 일(d)입니다.

다음 예제는 이름이 `myroute` 인 경로에서 2초의 시간 초과를 설정합니다.

```shell-session
$ oc annotate route myroute --overwrite haproxy.router.openshift.io/timeout=2s
```

#### 1.3.2. HTTP 헤더 구성

OpenShift Container Platform은 HTTP 헤더를 사용하는 다양한 방법을 제공합니다. 헤더를 설정하거나 삭제할 때 Ingress 컨트롤러의 특정 필드를 사용하거나 개별 경로를 사용하여 요청 및 응답 헤더를 수정할 수 있습니다.

경로 주석을 사용하여 특정 헤더를 설정할 수도 있습니다. 헤더를 구성하는 다양한 방법은 함께 작업할 때 문제가 발생할 수 있습니다.

참고

`IngressController` 또는 `Route` CR 내에서 헤더만 설정하거나 삭제할 수 있으므로 추가할 수 없습니다. HTTP 헤더가 값으로 설정된 경우 해당 값은 완료되어야 하며 나중에 추가할 필요가 없습니다.

X-Forwarded-For 헤더와 같은 헤더를 추가하는 것이 적합한 경우 `spec.httpHeaders.actions` 대신 `spec.httpHeaders.forwardedHeaderPolicy` 필드를 사용합니다.

#### 1.3.2.1. 우선순위 순서

Ingress 컨트롤러와 경로에서 동일한 HTTP 헤더를 수정하는 경우 HAProxy는 요청 또는 응답 헤더인지 여부에 따라 특정 방식으로 작업에 우선순위를 부여합니다.

HTTP 응답 헤더의 경우 경로에 지정된 작업 후에 Ingress 컨트롤러에 지정된 작업이 실행됩니다. 즉, Ingress 컨트롤러에 지정된 작업이 우선합니다.

HTTP 요청 헤더의 경우 경로에 지정된 작업은 Ingress 컨트롤러에 지정된 작업 후에 실행됩니다. 즉, 경로에 지정된 작업이 우선합니다.

예를 들어 클러스터 관리자는 다음 구성을 사용하여 Ingress 컨트롤러에서 값이 `DENY` 인 X-Frame-Options 응답 헤더를 설정합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
# ...
spec:
  httpHeaders:
    actions:
      response:
      - name: X-Frame-Options
        action:
          type: Set
          set:
            value: DENY
```

경로 소유자는 클러스터 관리자가 Ingress 컨트롤러에 설정한 것과 동일한 응답 헤더를 설정하지만 다음 구성을 사용하여 `SAMEORIGIN` 값이 사용됩니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
# ...
spec:
  httpHeaders:
    actions:
      response:
      - name: X-Frame-Options
        action:
          type: Set
          set:
            value: SAMEORIGIN
```

`IngressController` 사양과 `Route` 사양 모두에서 X-Frame-Options 응답 헤더를 구성하는 경우 특정 경로에서 프레임을 허용하는 경우에도 Ingress 컨트롤러의 글로벌 수준에서 이 헤더에 설정된 값이 우선합니다. 요청 헤더의 경우 `Route` spec 값은 `IngressController` 사양 값을 재정의합니다.

이 우선순위는 `haproxy.config` 파일에서 다음 논리를 사용하므로 Ingress 컨트롤러가 프런트 엔드로 간주되고 개별 경로가 백엔드로 간주되기 때문입니다. 프런트 엔드 구성에 적용된 헤더 값 `DENY` 는 백엔드에 설정된 `SAMEORIGIN` 값으로 동일한 헤더를 재정의합니다.

```plaintext
frontend public
  http-response set-header X-Frame-Options 'DENY'

frontend fe_sni
  http-response set-header X-Frame-Options 'DENY'

frontend fe_no_sni
  http-response set-header X-Frame-Options 'DENY'

backend be_secure:openshift-monitoring:alertmanager-main
  http-response set-header X-Frame-Options 'SAMEORIGIN'
```

또한 Ingress 컨트롤러 또는 경로 주석을 사용하여 설정된 경로 덮어쓰기 값에 정의된 모든 작업입니다.

#### 1.3.2.2. 특수 케이스 헤더

다음 헤더는 완전히 설정되거나 삭제되지 않거나 특정 상황에서 허용되지 않습니다.

| 헤더 이름 | `IngressController` 사양을 사용하여 구성 가능 | `Route` 사양을 사용하여 구성 가능 | 허용하지 않는 이유 | 다른 방법을 사용하여 구성 가능 |
| --- | --- | --- | --- | --- |
| `proxy` | 없음 | 없음 | `프록시` HTTP 요청 헤더는 `HTTP_PROXY` 환경 변수에 헤더 값을 삽입하여 취약한 CGI 애플리케이션을 활용하는 데 사용할 수 있습니다. `프록시` HTTP 요청 헤더는 비표준이며 구성 중에 오류가 발생하기 쉽습니다. | 없음 |
| `host` | 없음 | 제공됨 | `IngressController` CR을 사용하여 `호스트` HTTP 요청 헤더를 설정하면 올바른 경로를 찾을 때 HAProxy가 실패할 수 있습니다. | 없음 |
| `strict-transport-security` | 없음 | 없음 | `strict-transport-security` HTTP 응답 헤더는 경로 주석을 사용하여 이미 처리되었으며 별도의 구현이 필요하지 않습니다. | 제공됨: `haproxy.router.openshift.io/hsts_header` 경로 주석 |
| `쿠키` 및 `설정 쿠키` | 없음 | 없음 | HAProxy가 클라이언트 연결을 특정 백엔드 서버에 매핑하는 세션 추적에 사용되는 쿠키입니다. 이러한 헤더를 설정하도록 허용하면 HAProxy의 세션 선호도를 방해하고 HAProxy의 쿠키 소유권을 제한할 수 있습니다. | 예: `haproxy.router.openshift.io/disable_cookie` 경로 주석 `haproxy.router.openshift.io/cookie_name` 경로 주석 |

#### 1.3.3. 경로에서 HTTP 요청 및 응답 헤더 설정 또는 삭제

규정 준수 목적 또는 기타 이유로 특정 HTTP 요청 및 응답 헤더를 설정하거나 삭제할 수 있습니다. Ingress 컨트롤러에서 제공하는 모든 경로 또는 특정 경로에 대해 이러한 헤더를 설정하거나 삭제할 수 있습니다.

예를 들어 경로를 제공하는 Ingress 컨트롤러에서 지정하는 기본 글로벌 위치가 있더라도 해당 콘텐츠가 여러 언어로 작성된 경우 웹 애플리케이션에서 특정 경로에 대한 콘텐츠를 제공할 수 있도록 할 수 있습니다.

다음 절차에서는 애플리케이션 `https://app.example.com` 과 연결된 URL이 위치 `https://app.example.com/lang/en-us` 로 전달되도록 Content-Location HTTP 요청 헤더를 설정하는 경로를 생성합니다.

애플리케이션 트래픽을 이 위치로 전달한다는 것은 특정 경로를 사용하는 사람이 미국 영어로 작성된 웹 콘텐츠에 액세스하는 것을 의미합니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

OpenShift Container Platform 클러스터에 프로젝트 관리자로 로그인되어 있습니다.

포트에서 트래픽을 수신하는 포트와 HTTP 또는 TLS 끝점을 노출하는 웹 애플리케이션이 있습니다.

프로세스

경로 정의를 생성하고 `app-example-route.yaml` 이라는 파일에 저장합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
# ...
spec:
  host: app.example.com
  tls:
    termination: edge
  to:
    kind: Service
    name: app-example
  httpHeaders:
    actions:
      response:
      - name: Content-Location
        action:
          type: Set
          set:
            value: /lang/en-us
```

1. HTTP 헤더에서 수행할 작업 목록입니다.

2. 변경할 헤더 유형입니다. 이 경우 응답 헤더입니다.

3. 변경할 헤더의 이름입니다. 설정하거나 삭제할 수 있는 사용 가능한 헤더 목록은 HTTP 헤더 구성 을 참조하십시오.

4. 헤더에서 수행되는 작업 유형입니다. 이 필드에는 `Set` 또는 `Delete` 값이 있을 수 있습니다.

5. HTTP 헤더를 설정할 때 `값을` 제공해야 합니다. 값은 해당 헤더에 사용 가능한 지시문 목록(예: `DENY`)의 문자열이거나 HAProxy의 동적 값 구문을 사용하여 해석되는 동적 값이 될 수 있습니다. 이 경우 값은 콘텐츠의 상대 위치로 설정됩니다.

새로 생성된 경로 정의를 사용하여 기존 웹 애플리케이션에 대한 경로를 생성합니다.

```shell-session
$ oc -n app-example create -f app-example-route.yaml
```

HTTP 요청 헤더의 경우 경로 정의에 지정된 작업이 Ingress 컨트롤러의 HTTP 요청 헤더에 실행된 후 실행됩니다. 즉, 경로의 해당 요청 헤더에 설정된 모든 값이 Ingress 컨트롤러에 설정된 값보다 우선합니다. HTTP 헤더 처리 순서에 대한 자세한 내용은 HTTP 헤더 구성 을 참조하십시오.

#### 1.3.4. 쿠키를 사용하여 경로 상태 유지

OpenShift Container Platform은 모든 트래픽이 동일한 끝점에 도달하도록 하여 스테이트풀(stateful) 애플리케이션 트래픽을 사용할 수 있는 고정 세션을 제공합니다. 그러나 재시작, 스케일링 또는 구성 변경 등으로 인해 끝점 pod가 종료되면 이러한 상태 저장 특성이 사라질 수 있습니다.

OpenShift Container Platform에서는 쿠키를 사용하여 세션 지속성을 구성할 수 있습니다. 수신 컨트롤러는 사용자 요청을 처리할 끝점을 선택하고 세션에 대한 쿠키를 생성합니다.

쿠키는 요청에 대한 응답으로 다시 전달되고 사용자는 세션의 다음 요청과 함께 쿠키를 다시 보냅니다. 쿠키는 세션을 처리하는 끝점을 Ingress 컨트롤러에 알려 클라이언트 요청이 쿠키를 사용하여 동일한 pod로 라우팅되도록 합니다.

참고

HTTP 트래픽을 볼 수 없기 때문에 패스스루 경로에 쿠키를 설정할 수 없습니다. 대신 백엔드를 결정하는 소스 IP 주소를 기반으로 번호가 계산됩니다.

백엔드가 변경되면 트래픽이 잘못된 서버로 전달되어 덜 고정될 수 있습니다. 소스 IP를 숨기는 로드 밸런서를 사용하는 경우 모든 연결에 대해 동일한 번호가 설정되고 트래픽이 동일한 Pod로 전송됩니다.

#### 1.3.4.1. 쿠키를 사용하여 경로에 주석 달기

쿠키 이름을 설정하여 경로에 자동 생성되는 기본 쿠키 이름을 덮어쓸 수 있습니다. 그러면 경로 트래픽을 수신하는 애플리케이션에서 쿠키 이름을 확인할 수 있게 됩니다. 쿠키를 삭제하면 다음 요청이 끝점을 다시 선택하도록 강제할 수 있습니다. 결과적으로 서버가 과부하된 경우 해당 서버에서 클라이언트의 요청을 제거하고 재배포하려고 합니다.

프로세스

지정된 쿠키 이름으로 경로에 주석을 답니다.

```shell-session
$ oc annotate route <route_name> router.openshift.io/cookie_name="<cookie_name>"
```

다음과 같습니다.

`<route_name>`

경로 이름을 지정합니다.

`<cookie_name>`

쿠키 이름을 지정합니다.

예를 들어 쿠키 이름 `my_cookie` 로 `my_route` 경로에 주석을 달 수 있습니다.

```shell-session
$ oc annotate route my_route router.openshift.io/cookie_name="my_cookie"
```

경로 호스트 이름을 변수에 캡처합니다.

```shell-session
$ ROUTE_NAME=$(oc get route <route_name> -o jsonpath='{.spec.host}')
```

다음과 같습니다.

`<route_name>`

경로 이름을 지정합니다.

쿠키를 저장한 다음 경로에 액세스합니다.

```shell-session
$ curl $ROUTE_NAME -k -c /tmp/cookie_jar
```

경로에 연결할 때 이전 명령으로 저장된 쿠키를 사용합니다.

```shell-session
$ curl $ROUTE_NAME -k -b /tmp/cookie_jar
```

#### 1.3.5. 경로별 주석

Ingress 컨트롤러는 노출하는 모든 경로에 기본 옵션을 설정할 수 있습니다. 개별 경로는 주석에 특정 구성을 제공하는 방식으로 이러한 기본값 중 일부를 덮어쓸 수 있습니다. Red Hat은 operator 관리 경로에 경로 주석 추가를 지원하지 않습니다.

중요

여러 소스 IP 또는 서브넷이 있는 허용 목록을 만들려면 공백으로 구분된 목록을 사용합니다. 다른 구분 기호 유형으로 인해 경고 또는 오류 메시지 없이 목록이 무시됩니다.

| 변수 | 설명 |
| --- | --- |
| `haproxy.router.openshift.io/balance` | 로드 밸런싱 알고리즘을 설정합니다. 사용 가능한 옵션은 `random` , `source` , `roundrobin` [ 1 ] 및 `leastconn` 입니다. 기본값은 TLS 패스스루 경로의 `source` 입니다. 다른 모든 경로의 경우 기본값은 `random` 입니다. |
| `haproxy.router.openshift.io/disable_cookies` | 쿠키를 사용하여 관련 연결을 추적하지 않도록 설정합니다. `'true'` 또는 `'TRUE'` 로 설정하면 들어오는 각 HTTP 요청에 대한 백엔드 연결을 제공하는 백엔드를 선택하는 데 밸런스 알고리즘이 사용됩니다. |
| `router.openshift.io/cookie_name` | 이 경로에 사용할 선택적 쿠키를 지정합니다. 이름은 대문자와 소문자, 숫자, ‘_’, ‘-’의 조합으로 구성해야 합니다. 기본값은 경로의 해시된 내부 키 이름입니다. |
| `haproxy.router.openshift.io/pod-concurrent-connections` | 라우터에서 백업 pod로 허용되는 최대 연결 수를 설정합니다. 참고: Pod가 여러 개인 경우 각각 이 수만큼의 연결이 있을 수 있습니다. 라우터가 여러 개 있고 조정이 이루어지지 않는 경우에는 각각 이 횟수만큼 연결할 수 있습니다. 설정하지 않거나 0으로 설정하면 제한이 없습니다. |
| `haproxy.router.openshift.io/rate-limit-connections` | `'true'` 또는 `'TRUE'` 를 설정하면 경로당 특정 백엔드의 고정 테이블을 통해 구현되는 속도 제한 기능이 활성화됩니다. 참고: 이 주석을 사용하면 서비스 거부 공격에 대한 기본 보호 기능이 제공됩니다. |
| `haproxy.router.openshift.io/rate-limit-connections.concurrent-tcp` | 동일한 소스 IP 주소를 통해 만든 동시 TCP 연결 수를 제한합니다. 숫자 값을 허용합니다. 참고: 이 주석을 사용하면 서비스 거부 공격에 대한 기본 보호 기능이 제공됩니다. |
| `haproxy.router.openshift.io/rate-limit-connections.rate-http` | 동일한 소스 IP 주소가 있는 클라이언트에서 HTTP 요청을 수행할 수 있는 속도를 제한합니다. 숫자 값을 허용합니다. 참고: 이 주석을 사용하면 서비스 거부 공격에 대한 기본 보호 기능이 제공됩니다. |
| `haproxy.router.openshift.io/rate-limit-connections.rate-tcp` | 동일한 소스 IP 주소가 있는 클라이언트에서 TCP 연결을 수행할 수 있는 속도를 제한합니다. 숫자 값을 허용합니다. |
| `router.openshift.io/haproxy.health.check.interval` | 백엔드 상태 점검 간격을 설정합니다. (TimeUnits) |
| `haproxy.router.openshift.io/ip_allowlist` | 경로에 대한 허용 목록을 설정합니다. 허용 목록은 승인된 소스 주소에 대한 IP 주소 및 CIDR 범위로 이루어진 공백으로 구분된 목록입니다. 허용 목록에 없는 IP 주소의 요청은 삭제됩니다. `haproxy.config` 파일에 직접 표시되는 최대 IP 주소 및 CIDR 범위는 61입니다. [ 2 ] |
| `haproxy.router.openshift.io/hsts_header` | 엣지 종단 경로 또는 재암호화 경로에 Strict-Transport-Security 헤더를 설정합니다. |
| `haproxy.router.openshift.io/rewrite-target` | 백엔드의 요청 재작성 경로를 설정합니다. |
| `router.openshift.io/cookie-same-site` | 쿠키를 제한하는 값을 설정합니다. 값은 다음과 같습니다. `LAX` : 브라우저는 사이트 간 요청에 쿠키를 보내지 않지만 사용자가 외부 사이트에서 원본 사이트로 이동할 때 쿠키를 보냅니다. 이는 `SameSite` 값이 지정되지 않은 경우 기본 브라우저 동작입니다. `Strict` : 브라우저가 동일한 사이트 요청에 대해서만 쿠키를 보냅니다. `none` : 브라우저가 교차 사이트 요청과 동일한 사이트 요청에 대해 쿠키를 보냅니다. 이 값은 재암호화 및 엣지 경로에만 적용됩니다. 자세한 내용은 SameSite 쿠키 설명서 를 참조하십시오. |
| `haproxy.router.openshift.io/set-forwarded-headers` | 라우터당 `Forwarded` 및 `X-Forwarded-For` HTTP 헤더를 처리하기 위한 정책을 설정합니다. 값은 다음과 같습니다. `append` : 기존 헤더를 유지하면서 헤더를 추가합니다. 이는 기본값입니다. `replace` : 헤더를 설정하고 기존 헤더를 제거합니다. `never` : 헤더를 설정하지 않고 기존 헤더를 유지합니다. `if-none` : 아직 설정되지 않은 경우 헤더를 설정합니다. |

기본적으로 라우터는 5s마다 다시 로드되어 처음부터 포드 간에 분산 연결을 재설정합니다. 결과적으로 `roundrobin` 상태는 다시 로드해도 유지되지 않습니다.

이 알고리즘은 Pod에 거의 동일한 컴퓨팅 용량 및 스토리지 용량이 있는 경우 가장 잘 작동합니다. 예를 들어 CI/CD 파이프라인을 사용하므로 애플리케이션 또는 서비스에서 끝점을 지속적으로 변경한 경우 분산이 일관되지 않을 수 있습니다.

이 경우 다른 알고리즘을 사용하십시오.

허용 목록의 IP 주소 및 CIDR 범위가 61를 초과하면 `haproxy.config` 파일에서 참조되는 별도의 파일에 작성됩니다. 이 파일은 `/var/lib/haproxy/router/allowlists` 폴더에 저장됩니다.

참고

주소가 허용 목록에 작성되도록 하려면 전체 CIDR 범위가 Ingress 컨트롤러 구성 파일에 나열되어 있는지 확인합니다. etcd 오브젝트 크기 제한은 경로 주석의 크기를 제한합니다. 이로 인해 허용 목록에 포함할 수 있는 최대 IP 주소 및 CIDR 범위에 대한 임계값이 생성됩니다.

```yaml
metadata:
  annotations:
    haproxy.router.openshift.io/ip_allowlist: 192.168.1.10
```

```yaml
metadata:
  annotations:
    haproxy.router.openshift.io/ip_allowlist: 192.168.1.10 192.168.1.11 192.168.1.12
```

```yaml
metadata:
  annotations:
    haproxy.router.openshift.io/ip_allowlist: 192.168.1.0/24
```

```yaml
metadata:
  annotations:
    haproxy.router.openshift.io/ip_allowlist: 180.5.61.153 192.168.1.0/24 10.0.0.0/8
```

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  annotations:
    haproxy.router.openshift.io/rewrite-target: /
...
```

1. `/` 를 백엔드의 요청 재작성 경로로 설정합니다.

경로에 `haproxy.router.openshift.io/rewrite-target` 주석을 설정하면 Ingress Controller에서 요청을 백엔드 애플리케이션으로 전달하기 전에 이 경로를 사용하여 HTTP 요청의 경로를 재작성해야 합니다. `spec.path` 에 지정된 경로와 일치하는 요청 경로 부분은 주석에 지정된 재작성 대상으로 교체됩니다.

다음 표에 `spec.path`, 요청 경로, 재작성 대상의 다양한 조합에 따른 경로 재작성 동작의 예가 있습니다.

| Route.spec.path | 요청 경로 | 재작성 대상 | 전달된 요청 경로 |
| --- | --- | --- | --- |
| /foo | /foo | / | / |
| /foo | /foo/ | / | / |
| /foo | /foo/bar | / | /bar |
| /foo | /foo/bar/ | / | /bar/ |
| /foo | /foo | /bar | /bar |
| /foo | /foo/ | /bar | /bar/ |
| /foo | /foo/bar | /baz | /baz/bar |
| /foo | /foo/bar/ | /baz | /baz/bar/ |
| /foo/ | /foo | / | N/A(요청 경로가 라우팅 경로와 일치하지 않음) |
| /foo/ | /foo/ | / | / |
| /foo/ | /foo/bar | / | /bar |

`haproxy.router.openshift.io/rewrite-target` 의 특정 특수 문자는 올바르게 이스케이프해야 하므로 특수 처리가 필요합니다. 이러한 문자를 처리하는 방법을 알아보려면 다음 표를 참조하십시오.

| 문자의 경우 | 문자 사용 | 참고 |
| --- | --- | --- |
| # | \# | #을 사용하지 마십시오. 재작성 표현식이 종료되기 때문입니다. |
| % | % 또는 %% | %%와 같은 홀수 시퀀스를 사용하지 마십시오. |
| ‘ | \’ | 무시될 수 있기 때문에 방지 |

다른 모든 유효한 URL 문자는 이스케이프 없이 사용할 수 있습니다.

#### 1.3.6. 처리량 문제 문제 해결 방법

OpenShift Container Platform을 사용하여 애플리케이션을 배포하면 특정 서비스 간의 대기 시간이 비정상적으로 길어지는 등 네트워크 처리량 문제가 발생할 수 있습니다.

Pod 로그에 문제의 원인이 표시되지 않는 경우 다음 방법을 사용하여 성능 문제를 분석하십시오.

`ping` 또는 `tcpdump` 와 같은 패킷 Analyzer를 사용하여 Pod와 해당 노드 간의 트래픽을 분석합니다.

예를 들어 각 Pod에서 `tcpdump` 도구를 실행하여 문제의 원인이 되는 동작을 재현합니다. Pod에서 나가거나 Pod로 들어오는 트래픽의 대기 시간을 분석하기 위해 전송 및 수신 타임 스탬프를 비교하려면 전송 캡처와 수신 캡처를 둘 다 검토하십시오.

다른 Pod, 스토리지 장치 또는 데이터 플레인의 트래픽으로 노드 인터페이스가 과부하된 경우 OpenShift Container Platform에서 대기 시간이 발생할 수 있습니다.

```shell-session
$ tcpdump -s 0 -i any -w /tmp/dump.pcap host <podip 1> && host <podip 2>
```

1. `podip` 은 Pod의 IP 주소입니다. 아래 명령을 실행하여 Pod의 IP 주소를 가져옵니다.

```shell
oc get pod <pod_name> -o wide
```

`tcpdump` 명령은 두 Pod 간 모든 트래픽을 포함하는 `/tmp/dump.pcap` 에 파일을 생성합니다. 문제가 재현되기 직전에 Analyzer를 실행하고 문제 재현이 완료된 직후 Analyzer를 중지하여 파일 크기를 최소화할 수 있습니다. 다음을 사용하여 노드 간에 패킷 Analyzer를 실행할 수도 있습니다.

```shell-session
$ tcpdump -s 0 -i any -w /tmp/dump.pcap port 4789
```

스트리밍 처리량 및 UDP 처리량을 측정하려면 `iperf` 와 같은 대역폭 측정 툴을 사용합니다. 먼저 Pod에서 툴을 실행한 다음 노드에서 실행하여 병목 현상이 발생하는지 확인합니다.

`iperf` 설치 및 사용에 대한 자세한 내용은 Red Hat 솔루션을 참조하십시오.

경우에 따라 대기 시간 문제로 인해 클러스터에서 라우터 Pod를 사용하여 노드를 비정상으로 표시할 수 있습니다. 작업자 대기 시간 프로필을 사용하여 조치를 수행하기 전에 클러스터에서 노드 상태 업데이트를 기다리는 빈도를 조정합니다.

클러스터에 대기 시간이 짧고 대기 시간이 많은 노드가 지정된 경우 Ingress 컨트롤러에서 `spec.nodePlacement` 필드를 구성하여 라우터 Pod 배치를 제어합니다.

#### 1.3.7. 경로 허용 정책 구성

관리자 및 애플리케이션 개발자는 도메인 이름이 동일한 여러 네임스페이스에서 애플리케이션을 실행할 수 있습니다. 이는 여러 팀이 동일한 호스트 이름에 노출되는 마이크로 서비스를 개발하는 조직을 위한 것입니다.

주의

네임스페이스 간 클레임은 네임스페이스 간 신뢰가 있는 클러스터에 대해서만 허용해야 합니다. 그렇지 않으면 악의적인 사용자가 호스트 이름을 인수할 수 있습니다. 따라서 기본 승인 정책에서는 네임스페이스 간에 호스트 이름 클레임을 허용하지 않습니다.

사전 요구 사항

클러스터 관리자 권한이 있어야 합니다.

프로세스

다음 명령을 사용하여 `ingresscontroller` 리소스 변수의 `.spec.routeAdmission` 필드를 편집합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontroller/default --patch '{"spec":{"routeAdmission":{"namespaceOwnership":"InterNamespaceAllowed"}}}' --type=merge
```

```yaml
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
...
```

작은 정보

다음 YAML을 적용하여 경로 승인 정책을 구성할 수 있습니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
```

#### 1.3.8. 듀얼 스택 네트워킹을 위한 OpenShift Container Platform Ingress 컨트롤러 구성

OpenShift Container Platform 클러스터가 IPv4 및 IPv6 이중 스택 네트워킹에 맞게 구성된 경우 OpenShift Container Platform 경로에서 외부에서 클러스터에 연결할 수 있습니다.

Ingress 컨트롤러는 IPv4 및 IPv6 엔드 포인트가 모두 있는 서비스를 자동으로 제공하지만 단일 스택 또는 듀얼 스택 서비스에 대해 Ingress 컨트롤러를 구성할 수 있습니다.

사전 요구 사항

베어메탈에 OpenShift Container Platform 클러스터를 배포했습니다.

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로세스

Ingress 컨트롤러가 워크로드로 IPv4/IPv6을 통해 트래픽을 제공하도록 하려면 `ipFamilies` 및 `ipFamilyPolicy` 필드를 설정하여 서비스 YAML 파일을 생성하거나 기존 서비스 YAML 파일을 수정할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: yyyy-mm-ddT00:00:00Z
  labels:
    name: <service_name>
    manager: kubectl-create
    operation: Update
    time: yyyy-mm-ddT00:00:00Z
  name: <service_name>
  namespace: <namespace_name>
  resourceVersion: "<resource_version_number>"
  selfLink: "/api/v1/namespaces/<namespace_name>/services/<service_name>"
  uid: <uid_number>
spec:
  clusterIP: 172.30.0.0/16
  clusterIPs:
  - 172.30.0.0/16
  - <second_IP_address>
  ipFamilies:
  - IPv4
  - IPv6
  ipFamilyPolicy: RequireDualStack
  ports:
  - port: 8080
    protocol: TCP
    targetport: 8080
  selector:
    name: <namespace_name>
  sessionAffinity: None
  type: ClusterIP
status:
  loadbalancer: {}
```

1. 듀얼 스택 인스턴스에는 두 개의 서로 다른 `clusterIPs` 가 제공됩니다.

2. 단일 스택 인스턴스의 경우 `IPv4` 또는 `IPv6` 을 입력합니다. 듀얼 스택 인스턴스의 경우 `IPv4` 및 `IPv6` 모두를 입력합니다.

3. 단일 스택 인스턴스의 경우 `SingleStack` 을 입력합니다. 듀얼 스택 인스턴스의 경우 `RequireDualStack` 을 입력합니다.

이러한 리소스는 해당 `endpoints` 를 생성합니다. Ingress 컨트롤러는 이제 `endpointslices` 를 감시합니다.

```shell-session
$ oc get endpoints
```

`endpointslices` 를 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get endpointslices
```

### 1.4. 고급 경로 생성

여러 유형의 TLS 종료를 사용하여 클라이언트에 인증서를 제공하는 기능으로 보안 경로를 생성할 수 있습니다. 다음 섹션에서는 사용자 정의 인증서를 사용하여 재암호화 에지 및 패스스루 경로를 생성하는 방법을 설명합니다.

#### 1.4.1. 사용자 정의 인증서를 사용하여 엣지 경로 생성

아래 명령을 사용하면 엣지 TLS 종료와 사용자 정의 인증서로 보안 경로를 구성할 수 있습니다. 엣지 경로를 사용하면 Ingress 컨트롤러에서 트래픽을 대상 Pod로 전달하기 전에 TLS 암호화를 종료합니다. 이 경로는 Ingress 컨트롤러가 경로에 사용하는 TLS 인증서 및 키를 지정합니다.

```shell
oc create route
```

이 절차에서는 사용자 정의 인증서 및 엣지 TLS 종료를 사용하여 `Route` 리소스를 생성합니다. 다음 예에서는 인증서/키 쌍이 현재 작업 디렉터리의 `tls.crt` 및 `tls.key` 파일에 있다고 가정합니다.

인증서 체인을 완료하는 데 필요한 경우 CA 인증서를 지정할 수도 있습니다. `tls.crt`, `tls.key`, `ca.crt` (옵션)에 실제 경로 이름을 사용하십시오.

`frontend` 에는 노출하려는 서비스 이름을 사용합니다. `www.example.com` 을 적절한 호스트 이름으로 바꿉니다.

사전 요구 사항

PEM 인코딩 파일에 인증서/키 쌍이 있고 해당 인증서가 경로 호스트에 유효해야 합니다.

인증서 체인을 완성하는 PEM 인코딩 파일에 별도의 CA 인증서가 있을 수 있습니다.

노출하려는 서비스가 있어야 합니다.

참고

암호로 보호되는 키 파일은 지원되지 않습니다. 키 파일에서 암호를 제거하려면 다음 명령을 사용하십시오.

```shell-session
$ openssl rsa -in password_protected_tls.key -out tls.key
```

프로세스

엣지 TLS 종료 및 사용자 정의 인증서를 사용하여 보안 `Route` 리소스를 생성합니다.

```shell-session
$ oc create route edge --service=frontend --cert=tls.crt --key=tls.key --ca-cert=ca.crt --hostname=www.example.com
```

생성된 `Route` 리소스는 다음과 유사합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
spec:
  host: www.example.com
  to:
    kind: Service
    name: frontend
  tls:
    termination: edge
    key: |-
      -----BEGIN PRIVATE KEY-----
      [...]
      -----END PRIVATE KEY-----
    certificate: |-
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
    caCertificate: |-
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
```

추가 옵션은 다음 명령을 참조하십시오.

```shell
oc create route edge --help
```

#### 1.4.2. 사용자 정의 인증서를 사용하여 재암호화 경로 생성

아래 명령을 사용하여 사용자 정의 인증서와 함께 TLS 종료를 재암호화하여 보안 경로를 구성할 수 있습니다.

```shell
oc create route
```

이 절차에서는 사용자 정의 인증서를 사용하여 `Route` 리소스를 생성하고 TLS 종료를 재암호화합니다. 다음 예에서는 인증서/키 쌍이 현재 작업 디렉터리의 `tls.crt` 및 `tls.key` 파일에 있다고 가정합니다.

Ingress 컨트롤러에서 서비스의 인증서를 신뢰하도록 하려면 대상 CA 인증서도 지정해야 합니다. 인증서 체인을 완료하는 데 필요한 경우 CA 인증서를 지정할 수도 있습니다.

`tls.crt`, `tls.key`, `cacert.crt`, `ca.crt` (옵션)에 실제 경로 이름을 사용하십시오. `frontend` 에는 노출하려는 `서비스` 리소스 이름을 사용합니다.

`www.example.com` 을 적절한 호스트 이름으로 바꿉니다.

사전 요구 사항

PEM 인코딩 파일에 인증서/키 쌍이 있고 해당 인증서가 경로 호스트에 유효해야 합니다.

인증서 체인을 완성하는 PEM 인코딩 파일에 별도의 CA 인증서가 있을 수 있습니다.

PEM 인코딩 파일에 별도의 대상 CA 인증서가 있어야 합니다.

노출하려는 서비스가 있어야 합니다.

참고

암호로 보호되는 키 파일은 지원되지 않습니다. 키 파일에서 암호를 제거하려면 다음 명령을 사용하십시오.

```shell-session
$ openssl rsa -in password_protected_tls.key -out tls.key
```

프로세스

재암호화 TLS 종료 및 사용자 정의 인증서를 사용하여 보안 `Route` 리소스를 생성합니다.

```shell-session
$ oc create route reencrypt --service=frontend --cert=tls.crt --key=tls.key --dest-ca-cert=destca.crt --ca-cert=ca.crt --hostname=www.example.com
```

생성된 `Route` 리소스는 다음과 유사합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
spec:
  host: www.example.com
  to:
    kind: Service
    name: frontend
  tls:
    termination: reencrypt
    key: |-
      -----BEGIN PRIVATE KEY-----
      [...]
      -----END PRIVATE KEY-----
    certificate: |-
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
    caCertificate: |-
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
    destinationCACertificate: |-
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
```

자세한 옵션은 다음 명령을 참조하십시오.

```shell
oc create route reencrypt --help
```

#### 1.4.3. 패스스루 라우팅 생성

아래 명령을 사용하면 패스스루 종료와 사용자 정의 인증서로 보안 경로를 구성할 수 있습니다. 패스스루 종료를 사용하면 암호화된 트래픽이 라우터에서 TLS 종료를 제공하지 않고 바로 대상으로 전송됩니다. 따라서 라우터에 키 또는 인증서가 필요하지 않습니다.

```shell
oc create route
```

사전 요구 사항

노출하려는 서비스가 있어야 합니다.

프로세스

`Route` 리소스를 생성합니다.

```shell-session
$ oc create route passthrough route-passthrough-secured --service=frontend --port=8080
```

생성된 `Route` 리소스는 다음과 유사합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-passthrough-secured
spec:
  host: www.example.com
  port:
    targetPort: 8080
  tls:
    termination: passthrough
    insecureEdgeTerminationPolicy: None
  to:
    kind: Service
    name: frontend
```

1. 63자로 제한되는 개체의 이름입니다.

2. `termination` 필드는 `passthrough` 로 설정됩니다. 이 필드는 유일한 필수 `tls` 필드입니다.

3. `insecureEdgeTerminationPolicy` 는 선택 사항입니다. 비활성화경우 유효한 값은 `None`, `Redirect` 또는 빈 값입니다.

대상 Pod는 끝점의 트래픽에 대한 인증서를 제공해야 합니다. 현재 이 방법은 양방향 인증이라고도 하는 클라이언트 인증서도 지원할 수 있는 유일한 방법입니다.

#### 1.4.4. Ingress 주석에서 대상 CA 인증서를 사용하여 경로 생성

Ingress 오브젝트에 `route.openshift.io/destination-ca-certificate-secret` 주석을 사용하여 사용자 정의 대상 CA 인증서로 경로를 정의할 수 있습니다.

사전 요구 사항

PEM 인코딩 파일에 인증서/키 쌍이 있을 수 있습니다. 여기서 인증서가 경로 호스트에 유효합니다.

인증서 체인을 완성하는 PEM 인코딩 파일에 별도의 CA 인증서가 있을 수 있습니다.

PEM 인코딩 파일에 별도의 대상 CA 인증서가 있어야 합니다.

노출하려는 서비스가 있어야 합니다.

프로세스

다음 명령을 입력하여 대상 CA 인증서에 대한 보안을 생성합니다.

```shell-session
$ oc create secret generic dest-ca-cert --from-file=tls.crt=<file_path>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc -n test-ns create secret generic dest-ca-cert --from-file=tls.crt=tls.crt
```

```shell-session
secret/dest-ca-cert created
```

Ingress 주석에 `route.openshift.io/destination-ca-certificate-secret` 을 추가합니다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: secret-ca-cert
...
```

1. 이 주석은 kubernetes 시크릿을 참조합니다.

이 주석에서 참조된 시크릿은 생성된 경로에 삽입됩니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: reencrypt
    route.openshift.io/destination-ca-certificate-secret: secret-ca-cert
spec:
...
  tls:
    insecureEdgeTerminationPolicy: Redirect
    termination: reencrypt
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
...
```

#### 1.4.5. 외부 관리형 인증서를 사용하여 경로 생성

경로 API의 `.spec.tls.externalCertificate` 필드를 사용하여 타사 인증서 관리 솔루션으로 OpenShift Container Platform 경로를 구성할 수 있습니다. 시크릿을 통해 외부 관리형 TLS 인증서를 참조할 수 있으므로 수동 인증서 관리가 필요하지 않습니다.

외부 관리형 인증서를 사용하면 오류를 줄여 인증서 업데이트를 원활하게 롤아웃하고 OpenShift 라우터에서 갱신된 인증서를 즉시 제공할 수 있습니다. 에지 경로 및 재암호화 경로 둘 다와 함께 외부 관리형 인증서를 사용할 수 있습니다.

사전 요구 사항

`tls.key` 및 `tls.crt` 키가 모두 포함된 `kubernetes.io/tls` 유형의 PEM 인코딩 형식으로 유효한 인증서 또는 키 쌍을 포함하는 시크릿이 있어야 합니다. 예:.

```shell
$ oc create secret tls myapp-tls --cert=server.crt --key=server.key
```

프로세스

다음 명령을 실행하여 라우터 서비스 계정 읽기 권한을 허용하기 위해 시크릿과 동일한 네임스페이스에 `역할` 오브젝트를 생성합니다.

```shell-session
$ oc create role secret-reader --verb=get,list,watch --resource=secrets --resource-name=<secret-name> \
--namespace=<current-namespace>
```

`<secret-name` >: 시크릿의 실제 이름을 지정합니다.

`<current-namespace` >: 시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

보안과 동일한 네임스페이스에 `rolebinding` 오브젝트를 생성하고 다음 명령을 실행하여 라우터 서비스 계정을 새로 생성된 역할에 바인딩합니다.

```shell-session
$ oc create rolebinding secret-reader-binding --role=secret-reader --serviceaccount=openshift-ingress:router --namespace=<current-namespace>
```

`<current-namespace` >: 시크릿과 경로가 모두 있는 네임스페이스를 지정합니다.

`경로를` 정의하는 YAML 파일을 생성하고 다음 예제를 사용하여 인증서가 포함된 보안을 지정합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: myedge
  namespace: test
spec:
  host: myedge-test.apps.example.com
  tls:
    externalCertificate:
      name: <secret-name>
    termination: edge
    [...]
[...]
```

`<secret-name` >: 시크릿의 실제 이름을 지정합니다.

다음 명령을 실행하여 `경로` 리소스를 생성합니다.

```shell-session
$ oc apply -f <route.yaml>
```

`<route.yaml&` gt;: 생성된 YAML 파일 이름을 지정합니다.

보안이 존재하고 인증서/키 쌍이 있는 경우 라우터는 모든 사전 요구 사항을 충족하는 경우 생성된 인증서를 제공합니다.

참고

`.spec.tls.externalCertificate` 가 제공되지 않으면 라우터에서 기본 생성된 인증서를 사용합니다.

`.spec.tls.externalCertificate` 필드를 사용하는 경우 `.spec.tls.certificate` 필드 또는 `.spec.tls.key` 필드를 지정할 수 없습니다.

#### 1.4.6. Ingress 오브젝트를 통해 기본 인증서를 사용하여 경로 생성

TLS 구성을 지정하지 않고 Ingress 오브젝트를 생성하면 OpenShift Container Platform에서 비보안 경로를 생성합니다. 기본 Ingress 인증서를 사용하여 보안 에지 종료 경로를 생성하는 Ingress 오브젝트를 생성하려면 다음과 같이 빈 TLS 구성을 지정할 수 있습니다.

사전 요구 사항

노출하려는 서비스가 있습니다.

OpenShift CLI()에 액세스할 수 있습니다.

```shell
oc
```

프로세스

Ingress 오브젝트에 대한 YAML 파일을 생성합니다. 이 예제에서는 파일을 `example-ingress.yaml` 이라고 합니다.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  ...
spec:
  rules:
    ...
  tls:
  - {}
```

1. 사용자 정의 인증서를 지정하지 않고 TLS를 지정하려면 이 정확한 구문을 사용합니다.

다음 명령을 실행하여 Ingress 오브젝트를 생성합니다.

```shell-session
$ oc create -f example-ingress.yaml
```

검증

다음 명령을 실행하여 OpenShift Container Platform에서 Ingress 오브젝트에 대한 예상 경로를 생성했는지 확인합니다.

```shell-session
$ oc get routes -o yaml
```

```yaml
apiVersion: v1
items:
- apiVersion: route.openshift.io/v1
  kind: Route
  metadata:
    name: frontend-j9sdd
    ...
  spec:
  ...
    tls:
      insecureEdgeTerminationPolicy: Redirect
      termination: edge
  ...
```

1. 경로 이름에는 Ingress 오브젝트의 이름 뒤에 임의의 접미사가 포함됩니다.

2. 기본 인증서를 사용하려면 경로에서 `spec.certificate` 를 지정하지 않아야 합니다.

3. 경로는 `엣지` 종료 정책을 지정해야 합니다.

### 2.1. 수신 클러스터 트래픽 구성 개요

OpenShift Container Platform에서는 다음 방법을 통해 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있습니다.

순서 또는 기본 설정에 따라 권장되는 방법입니다.

HTTP/HTTPS가 있는 경우 Ingress 컨트롤러를 사용합니다.

HTTPS 이외의 TLS 암호화 프로토콜이 있는 경우(예: SNI 헤더가 있는 TLS), Ingress 컨트롤러를 사용합니다.

그 외에는 로드 밸런서, 외부 IP 또는 `NodePort` 를 사용합니다.

| 방법 | 목적 |
| --- | --- |
| Ingress 컨트롤러 사용 | HTTPS 이외의 HTTP/HTTPS 트래픽 및 TLS 암호화 프로토콜(예: SNI 헤더가 있는 TLS)에 액세스할 수 있습니다. |
| 로드 밸런서 서비스를 사용하여 외부 IP 자동 할당 | 풀에서 할당된 IP 주소를 통해 비표준 포트로의 트래픽을 허용합니다. 대부분의 클라우드 플랫폼은 로드 밸런서 IP 주소로 서비스를 시작하는 방법을 제공합니다. |
| MetalLB 및 MetalLB Operator 정보 | 시스템 네트워크의 풀에서 특정 IP 주소 또는 주소로의 트래픽을 허용합니다. 베어 메탈과 같은 베어 메탈 설치 또는 플랫폼의 경우 MetalLB는 로드 밸런서 IP 주소로 서비스를 시작하는 방법을 제공합니다. |
| 서비스에 외부 IP를 수동으로 할당 | 특정 IP 주소를 통해 비표준 포트로의 트래픽을 허용합니다. |
| `NodePort` 구성 | 클러스터의 모든 노드에 서비스를 공개합니다. |

#### 2.1.1. 비교: 외부 IP 주소에 대한 내결함성 액세스

외부 IP 주소에 대한 액세스를 제공하는 통신 방법의 경우 IP 주소에 대한 내결함성 액세스를 고려해야 합니다. 다음 기능은 외부 IP 주소에 대한 내결함성 액세스를 제공합니다.

IP 페일오버

IP 페일오버는 노드 집합의 가상 IP 주소 풀을 관리합니다. Keepalived 및 VRRP(Virtual Router Redundancy Protocol)로 구현됩니다. IP 페일오버는 계층 2 메커니즘일 뿐이며 멀티캐스트를 사용합니다. 멀티캐스트에는 일부 네트워크에 대한 단점이 있을 수 있습니다.

MetalLB

MetalLB에는 계층 2 모드가 있지만 멀티캐스트를 사용하지 않습니다. 계층 2 모드에는 하나의 노드를 통해 외부 IP 주소에 대한 모든 트래픽을 전송하는 단점이 있습니다.

수동으로 외부 IP 주소 할당

외부 IP 주소를 서비스에 할당하는 데 사용되는 IP 주소 블록을 사용하여 클러스터를 구성할 수 있습니다. 이 기능은 기본적으로 비활성화되어 있습니다. 이 기능은 유연하지만 클러스터 또는 네트워크 관리자에게 가장 큰 부담이 됩니다. 클러스터는 외부 IP로 향하는 트래픽을 수신할 준비가 되지만 각 고객은 트래픽을 노드로 라우팅하는 방법을 결정해야 합니다.

### 2.2. 서비스의 ExternalIP 구성

클러스터 관리자는 클러스터의 서비스로 트래픽을 보낼 수 있는 클러스터 외부의 IP 주소 블록을 선택할 수 있습니다.

이 기능은 일반적으로 베어 메탈 하드웨어에 설치된 클러스터에 가장 유용합니다.

#### 2.2.1. 사전 요구 사항

네트워크 인프라는 외부 IP 주소에 대한 트래픽을 클러스터로 라우팅해야 합니다.

#### 2.2.2. ExternalIP 정보

클라우드 환경이 아닌 경우 OpenShift Container Platform은 ExternalIP 기능을 사용하여 `Service` 오브젝트의 `spec.externalIPs[]` 매개변수에 외부 IP 주소를 지정할 수 있습니다. ExternalIP로 구성된 서비스는 `type=NodePort` 인 서비스와 유사하게 작동합니다.

여기서 트래픽이 로드 밸런싱을 위해 로컬 노드로 전달합니다.

중요

클라우드 환경의 경우 클라우드 로드 밸런서 자동 배포를 위해 로드 밸런서 서비스를 사용하여 서비스 끝점을 대상으로 합니다.

매개변수 값을 지정하면 OpenShift Container Platform에서 추가 가상 IP 주소를 서비스에 할당합니다. IP 주소는 클러스터에 대해 정의한 서비스 네트워크 외부에 있을 수 있습니다.

주의

ExternalIP는 기본적으로 비활성화되어 있으므로 ExternalIP 기능을 활성화하면 외부 IP 주소에 대한 클러스터 내 트래픽이 해당 서비스로 전달되므로 서비스에 보안 위험이 발생할 수 있습니다. 이 구성을 사용하면 클러스터 사용자가 외부 리소스로 향하는 민감한 트래픽을 가로챌 수 있습니다.

MetalLB 구현 또는 IP 페일오버 배포를 사용하여 다음과 같은 방법으로 ExternalIP 리소스를 서비스에 연결할 수 있습니다.

외부 IP 자동 할당

OpenShift Container Platform에서는 `spec.type=LoadBalancer` 가 설정된 `Service` 오브젝트를 생성할 때 `autoAssignCIDRs` CIDR 블록의 IP 주소를 `spec.externalIPs[]` 배열에 자동으로 할당합니다.

이 구성을 위해 OpenShift Container Platform은 로드 밸런서 서비스 유형의 클라우드 버전을 구현하고 서비스에 IP 주소를 할당합니다. 자동 할당은 기본적으로 비활성화되어 있으며 " ExternalIP용 구성" 섹션에 설명된 대로 클러스터 관리자가 구성해야 합니다.

외부 IP 수동 할당

OpenShift Container Platform에서는 `Service` 오브젝트를 생성할 때 `spec.externalIPs[]` 배열에 할당된 IP 주소를 사용합니다. 다른 서비스에서 이미 사용 중인 IP 주소는 지정할 수 없습니다.

MetalLB 구현 또는 IP 페일오버 배포를 사용하여 외부 IP 주소 블록을 호스팅한 후 외부 IP 주소 블록이 클러스터로 라우팅되도록 네트워킹 인프라를 구성해야 합니다. 이 구성은 IP 주소가 노드의 네트워크 인터페이스에 구성되지 않았음을 의미합니다.

트래픽을 처리하려면 ARM(Static Address Resolution Protocol) 항목과 같은 방법을 사용하여 라우팅 및 외부 IP에 대한 액세스를 구성해야 합니다.

OpenShift Container Platform은 다음 기능을 추가하여 Kubernetes의 ExternalIP 기능을 확장합니다.

구성 가능한 정책을 통해 사용자가 외부 IP 주소 사용 제한

요청 시 서비스에 자동으로 외부 IP 주소 할당

#### 2.2.3. ExternalIP 구성

`Network.config.openshift.io` CR(사용자 정의 리소스)의 다음 매개변수는 OpenShift Container Platform의 외부 IP 주소 사용을 제어합니다.

`spec.externalIP.autoAssignCIDRs` 는 서비스에 대한 외부 IP 주소를 선택할 때 로드 밸런서에서 사용하는 IP 주소 블록을 정의합니다. OpenShift Container Platform에서는 자동 할당에 대해 하나의 IP 주소 블록만 지원합니다.

이 구성에는 서비스에 ExternalIP를 수동으로 할당하는 것보다 적은 단계가 필요하므로 제한된 수의 공유 IP 주소의 포트 공간을 관리해야 합니다.

자동 할당을 활성화하면 Cloud Controller Manager Operator는 구성에서 `spec.type=LoadBalancer` defind를 사용하여 `서비스` 오브젝트에 외부 IP 주소를 할당합니다.

`spec.externalIP.policy` 는 IP 주소를 수동으로 지정할 때 허용되는 IP 주소 블록을 정의합니다. OpenShift Container Platform은 `spec.externalIP.autoAssignCIDRs` 매개변수에 정의된 IP 주소 블록에 정책 규칙을 적용하지 않습니다.

올바르게 라우팅되면 구성된 외부 IP 주소 블록의 외부 트래픽이 서비스에서 노출하는 TCP 또는 UDP 포트를 통해 서비스 끝점에 도달할 수 있습니다.

중요

클러스터 관리자는 externalIP로 라우팅을 구성해야 합니다. 또한 할당하는 IP 주소 블록이 클러스터의 하나 이상의 노드에서 종료되는지 확인해야 합니다. 자세한 내용은 Kubernetes 외부 IP를 참조하십시오.

OpenShift Container Platform은 자동 및 수동 IP 주소 할당을 모두 지원합니다. 이 지원을 통해 각 주소가 최대 하나의 서비스에 할당되고 각 서비스가 다른 서비스에서 노출하는 포트와 관계없이 선택한 포트를 노출할 수 있습니다.

참고

OpenShift Container Platform에서 `autoAssignCIDR` 로 정의된 IP 주소 블록을 사용하려면 호스트 네트워크에 필요한 IP 주소 할당 및 라우팅을 구성해야 합니다.

다음 YAML에서는 외부 IP 주소가 구성된 서비스를 설명합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: http-service
spec:
  clusterIP: 172.30.163.110
  externalIPs:
  - 192.168.132.253
  externalTrafficPolicy: Cluster
  ports:
  - name: highport
    nodePort: 31903
    port: 30102
    protocol: TCP
    targetPort: 30102
  selector:
    app: web
  sessionAffinity: None
  type: LoadBalancer
status:
  loadBalancer:
    ingress:
    - ip: 192.168.132.253
# ...
```

클라우드 공급자 플랫폼에서 프라이빗 클러스터를 실행하는 경우 다음 `패치` 명령을 실행하여 Ingress 컨트롤러의 로드 밸런서에 대한 게시 범위를 `internal` 로 변경할 수 있습니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontrollers/ingress-controller-with-nlb --type=merge --patch='{"spec":{"endpointPublishingStrategy":{"loadBalancer":{"scope":"Internal"}}}}'
```

이 명령을 실행하면 Ingress 컨트롤러는 OpenShift Container Platform 애플리케이션의 경로에 대한 액세스를 내부 네트워크로만 제한합니다.

#### 2.2.4. 외부 IP 주소 할당 제한 사항

클러스터 관리자는 IP 주소 블록을 지정하여 서비스의 IP 주소를 허용할 수 있습니다. 제한 사항은 `cluster-admin` 권한이 없는 사용자에게만 적용됩니다. 클러스터 관리자는 서비스 `spec.externalIPs[]` 필드를 IP 주소로 항상 설정할 수 있습니다.

정책 오브젝트에서 `spec.ExternalIP.policy` 매개변수에 대해 CIDR(Classless Inter-Domain Routing) 주소 블록을 지정하여 IP 주소 `정책을` 구성합니다.

```plaintext
{
  "policy": {
    "allowedCIDRs": [],
    "rejectedCIDRs": []
  }
}
```

정책 제한을 구성할 때는 다음 규칙이 적용됩니다.

`policy` 가 `{}` 로 설정된 경우 `spec.ExternalIPs[]` 를 사용하여 `Service` 를 생성하면 실패한 서비스가 생성됩니다. 이 설정은 OpenShift Container Platform의 기본값입니다. `정책에도 동일한 동작이 있습니다. null`.

`policy` 가 설정되고 `policy.allowedCIDRs[]` 또는 `policy.rejectedCIDRs[]` 가 설정된 경우 다음 규칙이 적용됩니다.

`allowedCIDRs[]` 및 `rejectedCIDRs[]` 가 둘 다 설정된 경우 `rejectedCIDRs[]` 가 `allowedCIDRs[]` 보다 우선합니다.

`allowedCIDRs[]` 가 설정된 경우 지정된 IP 주소가 허용되는 경우에만 `spec.ExternalIPs[]` 를 사용하여 `Service` 오브젝트를 생성합니다.

`rejectedCIDRs[]` 가 설정된 경우 지정된 IP 주소가 거부되지 않는 경우에만 `spec.ExternalIPs[]` 를 사용하여 `Service` 오브젝트를 생성할 수 있습니다.

#### 2.2.5. 정책 오브젝트의 예

이 섹션의 예제에서는 다른 `spec.externalIP.policy` 구성을 보여줍니다.

다음 예에서 정책은 OpenShift Container Platform에서 지정된 외부 IP 주소로 서비스를 생성하지 못하도록 합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  externalIP:
    policy: {}
# ...
```

다음 예에서는 `allowedCIDRs` 및 `rejectedCIDRs` 필드가 모두 설정되어 있습니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  externalIP:
    policy:
      allowedCIDRs:
      - 172.16.66.10/23
      rejectedCIDRs:
      - 172.16.66.10/24
# ...
```

다음 예에서 `policy` 는 `{}` 로 설정됩니다. 이 구성으로 아래 명령을 사용하여 configuration means `policy` 매개변수가 명령 출력에 표시되지 않습니다. `정책에도 동일한 동작이 있습니다. null`.

```shell
oc get networks.config.openshift.io -o yaml
```

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  clusterNetwork:
  - cidr: 10.128.0.0/14
    hostPrefix: 23
  externalIP:
    policy: {}
# ...
```

#### 2.2.6. ExternalIP 주소 블록 구성

ExternalIP 주소 블록에 대한 구성은 `cluster` 라는 네트워크 CR(사용자 정의 리소스)에 의해 정의됩니다. 네트워크 CR은 `config.openshift.io` API 그룹의 일부입니다.

중요

CVO(Cluster Version Operator)는 클러스터를 설치하는 동안 `cluster` 라는 네트워크 CR을 자동으로 생성합니다. 이 유형의 다른 CR 오브젝트는 생성할 수 없습니다.

다음 YAML에서는 ExternalIP 구성을 설명합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  externalIP:
    autoAssignCIDRs: []
    policy:
      ...
```

1. 서비스에 대한 외부 IP 주소 자동 할당에 사용할 수 있는 CIDR 형식으로 IP 주소 블록을 정의합니다. 단일 IP 주소 범위만 허용됩니다.

2. 서비스에 대한 IP 주소 수동 할당에 대한 제한을 정의합니다. 제한이 정의되지 않은 경우 `Service` 에서 `spec.externalIP` 필드를 지정할 수 없습니다. 기본적으로는 제한이 정의되어 있지 않습니다.

다음 YAML에서는 `policy` 스탠자의 필드를 설명합니다.

```yaml
policy:
  allowedCIDRs: []
  rejectedCIDRs: []
```

1. CIDR 형식의 허용된 IP 주소 범위 목록입니다.

2. CIDR 형식의 거부된 IP 주소 범위 목록입니다.

#### 2.2.6.1. 외부 IP 구성의 예

외부 IP 주소 풀에 사용 가능한 몇 가지 구성이 다음 예에 표시되어 있습니다.

다음 YAML에서는 자동으로 할당된 외부 IP 주소를 사용하는 구성을 설명합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  ...
  externalIP:
    autoAssignCIDRs:
    - 192.168.132.254/29
```

다음 YAML에서는 허용되거나 거부된 CIDR 범위에 대한 정책 규칙을 구성합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  ...
  externalIP:
    policy:
      allowedCIDRs:
      - 192.168.132.0/29
      - 192.168.132.8/29
      rejectedCIDRs:
      - 192.168.132.7/32
```

#### 2.2.7. 클러스터에 대한 외부 IP 주소 블록 구성

클러스터 관리자는 다음 ExternalIP 설정을 구성할 수 있습니다.

`Service` 오브젝트의 `spec.clusterIP` 필드를 자동으로 채우도록 OpenShift Container Platform에서 사용하는 ExternalIP 주소 블록입니다.

`Service` 오브젝트의 `spec.clusterIP` 배열에 수동으로 할당할 수 있는 IP 주소를 제한하는 정책 오브젝트입니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

프로세스

선택 사항: 현재 외부 IP 구성을 표시하려면 다음 명령을 입력합니다.

```shell-session
$ oc describe networks.config cluster
```

구성을 편집하려면 다음 명령을 입력합니다.

```shell-session
$ oc edit networks.config cluster
```

다음 예와 같이 ExternalIP 구성을 수정합니다.

```yaml
apiVersion: config.openshift.io/v1
kind: Network
metadata:
  name: cluster
spec:
  ...
  externalIP:
  ...
```

1. `externalIP` 스탠자에 대한 구성을 지정합니다.

업데이트된 ExternalIP 구성을 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get networks.config cluster -o go-template='{{.spec.externalIP}}{{"\n"}}'
```

#### 2.2.8. 추가 리소스

IP 페일오버 구성

MetalLB 및 MetalLB Operator 정보

#### 2.2.9. 다음 단계

서비스 외부 IP에 대한 수신 클러스터 트래픽 구성

### 2.3. Ingress 컨트롤러를 사용한 수신 클러스터 트래픽 구성

OpenShift Container Platform에서는 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있습니다. 이 방법에서는 Ingress 컨트롤러를 사용합니다.

#### 2.3.1. Ingress 컨트롤러 및 경로 사용

Ingress Operator에서는 Ingress 컨트롤러 및 와일드카드 DNS를 관리합니다.

OpenShift Container Platform 클러스터에 대한 외부 액세스를 허용하는 가장 일반적인 방법은 Ingress 컨트롤러를 사용하는 것입니다.

Ingress 컨트롤러는 외부 요청을 수락하고 구성된 경로를 기반으로 이러한 요청을 프록시하도록 구성되어 있습니다. 이는 HTTP, SNI를 사용하는 HTTPS, SNI를 사용하는 TLS로 제한되며, SNI를 사용하는 TLS를 통해 작동하는 웹 애플리케이션 및 서비스에 충분합니다.

관리자와 협력하여 구성된 경로를 기반으로 외부 요청을 수락하고 프록시하도록 Ingress 컨트롤러를 구성하십시오.

관리자는 와일드카드 DNS 항목을 생성한 다음 Ingress 컨트롤러를 설정할 수 있습니다. 그러면 관리자에게 문의하지 않고도 엣지 Ingress 컨트롤러로 작업할 수 있습니다.

기본적으로 클러스터의 모든 Ingress 컨트롤러는 클러스터의 모든 프로젝트에서 생성된 모든 경로를 허용할 수 있습니다.

Ingress 컨트롤러의 경우

기본적으로 두 개의 복제본이 있으므로 두 개의 작업자 노드에서 실행되어야 합니다.

더 많은 노드에 더 많은 복제본을 갖도록 확장할 수 있습니다.

참고

이 섹션의 절차에는 클러스터 관리자가 수행해야 하는 사전 요구 사항이 필요합니다.

#### 2.3.2. 사전 요구 사항

다음 절차를 시작하기 전에 관리자는 다음을 수행해야 합니다.

요청이 클러스터에 도달할 수 있도록 외부 포트를 클러스터 네트워킹 환경으로 설정합니다.

클러스터 관리자 역할의 사용자가 한 명 이상 있는지 확인합니다. 이 역할을 사용자에게 추가하려면 다음 명령을 실행합니다.

```plaintext
$ oc adm policy add-cluster-role-to-user cluster-admin username
```

클러스터에 대한 네트워크 액세스 권한이 있는 마스터와 노드가 하나 이상 있고 클러스터 외부의 시스템이 있는 OpenShift Container Platform 클러스터가 있어야 합니다. 이 절차에서는 외부 시스템이 클러스터와 동일한 서브넷에 있다고 가정합니다. 다른 서브넷에 있는 외부 시스템에 필요한 추가 네트워킹은 이 주제에서 다루지 않습니다.

#### 2.3.3. 프로젝트 및 서비스 생성

노출하려는 프로젝트 및 서비스가 존재하지 않는 경우 프로젝트를 생성한 다음 서비스를 생성합니다.

프로젝트 및 서비스가 이미 존재하는 경우 서비스 노출 절차로 건너뛰어 경로를 생성합니다.

사전 요구 사항

OpenShift CLI()를 설치하고 클러스터 관리자로 로그인합니다.

```shell
oc
```

프로세스

아래 명령을 실행하여 서비스에 대한 새 프로젝트를 생성합니다.

```shell
oc new-project
```

```shell-session
$ oc new-project <project_name>
```

아래 명령을 사용하여 서비스를 생성합니다.

```shell
oc new-app
```

```shell-session
$ oc new-app nodejs:12~https://github.com/sclorg/nodejs-ex.git
```

서비스가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get svc -n <project_name>
```

```shell-session
NAME        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
nodejs-ex   ClusterIP   172.30.197.157   <none>        8080/TCP   70s
```

참고

기본적으로 새 서비스에는 외부 IP 주소가 없습니다.

#### 2.3.4. 경로를 생성하여 서비스 노출

아래 명령을 사용하여 서비스를 경로로 노출할 수 있습니다.

```shell
oc expose
```

사전 요구 사항

OpenShift Container Platform에 로그인되어 있습니다.

프로세스

노출하려는 서비스가 있는 프로젝트에 로그인합니다.

```shell-session
$ oc project <project_name>
```

아래 명령을 실행하여 경로를 노출합니다.

```shell
oc expose service
```

```shell-session
$ oc expose service nodejs-ex
```

```shell-session
route.route.openshift.io/nodejs-ex exposed
```

서비스가 노출되었는지 확인하려면 다음 명령과 같은 툴을 사용하여 클러스터 외부에서 서비스에 액세스할 수 있는지 확인할 수 있습니다.

```shell
curl
```

경로의 호스트 이름을 찾으려면 다음 명령을 입력합니다.

```shell-session
$ oc get route
```

```shell-session
NAME        HOST/PORT                        PATH   SERVICES    PORT       TERMINATION   WILDCARD
nodejs-ex   nodejs-ex-myproject.example.com         nodejs-ex   8080-tcp                 None
```

호스트가 GET 요청에 응답하는지 확인하려면 다음 명령을 입력합니다.

```shell
curl
```

```shell-session
$ curl --head nodejs-ex-myproject.example.com
```

```shell-session
HTTP/1.1 200 OK
...
```

#### 2.3.5. OpenShift Container Platform의 Ingress 분할

OpenShift Container Platform에서 Ingress 컨트롤러는 모든 경로를 제공하거나 경로 서브 세트를 제공할 수 있습니다. 기본적으로 Ingress 컨트롤러는 클러스터의 모든 네임스페이스에서 생성된 모든 경로를 제공합니다.

선택한 특성을 기반으로 하는 경로의 하위 집합인 shard 를 생성하여 라우팅을 최적화하기 위해 클러스터에 Ingress 컨트롤러를 추가할 수 있습니다. 경로를 shard의 멤버로 표시하려면 경로 또는 네임스페이스 `메타데이터` 필드의 라벨을 사용합니다.

Ingress 컨트롤러는 선택 표현식 이라고도 하는 선택기 를 사용하여 제공할 전체 경로 풀에서 경로 서브 세트를 선택합니다.

Ingress 분할은 여러 Ingress 컨트롤러에서 들어오는 트래픽을 로드 밸런싱하거나, 트래픽을 특정 Ingress 컨트롤러로 라우팅하려는 경우 또는 다음 섹션에 설명된 다양한 다른 이유로 유용합니다.

기본적으로 각 경로는 클러스터의 기본 도메인을 사용합니다. 그러나 라우터의 도메인을 사용하도록 경로를 구성할 수 있습니다.

#### 2.3.6. Ingress 컨트롤러 분할

라우터 샤딩이라고도 하는 Ingress 분할을 사용하여 경로, 네임스페이스 또는 둘 다에 라벨을 추가하여 여러 라우터에 경로 세트를 배포할 수 있습니다. Ingress 컨트롤러는 해당 선택기 세트를 사용하여 라벨이 지정된 경로만 허용합니다. 각 Ingress shard는 지정된 선택 표현식을 사용하여 필터링된 경로로 구성됩니다.

클러스터로 들어오는 트래픽의 기본 메커니즘으로 Ingress 컨트롤러의 요구 사항이 중요할 수 있습니다. 클러스터 관리자는 다음을 위해 경로를 분할할 수 있습니다.

변경 사항에 대한 응답을 가속화하기 위해 여러 경로를 사용하여 Ingress 컨트롤러 또는 라우터의 균형을 조정합니다.

특정 경로를 할당하여 다른 경로와 안정성을 보장합니다.

특정 Ingress 컨트롤러에 다른 정책을 정의할 수 있도록 허용

특정 경로만 추가 기능을 사용하도록 허용

예를 들어, 내부 및 외부 사용자가 다른 경로를 볼 수 있도록 다른 주소에 다른 경로를 노출

Blue-Green 배포 중에 한 버전의 애플리케이션에서 다른 애플리케이션으로 트래픽을 전송합니다.

Ingress 컨트롤러가 분할되면 지정된 경로가 그룹의 Ingress 컨트롤러가 0개 이상 허용됩니다. 경로 상태는 Ingress 컨트롤러가 경로를 수락했는지 여부를 나타냅니다. Ingress 컨트롤러는 경로가 shard에 고유한 경우에만 경로를 허용합니다.

분할을 사용하면 여러 Ingress 컨트롤러를 통해 경로 서브 세트를 배포할 수 있습니다. 이러한 하위 집합은 겹치지 않거나 기존 샤딩이라고도 하거나 겹치는 분할이라고 할 수 있습니다. 그렇지 않으면 중복 분할이라고 합니다.

다음 표에서는 다음 세 가지 분할 방법을 간략하게 설명합니다.

| 샤딩 방법 | 설명 |
| --- | --- |
| 네임스페이스 선택기 | Ingress 컨트롤러에 네임스페이스 선택기를 추가하면 네임스페이스 선택기에 일치하는 라벨이 있는 네임스페이스의 모든 경로가 Ingress shard에 포함됩니다. Ingress 컨트롤러가 네임스페이스에서 생성된 모든 경로를 제공할 때 이 방법을 고려하십시오. |
| 경로 선택기 | Ingress 컨트롤러에 경로 선택기를 추가하면 경로 선택기와 일치하는 라벨이 있는 모든 경로가 Ingress shard에 포함됩니다. Ingress 컨트롤러에서 경로의 하위 집합 또는 네임스페이스의 특정 경로만 제공하려는 경우 이 방법을 고려하십시오. |
| 네임스페이스 및 경로 선택기 | 네임스페이스 선택기 및 경로 선택기 방법 모두에 대한 Ingress 컨트롤러 범위를 제공합니다. 네임스페이스 선택기와 경로 선택기 방법의 유연성을 원할 때 이 방법을 고려하십시오. |

#### 2.3.6.1. 기존 분할 예

레이블 선택기 `spec.namespaceSelector.matchExpressions` 가 있는 구성된 Ingress 컨트롤러 `finops-router` 의 예로, key 값이 financial 및 `ops` 로 설정되어 있습니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: finops-router
  namespace: openshift-ingress-operator
spec:
  namespaceSelector:
    matchExpressions:
    - key: name
      operator: In
      values:
      - finance
      - ops
```

선택기 `spec.namespaceSelector.matchLabels.name` 레이블이 `dev` 로 설정된 구성된 Ingress 컨트롤러 `dev-router` 의 예입니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: dev-router
  namespace: openshift-ingress-operator
spec:
  namespaceSelector:
    matchLabels:
      name: dev
```

`name:finance`, `name:ops`, `name:dev` 로 레이블이 지정된 각 네임스페이스와 같은 모든 애플리케이션 경로가 별도의 네임스페이스에 있는 경우 구성은 두 Ingress 컨트롤러 간에 경로를 효과적으로 배포합니다. 콘솔, 인증 및 기타 용도로 사용되는 OpenShift Container Platform 경로를 처리해서는 안 됩니다.

이전 시나리오에서는 분할의 특수한 경우가 되며 하위 집합이 겹치지 않습니다. 경로는 라우터 shard로 나뉩니다.

주의

`기본` Ingress 컨트롤러는 `namespaceSelector` 또는 `routeSelector` 필드에 제외를 위한 경로가 포함되지 않는 한 모든 경로를 계속 제공합니다. 기본 Ingress 컨트롤러에서 경로를 제외하는 방법에 대한 자세한 내용은 이 Red Hat Knowledgebase 솔루션 및 "기본 Ingress 컨트롤러 공유" 섹션을 참조하십시오.

#### 2.3.6.2. 중복된 분할 예

선택기 spec.namespaceSelector.matchExpressions에 `dev` 및 `ops` 로 설정된 라벨 선택기 `spec.namespaceSelector.matchExpressions` 가 있는 구성된 Ingress 컨트롤러 Cryostat `-router` 의 예

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: devops-router
  namespace: openshift-ingress-operator
spec:
  namespaceSelector:
    matchExpressions:
    - key: name
      operator: In
      values:
      - dev
      - ops
```

`name:dev` 및 `name:ops` 레이블이 지정된 네임스페이스의 경로는 이제 두 개의 다른 Ingress 컨트롤러에서 서비스를 제공합니다. 이 구성을 사용하면 경로의 하위 집합이 겹치게 됩니다.

경로의 하위 집합을 겹치는 상태에서 더 복잡한 라우팅 규칙을 생성할 수 있습니다. 예를 들어 우선순위가 더 높은 트래픽을 전용 `finops-router` 로 분산하는 동안 우선순위가 낮은 트래픽을 Cryostat `-router` 로 보낼 수 있습니다.

#### 2.3.6.3. 기본 Ingress 컨트롤러 분할

새 Ingress shard를 생성한 후 기본 Ingress 컨트롤러에서 승인한 새 Ingress shard에 허용되는 경로가 있을 수 있습니다. 이는 기본 Ingress 컨트롤러에 선택기가 없으며 기본적으로 모든 경로를 허용하기 때문입니다.

네임스페이스 선택기 또는 경로 선택기를 사용하여 특정 라벨이 있는 라우팅에서 Ingress 컨트롤러를 제한할 수 있습니다. 다음 절차에서는 네임스페이스 선택기를 사용하여 기본 Ingress 컨트롤러가 새로 shard된 financial, `ops`, `dev` 경로를 서비스하지 못하도록 제한합니다. 이렇게 하면 Ingress shard에 추가 격리가 추가됩니다.

중요

동일한 Ingress 컨트롤러에 모든 OpenShift Container Platform 관리 경로를 유지해야 합니다. 따라서 이러한 필수 경로를 제외하는 기본 Ingress 컨트롤러에 선택기를 추가하지 마십시오.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로젝트 관리자로 로그인했습니다.

프로세스

다음 명령을 실행하여 기본 Ingress 컨트롤러를 수정합니다.

```shell-session
$ oc edit ingresscontroller -n openshift-ingress-operator default
```

financial, `ops`, `dev` 라벨이 있는 경로를 제외하는 `namespaceSelector`

`를` 포함하도록 Ingress 컨트롤러를 편집합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  namespaceSelector:
    matchExpressions:
      - key: name
        operator: NotIn
        values:
          - finance
          - ops
          - dev
```

기본 Ingress 컨트롤러는 더 이상 `name:finance`, `name:ops`, `name:dev` 이라는 네임스페이스를 제공하지 않습니다.

#### 2.3.6.4. Ingress 샤딩 및 DNS

클러스터 관리자는 프로젝트의 각 라우터에 대해 별도의 DNS 항목을 만듭니다. 라우터는 알 수 없는 경로를 다른 라우터로 전달하지 않습니다.

다음 예제를 고려하십시오.

라우터 A는 호스트 192.168.0.5에 있으며 `*.foo.com` 이 있는 경로가 있습니다.

라우터 B는 호스트 192.168.1.9에 있으며 `*.example.com` 이 있는 경로가 있습니다.

별도의 DNS 항목은 라우터 B를 호스팅하는 노드와 `*.example.com` 을 호스팅하는 노드로 `*.foo.com` 을 확인해야 합니다.

`*.foo.com A IN 192.168.0.5`

`*.example.com A IN 192.168.1.9`

#### 2.3.6.5. 경로 라벨을 사용하여 Ingress 컨트롤러 분할 구성

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/nw-sharding-route-labels.png" alt="경로가 속하는 네임스페이스와 관계없이 지정된 경로 선택기와 일치하는 라벨을 포함하는 모든 경로를 제공하는 다른 경로 선택기가 있는 여러 Ingress 컨트롤러를 보여주는 다이어그램" kind="diagram" diagram_type="semantic_diagram"]
경로가 속하는 네임스페이스와 관계없이 지정된 경로 선택기와 일치하는 라벨을 포함하는 모든 경로를 제공하는 다른 경로 선택기가 있는 여러 Ingress 컨트롤러를 보여주는 다이어그램
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/88e02b6d127bf165fed27d7c18366e6a/nw-sharding-route-labels.png`_


경로 라벨을 사용한 Ingress 컨트롤러 분할이란 Ingress 컨트롤러가 경로 선택기에서 선택한 모든 네임스페이스의 모든 경로를 제공한다는 뜻입니다.

그림 2.1. 경로 라벨을 사용한 Ingress 분할

Ingress 컨트롤러 분할은 들어오는 트래픽 부하를 일련의 Ingress 컨트롤러에 균형 있게 분배하고 트래픽을 특정 Ingress 컨트롤러에 격리할 때 유용합니다. 예를 들어, 회사 A는 하나의 Ingress 컨트롤러로, 회사 B는 다른 Ingress 컨트롤러로 이동합니다.

프로세스

`router-internal.yaml` 파일을 다음과 같이 편집합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: sharded
  namespace: openshift-ingress-operator
spec:
  domain: <apps-sharded.basedomain.example.net>
  nodePlacement:
    nodeSelector:
      matchLabels:
        node-role.kubernetes.io/worker: ""
  routeSelector:
    matchLabels:
      type: sharded
```

1. Ingress 컨트롤러에서 사용할 도메인을 지정합니다. 이 도메인은 기본 Ingress 컨트롤러 도메인과 달라야 합니다.

Ingress 컨트롤러 `router-internal.yaml` 파일을 적용합니다.

```shell-session
# oc apply -f router-internal.yaml
```

Ingress 컨트롤러는 `type: sharded` 라벨이 있는 네임스페이스에서 경로를 선택합니다.

`router-internal.yaml` 에 구성된 도메인을 사용하여 새 경로를 생성합니다.

```shell-session
$ oc expose svc <service-name> --hostname <route-name>.apps-sharded.basedomain.example.net
```

#### 2.3.6.6. 네임스페이스 라벨을 사용하여 Ingress 컨트롤러 분할 구성

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/nw-sharding-namespace-labels.png" alt="지정된 네임스페이스 선택기와 일치하는 라벨이 포함된 네임스페이스에 속하는 경로가 다른 네임스페이스 선택기가 있는 여러 Ingress 컨트롤러를 표시하는 다이어그램" kind="diagram" diagram_type="semantic_diagram"]
지정된 네임스페이스 선택기와 일치하는 라벨이 포함된 네임스페이스에 속하는 경로가 다른 네임스페이스 선택기가 있는 여러 Ingress 컨트롤러를 표시하는 다이어그램
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/afe594e8499d327fa587b8ca4f61a2cd/nw-sharding-namespace-labels.png`_


네임스페이스 라벨을 사용한 Ingress 컨트롤러 분할이란 Ingress 컨트롤러가 네임스페이스 선택기에서 선택한 모든 네임스페이스의 모든 경로를 제공한다는 뜻입니다.

그림 2.2. 네임스페이스 라벨을 사용한 Ingress 분할

Ingress 컨트롤러 분할은 들어오는 트래픽 부하를 일련의 Ingress 컨트롤러에 균형 있게 분배하고 트래픽을 특정 Ingress 컨트롤러에 격리할 때 유용합니다. 예를 들어, 회사 A는 하나의 Ingress 컨트롤러로, 회사 B는 다른 Ingress 컨트롤러로 이동합니다.

프로세스

`router-internal.yaml` 파일을 다음과 같이 편집합니다.

```shell-session
$ cat router-internal.yaml
```

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: sharded
  namespace: openshift-ingress-operator
spec:
  domain: <apps-sharded.basedomain.example.net>
  nodePlacement:
    nodeSelector:
      matchLabels:
        node-role.kubernetes.io/worker: ""
  namespaceSelector:
    matchLabels:
      type: sharded
```

1. Ingress 컨트롤러에서 사용할 도메인을 지정합니다. 이 도메인은 기본 Ingress 컨트롤러 도메인과 달라야 합니다.

Ingress 컨트롤러 `router-internal.yaml` 파일을 적용합니다.

```shell-session
$ oc apply -f router-internal.yaml
```

Ingress 컨트롤러는 네임스페이스 선택기에서 선택한 `type: sharded` 라벨이 있는 네임스페이스에서 경로를 선택합니다.

`router-internal.yaml` 에 구성된 도메인을 사용하여 새 경로를 생성합니다.

```shell-session
$ oc expose svc <service-name> --hostname <route-name>.apps-sharded.basedomain.example.net
```

#### 2.3.6.7. Ingress 컨트롤러 샤딩의 경로 생성

경로를 사용하면 URL에서 애플리케이션을 호스팅할 수 있습니다. Ingress 컨트롤러 분할은 들어오는 트래픽 부하를 일련의 Ingress 컨트롤러 간에 균형을 유지하는 데 도움이 됩니다. 특정 Ingress 컨트롤러로 트래픽을 분리할 수도 있습니다. 예를 들어, 회사 A는 하나의 Ingress 컨트롤러로, 회사 B는 다른 Ingress 컨트롤러로 이동합니다.

다음 절차에서는 `hello-openshift` 애플리케이션을 예로 사용하여 Ingress 컨트롤러 샤딩에 대한 경로를 생성하는 방법을 설명합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

프로젝트 관리자로 로그인했습니다.

포트에서 트래픽을 수신하는 포트와 HTTP 또는 TLS 끝점을 노출하는 웹 애플리케이션이 있습니다.

분할을 위해 Ingress 컨트롤러를 구성했습니다.

프로세스

다음 명령을 실행하여 `hello-openshift` 라는 프로젝트를 생성합니다.

```shell-session
$ oc new-project hello-openshift
```

다음 명령을 실행하여 프로젝트에 Pod를 생성합니다.

```shell-session
$ oc create -f https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json
```

다음 명령을 실행하여 `hello-openshift` 라는 서비스를 생성합니다.

```shell-session
$ oc expose pod/hello-openshift
```

`hello-openshift-route.yaml` 이라는 경로 정의를 생성합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    type: sharded
  name: hello-openshift-edge
  namespace: hello-openshift
spec:
  subdomain: hello-openshift
  tls:
    termination: edge
  to:
    kind: Service
    name: hello-openshift
```

1. 레이블 키와 해당 라벨 값이 모두 Ingress 컨트롤러에 지정된 라벨 값과 일치해야 합니다. 이 예에서 Ingress 컨트롤러에는 레이블 키와 값 `type: sharded` 가 있습니다.

2. 경로는 `하위 도메인` 필드의 값을 사용하여 노출됩니다. `하위 도메인` 필드를 지정하는 경우 호스트 이름을 설정되지 않은 상태로 두어야 합니다. `host` 및 `subdomain` 필드를 모두 지정하면 경로는 `host` 필드의 값을 사용하고 하위 도메인 필드를 무시합니다.

다음 명령을 실행하여 `hello-openshift-route.yaml` 을 사용하여 `hello-openshift` 애플리케이션에 대한 경로를 생성합니다.

```shell-session
$ oc -n hello-openshift create -f hello-openshift-route.yaml
```

검증

다음 명령을 사용하여 경로 상태를 가져옵니다.

```shell-session
$ oc -n hello-openshift get routes/hello-openshift-edge -o yaml
```

생성된 `Route` 리소스는 다음과 유사해야 합니다.

```yaml
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  labels:
    type: sharded
  name: hello-openshift-edge
  namespace: hello-openshift
spec:
  subdomain: hello-openshift
  tls:
    termination: edge
  to:
    kind: Service
    name: hello-openshift
status:
  ingress:
  - host: hello-openshift.<apps-sharded.basedomain.example.net>
    routerCanonicalHostname: router-sharded.<apps-sharded.basedomain.example.net>
    routerName: sharded
```

1. Ingress 컨트롤러 또는 라우터의 호스트 이름은 을 사용하여 경로를 노출합니다. `host` 필드의 값은 Ingress 컨트롤러에서 자동으로 결정하고 해당 도메인을 사용합니다. 이 예에서 Ingress 컨트롤러의 도메인은 < `apps-sharded.basedomain.example.net>입니다`.

2. Ingress 컨트롤러의 호스트 이름입니다. 호스트 이름이 설정되지 않은 경우 경로는 하위 도메인을 대신 사용할 수 있습니다. 하위 도메인을 지정하면 경로를 노출하는 Ingress 컨트롤러의 도메인을 자동으로 사용합니다. 여러 Ingress 컨트롤러에서 경로를 노출하면 경로가 여러 URL에서 호스팅됩니다.

3. Ingress 컨트롤러의 이름입니다. 이 예에서 Ingress 컨트롤러에는 `shard된` 이름이 있습니다.

#### 2.3.6.8. 추가 리소스

기본 Ingress 컨트롤러(라우터) 성능

Ingress 컨트롤러 구성

베어메탈에 클러스터 설치

vSphere에 클러스터 설치

네트워크 정책 정의

### 2.4. Ingress 컨트롤러 끝점 게시 전략 구성

`endpointPublishingStrategy` 는 Ingress 컨트롤러 끝점을 다른 네트워크에 게시하고 로드 밸런서 통합을 활성화하며 다른 시스템에 대한 액세스를 제공하는 데 사용됩니다.

중요

RHOSP(Red Hat OpenStack Platform)에서 `LoadBalancerService` 끝점 게시 전략은 클라우드 공급자가 상태 모니터를 생성하도록 구성된 경우에만 지원됩니다. RHOSP 16.2의 경우 이 전략은 Amphora Octavia 공급자를 사용하는 경우에만 가능합니다.

자세한 내용은 RHOSP 설치 설명서의 "RHOSP Cloud Controller Manager 옵션 설정" 섹션을 참조하십시오.

#### 2.4.1. Ingress 컨트롤러 끝점 게시 전략

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/202_OpenShift_Ingress_0222_node_port.png" alt="OpenShift Container Platform Ingress NodePort 끝점 게시 전략" kind="figure" diagram_type="image_figure"]
OpenShift Container Platform Ingress NodePort 끝점 게시 전략
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/5b5c971559bcbb827169ef0452f4c9b9/202_OpenShift_Ingress_0222_node_port.png`_


`NodePortService` 끝점 게시 전략

`NodePortService` 끝점 게시 전략에서는 Kubernetes NodePort 서비스를 사용하여 Ingress 컨트롤러를 게시합니다.

이 구성에서는 Ingress 컨트롤러를 배포하기 위해 컨테이너 네트워킹을 사용합니다. 배포를 게시하기 위해 `NodePortService` 가 생성됩니다.

특정 노드 포트는 OpenShift Container Platform에 의해 동적으로 할당됩니다. 그러나 정적 포트 할당을 지원하기 위해 관리형 `NodePortService` 의 노드 포트 필드에 대한 변경 사항은 유지됩니다.

그림 2.3. NodePortService 다이어그램

이전 그림에서는 OpenShift Container Platform Ingress NodePort 끝점 게시 전략과 관련된 다음 개념을 보여줍니다.

클러스터에서 사용 가능한 모든 노드에는 외부에서 액세스할 수 있는 자체 IP 주소가 있습니다. 클러스터에서 실행 중인 서비스는 모든 노드의 고유한 NodePort에 바인딩됩니다.

예를 들어 그래픽에서 `10.0.128.4` IP 주소를 연결하여 클라이언트가 다운된 노드에 연결하면 노드 포트는 클라이언트를 서비스를 실행하는 사용 가능한 노드에 직접 연결합니다. 이 시나리오에서는 로드 밸런싱이 필요하지 않습니다. 이미지가 표시된 대로 `10.0.128.4` 주소가 다운되었으며 다른 IP 주소를 대신 사용해야 합니다.

참고

Ingress Operator는 서비스의 `.spec.ports[].nodePort` 필드에 대한 업데이트를 무시합니다.

기본적으로 포트는 자동으로 할당되며 통합을 위해 포트 할당에 액세스할 수 있습니다. 그러나 동적 포트에 대한 응답으로 쉽게 재구성할 수 없는 기존 인프라와 통합하기 위해 정적 포트 할당이 필요한 경우가 있습니다. 정적 노드 포트와 통합하기 위해 관리 서비스 리소스를 직접 업데이트할 수 있습니다.

자세한 내용은 `NodePort` 에 대한 Kubernetes 서비스 설명서 를 참조하십시오.

`HostNetwork` 끝점 게시 전략

`HostNetwork` 끝점 게시 전략에서는 Ingress 컨트롤러가 배포된 노드 포트에 Ingress 컨트롤러를 게시합니다.

`HostNetwork` 끝점 게시 전략이 있는 Ingress 컨트롤러는 노드당 하나의 Pod 복제본만 가질 수 있습니다. n 개의 복제본이 필요한 경우에는 해당 복제본을 예약할 수 있는 n 개 이상의 노드를 사용해야 합니다.

각 pod 복제본은 예약된 노드 호스트에서 포트 `80` 및 `443` 을 요청하므로 동일한 노드의 다른 pod가 해당 포트를 사용하는 경우 복제본을 노드에 예약할 수 없습니다.

`HostNetwork` 오브젝트에는 `httpPort: 80`, `httpsPort: 443`, `statsPort: 1936` 이라는 선택적 바인딩 포트에 대해 다음과 같은 기본값이 있는 `hostNetwork` 필드가 있습니다.

네트워크에 다른 바인딩 포트를 지정하면 `HostNetwork` 전략에 대해 동일한 노드에 여러 Ingress 컨트롤러를 배포할 수 있습니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: internal
  namespace: openshift-ingress-operator
spec:
  domain: example.com
  endpointPublishingStrategy:
    type: HostNetwork
    hostNetwork:
      httpPort: 80
      httpsPort: 443
      statsPort: 1936
```

#### 2.4.1.1. Ingress 컨트롤러 끝점에서 내부로 게시 범위 구성

클러스터 관리자가 클러스터가 프라이빗임을 지정하지 않고 새 클러스터를 설치하면 `범위를`

`External` 로 설정하여 기본 Ingress 컨트롤러가 생성됩니다. 클러스터 관리자는 `외부` 범위가 지정된 Ingress 컨트롤러를 `Internal` 로 변경할 수 있습니다.

사전 요구 사항

다음 명령CLI를 설치했습니다.

```shell
oc
```

프로세스

`외부` 범위가 지정된 Ingress 컨트롤러를 `Internal` 로 변경하려면 다음 명령을 입력합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontrollers/default --type=merge --patch='{"spec":{"endpointPublishingStrategy":{"type":"LoadBalancerService","loadBalancer":{"scope":"Internal"}}}}'
```

Ingress 컨트롤러의 상태를 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc -n openshift-ingress-operator get ingresscontrollers/default -o yaml
```

`Progressing` 상태 조건은 추가 작업을 수행해야 하는지 여부를 나타냅니다. 예를 들어 상태 조건은 다음 명령을 입력하여 서비스를 삭제해야 함을 나타낼 수 있습니다.

```shell-session
$ oc -n openshift-ingress delete services/router-default
```

서비스를 삭제하면 Ingress Operator에서 해당 서비스를 `Internal` 로 다시 생성합니다.

#### 2.4.1.2. 외부로 범위를 게시하는 Ingress 컨트롤러 끝점 구성

클러스터 관리자가 클러스터가 프라이빗임을 지정하지 않고 새 클러스터를 설치하면 `범위를`

`External` 로 설정하여 기본 Ingress 컨트롤러가 생성됩니다.

Ingress 컨트롤러의 범위는 설치 중 또는 이후에 내부로 구성할 수 있으며 클러스터 관리자는 `내부` Ingress 컨트롤러를 외부로 변경할 수 `있습니다`.

중요

일부 플랫폼에서는 서비스를 삭제하고 다시 생성해야 합니다.

범위를 변경하면 Ingress 트래픽으로 인해 몇 분 동안 중단될 수 있습니다. 이 절차는 OpenShift Container Platform에서 기존 서비스 로드 밸런서를 프로비저닝 해제하고 새 서비스 로드 밸런서를 프로비저닝하고 DNS를 업데이트할 수 있으므로 서비스를 삭제하고 다시 생성해야 하는 플랫폼에 적용됩니다.

사전 요구 사항

다음 명령CLI를 설치했습니다.

```shell
oc
```

프로세스

`내부` 범위가 지정된 Ingress 컨트롤러를 `외부로` 변경하려면 다음 명령을 입력합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontrollers/private --type=merge --patch='{"spec":{"endpointPublishingStrategy":{"type":"LoadBalancerService","loadBalancer":{"scope":"External"}}}}'
```

Ingress 컨트롤러의 상태를 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc -n openshift-ingress-operator get ingresscontrollers/default -o yaml
```

`Progressing` 상태 조건은 추가 작업을 수행해야 하는지 여부를 나타냅니다. 예를 들어 상태 조건은 다음 명령을 입력하여 서비스를 삭제해야 함을 나타낼 수 있습니다.

```shell-session
$ oc -n openshift-ingress delete services/router-default
```

서비스를 삭제하면 Ingress Operator에서 `외부` 로 다시 생성합니다.

#### 2.4.1.3. Ingress 컨트롤러에 단일 NodePort 서비스 추가

각 프로젝트에 `NodePort` -type `Service` 를 생성하는 대신 사용자 정의 Ingress 컨트롤러를 생성하여 `NodePortService` 끝점 게시 전략을 사용할 수 있습니다.

포트 충돌을 방지하려면 Ingress 샤딩을 통해 `HostNetwork` Ingress 컨트롤러가 있을 수 있는 노드에 경로 세트를 적용하려면 Ingress 컨트롤러에 대해 이 구성을 고려하십시오.

각 프로젝트에 `NodePort` -type `서비스를` 설정하기 전에 다음 고려 사항을 읽으십시오.

Nodeport Ingress 컨트롤러 도메인에 대한 와일드카드 DNS 레코드를 생성해야 합니다. Nodeport Ingress 컨트롤러 경로는 작업자 노드의 주소에서 연결할 수 있습니다. 경로에 필요한 DNS 레코드에 대한 자세한 내용은 "사용자 프로비저닝 DNS 요구 사항"을 참조하십시오.

서비스의 경로를 노출하고 사용자 정의 Ingress 컨트롤러 도메인의 `--hostname` 인수를 지정해야 합니다.

애플리케이션 Pod에 액세스할 수 있도록 경로의 `NodePort` -type `서비스에` 할당된 포트를 추가해야 합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

와일드카드 DNS 레코드를 생성했습니다.

프로세스

Ingress 컨트롤러에 대한 CR(사용자 정의 리소스) 파일을 생성합니다.

```yaml
apiVersion: v1
items:
- apiVersion: operator.openshift.io/v1
  kind: IngressController
  metadata:
    name: <custom_ic_name>
    namespace: openshift-ingress-operator
  spec:
    replicas: 1
    domain: <custom_ic_domain_name>
    nodePlacement:
      nodeSelector:
        matchLabels:
          <key>: <value>
    namespaceSelector:
     matchLabels:
       <key>: <value>
    endpointPublishingStrategy:
      type: NodePortService
# ...
```

1. `IngressController` CR의 사용자 정의 `이름을` 지정합니다.

2. Ingress 컨트롤러 서비스의 DNS 이름입니다. 예를 들어 기본 ingresscontroller 도메인은 `apps.ipi-cluster.example.com` 이므로 < `custom_ic_domain_name` >을 `nodeportsvc.ipi-cluster.example.com` 으로 지정합니다.

3. 사용자 정의 Ingress 컨트롤러를 포함하는 노드의 라벨을 지정합니다.

4. 네임스페이스 집합의 라벨을 지정합니다. < `key>:<value` >를 <key>가 새 레이블의 고유 이름이며 < `value` >가 값인 `키` -값 쌍의 맵으로 바꿉니다. 예: `ingresscontroller: custom-ic`.

아래 명령을 사용하여 노드에 라벨을 추가합니다.

```shell
oc label node
```

```shell-session
$ oc label node <node_name> <key>=<value>
```

1. 여기서 `<value` >는 `IngressController` CR의 `nodePlacement` 섹션에 지정된 키-값 쌍과 일치해야 합니다.

`IngressController` 오브젝트를 생성합니다.

```shell-session
$ oc create -f <ingress_controller_cr>.yaml
```

`IngressController` CR에 대해 생성된 서비스의 포트를 찾습니다.

```shell-session
$ oc get svc -n openshift-ingress
```

```shell-session
NAME                        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)                                     AGE
router-internal-default      ClusterIP   172.30.195.74    <none>        80/TCP,443/TCP,1936/TCP                     223d
router-nodeport-custom-ic3   NodePort    172.30.109.219   <none>        80:32432/TCP,443:31366/TCP,1936:30499/TCP   155m
```

새 프로젝트를 생성하려면 다음 명령을 입력합니다.

```shell-session
$ oc new-project <project_name>
```

새 네임스페이스에 레이블을 지정하려면 다음 명령을 입력합니다.

```shell-session
$ oc label namespace <project_name> <key>=<value>
```

1. 여기서 & `lt;key>=&` lt;value>는 Ingress 컨트롤러 CR의 `namespaceSelector` 섹션에 있는 값과 일치해야 합니다.

클러스터에 새 애플리케이션을 생성합니다.

```shell-session
$ oc new-app --image=<image_name>
```

1. < `image_name` >의 예는 `quay.io/openshifttest/hello-openshift:multiarch` 입니다.

Pod에서 서비스를 사용하여 클러스터 외부에 애플리케이션을 노출할 수 있도록 서비스의 `Route` 오브젝트를 생성합니다.

```shell-session
$ oc expose svc/<service_name> --hostname=<svc_name>-<project_name>.<custom_ic_domain_name>
```

참고

`--hostname` 인수에서 사용자 정의 Ingress 컨트롤러의 도메인 이름을 지정해야 합니다. 이 작업을 수행하지 않으면 Ingress Operator는 기본 Ingress 컨트롤러를 사용하여 클러스터의 모든 경로를 제공합니다.

경로에 `Admitted` 상태가 있고 사용자 정의 Ingress 컨트롤러에 대한 메타데이터가 포함되어 있는지 확인합니다.

```shell-session
$ oc get route/hello-openshift -o json | jq '.status.ingress'
```

```shell-session
# ...
{
  "conditions": [
    {
      "lastTransitionTime": "2024-05-17T18:25:41Z",
      "status": "True",
      "type": "Admitted"
    }
  ],
  [
    {
      "host": "hello-openshift.nodeportsvc.ipi-cluster.example.com",
      "routerCanonicalHostname": "router-nodeportsvc.nodeportsvc.ipi-cluster.example.com",
      "routerName": "nodeportsvc", "wildcardPolicy": "None"
    }
  ],
}
```

기본 Ingress 컨트롤러에서 `NodePort` -type `서비스를` 관리하지 못하도록 기본 `IngressController` CR을 업데이트합니다. 기본 Ingress 컨트롤러는 다른 모든 클러스터 트래픽을 계속 모니터링합니다.

```shell-session
$ oc patch --type=merge -n openshift-ingress-operator ingresscontroller/default --patch '{"spec":{"namespaceSelector":{"matchExpressions":[{"key":"<key>","operator":"NotIn","values":["<value>]}]}}}'
```

검증

다음 명령을 입력하여 DNS 항목이 클러스터 내부 및 외부에서 라우팅될 수 있는지 확인합니다. 이 명령은 절차의 앞부분에서 아래 명령을 실행하여 레이블을 수신한 노드의 IP 주소를 출력합니다.

```shell
oc label node
```

```shell-session
$ dig +short <svc_name>-<project_name>.<custom_ic_domain_name>
```

클러스터가 DNS 확인을 위해 외부 DNS 서버의 IP 주소를 사용하는지 확인하려면 다음 명령을 입력하여 클러스터 연결을 확인합니다.

```shell-session
$ curl <svc_name>-<project_name>.<custom_ic_domain_name>:<port>
```

1. 1

여기서 `<port` >는 `NodePort` -type `서비스` 의 노드 포트입니다. 아래 명령의 예제 출력에 따라 `80:32432/TCP` HTTP 경로는 `32432` 가 노드 포트임을 의미합니다.

```shell
oc get svc -n openshift-ingress
```

```shell-session
Hello OpenShift!
```

#### 2.4.2. 추가 리소스

Ingress 컨트롤러 구성 매개변수

RHOSP Cloud Controller Manager 옵션 설정

사용자 프로비저닝 DNS 요구사항

### 2.5. 로드 밸런서를 사용하여 수신 클러스터 트래픽 구성

OpenShift Container Platform에서는 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있습니다. 이 방법에서는 로드 밸런서를 사용합니다.

#### 2.5.1. 로드 밸런서를 사용하여 클러스터로 트래픽 가져오기

특정 외부 IP 주소가 필요하지 않은 경우 OpenShift Container Platform 클러스터에 대한 외부 액세스를 허용하도록 로드 밸런서 서비스를 구성할 수 있습니다.

로드 밸런서 서비스에서는 고유 IP를 할당합니다. 로드 밸런서에는 VIP(가상 IP)일 수 있는 단일 엣지 라우터 IP가 있지만 이는 초기 로드 밸런싱을 위한 단일 머신에 불과합니다.

참고

풀이 구성된 경우 클러스터 관리자가 아닌 인프라 수준에서 수행됩니다.

참고

이 섹션의 절차에는 클러스터 관리자가 수행해야 하는 사전 요구 사항이 필요합니다.

#### 2.5.2. 사전 요구 사항

다음 절차를 시작하기 전에 관리자는 다음을 수행해야 합니다.

요청이 클러스터에 도달할 수 있도록 외부 포트를 클러스터 네트워킹 환경으로 설정합니다.

클러스터 관리자 역할의 사용자가 한 명 이상 있는지 확인합니다. 이 역할을 사용자에게 추가하려면 다음 명령을 실행합니다.

```plaintext
$ oc adm policy add-cluster-role-to-user cluster-admin username
```

클러스터에 대한 네트워크 액세스 권한이 있는 마스터와 노드가 클러스터 외부에 각각 1개 이상씩 있는 OpenShift Container Platform 클러스터가 있어야 합니다. 이 절차에서는 외부 시스템이 클러스터와 동일한 서브넷에 있다고 가정합니다. 다른 서브넷에 있는 외부 시스템에 필요한 추가 네트워킹은 이 주제에서 다루지 않습니다.

#### 2.5.3. 프로젝트 및 서비스 생성

노출하려는 프로젝트 및 서비스가 존재하지 않는 경우 프로젝트를 생성한 다음 서비스를 생성합니다.

프로젝트 및 서비스가 이미 존재하는 경우 서비스 노출 절차로 건너뛰어 경로를 생성합니다.

사전 요구 사항

OpenShift CLI()를 설치하고 클러스터 관리자로 로그인합니다.

```shell
oc
```

프로세스

아래 명령을 실행하여 서비스에 대한 새 프로젝트를 생성합니다.

```shell
oc new-project
```

```shell-session
$ oc new-project <project_name>
```

아래 명령을 사용하여 서비스를 생성합니다.

```shell
oc new-app
```

```shell-session
$ oc new-app nodejs:12~https://github.com/sclorg/nodejs-ex.git
```

서비스가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get svc -n <project_name>
```

```shell-session
NAME        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
nodejs-ex   ClusterIP   172.30.197.157   <none>        8080/TCP   70s
```

참고

기본적으로 새 서비스에는 외부 IP 주소가 없습니다.

#### 2.5.4. 경로를 생성하여 서비스 노출

아래 명령을 사용하여 서비스를 경로로 노출할 수 있습니다.

```shell
oc expose
```

사전 요구 사항

OpenShift Container Platform에 로그인되어 있습니다.

프로세스

노출하려는 서비스가 있는 프로젝트에 로그인합니다.

```shell-session
$ oc project <project_name>
```

아래 명령을 실행하여 경로를 노출합니다.

```shell
oc expose service
```

```shell-session
$ oc expose service nodejs-ex
```

```shell-session
route.route.openshift.io/nodejs-ex exposed
```

서비스가 노출되었는지 확인하려면 다음 명령과 같은 툴을 사용하여 클러스터 외부에서 서비스에 액세스할 수 있는지 확인할 수 있습니다.

```shell
curl
```

경로의 호스트 이름을 찾으려면 다음 명령을 입력합니다.

```shell-session
$ oc get route
```

```shell-session
NAME        HOST/PORT                        PATH   SERVICES    PORT       TERMINATION   WILDCARD
nodejs-ex   nodejs-ex-myproject.example.com         nodejs-ex   8080-tcp                 None
```

호스트가 GET 요청에 응답하는지 확인하려면 다음 명령을 입력합니다.

```shell
curl
```

```shell-session
$ curl --head nodejs-ex-myproject.example.com
```

```shell-session
HTTP/1.1 200 OK
...
```

#### 2.5.5. 로드 밸런서 서비스 생성

다음 절차에 따라 로드 밸런서 서비스를 생성합니다.

사전 요구 사항

노출하려는 프로젝트와 서비스가 존재하는지 확인합니다.

클라우드 공급자는 로드 밸런서를 지원합니다.

프로세스

로드 밸런서 서비스를 생성하려면 다음을 수행합니다.

OpenShift Container Platform 4에 로그인합니다.

노출하려는 서비스가 있는 프로젝트를 로드합니다.

```shell-session
$ oc project project1
```

필요에 따라 컨트롤 플레인 노드에서 텍스트 파일을 열고 다음 텍스트를 붙여넣고 파일을 편집합니다.

```plaintext
apiVersion: v1
kind: Service
metadata:
  name: egress-2
spec:
  ports:
  - name: db
    port: 3306
  loadBalancerIP:
  loadBalancerSourceRanges:
  - 10.0.0.0/8
  - 192.168.0.0/16
  type: LoadBalancer
  selector:
    name: mysql
```

1. 로드 밸런서 서비스를 설명하는 이름을 입력합니다.

2. 노출하려는 서비스가 수신 대기 중인 포트와 동일한 포트를 입력합니다.

3. 로드 밸런서를 통한 트래픽을 제한하려면 특정 IP 주소 목록을 입력합니다. cloud-provider가 이 기능을 지원하지 않는 경우 이 필드는 무시됩니다.

4. 유형으로 `Loadbalancer` 를 입력합니다.

5. 서비스 이름을 입력합니다.

참고

로드 밸런서를 통한 트래픽을 특정 IP 주소로 제한하려면 Ingress 컨트롤러 필드 `spec.endpointPublishingStrategy.loadBalancer.allowedSourceRanges` 를 사용하는 것이 좋습니다. `loadBalancerSourceRanges` 필드를 설정하지 마십시오.

파일을 저장하고 종료합니다.

다음 명령을 실행하여 서비스를 생성합니다.

```shell-session
$ oc create -f <file-name>
```

예를 들면 다음과 같습니다.

```shell-session
$ oc create -f mysql-lb.yaml
```

새 서비스를 보려면 다음 명령을 실행합니다.

```shell-session
$ oc get svc
```

```shell-session
NAME       TYPE           CLUSTER-IP      EXTERNAL-IP                             PORT(S)          AGE
egress-2   LoadBalancer   172.30.22.226   ad42f5d8b303045-487804948.example.com   3306:30357/TCP   15m
```

활성화된 클라우드 공급자가 있는 경우 서비스에 외부 IP 주소가 자동으로 할당됩니다.

마스터에서 cURL과 같은 도구를 사용하여 공개 IP 주소로 서비스에 도달할 수 있는지 확인합니다.

```shell-session
$ curl <public-ip>:<port>
```

예를 들면 다음과 같습니다.

```shell-session
$ curl 172.29.121.74:3306
```

이 섹션의 예제에서는 클라이언트 애플리케이션이 필요한 MySQL 서비스를 사용합니다. `패킷이 잘못됨` 이라는 메시지가 포함된 문자열이 표시되면 서비스에 연결된 것입니다.

MySQL 클라이언트가 있는 경우 표준 CLI 명령으로 로그인하십시오.

```shell-session
$ mysql -h 172.30.131.89 -u admin -p
```

```shell-session
Enter password:
Welcome to the MariaDB monitor.  Commands end with ; or \g.

MySQL [(none)]>
```

### 2.6. AWS에서 수신 클러스터 트래픽 구성

OpenShift Container Platform에서는 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있습니다. 이 방법은 AWS, 특히 NLB(Network Load Balancer) 또는 Classic Load Balancer(CLB)의 로드 밸런서를 사용합니다.

두 유형의 로드 밸런서 모두 클라이언트의 IP 주소를 노드로 전달할 수 있지만 CLB에는 OpenShift Container Platform에서 자동으로 활성화하는 프록시 프로토콜 지원이 필요합니다.

NLB를 사용하도록 Ingress 컨트롤러를 구성하는 방법은 다음 두 가지가 있습니다.

현재 CLB를 사용하고 있는 Ingress 컨트롤러를 강제로 교체합니다. 이렇게 하면 `IngressController` 오브젝트가 삭제되고 새 DNS 레코드가 전파되고 NLB가 프로비저닝되는 동안 중단이 발생합니다.

NLB를 사용하도록 CLB를 사용하는 기존 Ingress 컨트롤러를 편집합니다. 이렇게 하면 `IngressController` 오브젝트를 삭제하고 다시 생성할 필요 없이 로드 밸런서가 변경됩니다.

두 방법 모두 NLB에서 CLB로 전환하는 데 사용할 수 있습니다.

새 AWS 또는 기존 AWS 클러스터에서 이러한 로드 밸런서를 구성할 수 있습니다.

#### 2.6.1. AWS에서 Classic Load Balancer 시간 초과 구성

OpenShift Container Platform에서는 특정 경로 또는 Ingress 컨트롤러에 대한 사용자 정의 시간 초과 기간을 설정하는 방법을 제공합니다. 또한 AWS Classic Load Balancer(CLB)에는 기본 60초의 시간 초과 기간이 있습니다.

CLB의 시간 초과 기간이 경로 시간 초과 또는 Ingress 컨트롤러 시간 초과보다 짧은 경우 로드 밸런서에서 연결을 조기에 종료할 수 있습니다. 경로와 CLB의 시간 초과 기간을 모두 늘려 이 문제를 방지할 수 있습니다.

#### 2.6.1.1. 경로 시간 초과 구성

SLA(Service Level Availability) 목적에 필요한 낮은 시간 초과 또는 백엔드가 느린 경우 높은 시간 초과가 필요한 서비스가 있는 경우 기존 경로에 대한 기본 시간 초과를 구성할 수 있습니다.

중요

OpenShift Container Platform 클러스터 앞에 사용자 관리 외부 로드 밸런서를 구성한 경우 사용자 관리 외부 로드 밸런서의 시간 초과 값이 경로의 시간 초과 값보다 높습니다. 이 구성으로 인해 클러스터가 사용하는 네트워크를 통한 네트워크 정체 문제가 발생하지 않습니다.

사전 요구 사항

실행 중인 클러스터에 배포된 Ingress 컨트롤러가 필요합니다.

프로세스

아래 명령을 사용하여 경로에 시간 초과를 추가합니다.

```shell
oc annotate
```

```shell-session
$ oc annotate route <route_name> \
    --overwrite haproxy.router.openshift.io/timeout=<timeout><time_unit>
```

1. 지원되는 시간 단위는 마이크로초(us), 밀리초(ms), 초(s), 분(m), 시간(h) 또는 일(d)입니다.

다음 예제는 이름이 `myroute` 인 경로에서 2초의 시간 초과를 설정합니다.

```shell-session
$ oc annotate route myroute --overwrite haproxy.router.openshift.io/timeout=2s
```

#### 2.6.1.2. Classic Load Balancer 시간 제한 구성

Classic Load Balancer(CLB)의 기본 시간 초과를 구성하여 유휴 연결을 확장할 수 있습니다.

사전 요구 사항

실행 중인 클러스터에 배포된 Ingress 컨트롤러가 있어야 합니다.

프로세스

다음 명령을 실행하여 기본 `ingresscontroller` 에 대해 AWS 연결 유휴 시간 제한 시간을 5분으로 설정합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontroller/default \
    --type=merge --patch='{"spec":{"endpointPublishingStrategy": \
    {"type":"LoadBalancerService", "loadBalancer": \
    {"scope":"External", "providerParameters":{"type":"AWS", "aws": \
    {"type":"Classic", "classicLoadBalancer": \
    {"connectionIdleTimeout":"5m"}}}}}}}'
```

선택 사항: 다음 명령을 실행하여 시간 초과의 기본값을 복원합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontroller/default \
    --type=merge --patch='{"spec":{"endpointPublishingStrategy": \
    {"loadBalancer":{"providerParameters":{"aws":{"classicLoadBalancer": \
    {"connectionIdleTimeout":null}}}}}}}'
```

참고

현재 범위가 이미 설정되어 있지 않으면 연결 시간 초과 값을 변경할 때 `scope` 필드를 지정해야 합니다. `범위` 필드를 설정할 때 기본 시간 초과 값을 복원하는 경우 다시 수행할 필요가 없습니다.

#### 2.6.2. 네트워크 로드 밸런서를 사용하여 AWS에서 수신 클러스터 트래픽 구성

OpenShift Container Platform은 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있는 방법을 제공합니다. 이러한 방법 중 하나는 NLB(Network Load Balancer)를 사용합니다. 신규 또는 기존 AWS 클러스터에서 NLB를 구성할 수 있습니다.

#### 2.6.2.1. Classic Load Balancer를 사용하여 Ingress 컨트롤러를 Network Load Balancer로 전환

Classic Load Balancer(CLB)를 사용하는 Ingress 컨트롤러를 AWS에서 NLB(Network Load Balancer)를 사용하는 컨트롤러로 전환할 수 있습니다.

이러한 로드 밸런서 간에 전환해도 `IngressController` 오브젝트가 삭제되지 않습니다.

주의

이 절차에서는 다음과 같은 문제가 발생할 수 있습니다.

새로운 DNS 레코드 전파, 새 로드 밸런서 프로비저닝 및 기타 요인으로 인해 몇 분 정도 지속될 수 있습니다. 이 절차를 적용한 후 Ingress 컨트롤러 로드 밸런서의 IP 주소 및 표준 이름이 변경될 수 있습니다.

서비스 주석의 변경으로 인해 로드 밸런서 리소스가 유출되었습니다.

프로세스

NLB를 사용하여 전환하려는 기존 Ingress 컨트롤러를 수정합니다. 이 예에서는 기본 Ingress 컨트롤러에 `외부` 범위가 있고 다른 사용자 정의가 없는 것으로 가정합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: null
  name: default
  namespace: openshift-ingress-operator
spec:
  endpointPublishingStrategy:
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: NLB
    type: LoadBalancerService
```

참고

`spec.endpointPublishingStrategy.loadBalancer.providerParameters.aws.type` 필드의 값을 지정하지 않으면 Ingress 컨트롤러는 설치 중에 설정된 클러스터 `Ingress` 구성에서 `spec.loadBalancer.platform.aws.type` 값을 사용합니다.

작은 정보

Ingress 컨트롤러에 도메인 변경과 같이 업데이트할 다른 사용자 지정이 있는 경우 대신 Ingress 컨트롤러 정의 파일을 강제로 교체하는 것이 좋습니다.

명령을 실행하여 Ingress 컨트롤러 YAML 파일에 변경 사항을 적용합니다.

```shell-session
$ oc apply -f ingresscontroller.yaml
```

Ingress 컨트롤러가 업데이트되는 동안 몇 분의 중단이 발생할 수 있습니다.

#### 2.6.2.2. 네트워크 로드 밸런서를 사용하여 Ingress 컨트롤러에서 Classic Load Balancer로 전환

NLB(Network Load Balancer)를 사용하는 Ingress 컨트롤러를 AWS에서CLB(Classic Load Balancer)를 사용하는 컨트롤러로 전환할 수 있습니다.

이러한 로드 밸런서 간에 전환해도 `IngressController` 오브젝트가 삭제되지 않습니다.

주의

이 절차에서는 새 DNS 레코드 전파, 새 로드 밸런서 프로비저닝 및 기타 요인으로 인해 몇 분 정도 지속될 수 있습니다. 이 절차를 적용한 후 Ingress 컨트롤러 로드 밸런서의 IP 주소 및 표준 이름이 변경될 수 있습니다.

프로세스

CLB를 사용하여 전환하려는 기존 Ingress 컨트롤러를 수정합니다. 이 예에서는 기본 Ingress 컨트롤러에 `외부` 범위가 있고 다른 사용자 정의가 없는 것으로 가정합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: null
  name: default
  namespace: openshift-ingress-operator
spec:
  endpointPublishingStrategy:
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: Classic
    type: LoadBalancerService
```

참고

`spec.endpointPublishingStrategy.loadBalancer.providerParameters.aws.type` 필드의 값을 지정하지 않으면 Ingress 컨트롤러는 설치 중에 설정된 클러스터 `Ingress` 구성에서 `spec.loadBalancer.platform.aws.type` 값을 사용합니다.

작은 정보

Ingress 컨트롤러에 도메인 변경과 같이 업데이트할 다른 사용자 지정이 있는 경우 대신 Ingress 컨트롤러 정의 파일을 강제로 교체하는 것이 좋습니다.

명령을 실행하여 Ingress 컨트롤러 YAML 파일에 변경 사항을 적용합니다.

```shell-session
$ oc apply -f ingresscontroller.yaml
```

Ingress 컨트롤러가 업데이트되는 동안 몇 분의 중단이 발생할 수 있습니다.

#### 2.6.2.3. Ingress Controller Classic Load Balancer를 Network Load Balancer로 교체

Classic Load Balancer(CLB)를 사용하는 Ingress 컨트롤러를 AWS에서 NLB(Network Load Balancer)를 사용하는 컨트롤러로 교체할 수 있습니다.

주의

이 절차에서는 다음과 같은 문제가 발생할 수 있습니다.

새로운 DNS 레코드 전파, 새 로드 밸런서 프로비저닝 및 기타 요인으로 인해 몇 분 정도 지속될 수 있습니다. 이 절차를 적용한 후 Ingress 컨트롤러 로드 밸런서의 IP 주소 및 표준 이름이 변경될 수 있습니다.

서비스 주석의 변경으로 인해 로드 밸런서 리소스가 유출되었습니다.

프로세스

새 기본 Ingress 컨트롤러를 사용하여 파일을 생성합니다. 다음 예제에서는 기본 Ingress 컨트롤러에 `외부` 범위가 있고 다른 사용자 정의가 없는 것으로 가정합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: null
  name: default
  namespace: openshift-ingress-operator
spec:
  endpointPublishingStrategy:
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: NLB
    type: LoadBalancerService
```

기본 Ingress 컨트롤러에 다른 사용자 지정이 있는 경우 파일을 적절하게 수정해야 합니다.

작은 정보

Ingress 컨트롤러에 다른 사용자 정의가 없으며 로드 밸런서 유형만 업데이트하는 경우 " Classic Load Balancer를 사용하여 Ingress 컨트롤러 전환"에 설명된 절차를 따르십시오.

Ingress 컨트롤러 YAML 파일을 강제로 교체합니다.

```shell-session
$ oc replace --force --wait -f ingresscontroller.yml
```

Ingress 컨트롤러가 교체될 때까지 기다립니다. 몇 분 동안 중단이 발생할 것으로 예상됩니다.

#### 2.6.2.4. 기존 AWS 클러스터에서 Ingress 컨트롤러 네트워크 로드 밸런서 생성

기존 클러스터에서 AWS NLB(Network Load Balancer)가 지원하는 Ingress 컨트롤러를 생성할 수 있습니다.

사전 요구 사항

AWS 클러스터가 설치되어 있어야 합니다.

인프라 리소스의 `PlatformStatus` 는 AWS여야 합니다.

`PlatformStatus` 가 AWS인지 확인하려면 다음을 실행하십시오.

```shell-session
$ oc get infrastructure/cluster -o jsonpath='{.status.platformStatus.type}'
AWS
```

프로세스

기존 클러스터에서 AWS NLB가 지원하는 Ingress 컨트롤러를 생성합니다.

Ingress 컨트롤러 매니페스트를 생성합니다.

```shell-session
$ cat ingresscontroller-aws-nlb.yaml
```

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: $my_ingress_controller
  namespace: openshift-ingress-operator
spec:
  domain: $my_unique_ingress_domain
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: NLB
```

1. `$my_ingress_controller` 를 Ingress 컨트롤러에 대해 고유한 이름으로 교체합니다.

2. `$my_unique_ingress_domain` 을 클러스터의 모든 Ingress 컨트롤러 간에 고유한 도메인 이름으로 교체합니다. 이 변수는 DNS 이름 <.

```shell
clustername>.<domain>의 하위 도메인이어야 합니다
```

3. 내부 NLB를 사용하려면 `External` 을 `Internal` 로 교체할 수 있습니다.

클러스터에서 리소스를 생성합니다.

```shell-session
$ oc create -f ingresscontroller-aws-nlb.yaml
```

중요

새 AWS 클러스터에서 Ingress 컨트롤러 NLB를 구성하려면 먼저 설치 구성 파일 생성 절차를 완료해야 합니다.

#### 2.6.2.5. 새 AWS 클러스터에서 Ingress 컨트롤러 네트워크 로드 밸런서 생성

새 클러스터에서 AWS NLB(Network Load Balancer)가 지원하는 Ingress 컨트롤러를 생성할 수 있습니다.

사전 요구 사항

`install-config.yaml` 파일을 생성하고 수정합니다.

프로세스

새 클러스터에서 AWS NLB가 지원하는 Ingress 컨트롤러를 생성합니다.

설치 프로그램이 포함된 디렉터리로 변경하고 매니페스트를 생성합니다.

```shell-session
$ ./openshift-install create manifests --dir <installation_directory>
```

1. `<installation_directory>` 는 클러스터의 `install-config.yaml` 파일이 포함된 디렉터리의 이름을 지정합니다.

`<installation_directory>/manifests/` 디렉터리에 `cluster-ingress-default-ingresscontroller.yaml` 이라는 이름으로 파일을 만듭니다.

```shell-session
$ touch <installation_directory>/manifests/cluster-ingress-default-ingresscontroller.yaml
```

1. `<installation_directory>` 는 클러스터의 `manifests /` 디렉터리가 포함된 디렉터리 이름을 지정합니다.

파일이 생성되면 다음과 같이 여러 네트워크 구성 파일이 `manifests/` 디렉토리에 나타납니다.

```shell-session
$ ls <installation_directory>/manifests/cluster-ingress-default-ingresscontroller.yaml
```

```shell-session
cluster-ingress-default-ingresscontroller.yaml
```

편집기에서 `cluster-ingress-default-ingresscontroller.yaml` 파일을 열고 원하는 운영자 구성을 설명하는 CR(사용자 정의 리소스)을 입력합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  creationTimestamp: null
  name: default
  namespace: openshift-ingress-operator
spec:
  endpointPublishingStrategy:
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: NLB
    type: LoadBalancerService
```

`cluster-ingress-default-ingresscontroller.yaml` 파일을 저장하고 텍스트 편집기를 종료합니다.

선택 사항: `manifests / cluster-ingress-default-ingresscontroller.yaml` 파일을 백업합니다. 설치 프로그램은 클러스터를 생성할 때 `manifests/` 디렉터리를 삭제합니다.

#### 2.6.2.6. LoadBalancerService Ingress 컨트롤러를 생성하는 동안 서브넷 선택

기존 클러스터의 Ingress 컨트롤러에 대한 로드 밸런서 서브넷을 수동으로 지정할 수 있습니다. 기본적으로 로드 밸런서 서브넷은 AWS에서 자동으로 검색하지만 Ingress 컨트롤러에 지정하면 수동으로 제어할 수 있습니다.

사전 요구 사항

AWS 클러스터가 설치되어 있어야 합니다.

`IngressController` 를 매핑하려는 서브넷의 이름 또는 ID를 알아야 합니다.

프로세스

CR(사용자 정의 리소스) 파일을 생성합니다.

다음 콘텐츠를 사용하여 YAML 파일(예: `sample-ingress.yaml`)을 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  namespace: openshift-ingress-operator
  name: <name>
spec:
  domain: <domain>
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
  dnsManagementPolicy: Managed
```

CR(사용자 정의 리소스) 파일을 생성합니다.

YAML 파일에 서브넷을 추가합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name:  <name>
  namespace: openshift-ingress-operator
spec:
  domain: <domain>
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: Classic
          classicLoadBalancer:
            subnets:
              ids:
              - <subnet>
              - <subnet>
              - <subnet>
dnsManagementPolicy: Managed
```

1. & `lt;name&` gt;을 `IngressController` 의 이름으로 바꿉니다.

2. & `lt;domain&` gt;을 `IngressController` 에서 제공하는 DNS 이름으로 바꿉니다.

3. NLB를 사용하는 경우 `networkLoadBalancer` 필드를 사용할 수도 있습니다.

4. 선택적으로 서브넷을 ID로 지정하는 대신 `names` 필드를 사용하여 이름으로 서브넷을 지정할 수 있습니다.

5. 서브넷 ID를 지정합니다(이름을 사용하는 경우 `이름`).

중요

가용성 영역당 최대 하나의 서브넷을 지정할 수 있습니다. 외부 Ingress 컨트롤러의 퍼블릭 서브넷 및 내부 Ingress 컨트롤러의 프라이빗 서브넷만 제공합니다.

CR 파일을 적용합니다.

파일을 저장하고 OpenShift CLI()를 사용하여 적용합니다.

```shell
oc
```

```shell-session
$  oc apply -f sample-ingress.yaml
```

`IngressController` 조건을 확인하여 로드 밸런서가 성공적으로 프로비저닝되었는지 확인합니다.

```shell-session
$ oc get ingresscontroller -n openshift-ingress-operator <name> -o jsonpath="{.status.conditions}" | yq -PC
```

#### 2.6.2.7. 기존 Ingress 컨트롤러에서 서브넷 업데이트

OpenShift Container Platform에서 수동으로 지정된 로드 밸런서 서브넷으로 `IngressController` 를 업데이트하여 중단을 방지하고 서비스 안정성을 유지하고 네트워크 구성이 특정 요구 사항에 맞게 조정되도록 할 수 있습니다.

다음 절차에서는 새 서브넷을 선택 및 적용하고, 구성 변경 사항을 확인하고, 로드 밸런서를 성공적으로 프로비저닝하는 방법을 보여줍니다.

주의

이 절차에서는 새 DNS 레코드 전파, 새 로드 밸런서 프로비저닝 및 기타 요인으로 인해 몇 분 정도 지속될 수 있습니다. 이 절차를 적용한 후 Ingress 컨트롤러 로드 밸런서의 IP 주소 및 표준 이름이 변경될 수 있습니다.

프로세스

수동으로 지정된 로드 밸런서 서브넷으로 `IngressController` 를 업데이트하려면 다음 단계를 따르십시오.

기존 IngressController를 수정하여 새 서브넷으로 업데이트합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name:  <name>
  namespace: openshift-ingress-operator
spec:
  domain: <domain>
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
      providerParameters:
        type: AWS
        aws:
          type: Classic
          classicLoadBalancer:
            subnets:
              ids:
              - <updated_subnet>
              - <updated_subnet>
              - <updated_subnet>
```

1. & `lt;name&` gt;을 `IngressController` 의 이름으로 바꿉니다.

2. & `lt;domain&` gt;을 `IngressController` 에서 제공하는 DNS 이름으로 바꿉니다.

3. 업데이트된 서브넷 ID를 지정합니다(이름을 사용하는 경우 `이름`).

4. NLB를 사용하는 경우 `networkLoadBalancer` 필드를 사용할 수도 있습니다.

5. 선택적으로 서브넷을 ID로 지정하는 대신 `names` 필드를 사용하여 이름으로 서브넷을 지정할 수 있습니다.

6. 서브넷 ID를 업데이트합니다(또는 이름을 사용하는 경우 `이름`).

중요

가용성 영역당 최대 하나의 서브넷을 지정할 수 있습니다. 외부 Ingress 컨트롤러의 퍼블릭 서브넷 및 내부 Ingress 컨트롤러의 프라이빗 서브넷만 제공합니다.

다음 명령을 실행하여 서브넷 업데이트를 적용하는 방법에 대한 지침은 `IngressController` 에서 `Progressing` 조건을 검사합니다.

```shell-session
$ oc get ingresscontroller -n openshift-ingress-operator subnets -o jsonpath="{.status.conditions[?(@.type==\"Progressing\")]}" | yq -PC
```

```shell-session
lastTransitionTime: "2024-11-25T20:19:31Z"
message: 'One or more status conditions indicate progressing: LoadBalancerProgressing=True (OperandsProgressing: One or more managed resources are progressing: The IngressController subnets were changed from [...] to [...].  To effectuate this change, you must delete the service: `oc -n openshift-ingress delete svc/router-<name>`; the service load-balancer will then be deprovisioned and a new one created. This will most likely cause the new load-balancer to have a different host name and IP address and cause disruption. To return to the previous state, you can revert the change to the IngressController: [...]'
reason: IngressControllerProgressing
status: "True"
type: Progressing
```

업데이트를 적용하려면 다음 명령을 실행하여 Ingress 컨트롤러와 연결된 서비스를 삭제합니다.

```shell-session
$ oc -n openshift-ingress delete svc/router-<name>
```

검증

로드 밸런서가 성공적으로 프로비저닝되었는지 확인하려면 다음 명령을 실행하여 `IngressController` 조건을 확인합니다.

```shell-session
$ oc get ingresscontroller -n openshift-ingress-operator <name> -o jsonpath="{.status.conditions}" | yq -PC
```

#### 2.6.2.8. NLB(Network Load Balancer)의 AWS Elastic IP(EIP) 주소 구성

Ingress 컨트롤러의 네트워크 로드 밸런서(NLB)에 대해 탄력적 IP라고도 하는 고정 IP를 지정할 수 있습니다. 이는 클러스터 네트워크에 대한 적절한 방화벽 규칙을 구성하려는 경우에 유용합니다.

사전 요구 사항

AWS 클러스터가 설치되어 있어야 합니다.

`IngressController` 를 매핑하려는 서브넷의 이름 또는 ID를 알아야 합니다.

절차

다음 콘텐츠가 포함된 YAML 파일을 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  namespace: openshift-ingress-operator
  name: <name>
spec:
  domain: <domain>
  endpointPublishingStrategy:
    loadBalancer:
      scope: External
      type: LoadBalancerService
      providerParameters:
        type: AWS
        aws:
          type: NLB
          networkLoadBalancer:
            subnets:
              ids:
              - <subnet_ID>
              names:
              - <subnet_A>
              - <subnet_B>
            eipAllocations:
            - <eipalloc_A>
            - <eipalloc_B>
            - <eipalloc_C>
```

1. &lt `;name&gt`; 자리 표시자를 Ingress 컨트롤러의 이름으로 바꿉니다.

2. &lt `;domain&` gt; 자리 표시자를 Ingress 컨트롤러에서 제공하는 DNS 이름으로 바꿉니다.

3. EIP를 할당하려면 범위를 `External` 값으로 설정하고 인터넷에 연결해야 합니다.

4. 서브넷의 ID와 이름을 지정합니다. 총 ID 및 이름 수는 할당된 EIP와 같아야 합니다.

5. EIP 주소를 지정합니다.

중요

가용성 영역당 최대 하나의 서브넷을 지정할 수 있습니다. 외부 Ingress 컨트롤러의 퍼블릭 서브넷만 제공합니다. 서브넷당 하나의 EIP 주소를 연결할 수 있습니다.

다음 명령을 입력하여 CR 파일을 저장하고 적용합니다.

```shell-session
$  oc apply -f sample-ingress.yaml
```

검증

다음 명령을 실행하여 `IngressController` 조건을 확인하여 로드 밸런서가 성공적으로 프로비저닝되었는지 확인합니다.

```shell-session
$ oc get ingresscontroller -n openshift-ingress-operator <name> -o jsonpath="{.status.conditions}" | yq -PC
```

#### 2.6.3. 추가 리소스

네트워크 사용자 지정으로 AWS에 클러스터를 설치합니다.

NLB 지원에 대한 자세한 내용은 AWS에서 네트워크 로드 밸런서 지원을 참조하십시오.

CLB에 대한 프록시 프로토콜 지원에 대한 자세한 내용은 Classic Load Balancer에 대한 프록시 프로토콜 지원 구성을 참조하십시오.

### 2.7. 서비스 외부 IP에 대한 수신 클러스터 트래픽 구성

MetalLB 구현 또는 IP 페일오버 배포를 사용하여 OpenShift Container Platform 클러스터 외부의 트래픽에 서비스를 사용할 수 있도록 ExternalIP 리소스를 서비스에 연결할 수 있습니다. 이러한 방식으로 외부 IP 주소를 호스팅하는 것은 베어 메탈 하드웨어에 설치된 클러스터에만 적용됩니다.

트래픽을 서비스로 라우팅하도록 외부 네트워크 인프라를 올바르게 구성해야 합니다.

#### 2.7.1. 사전 요구 사항

클러스터는 ExternalIP가 활성화된 상태로 구성됩니다. 자세한 내용은 서비스에 대한 ExternalIP 구성을 참조하십시오.

참고

송신 IP에는 동일한 ExternalIP를 사용하지 마십시오.

#### 2.7.2. 서비스에 ExternalIP 연결

ExternalIP 리소스를 서비스에 연결할 수 있습니다. 리소스를 서비스에 자동으로 연결하도록 클러스터를 구성한 경우 ExternalIP를 서비스에 수동으로 연결할 필요가 없습니다.

이 절차의 예제에서는 IP 페일오버 구성을 사용하여 클러스터의 서비스에 ExternalIP 리소스를 수동으로 연결하는 시나리오를 사용합니다.

프로세스

CLI에 다음 명령을 입력하여 ExternalIP 리소스에 호환되는 IP 주소 범위를 확인합니다.

```shell-session
$ oc get networks.config cluster -o jsonpath='{.spec.externalIP}{"\n"}'
```

참고

`autoAssignCIDRs` 가 설정되어 ExternalIP 리소스에서 `spec.externalIPs` 값을 지정하지 않은 경우 OpenShift Container Platform은 새 `Service` 오브젝트에 ExternalIP를 자동으로 할당합니다.

다음 옵션 중 하나를 선택하여 ExternalIP 리소스를 서비스에 연결합니다.

새 서비스를 생성하는 경우 `spec.externalIPs` 필드에 값을 지정하고 `allowedCIDRs` 매개변수에서 하나 이상의 유효한 IP 주소 배열을 지정합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: svc-with-externalip
spec:
  externalIPs:
    policy:
      allowedCIDRs:
      - 192.168.123.0/28
```

ExternalIP를 기존 서비스에 연결하는 경우 다음 명령을 입력합니다. `<name>` 을 서비스 이름으로 교체합니다. `<ip_address>` 를 유효한 ExternalIP 주소로 교체합니다. 쉼표로 구분된 여러 IP 주소를 제공할 수 있습니다.

```shell-session
$ oc patch svc <name> -p \
  '{
    "spec": {
      "externalIPs": [ "<ip_address>" ]
    }
  }'
```

예를 들면 다음과 같습니다.

```shell-session
$ oc patch svc mysql-55-rhel7 -p '{"spec":{"externalIPs":["192.174.120.10"]}}'
```

```shell-session
"mysql-55-rhel7" patched
```

ExternalIP 주소가 서비스에 연결되었는지 확인하려면 다음 명령을 입력합니다. 새 서비스에 ExternalIP를 지정한 경우 먼저 서비스를 생성해야 합니다.

```shell-session
$ oc get svc
```

```shell-session
NAME               CLUSTER-IP      EXTERNAL-IP     PORT(S)    AGE
mysql-55-rhel7     172.30.131.89   192.174.120.10  3306/TCP   13m
```

#### 2.7.3. 추가 리소스

MetalLB 및 MetalLB Operator 정보

IP 페일오버 구성

서비스의 ExternalIP 구성

### 2.8. NodePort를 사용하여 수신 클러스터 트래픽 구성

OpenShift Container Platform에서는 클러스터에서 실행되는 서비스와 클러스터 외부에서 통신할 수 있습니다. 이 방법에서는 `NodePort` 를 사용합니다.

#### 2.8.1. NodePort를 사용하여 클러스터로 트래픽 가져오기

클러스터의 모든 노드에서 특정 포트에 서비스를 노출하려면 `NodePort` 유형의 `서비스` 리소스를 사용하십시오. 포트는 `Service` 리소스의 `.spec.ports[*].nodePort` 필드에 지정됩니다.

중요

노드 포트를 사용하려면 추가 포트 리소스가 필요합니다.

`NodePort` 는 서비스를 노드 IP 주소의 정적 포트에 노출합니다. `NodePort` 는 기본적으로 `30000` ~ `32767` 범위에 있으며, 서비스에서 의도한 포트와 `NodePort` 가 일치하지 않을 수 있습니다. 예를 들어, 포트 `8080` 은 노드에서 포트 `31020` 으로 노출될 수 있습니다.

관리자는 외부 IP 주소가 노드로 라우팅되는지 확인해야 합니다.

`NodePort` 및 외부 IP는 독립적이며 둘 다 동시에 사용할 수 있습니다.

참고

이 섹션의 절차에는 클러스터 관리자가 수행해야 하는 사전 요구 사항이 필요합니다.

#### 2.8.2. 사전 요구 사항

다음 절차를 시작하기 전에 관리자는 다음을 수행해야 합니다.

요청이 클러스터에 도달할 수 있도록 외부 포트를 클러스터 네트워킹 환경으로 설정합니다.

클러스터 관리자 역할의 사용자가 한 명 이상 있는지 확인합니다. 이 역할을 사용자에게 추가하려면 다음 명령을 실행합니다.

```plaintext
$ oc adm policy add-cluster-role-to-user cluster-admin <user_name>
```

클러스터에 대한 네트워크 액세스 권한이 있는 마스터와 노드가 클러스터 외부에 각각 1개 이상씩 있는 OpenShift Container Platform 클러스터가 있어야 합니다. 이 절차에서는 외부 시스템이 클러스터와 동일한 서브넷에 있다고 가정합니다. 다른 서브넷에 있는 외부 시스템에 필요한 추가 네트워킹은 이 주제에서 다루지 않습니다.

#### 2.8.3. 프로젝트 및 서비스 생성

노출하려는 프로젝트 및 서비스가 존재하지 않는 경우 프로젝트를 생성한 다음 서비스를 생성합니다.

프로젝트 및 서비스가 이미 존재하는 경우 서비스 노출 절차로 건너뛰어 경로를 생성합니다.

사전 요구 사항

OpenShift CLI()를 설치하고 클러스터 관리자로 로그인합니다.

```shell
oc
```

프로세스

아래 명령을 실행하여 서비스에 대한 새 프로젝트를 생성합니다.

```shell
oc new-project
```

```shell-session
$ oc new-project <project_name>
```

아래 명령을 사용하여 서비스를 생성합니다.

```shell
oc new-app
```

```shell-session
$ oc new-app nodejs:12~https://github.com/sclorg/nodejs-ex.git
```

서비스가 생성되었는지 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get svc -n <project_name>
```

```shell-session
NAME        TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
nodejs-ex   ClusterIP   172.30.197.157   <none>        8080/TCP   70s
```

참고

기본적으로 새 서비스에는 외부 IP 주소가 없습니다.

#### 2.8.4. 경로를 생성하여 서비스 노출

아래 명령을 사용하여 서비스를 경로로 노출할 수 있습니다.

```shell
oc expose
```

사전 요구 사항

OpenShift Container Platform에 로그인되어 있습니다.

프로세스

노출하려는 서비스가 있는 프로젝트에 로그인합니다.

```shell-session
$ oc project <project_name>
```

애플리케이션의 노드 포트를 공개하려면 다음 명령을 입력하여 서비스의 CRD(사용자 정의 리소스 정의)를 수정합니다.

```shell-session
$ oc edit svc <service_name>
```

```yaml
spec:
  ports:
  - name: 8443-tcp
    nodePort: 30327
    port: 8443
    protocol: TCP
    targetPort: 8443
  sessionAffinity: None
  type: NodePort
```

1. 선택 사항: 애플리케이션의 노드 포트 범위를 지정합니다. 기본적으로 OpenShift Container Platform은 `30000-32767` 범위에서 사용 가능한 포트를 선택합니다.

2. 서비스 유형을 정의합니다.

선택 사항: 노드 포트가 노출된 상태로 서비스를 사용할 수 있는지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get svc -n myproject
```

```shell-session
NAME                TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
nodejs-ex           ClusterIP   172.30.217.127   <none>        3306/TCP         9m44s
nodejs-ex-ingress   NodePort    172.30.107.72    <none>        3306:31345/TCP   39s
```

선택 사항: 아래 명령에서 자동 생성한 서비스를 제거하려면 다음 명령을 입력합니다.

```shell
oc new-app
```

```shell-session
$ oc delete svc nodejs-ex
```

검증

`30000-32767` 범위의 포트로 서비스 노드 포트가 업데이트되었는지 확인하려면 다음 명령을 입력합니다.

```shell-session
$ oc get svc
```

다음 예제 출력에서 업데이트된 포트는 `30327` 입니다.

```shell-session
NAME    TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
httpd   NodePort   172.xx.xx.xx    <none>        8443:30327/TCP   109s
```

#### 2.8.5. 추가 리소스

노드 포트 서비스 범위 구성

Ingress 컨트롤러에 단일 NodePort 서비스 추가

### 2.9. 로드 밸런서 허용 소스 범위를 사용하여 수신 클러스터 트래픽 구성

`IngressController` 의 IP 주소 범위 목록을 지정할 수 있습니다. 이렇게 하면 `endpointPublishingStrategy` 가 `LoadBalancerService` 인 경우 로드 밸런서 서비스에 대한 액세스가 제한됩니다.

#### 2.9.1. 로드 밸런서 허용 소스 범위 구성

`spec.endpointPublishingStrategy.loadBalancer.allowedSourceRanges` 필드를 활성화하고 구성할 수 있습니다. 로드 밸런서 허용 소스 범위를 구성하면 Ingress 컨트롤러의 로드 밸런서에 대한 액세스를 지정된 IP 주소 범위 목록으로 제한할 수 있습니다.

Ingress Operator는 로드 밸런서 서비스를 조정하고 `AllowedSourceRanges` 를 기반으로 `spec.loadBalancerSourceRanges` 필드를 설정합니다.

참고

이전 버전의 OpenShift Container Platform에서 `spec.loadBalancerSourceRanges` 필드 또는 로드 밸런서 서비스 주석 `service.beta.kubernetes.io/load-balancer-source-ranges` 를 이미 설정한 경우 Ingress 컨트롤러는 업그레이드 후 `Progressing=True` 보고를 시작합니다.

이 문제를 해결하려면 `spec.loadBalancerSourceRanges` 필드를 덮어쓰는 `AllowedSourceRanges` 를 설정하고 `service.beta.kubernetes.io/load-balancer-source-ranges` 주석을 지웁니다. Ingress 컨트롤러가 `Progressing=False` 보고를 다시 시작합니다.

사전 요구 사항

실행 중인 클러스터에 배포된 Ingress 컨트롤러가 있습니다.

프로세스

다음 명령을 실행하여 Ingress 컨트롤러에 허용되는 소스 범위 API를 설정합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontroller/default \
    --type=merge --patch='{"spec":{"endpointPublishingStrategy": \
    {"type":"LoadBalancerService", "loadbalancer": \
    {"scope":"External", "allowedSourceRanges":["0.0.0.0/0"]}}}}'
```

1. 예제 값 `0.0.0.0/0` 은 허용되는 소스 범위를 지정합니다.

#### 2.9.2. 로드 밸런서로 마이그레이션 허용된 소스 범위

`service.beta.kubernetes.io/load-balancer-source-ranges` 주석을 이미 설정한 경우 로드 밸런서 허용 소스 범위로 마이그레이션할 수 있습니다.

`AllowedSourceRanges` 를 설정하면 Ingress 컨트롤러는 `AllowedSourceRanges` 값을 기반으로 `spec.loadBalancerSourceRanges` 필드를 설정하고 `service.beta.kubernetes.io/load-balancer-source-ranges` 주석을 설정합니다.

참고

이전 버전의 OpenShift Container Platform에서 `spec.loadBalancerSourceRanges` 필드 또는 로드 밸런서 서비스 주석 `service.beta.kubernetes.io/load-balancer-source-ranges` 를 이미 설정한 경우 Ingress 컨트롤러는 업그레이드 후 `Progressing=True` 보고를 시작합니다.

이 문제를 해결하려면 `spec.loadBalancerSourceRanges` 필드를 덮어쓰는 `AllowedSourceRanges` 를 설정하고 `service.beta.kubernetes.io/load-balancer-source-ranges` 주석을 지웁니다. Ingress 컨트롤러는 `Progressing=False` 보고를 다시 시작합니다.

사전 요구 사항

`service.beta.kubernetes.io/load-balancer-source-ranges` 주석을 설정해야 합니다.

프로세스

`service.beta.kubernetes.io/load-balancer-source-ranges` 가 설정되어 있는지 확인합니다.

```shell-session
$ oc get svc router-default -n openshift-ingress -o yaml
```

```yaml
apiVersion: v1
kind: Service
metadata:
  annotations:
    service.beta.kubernetes.io/load-balancer-source-ranges: 192.168.0.1/32
```

`spec.loadBalancerSourceRanges` 필드가 설정되지 않았는지 확인합니다.

```shell-session
$ oc get svc router-default -n openshift-ingress -o yaml
```

```yaml
...
spec:
  loadBalancerSourceRanges:
  - 0.0.0.0/0
...
```

클러스터를 OpenShift Container Platform 4.20으로 업데이트합니다.

다음 명령을 실행하여 `ingresscontroller` 에 허용되는 소스 범위 API를 설정합니다.

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontroller/default \
    --type=merge --patch='{"spec":{"endpointPublishingStrategy": \
    {"loadBalancer":{"allowedSourceRanges":["0.0.0.0/0"]}}}}'
```

1. 예제 값 `0.0.0.0/0` 은 허용되는 소스 범위를 지정합니다.

#### 2.9.3. 추가 리소스

OpenShift 업데이트 소개

### 2.10. 기존 ingress 오브젝트 패치

오브젝트를 다시 생성하거나 서비스를 중단하지 않고 기존 `Ingress` 오브젝트의 다음 필드를 업데이트하거나 수정할 수 있습니다.

사양

호스트

경로

백엔드 서비스

SSL/TLS 설정

주석

#### 2.10.1. Ingress 오브젝트를 패치하여 ingressWithoutClassName 경고 해결

`ingressClassName` 필드는 `IngressClass` 오브젝트의 이름을 지정합니다. 각 `Ingress` 오브젝트에 대한 `ingressClassName` 필드를 정의해야 합니다.

`Ingress` 오브젝트에 대한 `ingressClassName` 필드를 정의하지 않은 경우 라우팅 문제가 발생할 수 있습니다. 24시간 후에 `ingressWithoutClassName` 경고를 수신하여 `ingressClassName` 필드를 설정하도록 알립니다.

절차

완료된 `ingressClassName` 필드로 `Ingress` 오브젝트를 패치하여 적절한 라우팅 및 기능을 보장합니다.

모든 `IngressClass` 오브젝트를 나열합니다.

```shell-session
$ oc get ingressclass
```

모든 네임스페이스의 모든 `Ingress` 오브젝트를 나열합니다.

```shell-session
$ oc get ingress -A
```

`Ingress` 오브젝트를 패치합니다.

```shell-session
$ oc patch ingress/<ingress_name> --type=merge --patch '{"spec":{"ingressClassName":"openshift-default"}}'
```

& `lt;ingress_name&` gt;을 `Ingress` 오브젝트의 이름으로 바꿉니다. 이 명령은 원하는 ingress 클래스 이름을 포함하도록 `Ingress` 오브젝트를 패치합니다.

### 2.11. 특정 서브넷에 로드 밸런서 할당

로드 밸런서를 할당하여 애플리케이션 트래픽을 효율적으로 관리할 수 있습니다. 네트워크 관리자는 로드 밸런서를 할당하여 최적의 트래픽 배포, 애플리케이션 고가용성, 중단되지 않는 서비스 및 네트워크 분할을 보장할 수 있는 배포를 사용자 지정할 수 있습니다.

#### 2.11.1. AWS의 특정 서브넷에 API 및 Ingress 로드 밸런서 할당

가상 프라이빗 클라우드의 서브넷(VPC) 서브넷을 명시적으로 정의하고 `install-config.yaml` 파일의 `platform.aws.vpc.subnets` 섹션 내에서 직접 특정 역할을 할당하여 Ingress 컨트롤러의 OpenShift Load Balancer의 네트워크 배치를 제어할 수 있습니다.

이 방법을 사용하면 Ingress 컨트롤러 및 기타 클러스터 구성 요소와 같은 리소스에 사용되는 서브넷을 세부적으로 제어할 수 있습니다.

#### 2.11.1.1. 설치 시 OpenShift API 및 인그레스 로드 밸런서를 위한 AWS 서브넷 지정

다음 단계를 수행하여 특정 서브넷에 API 및 인그레스 로드 밸런서를 할당합니다.

사전 요구 사항

시작하기 전에 다음을 확인하십시오.

기존 AWS VPC(가상 프라이빗 클라우드)

다음과 같은 고려 사항이 있는 OpenShift 클러스터에서 사용하기 위해 사전 구성된 AWS 서브넷입니다.

서브넷 ID 목록이 있습니다(예: `subnet-0123456789abcdef0`). 이러한 ID는 `install-config.yaml` 파일에서 사용됩니다.

로드 밸런서 및 컨트롤 플레인과 같은 기타 중요한 구성 요소를 고가용성하려면 최소 두 개의 가용성 영역(AZ)을 사용합니다.

할당된 모든 역할에 대해 이러한 서브넷 내에 사용 가능한 IP 주소가 충분합니다.

네트워크 ACL 및 보안 그룹을 포함한 이러한 서브넷에 대한 AWS 구성은 할당된 모든 역할에 필요한 트래픽을 허용해야 합니다. 수신 컨트롤러를 호스팅하는 서브넷의 경우 일반적으로 필수 소스의 TCP 포트 80 및 443을 포함합니다.

대상 OpenShift 버전에 대한 OpenShift 설치 프로그램 바이너리가 있습니다.

`install-config.yaml` 파일이 있습니다.

프로세스

`install-config.yaml` 파일을 준비합니다.

아직 설치되지 않은 경우 OpenShift 설치 프로그램을 사용하여 설치 구성 파일을 생성합니다.

```shell-session
$ openshift-install create install-config --dir=<your_installation_directory>
```

이 명령은 지정된 디렉터리에 `install-config.yaml` 파일을 생성합니다.

서브넷을 정의하고 역할을 할당합니다.

텍스트 편집기를 사용하여 < `your_installation_directory` >에 있는 `install-config.yaml` 파일을 엽니다. `platform.aws.vpc.subnets` 필드에서 VPC 서브넷 및 지정된 역할을 정의합니다.

클러스터에서 사용할 각 AWS 서브넷마다 ID와 `역할` 목록을 지정하는 항목을 생성합니다. 각 역할은 `유형` 키가 있는 오브젝트입니다. 기본 Ingress 컨트롤러의 서브넷을 지정하려면 `IngressControllerLB 유형으로` 역할을 할당합니다.

```yaml
apiVersion: v1
baseDomain: example.com
metadata:
  name: my-cluster # Example cluster name
platform:
  aws:
    region: us-east-1
    vpc:
      subnets:
      - id: subnet-0fcf8e0392f0910d5 # Public Subnet in AZ us-east-1a
        roles:
        - type: IngressControllerLB
        - type: BootstrapNode
      - id: subnet-0xxxxxxxxxxxxxxza # Public Subnet in another AZ for HA
        roles:
        - type: IngressControllerLB
      - id: subnet-0fcf8e0392f0910d4 # Private Subnet in AZ us-east-1a
        roles:
        - type: ClusterNode
      - id: subnet-0yyyyyyyyyyyyyyzb # Private Subnet in another AZ for HA
        roles:
        - type: ClusterNode
      # Add other subnet IDs and their roles as needed for your cluster architecture
pullSecret: '...'
sshKey: '...'
```

1. 기본 도메인.

2. AWS 리전입니다.

3. `platform.aws` 아래의 vpc 오브젝트에는 서브넷 목록이 포함되어 있습니다.

4. OpenShift에서 사용할 모든 서브넷 오브젝트 목록입니다. 각 오브젝트는 서브넷 ID 및 해당 역할을 정의합니다.

5. 을 AWS 서브넷 ID로 바꿉니다.

6. `유형: IngressControllerLB` 역할은 특히 기본 Ingress 컨트롤러의 LoadBalancer에 대해 이 서브넷을 지정합니다. 프라이빗/내부 클러스터에서 `IngressControllerLB` 역할의 서브넷은 private이어야 합니다.

7. `type: ClusterNode` 역할은 컨트롤 플레인 및 컴퓨팅 노드에 이 서브넷을 지정합니다. 일반적으로 프라이빗 서브넷입니다.

8. 풀 시크릿입니다.

9. SSH 키입니다.

`서브넷` 목록의 컨트롤 플레인 로드 밸런서 항목은 유사한 패턴을 따릅니다.

```yaml
# ... (within platform.aws.vpc.subnets list)
      - id: subnet-0fcf8e0392f0910d6 # Public Subnet for External API LB
        roles:
        - type: ControlPlaneExternalLB
      - id: subnet-0fcf8e0392f0910d7 # Private Subnet for Internal API LB
        roles:
        - type: ControlPlaneInternalLB
# ...
```

기본 공용 Ingress 컨트롤러의 경우 `install-config.yaml` 파일에서 `IngressControllerLB` 역할이 할당된 모든 서브넷은 공용 서브넷이어야 합니다. 예를 들어 아웃바운드 트래픽을 인터넷 게이트웨이(IGW)로 보내는 AWS의 경로 테이블 항목이 있어야 합니다.

AZ에서 필요한 모든 서브넷, 공용 및 프라이빗을 나열하고 클러스터 아키텍처에 따라 적절한 역할을 할당해야 합니다.

서브넷 ID는 기존 VPC에서 서브넷을 정의하고 선택적으로 의도한 역할을 지정할 수 있습니다. 서브넷에 역할이 지정되지 않은 경우 서브넷 역할이 자동으로 결정됩니다. 이 경우 VPC에는 이외의 서브넷이 포함되어서는 안 됩니다.

```shell
kubernetes.io/cluster/<cluster-id> 태그가 없는 다른 클러스터
```

역할이 서브넷에 지정된 경우 각 서브넷에 하나 이상의 할당된 역할이 있어야 하며 `ClusterNode`, `BootstrapNode`, `IngressControllerLB`, `ControlPlaneExternalLB`, `ControlPlaneInternalLB` 역할을 하나 이상 서브넷에 할당해야 합니다.

그러나 클러스터 범위가 내부인 경우 `ControlPlaneExternalLB` 가 필요하지 않습니다.

클러스터 설치를 진행합니다.

`install-config.yaml` 파일에 대한 변경 사항을 저장한 후 클러스터를 생성합니다.

```shell-session
$ openshift-install create cluster --dir=<your_installation_directory>
```

이제 설치 프로그램에서 `IngressControllerLB` 역할로 지정된 서브넷에 Ingress Controller의 LoadBalancer를 배치하는 등 `install-config.yaml` 파일의 `platform.aws.vpc.subnets` 섹션의 서브넷 정의 및 명시적 역할 할당을 사용합니다.

참고

`IngressControllerLB`, `ClusterNode`, `ControlPlaneExternalLB`, `ControlPlaneInternalLB`, `BootstrapNode` 와 같은 유형을 지정하는 것과 같이 `platform.aws.vpc.subnets` 내의 역할 할당 메커니즘은 OpenShift 설치 프로그램이 다양한 클러스터 서비스 및 구성 요소에 적합한 서브넷을 식별하는 포괄적인 방법입니다.

### 2.12. DNS 관리 정책 이해

클러스터 관리자는 Ingress 컨트롤러를 생성할 때 Operator는 DNS 레코드를 자동으로 관리합니다. 이는 필수 DNS 영역이 클러스터 DNS 영역과 다른 경우 또는 DNS 영역이 클라우드 공급자 외부에서 호스팅되는 경우 몇 가지 제한 사항이 있습니다.

#### 2.12.1. 관리형 DNS 관리 정책

Ingress 컨트롤러에 대한 관리형 DNS 관리 정책을 사용하면 클라우드 공급자의 와일드카드 DNS 레코드의 라이프사이클이 Operator에 의해 자동으로 관리됩니다. 이는 기본 동작입니다.

Ingress 컨트롤러를 `Managed` 에서 `Unmanaged` DNS 관리 정책으로 변경하면 Operator에서 클라우드에 프로비저닝된 이전 와일드카드 DNS 레코드를 정리하지 않습니다.

Ingress 컨트롤러를 `Unmanaged` 에서 `Managed` DNS 관리 정책으로 변경하면 Operator에서 클라우드 공급자에 대한 DNS 레코드를 생성하려고 시도하거나 이미 존재하는 경우 DNS 레코드를 업데이트합니다.

#### 2.12.2. 관리되지 않는 DNS 관리 정책

Ingress 컨트롤러에 대한 관리되지 않는 DNS 관리 정책은 클라우드 공급자의 와일드카드 DNS 레코드 라이프사이클이 자동으로 관리되지 않도록 합니다. 대신 클러스터 관리자가 담당합니다.

#### 2.12.3. 수동 DNS 관리를 위한 Ingress 컨트롤러 생성

클러스터 관리자는 Unmanaged DNS 관리 정책을 사용하여 새 사용자 정의 Ingress 컨트롤러를 생성할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

다음 콘텐츠를 사용하여 `sample-ingress.yaml` 이라는 `IngressController` CR(사용자 정의 리소스) 파일을 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  namespace: openshift-ingress-operator
  name: <name>
spec:
  domain: <domain>
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
      dnsManagementPolicy: Unmanaged
```

1. `IngressController`

`오브젝트의 이름으로` <name>을 지정합니다.

2

- 으로 생성된 DNS 레코드를 기반으로 `도메인` 을 지정합니다.

3. 로드 밸런서를 외부에 노출하려면 `범위를`

`External` 로 지정합니다.

4. `dnsManagementPolicy` 는 Ingress 컨트롤러가 로드 밸런서와 연결된 와일드카드 DNS 레코드의 라이프사이클을 관리하고 있는지 여부를 나타냅니다. 유효한 값은 `Managed` 및 `Unmanaged` 입니다. 기본값은 `Managed` 입니다.

`IngressController` 오브젝트를 생성하려면 매니페스트를 적용합니다.

```shell-session
$ oc apply -f sample-ingress.yaml
```

다음 명령을 실행하여 Ingress 컨트롤러가 올바른 정책을 사용하여 생성되었는지 확인합니다.

```shell-session
$ oc get ingresscontroller <name> -n openshift-ingress-operator -o=jsonpath={.spec.endpointPublishingStrategy.loadBalancer}
```

출력을 검사하고 `dnsManagementPolicy` 가 `Unmanaged` 로 설정되어 있는지 확인합니다.

#### 2.12.4. 수동 DNS 관리를 위한 기존 Ingress 컨트롤러 수정

클러스터 관리자는 기존 Ingress 컨트롤러를 수정하여 DNS 레코드 라이프사이클을 수동으로 관리할 수 있습니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

선택한 Ingress 컨트롤러를 수정하여 `dnsManagementPolicy` 매개변수를 설정합니다.

```shell-session
$ SCOPE=$(oc -n openshift-ingress-operator get ingresscontroller <name> -o=jsonpath="{.status.endpointPublishingStrategy.loadBalancer.scope}")
```

```shell-session
$ oc -n openshift-ingress-operator patch ingresscontrollers/default --type=merge --patch="{\"spec\":{\"endpointPublishingStrategy\":{\"type\":\"LoadBalancerService\",\"loadBalancer\":{\"dnsManagementPolicy\":\"Unmanaged\", \"scope\":\"${SCOPE}\"}}}}"
ingresscontroller.operator.openshift.io/default patched
```

다음 명령을 실행하여 Ingress 컨트롤러가 올바르게 수정되었는지 확인합니다.

```shell-session
$ oc get ingresscontroller <name> -n openshift-ingress-operator -o=jsonpath={.spec.endpointPublishingStrategy.loadBalancer}
```

출력을 검사하고 `dnsManagementPolicy` 가 `Unmanaged` 로 설정되어 있는지 확인합니다.

#### 2.12.5. 추가 리소스

Ingress 컨트롤러 구성 매개변수

### 2.13. OpenShift Container Platform 네트워킹을 사용한 게이트웨이 API

OpenShift Container Platform은 Ingress Operator와 함께 Gateway API를 사용하여 네트워크 트래픽을 구성하는 추가 방법을 제공합니다.

중요

게이트웨이 API는 UDN(사용자 정의 네트워크)을 지원하지 않습니다.

#### 2.13.1. 게이트웨이 API 개요

게이트웨이 API는 커뮤니티에서 관리하는 오픈 소스 Kubernetes 네트워킹 메커니즘입니다. 클러스터의 경우 전송 계층 L4 및 애플리케이션 계층 L7 내의 라우팅에 중점을 둡니다. 다양한 벤더가 게이트웨이 API의 여러 구현을 제공합니다.

이 프로젝트는 광범위한 커뮤니티 지원이 포함된 이식 가능한 API를 사용하여 표준화된 에코시스템을 제공하기 위한 노력입니다. Gateway API 기능을 Ingress Operator에 통합하면 기존 커뮤니티 및 업스트림 개발 작업과 일치하는 네트워킹 솔루션을 사용할 수 있습니다.

게이트웨이 API는 Ingress Operator의 기능을 확장하여 더 세분화된 클러스터 트래픽 및 라우팅 구성을 처리합니다. 이러한 기능을 사용하면 게이트웨이 API CRD(사용자 정의 리소스 정의) 인스턴스를 생성할 수 있습니다. OpenShift Container Platform 클러스터의 경우 Ingress Operator는 다음 리소스를 생성합니다.

게이트웨이

이 리소스는 트래픽을 클러스터 내의 서비스로 변환하는 방법을 설명합니다. 예를 들어 특정 로드 밸런서 구성입니다.

GatewayClass

이 리소스는 공통 구성 및 동작을 공유하는 `Gateway` 오브젝트 세트를 정의합니다. 예를 들어 퍼블릭 또는 프라이빗 애플리케이션에 사용되는 게이트웨이 리소스 세트를 구분하기 위해 두 개의 별도 `Gateway Class` 오브젝트를 생성할 수 있습니다.

HTTPRoute

이 리소스는 게이트웨이에서 서비스로의 HTTP 요청의 라우팅 동작을 지정하며 HTTP 연결 또는 종료된 HTTPS 연결을 멀티플렉싱하는 데 특히 유용합니다.

GRPCRoute

이 리소스는 gRPC 요청의 라우팅 동작을 지정합니다.

ReferenceGrant

이 리소스는 네임스페이스 간 참조를 활성화합니다. 예를 들어, 경로가 다른 네임스페이스에 있는 백엔드로 트래픽을 전달할 수 있습니다.

OpenShift Container Platform에서 Gateway API의 구현은 `gateway.networking.k8s.io/v1` 을 기반으로 하며 이 버전의 모든 필드가 지원됩니다.

#### 2.13.1.1. 게이트웨이 API의 이점

Gateway API는 다음과 같은 이점을 제공합니다.

이식성: OpenShift Container Platform은 HAProxy를 사용하여 Ingress 성능을 개선하지만 게이트웨이 API는 특정 동작을 제공하기 위해 벤더별 주석을 사용하지 않습니다. HAProxy와 유사한 성능을 얻으려면 `게이트웨이` 오브젝트를 수평으로 확장하거나 관련 노드를 수직으로 확장해야 합니다.

문제 분리: 게이트웨이 API는 리소스에 대한 역할 기반 접근 방식을 사용하며 대규모 조직이 역할과 팀을 구성하는 방법에 보다 깔끔하게 적합합니다.

플랫폼 엔지니어는 `GatewayClass` 리소스에 중점을 둘 수 있으며 클러스터 관리자는 `게이트웨이` 리소스 구성에 중점을 둘 수 있으며 애플리케이션 개발자는 `HTTPRoute` 리소스를 사용하여 서비스를 라우팅하는 데 중점을 둘 수 있습니다.

확장성: 추가 기능은 표준화된 CRD로 개발됩니다.

#### 2.13.1.2. 게이트웨이 API의 제한 사항

게이트웨이 API에는 다음과 같은 제한 사항이 있습니다.

버전 비호환성: 게이트웨이 API 에코시스템이 빠르게 변경되고 일부 구현은 게이트웨이 API의 다른 버전을 기반으로 하므로 다른 구현에서는 작동하지 않습니다.

리소스 오버헤드: 더 유연하지만 Gateway API는 여러 리소스 유형을 사용하여 결과를 얻습니다. 소규모 애플리케이션의 경우 기존 Ingress의 단순성이 더 적합할 수 있습니다.

#### 2.13.2. OpenShift Container Platform용 게이트웨이 API 구현

Ingress Operator는 다른 벤더 구현에서 OpenShift Container Platform 클러스터에 정의된 CRD를 사용할 수 있는 방식으로 게이트웨이 API CRD의 라이프사이클을 관리합니다.

경우에 따라 Gateway API는 벤더 구현이 지원하지 않는 필드를 하나 이상 제공하지만 해당 구현은 스키마에서 나머지 필드와 호환되지 않습니다. 이러한 "드라이드 필드"로 인해 Ingress 워크로드, 잘못 프로비저닝된 애플리케이션 및 서비스, 보안 관련 문제가 발생할 수 있습니다.

OpenShift Container Platform은 특정 버전의 Gateway API CRD를 사용하므로 게이트웨이 API의 타사 구현을 사용하려면 모든 필드가 예상대로 작동하도록 OpenShift Container Platform 구현을 준수해야 합니다.

OpenShift Container Platform 4.20 클러스터 내에서 생성된 모든 CRD는 Ingress Operator에 의해 버전화되고 유지 관리됩니다.

CRD가 이미 있지만 Ingress Operator에서 이전에 관리하지 않은 경우 Ingress Operator는 이러한 구성이 OpenShift Container Platform에서 지원하는 Gateway API 버전과 호환되는지 여부를 확인하고 CRD 연속 승인이 필요한 admin-gate를 생성합니다.

중요

Gateway API CRD가 포함된 이전 OpenShift Container Platform 버전의 클러스터를 업데이트하는 경우 OpenShift Container Platform에서 지원하는 버전과 정확히 일치하도록 해당 리소스가 변경됩니다.

그렇지 않으면 해당 CRD가 OpenShift Container Platform에서 관리되지 않았으며 Red Hat에서 지원하지 않는 기능을 포함할 수 있으므로 클러스터를 업데이트할 수 없습니다.

#### 2.13.3. Ingress Operator의 Gateway API 시작하기

첫 번째 단계에 표시된 대로 GatewayClass를 생성할 때 클러스터에서 사용할 게이트웨이 API를 구성합니다.

중요

OpenShift Container Platform Gateway API 구현은 Cluster Ingress Operator (CIO)를 사용하여 `openshift-ingress` 네임스페이스에서 특정 버전의 OpenShift Service Mesh (OSSM v3.x)를 설치하고 관리합니다.

클러스터에 모든 네임스페이스에 활성 OpenShift Service Mesh(OSSM v2.x) 서브스크립션이 있는 경우 충돌이 발생합니다. OSSM v2.x 및 OSSM v3.x는 동일한 클러스터에 공존할 수 없습니다.

GatewayClass 리소스를 생성할 때 충돌하는 OSSM v2.x 서브스크립션이 있는 경우 Cluster Ingress Operator는 필요한 OSSM v3.x 구성 요소를 설치하려고 하지만 이 설치 작업에 실패합니다.

결과적으로 Gateway 또는 HTTPRoute와 같은 게이트웨이 API 리소스는 적용되지 않으며 트래픽을 라우팅하도록 프록시가 구성되지 않습니다. OpenShift Container Platform 4.19에서 이 오류는 자동으로 수행됩니다.

OpenShift Container Platform 4.20 이상에서는 이러한 충돌로 인해 Ingress ClusterOperator가 Degraded 상태를 보고합니다.

`GatewayClass` 를 생성하여 게이트웨이 API를 활성화하기 전에 클러스터에 활성 OSSM v2.x 서브스크립션이 없는지 확인합니다.

프로세스

`GatewayClass` 오브젝트를 생성합니다.

다음 정보가 포함된 YAML 파일 `openshift-default.yaml` 을 생성합니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: openshift-default
spec:
  controllerName: openshift.io/gateway-controller/v1
```

1. 컨트롤러 이름입니다.

중요

컨트롤러 이름은 Ingress Operator에서 관리할 수 있도록 정확히 표시되어야 합니다. 이 필드를 다른 것으로 설정하면 Ingress Operator는 `Gateway Class` 오브젝트 및 연결된 모든 게이트웨이, `GRPCRoute` 및 `HTTPRoute` 오브젝트를 무시합니다.

컨트롤러 이름은 OpenShift Container Platform에서 게이트웨이 API 구현과 연결되며 `openshift.io/gateway-controller/v1` 은 허용된 유일한 컨트롤러 이름입니다.

다음 명령을 실행하여 `GatewayClass` 리소스를 생성합니다.

```shell-session
$ oc create -f openshift-default.yaml
```

```shell-session
gatewayclass.gateway.networking.k8s.io/openshift-default created
```

`GatewayClass` 리소스를 생성하는 동안 Ingress Operator는 Red Hat OpenShift Service Mesh, Istio 사용자 정의 리소스 및 `openshift-ingress` 네임스페이스에 새 배포를 설치합니다.

선택 사항: 새 배포 `istiod-openshift-gateway` 가 준비되었으며 사용 가능한지 확인합니다.

```shell-session
$ oc get deployment -n openshift-ingress
```

```shell-session
NAME                       READY   UP-TO-DATE   AVAILABLE   AGE
istiod-openshift-gateway   1/1     1            1           55s
router-default             2/2     2            2           6h4m
```

다음 명령을 실행하여 보안을 생성합니다.

```shell-session
$ oc -n openshift-ingress create secret tls gwapi-wildcard --cert=wildcard.crt --key=wildcard.key
```

다음 명령을 실행하여 Ingress Operator의 도메인을 가져옵니다.

```shell-session
$ DOMAIN=$(oc get ingresses.config/cluster -o jsonpath={.spec.domain})
```

`Gateway` 오브젝트를 만듭니다.

다음 정보가 포함된 YAML 파일 `example-gateway.yaml` 을 만듭니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: example-gateway
  namespace: openshift-ingress
spec:
  gatewayClassName: openshift-default
  listeners:
  - name: https
    hostname: "*.gwapi.${DOMAIN}"
    port: 443
    protocol: HTTPS
    tls:
      mode: Terminate
      certificateRefs:
      - name: gwapi-wildcard
    allowedRoutes:
      namespaces:
        from: All
```

1. `Gateway` 오브젝트는 `openshift-ingress` 네임스페이스에 생성해야 합니다.

2. `Gateway` 오브젝트는 이전에 생성한 `GatewayClass` 오브젝트의 이름을 참조해야 합니다.

3. HTTPS 리스너는 클러스터 도메인의 하위 도메인과 일치하는 HTTPS 요청을 수신 대기합니다. 이 리스너를 사용하여 Gateway API `HTTPRoute` 리소스를 사용하여 애플리케이션에 대한 수신을 구성합니다.

4. 호스트 이름은 Ingress Operator 도메인의 하위 도메인이어야 합니다. 도메인을 사용하는 경우 리스너는 해당 도메인의 모든 트래픽을 제공하려고 합니다.

5. 이전에 생성한 보안의 이름입니다.

다음 명령을 실행하여 리소스를 적용합니다.

```shell-session
$ oc apply -f example-gateway.yaml
```

선택 사항: `게이트웨이` 오브젝트를 생성할 때 Red Hat OpenShift Service Mesh는 동일한 이름으로 배포 및 서비스를 자동으로 프로비저닝합니다. 다음 명령을 실행하여 확인합니다.

배포를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get deployment -n openshift-ingress example-gateway-openshift-default
```

```shell-session
NAME                                 READY   UP-TO-DATE   AVAILABLE   AGE
example-gateway-openshift-default    1/1     1            1           25s
```

서비스를 확인하려면 다음 명령을 실행합니다.

```shell-session
$ oc get service -n openshift-ingress example-gateway-openshift-default
```

```shell-session
NAME                                TYPE           CLUSTER-IP   EXTERNAL-IP         PORT(S)      AGE
example-gateway-openshift-default   LoadBalancer   10.1.2.3     <external_ipname>   <port_info>  47s
```

선택 사항: Ingress Operator는 리스너의 호스트 이름을 사용하여 `DNSRecord` CR을 자동으로 생성하고 `gateway.networking.k8s.io/gateway-name=example-gateway`. 다음 명령을 실행하여 DNS 레코드의 상태를 확인합니다.

```shell-session
$ oc -n openshift-ingress get dnsrecord -l gateway.networking.k8s.io/gateway-name=example-gateway -o yaml
```

```yaml
kind: DNSRecord
  ...
status:
  ...
  zones:
  - conditions:
    - message: The DNS provider succeeded in ensuring the record
      reason: ProviderSuccess
      status: "True"
      type: Published
    dnsZone:
      tags:
        ...
  - conditions:
    - message: The DNS provider succeeded in ensuring the record
      reason: ProviderSuccess
      status: "True"
      type: Published
    dnsZone:
      id: ...
```

이미 생성된 네임스페이스 및 `example-app/example-app` 이라는 애플리케이션으로 요청을 보내는 `HTTPRoute` 리소스를 생성합니다.

다음 정보가 포함된 YAML 파일 `example-route.yaml` 을 생성합니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: example-route
  namespace: example-app-ns
spec:
  parentRefs:
  - name: example-gateway
    namespace: openshift-ingress
  hostnames: ["example.gwapi.${DOMAIN}"]
  rules:
  - backendRefs:
    - name: example-app
      port: 8443
```

1. 애플리케이션을 배포하는 네임스페이스입니다.

2. 이 필드는 이전에 구성한 `Gateway` 오브젝트를 가리켜야 합니다.

3. 호스트 이름은 `Gateway` 오브젝트에 지정된 호스트 이름과 일치해야 합니다. 이 경우 리스너는 와일드카드 호스트 이름을 사용합니다.

4. 이 필드는 서비스를 가리키는 백엔드 참조를 지정합니다.

5. 애플리케이션의 `서비스` 이름입니다.

다음 명령을 실행하여 리소스를 적용합니다.

```shell-session
$ oc apply -f example-route.yaml
```

```shell-session
httproute.gateway.networking.k8s.io/example-route created
```

검증

다음 명령을 실행하여 `Gateway` 오브젝트가 배포되고 `조건이` 적용되었는지 확인합니다.

```shell-session
$ oc wait -n openshift-ingress --for=condition=Programmed gateways.gateway.networking.k8s.io example-gateway
```

```shell-session
gateway.gateway.networking.k8s.io/example-gateway condition met
```

구성된 `HTTPRoute` 오브젝트 호스트 이름으로 요청을 보냅니다.

```shell-session
$ curl -I --cacert <local cert file> https://example.gwapi.${DOMAIN}:443
```

#### 2.13.4. 게이트웨이 API 배포 토폴로지

게이트웨이 API는 공유 게이트웨이 또는 전용 게이트웨이의 두 가지 토폴로지를 제공하도록 설계되었습니다. 각 토폴로지에는 자체 이점이 있으며 보안 영향이 다릅니다.

전용 게이트웨이

경로 및 로드 밸런서 또는 프록시는 동일한 네임스페이스에서 제공됩니다. `Gateway` 오브젝트는 특정 애플리케이션 네임스페이스로의 경로를 제한합니다. OpenShift Container Platform에서 게이트웨이 API 리소스를 배포할 때 기본 토폴로지입니다.

공유 게이트웨이

경로는 여러 네임스페이스에서 제공되거나 여러 호스트 이름으로 제공됩니다. `Gateway` 오브젝트 필터는 `spec.listeners.allowedRoutes.namespaces` 필드를 사용하여 애플리케이션 네임스페이스의 경로를 허용합니다.

#### 2.13.4.1. 전용 게이트웨이 예

다음 예제에서는 전용 `게이트웨이` 리소스인 `fin-gateway` 를 보여줍니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: fin-gateway
  namespace: openshift-ingress
spec:
  listeners:
  - name: http
    protocol: HTTP
    port: 8080
    hostname: "example.com"
```

1. `spec.listeners[].allowedRoutes` 를 설정하지 않고 `Gateway` 리소스를 생성하면 암시적으로 `namespaces.from` 필드가 `Same` 값을 갖도록 설정됩니다.

다음 예제에서는 전용 `게이트웨이` 오브젝트에 연결하는 연결된 `HTTPRoute` 리소스 `sales-db` 를 보여줍니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: sales-db
  namespace: openshift-ingress
spec:
  parentRefs:
  - name: fin-gateway
  hostnames:
  - sales-db.example.com
  rules:
    - backendRefs:
        - name: sales-db
        ¦ port: 8080
```

`HTTPRoute` 리소스에는 게이트웨이에 연결하기 위해 `parentRefs` 필드의 값으로 `Gateway` 오브젝트의 이름이 있어야 합니다. 암시적으로 경로는 `Gateway` 오브젝트와 동일한 네임스페이스에 있는 것으로 간주됩니다.

#### 2.13.4.2. 공유 게이트웨이 예

다음 예제에서는 `shared -gateway- access: "true"` 를 포함하는 모든 네임스페이스와 일치하도록 `spec.listeners.allowedRoutes.namespaces` 레이블 선택기가 설정된 `Gateway` 리소스입니다.

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: devops-gateway
  namespace: openshift-ingress
listeners:
  - name: https
    protocol: HTTPS
    hostname: "example.com"
    allowedRoutes:
      namespaces:
        from: Selector
        selector:
        ¦ matchLabels:
        ¦   shared-gateway-access: "true"
```

다음 예제에서는 Cryostat `-gateway 리소스에 허용되는 네임스페이스` 를 보여줍니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dev
  labels:
    shared-gateway-access: "true"
---
apiVersion: v1
kind: Namespace
metadata:
  name: ops
  labels:
    shared-gateway-access: "true"
```

이 예제에서 두 개의 `HTTPRoute` 리소스 `dev-portal` 및 `ops-home` 은 다른 네임스페이스에 있지만 공유 게이트웨이에 연결되어 있습니다.

```yaml
apiVersion: v1
kind: HTTPRoute
metadata:
  name: dev-portal
  namespace: dev
spec:
  parentRefs:
  - name: devops-gateway
    namespace: openshift-ingress
  rules:
  - backendRefs:
    - name: dev-portal
      port: 8080
---
apiVersion: v1
kind: HTTPRoute
metadata:
  name: ops-home
  namespace: ops
spec:
  parentRefs:
  - name: devops-gateway
    namespace: openshift-ingress
  rules:
  - backendRefs:
    - name: ops-home
      port: 8080
```

공유 게이트웨이 토폴로지를 사용하면 경로가 연결할 `게이트웨이` 오브젝트의 네임스페이스를 지정해야 합니다. 여러 `Gateway` 오브젝트를 네임스페이스에서 배포하고 공유할 수 있습니다. 공유 게이트웨이가 여러 개인 경우 이 토폴로지는 Ingress 컨트롤러 샤딩과 개념적으로 유사합니다.

#### 2.13.5. Ingress Operator는 게이트웨이 API 및 OSSM 충돌로 인해 성능이 저하됨

OpenShift Container Platform 4.20 이상에서는 OSM(OpenShift Service Mesh) v2.x 서브스크립션이 있는 상태에서 `GatewayClass` 리소스를 생성하면 `ingress` Cluster Operator(CIO)에서 `Degraded` 상태를 보고합니다. 다음 절차에서는 이 충돌을 확인하고 해결하는 방법을 자세히 설명합니다.

게이트웨이 API 구현에 OSSM v3.x와 공존할 수 없는 OSSM v3.x가 필요하기 때문에 충돌이 발생합니다. CIO는 이 충돌을 감지하고, Gateway API 프로비저닝을 중지하고, `Degraded` 상태를 관리자에게 경고합니다.

사전 요구 사항

Cluster Operator는 `GatewayAPIOSSMConflict` 이유와 함께 `True` 상태 및 `Degraded` 유형을 보고합니다. 다음 명령을 실행하여 확인합니다.

```shell-session
$ oc get clusteroperator ingress -o yaml
```

출력의 상태 섹션에서 `status: "True" 및 reason: GatewayAPIOSSMConflict` 를 사용하여 `Degraded` 조건을 찾습니다.

```yaml
status:
  conditions:

    lastTransitionTime: "2025-10-22T17:00:00Z"

    message: 'Failed to install OpenShift Service Mesh 3.x for Gateway API: A
      conflicting OpenShift Service Mesh 2.x subscription was found. Remove the
      GatewayClass resource or the conflicting OSSM 2.x subscription to resolve.'
    reason: GatewayAPIOSSMConflict
    status: "True"
    type: Degraded
```

이 문제를 해결하고 `GatewayClass` 리소스를 제거하거나 Openshift Gateway API를 사용하여 클러스터에서 충돌하는 OpenShift Service Mesh v2.x 서브스크립션을 제거하여 `Degraded` 상태를 지우면 됩니다.

프로세스

OpenShift Gateway API를 사용하지 않으려면 `GatewayClass` 리소스를 제거합니다. Ingress Operator에서 게이트웨이 API 프로비저닝을 중지하라는 신호입니다.

```shell-session
$ oc delete gatewayclass <gatewayclass-name>
```

OpenShift Gateway API를 사용하려면 클러스터에서 충돌하는 OpenShift Service Mesh v2.x 서브스크립션을 제거해야 합니다.

```shell-session
$ oc -n openshift-operators delete subscription <OSSM v2.x subscription name>
```

v2.x 서브스크립션이 제거되면 Ingress Operator에서 OSSM v3.x 설치를 자동으로 재시도하고 게이트웨이 API 프로비저닝을 완료합니다.

추가 리소스

Ingress 컨트롤러 분할.

### 3.1. 로드 밸런서 서비스의 제한

RHOSP(Red Hat OpenStack Platform)의 OpenShift Container Platform 클러스터는 Octavia를 사용하여 로드 밸런서 서비스를 처리합니다. 이러한 선택으로 인해 이러한 클러스터에는 여러 가지 기능 제한이 있습니다.

RHOSP Octavia에는 Amphora 및 OVN의 두 가지 공급자가 있습니다. 이러한 공급자는 사용 가능한 기능과 구현 세부 사항에 따라 다릅니다. 이러한 차이점은 클러스터에서 생성된 로드 밸런서 서비스에 영향을 미칩니다.

#### 3.1.1. 로컬 외부 트래픽 정책

로드 밸런서 서비스에서 외부 트래픽 정책(ETP) 매개변수 `.spec.externalTrafficPolicy` 를 설정하여 서비스 끝점 Pod에 도달할 때 들어오는 트래픽의 소스 IP 주소를 유지할 수 있습니다. 그러나 클러스터가 Amphora Octavia 공급자를 사용하는 경우 트래픽의 소스 IP는 Amphora VM의 IP 주소로 교체됩니다.

클러스터가 OVN Octavia 공급자를 사용하는 경우 이 동작이 발생하지 않습니다.

`ETP` 옵션을 `Local` 로 설정하려면 로드 밸런서에 대한 상태 모니터를 생성해야 합니다. 상태 모니터 없이 트래픽을 기능적인 엔드포인트가 없는 노드로 라우팅할 수 있으므로 연결이 삭제됩니다.

Cloud Provider OpenStack에서 상태 모니터를 생성하도록 하려면 클라우드 공급자 구성에서 `create-monitor` 옵션 값을 `true` 로 설정해야 합니다.

RHOSP 16.2에서 OVN Octavia 공급자는 상태 모니터를 지원하지 않습니다. 따라서 ETP를 로컬로 설정하는 것은 지원되지 않습니다.

RHOSP 16.2에서 Amphora Octavia 공급자는 UDP 풀에서 HTTP 모니터를 지원하지 않습니다. 결과적으로 UDP 로드 밸런서 서비스에는 `UDP-CONNECT` 모니터가 대신 생성됩니다. 구현 세부 정보로 인해 이 구성은 OVN-Kubernetes CNI 플러그인에서만 제대로 작동합니다.

### 3.2. Octavia를 사용하여 애플리케이션 트래픽의 클러스터 확장

RHOSP(Red Hat OpenStack Platform)에서 실행되는 OpenShift Container Platform 클러스터는 Octavia 로드 밸런싱 서비스를 사용하여 여러 VM(가상 머신) 또는 유동 IP 주소에 트래픽을 배포할 수 있습니다. 이 기능을 사용하면 단일 머신 또는 주소가 생성하는 병목 현상이 완화됩니다.

애플리케이션 네트워크 확장에 사용하려면 자체 Octavia 로드 밸런서를 생성해야 합니다.

#### 3.2.1. Octavia를 사용하여 클러스터 스케일링

여러 API 로드 밸런서를 사용하려면 Octavia 로드 밸런서를 생성한 다음 이를 사용하도록 클러스터를 구성합니다.

사전 요구 사항

Octavia는 RHOSP(Red Hat OpenStack Platform) 배포에서 사용할 수 있습니다.

프로세스

명령줄에서 Amphora 드라이버를 사용하는 Octavia 로드 밸런서를 생성합니다.

```shell-session
$ openstack loadbalancer create --name API_OCP_CLUSTER --vip-subnet-id <id_of_worker_vms_subnet>
```

`API_OCP_CLUSTER` 대신 선택한 이름을 사용할 수 있습니다.

로드 밸런서가 활성화된 후 리스너를 생성합니다.

```shell-session
$ openstack loadbalancer listener create --name API_OCP_CLUSTER_6443 --protocol HTTPS--protocol-port 6443 API_OCP_CLUSTER
```

참고

로드 밸런서의 상태를 보려면 `openstack loadbalancer list` 를 입력합니다.

라운드 로빈 알고리즘을 사용하고 세션 지속성이 활성화된 풀을 생성합니다.

```shell-session
$ openstack loadbalancer pool create --name API_OCP_CLUSTER_pool_6443 --lb-algorithm ROUND_ROBIN --session-persistence type=<source_IP_address> --listener API_OCP_CLUSTER_6443 --protocol HTTPS
```

컨트롤 플레인 머신을 사용할 수 있도록 하려면 상태 모니터를 생성합니다.

```shell-session
$ openstack loadbalancer healthmonitor create --delay 5 --max-retries 4 --timeout 10 --type TCP API_OCP_CLUSTER_pool_6443
```

컨트롤 플레인 머신을 로드 밸런서 풀의 멤버로 추가합니다.

```shell-session
$ for SERVER in $(MASTER-0-IP MASTER-1-IP MASTER-2-IP)
do
  openstack loadbalancer member create --address $SERVER  --protocol-port 6443 API_OCP_CLUSTER_pool_6443
done
```

선택 사항: 클러스터 API 유동 IP 주소를 재사용하려면 설정을 해제합니다.

```shell-session
$ openstack floating ip unset $API_FIP
```

생성된 로드 밸런서 VIP에 설정되지 않은 `API_FIP` 또는 새 주소를 추가합니다.

```shell-session
$ openstack floating ip set  --port $(openstack loadbalancer show -c <vip_port_id> -f value API_OCP_CLUSTER) $API_FIP
```

이제 클러스터에서 로드 밸런싱에 Octavia를 사용합니다.

### 3.3. 사용자 관리 로드 밸런서의 서비스

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/external-load-balancer-default.png" alt="OpenShift Container Platform 환경에서 작동하는 Ingress 컨트롤러의 네트워크 워크플로 예제를 보여주는 이미지입니다." kind="diagram" diagram_type="semantic_diagram"]
OpenShift Container Platform 환경에서 작동하는 Ingress 컨트롤러의 네트워크 워크플로 예제를 보여주는 이미지입니다.
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/c35799e5c44cc8a51b928b5494bd9f84/external-load-balancer-default.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/external-load-balancer-openshift-api.png" alt="OpenShift Container Platform 환경에서 작동하는 OpenShift API의 네트워크 워크플로 예제를 보여주는 이미지입니다." kind="diagram" diagram_type="semantic_diagram"]
OpenShift Container Platform 환경에서 작동하는 OpenShift API의 네트워크 워크플로 예제를 보여주는 이미지입니다.
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/20b274ff0baf5743ab5f1a57d2dfdc40/external-load-balancer-openshift-api.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/external-load-balancer-machine-config-api.png" alt="OpenShift Container Platform 환경에서 작동하는 OpenShift MachineConfig API의 네트워크 워크플로 예제를 보여주는 이미지입니다." kind="diagram" diagram_type="semantic_diagram"]
OpenShift Container Platform 환경에서 작동하는 OpenShift MachineConfig API의 네트워크 워크플로 예제를 보여주는 이미지입니다.
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/647ca6d4bc4b5c847872ccda34e79ce5/external-load-balancer-machine-config-api.png`_


기본 로드 밸런서 대신 사용자 관리 로드 밸런서를 사용하도록 RHOSP(Red Hat OpenStack Platform)에서 OpenShift Container Platform 클러스터를 구성할 수 있습니다.

중요

사용자 관리 로드 밸런서 구성은 벤더의 로드 밸런서에 따라 다릅니다.

이 섹션의 정보와 예제는 지침용으로만 사용됩니다. 벤더의 로드 밸런서에 대한 자세한 내용은 벤더 설명서를 참조하십시오.

Red Hat은 사용자 관리 로드 밸런서에 대해 다음 서비스를 지원합니다.

Ingress 컨트롤러

OpenShift API

OpenShift MachineConfig API

사용자 관리 로드 밸런서에 대해 이러한 서비스 중 하나 또는 모두를 구성할지 여부를 선택할 수 있습니다. Ingress 컨트롤러 서비스만 구성하는 것은 일반적인 구성 옵션입니다. 각 서비스를 더 잘 이해하려면 다음 다이어그램을 참조하십시오.

그림 3.1. OpenShift Container Platform 환경에서 작동하는 Ingress 컨트롤러를 보여주는 네트워크 워크플로의 예

그림 3.2. OpenShift Container Platform 환경에서 작동하는 OpenShift API를 보여주는 네트워크 워크플로우의 예

그림 3.3. OpenShift Container Platform 환경에서 작동하는 OpenShift MachineConfig API를 보여주는 네트워크 워크플로우의 예

사용자 관리 로드 밸런서에 대해 지원되는 구성 옵션은 다음과 같습니다.

노드 선택기를 사용하여 Ingress 컨트롤러를 특정 노드 세트에 매핑합니다. 이 세트의 각 노드에 고정 IP 주소를 할당하거나 DHCP(Dynamic Host Configuration Protocol)에서 동일한 IP 주소를 수신하도록 각 노드를 구성해야 합니다. 인프라 노드는 일반적으로 이러한 유형의 구성을 수신합니다.

서브넷의 모든 IP 주소를 대상으로 지정합니다. 이 구성은 로드 밸런서 대상을 재구성하지 않고 해당 네트워크 내에서 노드를 생성하고 삭제할 수 있으므로 유지 관리 오버헤드를 줄일 수 있습니다. `/27` 또는 `/28` 과 같은 작은 네트워크에 머신 세트를 사용하여 Ingress Pod를 배포하는 경우 로드 밸런서 대상을 단순화할 수 있습니다.

작은 정보

머신 구성 풀의 리소스를 확인하여 네트워크에 존재하는 모든 IP 주소를 나열할 수 있습니다.

OpenShift Container Platform 클러스터에 대한 사용자 관리 로드 밸런서를 구성하기 전에 다음 정보를 고려하십시오.

프런트 엔드 IP 주소의 경우 프런트 엔드 IP 주소, Ingress 컨트롤러의 로드 밸런서 및 API 로드 밸런서에 동일한 IP 주소를 사용할 수 있습니다. 이 기능에 대해서는 벤더의 설명서를 확인하십시오.

백엔드 IP 주소의 경우 사용자 관리 로드 밸런서의 수명 동안 OpenShift Container Platform 컨트롤 플레인 노드의 IP 주소가 변경되지 않아야 합니다. 다음 작업 중 하나를 완료하여 이 작업을 수행할 수 있습니다.

각 컨트롤 플레인 노드에 고정 IP 주소를 할당합니다.

노드가 DHCP 리스를 요청할 때마다 DHCP에서 동일한 IP 주소를 수신하도록 각 노드를 구성합니다. 공급 업체에 따라 DHCP 리스를 IP 예약 또는 정적 DHCP 할당의 형태로 될 수 있습니다.

Ingress 컨트롤러 백엔드 서비스의 사용자 관리 로드 밸런서에서 Ingress 컨트롤러를 실행하는 각 노드를 수동으로 정의합니다. 예를 들어 Ingress 컨트롤러가 정의되지 않은 노드로 이동하는 경우 연결 중단이 발생할 수 있습니다.

#### 3.3.1. 사용자 관리 로드 밸런서 구성

기본 로드 밸런서 대신 사용자 관리 로드 밸런서를 사용하도록 RHOSP(Red Hat OpenStack Platform)에서 OpenShift Container Platform 클러스터를 구성할 수 있습니다.

중요

사용자 관리 로드 밸런서를 구성하기 전에 "사용자 관리 로드 밸런서의 서비스" 섹션을 읽으십시오.

사용자 관리 로드 밸런서에 대해 구성할 서비스에 적용되는 다음 사전 요구 사항을 읽으십시오.

참고

클러스터에서 실행되는 MetalLB는 사용자 관리 로드 밸런서로 작동합니다.

OpenShift API 사전 요구 사항

프런트 엔드 IP 주소를 정의했습니다.

TCP 포트 6443 및 22623은 로드 밸런서의 프런트 엔드 IP 주소에 노출됩니다. 다음 항목을 확인합니다.

포트 6443은 OpenShift API 서비스에 대한 액세스를 제공합니다.

포트 22623은 노드에 Ignition 시작 구성을 제공할 수 있습니다.

프런트 엔드 IP 주소와 포트 6443은 OpenShift Container Platform 클러스터 외부의 위치로 시스템의 모든 사용자가 연결할 수 있습니다.

프런트 엔드 IP 주소와 포트 22623은 OpenShift Container Platform 노드에서만 연결할 수 있습니다.

로드 밸런서 백엔드는 포트 6443 및 22623의 OpenShift Container Platform 컨트롤 플레인 노드와 통신할 수 있습니다.

Ingress 컨트롤러 사전 요구 사항

프런트 엔드 IP 주소를 정의했습니다.

TCP 포트 443 및 80은 로드 밸런서의 프런트 엔드 IP 주소에 노출됩니다.

프런트 엔드 IP 주소, 포트 80 및 포트 443은 OpenShift Container Platform 클러스터 외부에 있는 위치로 시스템의 모든 사용자가 연결할 수 있습니다.

프런트 엔드 IP 주소, 포트 80 및 포트 443은 OpenShift Container Platform 클러스터에서 작동하는 모든 노드에 연결할 수 있습니다.

로드 밸런서 백엔드는 포트 80, 443, 1936에서 Ingress 컨트롤러를 실행하는 OpenShift Container Platform 노드와 통신할 수 있습니다.

상태 점검 URL 사양의 사전 요구 사항

서비스를 사용할 수 없거나 사용할 수 없는지 결정하는 상태 점검 URL을 설정하여 대부분의 로드 밸런서를 구성할 수 있습니다. OpenShift Container Platform은 OpenShift API, 머신 구성 API 및 Ingress 컨트롤러 백엔드 서비스에 대한 이러한 상태 점검을 제공합니다.

다음 예제에서는 이전에 나열된 백엔드 서비스의 상태 점검 사양을 보여줍니다.

```shell-session
Path: HTTPS:6443/readyz
Healthy threshold: 2
Unhealthy threshold: 2
Timeout: 10
Interval: 10
```

```shell-session
Path: HTTPS:22623/healthz
Healthy threshold: 2
Unhealthy threshold: 2
Timeout: 10
Interval: 10
```

```shell-session
Path: HTTP:1936/healthz/ready
Healthy threshold: 2
Unhealthy threshold: 2
Timeout: 5
Interval: 10
```

프로세스

포트 6443, 22623, 443 및 80의 로드 밸런서에서 클러스터에 액세스할 수 있도록 HAProxy Ingress 컨트롤러를 구성합니다. 필요에 따라 HAProxy 구성에 있는 여러 서브넷의 IP 주소 또는 단일 서브넷의 IP 주소를 지정할 수 있습니다.

```shell-session
# ...
listen my-cluster-api-6443
    bind 192.168.1.100:6443
    mode tcp
    balance roundrobin
  option httpchk
  http-check connect
  http-check send meth GET uri /readyz
  http-check expect status 200
    server my-cluster-master-2 192.168.1.101:6443 check inter 10s rise 2 fall 2
    server my-cluster-master-0 192.168.1.102:6443 check inter 10s rise 2 fall 2
    server my-cluster-master-1 192.168.1.103:6443 check inter 10s rise 2 fall 2

listen my-cluster-machine-config-api-22623
    bind 192.168.1.100:22623
    mode tcp
    balance roundrobin
  option httpchk
  http-check connect
  http-check send meth GET uri /healthz
  http-check expect status 200
    server my-cluster-master-2 192.168.1.101:22623 check inter 10s rise 2 fall 2
    server my-cluster-master-0 192.168.1.102:22623 check inter 10s rise 2 fall 2
    server my-cluster-master-1 192.168.1.103:22623 check inter 10s rise 2 fall 2

listen my-cluster-apps-443
    bind 192.168.1.100:443
    mode tcp
    balance roundrobin
  option httpchk
  http-check connect
  http-check send meth GET uri /healthz/ready
  http-check expect status 200
    server my-cluster-worker-0 192.168.1.111:443 check port 1936 inter 10s rise 2 fall 2
    server my-cluster-worker-1 192.168.1.112:443 check port 1936 inter 10s rise 2 fall 2
    server my-cluster-worker-2 192.168.1.113:443 check port 1936 inter 10s rise 2 fall 2

listen my-cluster-apps-80
   bind 192.168.1.100:80
   mode tcp
   balance roundrobin
  option httpchk
  http-check connect
  http-check send meth GET uri /healthz/ready
  http-check expect status 200
    server my-cluster-worker-0 192.168.1.111:80 check port 1936 inter 10s rise 2 fall 2
    server my-cluster-worker-1 192.168.1.112:80 check port 1936 inter 10s rise 2 fall 2
    server my-cluster-worker-2 192.168.1.113:80 check port 1936 inter 10s rise 2 fall 2
# ...
```

```shell-session
# ...
listen api-server-6443
    bind *:6443
    mode tcp
      server master-00 192.168.83.89:6443 check inter 1s
      server master-01 192.168.84.90:6443 check inter 1s
      server master-02 192.168.85.99:6443 check inter 1s
      server bootstrap 192.168.80.89:6443 check inter 1s

listen machine-config-server-22623
    bind *:22623
    mode tcp
      server master-00 192.168.83.89:22623 check inter 1s
      server master-01 192.168.84.90:22623 check inter 1s
      server master-02 192.168.85.99:22623 check inter 1s
      server bootstrap 192.168.80.89:22623 check inter 1s

listen ingress-router-80
    bind *:80
    mode tcp
    balance source
      server worker-00 192.168.83.100:80 check inter 1s
      server worker-01 192.168.83.101:80 check inter 1s

listen ingress-router-443
    bind *:443
    mode tcp
    balance source
      server worker-00 192.168.83.100:443 check inter 1s
      server worker-01 192.168.83.101:443 check inter 1s

listen ironic-api-6385
    bind *:6385
    mode tcp
    balance source
      server master-00 192.168.83.89:6385 check inter 1s
      server master-01 192.168.84.90:6385 check inter 1s
      server master-02 192.168.85.99:6385 check inter 1s
      server bootstrap 192.168.80.89:6385 check inter 1s

listen inspector-api-5050
    bind *:5050
    mode tcp
    balance source
      server master-00 192.168.83.89:5050 check inter 1s
      server master-01 192.168.84.90:5050 check inter 1s
      server master-02 192.168.85.99:5050 check inter 1s
      server bootstrap 192.168.80.89:5050 check inter 1s
# ...
```

다음 명령CLI 명령을 사용하여 사용자 관리 로드 밸런서 및 해당 리소스가 작동하는지 확인합니다.

```shell
curl
```

다음 명령을 실행하고 응답을 관찰하여 Kubernetes API 서버 리소스에서 클러스터 머신 구성 API에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl https://<loadbalancer_ip_address>:6443/version --insecure
```

구성이 올바르면 응답으로 JSON 오브젝트가 표시됩니다.

```plaintext
{
  "major": "1",
  "minor": "11+",
  "gitVersion": "v1.11.0+ad103ed",
  "gitCommit": "ad103ed",
  "gitTreeState": "clean",
  "buildDate": "2019-01-09T06:44:10Z",
  "goVersion": "go1.10.3",
  "compiler": "gc",
  "platform": "linux/amd64"
}
```

다음 명령을 실행하고 출력을 관찰하여 클러스터 머신 구성 API에 머신 구성 서버 리소스에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl -v https://<loadbalancer_ip_address>:22623/healthz --insecure
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 200 OK
Content-Length: 0
```

다음 명령을 실행하고 출력을 관찰하여 포트 80의 Ingress 컨트롤러 리소스에서 컨트롤러에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl -I -L -H "Host: console-openshift-console.apps.<cluster_name>.<base_domain>" http://<load_balancer_front_end_IP_address>
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 302 Found
content-length: 0
location: https://console-openshift-console.apps.ocp4.private.opequon.net/
cache-control: no-cache
```

다음 명령을 실행하고 출력을 관찰하여 포트 443의 Ingress 컨트롤러 리소스에서 컨트롤러에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl -I -L --insecure --resolve console-openshift-console.apps.<cluster_name>.<base_domain>:443:<Load Balancer Front End IP Address> https://console-openshift-console.apps.<cluster_name>.<base_domain>
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 200 OK
referrer-policy: strict-origin-when-cross-origin
set-cookie: csrf-token=UlYWOyQ62LWjw2h003xtYSKlh1a0Py2hhctw0WmV2YEdhJjFyQwWcGBsja261dGLgaYO0nxzVErhiXt6QepA7g==; Path=/; Secure; SameSite=Lax
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-frame-options: DENY
x-xss-protection: 1; mode=block
date: Wed, 04 Oct 2023 16:29:38 GMT
content-type: text/html; charset=utf-8
set-cookie: 1e2670d92730b515ce3a1bb65da45062=1bf5e9573c9a2760c964ed1659cc1673; path=/; HttpOnly; Secure; SameSite=None
cache-control: private
```

사용자 관리 로드 밸런서의 프런트 엔드 IP 주소를 대상으로 하도록 클러스터의 DNS 레코드를 구성합니다. 로드 밸런서를 통해 클러스터 API 및 애플리케이션의 DNS 서버로 레코드를 업데이트해야 합니다.

```plaintext
<load_balancer_ip_address>  A  api.<cluster_name>.<base_domain>
A record pointing to Load Balancer Front End
```

```plaintext
<load_balancer_ip_address>   A apps.<cluster_name>.<base_domain>
A record pointing to Load Balancer Front End
```

중요

DNS 전파는 각 DNS 레코드를 사용할 수 있을 때까지 약간의 시간이 걸릴 수 있습니다. 각 레코드를 검증하기 전에 각 DNS 레코드가 전파되는지 확인합니다.

OpenShift Container Platform 클러스터가 사용자 관리 로드 밸런서를 사용하려면 클러스터의 `install-config.yaml` 파일에 다음 구성을 지정해야 합니다.

```yaml
# ...
platform:
  openstack:
    loadBalancer:
      type: UserManaged
    apiVIPs:
    - <api_ip>
    ingressVIPs:
    - <ingress_ip>
# ...
```

1. `type` 매개변수에 대해 `UserManaged` 를 설정하여 클러스터의 사용자 관리 로드 밸런서를 지정합니다. 매개변수의 기본값은 기본 내부 로드 밸런서를 나타내는 `OpenShiftManagedDefault` 입니다.

`openshift-kni-infra` 네임스페이스에 정의된 서비스의 경우 사용자 관리 로드 밸런서는 `coredns` 서비스를 클러스터의 Pod에 배포할 수 있지만 `keepalived` 및 `haproxy` 서비스를 무시합니다.

2. 사용자 관리 로드 밸런서를 지정할 때 필수 매개변수입니다. Kubernetes API가 사용자 관리 로드 밸런서와 통신할 수 있도록 사용자 관리 로드 밸런서의 공용 IP 주소를 지정합니다.

3. 사용자 관리 로드 밸런서를 지정할 때 필수 매개변수입니다. 사용자 관리 로드 밸런서에서 클러스터의 인그레스 트래픽을 관리할 수 있도록 사용자 관리 로드 밸런서의 공용 IP 주소를 지정합니다.

검증

다음 명령CLI 명령을 사용하여 사용자 관리 로드 밸런서 및 DNS 레코드 구성이 작동하는지 확인합니다.

```shell
curl
```

다음 명령을 실행하고 출력을 관찰하여 클러스터 API에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl https://api.<cluster_name>.<base_domain>:6443/version --insecure
```

구성이 올바르면 응답으로 JSON 오브젝트가 표시됩니다.

```plaintext
{
  "major": "1",
  "minor": "11+",
  "gitVersion": "v1.11.0+ad103ed",
  "gitCommit": "ad103ed",
  "gitTreeState": "clean",
  "buildDate": "2019-01-09T06:44:10Z",
  "goVersion": "go1.10.3",
  "compiler": "gc",
  "platform": "linux/amd64"
  }
```

다음 명령을 실행하고 출력을 관찰하여 클러스터 머신 구성에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl -v https://api.<cluster_name>.<base_domain>:22623/healthz --insecure
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 200 OK
Content-Length: 0
```

다음 명령을 실행하고 출력을 관찰하여 포트의 각 클러스터 애플리케이션에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl http://console-openshift-console.apps.<cluster_name>.<base_domain> -I -L --insecure
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 302 Found
content-length: 0
location: https://console-openshift-console.apps.<cluster-name>.<base domain>/
cache-control: no-cacheHTTP/1.1 200 OK
referrer-policy: strict-origin-when-cross-origin
set-cookie: csrf-token=39HoZgztDnzjJkq/JuLJMeoKNXlfiVv2YgZc09c3TBOBU4NI6kDXaJH1LdicNhN1UsQWzon4Dor9GWGfopaTEQ==; Path=/; Secure
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-frame-options: DENY
x-xss-protection: 1; mode=block
date: Tue, 17 Nov 2020 08:42:10 GMT
content-type: text/html; charset=utf-8
set-cookie: 1e2670d92730b515ce3a1bb65da45062=9b714eb87e93cf34853e87a92d6894be; path=/; HttpOnly; Secure; SameSite=None
cache-control: private
```

다음 명령을 실행하고 출력을 관찰하여 포트 443에서 각 클러스터 애플리케이션에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl https://console-openshift-console.apps.<cluster_name>.<base_domain> -I -L --insecure
```

구성이 올바르면 명령의 출력에 다음 응답이 표시됩니다.

```shell-session
HTTP/1.1 200 OK
referrer-policy: strict-origin-when-cross-origin
set-cookie: csrf-token=UlYWOyQ62LWjw2h003xtYSKlh1a0Py2hhctw0WmV2YEdhJjFyQwWcGBsja261dGLgaYO0nxzVErhiXt6QepA7g==; Path=/; Secure; SameSite=Lax
x-content-type-options: nosniff
x-dns-prefetch-control: off
x-frame-options: DENY
x-xss-protection: 1; mode=block
date: Wed, 04 Oct 2023 16:29:38 GMT
content-type: text/html; charset=utf-8
set-cookie: 1e2670d92730b515ce3a1bb65da45062=1bf5e9573c9a2760c964ed1659cc1673; path=/; HttpOnly; Secure; SameSite=None
cache-control: private
```

### 3.4. Ingress 컨트롤러에서 유동 IP 주소 지정

기본적으로 유동 IP 주소는 배포 시 RHOSP(Red Hat OpenStack Platform)의 OpenShift Container Platform 클러스터에 무작위로 할당됩니다. 이 유동 IP 주소는 Ingress 포트와 연결됩니다.

DNS 레코드 및 클러스터 배포를 업데이트하기 전에 유동 IP 주소를 사전 생성해야 할 수 있습니다. 이 경우 Ingress 컨트롤러에 유동 IP 주소를 정의할 수 있습니다. Octavia 사용 여부 또는 사용자 관리 클러스터와 관계없이 이 작업을 수행할 수 있습니다.

절차

유동 IP를 사용하여 Ingress 컨트롤러 CR(사용자 정의 리소스) 파일을 생성합니다.

```yaml
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  namespace: openshift-ingress-operator
  name: <name>
spec:
  domain: <domain>
  endpointPublishingStrategy:
    type: LoadBalancerService
    loadBalancer:
      scope: External
      providerParameters:
        type: OpenStack
        openstack:
          floatingIP: <ingress_port_IP>
```

1. Ingress 컨트롤러의 이름입니다. 기본 Ingress 컨트롤러를 사용하는 경우 이 필드의 값은 `기본값` 입니다.

2. Ingress 컨트롤러에서 제공하는 DNS 이름입니다.

3. 유동 IP 주소를 사용하려면 범위를 `External` 으로 설정해야 합니다.

4. Ingress 컨트롤러가 수신 대기 중인 포트와 연결된 유동 IP 주소입니다.

다음 명령을 실행하여 CR 파일을 적용합니다.

```shell-session
$ oc apply -f sample-ingress.yaml
```

Ingress 컨트롤러 끝점을 사용하여 DNS 레코드를 업데이트합니다.

```plaintext
*.apps.<name>.<domain>. IN A <ingress_port_IP>
```

OpenShift Container Platform 클러스터 생성을 계속합니다.

검증

다음 명령을 사용하여 `IngressController` 조건을 확인하여 로드 밸런서가 성공적으로 프로비저닝되었는지 확인합니다.

```shell-session
$ oc get ingresscontroller -n openshift-ingress-operator <name> -o jsonpath="{.status.conditions}" | yq -PC
```

### 4.1. MetalLB 주소 풀 구성

클러스터 관리자는 주소 풀을 추가, 수정, 삭제할 수 있습니다. MetalLB Operator는 주소 풀 사용자 정의 리소스를 사용하여 MetalLB에서 서비스에 할당할 수 있는 IP 주소를 설정합니다. 예제에 사용되는 네임스페이스는 네임스페이스가 `metallb-system` 이라고 가정합니다.

MetalLB Operator를 설치하는 방법에 대한 자세한 내용은 MetalLB 및 MetalLB Operator 정보를 참조하십시오.

#### 4.1.1. IPAddressPool 사용자 정의 리소스 정보

`IPAddressPool` 사용자 정의 리소스의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | 주소 풀의 이름을 지정합니다. 서비스를 추가할 때 `metallb.io/address-pool` 주석에 이 풀 이름을 지정하여 특정 풀에서 IP 주소를 선택할 수 있습니다. 문서 전체에서 `doc-example` , `silver` , `gold` 라는 이름이 사용됩니다. |
| `metadata.namespace` | `string` | 주소 풀의 네임스페이스를 지정합니다. MetalLB Operator에서 사용하는 동일한 네임스페이스를 지정합니다. |
| `metadata.label` | `string` | 선택 사항: `IPAddressPool` 에 할당된 키 값 쌍을 지정합니다. 이는 `IPAddressPool` 을 광고와 연결하기 위해 `BGPAdvertisement` 및 `L2Advertisement` CRD의 `ipAddressPoolSelectors` 에서 참조할 수 있습니다. |
| `spec.addresses` | `string` | 서비스에 할당할 MetalLB Operator의 IP 주소 목록을 지정합니다. 단일 풀에서 여러 범위를 지정할 수 있으며 모두 동일한 설정을 공유합니다. CIDR 표기법에서 각 범위를 지정하거나 하이픈으로 구분된 시작 및 끝 IP 주소로 지정합니다. |
| `spec.autoAssign` | `boolean` | 선택 사항: MetalLB에서 이 풀에서 IP 주소를 자동으로 할당하는지 여부를 지정합니다. `metallb.io/address-pool` 주석을 사용하여 이 풀에서 IP 주소를 명시적으로 요청하려면 `false` 를 지정합니다. 기본값은 `true` 입니다. 참고 IP 주소 풀 구성의 경우 address 필드가 `autoAssign` 이 활성화된 경우 충돌을 방지하기 위해 다른 네트워크 장치, 특히 게이트웨이 주소에서 사용할 수 있고 사용하지 않는 IP만 지정했는지 확인합니다. |
| `spec.avoidBuggyIPs` | `boolean` | 선택 사항: IP 주소가 `.0` 및 `.255` 로 끝나는 경우 풀에서 할당되지 않도록 합니다. 기본값은 `false` 입니다. 일부 이전 소비자 네트워크 장치는 `.0` 및 `.255` 로 끝나는 IP 주소를 실수로 차단합니다. |

`spec.serviceAllocation` 사양을 구성하여 `IPAddressPool` 의 IP 주소를 서비스 및 네임스페이스에 할당할 수 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `priority` | `int` | 선택 사항: 두 개 이상의 IP 주소 풀이 서비스 또는 네임스페이스와 일치하는 경우 IP 주소 풀 간의 우선 순위를 정의합니다. 더 낮은 숫자는 더 높은 우선 순위를 나타냅니다. |
| `네임스페이스` | `배열(문자열)` | 선택 사항: IP 주소 풀의 IP 주소에 할당할 수 있는 네임스페이스 목록을 지정합니다. |
| `namespaceSelectors` | `array (LabelSelector)` | 선택 사항: 목록 형식의 라벨 선택기를 사용하여 IP 주소 풀에서 IP 주소에 할당할 수 있는 네임스페이스 레이블을 지정합니다. |
| `serviceSelectors` | `array (LabelSelector)` | 선택 사항: 목록 형식의 라벨 선택기를 사용하여 주소 풀에서 IP 주소에 할당할 수 있는 서비스 레이블을 지정합니다. |

#### 4.1.2. 주소 풀 구성

클러스터 관리자는 클러스터에 주소 풀을 추가하여 MetalLB에서 로드 밸런서 서비스에 할당할 수 있는 IP 주소를 제어할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example
  labels:
    zone: east
spec:
  addresses:
  - 203.0.113.1-203.0.113.10
  - 203.0.113.65-203.0.113.75
# ...
```

1. `IPAddressPool` 에 할당된 이 레이블은 `BGPAdvertisement` CRD의 `ipAddressPoolSelectors` 에서 참조하여 `IPAddressPool` 을 광고와 연결할 수 있습니다.

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

검증

다음 명령을 입력하여 주소 풀을 확인합니다.

```shell-session
$ oc describe -n metallb-system IPAddressPool doc-example
```

```shell-session
Name:         doc-example
Namespace:    metallb-system
Labels:       zone=east
Annotations:  <none>
API Version:  metallb.io/v1beta1
Kind:         IPAddressPool
Metadata:
  ...
Spec:
  Addresses:
    203.0.113.1-203.0.113.10
    203.0.113.65-203.0.113.75
  Auto Assign:  true
Events:         <none>
```

주소 풀 이름(예: `doc-example`) 및 IP 주소 범위가 출력에 있는지 확인합니다.

#### 4.1.3. VLAN의 MetalLB 주소 풀 구성

클러스터 관리자는 클러스터에 주소 풀을 추가하여 MetalLB에서 로드 밸런서 서비스에 할당할 수 있는 생성된 VLAN의 IP 주소를 제어할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

별도의 VLAN을 구성합니다.

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

다음 예와 유사한 `ipaddresspool-vlan.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-vlan
  labels:
    zone: east
spec:
  addresses:
  - 192.168.100.1-192.168.100.254
```

1. `IPAddressPool` 에 할당된 이 레이블은 `BGPAdvertisement` CRD의 `ipAddressPoolSelectors` 에서 참조하여 `IPAddressPool` 을 광고와 연결할 수 있습니다.

2. 이 IP 범위는 네트워크의 VLAN에 할당된 서브넷과 일치해야 합니다. 계층 2(L2) 모드를 지원하려면 IP 주소 범위가 클러스터 노드와 동일한 서브넷에 있어야 합니다.

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool-vlan.yaml
```

이 구성이 VLAN에 적용되도록 하려면 `사양`

`gatewayConfig.ipForwarding` 을 `Global` 로 설정해야 합니다.

다음 명령을 실행하여 네트워크 구성 CR(사용자 정의 리소스)을 편집합니다.

```shell-session
$ oc edit network.operator.openshift/cluster
```

`gatewayConfig.ipForwarding` 을 `Global` 로 설정하도록 `spec.defaultNetwork.ovnKubernetesConfig` 섹션을 업데이트합니다. 다음과 같이 표시됩니다.

```yaml
...
spec:
  clusterNetwork:
    - cidr: 10.128.0.0/14
      hostPrefix: 23
  defaultNetwork:
    type: OVNKubernetes
    ovnKubernetesConfig:
      gatewayConfig:
        ipForwarding: Global
...
```

#### 4.1.4. 주소 풀 구성의 예

다음 예제에서는 특정 시나리오에 대한 주소 풀 구성을 보여줍니다.

#### 4.1.4.1. 예: IPv4 및 CIDR 범위

CIDR(Classless inter-domain routing) 표기법으로 IP 주소 범위를 지정할 수 있습니다. 하이픈을 사용하는 표기법과 CIDR 표기법을 결합하여 하한 및 상한을 분리할 수 있습니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: doc-example-cidr
  namespace: metallb-system
spec:
  addresses:
  - 192.168.100.0/24
  - 192.168.200.0/24
  - 192.168.255.1-192.168.255.5
# ...
```

#### 4.1.4.2. 예: IP 주소 할당

MetalLB가 주소 풀에서 IP 주소를 자동으로 할당하지 못하도록 `autoAssign` 필드를 `false` 로 설정할 수 있습니다. 그런 다음 IP 주소 풀에서 단일 IP 주소 또는 여러 IP 주소를 할당할 수 있습니다.

IP 주소를 할당하려면 `spec.addresses` 매개변수의 대상 IP 주소에 `/32` CIDR 표기법을 추가합니다. 이 설정은 특정 IP 주소만 할당에 사용할 수 있도록 하여 예약되지 않은 IP 주소만 애플리케이션을 사용할 수 있도록 합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: doc-example-reserved
  namespace: metallb-system
spec:
  addresses:
  - 192.168.100.1/32
  - 192.168.200.1/32
  autoAssign: false
# ...
```

참고

서비스를 추가할 때 주소 풀에서 특정 IP 주소를 요청하거나 주석에 풀 이름을 지정하여 풀에서 IP 주소를 요청할 수 있습니다.

#### 4.1.4.3. 예: IPv4 및 IPv6 주소

IPv4 및 IPv6을 사용하는 주소 풀을 추가할 수 있습니다. 여러 IPv4 예제와 마찬가지로 `address` 목록에 여러 범위를 지정할 수 있습니다.

서비스에 단일 IPv4 주소, 단일 IPv6 주소 또는 둘 다에 할당되었는지 여부는 서비스 추가 방법에 따라 결정됩니다. `spec.ipFamilies` 및 `spec.ipFamilyPolicy` 필드는 서비스에 IP 주소를 할당하는 방법을 제어합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: doc-example-combined
  namespace: metallb-system
spec:
  addresses:
  - 10.0.100.0/28
  - 2002:2:2::1-2002:2:2::100
# ...
```

1. 여기서 `10.0.100.0/28` 은 로컬 네트워크 IP 주소 뒤에 `/28` 네트워크 접두사가 있습니다.

#### 4.1.4.4. 예: 서비스 또는 네임스페이스에 IP 주소 풀 할당

`IPAddressPool` 의 IP 주소를 지정한 서비스 및 네임스페이스에 할당할 수 있습니다.

둘 이상의 IP 주소 풀에 서비스 또는 네임스페이스를 할당하는 경우 MetalLB는 우선순위가 높은 IP 주소 풀에서 사용 가능한 IP 주소를 사용합니다. 우선 순위가 높은 할당된 IP 주소 풀에서 사용할 수 있는 IP 주소가 없는 경우 MetalLB는 우선 순위가 낮거나 우선순위가 없는 IP 주소 풀의 사용 가능한 IP 주소를 사용합니다.

참고

`matchLabels` 라벨 선택기, `matchExpressions` 라벨 선택기 또는 둘 다 `namespaceSelectors` 및 `serviceSelectors` 사양에 사용할 수 있습니다. 이 예제에서는 각 사양에 대한 하나의 라벨 선택기를 보여줍니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: doc-example-service-allocation
  namespace: metallb-system
spec:
  addresses:
    - 192.168.20.0/24
  serviceAllocation:
    priority: 50
    namespaces:
      - namespace-a
      - namespace-b
    namespaceSelectors:
      - matchLabels:
          zone: east
    serviceSelectors:
      - matchExpressions:
        - key: security
          operator: In
          values:
          - S1
# ...
```

1. 주소 풀에 우선순위를 할당합니다. 더 낮은 숫자는 더 높은 우선 순위를 나타냅니다.

2. 목록 형식의 IP 주소 풀에 하나 이상의 네임스페이스를 할당합니다.

3. 목록 형식의 라벨 선택기를 사용하여 IP 주소 풀에 하나 이상의 네임스페이스 레이블을 할당합니다.

4. 목록 형식의 라벨 선택기를 사용하여 IP 주소 풀에 하나 이상의 서비스 레이블을 할당합니다.

#### 4.1.5. 다음 단계

L2 광고 및 라벨을 사용하여 MetalLB 구성

MetalLB BGP 피어 구성

MetalLB를 사용하도록 서비스 구성

### 4.2. IP 주소 풀에 대한 알림 정보

IP 주소가 계층 2 프로토콜, BGP 프로토콜 또는 둘 다와 함께 알리도록 MetalLB를 구성할 수 있습니다. 계층 2를 사용하면 MetalLB에서 내결함성 외부 IP 주소를 제공합니다. BGP를 사용하면 MetalLB에서 외부 IP 주소 및 로드 밸런싱에 대한 내결함성을 제공합니다.

MetalLB는 동일한 IP 주소 세트에 대해 L2 및 BGP를 사용한 광고를 지원합니다.

MetalLB는 특정 BGP 피어에 주소 풀을 네트워크의 노드 하위 집합에 효과적으로 할당할 수 있는 유연성을 제공합니다. 이를 통해 더 복잡한 구성(예: 노드 분리 또는 네트워크의 세그먼트화)이 가능합니다.

#### 4.2.1. BGPAdvertisement 사용자 정의 리소스 정보

`BGPAdvertisements` 오브젝트의 필드는 다음 표에 정의되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | BGP 광고의 이름을 지정합니다. |
| `metadata.namespace` | `string` | BGP 광고의 네임스페이스를 지정합니다. MetalLB Operator에서 사용하는 동일한 네임스페이스를 지정합니다. |
| `spec.aggregationLength` | `integer` | 선택 사항: 32비트 CIDR 마스크에 포함할 비트 수를 지정합니다. 발표자가 BGP 피어에 알리는 경로를 집계하기 위해 마스크는 여러 서비스 IP 주소의 경로에 적용되고 발표자는 집계된 경로를 알립니다. 예를 들어 집계 길이가 `24` 인 경우 speaker는 여러 `10.0.1.x/32` 서비스 IP 주소를 집계하고 단일 `10.0.1.0/24` 경로를 알릴 수 있습니다. |
| `spec.aggregationLengthV6` | `integer` | 선택 사항: 128비트 CIDR 마스크에 포함할 비트 수를 지정합니다. 예를 들어 집계 길이가 `124` 인 경우 speaker는 여러 `fc00:f853:0ccd:e799::x/128` 서비스 IP 주소를 집계하고 단일 `fc00:f853:0ccd:e799::0/124` 경로를 알릴 수 있습니다. |
| `spec.communities` | `string` | 선택 사항: 하나 이상의 BGP 커뮤니티를 지정합니다. 각 커뮤니티는 콜론 문자로 구분된 두 개의 16비트 값으로 지정됩니다. 잘 알려진 커뮤니티는 16비트 값으로 지정해야 합니다. `NO_EXPORT` : `65535:65281` `NO_ADVERTISE` : `65535:65282` `NO_EXPORT_SUBCONFED` : `65535:65283` 참고 문자열과 함께 생성된 커뮤니티 오브젝트를 사용할 수도 있습니다. |
| `spec.localPref` | `integer` | 선택 사항: 이 광고의 로컬 기본 설정을 지정합니다. 이 BGP 속성은 Autonomous System 내의 BGP 세션에 적용됩니다. |
| `spec.ipAddressPools` | `string` | 선택 사항: 이 광고와 함께 광고할 `IPAddressPools` 목록입니다. 이름별로 선택됩니다. |
| `spec.ipAddressPoolSelectors` | `string` | 선택 사항: 이 광고와 함께 광고되는 `IPAddressPool` 에 대한 선택기입니다. `IPAddressPool` 을 이름 자체 대신 `IPAddressPool` 에 할당된 레이블을 기반으로 광고에 연결하기 위한 것입니다. 이 또는 목록에 의해 선택된 `IPAddressPool` 이 없는 경우, 광고는 모든 `IPAddressPools` 에 적용됩니다. |
| `spec.nodeSelectors` | `string` | 선택 사항: `NodeSelectors` 를 사용하면 로드 밸런서 IP의 다음 홉으로 노드를 알릴 수 있습니다. 비어있는 경우 모든 노드가 다음 홉으로 발표됩니다. |
| `spec.peers` | `string` | 선택 사항: 목록을 사용하여 MetalLB 서비스 IP 주소에 대한 알림을 수신하는 각 `BGPPeer` 리소스의 `metadata.name` 값을 지정합니다. MetalLB 서비스 IP 주소는 IP 주소 풀에서 할당됩니다. 기본적으로 MetalLB 서비스 IP 주소는 구성된 모든 `BGPPeer` 리소스에 알립니다. 이 필드를 사용하여 특정 `BGPpeer` 리소스로 광고를 제한합니다. |

#### 4.2.2. BGP 광고 및 기본 사용 사례를 사용하여 MetalLB 구성

피어 BGP 라우터가 `203.0.113.200/32` 경로를 수신하고 MetalLB에서 서비스에 할당하는 각 로드 밸런서 IP 주소에 대해 `fc00:f853:ccd:e799::1/128` 경로를 수신하도록 MetalLB를 다음과 같이 구성합니다.

`localPref` 및 community 필드를 지정하지 않으므로 `localPref` 가 0으로 설정되고 BGP 커뮤니티가 없는 상태에서 경로가 광고됩니다.

#### 4.2.2.1. 예: BGP를 사용하여 기본 주소 풀 구성 알림

`IPAddressPool` 이 BGP 프로토콜과 함께 알리도록 다음과 같이 MetalLB를 구성합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-bgp-basic
spec:
  addresses:
    - 203.0.113.200/30
    - fc00:f853:ccd:e799::/124
```

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

BGP 광고를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgpadvertisement-basic
  namespace: metallb-system
spec:
  ipAddressPools:
  - doc-example-bgp-basic
```

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement.yaml
```

#### 4.2.3. BGP 광고 및 고급 사용 사례를 사용하여 MetalLB 구성

MetalLB가 `203.0.113.200` 과 `203.0.113.203` 사이의 범위에서 로드 밸런서 서비스에 IP 주소를 할당하고 `fc00:f853:ccd:e799::0` 및 `fc00:f853:ccd:e799::f`.

두 개의 BGP 알림을 설명하려면 MetalLB에서 `203.0.113.200` 의 IP 주소를 서비스에 할당할 때 인스턴스를 고려하십시오. 이 IP 주소를 예로 들어, 발표자는 BGP 피어에 두 경로를 알립니다.

`203.0.113.200/32`, `localPref` 가 `100` 으로 설정되고 커뮤니티는 `NO_ADVERTISE` 커뮤니티의 숫자 값으로 설정됩니다. 이 사양은 피어 라우터에 이 경로를 사용할 수 있지만 이 경로에 대한 정보를 BGP 피어로 전파해서는 안 됩니다.

`203.0.113.200/30` 은 MetalLB에서 할당한 로드 밸런서 IP 주소를 단일 경로로 집계합니다. MetalLB는 `8000:800` 으로 설정된 커뮤니티 특성을 사용하여 집계된 경로를 BGP 피어로 알립니다.

BGP 피어는 `203.0.113.200/30` 경로를 다른 BGP 피어에 전파합니다. 트래픽이 speaker가 있는 노드로 라우팅되는 경우 `203.0.113.200/32` 경로는 트래픽을 클러스터로 전달하고 서비스와 연결된 Pod에 사용됩니다.

더 많은 서비스를 추가하고 MetalLB는 풀에서 더 많은 로드 밸런서 IP 주소를 할당하면 피어 라우터는 각 서비스에 대해 하나의 로컬 경로와 `203.0.113.200/30` 집계 경로를 수신합니다. 추가하는 각 서비스는 `/30` 경로를 생성하지만 MetalLB는 피어 라우터와 통신하기 전에 경로를 하나의 BGP 광고에 중복시킵니다.

#### 4.2.3.1. 예: BGP를 사용하여 고급 주소 풀 구성 알림

`IPAddressPool` 이 BGP 프로토콜과 함께 알리도록 다음과 같이 MetalLB를 구성합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-bgp-adv
  labels:
    zone: east
spec:
  addresses:
    - 203.0.113.200/30
    - fc00:f853:ccd:e799::/124
  autoAssign: false
```

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

BGP 광고를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement1.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgpadvertisement-adv-1
  namespace: metallb-system
spec:
  ipAddressPools:
    - doc-example-bgp-adv
  communities:
    - 65535:65282
  aggregationLength: 32
  localPref: 100
```

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement1.yaml
```

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement2.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgpadvertisement-adv-2
  namespace: metallb-system
spec:
  ipAddressPools:
    - doc-example-bgp-adv
  communities:
    - 8000:800
  aggregationLength: 30
  aggregationLengthV6: 124
```

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement2.yaml
```

#### 4.2.4. 노드의 하위 집합에서 IP 주소 풀 광고

특정 노드 세트에서만 IP 주소 풀에서 IP 주소를 알리려면 BGPAdvertisement 사용자 정의 리소스에서 `.spec.nodeSelector` 사양을 사용합니다. 이 사양은 IP 주소 풀을 클러스터의 노드 집합과 연결합니다. 이는 클러스터의 다른 서브넷에 노드가 있고 특정 서브넷의 주소 풀에서 IP 주소를 알립니다(예: 공용 서브넷만 해당).

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

사용자 정의 리소스를 사용하여 IP 주소 풀을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: pool1
spec:
  addresses:
    - 4.4.4.100-4.4.4.200
    - 2001:100:4::200-2001:100:4::400
```

BGPAdvertisement 사용자 정의 리소스에서 `.spec.nodeSelector` 값을 정의하여 클러스터의 IP 주소를 알릴 노드를 제어합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: example
spec:
  ipAddressPools:
  - pool1
  nodeSelector:
  - matchLabels:
      kubernetes.io/hostname: NodeA
  - matchLabels:
      kubernetes.io/hostname: NodeB
```

이 예에서 `pool1` 의 IP 주소는 `NodeA` 및 `NodeB` 에서만 알립니다.

#### 4.2.5. L2Advertisement 사용자 정의 리소스 정보

`l2Advertisements` 오브젝트의 필드는 다음 표에 정의되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | L2 광고의 이름을 지정합니다. |
| `metadata.namespace` | `string` | L2 광고의 네임스페이스를 지정합니다. MetalLB Operator에서 사용하는 동일한 네임스페이스를 지정합니다. |
| `spec.ipAddressPools` | `string` | 선택 사항: 이 광고와 함께 광고할 `IPAddressPools` 목록입니다. 이름별로 선택됩니다. |
| `spec.ipAddressPoolSelectors` | `string` | 선택 사항: 이 광고와 함께 광고되는 `IPAddressPool` 에 대한 선택기입니다. `IPAddressPool` 을 이름 자체 대신 `IPAddressPool` 에 할당된 레이블을 기반으로 광고에 연결하기 위한 것입니다. 이 또는 목록에 의해 선택된 `IPAddressPool` 이 없는 경우, 광고는 모든 `IPAddressPools` 에 적용됩니다. |
| `spec.nodeSelectors` | `string` | 선택 사항: `NodeSelectors` 는 로드 밸런서 IP의 다음 홉으로 노드를 알리도록 제한합니다. 비어있는 경우 모든 노드가 다음 홉으로 발표됩니다. 중요 노드를 다음 홉으로 알리도록 제한하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다. 따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다. Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오. 기술 프리뷰 기능 지원 범위 |
| `spec.interfaces` | `string` | 선택 사항: 로드 밸런서 IP를 알리는 데 사용되는 `인터페이스` 목록입니다. |

#### 4.2.6. L2 광고를 사용하여 MetalLB 구성

`IPAddressPool` 이 L2 프로토콜과 함께 알리도록 다음과 같이 MetalLB를 구성합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-l2
spec:
  addresses:
    - 4.4.4.0/24
  autoAssign: false
```

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

L2 광고를 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `l2advertisement.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
   - doc-example-l2
```

설정을 적용합니다.

```shell-session
$ oc apply -f l2advertisement.yaml
```

#### 4.2.7. L2 광고 및 라벨을 사용하여 MetalLB 구성

`BGPAdvertisement` 및 `L2Advertisement` 사용자 정의 리소스 정의의 `ipAddressPoolSelectors` 필드는 이름 자체 대신 `IPAddressPool` 에 할당된 레이블을 기반으로 `IPAddressPool` 을 광고에 연결하는 데 사용됩니다.

이 예제에서는 `ipAddressPoolSelectors` 필드를 구성하여 `IPAddressPool` Pool이 L2 프로토콜로 광고되도록 MetalLB를 구성하는 방법을 보여줍니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-l2-label
  labels:
    zone: east
spec:
  addresses:
    - 172.31.249.87/32
```

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

`ipAddressPoolSelectors` 를 사용하여 IP를 알리는 L2 광고를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `l2advertisement.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2advertisement-label
  namespace: metallb-system
spec:
  ipAddressPoolSelectors:
    - matchExpressions:
        - key: zone
          operator: In
          values:
            - east
```

설정을 적용합니다.

```shell-session
$ oc apply -f l2advertisement.yaml
```

#### 4.2.8. 선택한 인터페이스에 대해 L2 알림을 사용하여 MetalLB 구성

기본적으로 서비스에 할당된 IP 주소 풀의 IP 주소는 모든 네트워크 인터페이스에서 광고됩니다. `L2Advertisement` 사용자 정의 리소스 정의의 `interfaces` 필드는 IP 주소 풀을 알리는 네트워크 인터페이스를 제한하는 데 사용됩니다.

이 예제에서는 IP 주소 풀이 모든 노드의 `interfaces` 필드에 나열된 네트워크 인터페이스에서만 광고되도록 MetalLB를 구성하는 방법을 보여줍니다.

사전 요구 사항

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

`ipaddresspool.yaml` 과 같은 파일을 생성하고 다음 예와 같은 구성 세부 정보를 입력합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-l2
spec:
  addresses:
    - 4.4.4.0/24
  autoAssign: false
```

다음 예와 같이 IP 주소 풀에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

`인터페이스` 선택기를 사용하여 IP를 알리는 L2 광고를 만듭니다.

`l2advertisement.yaml` 과 같은 YAML 파일을 생성하고 다음 예와 같은 구성 세부 정보를 입력합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: l2advertisement
  namespace: metallb-system
spec:
  ipAddressPools:
   - doc-example-l2
   interfaces:
   - interfaceA
   - interfaceB
```

다음 예와 같이 광고에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f l2advertisement.yaml
```

중요

인터페이스 선택기는 L2를 사용하여 지정된 IP를 알리기 위해 MetalLB가 노드를 선택하는 방식에 영향을 미치지 않습니다. 노드에 선택한 인터페이스가 없는 경우 선택한 노드에서 서비스를 알리지 않습니다.

#### 4.2.9. 보조 네트워크를 사용하여 MetalLB 구성

OpenShift Container Platform 4.14에서 기본 네트워크 동작은 네트워크 인터페이스 간에 IP 패킷 전달을 허용하지 않는 것입니다. 따라서 보조 인터페이스에 MetalLB를 구성할 때 필요한 인터페이스에 대해서만 IP 전달을 활성화하려면 머신 구성을 추가해야 합니다.

참고

4.13에서 업그레이드된 OpenShift Container Platform 클러스터는 글로벌 IP 전달을 활성화하기 위해 업그레이드 중에 글로벌 매개변수가 설정되어 있으므로 영향을 받지 않습니다.

보조 인터페이스에 대한 IP 전달을 활성화하려면 다음 두 가지 옵션이 있습니다.

특정 인터페이스에 대해 IP 전달을 활성화합니다.

모든 인터페이스에 대해 IP 전달을 활성화합니다.

참고

특정 인터페이스에 대해 IP 전달을 활성화하면 보다 세분화된 제어를 제공하는 동시에 모든 인터페이스에 대해 활성화하면 글로벌 설정이 적용됩니다.

#### 4.2.9.1. 특정 인터페이스에 대한 IP 전달 활성화

프로세스

다음 명령을 실행하여 Cluster Network Operator를 패치하여 `routingViaHost` 매개변수를 `true` 로 설정합니다.

```shell-session
$ oc patch network.operator cluster -p '{"spec":{"defaultNetwork":{"ovnKubernetesConfig":{"gatewayConfig": {"routingViaHost": true} }}}}' --type=merge
```

`MachineConfig` CR을 생성하고 적용하여 `bridge-net` 과 같은 특정 보조 인터페이스에 대한 전달을 활성화합니다.

Base64-로컬 시스템에서 다음 명령을 실행하여 네트워크 커널 매개변수를 구성하는 데 사용되는 문자열을 인코딩합니다.

```shell-session
$ echo -e "net.ipv4.conf.bridge-net.forwarding = 1" | base64 -w0
```

```shell-session
bmV0LmlwdjQuY29uZi5icmlkZ2UtbmV0LmZvcndhcmRpbmcgPSAxCg==
```

`MachineConfig` CR을 생성하여 `bridge-net` 이라는 지정된 보조 인터페이스에 대한 IP 전달을 활성화합니다.

다음 YAML을 `enable-ip-forward.yaml` 파일에 저장합니다.

```yaml
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: <node_role>
  name: 81-enable-global-forwarding
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,bmV0LmlwdjQuY29uZi5icmlkZ2UtbmV0LmZvcndhcmRpbmcgPSAxCg==
          verification: {}
        filesystem: root
        mode: 420
        path: /etc/sysctl.d/enable-global-forwarding.conf
  osImageURL: ""
```

1. IP 전달을 활성화하려는 노드 역할(예: `worker`)

2. 생성된 base64 문자열로 채우기

다음 명령을 실행하여 구성을 적용합니다.

```shell-session
$ oc apply -f enable-ip-forward.yaml
```

검증

머신 구성을 적용한 후 다음 절차에 따라 변경 사항을 확인합니다.

다음 명령을 실행하여 대상 노드에서 디버그 세션에 들어갑니다.

```shell-session
$ oc debug node/<node-name>
```

이 단계에서는 < `node-name>-debug` 라는 디버그 Pod를 인스턴스화합니다.

다음 명령을 실행하여 디버그 쉘 내에서 `/host` 를 root 디렉터리로 설정합니다.

```shell-session
$ chroot /host
```

디버그 Pod는 Pod 내의 `/host` 에 호스트의 루트 파일 시스템을 마운트합니다. root 디렉토리를 `/host` 로 변경하면 호스트의 실행 경로에 포함된 바이너리를 실행할 수 있습니다.

다음 명령을 실행하여 IP 전달이 활성화되었는지 확인합니다.

```shell-session
$ cat /etc/sysctl.d/enable-global-forwarding.conf
```

```shell-session
net.ipv4.conf.bridge-net.forwarding = 1
```

출력은 IPv4 전달이 `bridge-net` 인터페이스에서 활성화되었음을 나타냅니다.

#### 4.2.9.2. 전역적으로 IP 전달 활성화

다음 명령을 실행하여 IP 전달을 전역적으로 활성화합니다.

```shell-session
$ oc patch network.operator cluster -p '{"spec":{"defaultNetwork":{"ovnKubernetesConfig":{"gatewayConfig":{"ipForwarding": "Global"}}}}}' --type=merge
```

#### 4.2.10. 추가 리소스

커뮤니티 별칭 구성.

### 4.3. MetalLB BGP 피어 구성

클러스터 관리자는 BGP(Border Gateway Protocol) 피어를 추가, 수정, 삭제할 수 있습니다. MetalLB Operator는 BGP 피어 사용자 정의 리소스를 사용하여 MetalLB `발표` Pod가 BGP 세션을 시작하기 위해 연결하는 피어를 식별합니다. 피어는 MetalLB에서 서비스에 할당하는 로드 밸런서 IP 주소에 대한 경로 알림을 받습니다.

#### 4.3.1. BGP 피어 사용자 정의 리소스 정보

BGP 피어 사용자 지정 리소스의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | BGP 피어 사용자 지정 리소스의 이름을 지정합니다. |
| `metadata.namespace` | `string` | BGP 피어 사용자 지정 리소스의 네임스페이스를 지정합니다. |
| `spec.myASN` | `integer` | BGP 세션의 로컬 종료에 대한 Autonomous System Number (ASN)를 지정합니다. 추가하는 모든 BGP 피어 사용자 지정 리소스에서 동일한 값을 지정합니다. 범위는 `0` 에서 `4294967295` 입니다. |
| `spec.peerASN` | `integer` | BGP 세션의 원격 끝에 대한 ASN을 지정합니다. 범위는 `0` 에서 `4294967295` 입니다. 이 필드를 사용하는 경우 `spec.dynamicASN` 필드에 값을 지정할 수 없습니다. |
| `spec.dynamicASN` | `string` | 명시적으로 설정하지 않고 세션의 원격 끝에 사용할 ASN을 감지합니다. 동일한 ASN을 사용하는 피어의 `internal` 을 지정하거나 다른 ASN을 사용하는 피어의 경우 `external` 을 지정합니다. 이 필드를 사용하는 경우 `spec.peerASN` 필드에 값을 지정할 수 없습니다. |
| `spec.peerAddress` | `string` | BGP 세션을 설정하기 위해 연결할 피어의 IP 주소를 지정합니다. 이 필드를 사용하는 경우 `spec.interface` 필드에 값을 지정할 수 없습니다. |
| `spec.interface` | `string` | 세션을 설정할 때 사용할 인터페이스 이름을 지정합니다. 이 필드를 사용하여 번호가 지정되지 않은 BGP 피어링을 구성합니다. 두 BGP 피어 간에 지점 간 계층 2 연결을 설정해야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다. 이 필드를 사용하는 경우 `spec.peerAddress` 필드에 값을 지정할 수 없습니다. |
| `spec.sourceAddress` | `string` | 선택 사항: BGP 세션을 설정할 때 사용할 IP 주소를 지정합니다. 값은 IPv4 주소여야 합니다. |
| `spec.peerPort` | `integer` | 선택 사항: BGP 세션을 설정하기 위해 연결할 피어의 네트워크 포트를 지정합니다. 범위는 `0` 에서 `16384` 입니다. |
| `spec.holdTime` | `string` | 선택 사항: BGP 피어에 제안할 보류 시간 기간을 지정합니다. 최소값은 3초입니다( `3s` ). 일반적인 단위는 `3s` , `1m` 및 `5m30s` 와 같은 초와 분입니다. 경로 실패를 보다 신속하게 탐지하려면 BFD도 구성합니다. |
| `spec.keepaliveTime` | `string` | 선택 사항: keep-alive 메시지를 BGP 피어로 전송하는 최대 간격을 지정합니다. 이 필드를 지정하는 경우 `holdTime` 필드의 값도 지정해야 합니다. 지정된 값은 `holdTime` 필드의 값보다 작아야 합니다. |
| `spec.routerID` | `string` | 선택 사항: BGP 피어에 알릴 라우터 ID를 지정합니다. 이 필드를 지정하는 경우 추가한 모든 BGP 피어 사용자 지정 리소스에 동일한 값을 지정해야 합니다. |
| `spec.password` | `string` | 선택 사항: TCP MD5 인증된 BGP 세션을 적용하는 라우터의 피어에 보낼 MD5 암호를 지정합니다. |
| `spec.passwordSecret` | `string` | 선택 사항: BGP 피어에 대한 인증 시크릿의 이름을 지정합니다. 시크릿은 `metallb` 네임스페이스에 있어야 하며 basic-auth 유형이어야 합니다. |
| `spec.bfdProfile` | `string` | 선택 사항: BFD 프로필의 이름을 지정합니다. |
| `spec.nodeSelectors` | `object[]` | 선택 사항: 일치 표현식과 일치 레이블을 사용하여 BGP 피어에 연결할 수 있는 노드를 제어하는 선택기를 지정합니다. |
| `spec.ebgpMultiHop` | `boolean` | 선택 사항: BGP 피어가 여러 네트워크 홉 떨어져 있음을 지정합니다. BGP 피어가 동일한 네트워크에 직접 연결되지 않은 경우 이 필드가 `true` 로 설정되지 않는 한 speaker는 BGP 세션을 설정할 수 없습니다. 이 필드는 외부 BGP 에 적용됩니다. 외부 BGP는 BGP 피어가 다른 Autonomous 시스템에 속하는 시기를 설명하는 데 사용되는 용어입니다. |
| `connectTime` | `duration` | BGP가 인접한 연결 시도 사이에 대기하는 시간을 지정합니다. |

참고

`passwordSecret` 필드는 password 필드와 함께 사용할 수 있으며 사용할 `암호` 가 포함된 보안에 대한 참조를 포함합니다. 두 필드를 모두 설정하면 구문 분석 실패가 발생합니다.

#### 4.3.2. BGP 피어 구성

클러스터 관리자는 BGP 피어 사용자 지정 리소스를 추가하여 네트워크 라우터와 라우팅 정보를 교환하고 서비스의 IP 주소를 알릴 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

BGP 광고를 사용하여 MetalLB를 구성합니다.

프로세스

다음 예와 같은 콘텐츠를 사용하여 `bgppeer.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  namespace: metallb-system
  name: doc-example-peer
spec:
  peerAddress: 10.0.0.1
  peerASN: 64501
  myASN: 64500
  routerID: 10.10.10.10
```

BGP 피어의 구성을 적용합니다.

```shell-session
$ oc apply -f bgppeer.yaml
```

#### 4.3.3. 지정된 주소 풀에 대해 특정 BGP 피어 세트를 구성

다음 절차에서는 다음을 수행하는 방법을 설명합니다.

주소 풀 집합(`pool1` 및 `pool2`)을 구성합니다.

BGP 피어(`peer1` 및 `peer2`) 세트를 구성합니다.

`pool1` 을 `peer1` 에 할당하고 `pool2` 를 `peer2` 에 할당하도록 BGP 광고를 구성합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

주소 풀 `pool1` 을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool1.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: pool1
spec:
  addresses:
    - 4.4.4.100-4.4.4.200
    - 2001:100:4::200-2001:100:4::400
```

IP 주소 `pool1` 에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool1.yaml
```

주소 풀 `풀2` 를 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool2.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: pool2
spec:
  addresses:
    - 5.5.5.100-5.5.5.200
    - 2001:100:5::200-2001:100:5::400
```

IP 주소 `풀2` 의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool2.yaml
```

BGP `피어1` 을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgppeer1.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  namespace: metallb-system
  name: peer1
spec:
  peerAddress: 10.0.0.1
  peerASN: 64501
  myASN: 64500
  routerID: 10.10.10.10
```

BGP 피어의 구성을 적용합니다.

```shell-session
$ oc apply -f bgppeer1.yaml
```

BGP `피어2` 를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgppeer2.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  namespace: metallb-system
  name: peer2
spec:
  peerAddress: 10.0.0.2
  peerASN: 64501
  myASN: 64500
  routerID: 10.10.10.10
```

BGP 피어2에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f bgppeer2.yaml
```

BGP 광고 1을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement1.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgpadvertisement-1
  namespace: metallb-system
spec:
  ipAddressPools:
    - pool1
  peers:
    - peer1
  communities:
    - 65535:65282
  aggregationLength: 32
  aggregationLengthV6: 128
  localPref: 100
```

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement1.yaml
```

BGP 광고 2를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement2.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgpadvertisement-2
  namespace: metallb-system
spec:
  ipAddressPools:
    - pool2
  peers:
    - peer2
  communities:
    - 65535:65282
  aggregationLength: 32
  aggregationLengthV6: 128
  localPref: 100
```

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement2.yaml
```

#### 4.3.4. 네트워크 VRF를 통해 서비스 노출

네트워크 인터페이스의 VRF를 BGP 피어와 연결하여 VRF(가상 라우팅 및 전달) 인스턴스를 통해 서비스를 노출할 수 있습니다.

중요

VRF를 통해 BGP 피어에서 서비스를 노출하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다.

따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

네트워크 인터페이스에서 VRF를 사용하여 BGP 피어를 통해 서비스를 노출하면 트래픽을 서비스로 분리하고 독립적인 라우팅 결정을 구성하고 네트워크 인터페이스에서 멀티 테넌시 지원을 활성화할 수 있습니다.

참고

MetalLB는 네트워크 VRF에 속하는 인터페이스를 통해 BGP 세션을 설정하여 해당 인터페이스를 통해 서비스를 알리고 외부 트래픽을 활성화하여 이 인터페이스를 통해 서비스에 도달할 수 있습니다. 그러나 네트워크 VRF 라우팅 테이블은 OVN-Kubernetes에서 사용하는 기본 VRF 라우팅 테이블과 다릅니다.

따라서 트래픽이 OVN-Kubernetes 네트워크 인프라에 연결할 수 없습니다.

OVN-Kubernetes 네트워크 인프라에 도달하기 위해 서비스로 전송되는 트래픽을 활성화하려면 네트워크 트래픽의 다음 홉을 정의하도록 라우팅 규칙을 구성해야 합니다. 자세한 내용은 추가 리소스 섹션에서 " MetalLB를 사용한 대칭 라우팅 관리"의 `NodeNetworkConfigurationPolicy` 리소스를 참조하십시오.

다음은 BGP 피어와 네트워크 VRF를 통해 서비스를 노출하는 고급 단계입니다.

BGP 피어를 정의하고 네트워크 VRF 인스턴스를 추가합니다.

MetalLB의 IP 주소 풀을 지정합니다.

MetalLB에 대해 BGP 경로 알림을 구성하여 지정된 IP 주소 풀 및 VRF 인스턴스와 연결된 BGP 피어를 사용하여 경로를 알립니다.

서비스를 배포하여 구성을 테스트합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인했습니다.

`NodeNetworkConfigurationPolicy` 를 정의하여 VRF(Virtual Routing and Forwarding) 인스턴스를 네트워크 인터페이스와 연결합니다. 이 사전 요구 사항을 작성하는 방법에 대한 자세한 내용은 추가 리소스 섹션을 참조하십시오.

클러스터에 MetalLB를 설치했습니다.

프로세스

`BGPPeer` CR(사용자 정의 리소스)을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `frrviavrf.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: frrviavrf
  namespace: metallb-system
spec:
  myASN: 100
  peerASN: 200
  peerAddress: 192.168.130.1
  vrf: ens4vrf
```

1. BGP 피어와 연결할 네트워크 VRF 인스턴스를 지정합니다. MetalLB는 VRF의 라우팅 정보를 기반으로 서비스를 알리고 라우팅 결정을 내릴 수 있습니다.

참고

`NodeNetworkConfigurationPolicy` CR에서 이 네트워크 VRF 인스턴스를 구성해야 합니다. 자세한 내용은 추가 리소스를 참조하십시오.

다음 명령을 실행하여 BGP 피어에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f frrviavrf.yaml
```

`IPAddressPool` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `first-pool.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.169.10.0/32
```

다음 명령을 실행하여 IP 주소 풀에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f first-pool.yaml
```

`BGPAdvertisement` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `first-adv.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: first-adv
  namespace: metallb-system
spec:
  ipAddressPools:
    - first-pool
  peers:
    - frrviavrf
```

1. 이 예에서 MetalLB는 `첫 번째 풀 IP 주소 풀에서`

`frrviavrf` BGP 피어로 다양한 IP 주소를 알립니다.

다음 명령을 실행하여 BGP 알림에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f first-adv.yaml
```

`네임스페이스`, `배포` 및 `서비스` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `deploy-service.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: test
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: server
  namespace: test
spec:
  selector:
    matchLabels:
      app: server
  template:
    metadata:
      labels:
        app: server
    spec:
      containers:
      - name: server
        image: nginx
        ports:
        - name: http
          containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: server1
  namespace: test
spec:
  ports:
  - name: http
    port: 80
    protocol: TCP
    targetPort: 80
  selector:
    app: server
  type: LoadBalancer
```

다음 명령을 실행하여 네임스페이스, 배포 및 서비스에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f deploy-service.yaml
```

검증

다음 명령을 실행하여 MetalLB speaker Pod를 식별합니다.

```shell-session
$ oc get -n metallb-system pods -l component=speaker
```

```shell-session
NAME            READY   STATUS    RESTARTS   AGE
speaker-c6c5f   6/6     Running   0          69m
```

다음 명령을 실행하여 BGP 세션의 상태가 speaker Pod에 `Established` 되었는지 확인하고, 구성과 일치하도록 변수를 교체합니다.

```shell-session
$ oc exec -n metallb-system <speaker_pod> -c frr -- vtysh -c "show bgp vrf <vrf_name> neigh"
```

```shell-session
BGP neighbor is 192.168.30.1, remote AS 200, local AS 100, external link
  BGP version 4, remote router ID 192.168.30.1, local router ID 192.168.30.71
  BGP state = Established, up for 04:20:09

...
```

다음 명령을 실행하여 서비스가 올바르게 광고되는지 확인합니다.

```shell-session
$ oc exec -n metallb-system <speaker_pod> -c frr -- vtysh -c "show bgp vrf <vrf_name> ipv4"
```

추가 리소스

가상 라우팅 및 전달 정보

예: VRF 인스턴스 노드 네트워크 구성 정책과의 네트워크 인터페이스

송신 서비스 구성

MetalLB를 사용하여 대칭 라우팅 관리

#### 4.3.5.1. 예: BGP 피어에 연결하는 노드 제한

노드 선택기 필드를 지정하여 BGP 피어에 연결할 수 있는 노드를 제어할 수 있습니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: doc-example-nodesel
  namespace: metallb-system
spec:
  peerAddress: 10.0.20.1
  peerASN: 64501
  myASN: 64500
  nodeSelectors:
  - matchExpressions:
    - key: kubernetes.io/hostname
      operator: In
      values: [compute-1.example.com, compute-2.example.com]
```

#### 4.3.5.2. 예: BGP 피어의 BFD 프로필 지정

BGP 피어와 연결할 BFD 프로필을 지정할 수 있습니다. BFD는 BGP보다 동료 간 통신 오류를 보다 신속하게 탐지하여 BGP를 보완합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: doc-example-peer-bfd
  namespace: metallb-system
spec:
  peerAddress: 10.0.20.1
  peerASN: 64501
  myASN: 64500
  holdTime: "10s"
  bfdProfile: doc-example-bfd-profile-full
```

참고

BFD(Earwayal forwarding detection) 프로필을 삭제하고 BGP(Border Gateway Protocol) 피어 리소스에 추가된 `bfdProfile` 을 제거해도 BFD가 비활성화되지 않습니다. 대신 BGP 피어는 기본 BFD 프로필 사용을 시작합니다.

BGP 피어 리소스에서 BFD를 비활성화하려면 BGP 피어 구성을 삭제하고 BFD 프로필없이 다시 생성합니다. 자세한 내용은 BZ#2050824 에서 참조하십시오.

#### 4.3.5.3. 예: 이중 스택 네트워킹을 위한 BGP 피어 지정

듀얼 스택 네트워킹을 지원하려면 IPv4에 대해 하나의 BGP 피어 사용자 지정 리소스와 IPv6에 대해 하나의 BGP 피어 사용자 지정 리소스를 추가합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: doc-example-dual-stack-ipv4
  namespace: metallb-system
spec:
  peerAddress: 10.0.20.1
  peerASN: 64500
  myASN: 64500
---
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: doc-example-dual-stack-ipv6
  namespace: metallb-system
spec:
  peerAddress: 2620:52:0:88::104
  peerASN: 64500
  myASN: 64500
```

#### 4.3.5.4. 예: 번호가 지정되지 않은 BGP 피어링에 대해 BGP 피어 지정

번호가 지정되지 않은 BGP 피어링을 구성하려면 다음 예제 구성을 사용하여 `spec.interface` 필드에 인터페이스를 지정합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: peer-unnumber
  namespace: metallb-system
spec:
  myASN: 64512
  ASN: 645000
  interface: net0
```

참고

`interface` 필드를 사용하려면 두 BGP 피어 간에 지점 간 계층 2 연결을 설정해야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다.

이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.address` 필드에 값을 지정할 수 없습니다.

#### 4.3.6. 다음 단계

MetalLB를 사용하도록 서비스 구성

### 4.4. 커뮤니티 별칭 구성

클러스터 관리자는 커뮤니티 별칭을 구성하고 다양한 알림에서 사용할 수 있습니다.

#### 4.4.1. 커뮤니티 사용자 정의 리소스 정보

`커뮤니티` 사용자 정의 리소스는 커뮤니티의 별칭 컬렉션입니다. 사용자는 `BGPAdvertisement` 를 사용하여 `ipAddressPools` 를 알릴 때 사용할 이름이 지정된 별칭을 정의할 수 있습니다. `커뮤니티` 사용자 정의 리소스의 필드는 다음 표에 설명되어 있습니다.

참고

`커뮤니티` CRD는 BGPAdvertisement에만 적용됩니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | `커뮤니티` 이름을 지정합니다. |
| `metadata.namespace` | `string` | `커뮤니티` 의 네임스페이스를 지정합니다. MetalLB Operator에서 사용하는 동일한 네임스페이스를 지정합니다. |
| `spec.communities` | `string` | BGPAdvertisements에서 사용할 수 있는 BGP 커뮤니티 별칭 목록을 지정합니다. 커뮤니티 별칭은 이름(alias) 및 값(number:number) 쌍으로 구성됩니다. `spec.communities` 필드에서 별칭 이름을 참조하여 BGPAdvertisement를 커뮤니티 별칭에 연결합니다. |

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `name` | `string` | `커뮤니티` 의 별칭의 이름입니다. |
| `value` | `string` | 지정된 이름에 해당하는 BGP `커뮤니티` 값입니다. |

#### 4.4.2. BGP 광고 및 커뮤니티 별칭을 사용하여 MetalLB 구성

`IPAddressPool` 이 BGP 프로토콜 및 NO_ADVERTISE 커뮤니티의 숫자 값으로 설정된 커뮤니티 별칭과 함께 알리도록 다음과 같이 MetalLB를 구성합니다.

다음 예에서 피어 BGP 라우터 `doc-example-peer-community` 는 `203.0.113.200/32` 경로를 수신하고 MetalLB에서 서비스에 할당하는 각 로드 밸런서 IP 주소에 대해 `fc00:f853:ccd:e799::1/128` 경로를 수신합니다. 커뮤니티 별칭은 `NO_ADVERTISE` 커뮤니티로 구성됩니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

IP 주소 풀을 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `ipaddresspool.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  namespace: metallb-system
  name: doc-example-bgp-community
spec:
  addresses:
    - 203.0.113.200/30
    - fc00:f853:ccd:e799::/124
```

IP 주소 풀의 구성을 적용합니다.

```shell-session
$ oc apply -f ipaddresspool.yaml
```

`community1` 이라는 커뮤니티 별칭을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: Community
metadata:
  name: community1
  namespace: metallb-system
spec:
  communities:
    - name: NO_ADVERTISE
      value: '65535:65282'
```

`doc-example-bgp-peer` 라는 BGP 피어를 만듭니다.

다음 예와 같은 콘텐츠를 사용하여 `bgppeer.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  namespace: metallb-system
  name: doc-example-bgp-peer
spec:
  peerAddress: 10.0.0.1
  peerASN: 64501
  myASN: 64500
  routerID: 10.10.10.10
```

BGP 피어의 구성을 적용합니다.

```shell-session
$ oc apply -f bgppeer.yaml
```

커뮤니티 별칭을 사용하여 BGP 광고를 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `bgpadvertisement.yaml` 과 같은 파일을 만듭니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: bgp-community-sample
  namespace: metallb-system
spec:
  aggregationLength: 32
  aggregationLengthV6: 128
  communities:
    - NO_ADVERTISE
  ipAddressPools:
    - doc-example-bgp-community
  peers:
    - doc-example-peer
```

1. 여기에서 `CommunityAlias.name` 을 지정하고 커뮤니티 CR(사용자 정의 리소스) 이름은 지정합니다.

설정을 적용합니다.

```shell-session
$ oc apply -f bgpadvertisement.yaml
```

### 4.5. MetalLB BFD 프로필 구성

클러스터 관리자는 BFD(Bidirectional Forwarding Detection) 프로필을 추가, 수정, 삭제할 수 있습니다. MetalLB Operator는 BFD 프로필 사용자 정의 리소스를 사용하여 BFD를 사용하여 BGP만 제공하는 것보다 빠른 경로 실패 탐지를 제공합니다.

#### 4.5.1. BFD 프로필 사용자 정의 리소스 정보

BFD 프로필 사용자 정의 리소스의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `metadata.name` | `string` | BFD 프로필 사용자 정의 리소스의 이름을 지정합니다. |
| `metadata.namespace` | `string` | BFD 프로필 사용자 정의 리소스의 네임스페이스를 지정합니다. |
| `spec.detectMultiplier` | `integer` | 패킷 손실을 결정하기 위해 감지 수를 지정합니다. 원격 전송 간격은 이 값을 곱하여 연결 손실 감지 타이머를 결정합니다. 예를 들어, 로컬 시스템에 탐지기를 `3` 으로 설정하고 원격 시스템의 전송 간격이 `300` 으로 설정된 경우 로컬 시스템은 패킷을 수신하지 않고 `900` ms 후에만 오류를 감지합니다. 범위는 `2` 에서 `255` 사이입니다. 기본값은 `3` 입니다. |
| `spec.echoMode` | `boolean` | 에코 전송 모드를 지정합니다. 분산 BFD를 사용하지 않는 경우 에코 전송 모드는 피어도 FRR인 경우에만 작동합니다. 기본값은 `false` 이고 에코 전송 모드는 비활성화되어 있습니다. 에코 전송 모드가 활성화되면 대역폭 사용량을 줄이기 위해 제어 패킷의 전송 간격을 늘리는 것이 좋습니다. 예를 들어 전송 간격을 `2000` ms로 늘리는 것이 좋습니다. |
| `spec.echoInterval` | `integer` | 이 시스템에서 에코 패킷을 보내고 수신하는 데 사용하는 최소 전송 간격인 jitter를 지정합니다. 범위는 `10` 에서 `60000` 입니다. 기본값은 `50` ms입니다. |
| `spec.minimumTtl` | `integer` | 들어오는 제어 패킷에 대해 예상되는 최소 TTL을 지정합니다. 이 필드는 다중 홉 세션에만 적용됩니다. 최소 TTL을 설정하는 목적은 패킷 검증 요구 사항을 보다 엄격하게 만들고 다른 세션에서 제어 패킷 수신을 방지하는 것입니다. 기본값은 `254` 이며 시스템이 이 시스템과 피어 간에 하나의 홉만 예상함을 나타냅니다. |
| `spec.passiveMode` | `boolean` | 세션이 active 또는 passive로 표시되는지 여부를 지정합니다. 수동 세션은 연결을 시작하려고 시도하지 않습니다. 대신 수동 세션은 응답을 시작하기 전에 피어의 제어 패킷을 기다립니다. 세션을 패시브로 표시하는 것은 별 네트워크의 중앙 노드로 작동하는 라우터가 있고 전송할 시스템이 필요하지 않은 제어 패킷을 보내지 않으려는 경우 유용합니다. 기본값은 `false` 이며 세션을 활성으로 표시합니다. |
| `spec.receiveInterval` | `integer` | 이 시스템이 제어 패킷을 수신할 수 있는 최소 간격을 지정합니다. 범위는 `10` 에서 `60000` 입니다. 기본값은 `300` ms입니다. |
| `spec.transmitInterval` | `integer` | 이 시스템에서 제어 패킷을 보내는 데 사용하는 최소 전송 간격, 적은 지터를 지정합니다. 범위는 `10` 에서 `60000` 입니다. 기본값은 `300` ms입니다. |

#### 4.5.2. BFD 프로필 구성

클러스터 관리자는 BFD 프로필을 추가하고 프로필을 사용하도록 BGP 피어를 구성할 수 있습니다. BFD는 BGP 자체보다 빠른 경로 실패 탐지 기능을 제공합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

프로세스

다음 예와 같은 콘텐츠를 사용하여 `bfdprofile.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BFDProfile
metadata:
  name: doc-example-bfd-profile-full
  namespace: metallb-system
spec:
  receiveInterval: 300
  transmitInterval: 300
  detectMultiplier: 3
  echoMode: false
  passiveMode: true
  minimumTtl: 254
```

BFD 프로필에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f bfdprofile.yaml
```

#### 4.5.3. 다음 단계

BFD 프로필을 사용하도록 BGP 피어를 구성합니다.

### 4.6. MetalLB를 사용하도록 서비스 구성

클러스터 관리자는 `LoadBalancer` 유형의 서비스를 추가할 때 MetalLB에서 IP 주소를 할당하는 방법을 제어할 수 있습니다.

#### 4.6.1. 특정 IP 주소 요청

다른 로드 밸런서 구현과 마찬가지로 MetalLB에는 서비스 사양에서 `spec.loadBalancerIP` 필드가 허용됩니다.

요청된 IP 주소가 주소 풀의 범위 내에 있는 경우 MetalLB는 요청된 IP 주소를 할당합니다. 요청된 IP 주소가 범위 내에 없는 경우 MetalLB에서 경고를 보고합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service_name>
  annotations:
    metallb.io/address-pool: <address_pool_name>
spec:
  selector:
    <label_key>: <label_value>
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  type: LoadBalancer
  loadBalancerIP: <ip_address>
```

MetalLB에서 요청된 IP 주소를 할당할 수 없는 경우 서비스의 `EXTERNAL-IP` 는 `<pending>` 을 보고하고 다음 명령을 실행하면 다음 예와 같은 이벤트가 포함됩니다.

```shell
oc describe service <service_name>
```

```shell-session
...
Events:
  Type     Reason            Age    From                Message
  ----     ------            ----   ----                -------
  Warning  AllocationFailed  3m16s  metallb-controller  Failed to allocate IP for "default/invalid-request": "4.3.2.1" is not allowed in config
```

#### 4.6.2. 특정 풀에서 IP 주소 요청

특정 범위의 IP 주소를 할당하지만 특정 IP 주소와 관련이 없는 경우 `metallb.io/address-pool` 주석을 사용하여 지정된 주소 풀에서 IP 주소를 요청할 수 있습니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service_name>
  annotations:
    metallb.io/address-pool: <address_pool_name>
spec:
  selector:
    <label_key>: <label_value>
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  type: LoadBalancer
```

`<address_pool_name>` 에 대해 지정한 주소 풀이 없는 경우 MetalLB는 자동 할당을 허용하는 모든 풀에서 IP 주소를 할당하려고 시도합니다.

#### 4.6.3. IP 주소 수락

기본적으로 주소 풀은 자동 할당을 허용하도록 구성됩니다. MetalLB는 이러한 주소 풀에서 IP 주소를 할당합니다.

자동 할당을 위해 구성된 풀의 IP 주소를 수락하려면 특별한 주석이나 구성이 필요하지 않습니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: <service_name>
spec:
  selector:
    <label_key>: <label_value>
  ports:
    - port: 8080
      targetPort: 8080
      protocol: TCP
  type: LoadBalancer
```

#### 4.6.4. 특정 IP 주소 공유

기본적으로 서비스는 IP 주소를 공유하지 않습니다. 그러나 단일 IP 주소에 서비스를 공동 배치해야 하는 경우 `metallb.io/allow-shared-ip` 주석을 서비스에 추가하여 선택적 IP 공유를 활성화할 수 있습니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: service-http
  annotations:
    metallb.io/address-pool: doc-example
    metallb.io/allow-shared-ip: "web-server-svc"
spec:
  ports:
    - name: http
      port: 80
      protocol: TCP
      targetPort: 8080
  selector:
    <label_key>: <label_value>
  type: LoadBalancer
  loadBalancerIP: 172.31.249.7
---
apiVersion: v1
kind: Service
metadata:
  name: service-https
  annotations:
    metallb.io/address-pool: doc-example
    metallb.io/allow-shared-ip: "web-server-svc"
spec:
  ports:
    - name: https
      port: 443
      protocol: TCP
      targetPort: 8080
  selector:
    <label_key>: <label_value>
  type: LoadBalancer
  loadBalancerIP: 172.31.249.7
```

1. `metallb.io/allow-shared-ip` 주석에 동일한 값을 지정합니다. 이 값을 공유 키 라고 합니다.

2. 서비스에 대해 서로 다른 포트 번호를 지정합니다.

3. 서비스가 동일한 Pod 세트로 트래픽을 보내도록 `externalTrafficPolicy: local` 을 지정해야 하는 경우 동일한 Pod 선택기를 지정합니다. `cluster` 외부 트래픽 정책을 사용하는 경우 Pod 선택기를 동일할 필요가 없습니다.

4. 선택 사항: 이전 항목 3개를 지정하는 경우 MetalLB에서 서비스를 동일한 IP 주소에 배치할 수 있습니다. 서비스가 IP 주소를 공유하도록 하려면 공유할 IP 주소를 지정합니다.

기본적으로 Kubernetes는 다중 프로토콜 로드 밸런서 서비스를 허용하지 않습니다. 이 제한으로 인해 일반적으로 TCP 및 UDP에서 수신 대기해야 하는 DNS와 같은 서비스를 실행할 수 없습니다. MetalLB를 사용하여 이 Kubernetes 제한 사항을 해결하려면 다음 두 서비스를 생성합니다.

한 서비스에 대해 TCP를 지정하고 두 번째 서비스에 대해 UDP를 지정합니다.

두 서비스 모두에서 동일한 pod 선택기를 지정합니다.

동일한 공유 키와 `spec.loadBalancerIP` 값을 지정하여 TCP 및 UDP 서비스를 동일한 IP 주소에 공동 배치합니다.

#### 4.6.5. MetalLB를 사용하여 서비스 구성

주소 풀에서 외부 IP 주소를 사용하도록 로드 밸런싱 서비스를 구성할 수 있습니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

MetalLB Operator를 설치하고 MetalLB를 시작합니다.

하나 이상의 주소 풀을 구성합니다.

클라이언트의 트래픽을 클러스터의 호스트 네트워크로 라우팅하도록 네트워크를 구성합니다.

프로세스

`<service_name>.yaml` 파일을 생성합니다. 파일에서 `spec.type` 필드가 `LoadBalancer` 로 설정되어 있는지 확인합니다.

MetalLB에서 서비스에 할당하는 외부 IP 주소를 요청하는 방법에 대한 자세한 내용은 예제를 참조하십시오.

서비스를 생성합니다.

```shell-session
$ oc apply -f <service_name>.yaml
```

```shell-session
service/<service_name> created
```

검증

서비스를 설명합니다.

```shell-session
$ oc describe service <service_name>
```

```plaintext
Name:                     <service_name>
Namespace:                default
Labels:                   <none>
Annotations:              metallb.io/address-pool: doc-example
Selector:                 app=service_name
Type:                     LoadBalancer
IP Family Policy:         SingleStack
IP Families:              IPv4
IP:                       10.105.237.254
IPs:                      10.105.237.254
LoadBalancer Ingress:     192.168.100.5
Port:                     <unset>  80/TCP
TargetPort:               8080/TCP
NodePort:                 <unset>  30550/TCP
Endpoints:                10.244.0.50:8080
Session Affinity:         None
External Traffic Policy:  Cluster
Events:
  Type    Reason        Age                From             Message
  ----    ------        ----               ----             -------
  Normal  nodeAssigned  32m (x2 over 32m)  metallb-speaker  announcing from node "<node_name>"
```

1. 특정 풀에서 IP 주소를 요청하면 주석이 표시됩니다.

2. 서비스 유형에 `LoadBalancer` 가 표시되어야 합니다.

3. 서비스가 올바르게 할당된 경우 부하 분산기 ingress 필드는 외부 IP 주소를 나타냅니다.

4. events 필드는 외부 IP 주소를 알리기 위해 할당된 노드 이름을 나타냅니다. 오류가 발생하면 이벤트 필드에 오류 이유가 표시됩니다.

### 4.7. MetalLB를 사용하여 대칭 라우팅 관리

클러스터 관리자는 MetalLB, NMState, OVN-Kubernetes의 기능을 구현하여 MetalLB 로드 밸런서 서비스 뒤에 있는 Pod의 트래픽을 효과적으로 관리할 수 있습니다. 이 컨텍스트에서 이러한 기능을 결합하면 대칭 라우팅, 트래픽 분리 및 중복 CIDR 주소가 있는 다른 네트워크에서 클라이언트를 지원할 수 있습니다.

이 기능을 수행하려면 MetalLB를 사용하여 가상 라우팅 및 전달(VRF) 인스턴스를 구현하고 송신 서비스를 구성하는 방법을 알아봅니다.

중요

MetalLB 및 송신 서비스에서 VRF 인스턴스를 사용하여 대칭 트래픽을 구성하는 것은 기술 프리뷰 기능 전용입니다. 기술 프리뷰 기능은 Red Hat 프로덕션 서비스 수준 계약(SLA)에서 지원되지 않으며 기능적으로 완전하지 않을 수 있습니다.

따라서 프로덕션 환경에서 사용하는 것은 권장하지 않습니다. 이러한 기능을 사용하면 향후 제품 기능을 조기에 이용할 수 있어 개발 과정에서 고객이 기능을 테스트하고 피드백을 제공할 수 있습니다.

Red Hat 기술 프리뷰 기능의 지원 범위에 대한 자세한 내용은 다음 링크를 참조하십시오.

기술 프리뷰 기능 지원 범위

#### 4.7.1. MetalLB를 사용하여 대칭 라우팅을 관리하는 문제

여러 호스트 인터페이스와 함께 MetalLB를 사용하면 MetalLB에서 호스트에서 사용 가능한 모든 인터페이스를 통해 서비스를 노출하고 알립니다. 이를 통해 네트워크 격리, 비대칭 반환 트래픽 및 중복 CIDR 주소와 관련된 문제가 발생할 수 있습니다.

반환 트래픽이 올바른 클라이언트에 도달하도록 하는 한 가지 옵션은 정적 경로를 사용하는 것입니다. 그러나 이 솔루션을 사용하면 MetalLB에서 서비스를 분리한 다음 다른 인터페이스를 통해 각 서비스를 알릴 수 없습니다. 또한 정적 라우팅에는 수동 구성이 필요하며 원격 사이트를 추가하는 경우 유지 관리가 필요합니다.

MetalLB 서비스를 구현할 때 대칭 라우팅의 추가 문제는 외부 시스템에서 애플리케이션의 소스 및 대상 IP 주소가 동일해야 하는 시나리오입니다. OpenShift Container Platform의 기본 동작은 호스트 네트워크 인터페이스의 IP 주소를 Pod에서 발생하는 트래픽의 소스 IP 주소로 할당하는 것입니다. 이는 여러 호스트 인터페이스에서 문제가 됩니다.

MetalLB, NMState 및 OVN-Kubernetes의 기능을 결합하는 구성을 구현하여 이러한 문제를 해결할 수 있습니다.

#### 4.7.2. MetalLB와 함께 VRF를 사용하여 대칭 라우팅 관리 개요

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/357_OpenShift_MetalLB_VRF_0823.png" alt="MetalLB와 함께 VRF를 사용하여 대칭 라우팅 관리에 대한 네트워크 개요" kind="diagram" diagram_type="semantic_diagram"]
MetalLB와 함께 VRF를 사용하여 대칭 라우팅 관리에 대한 네트워크 개요
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/5f6abd1e005b06e55a04fcd3bc85366d/357_OpenShift_MetalLB_VRF_0823.png`_


NMState를 사용하여 호스트에서 VRF 인스턴스를 구성하고 VRF 인스턴스를 MetalLB `BGPPeer` 리소스와 연결하며, 송신 트래픽에 대한 송신 서비스를 OVN-Kubernetes와 구성하여 대칭 라우팅을 구현하는 문제를 해결할 수 있습니다.

그림 4.1. MetalLB와 함께 VRF를 사용하여 대칭 라우팅 관리에 대한 네트워크 개요

구성 프로세스에는 다음 세 단계가 포함됩니다.

1. VRF 및 라우팅 규칙 정의

VRF 인스턴스를 네트워크 인터페이스와 연결하도록 `NodeNetworkConfigurationPolicy` CR(사용자 정의 리소스)을 구성합니다.

VRF 라우팅 테이블을 사용하여 수신 및 송신 트래픽을 전달합니다.

1. VRF를 MetalLB `BGPPeer` 에 연결

네트워크 인터페이스에서 VRF 인스턴스를 사용하도록 MetalLB `BGPPeer` 리소스를 구성합니다.

`BGPPeer` 리소스를 VRF 인스턴스와 연결하면 지정된 네트워크 인터페이스가 BGP 세션의 기본 인터페이스가 되고 MetalLB는 이 인터페이스를 통해 서비스를 알립니다.

1. 송신 서비스 구성

송신 트래픽에 대해 VRF 인스턴스와 연결된 네트워크를 선택하도록 송신 서비스를 구성합니다.

선택 사항: MetalLB 로드 밸런서 서비스의 IP 주소를 송신 트래픽의 소스 IP로 사용하도록 송신 서비스를 구성합니다.

#### 4.7.3. MetalLB와 함께 VRF를 사용하여 대칭 라우팅 구성

동일한 수신 및 송신 네트워크 경로가 필요한 MetalLB 서비스 뒤의 애플리케이션에 대해 대칭 네트워크 라우팅을 구성할 수 있습니다.

이 예에서는 VRF 라우팅 테이블을 MetalLB 및 송신 서비스와 연결하여 `LoadBalancer` 서비스 뒤의 Pod의 수신 및 송신 트래픽에 대한 대칭 라우팅을 활성화합니다.

중요

`EgressService` CR에서 `sourceIPBy: "LoadBalancerIP"` 설정을 사용하는 경우 `BGPAdvertisement` CR(사용자 정의 리소스)에 로드 밸런서 노드를 지정해야 합니다.

`gatewayConfig.routingViaHost` 사양이 `true` 로 설정된 OVN-Kubernetes를 사용하는 클러스터에서 `sourceIPBy: "Network"` 설정을 사용할 수 있습니다. 또한 `sourceIPBy: "Network"` 설정을 사용하는 경우 네트워크 VRF 인스턴스로 구성된 노드에서 애플리케이션 워크로드를 예약해야 합니다.

사전 요구 사항

OpenShift CLI()를 설치합니다.

```shell
oc
```

`cluster-admin` 권한이 있는 사용자로 로그인합니다.

Kubernetes NMState Operator를 설치합니다.

MetalLB Operator를 설치합니다.

프로세스

`NodeNetworkConfigurationPolicy` CR을 생성하여 VRF 인스턴스를 정의합니다.

다음 예와 같은 콘텐츠를 사용하여 `node-network-vrf.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: nmstate.io/v1
kind: NodeNetworkConfigurationPolicy
metadata:
  name: vrfpolicy
spec:
  nodeSelector:
    vrf: "true"
  maxUnavailable: 3
  desiredState:
    interfaces:
    - name: ens4vrf
      type: vrf
      state: up
      vrf:
        port:
        - ens4
        route-table-id: 2
    - name: ens4
      type: ethernet
      state: up
      ipv4:
        address:
        - ip: 192.168.130.130
          prefix-length: 24
        dhcp: false
        enabled: true
    routes:
      config:
      - destination: 0.0.0.0/0
        metric: 150
        next-hop-address: 192.168.130.1
        next-hop-interface: ens4
        table-id: 2
    route-rules:
      config:
      - ip-to: 172.30.0.0/16
        priority: 998
        route-table: 254
      - ip-to: 10.132.0.0/14
        priority: 998
        route-table: 254
      - ip-to: 169.254.0.0/17
        priority: 998
        route-table: 254
```

1. 정책의 이름입니다.

2. 이 예제에서는 `vrf:true` 레이블이 있는 모든 노드에 정책을 적용합니다.

3. 인터페이스의 이름입니다.

4. 인터페이스 유형입니다. 이 예에서는 VRF 인스턴스를 생성합니다.

5. VRF가 연결하는 노드 인터페이스입니다.

6. VRF의 경로 테이블 ID의 이름입니다.

7. VRF와 연결된 인터페이스의 IPv4 주소입니다.

8. 네트워크 경로에 대한 구성을 정의합니다. `next-hop-address` 필드는 경로에 대한 다음 홉의 IP 주소를 정의합니다. `next-hop-interface` 필드는 경로에 대한 발신 인터페이스를 정의합니다. 이 예에서 VRF 라우팅 테이블은 `2` 이며, 이는 `EgressService` CR에 정의된 ID를 참조합니다.

9. 추가 경로 규칙을 정의합니다. `ip-to` 필드는 `Cluster Network` CIDR, `Service Network` CIDR, `Internal Masquerade` 서브넷 CIDR과 일치해야 합니다. 다음 명령을 실행하여 이러한 CIDR 주소 사양의 값을 볼 수 있습니다.

```shell
oc describe network.operator/cluster
```

10. 경로를 계산할 때 Linux 커널이 사용하는 기본 라우팅 테이블에는 ID `254` 가 있습니다.

다음 명령을 실행하여 정책을 적용합니다.

```shell-session
$ oc apply -f node-network-vrf.yaml
```

`BGPPeer` CR(사용자 정의 리소스)을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `frr-via-vrf.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta2
kind: BGPPeer
metadata:
  name: frrviavrf
  namespace: metallb-system
spec:
  myASN: 100
  peerASN: 200
  peerAddress: 192.168.130.1
  vrf: ens4vrf
```

1. BGP 피어와 연결할 VRF 인스턴스를 지정합니다. MetalLB는 VRF의 라우팅 정보를 기반으로 서비스를 알리고 라우팅 결정을 내릴 수 있습니다.

다음 명령을 실행하여 BGP 피어에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f frr-via-vrf.yaml
```

`IPAddressPool` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `first-pool.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.169.10.0/32
```

다음 명령을 실행하여 IP 주소 풀에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f first-pool.yaml
```

`BGPAdvertisement` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `first-adv.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: BGPAdvertisement
metadata:
  name: first-adv
  namespace: metallb-system
spec:
  ipAddressPools:
    - first-pool
  peers:
    - frrviavrf
  nodeSelectors:
    - matchLabels:
        egress-service.k8s.ovn.org/test-server1: ""
```

1. 이 예에서 MetalLB는 `첫 번째 풀 IP 주소 풀에서`

`frrviavrf` BGP 피어로 다양한 IP 주소를 알립니다.

2. 이 예에서 `EgressService` CR은 로드 밸런서 서비스 IP 주소를 사용하도록 송신 트래픽의 소스 IP 주소를 구성합니다. 따라서 Pod에서 시작되는 트래픽에 대해 동일한 반환 경로를 사용하도록 트래픽을 반환하려면 로드 밸런서 노드를 지정해야 합니다.

다음 명령을 실행하여 BGP 알림에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f first-adv.yaml
```

`EgressService` CR을 생성합니다.

다음 예와 같은 콘텐츠를 사용하여 `egress-service.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: k8s.ovn.org/v1
kind: EgressService
metadata:
  name: server1
  namespace: test
spec:
  sourceIPBy: "LoadBalancerIP"
  nodeSelector:
    matchLabels:
      vrf: "true"
  network: "2"
```

1. 송신 서비스의 이름을 지정합니다. `EgressService` 리소스의 이름은 수정할 로드 밸런서 서비스의 이름과 일치해야 합니다.

2. 송신 서비스의 네임스페이스를 지정합니다. `EgressService` 의 네임스페이스는 수정하려는 로드 밸런서 서비스의 네임스페이스와 일치해야 합니다. 송신 서비스는 네임스페이스 범위입니다.

3. 이 예에서는 `LoadBalancer` 서비스 수신 IP 주소를 송신 트래픽의 소스 IP 주소로 할당합니다.

4. `sourceIPBy` 사양에 `LoadBalancer` 를 지정하면 단일 노드가 `LoadBalancer` 서비스 트래픽을 처리합니다. 이 예에서는 `vrf: "true"` 레이블이 있는 노드만 서비스 트래픽을 처리할 수 있습니다.

노드를 지정하지 않으면 OVN-Kubernetes는 서비스 트래픽을 처리할 작업자 노드를 선택합니다. 노드를 선택하면 OVN-Kubernetes는 형식으로 노드에 레이블을 지정합니다.

```shell
egress-service.k8s.ovn.org/<svc_namespace>-<svc_name>: ""
```

5. 송신 트래픽의 라우팅 테이블 ID를 지정합니다. 값이 `NodeNetworkConfigurationPolicy` 리소스에 정의된 `route-table-id` ID와 일치하는지 확인합니다(예: `route-table-id: 2`).

다음 명령을 실행하여 송신 서비스에 대한 구성을 적용합니다.

```shell-session
$ oc apply -f egress-service.yaml
```

검증

다음 명령을 실행하여 MetalLB 서비스 뒤에서 실행 중인 Pod의 애플리케이션 끝점에 액세스할 수 있는지 확인합니다.

```shell-session
$ curl <external_ip_address>:<port_number>
```

1. 애플리케이션 엔드포인트에 맞게 외부 IP 주소 및 포트 번호를 업데이트합니다.

선택 사항: `LoadBalancer` 서비스 수신 IP 주소를 송신 트래픽의 소스 IP 주소로 할당한 경우 `tcpdump` 와 같은 툴을 사용하여 외부 클라이언트에서 수신된 패킷을 분석하여 이 구성을 확인합니다.

추가 리소스

가상 라우팅 및 전달 정보

네트워크 VRF를 통해 서비스 노출

예: VRF 인스턴스 노드 네트워크 구성 정책과의 네트워크 인터페이스

송신 서비스 구성

### 4.8. MetalLB 및 FRR-K8의 통합 구성

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/695_OpenShift_MetalLB_FRRK8s_integration_0624.png" alt="FRR과의 MetalLB 통합" kind="diagram" diagram_type="semantic_diagram"]
FRR과의 MetalLB 통합
[/FIGURE]

_Source: `ingress_and_load_balancing.html` · asset `https://access.redhat.com/webassets/avalon/d/OpenShift_Container_Platform-4.20-Ingress_and_load_balancing-ko-KR/images/76f6fc7e2474f19025af76e8d6a6402d/695_OpenShift_MetalLB_FRRK8s_integration_0624.png`_


FRRouting (FRR)은 Linux 및 UNIX 플랫폼을 위한 무료 오픈 소스 인터넷 라우팅 프로토콜 제품군입니다. `FRR-K8s` 는 Kubernetes 호환 방식으로 `FRR` API의 하위 집합을 노출하는 Kubernetes 기반 DaemonSet입니다.

클러스터 관리자는 `FRRConfiguration` CR(사용자 정의 리소스)을 사용하여 MetalLB에서 제공하지 않는 일부 FRR 서비스에 액세스할 수 있습니다(예: 경로 수신). `MetalLB` 는 적용된 MetalLB 구성에 해당하는 `FRR-K8s` 구성을 생성합니다.

주의

VRF(Virtual Route Forwarding)를 구성할 때 OpenShift Container Platform용으로 예약된 경우 VRF를 1000보다 낮은 테이블 ID로 변경해야 합니다.

#### 4.8.1. FRR 구성

여러 `FRRConfiguration` CR을 생성하여 `MetalLB` 에서 `FRR` 서비스를 사용할 수 있습니다. `MetalLB` 는 `FRR-K8` 이 모든 사용자가 생성한 다른 모든 구성과 병합하는 `FRRConfiguration` 오브젝트를 생성합니다.

예를 들어, 지정된 인접자가 알리는 모든 접두사를 수신하도록 `FRR-K8` 을 구성할 수 있습니다. 다음 예제에서는 호스트 `172.18.0.5` 를 사용하여 `BGPPeer` 에서 알리는 모든 접두사를 수신하도록 `FRR-K8s` 를 구성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
 name: test
 namespace: metallb-system
spec:
 bgp:
   routers:
   - asn: 64512
     neighbors:
     - address: 172.18.0.5
       asn: 64512
       toReceive:
        allowed:
            mode: all
```

적용된 구성에 관계없이 항상 접두사 집합을 차단하도록 FRR-K8s를 구성할 수도 있습니다. 이는 클러스터 오작동을 유발할 수 있는 Pod 또는 `ClusterIPs` CIDR로의 경로를 방지하는 데 유용할 수 있습니다. 다음 예제에서는 접두사 `192.168.1.0/24` 집합을 차단합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: MetalLB
metadata:
  name: metallb
  namespace: metallb-system
spec:
  bgpBackend: frr-k8s
  frrk8sConfig:
    alwaysBlock:
    - 192.168.1.0/24
```

`FRR-K8s` 를 설정하여 `클러스터 네트워크 CIDR 및 서비스 네트워크` CIDR을 차단할 수 있습니다. 다음 명령을 실행하여 이러한 CIDR 주소 사양의 값을 볼 수 있습니다.

```shell-session
$ oc describe network.config/cluster
```

#### 4.8.2. FRRConfiguration CRD 구성

다음 섹션에서는 `FRRConfiguration` CR(사용자 정의 리소스)을 사용하는 참조 예제를 제공합니다.

#### 4.8.2.1. 라우터 필드

router 필드를 사용하여 각 VRF(Virtual Routing and Forwarding) 리소스에 대해 여러 라우터를 구성할 수 있습니다. 각 라우터에 대해 Autonomous System Number (ASN)를 정의해야 합니다.

다음 예와 같이 BGP(Border Gateway Protocol) 조합 조합 목록을 정의할 수도 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
      - address: 172.18.0.6
        asn: 4200000000
        port: 179
```

#### 4.8.2.2. toAdvertise 필드

기본적으로 `FRR-K8s` 는 라우터 구성의 일부로 구성된 접두사를 알리지 않습니다. 이를 광고하기 위해, 귀하는 `toAdvertise` 필드를 사용합니다.

다음 예제와 같이 접두사의 하위 집합을 알릴 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
        toAdvertise:
          allowed:
            prefixes:
            - 192.168.2.0/24
      prefixes:
        - 192.168.2.0/24
        - 192.169.2.0/24
```

1. 접두사의 하위 집합을 알립니다.

다음 예제에서는 모든 접두사를 알리는 방법을 보여줍니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 4200000000
        ebgpMultiHop: true
        port: 180
        toAdvertise:
          allowed:
            mode: all
      prefixes:
        - 192.168.2.0/24
        - 192.169.2.0/24
```

1. 모든 접두사를 알립니다.

#### 4.8.2.3. 수신자 필드

기본적으로 `FRR-K8s` 는 인접자가 알리는 접두사를 처리하지 않습니다. `toReceive` 필드를 사용하여 이러한 주소를 처리할 수 있습니다.

다음 예제와 같이 접두사의 하위 집합에 대해 구성할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.18.0.5
          asn: 64512
          port: 179
          toReceive:
            allowed:
              prefixes:
              - prefix: 192.168.1.0/24
              - prefix: 192.169.2.0/24
                ge: 25
                le: 28
```

1. 2

접두사 길이가 `le` 접두사 길이보다 작거나 같고 접두사 길이보다 크거나 같은 경우 접두사 `가` 적용됩니다.

다음 예제에서는 발표된 모든 접두사를 처리하도록 FRR을 구성합니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.18.0.5
          asn: 64512
          port: 179
          toReceive:
            allowed:
              mode: all
```

#### 4.8.2.4. bgp 필드

`bgp` 필드를 사용하여 다양한 `BFD` 프로필을 정의하고 이를 인접지와 연결할 수 있습니다. 다음 예에서 `BFD` 는 `BGP` 세션을 백업하고 `FRR` 은 링크 실패를 감지할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
      neighbors:
      - address: 172.30.0.3
        asn: 64512
        port: 180
        bfdProfile: defaultprofile
    bfdProfiles:
      - name: defaultprofile
```

#### 4.8.2.5. nodeSelector 필드

기본적으로 `FRR-K8s` 는 데몬이 실행 중인 모든 노드에 구성을 적용합니다. `nodeSelector` 필드를 사용하여 구성을 적용할 노드를 지정할 수 있습니다. 예를 들면 다음과 같습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    routers:
    - asn: 64512
  nodeSelector:
    labelSelector:
    foo: "bar"
```

#### 4.8.2.6. 인터페이스 필드

`interface` 필드를 사용하여 다음 예제 구성을 사용하여 번호가 지정되지 않은 BGP 피어링을 구성할 수 있습니다.

```yaml
apiVersion: frrk8s.metallb.io/v1beta1
kind: FRRConfiguration
metadata:
  name: test
  namespace: frr-k8s-system
spec:
  bgp:
    bfdProfiles:
    - echoMode: false
      name: simple
      passiveMode: false
    routers:
    - asn: 64512
      neighbors:
      - asn: 64512
        bfdProfile: simple
        disableMP: false
        interface: net10
        port: 179
        toAdvertise:
          allowed:
            mode: filtered
            prefixes:
            - 5.5.5.5/32
        toReceive:
          allowed:
            mode: filtered
      prefixes:
      - 5.5.5.5/32
```

1. 번호가 지정되지 않은 BGP 피어링을 활성화합니다.

참고

`interface` 필드를 사용하려면 두 BGP 피어 간에 지점 간 계층 2 연결을 설정해야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다.

이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.address` 필드에 값을 지정할 수 없습니다.

`FRRConfiguration` 사용자 정의 리소스의 필드는 다음 표에 설명되어 있습니다.

| 필드 | 유형 | 설명 |
| --- | --- | --- |
| `spec.bgp.routers` | `array` | FRR이 구성할 라우터를 지정합니다( VRF당 하나씩). |
| `spec.bgp.routers.asn` | `integer` | 세션의 로컬 종료에 사용할 자동 시스템 번호(ASN)입니다. |
| `spec.bgp.routers.id` | `string` | `bgp` 라우터의 ID를 지정합니다. |
| `spec.bgp.routers.vrf` | `string` | 이 라우터에서 세션을 설정하는 데 사용되는 호스트 vrf를 지정합니다. |
| `spec.bgp.routers.neighbors` | `array` | BGP 세션을 설정하는 포인을 지정합니다. |
| `spec.bgp.routers.neighbors.asn` | `integer` | 세션의 원격 끝에 사용할 ASN을 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.dynamicASN` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.dynamicASN` | `string` | 명시적으로 설정하지 않고 세션의 원격 끝에 사용할 ASN을 감지합니다. 동일한 ASN이 있는 인접지의 `내부` 또는 다른 ASN을 가진 인접자의 경우 `외부` 를 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.asn` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.address` | `string` | 세션을 설정할 IP 주소를 지정합니다. 이 필드를 사용하는 경우 `spec.bgp.routers.neighbors.interface` 필드에 값을 지정할 수 없습니다. |
| `spec.bgp.routers.neighbors.interface` | `string` | 세션을 설정할 때 사용할 인터페이스 이름을 지정합니다. 이 필드를 사용하여 번호가 지정되지 않은 BGP 피어링을 구성합니다. 두 BGP 피어 간에 지점 간 계층 2 연결이 있어야 합니다. IPv4, IPv6 또는 듀얼 스택과 함께 번호가 지정되지 않은 BGP 피어링을 사용할 수 있지만 IPv6 RAs(Router Advertisements)를 활성화해야 합니다. 각 인터페이스는 하나의 BGP 연결로 제한됩니다. |
| `spec.bgp.routers.neighbors.port` | `integer` | 세션을 설정할 때 사용할 포트를 지정합니다. 기본값은 179입니다. |
| `spec.bgp.routers.neighbors.password` | `string` | BGP 세션을 설정하는 데 사용할 암호를 지정합니다. `password` 와 `PasswordSecret` 은 함께 사용할 수 없습니다. |
| `spec.bgp.routers.neighbors.passwordSecret` | `string` | 피어에 대한 인증 시크릿의 이름을 지정합니다. 시크릿은 "kubernetes.io/basic-auth" 유형이어야 하며 FRR-K8s 데몬과 동일한 네임스페이스에 있어야 합니다. "password" 키는 암호를 시크릿에 저장합니다. `password` 와 `PasswordSecret` 은 함께 사용할 수 없습니다. |
| `spec.bgp.routers.neighbors.holdTime` | `duration` | RFC4271에 따라 요청된 BGP 보류 시간을 지정합니다. 기본값은 180s입니다. |
| `spec.bgp.routers.neighbors.keepaliveTime` | `duration` | RFC4271에 따라 요청된 BGP keepalive 시간을 지정합니다. 기본값은 `60s` 입니다. |
| `spec.bgp.routers.neighbors.connectTime` | `duration` | BGP가 인접한 연결 시도 사이에 대기하는 시간을 지정합니다. |
| `spec.bgp.routers.neighbors.ebgpMultiHop` | `boolean` | BGPPeer가 멀티 홉 떨어져 있는지 여부를 나타냅니다. |
| `spec.bgp.routers.neighbors.bfdProfile` | `string` | BGP 세션과 연결된 BFD 세션에 사용할 BFD 프로필의 이름을 지정합니다. 설정되지 않은 경우 BFD 세션이 설정되지 않습니다. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed` | `array` | 인접지 및 관련 속성에 알리는 접두사 목록을 나타냅니다.Represents the list of prefixes to advertise to a neighbor, and the associated properties. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed.prefixes` | `문자열 배열` | 인접지에게 알리기 위한 접두사 목록을 지정합니다. 이 목록은 라우터에서 정의한 접두사와 일치해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.allowed.mode` | `string` | 접두사를 처리할 때 사용할 모드를 지정합니다. 접두사 목록의 접두사만 허용하도록 `filtered` 로 설정할 수 있습니다. 라우터에 구성된 모든 접두사를 허용하도록 `all` 으로 설정할 수 있습니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref` | `array` | 공개된 로컬 기본 설정과 연결된 접두사를 지정합니다. 광고할 수 있도록 허용된 접두사에 로컬 기본 설정과 연결된 접두사를 지정해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref.prefixes` | `문자열 배열` | 로컬 기본 설정과 연결된 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withLocalPref.localPref` | `integer` | 접두사와 연결된 로컬 기본 설정을 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity` | `array` | 공개된 BGP 커뮤니티와 관련된 접두사를 지정합니다. 광고하려는 접두사 목록에 로컬 기본 설정과 연결된 접두사를 포함해야 합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity.prefixes` | `문자열 배열` | 커뮤니티와 연결된 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toAdvertise.withCommunity.community` | `string` | 접두사와 연결된 커뮤니티를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive` | `array` | 인접자로부터 수신할 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed` | `array` | 인접자로부터 수신하려는 정보를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed.prefixes` | `array` | 인접지에서 허용되는 접두사를 지정합니다. |
| `spec.bgp.routers.neighbors.toReceive.allowed.mode` | `string` | 접두사를 처리할 때 사용할 모드를 지정합니다. `filtered` 로 설정하면 `prefixes` 목록의 접두사만 허용됩니다. `all` 로 설정하면 라우터에 구성된 모든 접두사가 허용됩니다. |
| `spec.bgp.routers.neighbors.disableMP` | `boolean` | IPv4 및 IPv6 경로 교환을 별도의 BGP 세션으로 분리하지 못하도록 MP BGP를 비활성화합니다. |
| `spec.bgp.routers.prefixes` | `문자열 배열` | 이 라우터 인스턴스에서 알릴 접두사를 모두 지정합니다. |
| `spec.bgp.bfdProfiles` | `array` | 토론을 구성할 때 사용할 bfd 프로필 목록을 지정합니다. |
| `spec.bgp.bfdProfiles.name` | `string` | 구성의 다른 부분에서 참조할 BFD 프로필의 이름입니다. |
| `spec.bgp.bfdProfiles.receiveInterval` | `integer` | 이 시스템에서 제어 패킷을 수신할 수 있는 최소 간격(밀리초)을 지정합니다. 기본값은 `300ms` 입니다. |
| `spec.bgp.bfdProfiles.transmitInterval` | `integer` | 이 시스템에서 BFD 제어 패킷을 밀리초 단위로 보내는 데 사용할 최소 전송 간격을 지정합니다. 기본값은 `300ms` 입니다. |
| `spec.bgp.bfdProfiles.detectMultiplier` | `integer` | 패킷 손실을 확인하기 위해 감지 수를 구성합니다. 연결 손실 감지 타이머를 확인하려면 원격 전송 간격을 이 값으로 곱합니다. |
| `spec.bgp.bfdProfiles.echoInterval` | `integer` | 이 시스템에서 처리할 수 있는 최소 에코 수신 전송 간격을 밀리초 단위로 구성합니다. 기본값은 `50ms` 입니다. |
| `spec.bgp.bfdProfiles.echoMode` | `boolean` | 에코 전송 모드를 활성화하거나 비활성화합니다. 이 모드는 기본적으로 비활성화되어 있으며 멀티 홉 설정에서 지원되지 않습니다. |
| `spec.bgp.bfdProfiles.passiveMode` | `boolean` | 세션을 패시브로 표시합니다. 수동 세션은 연결을 시작하지 않고 응답을 시작하기 전에 피어의 제어 패킷을 기다립니다. |
| `spec.bgp.bfdProfiles.MinimumTtl` | `integer` | 멀티 홉 세션만 사용할 수 있습니다. 들어오는 BFD 제어 패킷에 대해 예상되는 최소 TTL을 구성합니다. |
| `spec.nodeSelector` | `string` | 이 구성을 적용하려는 노드를 제한합니다. 지정된 경우 라벨이 지정된 선택기와 일치하는 노드만 구성을 적용하려고 합니다. 지정하지 않으면 모든 노드에서 이 구성을 적용하려고 합니다. |
| `status` | `string` | FRRConfiguration의 관찰 상태를 정의합니다. |

#### 4.8.3. FRR-K8s가 여러 구성을 병합하는 방법

여러 사용자가 동일한 노드를 선택하는 구성을 추가하는 경우 `FRR-K8은` 구성을 병합합니다. 각 구성은 다른 구성만 확장할 수 있습니다. 즉, 라우터에 새 인접을 추가하거나 추가 접두사를 인접자에게 광고할 수 있지만 다른 구성에 의해 추가된 구성 요소를 제거할 수는 없습니다.

#### 4.8.3.1. 구성 충돌

특정 구성으로 인해 오류가 발생하여 오류가 발생할 수 있습니다. 예를 들면 다음과 같습니다.

동일한 라우터에 대해 서로 다른 ASN (동일 VRF)

동일한 인접지(동일 IP/포트 사용)에 대해 서로 다른 ASN

이름이 같지만 다른 값이 있는 여러 BFD 프로필

데몬이 노드의 잘못된 구성을 찾으면 구성을 유효하지 않은 것으로 보고하고 이전 유효한 `FRR` 구성으로 되돌립니다.

#### 4.8.3.2. 병합

병합할 때 다음 작업을 수행할 수 있습니다.

인접지에게 알리고자 하는 IP 세트를 확장하십시오.

IP 세트와 함께 추가 인접자를 추가합니다.

커뮤니티를 연결하려는 IP 집합을 확장합니다.

이웃에게 들어오는 경로를 허용하십시오.

각 구성은 자체 포함되어야 합니다. 예를 들어 다른 구성의 접두사를 활용하여 라우터 섹션에 정의되지 않은 접두사를 허용할 수 없습니다.

적용할 구성이 호환되는 경우 병합은 다음과 같이 작동합니다.

`FR-K8은` 모든 라우터를 결합합니다.

`FRR-K8s` 는 각 라우터의 모든 접두사와 이해관계를 병합합니다.

`FR-K8s는` 각 인접지에 대한 모든 필터를 병합합니다.

참고

덜 제한적인 필터가 더 엄격한 필터보다 우선합니다. 예를 들어 일부 접두사를 수락하는 필터는 필터보다 우선하지 않으며 모든 접두사를 수락하는 필터가 일부 접두사를 허용하는 것보다 우선합니다.

### 4.9. MetalLB 로깅, 문제 해결 및 지원

MetalLB 구성 문제를 해결해야 하는 경우 일반적으로 사용되는 명령에 대한 다음 섹션을 참조하십시오.

#### 4.9.1. MetalLB 로깅 수준 설정

MetalLB는 기본 `정보` 설정을 사용하여 컨테이너에서 FRRouting(FRR)을 사용합니다. 이 예에 설명된 대로 `logLevel` 을 설정하여 생성된 로그의 상세 수준을 제어할 수 있습니다.

`logLevel` 을 다음과 같이 `debug` 로 설정하여 MetalLB에 대한 더 깊은 통찰력을 얻습니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 예와 같은 콘텐츠를 사용하여 `setdebugloglevel.yaml` 과 같은 파일을 생성합니다.

```yaml
apiVersion: metallb.io/v1beta1
kind: MetalLB
metadata:
  name: metallb
  namespace: metallb-system
spec:
  logLevel: debug
  nodeSelector:
    node-role.kubernetes.io/worker: ""
```

설정을 적용합니다.

```shell-session
$ oc replace -f setdebugloglevel.yaml
```

참고

여기에서는 `metallb` CR이 이미 생성되어 있으며 여기에서 로그 수준을 변경하고 있는 경우 다음 명령을 사용합니다.

```shell
oc replace
```

`발표자` Pod의 이름을 표시합니다.

```shell-session
$ oc get -n metallb-system pods -l component=speaker
```

```plaintext
NAME                    READY   STATUS    RESTARTS   AGE
speaker-2m9pm           4/4     Running   0          9m19s
speaker-7m4qw           3/4     Running   0          19s
speaker-szlmx           4/4     Running   0          9m19s
```

참고

speaker 및 controller Pod가 다시 생성되어 업데이트된 로깅 수준이 적용되도록 합니다. 로깅 수준은 MetalLB의 모든 구성 요소에 대해 수정됩니다.

`발표자` 로그를 확인합니다.

```shell-session
$ oc logs -n metallb-system speaker-7m4qw -c speaker
```

```plaintext
{"branch":"main","caller":"main.go:92","commit":"3d052535","goversion":"gc / go1.17.1 / amd64","level":"info","msg":"MetalLB speaker starting (commit 3d052535, branch main)","ts":"2022-05-17T09:55:05Z","version":""}
{"caller":"announcer.go:110","event":"createARPResponder","interface":"ens4","level":"info","msg":"created ARP responder for interface","ts":"2022-05-17T09:55:05Z"}
{"caller":"announcer.go:119","event":"createNDPResponder","interface":"ens4","level":"info","msg":"created NDP responder for interface","ts":"2022-05-17T09:55:05Z"}
{"caller":"announcer.go:110","event":"createARPResponder","interface":"tun0","level":"info","msg":"created ARP responder for interface","ts":"2022-05-17T09:55:05Z"}
{"caller":"announcer.go:119","event":"createNDPResponder","interface":"tun0","level":"info","msg":"created NDP responder for interface","ts":"2022-05-17T09:55:05Z"}
I0517 09:55:06.515686      95 request.go:665] Waited for 1.026500832s due to client-side throttling, not priority and fairness, request: GET:https://172.30.0.1:443/apis/operators.coreos.com/v1alpha1?timeout=32s
{"Starting Manager":"(MISSING)","caller":"k8s.go:389","level":"info","ts":"2022-05-17T09:55:08Z"}
{"caller":"speakerlist.go:310","level":"info","msg":"node event - forcing sync","node addr":"10.0.128.4","node event":"NodeJoin","node name":"ci-ln-qb8t3mb-72292-7s7rh-worker-a-vvznj","ts":"2022-05-17T09:55:08Z"}
{"caller":"service_controller.go:113","controller":"ServiceReconciler","enqueueing":"openshift-kube-controller-manager-operator/metrics","epslice":"{\"metadata\":{\"name\":\"metrics-xtsxr\",\"generateName\":\"metrics-\",\"namespace\":\"openshift-kube-controller-manager-operator\",\"uid\":\"ac6766d7-8504-492c-9d1e-4ae8897990ad\",\"resourceVersion\":\"9041\",\"generation\":4,\"creationTimestamp\":\"2022-05-17T07:16:53Z\",\"labels\":{\"app\":\"kube-controller-manager-operator\",\"endpointslice.kubernetes.io/managed-by\":\"endpointslice-controller.k8s.io\",\"kubernetes.io/service-name\":\"metrics\"},\"annotations\":{\"endpoints.kubernetes.io/last-change-trigger-time\":\"2022-05-17T07:21:34Z\"},\"ownerReferences\":[{\"apiVersion\":\"v1\",\"kind\":\"Service\",\"name\":\"metrics\",\"uid\":\"0518eed3-6152-42be-b566-0bd00a60faf8\",\"controller\":true,\"blockOwnerDeletion\":true}],\"managedFields\":[{\"manager\":\"kube-controller-manager\",\"operation\":\"Update\",\"apiVersion\":\"discovery.k8s.io/v1\",\"time\":\"2022-05-17T07:20:02Z\",\"fieldsType\":\"FieldsV1\",\"fieldsV1\":{\"f:addressType\":{},\"f:endpoints\":{},\"f:metadata\":{\"f:annotations\":{\".\":{},\"f:endpoints.kubernetes.io/last-change-trigger-time\":{}},\"f:generateName\":{},\"f:labels\":{\".\":{},\"f:app\":{},\"f:endpointslice.kubernetes.io/managed-by\":{},\"f:kubernetes.io/service-name\":{}},\"f:ownerReferences\":{\".\":{},\"k:{\\\"uid\\\":\\\"0518eed3-6152-42be-b566-0bd00a60faf8\\\"}\":{}}},\"f:ports\":{}}}]},\"addressType\":\"IPv4\",\"endpoints\":[{\"addresses\":[\"10.129.0.7\"],\"conditions\":{\"ready\":true,\"serving\":true,\"terminating\":false},\"targetRef\":{\"kind\":\"Pod\",\"namespace\":\"openshift-kube-controller-manager-operator\",\"name\":\"kube-controller-manager-operator-6b98b89ddd-8d4nf\",\"uid\":\"dd5139b8-e41c-4946-a31b-1a629314e844\",\"resourceVersion\":\"9038\"},\"nodeName\":\"ci-ln-qb8t3mb-72292-7s7rh-master-0\",\"zone\":\"us-central1-a\"}],\"ports\":[{\"name\":\"https\",\"protocol\":\"TCP\",\"port\":8443}]}","level":"debug","ts":"2022-05-17T09:55:08Z"}
```

FRR 로그를 확인합니다.

```shell-session
$ oc logs -n metallb-system speaker-7m4qw -c frr
```

```plaintext
Started watchfrr
2022/05/17 09:55:05 ZEBRA: client 16 says hello and bids fair to announce only bgp routes vrf=0
2022/05/17 09:55:05 ZEBRA: client 31 says hello and bids fair to announce only vnc routes vrf=0
2022/05/17 09:55:05 ZEBRA: client 38 says hello and bids fair to announce only static routes vrf=0
2022/05/17 09:55:05 ZEBRA: client 43 says hello and bids fair to announce only bfd routes vrf=0
2022/05/17 09:57:25.089 BGP: Creating Default VRF, AS 64500
2022/05/17 09:57:25.090 BGP: dup addr detect enable max_moves 5 time 180 freeze disable freeze_time 0
2022/05/17 09:57:25.090 BGP: bgp_get: Registering BGP instance (null) to zebra
2022/05/17 09:57:25.090 BGP: Registering VRF 0
2022/05/17 09:57:25.091 BGP: Rx Router Id update VRF 0 Id 10.131.0.1/32
2022/05/17 09:57:25.091 BGP: RID change : vrf VRF default(0), RTR ID 10.131.0.1
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF br0
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF ens4
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF ens4 addr 10.0.128.4/32
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF ens4 addr fe80::c9d:84da:4d86:5618/64
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF lo
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF ovs-system
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF tun0
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF tun0 addr 10.131.0.1/23
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF tun0 addr fe80::40f1:d1ff:feb6:5322/64
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF veth2da49fed
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF veth2da49fed addr fe80::24bd:d1ff:fec1:d88/64
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF veth2fa08c8c
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF veth2fa08c8c addr fe80::6870:ff:fe96:efc8/64
2022/05/17 09:57:25.091 BGP: Rx Intf add VRF 0 IF veth41e356b7
2022/05/17 09:57:25.091 BGP: Rx Intf address add VRF 0 IF veth41e356b7 addr fe80::48ff:37ff:fede:eb4b/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF veth1295c6e2
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF veth1295c6e2 addr fe80::b827:a2ff:feed:637/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF veth9733c6dc
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF veth9733c6dc addr fe80::3cf4:15ff:fe11:e541/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF veth336680ea
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF veth336680ea addr fe80::94b1:8bff:fe7e:488c/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF vetha0a907b7
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF vetha0a907b7 addr fe80::3855:a6ff:fe73:46c3/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF vethf35a4398
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF vethf35a4398 addr fe80::40ef:2fff:fe57:4c4d/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF vethf831b7f4
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF vethf831b7f4 addr fe80::f0d9:89ff:fe7c:1d32/64
2022/05/17 09:57:25.092 BGP: Rx Intf add VRF 0 IF vxlan_sys_4789
2022/05/17 09:57:25.092 BGP: Rx Intf address add VRF 0 IF vxlan_sys_4789 addr fe80::80c1:82ff:fe4b:f078/64
2022/05/17 09:57:26.094 BGP: 10.0.0.1 [FSM] Timer (start timer expire).
2022/05/17 09:57:26.094 BGP: 10.0.0.1 [FSM] BGP_Start (Idle->Connect), fd -1
2022/05/17 09:57:26.094 BGP: Allocated bnc 10.0.0.1/32(0)(VRF default) peer 0x7f807f7631a0
2022/05/17 09:57:26.094 BGP: sendmsg_zebra_rnh: sending cmd ZEBRA_NEXTHOP_REGISTER for 10.0.0.1/32 (vrf VRF default)
2022/05/17 09:57:26.094 BGP: 10.0.0.1 [FSM] Waiting for NHT
2022/05/17 09:57:26.094 BGP: bgp_fsm_change_status : vrf default(0), Status: Connect established_peers 0
2022/05/17 09:57:26.094 BGP: 10.0.0.1 went from Idle to Connect
2022/05/17 09:57:26.094 BGP: 10.0.0.1 [FSM] TCP_connection_open_failed (Connect->Active), fd -1
2022/05/17 09:57:26.094 BGP: bgp_fsm_change_status : vrf default(0), Status: Active established_peers 0
2022/05/17 09:57:26.094 BGP: 10.0.0.1 went from Connect to Active
2022/05/17 09:57:26.094 ZEBRA: rnh_register msg from client bgp: hdr->length=8, type=nexthop vrf=0
2022/05/17 09:57:26.094 ZEBRA: 0: Add RNH 10.0.0.1/32 type Nexthop
2022/05/17 09:57:26.094 ZEBRA: 0:10.0.0.1/32: Evaluate RNH, type Nexthop (force)
2022/05/17 09:57:26.094 ZEBRA: 0:10.0.0.1/32: NH has become unresolved
2022/05/17 09:57:26.094 ZEBRA: 0: Client bgp registers for RNH 10.0.0.1/32 type Nexthop
2022/05/17 09:57:26.094 BGP: VRF default(0): Rcvd NH update 10.0.0.1/32(0) - metric 0/0 #nhops 0/0 flags 0x6
2022/05/17 09:57:26.094 BGP: NH update for 10.0.0.1/32(0)(VRF default) - flags 0x6 chgflags 0x0 - evaluate paths
2022/05/17 09:57:26.094 BGP: evaluate_paths: Updating peer (10.0.0.1(VRF default)) status with NHT
2022/05/17 09:57:30.081 ZEBRA: Event driven route-map update triggered
2022/05/17 09:57:30.081 ZEBRA: Event handler for route-map: 10.0.0.1-out
2022/05/17 09:57:30.081 ZEBRA: Event handler for route-map: 10.0.0.1-in
2022/05/17 09:57:31.104 ZEBRA: netlink_parse_info: netlink-listen (NS 0) type RTM_NEWNEIGH(28), len=76, seq=0, pid=0
2022/05/17 09:57:31.104 ZEBRA:  Neighbor Entry received is not on a VLAN or a BRIDGE, ignoring
2022/05/17 09:57:31.105 ZEBRA: netlink_parse_info: netlink-listen (NS 0) type RTM_NEWNEIGH(28), len=76, seq=0, pid=0
2022/05/17 09:57:31.105 ZEBRA:  Neighbor Entry received is not on a VLAN or a BRIDGE, ignoring
```

#### 4.9.1.1. FRRouting (FRR) 로그 수준

다음 표에서는 FRR 로깅 수준을 설명합니다.

| 로그 수준 | 설명 |
| --- | --- |
| `all` | 모든 로깅 수준에 대한 모든 로깅 정보를 제공합니다. |
| `debug` | 사람이 진단적으로 도움이 되는 정보입니다. `디버그` 로 설정하여 자세한 문제 해결 정보를 제공합니다. |
| `info` | 항상 기록되어야 하지만 정상적인 상황에서 사용자 개입이 필요하지 않은 정보를 제공합니다. 이는 기본 로깅 수준입니다. |
| `warn` | 잠재적으로 일관되지 않은 `MetalLB` 동작을 유발할 수 있는 모든 것 일반적으로 `MetalLB` 는 이러한 유형의 오류에서 자동으로 복구됩니다. |
| `error` | `MetalLB` 의 기능에 치명적인 모든 오류입니다. 이러한 오류는 일반적으로 관리자가 수정하기 위해 개입해야 합니다. |
| `none` | 모든 로깅을 끕니다. |

#### 4.9.2. BGP 문제 해결

클러스터 관리자는 BGP 구성 문제를 해결해야 하는 경우 FRR 컨테이너에서 명령을 실행해야 합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

다음 명령을 실행하여 `frr-k8s` Pod의 이름을 표시합니다.

```shell-session
$ oc -n metallb-system get pods -l component=frr-k8s
```

```plaintext
NAME            READY   STATUS    RESTARTS   AGE
frr-k8s-thsmw   6/6     Running   0          109m
```

다음 명령을 실행하여 FRR에 대한 실행 중인 구성을 표시합니다.

```shell-session
$ oc exec -n metallb-system frr-k8s-thsmw -c frr -- vtysh -c "show running-config"
```

```plaintext
Building configuration...

Current configuration:
!
frr version 8.5.3
frr defaults traditional
hostname some-hostname
log file /etc/frr/frr.log informational
log timestamp precision 3
no ip forwarding
no ipv6 forwarding
service integrated-vtysh-config
!
router bgp 64500
 bgp router-id 10.0.1.2
 no bgp ebgp-requires-policy
 no bgp default ipv4-unicast
 no bgp network import-check
 neighbor 10.0.2.3 remote-as 64500
 neighbor 10.0.2.3 bfd profile doc-example-bfd-profile-full
 neighbor 10.0.2.3 timers 5 15
 neighbor 10.0.2.4 remote-as 64500
 neighbor 10.0.2.4 bfd profile doc-example-bfd-profile-full
 neighbor 10.0.2.4 timers 5 15
 !
 address-family ipv4 unicast
  network 203.0.113.200/30
  neighbor 10.0.2.3 activate
  neighbor 10.0.2.3 route-map 10.0.2.3-in in
  neighbor 10.0.2.4 activate
  neighbor 10.0.2.4 route-map 10.0.2.4-in in
 exit-address-family
 !
 address-family ipv6 unicast
  network fc00:f853:ccd:e799::/124
  neighbor 10.0.2.3 activate
  neighbor 10.0.2.3 route-map 10.0.2.3-in in
  neighbor 10.0.2.4 activate
  neighbor 10.0.2.4 route-map 10.0.2.4-in in
 exit-address-family
!
route-map 10.0.2.3-in deny 20
!
route-map 10.0.2.4-in deny 20
!
ip nht resolve-via-default
!
ipv6 nht resolve-via-default
!
line vty
!
bfd
 profile doc-example-bfd-profile-full
  transmit-interval 35
  receive-interval 35
  passive-mode
  echo-mode
  echo-interval 35
  minimum-ttl 10
 !
!
end
```

1. `라우터 bgp` 섹션은 MetalLB의 ASN을 나타냅니다.

2. 추가한 각 BGP 피어 사용자 지정 리소스에 대해 서로 > 행이 있는지 확인합니다.

```shell
인접한 <ip-address> remote-as <peer-ASN
```

3. BFD를 구성한 경우 BFD 프로필이 올바른 BGP 피어와 연결되고 BFD 프로필이 명령 출력에 표시되는지 확인합니다.

4. < 추가한 주소 풀에서 지정한 IP 주소 범위와 일치하는지 확인합니다.

```shell
ip-address-range> 네트워크가
```

다음 명령을 실행하여 BGP 요약을 표시합니다.

```shell-session
$ oc exec -n metallb-system frr-k8s-thsmw -c frr -- vtysh -c "show bgp summary"
```

```plaintext
IPv4 Unicast Summary:
BGP router identifier 10.0.1.2, local AS number 64500 vrf-id 0
BGP table version 1
RIB entries 1, using 192 bytes of memory
Peers 2, using 29 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
10.0.2.3        4      64500       387       389        0    0    0 00:32:02            0        1
10.0.2.4        4      64500         0         0        0    0    0    never       Active        0
Total number of neighbors 2

IPv6 Unicast Summary:
BGP router identifier 10.0.1.2, local AS number 64500 vrf-id 0
BGP table version 1
RIB entries 1, using 192 bytes of memory
Peers 2, using 29 KiB of memory

Neighbor        V         AS   MsgRcvd   MsgSent   TblVer  InQ OutQ  Up/Down State/PfxRcd   PfxSnt
10.0.2.3        4      64500       387       389        0    0    0 00:32:02 NoNeg
10.0.2.4        4      64500         0         0        0    0    0    never       Active        0

Total number of neighbors 2
```

1. 출력에 추가한 각 BGP 피어 사용자 지정 리소스에 대한 행이 포함되어 있는지 확인합니다.

2. `0` 개의 메시지 및 전송된 메시지를 표시하는 출력은 BGP 세션이 없는 BGP 피어를 나타냅니다. 네트워크 연결 및 BGP 피어의 BGP 구성을 확인합니다.

다음 명령을 실행하여 주소 풀을 수신한 BGP 피어를 표시합니다.

```shell-session
$ oc exec -n metallb-system frr-k8s-thsmw -c frr -- vtysh -c "show bgp ipv4 unicast 203.0.113.200/30"
```

`ipv4` 를 `ipv6` 으로 교체하여 IPv6 주소 풀을 수신한 BGP 피어를 표시합니다. `203.0.113.200/30` 을 주소 풀에서 IPv4 또는 IPv6 IP 주소 범위로 바꿉니다.

```plaintext
BGP routing table entry for 203.0.113.200/30
Paths: (1 available, best #1, table default)
  Advertised to non peer-group peers:
  10.0.2.3
  Local
    0.0.0.0 from 0.0.0.0 (10.0.1.2)
      Origin IGP, metric 0, weight 32768, valid, sourced, local, best (First path received)
      Last update: Mon Jan 10 19:49:07 2022
```

1. 출력에 BGP 피어의 IP 주소가 포함되어 있는지 확인합니다.

#### 4.9.3. BFD 문제 해결

Red Hat이 지원하는 BFD(Bidirectional Forwarding Detection) 구현에서는 `발표자` Pod의 컨테이너에서 FRRouting(FRR)을 사용합니다. BFD 구현은 BFD 피어를 설정된 BGP 세션을 통해 BGP 피어로 구성되고 있습니다. 클러스터 관리자는 BFD 구성 문제를 해결해야 하는 경우 FRR 컨테이너에서 명령을 실행해야 합니다.

사전 요구 사항

`cluster-admin` 역할의 사용자로 클러스터에 액세스할 수 있어야 합니다.

OpenShift CLI()가 설치되어 있습니다.

```shell
oc
```

프로세스

`발표자` Pod의 이름을 표시합니다.

```shell-session
$ oc get -n metallb-system pods -l component=speaker
```

```plaintext
NAME            READY   STATUS    RESTARTS   AGE
speaker-66bth   4/4     Running   0          26m
speaker-gvfnf   4/4     Running   0          26m
...
```

BFD 피어를 표시합니다.

```shell-session
$ oc exec -n metallb-system speaker-66bth -c frr -- vtysh -c "show bfd peers brief"
```

```plaintext
Session count: 2
SessionId  LocalAddress              PeerAddress              Status
=========  ============              ===========              ======
3909139637 10.0.1.2                  10.0.2.3                 up  <.>
```

<.> `PeerAddress` 열에 각 BFD 피어가 포함되어 있는지 확인합니다. 출력에 출력에 포함할 것으로 예상되는 BFD 피어 IP 주소가 나열되지 않은 경우 피어와 BGP 연결 문제를 해결합니다.

상태 필드가 `다운` 된 경우 노드와 피어 간의 링크와 장비에 대한 연결을 확인합니다. 다음 명령과 같은 명령을 사용하여 speaker Pod의 노드 이름을 확인할 수 있습니다.

```shell
oc get pods -n metallb-system speaker-66bth -o jsonpath='{.spec.nodeName}'
```

#### 4.9.4. BGP 및 BFD에 대한 MetalLB 메트릭

OpenShift Container Platform은 BGP 피어 및 BFD 프로필과 관련된 MetalLB의 다음 Prometheus 지표를 캡처합니다.

| 이름 | 설명 |
| --- | --- |
| `frrk8s_bfd_control_packet_input` | 각 BFD 피어로부터 수신된 BFD 제어 패킷의 수를 계산합니다. |
| `frrk8s_bfd_control_packet_output` | 각 BFD 피어로 전송되는 BFD 제어 패킷의 수를 계산합니다. |
| `frrk8s_bfd_echo_packet_input` | 각 BFD 피어로부터 수신된 BFD 에코 패킷의 수를 계산합니다. |
| `frrk8s_bfd_echo_packet_output` | 각 BFD로 전송되는 BFD 에코 패킷의 수를 계산합니다. |
| `frrk8s_bfd_session_down_events` | 피어가 `down` 상태를 입력한 BFD 세션의 횟수를 계산합니다. |
| `frrk8s_bfd_session_up` | BFD 피어와의 연결 상태를 나타냅니다. `1` 세션이 `up` 이고 `0` 은 세션이 `중단` 되었음을 나타냅니다. |
| `frrk8s_bfd_session_up_events` | 피어가 `up` 상태를 입력한 BFD 세션의 횟수를 계산합니다. |
| `frrk8s_bfd_zebra_notifications` | 각 BFD 피어에 대한 BFD Zebra 알림 수를 계산합니다. |

| 이름 | 설명 |
| --- | --- |
| `frrk8s_bgp_announced_prefixes_total` | BGP 피어에 광고되는 로드 밸런서 IP 주소 접두사 수를 계산합니다. 접두사 및 집계 경로 라는 용어는 동일한 의미가 있습니다. |
| `frrk8s_bgp_session_up` | BGP 피어와의 연결 상태를 나타냅니다. `1` 세션이 `up` 이고 `0` 은 세션이 `중단` 되었음을 나타냅니다. |
| `frrk8s_bgp_updates_total` | 각 BGP 피어로 전송되는 BGP 업데이트 메시지의 수를 계산합니다. |
| `frrk8s_bgp_opens_sent` | 각 BGP 피어로 전송되는 BGP 공개 메시지의 수를 계산합니다. |
| `frrk8s_bgp_opens_received` | 각 BGP 피어로부터 수신된 BGP 공개 메시지의 수를 계산합니다. |
| `frrk8s_bgp_notifications_sent` | 각 BGP 피어로 전송되는 BGP 알림 메시지의 수를 계산합니다. |
| `frrk8s_bgp_updates_total_received` | 각 BGP 피어로부터 수신된 BGP 업데이트 메시지의 수를 계산합니다. |
| `frrk8s_bgp_keepalives_sent` | 각 BGP 피어에 전송된 BGP keepalive 메시지의 수를 계산합니다. |
| `frrk8s_bgp_keepalives_received` | 각 BGP 피어에서 수신된 BGP keepalive 메시지의 수를 계산합니다. |
| `frrk8s_bgp_route_refresh_sent` | 각 BGP 피어에 전송된 BGP 경로 새로 고침 메시지의 수를 계산합니다. |
| `frrk8s_bgp_total_sent` | 각 BGP 피어로 전송되는 총 BGP 메시지 수를 계산합니다. |
| `frrk8s_bgp_total_received` | 각 BGP 피어로부터 수신된 총 BGP 메시지 수를 계산합니다. |

추가 리소스

모니터링 대시보드 사용에 대한 정보는 모니터링 대시보드를 사용하여 모든 프로젝트의 메트릭 쿼리 를 참조하십시오.

#### 4.9.5. MetalLB 데이터 수집 정보

다음 명령CLI 명령을 사용하여 클러스터, MetalLB 구성 및 MetalLB Operator에 대한 정보를 수집할 수 있습니다. 다음 기능 및 오브젝트는 MetalLB 및 MetalLB Operator와 연결되어 있습니다.

```shell
oc adm must-gather
```

MetalLB Operator가 배포된 네임스페이스 및 하위 오브젝트

모든 MetalLB Operator CRD(사용자 정의 리소스 정의)

다음 명령CLI 명령은 Red Hat이 BGP 및 BFD를 구현하는 데 사용하는 FRRouting (FRR)에서 다음 정보를 수집합니다.

```shell
oc adm must-gather
```

`/etc/frr/frr.conf`

`/etc/frr/frr.log`

`/etc/frr/daemons` 구성 파일

`/etc/frr/vtysh.conf`

이전 목록의 로그 및 구성 파일은 각 `speaker` pod의 `frr` 컨테이너에서 수집됩니다.

로그 및 구성 파일 외에도 CLI 명령은 다음 `vtysh` 명령에서 출력을 수집합니다.

```shell
oc adm must-gather
```

`show running-config`

`show bgp ipv4`

`show bgp ipv6`

`Bgp Neories를 표시합니다.`

`bfd 피어 표시`

다음 명령CLI 명령을 실행할 때 추가 구성이 필요하지 않습니다.

```shell
oc adm must-gather
```

추가 리소스

클러스터에 대한 데이터 수집
