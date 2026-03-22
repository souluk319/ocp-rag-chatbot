<!-- source: ocp_etcd.md -->

# Operations

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/scalability_and_performance/recommended-performance-and-scalability-practices-2
---

# Chapter 2. Recommended performance and scalability practices

## 2.1. Recommended control plane practicesCopy linkLink copied to clipboard!

To ensure optimal performance and scalability, apply the recommended practices for OpenShift Container Platform control planes. By understanding these recommended practices, you can configure your environment to handle increasing workloads while maintaining stability.

### 2.1.1. Recommended practices for scaling the clusterCopy linkLink copied to clipboard!

To scale your cluster effectively, apply the recommended practices for installations with cloud provider integration. By understanding this guidance, you can optimize performance and ensure stability as you increase the size of your environment.

Apply the following best practices to scale the number of compute machines in your OpenShift Container Platform cluster. You scale the worker machines by increasing or decreasing the number of replicas that are defined in the compute machine set.

When scaling up the cluster to higher node counts:

- Spread nodes across all of the available zones for higher availability.
- Scale up by no more than 25 to 50 machines at once.
- Consider creating new compute machine sets in each available zone with alternative instance types of similar size to help mitigate any periodic provider capacity constraints. For example, on AWS, usem5.largeandm5d.large.

Cloud providers might implement a quota for API services. Therefore, gradually scale the cluster.

The controller might not be able to create the machines if the replicas in the compute machine sets are set to higher numbers all at one time. The number of requests the cloud platform, which OpenShift Container Platform is deployed on top of, is able to handle impacts the process. The controller starts to query more while trying to create, check, and update the machines with the status. The cloud platform on which OpenShift Container Platform is deployed has API request limits; excessive queries might lead to machine creation failures due to cloud platform limitations.

Enable machine health checks when scaling to large node counts. In case of failures, the health checks monitor the condition and automatically repair unhealthy machines.

When scaling large and dense clusters to lower node counts, it might take large amounts of time because the process involves draining or evicting the objects running on the nodes being terminated in parallel. Also, the client might start to throttle the requests if there are too many objects to evict. The default client queries per second (QPS) and burst rates are currently set to50and100respectively. These values cannot be modified in OpenShift Container Platform.

### 2.1.2. Control plane node sizingCopy linkLink copied to clipboard!

To ensure optimal performance and stability, determine the resource requirements for control plane nodes. These sizing guidelines depend on the number and type of nodes and objects in your cluster.

The following control plane node size recommendations are based on the results of a control plane density focused testing, orCluster-density. This test creates the following objects across a given number of namespaces:

- 1 image stream
- 1 build
- 5 deployments, with 2 pod replicas in asleepstate, mounting 4 secrets, 4 config maps, and 1 downward API volume each
- 5 services, each one pointing to the TCP/8080 and TCP/8443 ports of one of the previous deployments
- 1 route pointing to the first of the previous services
- 10 secrets containing 2048 random string characters
- 10 config maps containing 2048 random string characters
| Number of compute nodes | Cluster-density (namespaces) | CPU cores | Memory (GB) |
| --- | --- | --- | --- |
| 24 | 500 | 4 | 16 |
| 120 | 1000 | 8 | 32 |
| 252 | 4000 | 16, but 24 if using the OVN-Kubernetes network plug-in | 64, but 128 if using the OVN-Kubernetes network plug-in |
| 501, but untested with the OVN-Kubernetes network plug-in | 4000 | 16 | 96 |

24

500

4

16

120

1000

8

32

252

4000

16, but 24 if using the OVN-Kubernetes network plug-in

64, but 128 if using the OVN-Kubernetes network plug-in

501, but untested with the OVN-Kubernetes network plug-in

4000

16

96

The data from the table above is based on an OpenShift Container Platform running on top of AWS, using r5.4xlarge instances as control-plane nodes and m5.2xlarge instances as compute nodes.

On a large and dense cluster with three control plane nodes, the CPU and memory usage will spike up when one of the nodes is stopped, rebooted, or fails. The failures can be due to unexpected issues with power, network, underlying infrastructure, or intentional cases where the cluster is restarted after shutting it down to save costs. The remaining two control plane nodes must handle the load in order to be highly available, which leads to increase in the resource usage. This is also expected during upgrades because the control plane nodes are cordoned, drained, and rebooted serially to apply the operating system updates, as well as the control plane Operators update. To avoid cascading failures, keep the overall CPU and memory resource usage on the control plane nodes to at most 60% of all available capacity to handle the resource usage spikes. Increase the CPU and memory on the control plane nodes accordingly to avoid potential downtime due to lack of resources.

The node sizing varies depending on the number of nodes and object counts in the cluster. It also depends on whether the objects are actively being created on the cluster. During object creation, the control plane is more active in terms of resource usage compared to when the objects are in theRunningphase.

Operator Lifecycle Manager (OLM) runs on the control plane nodes and its memory footprint depends on the number of namespaces and user installed operators that OLM needs to manage on the cluster. Control plane nodes need to be sized accordingly to avoid OOM kills. Following data points are based on the results from cluster maximums testing.

| Number of namespaces | OLM memory at idle state (GB) | OLM memory with 5 user operators installed (GB) |
| --- | --- | --- |
| 500 | 0.823 | 1.7 |
| 1000 | 1.2 | 2.5 |
| 1500 | 1.7 | 3.2 |
| 2000 | 2 | 4.4 |
| 3000 | 2.7 | 5.6 |
| 4000 | 3.8 | 7.6 |
| 5000 | 4.2 | 9.02 |
| 6000 | 5.8 | 11.3 |
| 7000 | 6.6 | 12.9 |
| 8000 | 6.9 | 14.8 |
| 9000 | 8 | 17.7 |
| 10,000 | 9.9 | 21.6 |

500

0.823

1.7

1000

1.2

2.5

1500

1.7

3.2

2000

2

4.4

3000

2.7

5.6

4000

3.8

7.6

5000

4.2

9.02

6000

5.8

11.3

7000

6.6

12.9

8000

6.9

14.8

9000

8

17.7

10,000

9.9

21.6

You can modify the control plane node size in a running OpenShift Container Platform 4.17 cluster for the following configurations only:

- Clusters installed with a user-provisioned installation method.
- AWS clusters installed with an installer-provisioned infrastructure installation method.
- Clusters that use a control plane machine set to manage control plane machines.

For all other configurations, you must estimate your total node count and use the suggested control plane node size during installation.

In OpenShift Container Platform 4.17, half of a CPU core (500 millicore) is now reserved by the system by default compared to OpenShift Container Platform 3.11 and previous versions. The sizes are determined taking that into consideration.

## 2.2. Selecting a larger AWS instance type for control plane machinesCopy linkLink copied to clipboard!

If the control plane machines in an Amazon Web Services (AWS) cluster require more resources, you can select a larger AWS instance type for the control plane machines to use.

The procedure for clusters that use a control plane machine set is different from the procedure for clusters that do not use a control plane machine set.

If you are uncertain about the state of theControlPlaneMachineSetCR in your cluster, you can verify the CR status.

### 2.2.2. Changing the Amazon Web Services instance type by using a control plane machine setCopy linkLink copied to clipboard!

You can change the Amazon Web Services (AWS) instance type that your control plane machines use by updating the specification in the control plane machine set custom resource (CR).

Prerequisites

- Your AWS cluster uses a control plane machine set.

Procedure

- Edit the following line under theproviderSpecfield:providerSpec:
  value:
    ...
    instanceType: <compatible_aws_instance_type>providerSpec:value:...instanceType:<compatible_aws_instance_type>Copy to ClipboardCopied!Toggle word wrapToggle overflow<compatible_aws_instance_type>: Specifies a larger AWS instance type with the same base as the previous selection. For example, you can changem6i.xlargetom6i.2xlargeorm6i.4xlarge.

Edit the following line under theproviderSpecfield:

```
providerSpec:
  value:
    ...
    instanceType: <compatible_aws_instance_type>
```

```
providerSpec:
  value:
    ...
    instanceType: <compatible_aws_instance_type>
```

- <compatible_aws_instance_type>: Specifies a larger AWS instance type with the same base as the previous selection. For example, you can changem6i.xlargetom6i.2xlargeorm6i.4xlarge.
- Save your changes.

### 2.2.3. Changing the Amazon Web Services instance type by using the AWS consoleCopy linkLink copied to clipboard!

You can change the Amazon Web Services (AWS) instance type that your control plane machines use by updating the instance type in the AWS console.

Prerequisites

- You have access to the AWS console with the permissions required to modify the EC2 Instance for your cluster.
- You have access to the OpenShift Container Platform cluster as a user with thecluster-adminrole.

Procedure

- Open the AWS console and fetch the instances for the control plane machines.
- Choose one control plane machine instance.For the selected control plane machine, back up the etcd data by creating an etcd snapshot. For more information, see "Backing up etcd".In the AWS console, stop the control plane machine instance.Select the stopped instance, and clickActionsInstance SettingsChange instance type.Change the instance to a larger type, ensuring that the type is the same base as the previous selection, and apply changes. For example, you can changem6i.xlargetom6i.2xlargeorm6i.4xlarge.Start the instance.If your OpenShift Container Platform cluster has a correspondingMachineobject for the instance, update the instance type of the object to match the instance type set in the AWS console.

Choose one control plane machine instance.

- For the selected control plane machine, back up the etcd data by creating an etcd snapshot. For more information, see "Backing up etcd".
- In the AWS console, stop the control plane machine instance.
- Select the stopped instance, and clickActionsInstance SettingsChange instance type.
- Change the instance to a larger type, ensuring that the type is the same base as the previous selection, and apply changes. For example, you can changem6i.xlargetom6i.2xlargeorm6i.4xlarge.
- Start the instance.
- If your OpenShift Container Platform cluster has a correspondingMachineobject for the instance, update the instance type of the object to match the instance type set in the AWS console.
- Repeat this process for each control plane machine.

## 2.3. Recommended infrastructure practicesCopy linkLink copied to clipboard!

This topic provides recommended performance and scalability practices for infrastructure in OpenShift Container Platform.

### 2.3.1. Infrastructure node sizingCopy linkLink copied to clipboard!

Infrastructure nodesare nodes that are labeled to run pieces of the OpenShift Container Platform environment. The infrastructure node resource requirements depend on the cluster age, nodes, and objects in the cluster, as these factors can lead to an increase in the number of metrics or time series in Prometheus. The following infrastructure node size recommendations are based on the results observed in cluster-density testing detailed in theControl plane node sizingsection, where the monitoring stack and the default ingress-controller were moved to these nodes.

| Number of worker nodes | Cluster density, or number of namespaces | CPU cores | Memory (GB) |
| --- | --- | --- | --- |
| 27 | 500 | 4 | 24 |
| 120 | 1000 | 8 | 48 |
| 252 | 4000 | 16 | 128 |
| 501 | 4000 | 32 | 128 |

27

500

4

24

120

1000

8

48

252

4000

16

128

501

4000

32

128

In general, three infrastructure nodes are recommended per cluster.

These sizing recommendations should be used as a guideline. Prometheus is a highly memory intensive application; the resource usage depends on various factors including the number of nodes, objects, the Prometheus metrics scraping interval, metrics or time series, and the age of the cluster. In addition, the router resource usage can also be affected by the number of routes and the amount/type of inbound requests.

These recommendations apply only to infrastructure nodes hosting Monitoring, Ingress and Registry infrastructure components installed during cluster creation.

In OpenShift Container Platform 4.17, half of a CPU core (500 millicore) is now reserved by the system by default compared to OpenShift Container Platform 3.11 and previous versions. This influences the stated sizing recommendations.

### 2.3.2. Scaling the Cluster Monitoring OperatorCopy linkLink copied to clipboard!

OpenShift Container Platform exposes metrics that the Cluster Monitoring Operator (CMO) collects and stores in the Prometheus-based monitoring stack. As an administrator, you can view dashboards for system resources, containers, and components metrics in the OpenShift Container Platform web console by navigating toObserveDashboards.

### 2.3.3. Prometheus database storage requirementsCopy linkLink copied to clipboard!

Red Hat performed various tests for different scale sizes.

- The following Prometheus storage requirements are not prescriptive and should be used as a reference. Higher resource consumption might be observed in your cluster depending on workload activity and resource density, including the number of pods, containers, routes, or other resources exposing metrics collected by Prometheus.
- You can configure the size-based data retention policy to suit your storage requirements.
| Number of nodes | Number of pods (2 containers per pod) | Prometheus storage growth per day | Prometheus storage growth per 15 days | Network (per tsdb chunk) |
| --- | --- | --- | --- | --- |
| 50 | 1800 | 6.3 GB | 94 GB | 16 MB |
| 100 | 3600 | 13 GB | 195 GB | 26 MB |
| 150 | 5400 | 19 GB | 283 GB | 36 MB |
| 200 | 7200 | 25 GB | 375 GB | 46 MB |

50

1800

6.3 GB

94 GB

16 MB

100

3600

13 GB

195 GB

26 MB

150

5400

19 GB

283 GB

36 MB

200

7200

25 GB

375 GB

46 MB

Approximately 20 percent of the expected size was added as overhead to ensure that the storage requirements do not exceed the calculated value.

The above calculation is for the default OpenShift Container Platform Cluster Monitoring Operator.

CPU utilization has minor impact. The ratio is approximately 1 core out of 40 per 50 nodes and 1800 pods.

Recommendations for OpenShift Container Platform

- Use at least two infrastructure (infra) nodes.
- Use at least threeopenshift-container-storagenodes with non-volatile memory express (SSD or NVMe) drives.

### 2.3.4. Configuring cluster monitoringCopy linkLink copied to clipboard!

You can increase the storage capacity for the Prometheus component in the cluster monitoring stack.

Procedure

To increase the storage capacity for Prometheus:

- Create a YAML configuration file,cluster-monitoring-config.yaml. For example:apiVersion: v1
kind: ConfigMap
data:
  config.yaml: |
    prometheusK8s:
      retention: {{PROMETHEUS_RETENTION_PERIOD}} 
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}} 
          resources:
            requests:
              storage: {{PROMETHEUS_STORAGE_SIZE}} 
    alertmanagerMain:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}} 
          resources:
            requests:
              storage: {{ALERTMANAGER_STORAGE_SIZE}} 
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoringapiVersion:v1kind:ConfigMapdata:config.yaml:|prometheusK8s:
      retention: {{PROMETHEUS_RETENTION_PERIOD}}1nodeSelector:node-role.kubernetes.io/infra:""volumeClaimTemplate:spec:storageClassName:{{STORAGE_CLASS}}2resources:requests:storage:{{PROMETHEUS_STORAGE_SIZE}}3alertmanagerMain:nodeSelector:node-role.kubernetes.io/infra:""volumeClaimTemplate:spec:storageClassName:{{STORAGE_CLASS}}4resources:requests:storage:{{ALERTMANAGER_STORAGE_SIZE}}5metadata:name:cluster-monitoring-confignamespace:openshift-monitoringCopy to ClipboardCopied!Toggle word wrapToggle overflow1The default value of Prometheus retention isPROMETHEUS_RETENTION_PERIOD=15d. Units are measured in time using one of these suffixes: s, m, h, d.24The storage class for your cluster.3A typical value isPROMETHEUS_STORAGE_SIZE=2000Gi. Storage values can be a plain integer or a fixed-point integer using one of these suffixes: E, P, T, G, M, K. You can also use the power-of-two equivalents: Ei, Pi, Ti, Gi, Mi, Ki.5A typical value isALERTMANAGER_STORAGE_SIZE=20Gi. Storage values can be a plain integer or a fixed-point integer using one of these suffixes: E, P, T, G, M, K. You can also use the power-of-two equivalents: Ei, Pi, Ti, Gi, Mi, Ki.

Create a YAML configuration file,cluster-monitoring-config.yaml. For example:

```
apiVersion: v1
kind: ConfigMap
data:
  config.yaml: |
    prometheusK8s:
      retention: {{PROMETHEUS_RETENTION_PERIOD}} 
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}} 
          resources:
            requests:
              storage: {{PROMETHEUS_STORAGE_SIZE}} 
    alertmanagerMain:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}} 
          resources:
            requests:
              storage: {{ALERTMANAGER_STORAGE_SIZE}} 
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
```

```
apiVersion: v1
kind: ConfigMap
data:
  config.yaml: |
    prometheusK8s:
      retention: {{PROMETHEUS_RETENTION_PERIOD}}
```

```
nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}}
```

```
resources:
            requests:
              storage: {{PROMETHEUS_STORAGE_SIZE}}
```

```
alertmanagerMain:
      nodeSelector:
        node-role.kubernetes.io/infra: ""
      volumeClaimTemplate:
        spec:
          storageClassName: {{STORAGE_CLASS}}
```

```
resources:
            requests:
              storage: {{ALERTMANAGER_STORAGE_SIZE}}
```

```
metadata:
  name: cluster-monitoring-config
  namespace: openshift-monitoring
```

**1**
  The default value of Prometheus retention isPROMETHEUS_RETENTION_PERIOD=15d. Units are measured in time using one of these suffixes: s, m, h, d.

**24**
  The storage class for your cluster.

**3**
  A typical value isPROMETHEUS_STORAGE_SIZE=2000Gi. Storage values can be a plain integer or a fixed-point integer using one of these suffixes: E, P, T, G, M, K. You can also use the power-of-two equivalents: Ei, Pi, Ti, Gi, Mi, Ki.

**5**
  A typical value isALERTMANAGER_STORAGE_SIZE=20Gi. Storage values can be a plain integer or a fixed-point integer using one of these suffixes: E, P, T, G, M, K. You can also use the power-of-two equivalents: Ei, Pi, Ti, Gi, Mi, Ki.
- Add values for the retention period, storage class, and storage sizes.
- Save the file.
- Apply the changes by running:oc create -f cluster-monitoring-config.yaml$oc create-fcluster-monitoring-config.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Apply the changes by running:

## 2.4. Recommended etcd practicesCopy linkLink copied to clipboard!

To ensure optimal performance and scalability for etcd in OpenShift Container Platform, you can complete the following practices.

### 2.4.1. Storage practices for etcdCopy linkLink copied to clipboard!

Because etcd writes data to disk and persists proposals on disk, its performance depends on disk performance. Although etcd is not particularly I/O intensive, it requires a low latency block device for optimal performance and stability. Because the consensus protocol for etcd depends on persistently storing metadata to a log (WAL), etcd is sensitive to disk-write latency. Slow disks and disk activity from other processes can cause long fsync latencies.

Those latencies can cause etcd to miss heartbeats, not commit new proposals to the disk on time, and ultimately experience request timeouts and temporary leader loss. High write latencies also lead to an OpenShift API slowness, which affects cluster performance. Because of these reasons, avoid colocating other workloads on the control-plane nodes that are I/O sensitive or intensive and share the same underlying I/O infrastructure.

Run etcd on a block device that can write at least 50 IOPS of 8KB sequentially, including fdatasync, in under 10ms. For heavy loaded clusters, sequential 500 IOPS of 8000 bytes (2 ms) are recommended. To measure those numbers, you can use a benchmarking tool, such as thefiocommand.

To achieve such performance, run etcd on machines that are backed by SSD or NVMe disks with low latency and high throughput. Consider single-level cell (SLC) solid-state drives (SSDs), which provide 1 bit per memory cell, are durable and reliable, and are ideal for write-intensive workloads.

The load on etcd arises from static factors, such as the number of nodes and pods, and dynamic factors, including changes in endpoints due to pod autoscaling, pod restarts, job executions, and other workload-related events. To accurately size your etcd setup, you must analyze the specific requirements of your workload. Consider the number of nodes, pods, and other relevant factors that impact the load on etcd.

The following hard drive practices provide optimal etcd performance:

- Use dedicated etcd drives. Avoid drives that communicate over the network, such as iSCSI. Do not place log files or other heavy workloads on etcd drives.
- Prefer drives with low latency to support fast read and write operations.
- Prefer high-bandwidth writes for faster compactions and defragmentation.
- Prefer high-bandwidth reads for faster recovery from failures.
- Use solid state drives as a minimum selection. Prefer NVMe drives for production environments.
- Use server-grade hardware for increased reliability.
- Avoid NAS or SAN setups and spinning drives. Ceph Rados Block Device (RBD) and other types of network-attached storage can result in unpredictable network latency. To provide fast storage to etcd nodes at scale, use PCI passthrough to pass NVM devices directly to the nodes.
- Always benchmark by using utilities such asfio. You can use such utilities to continuously monitor the cluster performance as it increases.
- Avoid using the Network File System (NFS) protocol or other network based file systems.

Some key metrics to monitor on a deployed OpenShift Container Platform cluster are p99 of etcd disk write ahead log duration and the number of etcd leader changes. Use Prometheus to track these metrics.

The etcd member database sizes can vary in a cluster during normal operations. This difference does not affect cluster upgrades, even if the leader size is different from the other members.

### 2.4.2. Validating the hardware for etcdCopy linkLink copied to clipboard!

To validate the hardware for etcd before or after you create the OpenShift Container Platform cluster, you can use fio.

Prerequisites

- Container runtimes such as Podman or Docker are installed on the machine that you are testing.
- Data is written to the/var/lib/etcdpath.

Procedure

- Run fio and analyze the results:If you use Podman, run this command:sudo podman run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perf$sudopodmanrun--volume/var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perfCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you use Docker, run this command:sudo docker run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perf$sudodockerrun--volume/var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perfCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run fio and analyze the results:

- If you use Podman, run this command:sudo podman run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perf$sudopodmanrun--volume/var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perfCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you use Podman, run this command:

- If you use Docker, run this command:sudo docker run --volume /var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perf$sudodockerrun--volume/var/lib/etcd:/var/lib/etcd:Z quay.io/cloud-bulldozer/etcd-perfCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you use Docker, run this command:

The output reports whether the disk is fast enough to host etcd by comparing the 99th percentile of the fsync metric captured from the run to see if it is less than 10 ms. A few of the most important etcd metrics that might affected by I/O performance are as follows:

- etcd_disk_wal_fsync_duration_seconds_bucketmetric reports the etcd’s WAL fsync duration
- etcd_disk_backend_commit_duration_seconds_bucketmetric reports the etcd backend commit latency duration
- etcd_server_leader_changes_seen_totalmetric reports the leader changes

Because etcd replicates the requests among all the members, its performance strongly depends on network input/output (I/O) latency. High network latencies result in etcd heartbeats taking longer than the election timeout, which results in leader elections that are disruptive to the cluster. A key metric to monitor on a deployed OpenShift Container Platform cluster is the 99th percentile of etcd network peer latency on each etcd cluster member. Use Prometheus to track the metric.

Thehistogram_quantile(0.99, rate(etcd_network_peer_round_trip_time_seconds_bucket[2m]))metric reports the round trip time for etcd to finish replicating the client requests between the members. Ensure that it is less than 50 ms.

### 2.4.3. Node scaling for etcdCopy linkLink copied to clipboard!

In general, clusters must have 3 control plane nodes. However, if your cluster is installed on a bare metal platform, you can scale a cluster up to 5 control plane nodes as a postinstallation task. For example, to scale from 3 to 4 control plane nodes after installation, you can add a host and install it as a control plane node. Then, the etcd Operator scales accordingly to account for the additional control plane node.

Scaling a cluster to 4 or 5 control plane nodes is available only on bare metal platforms.

For more information about how to scale control plane nodes by using the Assisted Installer, see "Adding hosts with the API" and "Replacing a control plane node in a healthy cluster".

The following table shows failure tolerance for clusters of different sizes:

| Cluster size | Majority | Failure tolerance |
| --- | --- | --- |
| 1 node | 1 | 0 |
| 3 nodes | 2 | 1 |
| 4 nodes | 3 | 1 |
| 5 nodes | 3 | 2 |

1 node

1

0

3 nodes

2

1

4 nodes

3

1

5 nodes

3

2

For more information about recovering from quorum loss, see "Restoring to a previous cluster state".

### 2.4.4. Moving etcd to a different diskCopy linkLink copied to clipboard!

You can move etcd from a shared disk to a separate disk to prevent or resolve performance issues.

The Machine Config Operator (MCO) is responsible for mounting a secondary disk for OpenShift Container Platform 4.17 container storage.

This encoded script only supports device names for the following device types:

**SCSI or SATA**
  /dev/sd*

**Virtual device**
  /dev/vd*

**NVMe**
  /dev/nvme*[0-9]*n*

Limitations

- When the new disk is attached to the cluster, the etcd database is part of the root mount. It is not part of the secondary disk or the intended disk when the primary node is recreated. As a result, the primary node will not create a separate/var/lib/etcdmount.

Prerequisites

- You have a backup of your cluster’s etcd data.
- You have installed the OpenShift CLI (oc).
- You have access to the cluster withcluster-adminprivileges.
- Add additional disks before uploading the machine configuration.
- TheMachineConfigPoolmust matchmetadata.labels[machineconfiguration.openshift.io/role]. This applies to a controller, worker, or a custom pool.

This procedure does not move parts of the root file system, such as/var/, to another disk or partition on an installed node.

This procedure is not supported when using control plane machine sets.

Procedure

- Attach the new disk to the cluster and verify that the disk is detected in the node by running thelsblkcommand in a debug shell:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowlsblk#lsblkCopy to ClipboardCopied!Toggle word wrapToggle overflowNote the device name of the new disk reported by thelsblkcommand.

Attach the new disk to the cluster and verify that the disk is detected in the node by running thelsblkcommand in a debug shell:

Note the device name of the new disk reported by thelsblkcommand.

- Create the following script and name itetcd-find-secondary-device.sh:#!/bin/bash
set -uo pipefail

for device in <device_type_glob>; do 
/usr/sbin/blkid "${device}" &> /dev/null
 if [ $? == 2  ]; then
    echo "secondary device found ${device}"
    echo "creating filesystem for etcd mount"
    mkfs.xfs -L var-lib-etcd -f "${device}" &> /dev/null
    udevadm settle
    touch /etc/var-lib-etcd-mount
    exit
 fi
done
echo "Couldn't find secondary block device!" >&2
exit 77#!/bin/bashset-uopipefailfordevicein<device_type_glob>;do1/usr/sbin/blkid"${device}"&>/dev/nullif[$?==2];thenecho"secondary device found${device}"echo"creating filesystem for etcd mount"mkfs.xfs-Lvar-lib-etcd-f"${device}"&>/dev/null
    udevadm settletouch/etc/var-lib-etcd-mountexitfidoneecho"Couldn't find secondary block device!">&2exit77Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<device_type_glob>with a shell glob for your block device type. For SCSI or SATA drives, use/dev/sd*; for virtual drives, use/dev/vd*; for NVMe drives, use/dev/nvme*[0-9]*n*.

Create the following script and name itetcd-find-secondary-device.sh:

```
#!/bin/bash
set -uo pipefail

for device in <device_type_glob>; do 
/usr/sbin/blkid "${device}" &> /dev/null
 if [ $? == 2  ]; then
    echo "secondary device found ${device}"
    echo "creating filesystem for etcd mount"
    mkfs.xfs -L var-lib-etcd -f "${device}" &> /dev/null
    udevadm settle
    touch /etc/var-lib-etcd-mount
    exit
 fi
done
echo "Couldn't find secondary block device!" >&2
exit 77
```

```
#!/bin/bash
set -uo pipefail

for device in <device_type_glob>; do
```

```
/usr/sbin/blkid "${device}" &> /dev/null
 if [ $? == 2  ]; then
    echo "secondary device found ${device}"
    echo "creating filesystem for etcd mount"
    mkfs.xfs -L var-lib-etcd -f "${device}" &> /dev/null
    udevadm settle
    touch /etc/var-lib-etcd-mount
    exit
 fi
done
echo "Couldn't find secondary block device!" >&2
exit 77
```

**1**
  Replace<device_type_glob>with a shell glob for your block device type. For SCSI or SATA drives, use/dev/sd*; for virtual drives, use/dev/vd*; for NVMe drives, use/dev/nvme*[0-9]*n*.
- Create a base64-encoded string from theetcd-find-secondary-device.shscript and note its contents:base64 -w0 etcd-find-secondary-device.sh$base64-w0etcd-find-secondary-device.shCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a base64-encoded string from theetcd-find-secondary-device.shscript and note its contents:

- Create aMachineConfigYAML file namedetcd-mc.ymlwith contents such as the following:apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 98-var-lib-etcd
spec:
  config:
    ignition:
      version: 3.4.0
    storage:
      files:
        - path: /etc/find-secondary-device
          mode: 0755
          contents:
            source: data:text/plain;charset=utf-8;base64,<encoded_etcd_find_secondary_device_script> 
    systemd:
      units:
        - name: find-secondary-device.service
          enabled: true
          contents: |
            [Unit]
            Description=Find secondary device
            DefaultDependencies=false
            After=systemd-udev-settle.service
            Before=local-fs-pre.target
            ConditionPathExists=!/etc/var-lib-etcd-mount

            [Service]
            RemainAfterExit=yes
            ExecStart=/etc/find-secondary-device

            RestartForceExitStatus=77

            [Install]
            WantedBy=multi-user.target
        - name: var-lib-etcd.mount
          enabled: true
          contents: |
            [Unit]
            Before=local-fs.target

            [Mount]
            What=/dev/disk/by-label/var-lib-etcd
            Where=/var/lib/etcd
            Type=xfs
            TimeoutSec=120s

            [Install]
            RequiredBy=local-fs.target
        - name: sync-var-lib-etcd-to-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Sync etcd data if new mount is empty
            DefaultDependencies=no
            After=var-lib-etcd.mount var.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecCondition=/usr/bin/test ! -d /var/lib/etcd/member
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 1
            ExecStart=/bin/rsync -ar /sysroot/ostree/deploy/rhcos/var/lib/etcd/ /var/lib/etcd/
            ExecStart=/usr/sbin/semanage fcontext -a -t container_var_lib_t '/var/lib/etcd(/.*)?'
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 0
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.target
        - name: restorecon-var-lib-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Restore recursive SELinux security contexts
            DefaultDependencies=no
            After=var-lib-etcd.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecStart=/sbin/restorecon -R /var/lib/etcd/
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.targetapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:mastername:98-var-lib-etcdspec:config:ignition:version:3.4.0storage:files:-path:/etc/find-secondary-devicemode:0755contents:source:data:text/plain;charset=utf-8;base64,<encoded_etcd_find_secondary_device_script>1systemd:units:-name:find-secondary-device.serviceenabled:truecontents:|[Unit]
            Description=Find secondary device
            DefaultDependencies=false
            After=systemd-udev-settle.service
            Before=local-fs-pre.target
            ConditionPathExists=!/etc/var-lib-etcd-mount[Service]RemainAfterExit=yes
            ExecStart=/etc/find-secondary-device

            RestartForceExitStatus=77[Install]WantedBy=multi-user.target-name:var-lib-etcd.mountenabled:truecontents:|[Unit]
            Before=local-fs.target[Mount]What=/dev/disk/by-label/var-lib-etcd
            Where=/var/lib/etcd
            Type=xfs
            TimeoutSec=120s[Install]RequiredBy=local-fs.target-name:sync-var-lib-etcd-to-etcd.serviceenabled:truecontents:|[Unit]
            Description=Sync etcd data if new mount is empty
            DefaultDependencies=no
            After=var-lib-etcd.mount var.mount
            Before=crio.service[Service]Type=oneshot
            RemainAfterExit=yes
            ExecCondition=/usr/bin/test!-d /var/lib/etcd/member
            ExecStart=/usr/sbin/setsebool-P rsync_full_access 1
            ExecStart=/bin/rsync-ar /sysroot/ostree/deploy/rhcos/var/lib/etcd/ /var/lib/etcd/
            ExecStart=/usr/sbin/semanage fcontext-a-t container_var_lib_t '/var/lib/etcd(/.*)?'ExecStart=/usr/sbin/setsebool-P rsync_full_access 0
            TimeoutSec=0[Install]WantedBy=multi-user.target graphical.target-name:restorecon-var-lib-etcd.serviceenabled:truecontents:|[Unit]
            Description=Restore recursive SELinux security contexts
            DefaultDependencies=no
            After=var-lib-etcd.mount
            Before=crio.service[Service]Type=oneshot
            RemainAfterExit=yes
            ExecStart=/sbin/restorecon-R /var/lib/etcd/
            TimeoutSec=0[Install]WantedBy=multi-user.target graphical.targetCopy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<encoded_etcd_find_secondary_device_script>with the encoded script contents that you noted.

Create aMachineConfigYAML file namedetcd-mc.ymlwith contents such as the following:

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 98-var-lib-etcd
spec:
  config:
    ignition:
      version: 3.4.0
    storage:
      files:
        - path: /etc/find-secondary-device
          mode: 0755
          contents:
            source: data:text/plain;charset=utf-8;base64,<encoded_etcd_find_secondary_device_script> 
    systemd:
      units:
        - name: find-secondary-device.service
          enabled: true
          contents: |
            [Unit]
            Description=Find secondary device
            DefaultDependencies=false
            After=systemd-udev-settle.service
            Before=local-fs-pre.target
            ConditionPathExists=!/etc/var-lib-etcd-mount

            [Service]
            RemainAfterExit=yes
            ExecStart=/etc/find-secondary-device

            RestartForceExitStatus=77

            [Install]
            WantedBy=multi-user.target
        - name: var-lib-etcd.mount
          enabled: true
          contents: |
            [Unit]
            Before=local-fs.target

            [Mount]
            What=/dev/disk/by-label/var-lib-etcd
            Where=/var/lib/etcd
            Type=xfs
            TimeoutSec=120s

            [Install]
            RequiredBy=local-fs.target
        - name: sync-var-lib-etcd-to-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Sync etcd data if new mount is empty
            DefaultDependencies=no
            After=var-lib-etcd.mount var.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecCondition=/usr/bin/test ! -d /var/lib/etcd/member
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 1
            ExecStart=/bin/rsync -ar /sysroot/ostree/deploy/rhcos/var/lib/etcd/ /var/lib/etcd/
            ExecStart=/usr/sbin/semanage fcontext -a -t container_var_lib_t '/var/lib/etcd(/.*)?'
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 0
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.target
        - name: restorecon-var-lib-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Restore recursive SELinux security contexts
            DefaultDependencies=no
            After=var-lib-etcd.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecStart=/sbin/restorecon -R /var/lib/etcd/
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.target
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 98-var-lib-etcd
spec:
  config:
    ignition:
      version: 3.4.0
    storage:
      files:
        - path: /etc/find-secondary-device
          mode: 0755
          contents:
            source: data:text/plain;charset=utf-8;base64,<encoded_etcd_find_secondary_device_script>
```

```
systemd:
      units:
        - name: find-secondary-device.service
          enabled: true
          contents: |
            [Unit]
            Description=Find secondary device
            DefaultDependencies=false
            After=systemd-udev-settle.service
            Before=local-fs-pre.target
            ConditionPathExists=!/etc/var-lib-etcd-mount

            [Service]
            RemainAfterExit=yes
            ExecStart=/etc/find-secondary-device

            RestartForceExitStatus=77

            [Install]
            WantedBy=multi-user.target
        - name: var-lib-etcd.mount
          enabled: true
          contents: |
            [Unit]
            Before=local-fs.target

            [Mount]
            What=/dev/disk/by-label/var-lib-etcd
            Where=/var/lib/etcd
            Type=xfs
            TimeoutSec=120s

            [Install]
            RequiredBy=local-fs.target
        - name: sync-var-lib-etcd-to-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Sync etcd data if new mount is empty
            DefaultDependencies=no
            After=var-lib-etcd.mount var.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecCondition=/usr/bin/test ! -d /var/lib/etcd/member
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 1
            ExecStart=/bin/rsync -ar /sysroot/ostree/deploy/rhcos/var/lib/etcd/ /var/lib/etcd/
            ExecStart=/usr/sbin/semanage fcontext -a -t container_var_lib_t '/var/lib/etcd(/.*)?'
            ExecStart=/usr/sbin/setsebool -P rsync_full_access 0
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.target
        - name: restorecon-var-lib-etcd.service
          enabled: true
          contents: |
            [Unit]
            Description=Restore recursive SELinux security contexts
            DefaultDependencies=no
            After=var-lib-etcd.mount
            Before=crio.service

            [Service]
            Type=oneshot
            RemainAfterExit=yes
            ExecStart=/sbin/restorecon -R /var/lib/etcd/
            TimeoutSec=0

            [Install]
            WantedBy=multi-user.target graphical.target
```

**1**
  Replace<encoded_etcd_find_secondary_device_script>with the encoded script contents that you noted.

Verification steps

- Run thegrep /var/lib/etcd /proc/mountscommand in a debug shell for the node to ensure that the disk is mounted:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowgrep -w "/var/lib/etcd" /proc/mounts#grep-w"/var/lib/etcd"/proc/mountsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output/dev/sdb /var/lib/etcd xfs rw,seclabel,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0/dev/sdb /var/lib/etcd xfs rw,seclabel,relatime,attr2,inode64,logbufs=8,logbsize=32k,noquota 0 0Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run thegrep /var/lib/etcd /proc/mountscommand in a debug shell for the node to ensure that the disk is mounted:

Example output

### 2.4.5. Defragmenting etcd dataCopy linkLink copied to clipboard!

For large and dense clusters, etcd can suffer from poor performance if the keyspace grows too large and exceeds the space quota. Periodically maintain and defragment etcd to free up space in the data store. Monitor Prometheus for etcd metrics and defragment it when required; otherwise, etcd can raise a cluster-wide alarm that puts the cluster into a maintenance mode that accepts only key reads and deletes.

Monitor these key metrics:

- etcd_server_quota_backend_bytes, which is the current quota limit
- etcd_mvcc_db_total_size_in_use_in_bytes, which indicates the actual database usage after a history compaction
- etcd_mvcc_db_total_size_in_bytes, which shows the database size, including free space waiting for defragmentation

Defragment etcd data to reclaim disk space after events that cause disk fragmentation, such as etcd history compaction.

History compaction is performed automatically every five minutes and leaves gaps in the back-end database. This fragmented space is available for use by etcd, but is not available to the host file system. You must defragment etcd to make this space available to the host file system.

Defragmentation occurs automatically, but you can also trigger it manually.

Automatic defragmentation is good for most cases, because the etcd operator uses cluster information to determine the most efficient operation for the user.

#### 2.4.5.1. Automatic defragmentationCopy linkLink copied to clipboard!

The etcd Operator automatically defragments disks. No manual intervention is needed.

Verify that the defragmentation process is successful by viewing one of these logs:

- etcd logs
- cluster-etcd-operator pod
- operator status error log

Automatic defragmentation can cause leader election failure in various OpenShift core components, such as the Kubernetes controller manager, which triggers a restart of the failing component. The restart is harmless and either triggers failover to the next running instance or the component resumes work again after the restart.

Example log output for successful defragmentation

Example log output for unsuccessful defragmentation

#### 2.4.5.2. Manual defragmentationCopy linkLink copied to clipboard!

A Prometheus alert indicates when you need to use manual defragmentation. The alert is displayed in two cases:

- When etcd uses more than 50% of its available space for more than 10 minutes
- When etcd is actively using less than 50% of its total database size for more than 10 minutes

You can also determine whether defragmentation is needed by checking the etcd database size in MB that will be freed by defragmentation with the PromQL expression:(etcd_mvcc_db_total_size_in_bytes - etcd_mvcc_db_total_size_in_use_in_bytes)/1024/1024

Defragmenting etcd is a blocking action. The etcd member will not respond until defragmentation is complete. For this reason, wait at least one minute between defragmentation actions on each of the pods to allow the cluster to recover.

Follow this procedure to defragment etcd data on each etcd member.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.

Procedure

- Determine which etcd member is the leader, because the leader should be defragmented last.Get the list of etcd pods:oc -n openshift-etcd get pods -l k8s-app=etcd -o wide$oc-nopenshift-etcd get pods-lk8s-app=etcd-owideCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputetcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>etcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>Copy to ClipboardCopied!Toggle word wrapToggle overflowChoose a pod and run the following command to determine which etcd member is the leader:oc rsh -n openshift-etcd etcd-ip-10-0-159-225.example.redhat.com etcdctl endpoint status --cluster -w table$oc rsh-nopenshift-etcd etcd-ip-10-0-159-225.example.redhat.com etcdctl endpoint status--cluster-wtableCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputDefaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Defaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Copy to ClipboardCopied!Toggle word wrapToggle overflowBased on theIS LEADERcolumn of this output, thehttps://[REDACTED_PRIVATE_IP]:2379endpoint is the leader. Matching this endpoint with the output of the previous step, the pod name of the leader isetcd-ip-10-0-199-170.example.redhat.com.

Determine which etcd member is the leader, because the leader should be defragmented last.

- Get the list of etcd pods:oc -n openshift-etcd get pods -l k8s-app=etcd -o wide$oc-nopenshift-etcd get pods-lk8s-app=etcd-owideCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputetcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>etcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Get the list of etcd pods:

Example output

```
etcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>
```

```
etcd-ip-10-0-159-225.example.redhat.com                3/3     Running     0          175m   [REDACTED_PRIVATE_IP]   ip-10-0-159-225.example.redhat.com   <none>           <none>
etcd-ip-10-0-191-37.example.redhat.com                 3/3     Running     0          173m   [REDACTED_PRIVATE_IP]    ip-10-0-191-37.example.redhat.com    <none>           <none>
etcd-ip-10-0-199-170.example.redhat.com                3/3     Running     0          176m   [REDACTED_PRIVATE_IP]   ip-10-0-199-170.example.redhat.com   <none>           <none>
```

- Choose a pod and run the following command to determine which etcd member is the leader:oc rsh -n openshift-etcd etcd-ip-10-0-159-225.example.redhat.com etcdctl endpoint status --cluster -w table$oc rsh-nopenshift-etcd etcd-ip-10-0-159-225.example.redhat.com etcdctl endpoint status--cluster-wtableCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputDefaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Defaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Copy to ClipboardCopied!Toggle word wrapToggle overflowBased on theIS LEADERcolumn of this output, thehttps://[REDACTED_PRIVATE_IP]:2379endpoint is the leader. Matching this endpoint with the output of the previous step, the pod name of the leader isetcd-ip-10-0-199-170.example.redhat.com.

Choose a pod and run the following command to determine which etcd member is the leader:

Example output

```
Defaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

```
Defaulting container name to etcdctl.
Use 'oc describe pod/etcd-ip-10-0-159-225.example.redhat.com -n openshift-etcd' to see all of the containers in this pod.
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

Based on theIS LEADERcolumn of this output, thehttps://[REDACTED_PRIVATE_IP]:2379endpoint is the leader. Matching this endpoint with the output of the previous step, the pod name of the leader isetcd-ip-10-0-199-170.example.redhat.com.

- Defragment an etcd member.Connect to the running etcd container, passing in the name of a pod that isnotthe leader:oc rsh -n openshift-etcd etcd-ip-10-0-159-225.example.redhat.com$oc rsh-nopenshift-etcd etcd-ip-10-0-159-225.example.redhat.comCopy to ClipboardCopied!Toggle word wrapToggle overflowUnset theETCDCTL_ENDPOINTSenvironment variable:unset ETCDCTL_ENDPOINTSsh-4.4# unset ETCDCTL_ENDPOINTSCopy to ClipboardCopied!Toggle word wrapToggle overflowDefragment the etcd member:etcdctl --command-timeout=30s --endpoints=https://localhost:2379 defragsh-4.4# etcdctl --command-timeout=30s --endpoints=https://localhost:2379 defragCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputFinished defragmenting etcd member[https://localhost:2379]Finished defragmenting etcd member[https://localhost:2379]Copy to ClipboardCopied!Toggle word wrapToggle overflowIf a timeout error occurs, increase the value for--command-timeoutuntil the command succeeds.Verify that the database size was reduced:etcdctl endpoint status -w table --clustersh-4.4# etcdctl endpoint status -w table --clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        | 
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------++---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        |1| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Copy to ClipboardCopied!Toggle word wrapToggle overflowThis example shows that the database size for this etcd member is now 41 MB as opposed to the starting size of 104 MB.Repeat these steps to connect to each of the other etcd members and defragment them. Always defragment the leader last.Wait at least one minute between defragmentation actions to allow the etcd pod to recover. Until the etcd pod recovers, the etcd member will not respond.

Defragment an etcd member.

- Connect to the running etcd container, passing in the name of a pod that isnotthe leader:oc rsh -n openshift-etcd etcd-ip-10-0-159-225.example.redhat.com$oc rsh-nopenshift-etcd etcd-ip-10-0-159-225.example.redhat.comCopy to ClipboardCopied!Toggle word wrapToggle overflow

Connect to the running etcd container, passing in the name of a pod that isnotthe leader:

- Unset theETCDCTL_ENDPOINTSenvironment variable:unset ETCDCTL_ENDPOINTSsh-4.4# unset ETCDCTL_ENDPOINTSCopy to ClipboardCopied!Toggle word wrapToggle overflow

Unset theETCDCTL_ENDPOINTSenvironment variable:

- Defragment the etcd member:etcdctl --command-timeout=30s --endpoints=https://localhost:2379 defragsh-4.4# etcdctl --command-timeout=30s --endpoints=https://localhost:2379 defragCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputFinished defragmenting etcd member[https://localhost:2379]Finished defragmenting etcd member[https://localhost:2379]Copy to ClipboardCopied!Toggle word wrapToggle overflowIf a timeout error occurs, increase the value for--command-timeoutuntil the command succeeds.

Defragment the etcd member:

Example output

If a timeout error occurs, increase the value for--command-timeoutuntil the command succeeds.

- Verify that the database size was reduced:etcdctl endpoint status -w table --clustersh-4.4# etcdctl endpoint status -w table --clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        | 
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------++---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        |1| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+Copy to ClipboardCopied!Toggle word wrapToggle overflowThis example shows that the database size for this etcd member is now 41 MB as opposed to the starting size of 104 MB.

Verify that the database size was reduced:

Example output

```
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        | 
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

```
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|         ENDPOINT          |        ID        | VERSION | DB SIZE | IS LEADER | IS LEARNER | RAFT TERM | RAFT INDEX | RAFT APPLIED INDEX | ERRORS |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
|  [REDACTED_INTERNAL_URL] | 251cd44483d811c3 |   3.5.9 |  104 MB |     false |      false |         7 |      91624 |              91624 |        |
| [REDACTED_INTERNAL_URL] | 264c7c58ecbdabee |   3.5.9 |   41 MB |     false |      false |         7 |      91624 |              91624 |        |
```

```
| [REDACTED_INTERNAL_URL] | 9ac311f93915cc79 |   3.5.9 |  104 MB |      true |      false |         7 |      91624 |              91624 |        |
+---------------------------+------------------+---------+---------+-----------+------------+-----------+------------+--------------------+--------+
```

This example shows that the database size for this etcd member is now 41 MB as opposed to the starting size of 104 MB.

- Repeat these steps to connect to each of the other etcd members and defragment them. Always defragment the leader last.Wait at least one minute between defragmentation actions to allow the etcd pod to recover. Until the etcd pod recovers, the etcd member will not respond.

Repeat these steps to connect to each of the other etcd members and defragment them. Always defragment the leader last.

Wait at least one minute between defragmentation actions to allow the etcd pod to recover. Until the etcd pod recovers, the etcd member will not respond.

- If anyNOSPACEalarms were triggered due to the space quota being exceeded, clear them.Check if there are anyNOSPACEalarms:etcdctl alarm listsh-4.4# etcdctl alarm listCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputmemberID:12345678912345678912 alarm:NOSPACEmemberID:12345678912345678912 alarm:NOSPACECopy to ClipboardCopied!Toggle word wrapToggle overflowClear the alarms:etcdctl alarm disarmsh-4.4# etcdctl alarm disarmCopy to ClipboardCopied!Toggle word wrapToggle overflow

If anyNOSPACEalarms were triggered due to the space quota being exceeded, clear them.

- Check if there are anyNOSPACEalarms:etcdctl alarm listsh-4.4# etcdctl alarm listCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputmemberID:12345678912345678912 alarm:NOSPACEmemberID:12345678912345678912 alarm:NOSPACECopy to ClipboardCopied!Toggle word wrapToggle overflow

Check if there are anyNOSPACEalarms:

Example output

- Clear the alarms:etcdctl alarm disarmsh-4.4# etcdctl alarm disarmCopy to ClipboardCopied!Toggle word wrapToggle overflow

Clear the alarms:

### 2.4.6. Setting tuning parameters for etcdCopy linkLink copied to clipboard!

You can set the control plane hardware speed to"Standard","Slower", or the default, which is"".

The default setting allows the system to decide which speed to use. This value enables upgrades from versions where this feature does not exist, as the system can select values from previous versions.

By selecting one of the other values, you are overriding the default. If you see many leader elections due to timeouts or missed heartbeats and your system is set to""or"Standard", set the hardware speed to"Slower"to make the system more tolerant to the increased latency.

#### 2.4.6.1. Changing hardware speed toleranceCopy linkLink copied to clipboard!

To change the hardware speed tolerance for etcd, complete the following steps.

Procedure

- Check to see what the current value is by entering the following command:oc describe etcd/cluster | grep "Control Plane Hardware Speed"$oc describe etcd/cluster|grep"Control Plane Hardware Speed"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputControl Plane Hardware Speed:  <VALUE>Control Plane Hardware Speed:  <VALUE>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the output is empty, the field has not been set and should be considered as the default ("").

Check to see what the current value is by entering the following command:

Example output

If the output is empty, the field has not been set and should be considered as the default ("").

- Change the value by entering the following command. Replace<value>with one of the valid values:"","Standard", or"Slower":oc patch etcd/cluster --type=merge -p '{"spec": {"controlPlaneHardwareSpeed": "<value>"}}'$oc patch etcd/cluster--type=merge-p'{"spec": {"controlPlaneHardwareSpeed": "<value>"}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowThe following table indicates the heartbeat interval and leader election timeout for each profile. These values are subject to change.ExpandProfileETCD_HEARTBEAT_INTERVALETCD_LEADER_ELECTION_TIMEOUT""Varies depending on platformVaries depending on platformStandard1001000Slower5002500

Change the value by entering the following command. Replace<value>with one of the valid values:"","Standard", or"Slower":

The following table indicates the heartbeat interval and leader election timeout for each profile. These values are subject to change.

| Profile | ETCD_HEARTBEAT_INTERVAL | ETCD_LEADER_ELECTION_TIMEOUT |
| --- | --- | --- |
| "" | Varies depending on platform | Varies depending on platform |
| Standard | 100 | 1000 |
| Slower | 500 | 2500 |

Profile

ETCD_HEARTBEAT_INTERVAL

ETCD_LEADER_ELECTION_TIMEOUT

""

Varies depending on platform

Varies depending on platform

Standard

100

1000

Slower

500

2500

- Review the output:Example outputetcd.operator.openshift.io/cluster patchedetcd.operator.openshift.io/cluster patchedCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you enter any value besides the valid values, error output is displayed. For example, if you entered"Faster"as the value, the output is as follows:Example outputThe Etcd "cluster" is invalid: spec.controlPlaneHardwareSpeed: Unsupported value: "Faster": supported values: "", "Standard", "Slower"The Etcd "cluster" is invalid: spec.controlPlaneHardwareSpeed: Unsupported value: "Faster": supported values: "", "Standard", "Slower"Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review the output:

Example output

If you enter any value besides the valid values, error output is displayed. For example, if you entered"Faster"as the value, the output is as follows:

Example output

- Verify that the value was changed by entering the following command:oc describe etcd/cluster | grep "Control Plane Hardware Speed"$oc describe etcd/cluster|grep"Control Plane Hardware Speed"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputControl Plane Hardware Speed:  ""Control Plane Hardware Speed:  ""Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the value was changed by entering the following command:

Example output

- Wait for etcd pods to roll out:oc get pods -n openshift-etcd -w$oc get pods-nopenshift-etcd-wCopy to ClipboardCopied!Toggle word wrapToggle overflowThe following output shows the expected entries for master-0. Before you continue, wait until all masters show a status of4/4 Running.Example outputinstaller-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          1s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           1/1     Running             0          2s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          34s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            0/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Pending             0          0s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:1/3            0          1s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:2/3            0          2s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     PodInitializing     0          3s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          4s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            1/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          20s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Running             0          20sinstaller-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          1s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           1/1     Running             0          2s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          34s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            0/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Pending             0          0s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:1/3            0          1s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:2/3            0          2s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     PodInitializing     0          3s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          4s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            1/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          20s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Running             0          20sCopy to ClipboardCopied!Toggle word wrapToggle overflow

Wait for etcd pods to roll out:

The following output shows the expected entries for master-0. Before you continue, wait until all masters show a status of4/4 Running.

Example output

```
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          1s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           1/1     Running             0          2s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          34s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            0/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Pending             0          0s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:1/3            0          1s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:2/3            0          2s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     PodInitializing     0          3s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          4s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            1/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          20s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Running             0          20s
```

```
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Pending             0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          0s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     ContainerCreating   0          1s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           1/1     Running             0          2s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          34s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
installer-9-ci-ln-qkgs94t-72292-9clnd-master-0           0/1     Completed           0          36s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            0/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Terminating         0          11m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Pending             0          0s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:1/3            0          1s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     Init:2/3            0          2s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  0/4     PodInitializing     0          3s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          4s
etcd-guard-ci-ln-qkgs94t-72292-9clnd-master-0            1/1     Running             0          26m
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  3/4     Running             0          20s
etcd-ci-ln-qkgs94t-72292-9clnd-master-0                  4/4     Running             0          20s
```

- Enter the following command to review to the values:oc describe -n openshift-etcd pod/<ETCD_PODNAME> | grep -e HEARTBEAT_INTERVAL -e ELECTION_TIMEOUT$oc describe-nopenshift-etcd pod/<ETCD_PODNAME>|grep-eHEARTBEAT_INTERVAL-eELECTION_TIMEOUTCopy to ClipboardCopied!Toggle word wrapToggle overflowThese values might not have changed from the default.

Enter the following command to review to the values:

These values might not have changed from the default.

### 2.4.7. Increasing the database size for etcdCopy linkLink copied to clipboard!

You can set the disk quota in gibibytes (GiB) for each etcd instance. If you set a disk quota for your etcd instance, you can specify integer values from 8 to 32. The default value is 8. You can specify only increasing values.

You might want to increase the disk quota if you encounter alow spacealert. This alert indicates that the cluster is too large to fit in etcd despite automatic compaction and defragmentation. If you see this alert, you need to increase the disk quota immediately because after etcd runs out of space, writes fail.

Another scenario where you might want to increase the disk quota is if you encounter anexcessive database growthalert. This alert is a warning that the database might grow too large in the next four hours. In this scenario, consider increasing the disk quota so that you do not eventually encounter alow spacealert and possible write fails.

If you increase the disk quota, the disk space that you specify is not immediately reserved. Instead, etcd can grow to that size if needed. Ensure that etcd is running on a dedicated disk that is larger than the value that you specify for the disk quota.

For large etcd databases, the control plane nodes must have additional memory and storage. Because you must account for the API server cache, the minimum memory required is at least three times the configured size of the etcd database.

Increasing the database size for etcd is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

#### 2.4.7.1. Changing the etcd database sizeCopy linkLink copied to clipboard!

To change the database size for etcd, complete the following steps.

Procedure

- Check the current value of the disk quota for each etcd instance by entering the following command:oc describe etcd/cluster | grep "Backend Quota"$oc describe etcd/cluster|grep"Backend Quota"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputBackend Quota Gi B: <value>Backend Quota Gi B: <value>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check the current value of the disk quota for each etcd instance by entering the following command:

Example output

- Change the value of the disk quota by entering the following command:oc patch etcd/cluster --type=merge -p '{"spec": {"backendQuotaGiB": <value>}}'$oc patch etcd/cluster--type=merge-p'{"spec": {"backendQuotaGiB": <value>}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputetcd.operator.openshift.io/cluster patchedetcd.operator.openshift.io/cluster patchedCopy to ClipboardCopied!Toggle word wrapToggle overflow

Change the value of the disk quota by entering the following command:

Example output

Verification

- Verify that the new value for the disk quota is set by entering the following command:oc describe etcd/cluster | grep "Backend Quota"$oc describe etcd/cluster|grep"Backend Quota"Copy to ClipboardCopied!Toggle word wrapToggle overflowThe etcd Operator automatically rolls out the etcd instances with the new values.

Verify that the new value for the disk quota is set by entering the following command:

The etcd Operator automatically rolls out the etcd instances with the new values.

- Verify that the etcd pods are up and running by entering the following command:oc get pods -n openshift-etcd$oc get pods-nopenshift-etcdCopy to ClipboardCopied!Toggle word wrapToggle overflowThe following output shows the expected entries.Example outputNAME                                                   READY   STATUS      RESTARTS   AGE
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-0                4/4     Running     0          39m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-1                4/4     Running     0          37m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-2                4/4     Running     0          41m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-0          1/1     Running     0          51m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-1          1/1     Running     0          49m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-2          1/1     Running     0          54m
installer-5-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          51m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          46m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          44m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          49m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          40m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          38m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          42m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          43m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          42mNAME                                                   READY   STATUS      RESTARTS   AGE
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-0                4/4     Running     0          39m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-1                4/4     Running     0          37m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-2                4/4     Running     0          41m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-0          1/1     Running     0          51m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-1          1/1     Running     0          49m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-2          1/1     Running     0          54m
installer-5-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          51m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          46m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          44m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          49m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          40m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          38m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          42m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          43m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          42mCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the etcd pods are up and running by entering the following command:

The following output shows the expected entries.

Example output

```
NAME                                                   READY   STATUS      RESTARTS   AGE
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-0                4/4     Running     0          39m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-1                4/4     Running     0          37m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-2                4/4     Running     0          41m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-0          1/1     Running     0          51m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-1          1/1     Running     0          49m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-2          1/1     Running     0          54m
installer-5-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          51m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          46m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          44m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          49m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          40m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          38m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          42m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          43m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          42m
```

```
NAME                                                   READY   STATUS      RESTARTS   AGE
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-0                4/4     Running     0          39m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-1                4/4     Running     0          37m
etcd-ci-ln-b6kfsw2-72292-mzwbq-master-2                4/4     Running     0          41m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-0          1/1     Running     0          51m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-1          1/1     Running     0          49m
etcd-guard-ci-ln-b6kfsw2-72292-mzwbq-master-2          1/1     Running     0          54m
installer-5-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          51m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          46m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          44m
installer-7-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          49m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-0         0/1     Completed   0          40m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-1         0/1     Completed   0          38m
installer-8-ci-ln-b6kfsw2-72292-mzwbq-master-2         0/1     Completed   0          42m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          43m
revision-pruner-7-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          43m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-0   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-1   0/1     Completed   0          42m
revision-pruner-8-ci-ln-b6kfsw2-72292-mzwbq-master-2   0/1     Completed   0          42m
```

- Verify that the disk quota value is updated for the etcd pod by entering the following command:oc describe -n openshift-etcd pod/<etcd_podname> | grep "ETCD_QUOTA_BACKEND_BYTES"$oc describe-nopenshift-etcd pod/<etcd_podname>|grep"ETCD_QUOTA_BACKEND_BYTES"Copy to ClipboardCopied!Toggle word wrapToggle overflowThe value might not have changed from the default value of8.Example outputETCD_QUOTA_BACKEND_BYTES:                               8589934592ETCD_QUOTA_BACKEND_BYTES:                               8589934592Copy to ClipboardCopied!Toggle word wrapToggle overflowWhile the value that you set is an integer in GiB, the value shown in the output is converted to bytes.

Verify that the disk quota value is updated for the etcd pod by entering the following command:

The value might not have changed from the default value of8.

Example output

While the value that you set is an integer in GiB, the value shown in the output is converted to bytes.

#### 2.4.7.2. TroubleshootingCopy linkLink copied to clipboard!

If you encounter issues when you try to increase the database size for etcd, the following troubleshooting steps might help.

##### 2.4.7.2.1. Value is too smallCopy linkLink copied to clipboard!

If the value that you specify is less than8, you see the following error message:

Example error message

```
The Etcd "cluster" is invalid:
* spec.backendQuotaGiB: Invalid value: 5: spec.backendQuotaGiB in body should be greater than or equal to 8
* spec.backendQuotaGiB: Invalid value: "integer": etcd backendQuotaGiB may not be decreased
```

```
The Etcd "cluster" is invalid:
* spec.backendQuotaGiB: Invalid value: 5: spec.backendQuotaGiB in body should be greater than or equal to 8
* spec.backendQuotaGiB: Invalid value: "integer": etcd backendQuotaGiB may not be decreased
```

To resolve this issue, specify an integer between8and32.

##### 2.4.7.2.2. Value is too largeCopy linkLink copied to clipboard!

If the value that you specify is greater than32, you see the following error message:

Example error message

To resolve this issue, specify an integer between8and32.

##### 2.4.7.2.3. Value is decreasingCopy linkLink copied to clipboard!

If the value is set to a valid value between8and32, you cannot decrease the value. Otherwise, you see an error message.

- Check to see the current value by entering the following command:oc describe etcd/cluster | grep "Backend Quota"$oc describe etcd/cluster|grep"Backend Quota"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputBackend Quota Gi B: 10Backend Quota Gi B: 10Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check to see the current value by entering the following command:

Example output

- Decrease the disk quota value by entering the following command:oc patch etcd/cluster --type=merge -p '{"spec": {"backendQuotaGiB": 8}}'$oc patch etcd/cluster--type=merge-p'{"spec": {"backendQuotaGiB": 8}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample error messageThe Etcd "cluster" is invalid: spec.backendQuotaGiB: Invalid value: "integer": etcd backendQuotaGiB may not be decreasedThe Etcd "cluster" is invalid: spec.backendQuotaGiB: Invalid value: "integer": etcd backendQuotaGiB may not be decreasedCopy to ClipboardCopied!Toggle word wrapToggle overflow

Decrease the disk quota value by entering the following command:

Example error message

- To resolve this issue, specify an integer greater than10.
