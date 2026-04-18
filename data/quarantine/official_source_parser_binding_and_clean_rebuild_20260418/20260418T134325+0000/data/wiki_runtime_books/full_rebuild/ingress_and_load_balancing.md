# Ingress 및 로드 밸런싱

## Creating basic routes

If you have unencrypted HTTP, you can create a basic route with a route object.

## Securing routes

You can secure a route with HTTP strict transport security (HSTS).

## Configuring routes

To customise route configuration for specific traffic behaviors, apply annotations, headers, and cookies. By using these mechanisms, you can define granular routing rules, extending standard capabilities to meet complex application requirements.

## Creating advanced routes

To secure application traffic and serve custom certificates to clients, configure routes by using edge, passthrough, or re-encrypt TLS termination. By using these methods, you can define granular encryption rules, ensuring that traffic is decrypted and re-encrypted according to your specific security requirements.

## Configuring ingress cluster traffic overview

To enable communication between external networks and services in {product-title}, configure ingress cluster traffic.

#### Additional resources

* Use an Ingress Controller

* Automatically assign an external IP using a load balancer service

* About MetalLB and the MetalLB Operator

* Manually assign an external IP to a service

* Configure a `NodePort`

## Configuring ExternalIPs for services

As a cluster administrator, you can select an IP address block that is external to the cluster and can send traffic to services in the cluster. This functionality is generally most useful for clusters installed on bare-metal hardware.

> Before you configure ExternalIPs for services, your network infrastructure must route traffic for the external IP addresses to your cluster.

#### Additional resources

* Configuring IP failover

* About MetalLB and the MetalLB Operator

#### Next steps

* Configuring ingress cluster traffic for a service external IP

## Configuring ingress cluster traffic by using an Ingress Controller

You can use the Ingress Controller to control how external users communicate with services that run inside the cluster.

Before you begin any of the procedures that are listed in the Configuring ingress cluster traffic by using an Ingress Controller document, ensure that you meet the following prerequisites. A cluster administrator performs these prerequisites:

* Set up the external port to the cluster networking environment so that requests
can reach the cluster.

* Make sure there is at least one user with cluster admin role. To add this role
to a user, run the following command:
```terminal
$ oc adm policy add-cluster-role-to-user cluster-admin username
```

* You have an {product-title} cluster with at least one master and at least one node and a system outside the cluster that has network access to the cluster. This procedure assumes that the external system is on the same subnet as the cluster. The additional networking required for external systems on a different subnet is out-of-scope for this topic.

##### Additional resources

* Baseline Ingress Controller (router) performance

* Configuring the Ingress Controller

* Installing a cluster on bare metal

* Installing a cluster on vSphere

* About network policy

## Configuring the Ingress Controller endpoint publishing strategy

To expose Ingress Controller endpoints to external systems and enable load balancer integrations in {product-title}, configure the `endpointPublishingStrategy` parameter.

> On {rh-openstack-first}, the `LoadBalancerService` endpoint publishing strategy is supported only if a cloud provider is configured to create health monitors. For {rh-openstack} 16.2, this strategy is possible only if you use the Amphora Octavia provider.

> For more information, see the "Setting {rh-openstack} Cloud Controller Manager options" section of the {rh-openstack} installation documentation.

#### Additional resources

* Ingress Controller configuration parameters

* Setting {rh-openstack} Cloud Controller Manager options

* User-provisioned DNS requirements

## Configuring ingress cluster traffic using a load balancer

{product-title} provides methods for communicating from outside the cluster with services running in the cluster. This method uses a load balancer.

Before starting the following procedures, the administrator must complete the following prerequisite tasks:

* Set up the external port to the cluster networking environment so that requests can reach the cluster.

* Have an {product-title} cluster with at least one control plane node, at least one compute node, and a system outside the cluster that has network access to the cluster. This procedure assumes that the external system is on the same subnet as the cluster. The additional networking required for external systems on a different subnet is out-of-scope for this topic.

* Make sure there is at least one user with cluster admin role. To add this role to a user, run the following command:
```terminal
$ oc adm policy add-cluster-role-to-user cluster-admin username
```

## Configuring ingress cluster traffic on AWS

{product-title} provides methods for communicating from outside the cluster with services running in the cluster. This method uses load balancers on {aws-first}, specifically a Network Load Balancer (NLB) or a Classic Load Balancer (CLB). Both types of load balancers can forward the IP address of the client to the node, but a CLB requires proxy protocol support, which {product-title} automatically enables.

There are two ways to configure an Ingress Controller to use an NLB:

 By force replacing the Ingress Controller that is currently using a CLB. This deletes the `IngressController` object and an outage occurs while the new DNS records propagate and the NLB is being provisioned.
 By editing an existing Ingress Controller that uses a CLB to then use an NLB. This changes the load balancer without having to delete and recreate the `IngressController` object.

Both methods can be used to switch from an NLB to a CLB.

You can configure these load balancers on a new or existing {aws-short} cluster.

#### Additional resources

* Creating the installation configuration file

#### Additional resources

* Installing a cluster on AWS with network customizations
* [Network Load Balancer support on AWS](https://kubernetes.io/docs/concepts/services-networking/service/#aws-nlb-support)
* [Configure proxy protocol support for your Classic Load Balancer](https://docs.aws.amazon.com/elasticloadbalancing/latest/classic/enable-proxy-protocol.html)

## Configuring ingress cluster traffic for a service external IP

You can use either a MetalLB implementation or an IP failover deployment to attach an ExternalIP resource to a service so that the service is available to traffic outside your {product-title} cluster.

Hosting an external IP address in this way is only applicable for a cluster installed on bare-metal hardware.

You must ensure that you correctly configure the external network infrastructure to route traffic to the service.

Before you begin the procedure, ensure that you meet the following prerequisite:

* You configured your cluster with ExternalIPs enabled. For more information, see "Configuring ExternalIPs for services" in the _Additional resources_ section.

> Do not use the same ExternalIP for the egress IP.

#### Additional resources

Configuring ExternalIPs for services

* About MetalLB and the MetalLB Operator

* Configuring IP failover

* Configuring ExternalIPs for services

## Configuring ingress cluster traffic by using a NodePort

To enable external access to your application for specific networking requirements, expose a service by using a `NodePort`.

This configuration opens a specific port on every node in the cluster, allowing external traffic to reach your workloads by using an IP address of any node.

{product-title} provides methods for communicating from outside the cluster with services running in the cluster. This method uses a `NodePort`.

Before starting the following procedures, the administrator must complete the following prerequisite tasks:

* Set up the external port to the cluster networking environment so that requests can reach the cluster.

* Have an {product-title} cluster with at least one control plane node, at least one compute node, and a system outside the cluster that has network access to the cluster. This procedure assumes that the external system is on the same subnet as the cluster. The additional networking required for external systems on a different subnet is out-of-scope for this topic.

* Make sure there is at least one user with cluster admin role. To add this role to a user, run the following command:
----
$ oc adm policy add-cluster-role-to-user cluster-admin <user_name>
----

#### Additional resources

* Configuring the node port service range

* Adding a single NodePort service to an Ingress Controller

## Configuring ingress cluster traffic using load balancer allowed source ranges

You can specify a list of IP address ranges for the Ingress Controller. This action restricts access to the load balancer service when you specify the `LoadBalancerService` value for the `endpointPublishingStrategy` parameter.

#### Additional resources

* Introduction to OpenShift updates

## Patching existing ingress objects

You can update or modify the following fields of existing `Ingress` objects without recreating the objects or disrupting services to these objects:

* Specifications
* Host
* Path
* Backend services
* SSL/TLS settings
* Annotations

## Understanding DNS management policies

To ensure application accessiblity across external networks in {product-title}, you can manually configure DNS records for an Ingress Controller.

As a cluster administrator, when you create an Ingress Controller, the Operator manages the DNS records automatically. This has some limitations when the required DNS zone is different from the cluster DNS zone or when the DNS zone is hosted outside the cloud provider.

The following list details key aspects for a managed DNS management policy:

* The Managed DNS management policy for Ingress Controllers ensures that the lifecycle of the wildcard DNS record on the cloud provider is automatically managed by the Operator. This is the default behavior.

* When you change an Ingress Controller from `Managed` to `Unmanaged` DNS management policy, the Operator does not clean up the previous wildcard DNS record provisioned on the cloud.

* When you change an Ingress Controller from `Unmanaged` to `Managed` DNS management policy, the Operator attempts to create the DNS record on the cloud provider if it does not exist or updates the DNS record if it already exists.

The following list details key aspects for a unmanaged DNS management policy:

* The Unmanaged DNS management policy for Ingress Controllers ensures that the lifecycle of the wildcard DNS record on the cloud provider is not automatically managed; instead, it becomes the responsibility of the cluster administrator.

#### Additional resources

* Ingress Controller configuration parameters

## Gateway API with {product-title} networking

To manage complex network traffic and implement advanced routing policies in {product-title}, use the Ingress Operator to configure the Gateway API.

> Gateway API does not support user-defined networks (UDN).

Additional resources
* Ingress Controller sharding

## Load balancing on {rh-openstack}

To distribute network traffic and communications activity evenly across your compute instances in {rh-openstack}, configure load balancing services.

## Configuring MetalLB address pools

To allocate and manage the IP addresses assigned to load balancer services, configure MetalLB address pool custom resources. Defining these pools ensures that application workloads remain reachable through designated network ranges for consistent external access.

The namespaces used in the examples show `metallb-system` as the namespace.

For more information about how to install the MetalLB Operator, see About MetalLB and the MetalLB Operator.

#### Additional resources

* Configuring MetalLB with an L2 advertisement and label

* Configuring MetalLB BGP peers

* Configuring services to use MetalLB

## About advertising for the IP address pools

To provide fault-tolerant external IP addresses and load balancing for cluster services, configure MetalLB to advertise addresses by using Layer 2 protocols, the Border Gateway Protocol (BGP), or both. Selecting the appropriate protocol ensures reliable traffic routing and high availability for your application workloads.

MetalLB supports advertising by using Layer 2 and BGP for the same set of IP addresses.

MetalLB provides the flexibility to assign address pools to specific BGP peers, effectively limiting advertising to a subset of nodes on the network. This allows for more complex configurations, such as facilitating the isolation of nodes or the segmentation of the network.

#### Additional resources

* Configuring a community alias

## Configuring MetalLB BGP peers

To establish BGP sessions and advertise routes for load balancer services, configure MetalLB Border Gateway Protocol (BGP) peer custom resources (CRs). Defining these peers ensures that your network infrastructure receives accurate routing information to reach cluster application workloads.

You can add, modify, and delete BGP peers. The MetalLB Operator uses the BGP peer custom resources to identify the peers that MetalLB `speaker` pods contact to start BGP sessions. The peers receive the route advertisements for the load-balancer IP addresses that MetalLB assigns to services.

#### Additional resources

* About virtual routing and forwarding

* Example: Network interface with a VRF instance node network configuration policy

* Configuring an egress service

* Managing symmetric routing with MetalLB

#### Additional resources

* Configuring services to use MetalLB

## Configuring community alias

As a cluster administrator, you can configure a community alias and use it across different advertisements.

## Configuring MetalLB BFD profiles

To achieve faster path failure detection for BGP sessions, configure MetalLB Bidirectional Forwarding Detection (BFD) profiles. Establishing these profiles ensures that your network routing remains highly available and responsive by identifying connectivity issues more quickly than standard protocols.

You can add, modify, and delete BFD profiles. The MetalLB Operator uses the BFD profile custom resources (CRs) to identify the BGP sessions that use BFD.

#### Additional resources

* Configuring MetalLB BGP peers

## Configuring services to use MetalLB

To ensure predictable network endpoints, control how MetalLB assigns IP addresses to services of type `LoadBalancer`. Requesting specific addresses or pools ensures that your applications receive valid IP assignments that align with your specific network addressing plan.

## Managing symmetric routing with MetalLB

As a cluster administrator, you can effectively manage traffic for pods behind a MetalLB load-balancer service with multiple host interfaces by implementing features from MetalLB, NMState, and OVN-Kubernetes. By combining these features in this context, you can provide symmetric routing, traffic segregation, and support clients on different networks with overlapping CIDR addresses.

To achieve this functionality, learn how to implement virtual routing and forwarding (VRF) instances with MetalLB, and configure egress services.

Additional resources

* About virtual routing and forwarding

* Exposing a service through a network VRF

* Example: Network interface with a VRF instance node network configuration policy

* Configuring an egress service

## Configuring the integration of MetalLB and FRR-K8s

[FIGURE src="/playbooks/wiki-assets/full_rebuild/ingress_and_load_balancing/695_OpenShift_MetalLB_FRRK8s_integration_0624.png" alt="MetalLB integration with FRR" kind="figure" diagram_type="image_figure"]
MetalLB integration with FRR
[/FIGURE]

_Source: `metallb-frr-k8s.adoc` · asset `695_OpenShift_MetalLB_FRRK8s_integration_0624.png`_


To access advanced routing services not natively provided by MetalLB, configure the `FRRConfiguration` custom resource (CR). Defining the CR exposes specific FRRouting (FRR) capabilities and extends the routing functionality of your cluster beyond standard MetalLB advertisements.

FRRouting (FRR) is a free, open-source internet routing protocol suite for Linux and UNIX platforms. `FRR-K8s` is a Kubernetes-based DaemonSet that exposes a subset of the `FRR` API in a Kubernetes-compliant manner. `MetalLB` generates the `FRR-K8s` configuration corresponding to the MetalLB configuration applied.

> When configuring Virtual Route Forwarding (VRF), you must change the VRFs to a table ID lower than `1000` as higher than `1000` is reserved for {product-title}.

## MetalLB logging, troubleshooting, and support

To diagnose and resolve MetalLB configuration issues, refer to this list of commonly used commands. By using these commands, you can verify network connectivity and inspect service states to ensure efficient error recovery.

Additional resources

* [Querying metrics for all projects with the monitoring dashboard](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/accessing_metrics/accessing-metrics-as-an-administrator#querying-metrics-for-all-projects-with-mon-dashboard_accessing-metrics-as-an-administrator)

Additional resources

* Gathering data about your cluster
