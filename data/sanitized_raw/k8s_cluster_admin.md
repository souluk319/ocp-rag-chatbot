<!-- source: k8s_cluster_admin.md -->

# Administration

---
Source: https://kubernetes.io/docs/concepts/cluster-administration/
---

# Cluster Administration

The cluster administration overview is for anyone creating or administering a Kubernetes cluster.It assumes some familiarity with core Kubernetesconcepts.

## Planning a cluster

See the guides inSetupfor examples of how to plan, set up, and configure
Kubernetes clusters. The solutions listed in this article are calleddistros.

#### Note:

Before choosing a guide, here are some considerations:

- Do you want to try out Kubernetes on your computer, or do you want to build a high-availability,multi-node cluster? Choose distros best suited for your needs.
- Will you be usinga hosted Kubernetes cluster, such asGoogle Kubernetes Engine, orhosting your own cluster?
- Will your cluster beon-premises, orin the cloud (IaaS)? Kubernetes does not directly
support hybrid clusters. Instead, you can set up multiple clusters.
- If you are configuring Kubernetes on-premises, consider whichnetworking modelfits best.
- Will you be running Kubernetes on"bare metal" hardwareor onvirtual machines (VMs)?
- Do youwant to run a cluster, or do you expect to doactive development of Kubernetes project code?If the latter, choose an actively-developed distro. Some distros only use binary releases, but
offer a greater variety of choices.
- Familiarize yourself with thecomponentsneeded to run a cluster.

## Managing a cluster

- Learn how tomanage nodes.Read aboutNode autoscaling.

Learn how tomanage nodes.

- Read aboutNode autoscaling.
- Learn how to set up and manage theresource quotafor shared clusters.

Learn how to set up and manage theresource quotafor shared clusters.

## Securing a cluster

- Generate Certificatesdescribes the steps to
generate certificates using different tool chains.

Generate Certificatesdescribes the steps to
generate certificates using different tool chains.

- Kubernetes Container Environmentdescribes
the environment for Kubelet managed containers on a Kubernetes node.

Kubernetes Container Environmentdescribes
the environment for Kubelet managed containers on a Kubernetes node.

- Controlling Access to the Kubernetes APIdescribes
how Kubernetes implements access control for its own API.

Controlling Access to the Kubernetes APIdescribes
how Kubernetes implements access control for its own API.

- Authenticatingexplains authentication in
Kubernetes, including the various authentication options.

Authenticatingexplains authentication in
Kubernetes, including the various authentication options.

- Authorizationis separate from
authentication, and controls how HTTP calls are handled.

Authorizationis separate from
authentication, and controls how HTTP calls are handled.

- Using Admission Controllersexplains plug-ins which intercepts requests to the Kubernetes API server after authentication
and authorization.

Using Admission Controllersexplains plug-ins which intercepts requests to the Kubernetes API server after authentication
and authorization.

- Admission Webhook Good Practicesprovides good practices and considerations when designing mutating admission
webhooks and validating admission webhooks.

Admission Webhook Good Practicesprovides good practices and considerations when designing mutating admission
webhooks and validating admission webhooks.

- Using Sysctls in a Kubernetes Clusterdescribes to an administrator how to use thesysctlcommand-line tool to set kernel parameters.

Using Sysctls in a Kubernetes Clusterdescribes to an administrator how to use thesysctlcommand-line tool to set kernel parameters.

- Auditingdescribes how to interact with Kubernetes'audit logs.

Auditingdescribes how to interact with Kubernetes'audit logs.

### Securing the kubelet

- Control Plane-Node communication
- TLS bootstrapping
- Kubelet authentication/authorization

## Optional Cluster Services

- DNS Integrationdescribes how to resolve
a DNS name directly to a Kubernetes service.

DNS Integrationdescribes how to resolve
a DNS name directly to a Kubernetes service.

- Logging and Monitoring Cluster Activityexplains how logging in Kubernetes works and how to implement it.

Logging and Monitoring Cluster Activityexplains how logging in Kubernetes works and how to implement it.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
