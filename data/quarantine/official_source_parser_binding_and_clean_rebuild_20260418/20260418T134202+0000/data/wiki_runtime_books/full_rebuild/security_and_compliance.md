# 보안 및 컴플라이언스

### Security overview

It is important to understand how to properly secure various aspects of your {product-title} cluster.

#### Container security

A good starting point to understanding {product-title} security is to review the concepts in xref:../security/container_security/security-understanding.adoc#security-understanding[Understanding container security]. This and subsequent sections provide a high-level walkthrough of the container security measures available in {product-title}, including solutions for the host layer, the container and orchestration layer, and the build and application layer. These sections also include information on the following topics:

* Why container security is important and how it compares with existing security standards.
* Which container security measures are provided by the host ({op-system} and {op-system-base}) layer and
which are provided by {product-title}.
* How to evaluate your container content and sources for vulnerabilities.
* How to design your build and deployment process to proactively check container content.
* How to control access to containers through authentication and authorization.
* How networking and attached storage are secured in {product-title}.
* Containerized solutions for API management and SSO.

#### Auditing

{product-title} auditing provides a security-relevant chronological set of records documenting the sequence of activities that have affected the system by individual users, administrators, or other components of the system. Administrators can xref:../security/audit-log-policy-config.adoc#audit-log-policy-config[configure the audit log policy] and xref:../security/audit-log-view.adoc#audit-log-view[view audit logs].

#### Certificates

Certificates are used by various components to validate access to the cluster. Administrators can xref:../security/certificates/replacing-default-ingress-certificate.adoc#replacing-default-ingress[replace the default ingress certificate], xref:../security/certificates/api-server.adoc#api-server-certificates[add API server certificates], or xref:../security/certificates/service-serving-certificate.adoc#add-service-serving[add a service certificate].

You can also review more details about the types of certificates used by the cluster:

* xref:../security/certificate_types_descriptions/user-provided-certificates-for-api-server.adoc#cert-types-user-provided-certificates-for-the-api-server[User-provided certificates for the API server]
* xref:../security/certificate_types_descriptions/proxy-certificates.adoc#cert-types-proxy-certificates[Proxy certificates]
* xref:../security/certificate_types_descriptions/service-ca-certificates.adoc#cert-types-service-ca-certificates[Service CA certificates]
* xref:../security/certificate_types_descriptions/node-certificates.adoc#cert-types-node-certificates[Node certificates]
* xref:../security/certificate_types_descriptions/bootstrap-certificates.adoc#cert-types-bootstrap-certificates[Bootstrap certificates]
* xref:../security/certificate_types_descriptions/etcd-certificates.adoc#cert-types-etcd-certificates[etcd certificates]
* xref:../security/certificate_types_descriptions/olm-certificates.adoc#cert-types-olm-certificates[OLM certificates]
* xref:../security/certificate_types_descriptions/aggregated-api-client-certificates.adoc#cert-types-aggregated-api-client-certificates[Aggregated API client certificates]
* xref:../security/certificate_types_descriptions/machine-config-operator-certificates.adoc#cert-types-machine-config-operator-certificates[Machine Config Operator certificates]
* xref:../security/certificate_types_descriptions/user-provided-certificates-for-default-ingress.adoc#cert-types-user-provided-certificates-for-default-ingress[User-provided certificates for default ingress]
* xref:../security/certificate_types_descriptions/ingress-certificates.adoc#cert-types-ingress-certificates[Ingress certificates]
* xref:../security/certificate_types_descriptions/monitoring-and-cluster-logging-operator-component-certificates.adoc#cert-types-monitoring-and-cluster-logging-operator-component-certificates[Monitoring and cluster logging Operator component certificates]
* xref:../security/certificate_types_descriptions/control-plane-certificates.adoc#cert-types-control-plane-certificates[Control plane certificates]

#### Encrypting data

You can xref:../etcd/etcd-encrypt.adoc#etcd-encrypt[enable etcd encryption] for your cluster to provide an additional layer of data security. For example, it can help protect the loss of sensitive data if an etcd backup is exposed to the incorrect parties.

#### Vulnerability scanning

Administrators can use the {rhq-cso} to run xref:../security/pod-vulnerability-scan.adoc#pod-vulnerability-scan[vulnerability scans] and review information about detected vulnerabilities.

### Compliance overview

For many {product-title} customers, regulatory readiness, or compliance, on some level is required before any systems can be put into production. That regulatory readiness can be imposed by national standards, industry standards, or the organization's corporate governance framework.

#### Compliance checking

Administrators can use the xref:../security/compliance_operator/co-concepts/compliance-operator-understanding.adoc#understanding-compliance-operator[Compliance Operator] to run compliance scans and recommend remediations for any issues found. The xref:../security/compliance_operator/co-scans/oc-compliance-plug-in-using.adoc#using-oc-compliance-plug-in[`oc-compliance` plugin] is an OpenShift CLI (`oc`) plugin that provides a set of utilities to easily interact with the Compliance Operator.

#### File integrity checking

Administrators can use the xref:../security/file_integrity_operator/file-integrity-operator-understanding.adoc#understanding-file-integrity-operator[File Integrity Operator] to continually run file integrity checks on cluster nodes and provide a log of files that have been modified.

### Additional resources

* xref:../authentication/understanding-authentication.adoc#understanding-authentication[Understanding authentication]
* xref:../authentication/configuring-internal-oauth.adoc#configuring-internal-oauth[Configuring the internal OAuth server]
* xref:../authentication/understanding-identity-provider.adoc#understanding-identity-provider[Understanding identity provider configuration]
* xref:../authentication/using-rbac.adoc#using-rbac[Using RBAC to define and apply permissions]
* xref:../authentication/managing-security-context-constraints.adoc#managing-pod-security-policies[Managing security context constraints]
