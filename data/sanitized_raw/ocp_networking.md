<!-- source: ocp_networking.md -->

# Networking

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/networking_overview/understanding-networking
---

# Chapter 2. Understanding networking

To build resilient and secure applications in OpenShift Container Platform, configure the networking infrastructure for your cluster. Defining reliable pod-to-pod communication and traffic routing rules ensures that every application component functions correctly within the environment.

- API resources, such asIngressandRoute

By default, Kubernetes allocates each pod an internal IP address for applications running within the pod. Pods and their containers can network, but clients outside the cluster do not have networking access. When you expose your application to external traffic, giving each pod its own IP address means that pods can be treated like physical hosts or virtual machines in terms of port allocation, networking, naming, service discovery, load balancing, application configuration, and migration.

Some cloud platforms offer metadata APIs that listen on the 169.254.169.254 IP address, a link-local IP address in the IPv4169.254.0.0/16CIDR block.

This CIDR block is not reachable from the pod network. Pods that need access to these IP addresses must be given host network access by setting thespec.hostNetworkfield in the pod spec totrue.

If you allow a pod host network access, you grant the pod privileged access to the underlying network infrastructure.

## 2.1. OpenShift Container Platform DNSCopy linkLink copied to clipboard!

If you are running multiple services, such as front-end and back-end services for use with multiple pods, environment variables are created for user names, service IPs, and more so the front-end pods can communicate with the back-end services. If the service is deleted and recreated, a new IP address can be assigned to the service, and requires the front-end pods to be recreated to pick up the updated values for the service IP environment variable. Additionally, the back-end service must be created before any of the front-end pods to ensure that the service IP is generated properly, and that it can be provided to the front-end pods as an environment variable.

For this reason, OpenShift Container Platform has a built-in DNS so that the services can be reached by the service DNS as well as the service IP/port.

## 2.2. OpenShift Container Platform Ingress OperatorCopy linkLink copied to clipboard!

When you create your OpenShift Container Platform cluster, pods and services running on the cluster are each allocated their own IP addresses. The IP addresses are accessible to other pods and services running nearby but are not accessible to outside clients.

The Ingress Operator makes it possible for external clients to access your service by deploying and managing one or more HAProxy-basedIngress Controllersto handle routing. You can use the Ingress Operator to route traffic by specifying OpenShift Container PlatformRouteand KubernetesIngressresources. Configurations within the Ingress Controller, such as the ability to defineendpointPublishingStrategytype and internal load balancing, provide ways to publish Ingress Controller endpoints.

### 2.2.1. Comparing routes and IngressCopy linkLink copied to clipboard!

The Kubernetes Ingress resource in OpenShift Container Platform implements the Ingress Controller with a shared router service that runs as a pod inside the cluster. The most common way to manage Ingress traffic is with the Ingress Controller. You can scale and replicate this pod like any other regular pod. This router service is based onHAProxy, which is an open source load balancer solution.

The OpenShift Container Platform route provides Ingress traffic to services in the cluster. Routes provide advanced features that might not be supported by standard Kubernetes Ingress Controllers, such as TLS re-encryption, TLS passthrough, and split traffic for blue-green deployments.

Ingress traffic accesses services in the cluster through a route. Routes and Ingress are the main resources for handling Ingress traffic. Ingress provides features similar to a route, such as accepting external requests and delegating them based on the route. However, with Ingress you can only allow certain types of connections: HTTP/2, HTTPS and server name identification (SNI), and TLS with certificate. In OpenShift Container Platform, routes are generated to meet the conditions specified by the Ingress resource.

## 2.3. Glossary of common terms for OpenShift Container Platform networkingCopy linkLink copied to clipboard!

This glossary defines common terms that are used in the networking content.

**authentication**
  To control access to an OpenShift Container Platform cluster, a cluster administrator can configure user authentication and ensure only approved users access the cluster. To interact with an OpenShift Container Platform cluster, you must authenticate to the OpenShift Container Platform API. You can authenticate by providing an OAuth access token or an X.509 client certificate in your requests to the OpenShift Container Platform API.

**AWS Load Balancer Operator**
  The AWS Load Balancer (ALB) Operator deploys and manages an instance of theaws-load-balancer-controller.

**Cluster Network Operator**
  The Cluster Network Operator (CNO) deploys and manages the cluster network components in an OpenShift Container Platform cluster. This includes deployment of the Container Network Interface (CNI) network plugin selected for the cluster during installation.

**config map**
  A config map provides a way to inject configuration data into pods. You can reference the data stored in a config map in a volume of typeConfigMap. Applications running in a pod can use this data.

**custom resource (CR)**
  A CR is extension of the Kubernetes API. You can create custom resources.

**DNS**
  Cluster DNS is a DNS server which serves DNS records for Kubernetes services. Containers started by Kubernetes automatically include this DNS server in their DNS searches.

**DNS Operator**
  The DNS Operator deploys and manages CoreDNS to provide a name resolution service to pods. This enables DNS-based Kubernetes Service discovery in OpenShift Container Platform.

**deployment**
  A Kubernetes resource object that maintains the life cycle of an application.

**domain**
  Domain is a DNS name serviced by the Ingress Controller.

**egress**
  The process of data sharing externally through a network’s outbound traffic from a pod.

**External DNS Operator**
  The External DNS Operator deploys and manages ExternalDNS to provide the name resolution for services and routes from the external DNS provider to OpenShift Container Platform.

**HTTP-based route**
  An HTTP-based route is an unsecured route that uses the basic HTTP routing protocol and exposes a service on an unsecured application port.

**Ingress**
  The Kubernetes Ingress resource in OpenShift Container Platform implements the Ingress Controller with a shared router service that runs as a pod inside the cluster.

**Ingress Controller**
  The Ingress Operator manages Ingress Controllers. Using an Ingress Controller is the most common way to allow external access to an OpenShift Container Platform cluster.

**installer-provisioned infrastructure**
  The installation program deploys and configures the infrastructure that the cluster runs on.

**kubelet**
  A primary node agent that runs on each node in the cluster to ensure that containers are running in a pod.

**Kubernetes NMState Operator**
  The Kubernetes NMState Operator provides a Kubernetes API for performing state-driven network configuration across the OpenShift Container Platform cluster’s nodes with NMState.

**kube-proxy**
  Kube-proxy is a proxy service which runs on each node and helps in making services available to the external host. It helps in forwarding the request to correct containers and is capable of performing primitive load balancing.

**load balancers**
  OpenShift Container Platform uses load balancers for communicating from outside the cluster with services running in the cluster.

**MetalLB Operator**
  As a cluster administrator, you can add the MetalLB Operator to your cluster so that when a service of typeLoadBalanceris added to the cluster, MetalLB can add an external IP address for the service.

**multicast**
  With IP multicast, data is broadcast to many IP addresses simultaneously.

**namespaces**
  A namespace isolates specific system resources that are visible to all processes. Inside a namespace, only processes that are members of that namespace can see those resources.

**networking**
  Network information of a OpenShift Container Platform cluster.

**node**
  A worker machine in the OpenShift Container Platform cluster. A node is either a virtual machine (VM) or a physical machine.

**OpenShift Container Platform Ingress Operator**
  The Ingress Operator implements theIngressControllerAPI and is the component responsible for enabling external access to OpenShift Container Platform services.

**pod**
  One or more containers with shared resources, such as volume and IP addresses, running in your OpenShift Container Platform cluster. A pod is the smallest compute unit defined, deployed, and managed.

**PTP Operator**
  The PTP Operator creates and manages thelinuxptpservices.

**route**
  The OpenShift Container Platform route provides Ingress traffic to services in the cluster. Routes provide advanced features that might not be supported by standard Kubernetes Ingress Controllers, such as TLS re-encryption, TLS passthrough, and split traffic for blue-green deployments.

**scaling**
  Increasing or decreasing the resource capacity.

**service**
  Exposes a running application on a set of pods.

**Single Root I/O Virtualization (SR-IOV) Network Operator**
  The Single Root I/O Virtualization (SR-IOV) Network Operator manages the SR-IOV network devices and network attachments in your cluster.

**software-defined networking (SDN)**
  A software-defined networking (SDN) approach to provide a unified cluster network that enables communication between pods across the OpenShift Container Platform cluster.

**Stream Control Transmission Protocol (SCTP)**
  SCTP is a reliable message based protocol that runs on top of an IP network.

**taint**
  Taints and tolerations ensure that pods are scheduled onto appropriate nodes. You can apply one or more taints on a node.

**toleration**
  You can apply tolerations to pods. Tolerations allow the scheduler to schedule pods with matching taints.

**web console**
  A user interface (UI) to manage OpenShift Container Platform.
