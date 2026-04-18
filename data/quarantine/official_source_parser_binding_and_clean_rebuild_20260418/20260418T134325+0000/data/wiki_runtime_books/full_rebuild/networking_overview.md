# 네트워킹 개요

## Understanding networking

To build resilient and secure applications in {product-title}, configure the networking infrastructure for your cluster. Defining reliable pod-to-pod communication and traffic routing rules ensures that every application component functions correctly within the environment.

Additional resources

* About network policy

## Accessing hosts

To establish secure administrative access to {product-title} instances and control plane nodes, create a bastion host.

Configuring a bastion host provides an entry point for Secure Shell (SSH) traffic, ensuring that your cluster remains protected while allowing for remote management.

## Networking dashboards

To monitor and analyze network performance within your cluster, view networking metrics in the {product-title} web console. By accessing these dashboards through *Observe* -> *Dashboards*,  you can identify traffic patterns and troubleshoot connectivity issues to ensure consistent workload availability.

Network Observability Operator::

If you have the Network Observability Operator installed, you can view network traffic metrics dashboards by selecting the *Netobserv* dashboard from the *Dashboards* drop-down list. For more information about metrics available in this *Dashboard*, see Network Observability metrics dashboards.

Networking and OVN-Kubernetes dashboard::

You can view both general networking metrics and OVN-Kubernetes metrics from the dashboard.
To view general networking metrics, select *Networking/Linux Subsystem Stats* from the *Dashboards* drop-down list. You can view the following networking metrics from the dashboard: *Network Utilisation*, *Network Saturation*, and *Network Errors*.
To view OVN-Kubernetes metrics select *Networking/Infrastructure* from the *Dashboards* drop-down list. You can view the following OVN-Kubernetes metrics: *Networking Configuration*, *TCP Latency Probes*, *Control Plane Resources*, and *Worker Resources*.

Ingress Operator dashboard::

You can view networking metrics handled by the Ingress Operator from the dashboard. This includes metrics like the following:
* Incoming and outgoing bandwidth
* HTTP error rates
* HTTP server response latency
To view these Ingress metrics, select *Networking/Ingress* from the *Dashboards* drop-down list. You can view Ingress metrics for the following categories: *Top 10 Per Route*, *Top 10 Per Namespace*, and *Top 10 Per Shard*.

## CIDR range definitions

To ensure stable and accurate network routing in {product-title} clusters that use OVN-Kubernetes, define non-overlapping Classless Inter-Domain Routing (CIDR) subnet ranges. Establishing unique ranges prevents IP address conflicts so that internal traffic reaches its intended destination without interference.

> For {product-title} 4.17 and later versions, clusters use `169.254.0.0/17` for IPv4 and `fd69::/112` for IPv6 as the default masquerade subnet. You must avoid these ranges. For upgraded clusters, there is no change to the default masquerade subnet.

> You can use the [Red Hat OpenShift Network Calculator](https://access.redhat.com/labs/ocpnc/) to decide your networking needs before setting CIDR range during cluster creation.

> You must have a Red Hat account to use the calculator.

The following subnet types are mandatory for a cluster that uses OVN-Kubernetes:

* Join: Uses a join switch to connect gateway routers to distributed routers. A join switch reduces the number of IP addresses for a distributed router. For a cluster that uses the OVN-Kubernetes plugin, an IP address from a dedicated subnet is assigned to any logical port that attaches to the join switch.
* Masquerade: Prevents collisions for identical source and destination IP addresses that are sent from a node as hairpin traffic to the same node after a load balancer makes a routing decision.
* Transit: A transit switch is a type of distributed switch that spans across all nodes in the cluster. A transit switch routes traffic between different zones. For a cluster that uses the OVN-Kubernetes plugin, an IP address from a dedicated subnet is assigned to any logical port that attaches to the transit switch.

> You can change the join, masquerade, and transit CIDR ranges for your cluster as a postinstallation task.

When specifying subnet CIDR ranges, ensure that the subnet CIDR range is within the defined Machine CIDR. You must verify that the subnet CIDR ranges allow for enough IP addresses for all intended workloads depending on which platform the cluster is hosted.

OVN-Kubernetes, the default network provider in {product-title} 4.14 and later versions, internally uses the following IP address subnet ranges:

* `V4JoinSubnet`: `100.64.0.0/16`
* `V6JoinSubnet`: `fd98::/64`
* `V4TransitSwitchSubnet`: `100.88.0.0/16`
* `V6TransitSwitchSubnet`: `fd97::/64`
* `defaultV4MasqueradeSubnet`: `169.254.0.0/17`
* `defaultV6MasqueradeSubnet`: `fd69::/112`

> The earlier list includes join, transit, and masquerade IPv4 and IPv6 address subnets. If your cluster uses OVN-Kubernetes, do not include any of these IP address subnet ranges in any other CIDR definitions in your cluster or infrastructure.

Additional resources

* Configuring OVN-Kubernetes internal IP address subnets

Additional resources

* Cluster Network Operator configuration

Additional resources
* Cluster Network Operator configuration
* Configuring the cluster network range
