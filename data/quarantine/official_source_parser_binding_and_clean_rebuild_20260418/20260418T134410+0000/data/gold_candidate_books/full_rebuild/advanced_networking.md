# 고급 네트워킹

## Verifying connectivity to an endpoint

The Cluster Network Operator (CNO) runs a controller, the connectivity check controller, that performs a connection health check between resources within your cluster.
By reviewing the results of the health checks, you can diagnose connection problems or eliminate network connectivity as the cause of an issue that you are investigating.

## Changing the MTU for the cluster network

As a cluster administrator, you can change the maximum transmission unit (MTU) for the cluster network after cluster installation. This change is disruptive as cluster nodes must be rebooted to finalize the MTU change.

#### Additional resources

* Using advanced networking options for PXE and ISO installations
* [Manually creating NetworkManager profiles in key file format](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html-single/configuring_and_managing_networking/index#proc_manually-creating-a-networkmanager-profile-in-keyfile-format_assembly_networkmanager-connection-profiles-in-keyfile-format)
* [Configuring a dynamic Ethernet connection using nmcli](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/9/html-single/configuring_and_managing_networking/index#configuring-a-dynamic-ethernet-connection-using-nmcli_configuring-an-ethernet-connection)

## Network bonding considerations

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/552_OpenShift_slb_mode_0625.png" alt="OVS `balance-slb` mode ` operating on a localnet with two NADs" kind="figure" diagram_type="image_figure"]
OVS `balance-slb` mode ` operating on a localnet with two NADs
[/FIGURE]

_Source: `enabling-OVS-balance-slb-mode.adoc` · asset `552_OpenShift_slb_mode_0625.png`_


You can use network bonding, also known as _link aggregration_, to combine many network interfaces into a single, logical interface. This means that you can use different modes for handling how network traffic distributes across bonded interfaces. Each mode provides fault tolerance and some modes provide load balancing capabilities to your network. Red Hat supports Open vSwitch (OVS) bonding and kernel bonding.

## Using the Stream Control Transmission Protocol (SCTP)

As a cluster administrator, you can use the Stream Control Transmission Protocol (SCTP) on a bare-metal cluster.

## Associating secondary interfaces metrics to network attachments

To gain better visibility into cluster traffic, you can associate secondary interface metrics with specific network attachments. By using the `pod_network_info` metric to label interfaces based on their `NetworkAttachmentDefinition` resource, you can more easily monitor performance and troubleshoot connectivity issues across your network.

## About BGP routing

This feature provides native Border Gateway Protocol (BGP) routing capabilities for the cluster.

> If you are using the MetalLB Operator and there are existing `FRRConfiguration` CRs in the `metallb-system` namespace created by cluster administrators or third-party cluster components other than the MetalLB Operator, you must ensure that they are copied to the `openshift-frr-k8s` namespace or that those third-party cluster components use the new namespace. For more information, see Migrating FRR-K8s resources.

#### Additional resources

- [FRRouting User Guide: BGP](https://docs.frrouting.org/en/latest/bgp.html)

## Enabling BGP routing

As a cluster administrator, you can enable OVN-Kubernetes Border Gateway Protocol (BGP) routing support for your cluster.

## Disabling BGP routing

As a cluster administrator, you can enable OVN-Kubernetes Border Gateway Protocol (BGP) routing support for your cluster.

## Migrating FRR-K8s resources

All user-created FRR-K8s custom resources (CRs) in the `metallb-system` namespace under OpenShift Container Platform 4.17 and earlier releases must be migrated to the `openshift-frr-k8s` namespace. As a cluster administrator, complete the steps in this procedure to migrate your FRR-K8s custom resources.

## About route advertisements

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/524-openshift-bgp-ovn-k8s-no-vpn-0325.png" alt="Advertising pod IPs from a cluster user-defined network over BGP" kind="figure" diagram_type="image_figure"]
Advertising pod IPs from a cluster user-defined network over BGP
[/FIGURE]

_Source: `nw-routeadvertisements-example.adoc` · asset `524-openshift-bgp-ovn-k8s-no-vpn-0325.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/524-openshift-bgp-ovn-k8s-vrf-lite-0325.png" alt="Advertising pod IPs from a cluster user-defined network over BGP with VPN" kind="figure" diagram_type="image_figure"]
Advertising pod IPs from a cluster user-defined network over BGP with VPN
[/FIGURE]

_Source: `nw-routeadvertisements-example.adoc` · asset `524-openshift-bgp-ovn-k8s-vrf-lite-0325.png`_


To simplify network management and improve failover visibility, you can use route advertisements to share pod and egress IP routes between your cluster and the provider network. This feature requires the OVN-Kubernetes plugin and a Border Gateway Protocol (BGP) provider.

For more information, see About BGP routing.

#### Additional resources

- Configuring the FRRConfiguration CRD

- [Starting a service within an isolated VRF network](https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/8/html/configuring_and_managing_networking/assembly_starting-a-service-within-an-isolated-vrf-network_configuring-and-managing-networking)

- [FRRouting User Guide: BGP](https://docs.frrouting.org/en/latest/bgp.html)

## Enabling route advertisements

To improve network reachability and failover visibility for your cluster, you can enable route advertisements for pod and egress IP addresses. This configuration requires the OVN-Kubernetes network plugin and allows your cluster to share routes with an external provider network.

As a cluster administrator, you can configure additional route advertisements for your cluster. You must use the OVN-Kubernetes network plugin.

## Disabling route advertisements

To stop the broadcast of cluster network routes and egress IP addresses to your provider network, you can disable route advertisements. Disabling this feature removes the automatically generated routing configurations while maintaining your existing network infrastructure.

## Example route advertisements setup

To learn how to implement a route reflection setup on bare-metal infrastructure, you can follow this sample configuration. This example demonstrates how to enable the necessary feature gates and configure objects to advertise pod and egress IP routes.

As a cluster administrator, you can configure the following example route advertisements setup for your cluster. This configuration is intended as a sample that demonstrates how to configure route advertisements.

## About PTP in OpenShift cluster nodes

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_1123_PTP_network.png" alt="Diagram showing a PTP grandmaster clock" kind="diagram" diagram_type="semantic_diagram"]
Diagram showing a PTP grandmaster clock
[/FIGURE]

_Source: `nw-ptp-introduction.adoc` · asset `319_OpenShift_PTP_bare-metal_OCP_nodes_1123_PTP_network.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_1023_PTP.png" alt="GNSS and T-GM system architecture" kind="diagram" diagram_type="semantic_diagram"]
GNSS and T-GM system architecture
[/FIGURE]

_Source: `ptp-overview-of-gnss-grandmaster-clock.adoc` · asset `319_OpenShift_PTP_bare-metal_OCP_nodes_1023_PTP.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-using-dual-nic-ptp.png" alt="Dual NIC PTP grandmaster clock connected to GNSS timing source and downstream PTP boundary and ordinary clocks" kind="figure" diagram_type="image_figure"]
Dual NIC PTP grandmaster clock connected to GNSS timing source and downstream PTP boundary and ordinary clocks
[/FIGURE]

_Source: `ptp-dual-nics.adoc` · asset `openshift-ptp-using-dual-nic-ptp.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-3-card-grandmaster.png" alt="3-card PTP grandmaster clock connected to GNSS timing source and downstream PTP boundary and ordinary clocks" kind="figure" diagram_type="image_figure"]
3-card PTP grandmaster clock connected to GNSS timing source and downstream PTP boundary and ordinary clocks
[/FIGURE]

_Source: `ptp-three-card-grandmaster.adoc` · asset `openshift-ptp-3-card-grandmaster.png`_


Precision Time Protocol (PTP) is used to synchronize clocks in a network. When used in conjunction with hardware support, PTP is capable of sub-microsecond accuracy, and is more accurate than Network Time Protocol (NTP).

> If your `openshift-sdn` cluster with PTP uses the User Datagram Protocol (UDP) for hardware time stamping and you migrate to the OVN-Kubernetes plugin, the hardware time stamping cannot be applied to primary interface devices, such as an Open vSwitch (OVS) bridge. As a result, UDP version 4 configurations cannot work with a `br-ex` interface.

You can configure `linuxptp` services and use PTP-capable hardware in OpenShift Container Platform cluster nodes.

Use the OpenShift Container Platform web console or OpenShift CLI (`oc`) to install PTP by deploying the PTP Operator. The PTP Operator creates and manages the `linuxptp` services and provides the following features:

* Discovery of the PTP-capable devices in the cluster.

* Management of the configuration of `linuxptp` services.

* Notification of PTP clock events that negatively affect the performance and reliability of your application with the PTP Operator `cloud-event-proxy` sidecar.

> The PTP Operator works with PTP-capable devices on clusters provisioned only on bare-metal infrastructure.

Additional resources
* Disabling chrony time service

## Configuring PTP devices

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/openshift-ptp-holdover-tgm-clock-with-gnss.png" alt="Holdover in a T-GM clock with GNSS as the source" kind="figure" diagram_type="image_figure"]
Holdover in a T-GM clock with GNSS as the source
[/FIGURE]

_Source: `nw-ptp-holdover-in-a-grandmaster-clock.adoc` · asset `openshift-ptp-holdover-tgm-clock-with-gnss.png`_


The PTP Operator adds the `NodePtpDevice.ptp.openshift.io` custom resource definition (CRD) to OpenShift Container Platform.

When installed, the PTP Operator searches your cluster for Precision Time Protocol (PTP) capable network devices on each node. The Operator creates and updates a `NodePtpDevice` custom resource (CR) object for each node that provides a compatible PTP-capable network device.

Network interface controller (NIC) hardware with built-in PTP capabilities sometimes require a device-specific configuration. You can use hardware-specific NIC features for supported hardware with the PTP Operator by configuring a plugin in the `PtpConfig` custom resource (CR). The `linuxptp-daemon` service uses the named parameters in the `plugin` stanza to start `linuxptp` processes, `ptp4l` and `phc2sys`, based on the specific hardware configuration.

> In OpenShift Container Platform 4.20, the Intel E810 NIC is supported with a `PtpConfig` plugin.

Additional resources

* Configuring the PTP fast event notifications publisher

Additional resources

* Grandmaster clock class sync state reference

Additional resources

* Configuring FIFO priority scheduling for PTP hardware

* Configuring the PTP fast event notifications publisher

Additional resources

* Configuring FIFO priority scheduling for PTP hardware

* Configuring the PTP fast event notifications publisher

Additional resources

* Configuring linuxptp services as ordinary clock

* Using dual-port NICs to improve redundancy for PTP ordinary clocks

## Developing PTP events consumer applications with the REST API v2

[FIGURE src="/playbooks/wiki-assets/full_rebuild/advanced_networking/319_OpenShift_PTP_bare-metal_OCP_nodes_0323_4.17.png" alt="Overview of consuming PTP fast events from the PTP event producer REST API" kind="figure" diagram_type="image_figure"]
Overview of consuming PTP fast events from the PTP event producer REST API
[/FIGURE]

_Source: `cnf-about-ptp-events-using-ptp-event-producer-with-o-ran-api.adoc` · asset `319_OpenShift_PTP_bare-metal_OCP_nodes_0323_4.17.png`_


When developing consumer applications that make use of Precision Time Protocol (PTP) events on a bare-metal cluster node, you deploy your consumer application in a separate application pod.
The consumer application subscribes to PTP events by using the PTP events REST API v2.

> The following information provides general guidance for developing consumer applications that use PTP events.
> A complete events consumer application example is outside the scope of this information.

Additional resources

* PTP events REST API v2 reference

Additional resources

* Configuring linuxptp services as ordinary clock

Additional resources

* api/ocloudNotifications/v2/subscriptions

Additional resources

* [Accessing metrics as a developer](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/accessing_metrics/accessing-metrics-as-a-developer)

## PTP events REST API v2 reference

Use the following REST API v2 endpoints to subscribe the `cloud-event-consumer` application to Precision Time Protocol (PTP) events posted at `\http://ptp-event-publisher-service-NODE_NAME.openshift-ptp.svc.cluster.local:9043/api/ocloudNotifications/v2` in the PTP events producer pod.

* `api/ocloudNotifications/v2/subscriptions`
** `POST`: Creates a new subscription
** `GET`: Retrieves a list of subscriptions
** `DELETE`: Deletes all subscriptions

* `api/ocloudNotifications/v2/subscriptions/{subscription_id}`
** `GET`: Returns details for the specified subscription ID
** `DELETE`: Deletes the subscription associated with the specified subscription ID

* `api/ocloudNotifications/v2/health`
** `GET`: Returns the health status of `ocloudNotifications` API

* `api/ocloudNotifications/v2/publishers`
** `GET`: Returns a list of PTP event publishers for the cluster node

* `api/ocloudnotifications/v2/{resource_address}/CurrentState`
** `GET`: Returns the current state of the event type specified by the `{resouce_address}`.
