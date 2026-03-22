<!-- source: ocp_control_plane.md -->

# Architecture

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/control-plane
---

# Chapter 6. Control plane architecture

Thecontrol plane, which is composed of control plane machines, manages the OpenShift Container Platform cluster. The control plane machines manage workloads on the compute machines, which are also known as worker machines. The cluster itself manages all upgrades to the machines by the actions of the Cluster Version Operator (CVO), the Machine Config Operator, and a set of individual Operators.

## 6.1. Node configuration management with machine config poolsCopy linkLink copied to clipboard!

Machines that run control plane components or user workloads are divided into groups based on the types of resources they handle. These groups of machines are called machine config pools (MCP). Each MCP manages a set of nodes and its corresponding machine configs. The role of the node determines which MCP it belongs to; the MCP governs nodes based on its assigned node role label. Nodes in an MCP have the same configuration; this means nodes can be scaled up and torn down in response to increased or decreased workloads.

By default, there are two MCPs created by the cluster when it is installed:masterandworker. Each default MCP has a defined configuration applied by the Machine Config Operator (MCO), which is responsible for managing MCPs and facilitating MCP updates.

For worker nodes, you can create additional MCPs, or custom pools, to manage nodes with custom use cases that extend outside of the default node types. Custom MCPs for the control plane nodes are not supported.

Custom pools are pools that inherit their configurations from the worker pool. They use any machine config targeted for the worker pool, but add the ability to deploy changes only targeted at the custom pool. Since a custom pool inherits its configuration from the worker pool, any change to the worker pool is applied to the custom pool as well. Custom pools that do not inherit their configurations from the worker pool are not supported by the MCO.

A node can only be included in one MCP. If a node has multiple labels that correspond to several MCPs, likeworker,infra, it is managed by the infra custom pool, not the worker pool. Custom pools take priority on selecting nodes to manage based on node labels; nodes that do not belong to a custom pool are managed by the worker pool.

It is recommended to have a custom pool for every node role you want to manage in your cluster. For example, if you create infra nodes to handle infra workloads, it is recommended to create a custom infra MCP to group those nodes together. If you apply aninfrarole label to a worker node so it has theworker,infradual label, but do not have a custom infra MCP, the MCO considers it a worker node. If you remove theworkerlabel from a node and apply theinfralabel without grouping it in a custom pool, the node is not recognized by the MCO and is unmanaged by the cluster.

Any node labeled with theinfrarole that is only running infra workloads is not counted toward the total number of subscriptions. The MCP managing an infra node is mutually exclusive from how the cluster determines subscription charges; tagging a node with the appropriateinfrarole and using taints to prevent user workloads from being scheduled on that node are the only requirements for avoiding subscription charges for infra workloads.

The MCO applies updates for pools independently; for example, if there is an update that affects all pools, nodes from each pool update in parallel with each other. If you add a custom pool, nodes from that pool also attempt to update concurrently with the master and worker nodes.

There might be situations where the configuration on a node does not fully match what the currently-applied machine config specifies. This state is calledconfiguration drift. The Machine Config Daemon (MCD) regularly checks the nodes for configuration drift. If the MCD detects configuration drift, the MCO marks the nodedegradeduntil an administrator corrects the node configuration. A degraded node is online and operational, but, it cannot be updated.

## 6.2. Machine roles in OpenShift Container PlatformCopy linkLink copied to clipboard!

OpenShift Container Platform assigns hosts different roles. These roles define the function of the machine within the cluster. The cluster contains definitions for the standardmasterandworkerrole types.

The cluster also contains the definition for thebootstraprole. Because the bootstrap machine is used only during cluster installation, its function is explained in the cluster installation documentation.

### 6.2.1. Control plane and node host compatibilityCopy linkLink copied to clipboard!

The OpenShift Container Platform version must match between control plane host and node host. For example, in a 4.17 cluster, all control plane hosts must be 4.17 and all nodes must be 4.17.

Temporary mismatches during cluster upgrades are acceptable. For example, when upgrading from the previous OpenShift Container Platform version to 4.17, some nodes will upgrade to 4.17 before others. Prolonged skewing of control plane hosts and node hosts might expose older compute machines to bugs and missing features. Users should resolve skewed control plane hosts and node hosts as soon as possible.

Thekubeletservice must not be newer thankube-apiserver, and can be up to two minor versions older depending on whether your OpenShift Container Platform version is odd or even. The table below shows the appropriate version compatibility:

| OpenShift Container Platform version | Supportedkubeletskew |
| --- | --- |
| Odd OpenShift Container Platform minor versions[1] | Up to one version older |
| Even OpenShift Container Platform minor versions[2] | Up to two versions older |

Odd OpenShift Container Platform minor versions[1]

Up to one version older

Even OpenShift Container Platform minor versions[2]

Up to two versions older

- For example, OpenShift Container Platform 4.11, 4.13.
- For example, OpenShift Container Platform 4.10, 4.12.

### 6.2.2. Cluster workersCopy linkLink copied to clipboard!

In a Kubernetes cluster, worker nodes run and manage the actual workloads requested by Kubernetes users. The worker nodes advertise their capacity and the scheduler, which is a control plane service, determines on which nodes to start pods and containers. The following important services run on each worker node:

- CRI-O, which is the container engine.
- kubelet, which is the service that accepts and fulfills requests for running and stopping container workloads.
- A service proxy, which manages communication for pods across workers.
- The runC or crun low-level container runtime, which creates and runs containers.

For information about how to enable crun instead of the default runC, see the documentation for creating aContainerRuntimeConfigCR.

In OpenShift Container Platform, compute machine sets control the compute machines, which are assigned theworkermachine role. Machines with theworkerrole drive compute workloads that are governed by a specific machine pool that autoscales them. Because OpenShift Container Platform has the capacity to support multiple machine types, the machines with theworkerrole are classed ascomputemachines. In this release, the termsworker machineandcompute machineare used interchangeably because the only default type of compute machine is the worker machine. In future versions of OpenShift Container Platform, different types of compute machines, such as infrastructure machines, might be used by default.

Compute machine sets are groupings of compute machine resources under themachine-apinamespace. Compute machine sets are configurations that are designed to start new compute machines on a specific cloud provider. Conversely, machine config pools (MCPs) are part of the Machine Config Operator (MCO) namespace. An MCP is used to group machines together so the MCO can manage their configurations and facilitate their upgrades.

### 6.2.3. Cluster control planesCopy linkLink copied to clipboard!

In a Kubernetes cluster, themasternodes run services that are required to control the Kubernetes cluster. In OpenShift Container Platform, the control plane is comprised of control plane machines that have amastermachine role. They contain more than just the Kubernetes services for managing the OpenShift Container Platform cluster.

For most OpenShift Container Platform clusters, control plane machines are defined by a series of standalone machine API resources. For supported cloud provider and OpenShift Container Platform version combinations, control planes can be managed with control plane machine sets. Extra controls apply to control plane machines to prevent you from deleting all of the control plane machines and breaking your cluster.

Exactly three control plane nodes must be used for all production deployments. However, on bare metal platforms, clusters can be scaled up to five control plane nodes.

Services that fall under the Kubernetes category on the control plane include the Kubernetes API server, etcd, the Kubernetes controller manager, and the Kubernetes scheduler.

| Component | Description |
| --- | --- |
| Kubernetes API server | The Kubernetes API server validates and configures the data for pods, services, and replication cont |
| etcd | etcd stores the persistent control plane state while other components watch etcd for changes to brin |
| Kubernetes controller manager | The Kubernetes controller manager watches etcd for changes to objects such as replication, namespace |
| Kubernetes scheduler | The Kubernetes scheduler watches for newly created pods without an assigned node and selects the bes |

Kubernetes API server

The Kubernetes API server validates and configures the data for pods, services, and replication controllers. It also provides a focal point for the shared state of the cluster.

etcd

etcd stores the persistent control plane state while other components watch etcd for changes to bring themselves into the specified state.

Kubernetes controller manager

The Kubernetes controller manager watches etcd for changes to objects such as replication, namespace, and service account controller objects, and then uses the API to enforce the specified state. Several such processes create a cluster with one active leader at a time.

Kubernetes scheduler

The Kubernetes scheduler watches for newly created pods without an assigned node and selects the best node to host the pod.

There are also OpenShift services that run on the control plane, which include the OpenShift API server, OpenShift controller manager, OpenShift OAuth API server, and OpenShift OAuth server.

| Component | Description |
| --- | --- |
| OpenShift API server | The OpenShift API server validates and configures the data for OpenShift resources, such as projects |
| OpenShift controller manager | The OpenShift controller manager watches etcd for changes to OpenShift objects, such as project, rou |
| OpenShift OAuth API server | The OpenShift OAuth API server validates and configures the data to authenticate to OpenShift Contai |
| OpenShift OAuth server | Users request tokens from the OpenShift OAuth server to authenticate themselves to the API.The OpenS |

OpenShift API server

The OpenShift API server validates and configures the data for OpenShift resources, such as projects, routes, and templates.

The OpenShift API server is managed by the OpenShift API Server Operator.

OpenShift controller manager

The OpenShift controller manager watches etcd for changes to OpenShift objects, such as project, route, and template controller objects, and then uses the API to enforce the specified state.

The OpenShift controller manager is managed by the OpenShift Controller Manager Operator.

OpenShift OAuth API server

The OpenShift OAuth API server validates and configures the data to authenticate to OpenShift Container Platform, such as users, groups, and OAuth tokens.

The OpenShift OAuth API server is managed by the Cluster Authentication Operator.

OpenShift OAuth server

Users request tokens from the OpenShift OAuth server to authenticate themselves to the API.

The OpenShift OAuth server is managed by the Cluster Authentication Operator.

Some of these services on the control plane machines run as systemd services, while others run as static pods.

Systemd services are appropriate for services that you need to always come up on that particular system shortly after it starts. For control plane machines, those include sshd, which allows remote login. It also includes services such as:

- The CRI-O container engine (crio), which runs and manages the containers. OpenShift Container Platform 4.17 uses CRI-O instead of the Docker Container Engine.
- Kubelet (kubelet), which accepts requests for managing containers on the machine from control plane services.

CRI-O and Kubelet must run directly on the host as systemd services because they need to be running before you can run other containers.

Theinstaller-*andrevision-pruner-*control plane pods must run with root permissions because they write to the/etc/kubernetesdirectory, which is owned by the root user. These pods are in the following namespaces:

- openshift-etcd
- openshift-kube-apiserver
- openshift-kube-controller-manager
- openshift-kube-scheduler

## 6.3. Operators in OpenShift Container PlatformCopy linkLink copied to clipboard!

Operators are among the most important components of OpenShift Container Platform. They are the preferred method of packaging, deploying, and managing services on the control plane. They can also provide advantages to applications that users run.

Operators integrate with Kubernetes APIs and CLI tools such askubectland the OpenShift CLI (oc). They provide the means of monitoring applications, performing health checks, managing over-the-air (OTA) updates, and ensuring that applications remain in your specified state.

Operators also offer a more granular configuration experience. You configure each component by modifying the API that the Operator exposes instead of modifying a global configuration file.

Because CRI-O and the Kubelet run on every node, almost every other cluster function can be managed on the control plane by using Operators. Components that are added to the control plane by using Operators include critical networking and credential services.

While both follow similar Operator concepts and goals, Operators in OpenShift Container Platform are managed by two different systems, depending on their purpose:

**Cluster Operators**
  Managed by the Cluster Version Operator (CVO) and installed by default to perform cluster functions.

**Optional add-on Operators**
  Managed by Operator Lifecycle Manager (OLM) and can be made accessible for users to run in their applications. Also known asOLM-based Operators.

### 6.3.1. Cluster OperatorsCopy linkLink copied to clipboard!

In OpenShift Container Platform, all cluster functions are divided into a series of defaultcluster Operators. Cluster Operators manage a particular area of cluster functionality, such as cluster-wide application logging, management of the Kubernetes control plane, or the machine provisioning system.

Cluster Operators are represented by aClusterOperatorobject, which cluster administrators can view in the OpenShift Container Platform web console from theAdministrationCluster Settingspage. Each cluster Operator provides a simple API for determining cluster functionality. The Operator hides the details of managing the lifecycle of that component. Operators can manage a single component or tens of components, but the end goal is always to reduce operational burden by automating common actions.

### 6.3.2. Add-on OperatorsCopy linkLink copied to clipboard!

Operator Lifecycle Manager (OLM) and OperatorHub are default components in OpenShift Container Platform that help manage Kubernetes-native applications as Operators. Together they provide the system for discovering, installing, and managing the optional add-on Operators available on the cluster.

Using OperatorHub in the OpenShift Container Platform web console, cluster administrators and authorized users can select Operators to install from catalogs of Operators. After installing an Operator from OperatorHub, it can be made available globally or in specific namespaces to run in user applications.

Default catalog sources are available that include Red Hat Operators, certified Operators, and community Operators. Cluster administrators can also add their own custom catalog sources, which can contain a custom set of Operators.

Developers can use the Operator SDK to help author custom Operators that take advantage of OLM features, as well. Their Operator can then be bundled and added to a custom catalog source, which can be added to a cluster and made available to users.

OLM does not manage the cluster Operators that comprise the OpenShift Container Platform architecture.

## 6.4. Overview of etcdCopy linkLink copied to clipboard!

etcd is a consistent, distributed key-value store that holds small amounts of data that can fit entirely in memory. Although etcd is a core component of many projects, it is the primary data store for Kubernetes, which is the standard system for container orchestration.

### 6.4.1. Benefits of using etcdCopy linkLink copied to clipboard!

By using etcd, you can benefit in several ways:

- Maintain consistent uptime for your cloud-native applications, and keep them working even if individual servers fail
- Store and replicate all cluster states for Kubernetes
- Distribute configuration data to provide redundancy and resiliency for the configuration of nodes

### 6.4.2. How etcd worksCopy linkLink copied to clipboard!

To ensure a reliable approach to cluster configuration and management, etcd uses the etcd Operator. The Operator simplifies the use of etcd on a Kubernetes container platform like OpenShift Container Platform. With the etcd Operator, you can create or delete etcd members, resize clusters, perform backups, and upgrade etcd.

The etcd Operator observes, analyzes, and acts:

- It observes the cluster state by using the Kubernetes API.
- It analyzes differences between the current state and the state that you want.
- It fixes the differences through the etcd cluster management APIs, the Kubernetes API, or both.

etcd holds the cluster state, which is constantly updated. This state is continuously persisted, which leads to a high number of small changes at high frequency. As a result, it is critical to back the etcd cluster member with fast, low-latency I/O. For more information about best practices for etcd, see "Recommended etcd practices".
