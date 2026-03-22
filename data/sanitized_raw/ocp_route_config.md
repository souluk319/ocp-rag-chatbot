<!-- source: ocp_route_config.md -->

# Networking

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/ingress_and_load_balancing/routes
---

# Chapter 1. Routes

## 1.1. Creating basic routesCopy linkLink copied to clipboard!

If you have unencrypted HTTP, you can create a basic route with a route object.

### 1.1.1. Creating an HTTP-based routeCopy linkLink copied to clipboard!

You can use the following procedure to create a simple HTTP-based route to a web application, using thehello-openshiftapplication as an example.

You can create a route to host your application at a public URL. The route can either be secure or unsecured, depending on the network security configuration of your application. An HTTP-based route is an unsecured route that uses the basic HTTP routing protocol and exposes a service on an unsecured application port.

Prerequisites

- You installed the OpenShift CLI (oc).
- You are logged in as an administrator.
- You have a web application that exposes a port and a TCP endpoint listening for traffic on the port.

Procedure

- Create a project calledhello-openshiftby running the following command:oc new-project hello-openshift$oc new-project hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a project calledhello-openshiftby running the following command:

- Create a pod in the project by running the following command:oc create -f https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json$oc create-fhttps://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.jsonCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a pod in the project by running the following command:

- Create a service calledhello-openshiftby running the following command:oc expose pod/hello-openshift$oc expose pod/hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a service calledhello-openshiftby running the following command:

- Create an unsecured route to thehello-openshiftapplication by running the following command:oc expose svc hello-openshift$oc expose svc hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create an unsecured route to thehello-openshiftapplication by running the following command:

Verification

- To verify that therouteresource that you created, run the following command:oc get routes -o yaml hello-openshift$oc get routes-oyaml hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflowExample YAML definition of the created unsecured routeapiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: hello-openshift
spec:
  host: www.example.com
  port:
    targetPort: 8080
  to:
    kind: Service
    name: hello-openshiftapiVersion:route.openshift.io/v1kind:Routemetadata:name:hello-openshiftspec:host:www.example.comport:targetPort:8080to:kind:Servicename:hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflowwhere:hostSpecifies an alias DNS record that points to the service. This field can be any valid DNS name, such aswww.example.com. The DNS name must follow DNS952 subdomain conventions. If not specified, a route name is automatically generated.targetPortSpecifies the target port on pods that is selected by the service that this route points to.To display your default ingress domain, run the following command:oc get ingresses.config/cluster -o jsonpath={.spec.domain}$oc get ingresses.config/cluster-ojsonpath={.spec.domain}Copy to ClipboardCopied!Toggle word wrapToggle overflow

To verify that therouteresource that you created, run the following command:

Example YAML definition of the created unsecured route

```
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

```
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

where:

**host**
  Specifies an alias DNS record that points to the service. This field can be any valid DNS name, such aswww.example.com. The DNS name must follow DNS952 subdomain conventions. If not specified, a route name is automatically generated.

**targetPort**
  Specifies the target port on pods that is selected by the service that this route points to.To display your default ingress domain, run the following command:oc get ingresses.config/cluster -o jsonpath={.spec.domain}$oc get ingresses.config/cluster-ojsonpath={.spec.domain}Copy to ClipboardCopied!Toggle word wrapToggle overflow

Specifies the target port on pods that is selected by the service that this route points to.

To display your default ingress domain, run the following command:

### 1.1.2. Path-based routesCopy linkLink copied to clipboard!

To serve multiple applications by using a single hostname, configure path-based routes. This HTTP-based configuration directs traffic to specific services by comparing the URL path component, ensuring requests match the most specific route defined.

The following table shows example routes and their accessibility:

| Route | When compared to | Accessible |
| --- | --- | --- |
| www.example.com/test | www.example.com/test | Yes |
| www.example.com | No |
| www.example.com/testandwww.example.com | www.example.com/test | Yes |
| www.example.com | Yes |
| www.example.com | www.example.com/text | Yes (Matched by the host, not the route) |
| www.example.com | Yes |

www.example.com/test

www.example.com/test

Yes

www.example.com

No

www.example.com/testandwww.example.com

www.example.com/test

Yes

www.example.com

Yes

www.example.com

www.example.com/text

Yes (Matched by the host, not the route)

www.example.com

Yes

Example of an unsecured route with a path

```
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

```
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

- spec.host: Specifies the path attribute for a path-based route.

Path-based routing is not available when using passthrough TLS, as the router does not terminate TLS in that case and cannot read the contents of the request.

### 1.1.3. Creating a route for Ingress Controller shardingCopy linkLink copied to clipboard!

To host applications at specific URLs and balance traffic load in OpenShift Container Platform, configure Ingress Controller sharding. By sharding, you can isolate traffic for specific workloads or tenants, ensuring efficient resource management across your cluster.

The following procedure describes how to create a route for Ingress Controller sharding, using thehello-openshiftapplication as an example.

Prerequisites

- You installed the OpenShift CLI (oc).
- You are logged in as a project administrator.
- You have a web application that exposes a port and an HTTP or TLS endpoint listening for traffic on the port.
- You have configured the Ingress Controller for sharding.

Procedure

- Create a project calledhello-openshiftby running the following command:oc new-project hello-openshift$oc new-project hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a project calledhello-openshiftby running the following command:

- Create a pod in the project by running the following command:oc create -f https://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.json$oc create-fhttps://raw.githubusercontent.com/openshift/origin/master/examples/hello-openshift/hello-pod.jsonCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a pod in the project by running the following command:

- Create a service calledhello-openshiftby running the following command:oc expose pod/hello-openshift$oc expose pod/hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a service calledhello-openshiftby running the following command:

- Create a route definition calledhello-openshift-route.yaml:YAML definition of the created route for shardingapiVersion: route.openshift.io/v1
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
    name: hello-openshiftapiVersion:route.openshift.io/v1kind:Routemetadata:labels:type:shardedname:hello-openshift-edgenamespace:hello-openshiftspec:subdomain:hello-openshifttls:termination:edgeto:kind:Servicename:hello-openshiftCopy to ClipboardCopied!Toggle word wrapToggle overflowwhere:typeSpecifies both the label key and its corresponding label value must match the ones specified in the Ingress Controller. In this example, the Ingress Controller has the label key and valuetype: sharded.subdomainSpecifies the route gets exposed by using the value of thesubdomainfield. When you specify thesubdomainfield, you must leave the hostname unset. If you specify both thehostandsubdomainfields, then the route uses the value of thehostfield, and ignore thesubdomainfield.

Create a route definition calledhello-openshift-route.yaml:

YAML definition of the created route for sharding

```
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

```
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

where:

**type**
  Specifies both the label key and its corresponding label value must match the ones specified in the Ingress Controller. In this example, the Ingress Controller has the label key and valuetype: sharded.

**subdomain**
  Specifies the route gets exposed by using the value of thesubdomainfield. When you specify thesubdomainfield, you must leave the hostname unset. If you specify both thehostandsubdomainfields, then the route uses the value of thehostfield, and ignore thesubdomainfield.
- Usehello-openshift-route.yamlto create a route to thehello-openshiftapplication by running the following command:oc -n hello-openshift create -f hello-openshift-route.yaml$oc-nhello-openshift create-fhello-openshift-route.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Usehello-openshift-route.yamlto create a route to thehello-openshiftapplication by running the following command:

Verification

- Get the status of the route with the following command:oc -n hello-openshift get routes/hello-openshift-edge -o yaml$oc-nhello-openshift get routes/hello-openshift-edge-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowThe resultingRouteresource should look similar to the following:Example outputapiVersion: route.openshift.io/v1
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
    routerName: shardedapiVersion:route.openshift.io/v1kind:Routemetadata:labels:type:shardedname:hello-openshift-edgenamespace:hello-openshiftspec:subdomain:hello-openshifttls:termination:edgeto:kind:Servicename:hello-openshiftstatus:ingress:-host:hello-openshift.<apps-sharded.basedomain.example.net>routerCanonicalHostname:router-sharded.<apps-sharded.basedomain.example.net>routerName:shardedCopy to ClipboardCopied!Toggle word wrapToggle overflowwhere:hostSpecifies the hostname the Ingress Controller, or router, uses to expose the route. The value of thehostfield is automatically determined by the Ingress Controller, and uses its domain. In this example, the domain of the Ingress Controller is<apps-sharded.basedomain.example.net>.<apps-sharded.basedomain.example.net>Specifies the hostname of the Ingress Controller. If the hostname is not set, the route can use a subdomain instead. When you specify a subdomain, you automatically use the domain of the Ingress Controller that exposes the route. When a route is exposed by multiple Ingress Controllers, the route is hosted at multiple URLs.routerNameSpecifies the name of the Ingress Controller. In this example, the Ingress Controller has the namesharded.

Get the status of the route with the following command:

The resultingRouteresource should look similar to the following:

Example output

```
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

```
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

where:

**host**
  Specifies the hostname the Ingress Controller, or router, uses to expose the route. The value of thehostfield is automatically determined by the Ingress Controller, and uses its domain. In this example, the domain of the Ingress Controller is<apps-sharded.basedomain.example.net>.

**<apps-sharded.basedomain.example.net>**
  Specifies the hostname of the Ingress Controller. If the hostname is not set, the route can use a subdomain instead. When you specify a subdomain, you automatically use the domain of the Ingress Controller that exposes the route. When a route is exposed by multiple Ingress Controllers, the route is hosted at multiple URLs.

**routerName**
  Specifies the name of the Ingress Controller. In this example, the Ingress Controller has the namesharded.

### 1.1.4. Creating a route through an Ingress objectCopy linkLink copied to clipboard!

To integrate ecosystem components that require Ingress resources, configure an Ingress object. OpenShift Container Platform automatically manages the lifecycle of the corresponding route objects, creating and deleting them to ensure seamless connectivity.

Procedure

- Define an Ingress object in the OpenShift Container Platform console or by entering theoc createcommand:YAML Definition of an IngressapiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
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
# ...apiVersion:networking.k8s.io/v1kind:Ingressmetadata:name:frontendannotations:route.openshift.io/termination:"reencrypt"route.openshift.io/destination-ca-certificate-secret:[REDACTED_SECRET] ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:route.openshift.io/terminationSpecifies theroute.openshift.io/terminationannotation. You can configure thespec.tls.terminationparameter of theRoutebecauseIngressdoes not have this parameter. The accepted values areedge,passthrough, andreencrypt. All other values are silently ignored. When the annotation value is unset,edgeis the default route. The TLS certificate details must be defined in the template file to implement the default edge route.rules.hostSpecifies an explicit hostname for theIngressobject. Mandatory parameter. You can use the<host_name>.<cluster_ingress_domain>syntax, for exampleapps.openshiftdemos.com, to take advantage of the*.<cluster_ingress_domain>wildcard DNS record and serving certificate for the cluster. Otherwise, you must ensure that there is a DNS record for the chosen hostname.destination-ca-certificate-secretSpecifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation can be used on an Ingress object to define a route with a custom destination certificate (CA). The annotation references a kubernetes secret,secret-ca-certthat will be inserted into the generated route.If you specify thepassthroughvalue in theroute.openshift.io/terminationannotation, setpathto''andpathTypetoImplementationSpecificin the spec:apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
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
# ...apiVersion:networking.k8s.io/v1kind:Ingress# ...spec:rules:-host:www.example.comhttp:paths:-path:''pathType:ImplementationSpecificbackend:service:name:frontendport:number:443# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowoc apply -f ingress.yaml$oc apply-fingress.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowTo specify a route object with a destination CA from an ingress object, you must create akubernetes.io/tlsorOpaquetype secret with a certificate in PEM-encoded format in thedata.tls.crtspecifier of the secret.

Define an Ingress object in the OpenShift Container Platform console or by entering theoc createcommand:

YAML Definition of an Ingress

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
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
# ...
```

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
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
# ...
```

where:

**route.openshift.io/termination**
  Specifies theroute.openshift.io/terminationannotation. You can configure thespec.tls.terminationparameter of theRoutebecauseIngressdoes not have this parameter. The accepted values areedge,passthrough, andreencrypt. All other values are silently ignored. When the annotation value is unset,edgeis the default route. The TLS certificate details must be defined in the template file to implement the default edge route.

**rules.host**
  Specifies an explicit hostname for theIngressobject. Mandatory parameter. You can use the<host_name>.<cluster_ingress_domain>syntax, for exampleapps.openshiftdemos.com, to take advantage of the*.<cluster_ingress_domain>wildcard DNS record and serving certificate for the cluster. Otherwise, you must ensure that there is a DNS record for the chosen hostname.

**destination-ca-certificate-secret**
  Specifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation can be used on an Ingress object to define a route with a custom destination certificate (CA). The annotation references a kubernetes secret,secret-ca-certthat will be inserted into the generated route.If you specify thepassthroughvalue in theroute.openshift.io/terminationannotation, setpathto''andpathTypetoImplementationSpecificin the spec:apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
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
# ...apiVersion:networking.k8s.io/v1kind:Ingress# ...spec:rules:-host:www.example.comhttp:paths:-path:''pathType:ImplementationSpecificbackend:service:name:frontendport:number:443# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowoc apply -f ingress.yaml$oc apply-fingress.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowTo specify a route object with a destination CA from an ingress object, you must create akubernetes.io/tlsorOpaquetype secret with a certificate in PEM-encoded format in thedata.tls.crtspecifier of the secret.

Specifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation can be used on an Ingress object to define a route with a custom destination certificate (CA). The annotation references a kubernetes secret,secret-ca-certthat will be inserted into the generated route.

- If you specify thepassthroughvalue in theroute.openshift.io/terminationannotation, setpathto''andpathTypetoImplementationSpecificin the spec:apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
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
# ...apiVersion:networking.k8s.io/v1kind:Ingress# ...spec:rules:-host:www.example.comhttp:paths:-path:''pathType:ImplementationSpecificbackend:service:name:frontendport:number:443# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowoc apply -f ingress.yaml$oc apply-fingress.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you specify thepassthroughvalue in theroute.openshift.io/terminationannotation, setpathto''andpathTypetoImplementationSpecificin the spec:

```
apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
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
# ...
```

```
apiVersion: networking.k8s.io/v1
kind: Ingress
# ...
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
# ...
```

- To specify a route object with a destination CA from an ingress object, you must create akubernetes.io/tlsorOpaquetype secret with a certificate in PEM-encoded format in thedata.tls.crtspecifier of the secret.
- List your routes:oc get routes$oc get routesCopy to ClipboardCopied!Toggle word wrapToggle overflowThe result includes an autogenerated route whose name starts withfrontend-:NAME             HOST/PORT         PATH    SERVICES    PORT    TERMINATION          WILDCARD
frontend-gnztq   www.example.com           frontend    443     reencrypt/Redirect   NoneNAME             HOST/PORT         PATH    SERVICES    PORT    TERMINATION          WILDCARD
frontend-gnztq   www.example.com           frontend    443     reencrypt/Redirect   NoneCopy to ClipboardCopied!Toggle word wrapToggle overflowYAML definition example of an autogenerated routeapiVersion: route.openshift.io/v1
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
    name: frontendapiVersion:route.openshift.io/v1kind:Routemetadata:name:frontend-gnztqownerReferences:-apiVersion:networking.k8s.io/v1controller:truekind:Ingressname:frontenduid:4e6c59cc-704d-4f44-b390-617d879033b6spec:host:www.example.compath:/port:targetPort:httpstls:certificate:|-----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----insecureEdgeTerminationPolicy:Redirectkey:|-----BEGIN RSA PRIVATE KEY-----
      [...]
      -----END RSA PRIVATE KEY-----termination:reencryptdestinationCACertificate:|-----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----to:kind:Servicename:frontendCopy to ClipboardCopied!Toggle word wrapToggle overflow

List your routes:

The result includes an autogenerated route whose name starts withfrontend-:

```
NAME             HOST/PORT         PATH    SERVICES    PORT    TERMINATION          WILDCARD
frontend-gnztq   www.example.com           frontend    443     reencrypt/Redirect   None
```

```
NAME             HOST/PORT         PATH    SERVICES    PORT    TERMINATION          WILDCARD
frontend-gnztq   www.example.com           frontend    443     reencrypt/Redirect   None
```

YAML definition example of an autogenerated route

```
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

```
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

## 1.2. Securing routesCopy linkLink copied to clipboard!

You can secure a route with HTTP strict transport security (HSTS).

### 1.2.1. HTTP Strict Transport SecurityCopy linkLink copied to clipboard!

To enhance security and optimize website performance, use the HTTP Strict Transport Security (HSTS) policy. This mechanism signals browsers to use only HTTPS traffic on the route host, eliminating the need for HTTP redirects and speeding up user interactions.

When HSTS policy is enforced, HSTS adds a Strict Transport Security header to HTTP and HTTPS responses from the site. You can use theinsecureEdgeTerminationPolicyvalue in a route to redirect HTTP to HTTPS. When HSTS is enforced, the client changes all requests from the HTTP URL to HTTPS before the request is sent, eliminating the need for a redirect.

Cluster administrators can configure HSTS to do the following:

- Enable HSTS per-route
- Disable HSTS per-route
- Enforce HSTS per-domain, for a set of domains, or use namespace labels in combination with domains

HSTS works only with secure routes, either edge-terminated or re-encrypt. The configuration is ineffective on HTTP or passthrough routes.

#### 1.2.1.1. Enabling HTTP Strict Transport Security per-routeCopy linkLink copied to clipboard!

To enforce secure HTTPS connections for specific applications, enable HTTP Strict Transport Security (HSTS) on a per-route basis. Applying thehaproxy.router.openshift.io/hsts_headerannotation to edge and re-encrypt routes ensures that browsers reject unencrypted traffic.

Prerequisites

- You are logged in to the cluster with a user with administrator privileges for the project.
- You installed the OpenShift CLI (oc).

Procedure

- To enable HSTS on a route, add thehaproxy.router.openshift.io/hsts_headervalue to the edge-terminated or re-encrypt route. You can use theoc annotatetool to do this by running the following command:oc annotate route <route_name> -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000;\
includeSubDomains;preload"$oc annotate route<route_name>-n<namespace>--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=31536000;\1includeSubDomains;preload"Copy to ClipboardCopied!Toggle word wrapToggle overflow1In this example, the maximum age is set to31536000ms, which is approximately 8.5 hours.In this example, the equal sign (=) is in quotes. This is required to properly execute the annotate command.Example route configured with an annotationapiVersion: route.openshift.io/v1
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
  wildcardPolicy: "Subdomain"apiVersion:route.openshift.io/v1kind:Routemetadata:annotations:haproxy.router.openshift.io/hsts_header:max-age=31536000;includeSubDomains;preload# ...spec:host:def.abc.comtls:termination:"reencrypt"...wildcardPolicy:"Subdomain"Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:max-ageSpecifies the measurement of the length of time, in seconds, for the HSTS policy. If set to0, it negates the policy.includeSubDomainsSpecifies that all subdomains of the host must have the same HSTS policy as the host. Optional parameter.preloadSpecifies that the site is included in the HSTS preload list whenmax-ageis greater than0. For example, sites such as Google can construct a list of sites that havepreloadset. Browsers can then use these lists to determine which sites they can communicate with over HTTPS, even before they have interacted with the site. Withoutpreloadset, browsers must have interacted with the site over HTTPS, at least once, to get the header. Optional parameter.

To enable HSTS on a route, add thehaproxy.router.openshift.io/hsts_headervalue to the edge-terminated or re-encrypt route. You can use theoc annotatetool to do this by running the following command:

```
oc annotate route <route_name> -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000;\
includeSubDomains;preload"
```

```
includeSubDomains;preload"
```

**1**
  In this example, the maximum age is set to31536000ms, which is approximately 8.5 hours.

In this example, the equal sign (=) is in quotes. This is required to properly execute the annotate command.

Example route configured with an annotation

```
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
```

```
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
```

where:

**max-age**
  Specifies the measurement of the length of time, in seconds, for the HSTS policy. If set to0, it negates the policy.

**includeSubDomains**
  Specifies that all subdomains of the host must have the same HSTS policy as the host. Optional parameter.

**preload**
  Specifies that the site is included in the HSTS preload list whenmax-ageis greater than0. For example, sites such as Google can construct a list of sites that havepreloadset. Browsers can then use these lists to determine which sites they can communicate with over HTTPS, even before they have interacted with the site. Withoutpreloadset, browsers must have interacted with the site over HTTPS, at least once, to get the header. Optional parameter.

#### 1.2.1.2. Disabling HTTP Strict Transport Security per-routeCopy linkLink copied to clipboard!

To allow unencrypted connections or troubleshoot access issues, disable HTTP Strict Transport Security (HSTS) for a specific route. Setting themax-ageroute annotation to0instructs browsers to stop enforcing HTTPS requirements on the route host.

Prerequisites

- You are logged in to the cluster with a user with administrator privileges for the project.
- You installed the OpenShift CLI (oc).

Procedure

- To disable HSTS, enter the following to set themax-agevalue in the route annotation to0:oc annotate route <route_name> -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=0"$oc annotate route<route_name>-n<namespace>--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=0"Copy to ClipboardCopied!Toggle word wrapToggle overflowYou can alternatively apply the following YAML to create the config map for disabling HSTS per-route:kind: Route
apiVersion: route.openshift.io/v1
metadata:
  annotations:
    haproxy.router.openshift.io/hsts_header: max-age=0kind:RouteapiVersion:route.openshift.io/v1metadata:annotations:haproxy.router.openshift.io/hsts_header:max-age=0Copy to ClipboardCopied!Toggle word wrapToggle overflow

To disable HSTS, enter the following to set themax-agevalue in the route annotation to0:

You can alternatively apply the following YAML to create the config map for disabling HSTS per-route:

```
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  annotations:
    haproxy.router.openshift.io/hsts_header: max-age=0
```

```
kind: Route
apiVersion: route.openshift.io/v1
metadata:
  annotations:
    haproxy.router.openshift.io/hsts_header: max-age=0
```

- To disable HSTS for every route in a namespace, enter the following command:oc annotate route --all -n <namespace> --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=0"$oc annotate route--all-n<namespace>--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=0"Copy to ClipboardCopied!Toggle word wrapToggle overflow

To disable HSTS for every route in a namespace, enter the following command:

Verification

- To query the annotation for all routes, enter the following command:oc get route  --all-namespaces -o go-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'$oc get route  --all-namespaces-ogo-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName: routename HSTS: max-age=0Name: routename HSTS: max-age=0Copy to ClipboardCopied!Toggle word wrapToggle overflow

To query the annotation for all routes, enter the following command:

Example output

#### 1.2.1.3. Enforcing HTTP Strict Transport Security per-domainCopy linkLink copied to clipboard!

To enforce HTTP Strict Transport Security (HSTS) per-domain for secure routes, add arequiredHSTSPoliciesrecord to the Ingress spec to capture the configuration of the HSTS policy.

If you configure arequiredHSTSPolicyto enforce HSTS, then any newly created route must be configured with a compliant HSTS policy annotation.

To handle upgraded clusters with non-compliant HSTS routes, you can update the manifests at the source and apply the updates.

You cannot useoc expose routeoroc create routecommands to add a route in a domain that enforces HSTS, because the API for these commands does not accept annotations.

HSTS cannot be applied to insecure, or non-TLS routes, even if HSTS is requested for all routes globally.

Prerequisites

- You are logged in to the cluster with a user with administrator privileges for the project.
- You installed the OpenShift CLI (oc).

Procedure

- Edit the Ingress configuration YAML by running the following command and updating fields as needed:oc edit ingresses.config.openshift.io/cluster$oc edit ingresses.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowExample HSTS policyapiVersion: config.openshift.io/v1
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
    includeSubDomainsPolicy: RequireNoIncludeSubDomainsapiVersion:config.openshift.io/v1kind:Ingressmetadata:name:clusterspec:domain:'hello-openshift-default.apps.username.devcluster.openshift.com'requiredHSTSPolicies:1-domainPatterns:2-'*hello-openshift-default.apps.username.devcluster.openshift.com'-'*hello-openshift-default2.apps.username.devcluster.openshift.com'namespaceSelector:3matchLabels:myPolicy:strictmaxAge:4smallestMaxAge:1largestMaxAge:31536000preloadPolicy:RequirePreload5includeSubDomainsPolicy:RequireIncludeSubDomains6-domainPatterns:-'abc.example.com'-'*xyz.example.com'namespaceSelector:matchLabels:{}maxAge:{}preloadPolicy:NoOpinionincludeSubDomainsPolicy:RequireNoIncludeSubDomainsCopy to ClipboardCopied!Toggle word wrapToggle overflow1Required.requiredHSTSPoliciesare validated in order, and the first matchingdomainPatternsapplies.2Required. You must specify at least onedomainPatternshostname. Any number of domains can be listed. You can include multiple sections of enforcing options for differentdomainPatterns.3Optional. If you includenamespaceSelector, it must match the labels of the project where the routes reside, to enforce the set HSTS policy on the routes. Routes that only match thenamespaceSelectorand not thedomainPatternsare not validated.4Required.max-agemeasures the length of time, in seconds, that the HSTS policy is in effect. This policy setting allows for a smallest and largestmax-ageto be enforced.ThelargestMaxAgevalue must be between0and2147483647. It can be left unspecified, which means no upper limit is enforced.ThesmallestMaxAgevalue must be between0and2147483647. Enter0to disable HSTS for troubleshooting, otherwise enter1if you never want HSTS to be disabled. It can be left unspecified, which means no lower limit is enforced.5Optional. Includingpreloadinhaproxy.router.openshift.io/hsts_headerallows external services to include this site in their HSTS preload lists. Browsers can then use these lists to determine which sites they can communicate with over HTTPS, before they have interacted with the site. Withoutpreloadset, browsers need to interact at least once with the site to get the header.preloadcan be set with one of the following:RequirePreload:preloadis required by theRequiredHSTSPolicy.RequireNoPreload:preloadis forbidden by theRequiredHSTSPolicy.NoOpinion:preloaddoes not matter to theRequiredHSTSPolicy.6Optional.includeSubDomainsPolicycan be set with one of the following:RequireIncludeSubDomains:includeSubDomainsis required by theRequiredHSTSPolicy.RequireNoIncludeSubDomains:includeSubDomainsis forbidden by theRequiredHSTSPolicy.NoOpinion:includeSubDomainsdoes not matter to theRequiredHSTSPolicy.

Edit the Ingress configuration YAML by running the following command and updating fields as needed:

Example HSTS policy

```
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

```
apiVersion: config.openshift.io/v1
kind: Ingress
metadata:
  name: cluster
spec:
  domain: 'hello-openshift-default.apps.username.devcluster.openshift.com'
  requiredHSTSPolicies:
```

```
- domainPatterns:
```

```
- '*hello-openshift-default.apps.username.devcluster.openshift.com'
    - '*hello-openshift-default2.apps.username.devcluster.openshift.com'
    namespaceSelector:
```

```
matchLabels:
        myPolicy: strict
    maxAge:
```

```
smallestMaxAge: 1
      largestMaxAge: 31536000
    preloadPolicy: RequirePreload
```

```
includeSubDomainsPolicy: RequireIncludeSubDomains
```

```
- domainPatterns:
    - 'abc.example.com'
    - '*xyz.example.com'
    namespaceSelector:
      matchLabels: {}
    maxAge: {}
    preloadPolicy: NoOpinion
    includeSubDomainsPolicy: RequireNoIncludeSubDomains
```

**1**
  Required.requiredHSTSPoliciesare validated in order, and the first matchingdomainPatternsapplies.

**2**
  Required. You must specify at least onedomainPatternshostname. Any number of domains can be listed. You can include multiple sections of enforcing options for differentdomainPatterns.

**3**
  Optional. If you includenamespaceSelector, it must match the labels of the project where the routes reside, to enforce the set HSTS policy on the routes. Routes that only match thenamespaceSelectorand not thedomainPatternsare not validated.

**4**
  Required.max-agemeasures the length of time, in seconds, that the HSTS policy is in effect. This policy setting allows for a smallest and largestmax-ageto be enforced.ThelargestMaxAgevalue must be between0and2147483647. It can be left unspecified, which means no upper limit is enforced.ThesmallestMaxAgevalue must be between0and2147483647. Enter0to disable HSTS for troubleshooting, otherwise enter1if you never want HSTS to be disabled. It can be left unspecified, which means no lower limit is enforced.
- ThelargestMaxAgevalue must be between0and2147483647. It can be left unspecified, which means no upper limit is enforced.
- ThesmallestMaxAgevalue must be between0and2147483647. Enter0to disable HSTS for troubleshooting, otherwise enter1if you never want HSTS to be disabled. It can be left unspecified, which means no lower limit is enforced.

**5**
  Optional. Includingpreloadinhaproxy.router.openshift.io/hsts_headerallows external services to include this site in their HSTS preload lists. Browsers can then use these lists to determine which sites they can communicate with over HTTPS, before they have interacted with the site. Withoutpreloadset, browsers need to interact at least once with the site to get the header.preloadcan be set with one of the following:RequirePreload:preloadis required by theRequiredHSTSPolicy.RequireNoPreload:preloadis forbidden by theRequiredHSTSPolicy.NoOpinion:preloaddoes not matter to theRequiredHSTSPolicy.
- RequirePreload:preloadis required by theRequiredHSTSPolicy.
- RequireNoPreload:preloadis forbidden by theRequiredHSTSPolicy.
- NoOpinion:preloaddoes not matter to theRequiredHSTSPolicy.

**6**
  Optional.includeSubDomainsPolicycan be set with one of the following:RequireIncludeSubDomains:includeSubDomainsis required by theRequiredHSTSPolicy.RequireNoIncludeSubDomains:includeSubDomainsis forbidden by theRequiredHSTSPolicy.NoOpinion:includeSubDomainsdoes not matter to theRequiredHSTSPolicy.
- RequireIncludeSubDomains:includeSubDomainsis required by theRequiredHSTSPolicy.
- RequireNoIncludeSubDomains:includeSubDomainsis forbidden by theRequiredHSTSPolicy.
- NoOpinion:includeSubDomainsdoes not matter to theRequiredHSTSPolicy.
- You can apply HSTS to all routes in the cluster or in a particular namespace by entering theoc annotate command.To apply HSTS to all routes in the cluster, enter theoc annotate command. For example:oc annotate route --all --all-namespaces --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"$oc annotate route--all--all-namespaces--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=31536000"Copy to ClipboardCopied!Toggle word wrapToggle overflowTo apply HSTS to all routes in a particular namespace, enter theoc annotate command. For example:oc annotate route --all -n my-namespace --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"$oc annotate route--all-nmy-namespace--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=31536000"Copy to ClipboardCopied!Toggle word wrapToggle overflow

You can apply HSTS to all routes in the cluster or in a particular namespace by entering theoc annotate command.

- To apply HSTS to all routes in the cluster, enter theoc annotate command. For example:oc annotate route --all --all-namespaces --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"$oc annotate route--all--all-namespaces--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=31536000"Copy to ClipboardCopied!Toggle word wrapToggle overflow

To apply HSTS to all routes in the cluster, enter theoc annotate command. For example:

- To apply HSTS to all routes in a particular namespace, enter theoc annotate command. For example:oc annotate route --all -n my-namespace --overwrite=true "haproxy.router.openshift.io/hsts_header"="max-age=31536000"$oc annotate route--all-nmy-namespace--overwrite=true"haproxy.router.openshift.io/hsts_header"="max-age=31536000"Copy to ClipboardCopied!Toggle word wrapToggle overflow

To apply HSTS to all routes in a particular namespace, enter theoc annotate command. For example:

Verification

You can review the HSTS policy you configured. For example:

- To review themaxAgeset for required HSTS policies, enter the following command:oc get clusteroperator/ingress -n openshift-ingress-operator -o jsonpath='{range .spec.requiredHSTSPolicies[*]}{.spec.requiredHSTSPolicies.maxAgePolicy.largestMaxAge}{"\n"}{end}'$oc get clusteroperator/ingress-nopenshift-ingress-operator-ojsonpath='{range .spec.requiredHSTSPolicies[*]}{.spec.requiredHSTSPolicies.maxAgePolicy.largestMaxAge}{"\n"}{end}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

To review themaxAgeset for required HSTS policies, enter the following command:

- To review the HSTS annotations on all routes, enter the following command:oc get route  --all-namespaces -o go-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'$oc get route  --all-namespaces-ogo-template='{{range .items}}{{if .metadata.annotations}}{{$a := index .metadata.annotations "haproxy.router.openshift.io/hsts_header"}}{{$n := .metadata.name}}{{with $a}}Name: {{$n}} HSTS: {{$a}}{{"\n"}}{{else}}{{""}}{{end}}{{end}}{{end}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName: <_routename_> HSTS: max-age=31536000;preload;includeSubDomainsName: <_routename_> HSTS: max-age=31536000;preload;includeSubDomainsCopy to ClipboardCopied!Toggle word wrapToggle overflow

To review the HSTS annotations on all routes, enter the following command:

Example output

## 1.3. Configuring routesCopy linkLink copied to clipboard!

To customise route configuration for specific traffic behaviors, apply annotations, headers, and cookies. By using these mechanisms, you can define granular routing rules, extending standard capabilities to meet complex application requirements.

### 1.3.1. Configuring route timeoutsCopy linkLink copied to clipboard!

You can configure the default timeouts for an existing route when you have services in need of a low timeout, which is required for Service Level Availability (SLA) purposes, or a high timeout, for cases with a slow back end.

If you configured a user-managed external load balancer in front of your OpenShift Container Platform cluster, ensure that the timeout value for the user-managed external load balancer is higher than the timeout value for the route. This configuration prevents network congestion issues over the network that your cluster uses.

Prerequisites

- You deployed an Ingress Controller on a running cluster.

Procedure

- Using theoc annotatecommand, add the timeout to the route:oc annotate route <route_name> \
    --overwrite haproxy.router.openshift.io/timeout=<timeout><time_unit>$oc annotate route<route_name>\--overwritehaproxy.router.openshift.io/timeout=<timeout><time_unit>Copy to ClipboardCopied!Toggle word wrapToggle overflow<timeout>: Supported time units are microseconds (us), milliseconds (ms), seconds (s), minutes (m), hours (h), or days (d).The following example sets a timeout of two seconds on a route namedmyroute:oc annotate route myroute --overwrite haproxy.router.openshift.io/timeout=2s$oc annotate route myroute--overwritehaproxy.router.openshift.io/timeout=2sCopy to ClipboardCopied!Toggle word wrapToggle overflow

Using theoc annotatecommand, add the timeout to the route:

```
oc annotate route <route_name> \
    --overwrite haproxy.router.openshift.io/timeout=<timeout><time_unit>
```

```
$ oc annotate route <route_name> \
    --overwrite haproxy.router.openshift.io/timeout=<timeout><time_unit>
```

- <timeout>: Supported time units are microseconds (us), milliseconds (ms), seconds (s), minutes (m), hours (h), or days (d).The following example sets a timeout of two seconds on a route namedmyroute:oc annotate route myroute --overwrite haproxy.router.openshift.io/timeout=2s$oc annotate route myroute--overwritehaproxy.router.openshift.io/timeout=2sCopy to ClipboardCopied!Toggle word wrapToggle overflow

<timeout>: Supported time units are microseconds (us), milliseconds (ms), seconds (s), minutes (m), hours (h), or days (d).

The following example sets a timeout of two seconds on a route namedmyroute:

### 1.3.2. HTTP header configurationCopy linkLink copied to clipboard!

To customize request and response headers for your applications, configure the Ingress Controller or apply specific route annotations. Understanding the interaction between these configuration methods ensures you effectively manage global and route-specific header policies.

You can also set certain headers by using route annotations. The various ways of configuring headers can present challenges when working together.

You can only set or delete headers within anIngressControllerorRouteCR, you cannot append them. If an HTTP header is set with a value, that value must be complete and not require appending in the future. In situations where it makes sense to append a header, such as the X-Forwarded-For header, use thespec.httpHeaders.forwardedHeaderPolicyfield, instead ofspec.httpHeaders.actions.

**Order of precedence**
  When the same HTTP header is modified both in the Ingress Controller and in a route, HAProxy prioritizes the actions in certain ways depending on whether it is a request or response header.For HTTP response headers, actions specified in the Ingress Controller are executed after the actions specified in a route. This means that the actions specified in the Ingress Controller take precedence.For HTTP request headers, actions specified in a route are executed after the actions specified in the Ingress Controller. This means that the actions specified in the route take precedence.

When the same HTTP header is modified both in the Ingress Controller and in a route, HAProxy prioritizes the actions in certain ways depending on whether it is a request or response header.

- For HTTP response headers, actions specified in the Ingress Controller are executed after the actions specified in a route. This means that the actions specified in the Ingress Controller take precedence.
- For HTTP request headers, actions specified in a route are executed after the actions specified in the Ingress Controller. This means that the actions specified in the route take precedence.

For example, a cluster administrator sets the X-Frame-Options response header with the valueDENYin the Ingress Controller using the following configuration:

ExampleIngressControllerspec

```
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

```
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

A route owner sets the same response header that the cluster administrator set in the Ingress Controller, but with the valueSAMEORIGINusing the following configuration:

ExampleRoutespec

```
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

```
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

When both theIngressControllerspec andRoutespec are configuring the X-Frame-Options response header, then the value set for this header at the global level in the Ingress Controller takes precedence, even if a specific route allows frames. For a request header, theRoutespec value overrides theIngressControllerspec value.

This prioritization occurs because thehaproxy.configfile uses the following logic, where the Ingress Controller is considered the front end and individual routes are considered the back end. The header valueDENYapplied to the front end configurations overrides the same header with the valueSAMEORIGINthat is set in the back end:

```
frontend public
  http-response set-header X-Frame-Options 'DENY'

frontend fe_sni
  http-response set-header X-Frame-Options 'DENY'

frontend fe_no_sni
  http-response set-header X-Frame-Options 'DENY'

backend be_secure:openshift-monitoring:alertmanager-main
  http-response set-header X-Frame-Options 'SAMEORIGIN'
```

```
frontend public
  http-response set-header X-Frame-Options 'DENY'

frontend fe_sni
  http-response set-header X-Frame-Options 'DENY'

frontend fe_no_sni
  http-response set-header X-Frame-Options 'DENY'

backend be_secure:openshift-monitoring:alertmanager-main
  http-response set-header X-Frame-Options 'SAMEORIGIN'
```

Additionally, any actions defined in either the Ingress Controller or a route override values set using route annotations.

**Special case headers**
  The following headers are either prevented entirely from being set or deleted, or allowed under specific circumstances:
| Header name | Configurable usingIngressControllerspec | Configurable usingRoutespec | Reason for disallowment | Configurable using another method |
| --- | --- | --- | --- | --- |
| proxy | No | No | TheproxyHTTP request header can be used to exploit vulnerable CGI applications by injecting the head | No |
| host | No | Yes | When thehostHTTP request header is set using theIngressControllerCR, HAProxy can fail when looking u | No |
| strict-transport-security | No | No | Thestrict-transport-securityHTTP response header is already handled using route annotations and does | Yes: thehaproxy.router.openshift.io/hsts_headerroute annotation |
| cookieandset-cookie | No | No | The cookies that HAProxy sets are used for session tracking to map client connections to particular  | Yes:thehaproxy.router.openshift.io/disable_cookieroute annotationthehaproxy.router.openshift.io/cook |

proxy

No

No

TheproxyHTTP request header can be used to exploit vulnerable CGI applications by injecting the header value into theHTTP_PROXYenvironment variable. TheproxyHTTP request header is also non-standard and prone to error during configuration.

No

host

No

Yes

When thehostHTTP request header is set using theIngressControllerCR, HAProxy can fail when looking up the correct route.

No

strict-transport-security

No

No

Thestrict-transport-securityHTTP response header is already handled using route annotations and does not need a separate implementation.

Yes: thehaproxy.router.openshift.io/hsts_headerroute annotation

cookieandset-cookie

No

No

The cookies that HAProxy sets are used for session tracking to map client connections to particular back-end servers. Allowing these headers to be set could interfere with HAProxy’s session affinity and restrict HAProxy’s ownership of a cookie.

Yes:

- thehaproxy.router.openshift.io/disable_cookieroute annotation
- thehaproxy.router.openshift.io/cookie_nameroute annotation

### 1.3.3. Setting or deleting HTTP request and response headers in a routeCopy linkLink copied to clipboard!

You can set or delete certain HTTP request and response headers for compliance purposes or other reasons. You can set or delete these headers either for all routes served by an Ingress Controller or for specific routes.

For example, you might want to enable a web application to serve content in alternate locations for specific routes if that content is written in multiple languages, even if there is a default global location specified by the Ingress Controller serving the routes.

The following procedure creates a route that sets the Content-Location HTTP request header so that the URL associated with the application,https://app.example.com, directs to the locationhttps://app.example.com/lang/en-us. Directing application traffic to this location means that anyone using that specific route is accessing web content written in American English.

Prerequisites

- You have installed the OpenShift CLI (oc).
- You are logged into an OpenShift Container Platform cluster as a project administrator.
- You have a web application that exposes a port and an HTTP or TLS endpoint listening for traffic on the port.

Procedure

- Create a route definition and save it in a file calledapp-example-route.yaml:YAML definition of the created route with HTTP header directivesapiVersion: route.openshift.io/v1
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
# ...apiVersion:route.openshift.io/v1kind:Route# ...spec:host:app.example.comtls:termination:edgeto:kind:Servicename:app-examplehttpHeaders:actions:response:-name:Content-Locationaction:type:Setset:value:/lang/en-us# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:actionsSpecifies the list of actions you want to perform on the HTTP headers.responseSpecifies the type of header you want to change. In this case, a response header.response.nameSpecifies the name of the header you want to change. For a list of available headers you can set or delete, seeHTTP header configuration.action.typeSpecifies the type of action being taken on the header. This field can have the valueSetorDelete.set.valueWhen setting HTTP headers, you must provide avalue. The value can be a string from a list of available directives for that header, for exampleDENY, or it can be a dynamic value that will be interpreted using HAProxy’s dynamic value syntax. In this case, the value is set to the relative location of the content.

Create a route definition and save it in a file calledapp-example-route.yaml:

YAML definition of the created route with HTTP header directives

```
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
# ...
```

```
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
# ...
```

where:

**actions**
  Specifies the list of actions you want to perform on the HTTP headers.

**response**
  Specifies the type of header you want to change. In this case, a response header.

**response.name**
  Specifies the name of the header you want to change. For a list of available headers you can set or delete, seeHTTP header configuration.

**action.type**
  Specifies the type of action being taken on the header. This field can have the valueSetorDelete.

**set.value**
  When setting HTTP headers, you must provide avalue. The value can be a string from a list of available directives for that header, for exampleDENY, or it can be a dynamic value that will be interpreted using HAProxy’s dynamic value syntax. In this case, the value is set to the relative location of the content.
- Create a route to your existing web application using the newly created route definition:oc -n app-example create -f app-example-route.yaml$oc-napp-example create-fapp-example-route.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowFor HTTP request headers, the actions specified in the route definitions are executed after any actions performed on HTTP request headers in the Ingress Controller. This means that any values set for those request headers in a route will take precedence over the ones set in the Ingress Controller. For more information on the processing order of HTTP headers, seeHTTP header configuration.

Create a route to your existing web application using the newly created route definition:

For HTTP request headers, the actions specified in the route definitions are executed after any actions performed on HTTP request headers in the Ingress Controller. This means that any values set for those request headers in a route will take precedence over the ones set in the Ingress Controller. For more information on the processing order of HTTP headers, seeHTTP header configuration.

### 1.3.4. Using cookies to keep route statefulnessCopy linkLink copied to clipboard!

To maintain stateful application traffic during pod restarts or scaling events, configure sticky sessions by using cookies. By using this method, you ensure that all incoming traffic reaches the same endpoint, preventing state loss even if the specific endpoint pod changes.

OpenShift Container Platform can use cookies to configure session persistence. The Ingress Controller selects an endpoint to handle any user requests, and creates a cookie for the session. The cookie is passed back in the response to the request and the user sends the cookie back with the next request in the session. The cookie tells the Ingress Controller which endpoint is handling the session, ensuring that client requests use the cookie so that they are routed to the same pod.

Cookies cannot be set on passthrough routes, because the HTTP traffic cannot be seen. Instead, a number is calculated based on the source IP address, which determines the backend.

If backends change, the traffic can be directed to the wrong server, making it less sticky. If you are using a load balancer, which hides source IP, the same number is set for all connections and traffic is sent to the same pod.

#### 1.3.4.1. Annotating a route with a cookieCopy linkLink copied to clipboard!

To enable applications to manage session persistence and load distribution, annotate the route with a custom cookie name. Overwriting the default cookie allows the backend application to identify and delete the specific cookie, forcing endpoint re-selection when necessary.

When a server is overloaded, the server tries to remove the requests from the client and redistribute the requests to other endpoints.

Procedure

- Annotate the route with the specified cookie name:oc annotate route <route_name> router.openshift.io/cookie_name="<cookie_name>"$oc annotate route<route_name>router.openshift.io/cookie_name="<cookie_name>"Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<route_name>Specifies the name of the route.<cookie_name>Specifies the name for the cookie.For example, to annotate the routemy_routewith the cookie namemy_cookie:oc annotate route my_route router.openshift.io/cookie_name="my_cookie"$oc annotate route my_route router.openshift.io/cookie_name="my_cookie"Copy to ClipboardCopied!Toggle word wrapToggle overflow

Annotate the route with the specified cookie name:

where:

**<route_name>**
  Specifies the name of the route.

**<cookie_name>**
  Specifies the name for the cookie.For example, to annotate the routemy_routewith the cookie namemy_cookie:oc annotate route my_route router.openshift.io/cookie_name="my_cookie"$oc annotate route my_route router.openshift.io/cookie_name="my_cookie"Copy to ClipboardCopied!Toggle word wrapToggle overflow

Specifies the name for the cookie.

For example, to annotate the routemy_routewith the cookie namemy_cookie:

- Capture the route hostname in a variable:ROUTE_NAME=$(oc get route <route_name> -o jsonpath='{.spec.host}')$ROUTE_NAME=$(oc get route<route_name>-ojsonpath='{.spec.host}')Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<route_name>Specifies the name of the route.

Capture the route hostname in a variable:

where:

**<route_name>**
  Specifies the name of the route.
- Save the cookie, and then access the route:curl $ROUTE_NAME -k -c /tmp/cookie_jar$curl$ROUTE_NAME-k-c/tmp/cookie_jarCopy to ClipboardCopied!Toggle word wrapToggle overflowUse the cookie saved by the previous command when connecting to the route:curl $ROUTE_NAME -k -b /tmp/cookie_jar$curl$ROUTE_NAME-k-b/tmp/cookie_jarCopy to ClipboardCopied!Toggle word wrapToggle overflow

Save the cookie, and then access the route:

Use the cookie saved by the previous command when connecting to the route:

### 1.3.5. Route-specific annotationsCopy linkLink copied to clipboard!

The Ingress Controller can set the default options for all the routes it exposes. An individual route can override some of these defaults by providing specific configurations in its annotations. Red Hat does not support adding a route annotation to an operator-managed route.

To create a whitelist with multiple source IPs or subnets, use a space-delimited list. Any other delimiter type causes the list to be ignored without a warning or error message.

| Variable | Description |
| --- | --- |
| haproxy.router.openshift.io/balance | Sets the load-balancing algorithm. Available options arerandom,source,roundrobin[1], andleastconn. T |
| haproxy.router.openshift.io/disable_cookies | Disables the use of cookies to track related connections. If set to'true'or'TRUE', the balance algor |
| router.openshift.io/cookie_name | Specifies an optional cookie to use for this route. The name must consist of any combination of uppe |
| haproxy.router.openshift.io/pod-concurrent-connections | Sets the maximum number of connections that are allowed to a backing pod from a router.Note: If ther |
| haproxy.router.openshift.io/rate-limit-connections | Setting'true'or'TRUE'enables rate limiting functionality which is implemented through stick-tables o |
| haproxy.router.openshift.io/rate-limit-connections.concurrent-tcp | Limits the number of concurrent TCP connections made through the same source IP address. It accepts  |
| haproxy.router.openshift.io/rate-limit-connections.rate-http | Limits the rate at which a client with the same source IP address can make HTTP requests. It accepts |
| haproxy.router.openshift.io/rate-limit-connections.rate-tcp | Limits the rate at which a client with the same source IP address can make TCP connections. It accep |
| router.openshift.io/haproxy.health.check.interval | Sets the interval for the back-end health checks. (TimeUnits) |
| haproxy.router.openshift.io/ip_whitelist | Sets an allowlist for the route. The allowlist is a space-separated list of IP addresses and CIDR ra |
| haproxy.router.openshift.io/hsts_header | Sets a Strict-Transport-Security header for the edge terminated or re-encrypt route. |
| haproxy.router.openshift.io/rewrite-target | Sets the rewrite path of the request on the backend. |
| router.openshift.io/cookie-same-site | Sets a value to restrict cookies. The values are:Lax: the browser does not send cookies on cross-sit |
| haproxy.router.openshift.io/set-forwarded-headers | Sets the policy for handling theForwardedandX-Forwarded-ForHTTP headers per route. The values are:ap |

haproxy.router.openshift.io/balance

Sets the load-balancing algorithm. Available options arerandom,source,roundrobin[1], andleastconn. The default value issourcefor TLS passthrough routes. For all other routes, the default israndom.

haproxy.router.openshift.io/disable_cookies

Disables the use of cookies to track related connections. If set to'true'or'TRUE', the balance algorithm is used to choose which back-end serves connections for each incoming HTTP request.

router.openshift.io/cookie_name

Specifies an optional cookie to use for this route. The name must consist of any combination of upper and lower case letters, digits, "_", and "-". The default is the hashed internal key name for the route.

haproxy.router.openshift.io/pod-concurrent-connections

Sets the maximum number of connections that are allowed to a backing pod from a router.Note: If there are multiple pods, each can have this many connections. If you have multiple routers, there is no coordination among them, each may connect this many times. If not set, or set to 0, there is no limit.

haproxy.router.openshift.io/rate-limit-connections

Setting'true'or'TRUE'enables rate limiting functionality which is implemented through stick-tables on the specific backend per route.Note: Using this annotation provides basic protection against denial-of-service attacks.

haproxy.router.openshift.io/rate-limit-connections.concurrent-tcp

Limits the number of concurrent TCP connections made through the same source IP address. It accepts a numeric value.Note: Using this annotation provides basic protection against denial-of-service attacks.

haproxy.router.openshift.io/rate-limit-connections.rate-http

Limits the rate at which a client with the same source IP address can make HTTP requests. It accepts a numeric value.Note: Using this annotation provides basic protection against denial-of-service attacks.

haproxy.router.openshift.io/rate-limit-connections.rate-tcp

Limits the rate at which a client with the same source IP address can make TCP connections. It accepts a numeric value.

router.openshift.io/haproxy.health.check.interval

Sets the interval for the back-end health checks. (TimeUnits)

haproxy.router.openshift.io/ip_whitelist

Sets an allowlist for the route. The allowlist is a space-separated list of IP addresses and CIDR ranges for the approved source addresses. Requests from IP addresses that are not in the allowlist are dropped.

The maximum number of IP addresses and CIDR ranges directly visible in thehaproxy.configfile is 61. [2]

haproxy.router.openshift.io/hsts_header

Sets a Strict-Transport-Security header for the edge terminated or re-encrypt route.

haproxy.router.openshift.io/rewrite-target

Sets the rewrite path of the request on the backend.

router.openshift.io/cookie-same-site

Sets a value to restrict cookies. The values are:

Lax: the browser does not send cookies on cross-site requests, but does send cookies when users navigate to the origin site from an external site. This is the default browser behavior when theSameSitevalue is not specified.

Strict: the browser sends cookies only for same-site requests.

None: the browser sends cookies for both cross-site and same-site requests.

This value is applicable to re-encrypt and edge routes only. For more information, see theSameSite cookies documentation.

haproxy.router.openshift.io/set-forwarded-headers

Sets the policy for handling theForwardedandX-Forwarded-ForHTTP headers per route. The values are:

append: appends the header, preserving any existing header. This is the default value.

replace: sets the header, removing any existing header.

never: never sets the header, but preserves any existing header.

if-none: sets the header if it is not already set.

- By default, the router reloads every 5 s which resets the balancing connection across pods from the beginning. As a result, theroundrobinstate is not preserved across reloads. This algorithm works best when pods have nearly identical computing capabilites and storage capacity. If your application or service has continuously changing endpoints, for example, due to the use of a CI/CD pipeline, uneven balancing can result. In this case, use a different algorithm.
- If the number of IP addresses and CIDR ranges in an allowlist exceeds 61, they are written into a separate file that is then referenced from thehaproxy.configfile. This file is stored in the/var/lib/haproxy/router/allowlistsfolder.To ensure that the addresses are written to the allowlist, check that the full list of CIDR ranges are listed in the Ingress Controller configuration file. The etcd object size limit restricts how large a route annotation can be. Because of this, it creates a threshold for the maximum number of IP addresses and CIDR ranges that you can include in an allowlist.

If the number of IP addresses and CIDR ranges in an allowlist exceeds 61, they are written into a separate file that is then referenced from thehaproxy.configfile. This file is stored in the/var/lib/haproxy/router/allowlistsfolder.

To ensure that the addresses are written to the allowlist, check that the full list of CIDR ranges are listed in the Ingress Controller configuration file. The etcd object size limit restricts how large a route annotation can be. Because of this, it creates a threshold for the maximum number of IP addresses and CIDR ranges that you can include in an allowlist.

A route that allows only one specific IP address

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP]
```

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP]
```

A route that allows several IP addresses

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP] [REDACTED_PRIVATE_IP] [REDACTED_PRIVATE_IP]
```

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP] [REDACTED_PRIVATE_IP] [REDACTED_PRIVATE_IP]
```

A route that allows an IP address CIDR network

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP]/24
```

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: [REDACTED_PRIVATE_IP]/24
```

A route that allows both IP an address and IP address CIDR networks

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: 180.5.61.153 [REDACTED_PRIVATE_IP]/24 [REDACTED_PRIVATE_IP]/8
```

```
metadata:
  annotations:
    haproxy.router.openshift.io/ip_whitelist: 180.5.61.153 [REDACTED_PRIVATE_IP]/24 [REDACTED_PRIVATE_IP]/8
```

A route specifying a rewrite target

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  annotations:
    haproxy.router.openshift.io/rewrite-target: / 
...
```

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  annotations:
    haproxy.router.openshift.io/rewrite-target: /
```

```
...
```

**1**
  Sets/as rewrite path of the request on the backend.

Setting thehaproxy.router.openshift.io/rewrite-targetannotation on a route specifies that the Ingress Controller should rewrite paths in HTTP requests using this route before forwarding the requests to the backend application. The part of the request path that matches the path specified inspec.pathis replaced with the rewrite target specified in the annotation.

The following table provides examples of the path rewriting behavior for various combinations ofspec.path, request path, and rewrite target.

| Route.spec.path | Request path | Rewrite target | Forwarded request path |
| --- | --- | --- | --- |
| /foo | /foo | / | / |
| /foo | /foo/ | / | / |
| /foo | /foo/bar | / | /bar |
| /foo | /foo/bar/ | / | /bar/ |
| /foo | /foo | /bar | /bar |
| /foo | /foo/ | /bar | /bar/ |
| /foo | /foo/bar | /baz | /baz/bar |
| /foo | /foo/bar/ | /baz | /baz/bar/ |
| /foo/ | /foo | / | N/A (request path does not match route path) |
| /foo/ | /foo/ | / | / |
| /foo/ | /foo/bar | / | /bar |

/foo

/foo

/

/

/foo

/foo/

/

/

/foo

/foo/bar

/

/bar

/foo

/foo/bar/

/

/bar/

/foo

/foo

/bar

/bar

/foo

/foo/

/bar

/bar/

/foo

/foo/bar

/baz

/baz/bar

/foo

/foo/bar/

/baz

/baz/bar/

/foo/

/foo

/

N/A (request path does not match route path)

/foo/

/foo/

/

/

/foo/

/foo/bar

/

/bar

Certain special characters inhaproxy.router.openshift.io/rewrite-targetrequire special handling because they must be escaped properly. Refer to the following table to understand how these characters are handled.

| For character | Use characters | Notes |
| --- | --- | --- |
| # | \# | Avoid # because it terminates the rewrite expression |
| % | % or %% | Avoid odd sequences such as %%% |
| ‘ | \’ | Avoid ‘ because it is ignored |

#

\#

Avoid # because it terminates the rewrite expression

%

% or %%

Avoid odd sequences such as %%%

‘

\’

Avoid ‘ because it is ignored

All other valid URL characters can be used without escaping.

### 1.3.6. Throughput issue troubleshooting methodsCopy linkLink copied to clipboard!

To diagnose and resolve network throughput issues, such as unusually high latency between specific services, apply troubleshooting methods. Identifying connectivity bottlenecks helps ensure stable application performance within OpenShift Container Platform.

If pod logs do not reveal any cause of the problem, use the following methods to analyze performance issues:

- Use a packet analyzer, such aspingortcpdumpto analyze traffic between a pod and its node.For example,run thetcpdumptool on each podwhile reproducing the behavior that led to the issue. Review the captures on both sides to compare send and receive timestamps to analyze the latency of traffic to and from a pod. Latency can occur in OpenShift Container Platform if a node interface is overloaded with traffic from other pods, storage devices, or the data plane.tcpdump -s 0 -i any -w /tmp/dump.pcap host <podip 1> && host <podip 2>$tcpdump-s0-iany-w/tmp/dump.pcaphost<podip1>&&host<podip2>1Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:podipSpecifies the IP address for the pod. Run theoc get pod <pod_name> -o widecommand to get the IP address of a pod.Thetcpdumpcommand generates a file at/tmp/dump.pcapcontaining all traffic between these two pods. You can run the analyzer shortly before the issue is reproduced and stop the analyzer shortly after the issue is finished reproducing to minimize the size of the file. You can alsorun a packet analyzer between the nodeswith:tcpdump -s 0 -i any -w /tmp/dump.pcap port 4789$tcpdump-s0-iany-w/tmp/dump.pcap port4789Copy to ClipboardCopied!Toggle word wrapToggle overflow

Use a packet analyzer, such aspingortcpdumpto analyze traffic between a pod and its node.

For example,run thetcpdumptool on each podwhile reproducing the behavior that led to the issue. Review the captures on both sides to compare send and receive timestamps to analyze the latency of traffic to and from a pod. Latency can occur in OpenShift Container Platform if a node interface is overloaded with traffic from other pods, storage devices, or the data plane.

where:

**podip**
  Specifies the IP address for the pod. Run theoc get pod <pod_name> -o widecommand to get the IP address of a pod.Thetcpdumpcommand generates a file at/tmp/dump.pcapcontaining all traffic between these two pods. You can run the analyzer shortly before the issue is reproduced and stop the analyzer shortly after the issue is finished reproducing to minimize the size of the file. You can alsorun a packet analyzer between the nodeswith:tcpdump -s 0 -i any -w /tmp/dump.pcap port 4789$tcpdump-s0-iany-w/tmp/dump.pcap port4789Copy to ClipboardCopied!Toggle word wrapToggle overflow

Specifies the IP address for the pod. Run theoc get pod <pod_name> -o widecommand to get the IP address of a pod.

Thetcpdumpcommand generates a file at/tmp/dump.pcapcontaining all traffic between these two pods. You can run the analyzer shortly before the issue is reproduced and stop the analyzer shortly after the issue is finished reproducing to minimize the size of the file. You can alsorun a packet analyzer between the nodeswith:

- Use a bandwidth measuring tool, such asiperf, to measure streaming throughput and UDP throughput. Locate any bottlenecks by running the tool from the pods first, and then running it from the nodes.For information on installing and usingiperf, see thisRed Hat Solution.

Use a bandwidth measuring tool, such asiperf, to measure streaming throughput and UDP throughput. Locate any bottlenecks by running the tool from the pods first, and then running it from the nodes.

- For information on installing and usingiperf, see thisRed Hat Solution.
- In some cases, the cluster might mark the node with the router pod as unhealthy due to latency issues. Use worker latency profiles to adjust the frequency that the cluster waits for a status update from the node before taking action.
- If your cluster has designated lower-latency and higher-latency nodes, configure thespec.nodePlacementfield in the Ingress Controller to control the placement of the router pod.

### 1.3.7. Configuring the route admission policyCopy linkLink copied to clipboard!

Administrators and application developers can run applications in multiple namespaces with the same domain name. This is for organizations where multiple teams develop microservices that are exposed on the same hostname.

Allowing claims across namespaces should only be enabled for clusters with trust between namespaces, otherwise a malicious user could take over a hostname. For this reason, the default admission policy disallows hostname claims across namespaces.

Prerequisites

- Cluster administrator privileges.

Procedure

- Edit the.spec.routeAdmissionfield of theingresscontrollerresource variable using the following command:oc -n openshift-ingress-operator patch ingresscontroller/default --patch '{"spec":{"routeAdmission":{"namespaceOwnership":"InterNamespaceAllowed"}}}' --type=merge$oc-nopenshift-ingress-operator patch ingresscontroller/default--patch'{"spec":{"routeAdmission":{"namespaceOwnership":"InterNamespaceAllowed"}}}'--type=mergeCopy to ClipboardCopied!Toggle word wrapToggle overflowSample Ingress Controller configurationspec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
...spec:routeAdmission:namespaceOwnership:InterNamespaceAllowed...Copy to ClipboardCopied!Toggle word wrapToggle overflowYou can alternatively apply the following YAML to configure the route admission policy:apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowedapiVersion:operator.openshift.io/v1kind:IngressControllermetadata:name:defaultnamespace:openshift-ingress-operatorspec:routeAdmission:namespaceOwnership:InterNamespaceAllowedCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit the.spec.routeAdmissionfield of theingresscontrollerresource variable using the following command:

Sample Ingress Controller configuration

```
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
...
```

```
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
...
```

You can alternatively apply the following YAML to configure the route admission policy:

```
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
```

```
apiVersion: operator.openshift.io/v1
kind: IngressController
metadata:
  name: default
  namespace: openshift-ingress-operator
spec:
  routeAdmission:
    namespaceOwnership: InterNamespaceAllowed
```

### 1.3.8. Configuring the OpenShift Container Platform Ingress Controller for dual-stack networkingCopy linkLink copied to clipboard!

If your OpenShift Container Platform cluster is configured for IPv4 and IPv6 dual-stack networking, your cluster is externally reachable by OpenShift Container Platform routes.

The Ingress Controller automatically serves services that have both IPv4 and IPv6 endpoints, but you can configure the Ingress Controller for single-stack or dual-stack services.

Prerequisites

- You deployed an OpenShift Container Platform cluster on bare metal.
- You installed the OpenShift CLI (oc).

Procedure

- To have the Ingress Controller serve traffic over IPv4/IPv6 to a workload, you can create a service YAML file or modify an existing service YAML file by setting theipFamiliesandipFamilyPolicyfields. For example:Sample service YAML fileapiVersion: v1
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
  clusterIP: [REDACTED_PRIVATE_IP]/16
  clusterIPs: 
  - [REDACTED_PRIVATE_IP]/16
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
  loadbalancer: {}apiVersion:v1kind:Servicemetadata:creationTimestamp:yyyy-mm-ddT00:00:00Zlabels:name:<service_name>manager:kubectl-createoperation:Updatetime:yyyy-mm-ddT00:00:00Zname:<service_name>namespace:<namespace_name>resourceVersion:"<resource_version_number>"selfLink:"/api/v1/namespaces/<namespace_name>/services/<service_name>"uid:<uid_number>spec:clusterIP:[REDACTED_PRIVATE_IP]/16clusterIPs:1-[REDACTED_PRIVATE_IP]/16-<second_IP_address>ipFamilies:2-IPv4-IPv6ipFamilyPolicy:RequireDualStack3ports:-port:8080protocol:TCPtargetport:8080selector:name:<namespace_name>sessionAffinity:Nonetype:ClusterIPstatus:loadbalancer:{}Copy to ClipboardCopied!Toggle word wrapToggle overflow11In a dual-stack instance, there are two differentclusterIPsprovided.2For a single-stack instance, enterIPv4orIPv6. For a dual-stack instance, enter bothIPv4andIPv6.3For a single-stack instance, enterSingleStack. For a dual-stack instance, enterRequireDualStack.These resources generate correspondingendpoints. The Ingress Controller now watchesendpointslices.

To have the Ingress Controller serve traffic over IPv4/IPv6 to a workload, you can create a service YAML file or modify an existing service YAML file by setting theipFamiliesandipFamilyPolicyfields. For example:

Sample service YAML file

```
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
  clusterIP: [REDACTED_PRIVATE_IP]/16
  clusterIPs: 
  - [REDACTED_PRIVATE_IP]/16
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

```
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
  clusterIP: [REDACTED_PRIVATE_IP]/16
  clusterIPs:
```

```
- [REDACTED_PRIVATE_IP]/16
  - <second_IP_address>
  ipFamilies:
```

```
- IPv4
  - IPv6
  ipFamilyPolicy: RequireDualStack
```

```
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

**11**
  In a dual-stack instance, there are two differentclusterIPsprovided.

**2**
  For a single-stack instance, enterIPv4orIPv6. For a dual-stack instance, enter bothIPv4andIPv6.

**3**
  For a single-stack instance, enterSingleStack. For a dual-stack instance, enterRequireDualStack.

These resources generate correspondingendpoints. The Ingress Controller now watchesendpointslices.

- To viewendpoints, enter the following command:oc get endpoints$oc get endpointsCopy to ClipboardCopied!Toggle word wrapToggle overflow

To viewendpoints, enter the following command:

- To viewendpointslices, enter the following command:oc get endpointslices$oc get endpointslicesCopy to ClipboardCopied!Toggle word wrapToggle overflow

To viewendpointslices, enter the following command:

## 1.4. Creating advanced routesCopy linkLink copied to clipboard!

To secure application traffic and serve custom certificates to clients, configure routes by using edge, passthrough, or re-encrypt TLS termination. By using these methods, you can define granular encryption rules, ensuring that traffic is decrypted and re-encrypted according to your specific security requirements.

### 1.4.1. Creating an edge route with a custom certificateCopy linkLink copied to clipboard!

To secure traffic by using a custom certificate, configure a route with edge TLS termination by running theoc create routecommand. This configuration terminates encryption at the Ingress Controller before forwarding traffic to the destination pod.

The route specifies the TLS certificate and key that the Ingress Controller uses for the route.

Prerequisites

- You must have a certificate/key pair in PEM-encoded files, where the certificate is valid for the route host.
- You may have a separate CA certificate in a PEM-encoded file that completes the certificate chain.

Password protected key files are not supported. To remove a passphrase from a key file, use the following command:

Procedure

This procedure creates aRouteresource with a custom certificate and edge TLS termination. The following assumes that the certificate/key pair are in thetls.crtandtls.keyfiles in the current working directory. You may also specify a CA certificate if needed to complete the certificate chain. Substitute the actual path names fortls.crt,tls.key, and (optionally)ca.crt. Substitute the name of the service that you want to expose forfrontend. Substitute the appropriate hostname forwww.example.com.

- Create a secureRouteresource using edge TLS termination and a custom certificate.oc create route edge --service=frontend --cert=tls.crt --key=tls.key --ca-cert=ca.crt --hostname=www.example.com$oc create route edge--service=frontend--cert=tls.crt--key=tls.key --ca-cert=ca.crt--hostname=www.example.comCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you examine the resultingRouteresource, the resource should have a configuration similar to the following example:YAML Definition of the Secure RouteapiVersion: route.openshift.io/v1
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
# ...apiVersion:route.openshift.io/v1kind:Routemetadata:name:frontendspec:host:www.example.comto:kind:Servicename:frontendtls:termination:edgekey:|------BEGIN PRIVATE KEY-----[...]-----END PRIVATE KEY-----certificate:|------BEGIN CERTIFICATE-----[...]-----END CERTIFICATE-----caCertificate:|------BEGIN CERTIFICATE-----[...]-----END CERTIFICATE-----# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowSeeoc create route edge --helpfor more options.

Create a secureRouteresource using edge TLS termination and a custom certificate.

If you examine the resultingRouteresource, the resource should have a configuration similar to the following example:

YAML Definition of the Secure Route

```
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
# ...
```

```
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
# ...
```

Seeoc create route edge --helpfor more options.

### 1.4.2. Creating a re-encrypt route with a custom certificateCopy linkLink copied to clipboard!

To secure traffic by using a custom certificate, configure a route with re-encrypt TLS termination by running theoc create routecommand. This configuration enables the Ingress Controller to decrypt traffic, and then re-encrypt traffic before forwarding the traffic to the destination pod.

Prerequisites

- You must have a certificate/key pair in PEM-encoded files, where the certificate is valid for the route host.
- You may have a separate CA certificate in a PEM-encoded file that completes the certificate chain.
- You must have a separate destination CA certificate in a PEM-encoded file.
- You must have a service that you want to expose.

Password protected key files are not supported. To remove a passphrase from a key file, use the following command:

Procedure

This procedure creates aRouteresource with a custom certificate and reencrypt TLS termination. The following assumes that the certificate/key pair are in thetls.crtandtls.keyfiles in the current working directory. You must also specify a destination CA certificate to enable the Ingress Controller to trust the service’s certificate. You may also specify a CA certificate if needed to complete the certificate chain. Substitute the actual path names fortls.crt,tls.key,cacert.crt, and (optionally)ca.crt. Substitute the name of theServiceresource that you want to expose forfrontend. Substitute the appropriate hostname forwww.example.com.

- Create a secureRouteresource using reencrypt TLS termination and a custom certificate:oc create route reencrypt --service=frontend --cert=tls.crt --key=tls.key --dest-ca-cert=destca.crt --ca-cert=ca.crt --hostname=www.example.com$oc create route reencrypt--service=frontend--cert=tls.crt--key=tls.key --dest-ca-cert=destca.crt --ca-cert=ca.crt--hostname=www.example.comCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you examine the resultingRouteresource, the resource should have a configuration similar to the following example:YAML Definition of the Secure RouteapiVersion: route.openshift.io/v1
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
# ...apiVersion:route.openshift.io/v1kind:Routemetadata:name:frontendspec:host:www.example.comto:kind:Servicename:frontendtls:termination:reencryptkey:|------BEGIN PRIVATE KEY-----[...]-----END PRIVATE KEY-----certificate:|------BEGIN CERTIFICATE-----[...]-----END CERTIFICATE-----caCertificate:|------BEGIN CERTIFICATE-----[...]-----END CERTIFICATE-----destinationCACertificate:|------BEGIN CERTIFICATE-----[...]-----END CERTIFICATE-----# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowSeeoc create route reencrypt --helpfor more options.

Create a secureRouteresource using reencrypt TLS termination and a custom certificate:

If you examine the resultingRouteresource, the resource should have a configuration similar to the following example:

YAML Definition of the Secure Route

```
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
# ...
```

```
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
# ...
```

Seeoc create route reencrypt --helpfor more options.

### 1.4.3. Creating a passthrough routeCopy linkLink copied to clipboard!

To send encrypted traffic directly to the destination without decryption at the router, configure a route with passthrough termination by running theoc create routecommand. This configuration requires no key or certificate on the route, as the destination pod handles TLS termination.

Prerequisites

- You must have a service that you want to expose.

Procedure

- Create aRouteresource:oc create route passthrough route-passthrough-secured --service=frontend --port=8080$oc create route passthrough route-passthrough-secured--service=frontend--port=8080Copy to ClipboardCopied!Toggle word wrapToggle overflowIf you examine the resultingRouteresource, it should look similar to the following:A Secured Route Using Passthrough TerminationapiVersion: route.openshift.io/v1
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
    name: frontendapiVersion:route.openshift.io/v1kind:Routemetadata:name:route-passthrough-securedspec:host:www.example.comport:targetPort:8080tls:termination:passthroughinsecureEdgeTerminationPolicy:Noneto:kind:Servicename:frontendCopy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies the name of the object, which is limited to 63 characters.tls.terminationSpecifies theterminationfield is set topassthrough. This is the only requiredtlsfield.tls.insecureEdgeTerminationPolicySpecifies the type of edge termination policy. Optional parameter. The only valid values areNone,Redirect, or empty for disabled.The destination pod is responsible for serving certificates for the traffic at the endpoint. This is currently the only method that can support requiring client certificates, also known as two-way authentication.

Create aRouteresource:

If you examine the resultingRouteresource, it should look similar to the following:

A Secured Route Using Passthrough Termination

```
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

```
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

where:

**metadata.name**
  Specifies the name of the object, which is limited to 63 characters.

**tls.termination**
  Specifies theterminationfield is set topassthrough. This is the only requiredtlsfield.

**tls.insecureEdgeTerminationPolicy**
  Specifies the type of edge termination policy. Optional parameter. The only valid values areNone,Redirect, or empty for disabled.The destination pod is responsible for serving certificates for the traffic at the endpoint. This is currently the only method that can support requiring client certificates, also known as two-way authentication.

Specifies the type of edge termination policy. Optional parameter. The only valid values areNone,Redirect, or empty for disabled.

The destination pod is responsible for serving certificates for the traffic at the endpoint. This is currently the only method that can support requiring client certificates, also known as two-way authentication.

### 1.4.4. Creating a route using the destination CA certificate in the Ingress annotationCopy linkLink copied to clipboard!

To define a route with a custom destination CA certificate, apply theroute.openshift.io/destination-ca-certificate-secretannotation to an Ingress object. This configuration ensures the Ingress Controller uses the specified secret to verify the identity of the destination service.

Prerequisites

- You have a certificate/key pair in PEM-encoded files, where the certificate is valid for the route host.
- You have a separate CA certificate in a PEM-encoded file that completes the certificate chain.
- You have a separate destination CA certificate in a PEM-encoded file.
- You have a service that you want to expose.

Procedure

- Create a secret for the destination CA certificate by entering the following command:oc create secret generic dest-ca-cert --from-file=tls.crt=<file_path>$oc create secret generic dest-ca-cert --from-file=tls.crt=<file_path>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc -n test-ns create secret generic dest-ca-cert --from-file=tls.crt=tls.crt$oc-ntest-ns create secret generic dest-ca-cert --from-file=tls.crt=tls.crtCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputsecret/dest-ca-cert createdsecret/dest-ca-cert createdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a secret for the destination CA certificate by entering the following command:

For example:

Example output

- Add theroute.openshift.io/destination-ca-certificate-secretto the Ingress annotations:apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
...apiVersion:networking.k8s.io/v1kind:Ingressmetadata:name:frontendannotations:route.openshift.io/termination:"reencrypt"route.openshift.io/destination-ca-certificate-secret:[REDACTED_SECRET] to ClipboardCopied!Toggle word wrapToggle overflowwhere:destination-ca-certificate-secretSpecifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation references a Kubernetes secret.The Ingress Controller inserts a secret that is referenced in the annotation into the generated route.Example outputapiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: reencrypt
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
spec:
...
  tls:
    insecureEdgeTerminationPolicy: Redirect
    termination: reencrypt
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
...apiVersion:route.openshift.io/v1kind:Routemetadata:name:frontendannotations:route.openshift.io/termination:reencryptroute.openshift.io/destination-ca-certificate-secret:[REDACTED_SECRET] CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Add theroute.openshift.io/destination-ca-certificate-secretto the Ingress annotations:

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
...
```

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: "reencrypt"
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
...
```

where:

**destination-ca-certificate-secret**
  Specifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation references a Kubernetes secret.The Ingress Controller inserts a secret that is referenced in the annotation into the generated route.Example outputapiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: reencrypt
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
spec:
...
  tls:
    insecureEdgeTerminationPolicy: Redirect
    termination: reencrypt
    destinationCACertificate: |
      -----BEGIN CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----
...apiVersion:route.openshift.io/v1kind:Routemetadata:name:frontendannotations:route.openshift.io/termination:reencryptroute.openshift.io/destination-ca-certificate-secret:[REDACTED_SECRET] CERTIFICATE-----
      [...]
      -----END CERTIFICATE-----...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Specifies theroute.openshift.io/destination-ca-certificate-secretannotation. The annotation references a Kubernetes secret.

The Ingress Controller inserts a secret that is referenced in the annotation into the generated route.

Example output

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: reencrypt
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
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

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: frontend
  annotations:
    route.openshift.io/termination: reencrypt
    route.openshift.io/destination-ca-certificate-secret: [REDACTED_SECRET]
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

### 1.4.5. Creating a route with externally managed certificateCopy linkLink copied to clipboard!

Securing route with external certificates in TLS secrets is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

You can configure OpenShift Container Platform routes with third-party certificate management solutions by using the.spec.tls.externalCertificatefield of the route API. You can reference externally managed TLS certificates via secrets, eliminating the need for manual certificate management.

By using the externally managed certificate, you can reduce errors to ensure a smoother rollout of certificate updates and enable the OpenShift router to serve renewed certificates promptly. You can use externally managed certificates with both edge routes and re-encrypt routes.

This feature applies to both edge routes and re-encrypt routes.

Prerequisites

- You must enable theRouteExternalCertificatefeature gate.
- You havecreatepermission on theroutes/custom-hostsub-resource, which is used for both creating and updating routes.
- You must have a secret containing a valid certificate or key pair in PEM-encoded format of typekubernetes.io/tls, which includes bothtls.keyandtls.crtkeys. Example command:$ oc create secret tls myapp-tls --cert=server.crt --key=server.key.

Procedure

- Create aroleobject in the same namespace as the secret to allow the router service account read access by running the following command:oc create role secret-reader --verb=get,list,watch --resource=secrets --resource-name=<secret-name> \
--namespace=<current-namespace>$oc create role secret-reader--verb=get,list,watch--resource=secrets --resource-name=<secret-name>\--namespace=<current-namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow<secret-name>: Specify the actual name of your secret.<current-namespace>: Specify the namespace where both your secret and route reside.

Create aroleobject in the same namespace as the secret to allow the router service account read access by running the following command:

```
oc create role secret-reader --verb=get,list,watch --resource=secrets --resource-name=<secret-name> \
--namespace=<current-namespace>
```

```
$ oc create role secret-reader --verb=get,list,watch --resource=secrets --resource-name=<secret-name> \
--namespace=<current-namespace>
```

- <secret-name>: Specify the actual name of your secret.
- <current-namespace>: Specify the namespace where both your secret and route reside.
- Create arolebindingobject in the same namespace as the secret and bind the router service account to the newly created role by running the following command:oc create rolebinding secret-reader-binding --role=secret-reader --serviceaccount=openshift-ingress:router --namespace=<current-namespace>$oc create rolebinding secret-reader-binding--role=secret-reader--serviceaccount=openshift-ingress:router--namespace=<current-namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow<current-namespace>: Specify the namespace where both your secret and route reside.

Create arolebindingobject in the same namespace as the secret and bind the router service account to the newly created role by running the following command:

- <current-namespace>: Specify the namespace where both your secret and route reside.
- Create a YAML file that defines therouteand specifies the secret containing your certificate using the following example.YAML definition of the secure routeapiVersion: route.openshift.io/v1
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
[...]apiVersion:route.openshift.io/v1kind:Routemetadata:name:myedgenamespace:testspec:host:myedge-test.apps.example.comtls:externalCertificate:name:<secret-name>termination:edge[...][...]Copy to ClipboardCopied!Toggle word wrapToggle overflow<secret-name>: Specify the actual name of your secret.

Create a YAML file that defines therouteand specifies the secret containing your certificate using the following example.

YAML definition of the secure route

```
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

```
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

- <secret-name>: Specify the actual name of your secret.
- Create arouteresource by running the following command. If the secret exists and has a certificate/key pair, the router serves the generated certificate if all prerequisites are met.oc apply -f <route.yaml>$oc apply-f<route.yaml>1Copy to ClipboardCopied!Toggle word wrapToggle overflow<route.yaml>: Specify the generated YAML filename.

Create arouteresource by running the following command. If the secret exists and has a certificate/key pair, the router serves the generated certificate if all prerequisites are met.

- <route.yaml>: Specify the generated YAML filename.

If.spec.tls.externalCertificateis not provided, the router uses default generated certificates.

You cannot provide the.spec.tls.certificatefield or the.spec.tls.keyfield when using the.spec.tls.externalCertificatefield.

### 1.4.6. Creating a route using the default certificate through an Ingress objectCopy linkLink copied to clipboard!

To generate a secure, edge-terminated route that uses the default ingress certificate, specify an empty TLS configuration in the Ingress object. This configuration overrides the default behavior, preventing the creation of an insecure route.

Prerequisites

- You have a service that you want to expose.
- You have access to the OpenShift CLI (oc).

Procedure

- Create a YAML file for the Ingress object. In the following example, the file is calledexample-ingress.yaml:YAML definition of an Ingress objectapiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: frontend
  ...
spec:
  rules:
    ...
  tls:
  - {}apiVersion:networking.k8s.io/v1kind:Ingressmetadata:name:frontend...spec:rules:...tls:-{}Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.tlsSpecifies the TLS configuration. Use the exact syntax shown to specify TLS without specifying a custom certificate.

Create a YAML file for the Ingress object. In the following example, the file is calledexample-ingress.yaml:

YAML definition of an Ingress object

```
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

```
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

where:

**spec.tls**
  Specifies the TLS configuration. Use the exact syntax shown to specify TLS without specifying a custom certificate.
- Create the Ingress object by running the following command:oc create -f example-ingress.yaml$oc create-fexample-ingress.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the Ingress object by running the following command:

Verification

- Verify that OpenShift Container Platform has created the expected route for the Ingress object by running the following command:oc get routes -o yaml$oc get routes-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: v1
items:
- apiVersion: route.openshift.io/v1
  kind: Route
  metadata:
    name: frontend-j9sdd
# ...
  spec:
  ...
    tls:
      insecureEdgeTerminationPolicy: Redirect
      termination: edge
# ...apiVersion:v1items:-apiVersion:route.openshift.io/v1kind:Routemetadata:name:frontend-j9sdd# ...spec:...tls:insecureEdgeTerminationPolicy:Redirecttermination:edge# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies the name of the route, which includes the name of the Ingress object followed by a random suffix.spec.tlsTo use the default certificate, the route should not specifyspec.certificate.tls.terminationSpecifies the termination policy for the route. The route should specify theedgetermination policy.

Verify that OpenShift Container Platform has created the expected route for the Ingress object by running the following command:

Example output

```
apiVersion: v1
items:
- apiVersion: route.openshift.io/v1
  kind: Route
  metadata:
    name: frontend-j9sdd
# ...
  spec:
  ...
    tls:
      insecureEdgeTerminationPolicy: Redirect
      termination: edge
# ...
```

```
apiVersion: v1
items:
- apiVersion: route.openshift.io/v1
  kind: Route
  metadata:
    name: frontend-j9sdd
# ...
  spec:
  ...
    tls:
      insecureEdgeTerminationPolicy: Redirect
      termination: edge
# ...
```

where:

**metadata.name**
  Specifies the name of the route, which includes the name of the Ingress object followed by a random suffix.

**spec.tls**
  To use the default certificate, the route should not specifyspec.certificate.

**tls.termination**
  Specifies the termination policy for the route. The route should specify theedgetermination policy.
