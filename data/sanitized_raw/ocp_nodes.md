<!-- source: ocp_nodes.md -->

# Nodes

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/nodes/working-with-nodes
---

# Chapter 6. Working with nodes

## 6.1. Viewing and listing the nodes in your OpenShift Container Platform clusterCopy linkLink copied to clipboard!

You can list all the nodes in your cluster to obtain information such as status, age, memory usage, and details about the nodes.

When you perform node management operations, the CLI interacts with node objects that are representations of actual node hosts. The master uses the information from node objects to validate nodes with health checks.

### 6.1.1. About listing all the nodes in a clusterCopy linkLink copied to clipboard!

You can get detailed information about the nodes in the cluster, which can help you understand the state of the nodes in your cluster.

- The following command lists all nodes:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowThe following example is a cluster with healthy nodes:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                   STATUS    ROLES     AGE       VERSION
master.example.com     Ready     master    7h        v1.30.3
node1.example.com      Ready     worker    7h        v1.30.3
node2.example.com      Ready     worker    7h        v1.30.3NAME                   STATUS    ROLES     AGE       VERSION
master.example.com     Ready     master    7h        v1.30.3
node1.example.com      Ready     worker    7h        v1.30.3
node2.example.com      Ready     worker    7h        v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflowThe following example is a cluster with one unhealthy node:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                   STATUS                      ROLES     AGE       VERSION
master.example.com     Ready                       master    7h        v1.30.3
node1.example.com      NotReady,SchedulingDisabled worker    7h        v1.30.3
node2.example.com      Ready                       worker    7h        v1.30.3NAME                   STATUS                      ROLES     AGE       VERSION
master.example.com     Ready                       master    7h        v1.30.3
node1.example.com      NotReady,SchedulingDisabled worker    7h        v1.30.3
node2.example.com      Ready                       worker    7h        v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflowThe conditions that trigger aNotReadystatus are shown later in this section.

The following command lists all nodes:

The following example is a cluster with healthy nodes:

Example output

```
NAME                   STATUS    ROLES     AGE       VERSION
master.example.com     Ready     master    7h        v1.30.3
node1.example.com      Ready     worker    7h        v1.30.3
node2.example.com      Ready     worker    7h        v1.30.3
```

```
NAME                   STATUS    ROLES     AGE       VERSION
master.example.com     Ready     master    7h        v1.30.3
node1.example.com      Ready     worker    7h        v1.30.3
node2.example.com      Ready     worker    7h        v1.30.3
```

The following example is a cluster with one unhealthy node:

Example output

```
NAME                   STATUS                      ROLES     AGE       VERSION
master.example.com     Ready                       master    7h        v1.30.3
node1.example.com      NotReady,SchedulingDisabled worker    7h        v1.30.3
node2.example.com      Ready                       worker    7h        v1.30.3
```

```
NAME                   STATUS                      ROLES     AGE       VERSION
master.example.com     Ready                       master    7h        v1.30.3
node1.example.com      NotReady,SchedulingDisabled worker    7h        v1.30.3
node2.example.com      Ready                       worker    7h        v1.30.3
```

The conditions that trigger aNotReadystatus are shown later in this section.

- The-o wideoption provides additional information on nodes.oc get nodes -o wide$oc get nodes-owideCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                STATUS   ROLES    AGE    VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                                                       KERNEL-VERSION                 CONTAINER-RUNTIME
master.example.com  Ready    master   171m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node1.example.com   Ready    worker   72m    v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node2.example.com   Ready    worker   164m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-devNAME                STATUS   ROLES    AGE    VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                                                       KERNEL-VERSION                 CONTAINER-RUNTIME
master.example.com  Ready    master   171m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node1.example.com   Ready    worker   72m    v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node2.example.com   Ready    worker   164m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-devCopy to ClipboardCopied!Toggle word wrapToggle overflow

The-o wideoption provides additional information on nodes.

Example output

```
NAME                STATUS   ROLES    AGE    VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                                                       KERNEL-VERSION                 CONTAINER-RUNTIME
master.example.com  Ready    master   171m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node1.example.com   Ready    worker   72m    v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node2.example.com   Ready    worker   164m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
```

```
NAME                STATUS   ROLES    AGE    VERSION   INTERNAL-IP    EXTERNAL-IP   OS-IMAGE                                                       KERNEL-VERSION                 CONTAINER-RUNTIME
master.example.com  Ready    master   171m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node1.example.com   Ready    worker   72m    v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
node2.example.com   Ready    worker   164m   v1.30.3   [REDACTED_PRIVATE_IP]   <none>        Red Hat Enterprise Linux CoreOS 48.83.202103210901-0 (Ootpa)   4.18.0-240.15.1.el8_3.x86_64   cri-o://1.30.3-30.rhaos4.10.gitf2f339d.el8-dev
```

- The following command lists information about a single node:oc get node <node>$oc getnode<node>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc get node node1.example.com$oc getnodenode1.example.comCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                   STATUS    ROLES     AGE       VERSION
node1.example.com      Ready     worker    7h        v1.30.3NAME                   STATUS    ROLES     AGE       VERSION
node1.example.com      Ready     worker    7h        v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflow

The following command lists information about a single node:

For example:

Example output

```
NAME                   STATUS    ROLES     AGE       VERSION
node1.example.com      Ready     worker    7h        v1.30.3
```

```
NAME                   STATUS    ROLES     AGE       VERSION
node1.example.com      Ready     worker    7h        v1.30.3
```

- The following command provides more detailed information about a specific node, including the reason for the current condition:oc describe node <node>$oc describenode<node>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc describe node node1.example.com$oc describenodenode1.example.comCopy to ClipboardCopied!Toggle word wrapToggle overflowThe following example contains some values that are specific to OpenShift Container Platform on AWS.Example outputName:               node1.example.com
Roles:              worker
Labels:             kubernetes.io/os=linux
                    kubernetes.io/hostname=ip-10-0-131-14
                    kubernetes.io/arch=amd64
                    node-role.kubernetes.io/worker=
                    node.kubernetes.io/instance-type=m4.large
                    node.openshift.io/os_id=rhcos
                    node.openshift.io/os_version=4.5
                    region=east
                    topology.kubernetes.io/region=us-east-1
                    topology.kubernetes.io/zone=us-east-1a
Annotations:        cluster.k8s.io/machine: openshift-machine-api/ahardin-worker-us-east-2a-q5dzc
                    machineconfiguration.openshift.io/currentConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/desiredConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/state: Done
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 13 Feb 2019 11:05:57 -0500
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  OutOfDisk        False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientDisk     kubelet has sufficient disk space available
  MemoryPressure   False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:07:09 -0500   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:   [REDACTED_PRIVATE_IP]
  InternalDNS:  ip-10-0-140-16.us-east-2.compute.internal
  Hostname:     ip-10-0-140-16.us-east-2.compute.internal
Capacity:
 attachable-volumes-aws-ebs:  39
 cpu:                         2
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      8172516Ki
 pods:                        250
Allocatable:
 attachable-volumes-aws-ebs:  39
 cpu:                         1500m
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      7558116Ki
 pods:                        250
System Info:
 Machine ID:                              63787c9534c24fde9a0cde35c13f1f66
 System UUID:                             EC22BF97-A006-4A58-6AF8-0A38DEEA122A
 Boot ID:                                 f24ad37d-2594-46b4-8830-7f7555918325
 Kernel Version:                          3.10.0-957.5.1.el7.x86_64
 OS Image:                                Red Hat Enterprise Linux CoreOS 410.8.20190520.0 (Ootpa)
 Operating System:                        linux
 Architecture:                            amd64
 Container Runtime Version:               cri-o://1.30.3-0.6.dev.rhaos4.3.git9ad059b.el8-rc2
 Kubelet Version:                         v1.30.3
 Kube-Proxy Version:                      v1.30.3
PodCIDR:                                  [REDACTED_PRIVATE_IP]/24
ProviderID:                               aws:///us-east-2a/i-04e87b31dc6b3e171
Non-terminated Pods:                      (12 in total)
  Namespace                               Name                                   CPU Requests  CPU Limits  Memory Requests  Memory Limits
  ---------                               ----                                   ------------  ----------  ---------------  -------------
  openshift-cluster-node-tuning-operator  tuned-hdl5q                            0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-dns                           dns-default-l69zr                      0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-image-registry                node-ca-9hmcg                          0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ingress                       router-default-76455c45c-c5ptv         0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-machine-config-operator       machine-config-daemon-cvqw9            20m (1%)      0 (0%)      50Mi (0%)        0 (0%)
  openshift-marketplace                   community-operators-f67fh              0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-monitoring                    alertmanager-main-0                    50m (3%)      50m (3%)    210Mi (2%)       10Mi (0%)
  openshift-monitoring                    node-exporter-l7q8d                    10m (0%)      20m (1%)    20Mi (0%)        40Mi (0%)
  openshift-monitoring                    prometheus-adapter-75d769c874-hvb85    0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-multus                        multus-kw8w5                           0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ovn-kubernetes                          ovnkube-node-t4dsn                              80m (0%)     0 (0%)      1630Mi (0%)       0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource                    Requests     Limits
  --------                    --------     ------
  cpu                         380m (25%)   270m (18%)
  memory                      880Mi (11%)  250Mi (3%)
  attachable-volumes-aws-ebs  0            0
Events:
  Type     Reason                   Age                From                      Message
  ----     ------                   ----               ----                      -------
  Normal   NodeHasSufficientPID     6d (x5 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   NodeAllocatableEnforced  6d                 kubelet, m01.example.com  Updated Node Allocatable limit across pods
  Normal   NodeHasSufficientMemory  6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientDisk    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientDisk
  Normal   NodeHasSufficientPID     6d                 kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   Starting                 6d                 kubelet, m01.example.com  Starting kubelet.
#...Name:               node1.example.com
Roles:              worker
Labels:             kubernetes.io/os=linux
                    kubernetes.io/hostname=ip-10-0-131-14
                    kubernetes.io/arch=amd64
                    node-role.kubernetes.io/worker=
                    node.kubernetes.io/instance-type=m4.large
                    node.openshift.io/os_id=rhcos
                    node.openshift.io/os_version=4.5
                    region=east
                    topology.kubernetes.io/region=us-east-1
                    topology.kubernetes.io/zone=us-east-1a
Annotations:        cluster.k8s.io/machine: openshift-machine-api/ahardin-worker-us-east-2a-q5dzc
                    machineconfiguration.openshift.io/currentConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/desiredConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/state: Done
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 13 Feb 2019 11:05:57 -0500
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  OutOfDisk        False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientDisk     kubelet has sufficient disk space available
  MemoryPressure   False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:07:09 -0500   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:   [REDACTED_PRIVATE_IP]
  InternalDNS:  ip-10-0-140-16.us-east-2.compute.internal
  Hostname:     ip-10-0-140-16.us-east-2.compute.internal
Capacity:
 attachable-volumes-aws-ebs:  39
 cpu:                         2
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      8172516Ki
 pods:                        250
Allocatable:
 attachable-volumes-aws-ebs:  39
 cpu:                         1500m
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      7558116Ki
 pods:                        250
System Info:
 Machine ID:                              63787c9534c24fde9a0cde35c13f1f66
 System UUID:                             EC22BF97-A006-4A58-6AF8-0A38DEEA122A
 Boot ID:                                 f24ad37d-2594-46b4-8830-7f7555918325
 Kernel Version:                          3.10.0-957.5.1.el7.x86_64
 OS Image:                                Red Hat Enterprise Linux CoreOS 410.8.20190520.0 (Ootpa)
 Operating System:                        linux
 Architecture:                            amd64
 Container Runtime Version:               cri-o://1.30.3-0.6.dev.rhaos4.3.git9ad059b.el8-rc2
 Kubelet Version:                         v1.30.3
 Kube-Proxy Version:                      v1.30.3
PodCIDR:                                  [REDACTED_PRIVATE_IP]/24
ProviderID:                               aws:///us-east-2a/i-04e87b31dc6b3e171
Non-terminated Pods:                      (12 in total)
  Namespace                               Name                                   CPU Requests  CPU Limits  Memory Requests  Memory Limits
  ---------                               ----                                   ------------  ----------  ---------------  -------------
  openshift-cluster-node-tuning-operator  tuned-hdl5q                            0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-dns                           dns-default-l69zr                      0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-image-registry                node-ca-9hmcg                          0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ingress                       router-default-76455c45c-c5ptv         0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-machine-config-operator       machine-config-daemon-cvqw9            20m (1%)      0 (0%)      50Mi (0%)        0 (0%)
  openshift-marketplace                   community-operators-f67fh              0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-monitoring                    alertmanager-main-0                    50m (3%)      50m (3%)    210Mi (2%)       10Mi (0%)
  openshift-monitoring                    node-exporter-l7q8d                    10m (0%)      20m (1%)    20Mi (0%)        40Mi (0%)
  openshift-monitoring                    prometheus-adapter-75d769c874-hvb85    0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-multus                        multus-kw8w5                           0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ovn-kubernetes                          ovnkube-node-t4dsn                              80m (0%)     0 (0%)      1630Mi (0%)       0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource                    Requests     Limits
  --------                    --------     ------
  cpu                         380m (25%)   270m (18%)
  memory                      880Mi (11%)  250Mi (3%)
  attachable-volumes-aws-ebs  0            0
Events:
  Type     Reason                   Age                From                      Message
  ----     ------                   ----               ----                      -------
  Normal   NodeHasSufficientPID     6d (x5 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   NodeAllocatableEnforced  6d                 kubelet, m01.example.com  Updated Node Allocatable limit across pods
  Normal   NodeHasSufficientMemory  6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientDisk    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientDisk
  Normal   NodeHasSufficientPID     6d                 kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   Starting                 6d                 kubelet, m01.example.com  Starting kubelet.
#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:NamesSpecifies the name of the node.RolesSpecifies the role of the node, eithermasterorworker.LabelsSpecifies the labels applied to the node.AnnotationsSpecifies the annotations applied to the node.TaintsSpecifies the taints applied to the node.ConditionsSpecifies the node conditions and status. Theconditionsstanza lists theReady,PIDPressure,MemoryPressure,DiskPressureandOutOfDiskstatus. These condition are described later in this section.AddressesSpecifies the IP address and hostname of the node.CapacitySpecifies the pod resources and allocatable resources.InformationSpecifies information about the node host.Non-terminated PodsSpecifies the pods on the node.EventsSpecifies the events reported by the node.The control plane label is not automatically added to newly created or updated master nodes. If you want to use the control plane label for your nodes, you can manually configure the label. For more information, seeUnderstanding how to update labels on nodesin theAdditional resourcessection.

The following command provides more detailed information about a specific node, including the reason for the current condition:

For example:

The following example contains some values that are specific to OpenShift Container Platform on AWS.

Example output

```
Name:               node1.example.com
Roles:              worker
Labels:             kubernetes.io/os=linux
                    kubernetes.io/hostname=ip-10-0-131-14
                    kubernetes.io/arch=amd64
                    node-role.kubernetes.io/worker=
                    node.kubernetes.io/instance-type=m4.large
                    node.openshift.io/os_id=rhcos
                    node.openshift.io/os_version=4.5
                    region=east
                    topology.kubernetes.io/region=us-east-1
                    topology.kubernetes.io/zone=us-east-1a
Annotations:        cluster.k8s.io/machine: openshift-machine-api/ahardin-worker-us-east-2a-q5dzc
                    machineconfiguration.openshift.io/currentConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/desiredConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/state: Done
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 13 Feb 2019 11:05:57 -0500
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  OutOfDisk        False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientDisk     kubelet has sufficient disk space available
  MemoryPressure   False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:07:09 -0500   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:   [REDACTED_PRIVATE_IP]
  InternalDNS:  ip-10-0-140-16.us-east-2.compute.internal
  Hostname:     ip-10-0-140-16.us-east-2.compute.internal
Capacity:
 attachable-volumes-aws-ebs:  39
 cpu:                         2
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      8172516Ki
 pods:                        250
Allocatable:
 attachable-volumes-aws-ebs:  39
 cpu:                         1500m
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      7558116Ki
 pods:                        250
System Info:
 Machine ID:                              63787c9534c24fde9a0cde35c13f1f66
 System UUID:                             EC22BF97-A006-4A58-6AF8-0A38DEEA122A
 Boot ID:                                 f24ad37d-2594-46b4-8830-7f7555918325
 Kernel Version:                          3.10.0-957.5.1.el7.x86_64
 OS Image:                                Red Hat Enterprise Linux CoreOS 410.8.20190520.0 (Ootpa)
 Operating System:                        linux
 Architecture:                            amd64
 Container Runtime Version:               cri-o://1.30.3-0.6.dev.rhaos4.3.git9ad059b.el8-rc2
 Kubelet Version:                         v1.30.3
 Kube-Proxy Version:                      v1.30.3
PodCIDR:                                  [REDACTED_PRIVATE_IP]/24
ProviderID:                               aws:///us-east-2a/i-04e87b31dc6b3e171
Non-terminated Pods:                      (12 in total)
  Namespace                               Name                                   CPU Requests  CPU Limits  Memory Requests  Memory Limits
  ---------                               ----                                   ------------  ----------  ---------------  -------------
  openshift-cluster-node-tuning-operator  tuned-hdl5q                            0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-dns                           dns-default-l69zr                      0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-image-registry                node-ca-9hmcg                          0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ingress                       router-default-76455c45c-c5ptv         0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-machine-config-operator       machine-config-daemon-cvqw9            20m (1%)      0 (0%)      50Mi (0%)        0 (0%)
  openshift-marketplace                   community-operators-f67fh              0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-monitoring                    alertmanager-main-0                    50m (3%)      50m (3%)    210Mi (2%)       10Mi (0%)
  openshift-monitoring                    node-exporter-l7q8d                    10m (0%)      20m (1%)    20Mi (0%)        40Mi (0%)
  openshift-monitoring                    prometheus-adapter-75d769c874-hvb85    0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-multus                        multus-kw8w5                           0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ovn-kubernetes                          ovnkube-node-t4dsn                              80m (0%)     0 (0%)      1630Mi (0%)       0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource                    Requests     Limits
  --------                    --------     ------
  cpu                         380m (25%)   270m (18%)
  memory                      880Mi (11%)  250Mi (3%)
  attachable-volumes-aws-ebs  0            0
Events:
  Type     Reason                   Age                From                      Message
  ----     ------                   ----               ----                      -------
  Normal   NodeHasSufficientPID     6d (x5 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   NodeAllocatableEnforced  6d                 kubelet, m01.example.com  Updated Node Allocatable limit across pods
  Normal   NodeHasSufficientMemory  6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientDisk    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientDisk
  Normal   NodeHasSufficientPID     6d                 kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   Starting                 6d                 kubelet, m01.example.com  Starting kubelet.
#...
```

```
Name:               node1.example.com
Roles:              worker
Labels:             kubernetes.io/os=linux
                    kubernetes.io/hostname=ip-10-0-131-14
                    kubernetes.io/arch=amd64
                    node-role.kubernetes.io/worker=
                    node.kubernetes.io/instance-type=m4.large
                    node.openshift.io/os_id=rhcos
                    node.openshift.io/os_version=4.5
                    region=east
                    topology.kubernetes.io/region=us-east-1
                    topology.kubernetes.io/zone=us-east-1a
Annotations:        cluster.k8s.io/machine: openshift-machine-api/ahardin-worker-us-east-2a-q5dzc
                    machineconfiguration.openshift.io/currentConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/desiredConfig: worker-309c228e8b3a92e2235edd544c62fea8
                    machineconfiguration.openshift.io/state: Done
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 13 Feb 2019 11:05:57 -0500
Taints:             <none>
Unschedulable:      false
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  OutOfDisk        False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientDisk     kubelet has sufficient disk space available
  MemoryPressure   False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:05:57 -0500   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Wed, 13 Feb 2019 15:09:42 -0500   Wed, 13 Feb 2019 11:07:09 -0500   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:   [REDACTED_PRIVATE_IP]
  InternalDNS:  ip-10-0-140-16.us-east-2.compute.internal
  Hostname:     ip-10-0-140-16.us-east-2.compute.internal
Capacity:
 attachable-volumes-aws-ebs:  39
 cpu:                         2
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      8172516Ki
 pods:                        250
Allocatable:
 attachable-volumes-aws-ebs:  39
 cpu:                         1500m
 hugepages-1Gi:               0
 hugepages-2Mi:               0
 memory:                      7558116Ki
 pods:                        250
System Info:
 Machine ID:                              63787c9534c24fde9a0cde35c13f1f66
 System UUID:                             EC22BF97-A006-4A58-6AF8-0A38DEEA122A
 Boot ID:                                 f24ad37d-2594-46b4-8830-7f7555918325
 Kernel Version:                          3.10.0-957.5.1.el7.x86_64
 OS Image:                                Red Hat Enterprise Linux CoreOS 410.8.20190520.0 (Ootpa)
 Operating System:                        linux
 Architecture:                            amd64
 Container Runtime Version:               cri-o://1.30.3-0.6.dev.rhaos4.3.git9ad059b.el8-rc2
 Kubelet Version:                         v1.30.3
 Kube-Proxy Version:                      v1.30.3
PodCIDR:                                  [REDACTED_PRIVATE_IP]/24
ProviderID:                               aws:///us-east-2a/i-04e87b31dc6b3e171
Non-terminated Pods:                      (12 in total)
  Namespace                               Name                                   CPU Requests  CPU Limits  Memory Requests  Memory Limits
  ---------                               ----                                   ------------  ----------  ---------------  -------------
  openshift-cluster-node-tuning-operator  tuned-hdl5q                            0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-dns                           dns-default-l69zr                      0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-image-registry                node-ca-9hmcg                          0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ingress                       router-default-76455c45c-c5ptv         0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-machine-config-operator       machine-config-daemon-cvqw9            20m (1%)      0 (0%)      50Mi (0%)        0 (0%)
  openshift-marketplace                   community-operators-f67fh              0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-monitoring                    alertmanager-main-0                    50m (3%)      50m (3%)    210Mi (2%)       10Mi (0%)
  openshift-monitoring                    node-exporter-l7q8d                    10m (0%)      20m (1%)    20Mi (0%)        40Mi (0%)
  openshift-monitoring                    prometheus-adapter-75d769c874-hvb85    0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-multus                        multus-kw8w5                           0 (0%)        0 (0%)      0 (0%)           0 (0%)
  openshift-ovn-kubernetes                          ovnkube-node-t4dsn                              80m (0%)     0 (0%)      1630Mi (0%)       0 (0%)
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource                    Requests     Limits
  --------                    --------     ------
  cpu                         380m (25%)   270m (18%)
  memory                      880Mi (11%)  250Mi (3%)
  attachable-volumes-aws-ebs  0            0
Events:
  Type     Reason                   Age                From                      Message
  ----     ------                   ----               ----                      -------
  Normal   NodeHasSufficientPID     6d (x5 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   NodeAllocatableEnforced  6d                 kubelet, m01.example.com  Updated Node Allocatable limit across pods
  Normal   NodeHasSufficientMemory  6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientMemory
  Normal   NodeHasNoDiskPressure    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasNoDiskPressure
  Normal   NodeHasSufficientDisk    6d (x6 over 6d)    kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientDisk
  Normal   NodeHasSufficientPID     6d                 kubelet, m01.example.com  Node m01.example.com status is now: NodeHasSufficientPID
  Normal   Starting                 6d                 kubelet, m01.example.com  Starting kubelet.
#...
```

where:

**Names**
  Specifies the name of the node.

**Roles**
  Specifies the role of the node, eithermasterorworker.

**Labels**
  Specifies the labels applied to the node.

**Annotations**
  Specifies the annotations applied to the node.

**Taints**
  Specifies the taints applied to the node.

**Conditions**
  Specifies the node conditions and status. Theconditionsstanza lists theReady,PIDPressure,MemoryPressure,DiskPressureandOutOfDiskstatus. These condition are described later in this section.

**Addresses**
  Specifies the IP address and hostname of the node.

**Capacity**
  Specifies the pod resources and allocatable resources.

**Information**
  Specifies information about the node host.

**Non-terminated Pods**
  Specifies the pods on the node.

**Events**
  Specifies the events reported by the node.

The control plane label is not automatically added to newly created or updated master nodes. If you want to use the control plane label for your nodes, you can manually configure the label. For more information, seeUnderstanding how to update labels on nodesin theAdditional resourcessection.

Among the information shown for nodes, the following node conditions appear in the output of the commands shown in this section:

| Condition | Description |
| --- | --- |
| Ready | Iftrue, the node is healthy and ready to accept pods. Iffalse, the node is not healthy and is not ac |
| DiskPressure | Iftrue, the disk capacity is low. |
| MemoryPressure | Iftrue, the node memory is low. |
| PIDPressure | Iftrue, there are too many processes on the node. |
| OutOfDisk | Iftrue, the node has insufficient free space on the node for adding new pods. |
| NetworkUnavailable | Iftrue, the network for the node is not correctly configured. |
| NotReady | Iftrue, one of the underlying components, such as the container runtime or network, is experiencing  |
| SchedulingDisabled | Pods cannot be scheduled for placement on the node. |

Ready

Iftrue, the node is healthy and ready to accept pods. Iffalse, the node is not healthy and is not accepting pods. Ifunknown, the node controller has not received a heartbeat from the node for thenode-monitor-grace-period(the default is 40 seconds).

DiskPressure

Iftrue, the disk capacity is low.

MemoryPressure

Iftrue, the node memory is low.

PIDPressure

Iftrue, there are too many processes on the node.

OutOfDisk

Iftrue, the node has insufficient free space on the node for adding new pods.

NetworkUnavailable

Iftrue, the network for the node is not correctly configured.

NotReady

Iftrue, one of the underlying components, such as the container runtime or network, is experiencing issues or is not yet configured.

SchedulingDisabled

Pods cannot be scheduled for placement on the node.

### 6.1.2. Listing pods on a node in your clusterCopy linkLink copied to clipboard!

You can list all of the pods on a node by using theoc get podscommand along with specific flags. This command shows the number of pods on that node, the state of the pods, number of pod restarts, and the age of the pods.

Procedure

- To list all or selected pods on selected nodes:oc get pod --selector=<nodeSelector>$oc get pod--selector=<nodeSelector>Copy to ClipboardCopied!Toggle word wrapToggle overflowoc get pod --selector=kubernetes.io/os$oc get pod--selector=kubernetes.io/osCopy to ClipboardCopied!Toggle word wrapToggle overflowOr:oc get pod -l=<nodeSelector>$oc get pod-l=<nodeSelector>Copy to ClipboardCopied!Toggle word wrapToggle overflowoc get pod -l kubernetes.io/os=linux$oc get pod-lkubernetes.io/os=linuxCopy to ClipboardCopied!Toggle word wrapToggle overflow

To list all or selected pods on selected nodes:

Or:

- To list all pods on a specific node, including terminated pods:oc get pod --all-namespaces --field-selector=spec.nodeName=<nodename>$oc get pod --all-namespaces --field-selector=spec.nodeName=<nodename>Copy to ClipboardCopied!Toggle word wrapToggle overflow

To list all pods on a specific node, including terminated pods:

### 6.1.3. Viewing memory and CPU usage statistics on your nodesCopy linkLink copied to clipboard!

You can display usage statistics about nodes, including CPU, memory, and storage consumption. These statistics can help you ensure your cluster is running efficiently.

Prerequisites

- You must havecluster-readerpermission to view the usage statistics.
- Metrics must be installed to view the usage statistics.

Procedure

- To view the usage statistics:oc adm top nodes$oc admtopnodesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                   CPU(cores)   CPU%      MEMORY(bytes)   MEMORY%
ip-10-0-12-143.ec2.compute.internal    1503m        100%      4533Mi          61%
ip-10-0-132-16.ec2.compute.internal    76m          5%        1391Mi          18%
ip-10-0-140-137.ec2.compute.internal   398m         26%       2473Mi          33%
ip-10-0-142-44.ec2.compute.internal    656m         43%       6119Mi          82%
ip-10-0-146-165.ec2.compute.internal   188m         12%       3367Mi          45%
ip-10-0-19-62.ec2.compute.internal     896m         59%       5754Mi          77%
ip-10-0-44-193.ec2.compute.internal    632m         42%       5349Mi          72%NAME                                   CPU(cores)   CPU%      MEMORY(bytes)   MEMORY%
ip-10-0-12-143.ec2.compute.internal    1503m        100%      4533Mi          61%
ip-10-0-132-16.ec2.compute.internal    76m          5%        1391Mi          18%
ip-10-0-140-137.ec2.compute.internal   398m         26%       2473Mi          33%
ip-10-0-142-44.ec2.compute.internal    656m         43%       6119Mi          82%
ip-10-0-146-165.ec2.compute.internal   188m         12%       3367Mi          45%
ip-10-0-19-62.ec2.compute.internal     896m         59%       5754Mi          77%
ip-10-0-44-193.ec2.compute.internal    632m         42%       5349Mi          72%Copy to ClipboardCopied!Toggle word wrapToggle overflow

To view the usage statistics:

Example output

```
NAME                                   CPU(cores)   CPU%      MEMORY(bytes)   MEMORY%
ip-10-0-12-143.ec2.compute.internal    1503m        100%      4533Mi          61%
ip-10-0-132-16.ec2.compute.internal    76m          5%        1391Mi          18%
ip-10-0-140-137.ec2.compute.internal   398m         26%       2473Mi          33%
ip-10-0-142-44.ec2.compute.internal    656m         43%       6119Mi          82%
ip-10-0-146-165.ec2.compute.internal   188m         12%       3367Mi          45%
ip-10-0-19-62.ec2.compute.internal     896m         59%       5754Mi          77%
ip-10-0-44-193.ec2.compute.internal    632m         42%       5349Mi          72%
```

```
NAME                                   CPU(cores)   CPU%      MEMORY(bytes)   MEMORY%
ip-10-0-12-143.ec2.compute.internal    1503m        100%      4533Mi          61%
ip-10-0-132-16.ec2.compute.internal    76m          5%        1391Mi          18%
ip-10-0-140-137.ec2.compute.internal   398m         26%       2473Mi          33%
ip-10-0-142-44.ec2.compute.internal    656m         43%       6119Mi          82%
ip-10-0-146-165.ec2.compute.internal   188m         12%       3367Mi          45%
ip-10-0-19-62.ec2.compute.internal     896m         59%       5754Mi          77%
ip-10-0-44-193.ec2.compute.internal    632m         42%       5349Mi          72%
```

- To view the usage statistics for nodes with labels:oc adm top node --selector=''$oc admtopnode--selector=''Copy to ClipboardCopied!Toggle word wrapToggle overflowYou must choose the selector (label query) to filter on. Supports=,==, and!=.

To view the usage statistics for nodes with labels:

You must choose the selector (label query) to filter on. Supports=,==, and!=.

## 6.2. Working with nodesCopy linkLink copied to clipboard!

As an administrator, you can perform several tasks to make your clusters more efficient.

### 6.2.1. Evacuating pods on nodesCopy linkLink copied to clipboard!

You can remove, or evacuate, pods from a given node or nodes. Evacuating pods allows you to migrate all or selected pods to other nodes.

You can evacuate only pods that are backed by a replication controller. The replication controller creates new pods on other nodes and removes the existing pods from the specified node(s).

Bare pods, meaning those not backed by a replication controller, are unaffected by default. You can evacuate a subset of pods by specifying a pod selector. Because pod selectors are based on labels, all of the pods with the specified label are evacuated.

Procedure

- Mark the nodes as unschedulable before performing the pod evacuation.Mark the node as unschedulable by running the following command:oc adm cordon <node1>$oc adm cordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputnode/<node1> cordonednode/<node1> cordonedCopy to ClipboardCopied!Toggle word wrapToggle overflowCheck that the node status isReady,SchedulingDisabledby running the following command:oc get node <node1>$oc getnode<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3NAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the nodes as unschedulable before performing the pod evacuation.

- Mark the node as unschedulable by running the following command:oc adm cordon <node1>$oc adm cordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputnode/<node1> cordonednode/<node1> cordonedCopy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the node as unschedulable by running the following command:

Example output

- Check that the node status isReady,SchedulingDisabledby running the following command:oc get node <node1>$oc getnode<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3NAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check that the node status isReady,SchedulingDisabledby running the following command:

Example output

```
NAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3
```

```
NAME        STATUS                     ROLES     AGE       VERSION
<node1>     Ready,SchedulingDisabled   worker    1d        v1.30.3
```

- Evacuate the pods by using one of the following methods:Evacuate all or selected pods on one or more nodes by running theoc adm draincommand:oc adm drain <node1> <node2> [--pod-selector=<pod_selector>]$oc adm drain<node1><node2>[--pod-selector=<pod_selector>]Copy to ClipboardCopied!Toggle word wrapToggle overflowForce the deletion of bare pods by using the--forceoption with theoc adm draincommand. When set totrue, deletion continues even if there are pods not managed by a replication controller, replica set, job, daemon set, or stateful set.oc adm drain <node1> <node2> --force=true$oc adm drain<node1><node2>--force=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowSet a period of time in seconds for each pod to terminate gracefully by using the--grace-periodoption with theoc adm draincommand. If negative, the default value specified in the pod will be used:oc adm drain <node1> <node2> --grace-period=-1$oc adm drain<node1><node2>--grace-period=-1Copy to ClipboardCopied!Toggle word wrapToggle overflowIgnore pods managed by daemon sets by using the--ignore-daemonsets=trueoption with theoc adm draincommand:oc adm drain <node1> <node2> --ignore-daemonsets=true$oc adm drain<node1><node2>--ignore-daemonsets=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowSet the length of time to wait before giving up using the--timeoutoption with theoc adm draincommand. A value of0sets an infinite length of time.oc adm drain <node1> <node2> --timeout=5s$oc adm drain<node1><node2>--timeout=5sCopy to ClipboardCopied!Toggle word wrapToggle overflowDelete pods even if there are pods usingemptyDirvolumes by setting the--delete-emptydir-data=trueoption with theoc adm draincommand. Local data is deleted when the node is drained.oc adm drain <node1> <node2> --delete-emptydir-data=true$oc adm drain<node1><node2>--delete-emptydir-data=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowList objects that would be migrated without actually performing the evacuation, by using the--dry-run=trueoption with theoc adm draincommand:oc adm drain <node1> <node2>  --dry-run=true$oc adm drain<node1><node2>--dry-run=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowInstead of specifying specific node names (for example,<node1> <node2>), you can use the--selector=<node_selector>option with theoc adm draincommand to evacuate pods on selected nodes.

Evacuate the pods by using one of the following methods:

- Evacuate all or selected pods on one or more nodes by running theoc adm draincommand:oc adm drain <node1> <node2> [--pod-selector=<pod_selector>]$oc adm drain<node1><node2>[--pod-selector=<pod_selector>]Copy to ClipboardCopied!Toggle word wrapToggle overflow

Evacuate all or selected pods on one or more nodes by running theoc adm draincommand:

- Force the deletion of bare pods by using the--forceoption with theoc adm draincommand. When set totrue, deletion continues even if there are pods not managed by a replication controller, replica set, job, daemon set, or stateful set.oc adm drain <node1> <node2> --force=true$oc adm drain<node1><node2>--force=trueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Force the deletion of bare pods by using the--forceoption with theoc adm draincommand. When set totrue, deletion continues even if there are pods not managed by a replication controller, replica set, job, daemon set, or stateful set.

- Set a period of time in seconds for each pod to terminate gracefully by using the--grace-periodoption with theoc adm draincommand. If negative, the default value specified in the pod will be used:oc adm drain <node1> <node2> --grace-period=-1$oc adm drain<node1><node2>--grace-period=-1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Set a period of time in seconds for each pod to terminate gracefully by using the--grace-periodoption with theoc adm draincommand. If negative, the default value specified in the pod will be used:

- Ignore pods managed by daemon sets by using the--ignore-daemonsets=trueoption with theoc adm draincommand:oc adm drain <node1> <node2> --ignore-daemonsets=true$oc adm drain<node1><node2>--ignore-daemonsets=trueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Ignore pods managed by daemon sets by using the--ignore-daemonsets=trueoption with theoc adm draincommand:

- Set the length of time to wait before giving up using the--timeoutoption with theoc adm draincommand. A value of0sets an infinite length of time.oc adm drain <node1> <node2> --timeout=5s$oc adm drain<node1><node2>--timeout=5sCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set the length of time to wait before giving up using the--timeoutoption with theoc adm draincommand. A value of0sets an infinite length of time.

- Delete pods even if there are pods usingemptyDirvolumes by setting the--delete-emptydir-data=trueoption with theoc adm draincommand. Local data is deleted when the node is drained.oc adm drain <node1> <node2> --delete-emptydir-data=true$oc adm drain<node1><node2>--delete-emptydir-data=trueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Delete pods even if there are pods usingemptyDirvolumes by setting the--delete-emptydir-data=trueoption with theoc adm draincommand. Local data is deleted when the node is drained.

- List objects that would be migrated without actually performing the evacuation, by using the--dry-run=trueoption with theoc adm draincommand:oc adm drain <node1> <node2>  --dry-run=true$oc adm drain<node1><node2>--dry-run=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowInstead of specifying specific node names (for example,<node1> <node2>), you can use the--selector=<node_selector>option with theoc adm draincommand to evacuate pods on selected nodes.

List objects that would be migrated without actually performing the evacuation, by using the--dry-run=trueoption with theoc adm draincommand:

Instead of specifying specific node names (for example,<node1> <node2>), you can use the--selector=<node_selector>option with theoc adm draincommand to evacuate pods on selected nodes.

- Mark the node as schedulable when done by using the following command.oc adm uncordon <node1>$oc adm uncordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the node as schedulable when done by using the following command.

### 6.2.2. Understanding how to update labels on nodesCopy linkLink copied to clipboard!

You can update any label on a node in order to adapt your cluster to evolving needs.

Node labels are not persisted after a node is deleted even if the node is backed up by a Machine.

Any change to aMachineSetobject is not applied to existing machines owned by the compute machine set. For example, labels edited or added to an existingMachineSetobject are not propagated to existing machines and nodes associated with the compute machine set.

- The following command adds or updates labels on a node:oc label node <node> <key_1>=<value_1> ... <key_n>=<value_n>$oc labelnode<node><key_1>=<value_1>...<key_n>=<value_n>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc label nodes webconsole-7f7f6 unhealthy=true$oc label nodes webconsole-7f7f6unhealthy=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can alternatively apply the following YAML to apply the label:kind: Node
apiVersion: v1
metadata:
  name: webconsole-7f7f6
  labels:
    unhealthy: 'true'
#...kind:NodeapiVersion:v1metadata:name:webconsole-7f7f6labels:unhealthy:'true'#...Copy to ClipboardCopied!Toggle word wrapToggle overflow

The following command adds or updates labels on a node:

For example:

You can alternatively apply the following YAML to apply the label:

```
kind: Node
apiVersion: v1
metadata:
  name: webconsole-7f7f6
  labels:
    unhealthy: 'true'
#...
```

```
kind: Node
apiVersion: v1
metadata:
  name: webconsole-7f7f6
  labels:
    unhealthy: 'true'
#...
```

- The following command updates all pods in the namespace:oc label pods --all <key_1>=<value_1>$oc label pods--all<key_1>=<value_1>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc label pods --all status=unhealthy$oc label pods--allstatus=unhealthyCopy to ClipboardCopied!Toggle word wrapToggle overflow

The following command updates all pods in the namespace:

For example:

In OpenShift Container Platform 4.12 and later, newly installed clusters include both thenode-role.kubernetes.io/control-planeandnode-role.kubernetes.io/masterlabels on control plane nodes by default.

In OpenShift Container Platform versions earlier than 4.12, thenode-role.kubernetes.io/control-planelabel is not added by default. Therefore, you must manually add thenode-role.kubernetes.io/control-planelabel to control plane nodes in clusters upgraded from earlier versions.

### 6.2.3. Understanding how to mark nodes as unschedulable or schedulableCopy linkLink copied to clipboard!

You can mark a node as unschedulable in order to block any new pods from being scheduled on the node.

When you mark a node as unschedulable, existing pods on the node are not affected.

By default, healthy nodes with aReadystatus are marked as schedulable, which means that you can place new pods on the node.

- The following command marks a node or nodes as unschedulable:Example outputoc adm cordon <node>$oc adm cordon<node>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc adm cordon node1.example.com$oc adm cordon node1.example.comCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputnode/node1.example.com cordoned

NAME                 LABELS                                        STATUS
node1.example.com    kubernetes.io/hostname=node1.example.com      Ready,SchedulingDisablednode/node1.example.com cordoned

NAME                 LABELS                                        STATUS
node1.example.com    kubernetes.io/hostname=node1.example.com      Ready,SchedulingDisabledCopy to ClipboardCopied!Toggle word wrapToggle overflow

The following command marks a node or nodes as unschedulable:

Example output

For example:

Example output

```
node/node1.example.com cordoned

NAME                 LABELS                                        STATUS
node1.example.com    kubernetes.io/hostname=node1.example.com      Ready,SchedulingDisabled
```

```
node/node1.example.com cordoned

NAME                 LABELS                                        STATUS
node1.example.com    kubernetes.io/hostname=node1.example.com      Ready,SchedulingDisabled
```

- The following command marks a currently unschedulable node or nodes as schedulable:oc adm uncordon <node1>$oc adm uncordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowInstead of specifying specific node names (for example,<node>), you can use the--selector=<node_selector>option to mark selected nodes as schedulable or unschedulable.

The following command marks a currently unschedulable node or nodes as schedulable:

Instead of specifying specific node names (for example,<node>), you can use the--selector=<node_selector>option to mark selected nodes as schedulable or unschedulable.

### 6.2.4. Handling errors in single-node OpenShift clusters when the node reboots without draining application podsCopy linkLink copied to clipboard!

You can remove failed pods from a node by using the--field-selector status.phase=Failedflag with theoc delete podscommand.

In single-node OpenShift clusters and in OpenShift Container Platform clusters in general, a situation can arise where a node reboot occurs without first draining the node. This can occur where an application pod requesting devices fails with theUnexpectedAdmissionErrorerror.Deployment,ReplicaSet, orDaemonSeterrors are reported because the application pods that require those devices start before the pod serving those devices. You cannot control the order of pod restarts.

While this behavior is to be expected, it can cause a pod to remain on the cluster even though it has failed to deploy successfully. The pod continues to reportUnexpectedAdmissionError. This issue is mitigated by the fact that application pods are typically included in aDeployment,ReplicaSet, orDaemonSet. If a pod is in this error state, it is of little concern because another instance should be running. Belonging to aDeployment,ReplicaSet, orDaemonSetguarantees the successful creation and execution of subsequent pods and ensures the successful deployment of the application.

There is ongoing work upstream to ensure that such pods are gracefully terminated. Until that work is resolved, run the following command for a single-node OpenShift cluster to remove the failed pods:

The option to drain the node is unavailable for single-node OpenShift clusters.

### 6.2.5. Deleting nodes from a clusterCopy linkLink copied to clipboard!

You can delete a node from a OpenShift Container Platform cluster by scaling down the appropriateMachineSetobject.

When a cluster is integrated with a cloud provider, you must delete the corresponding machine to delete a node. Do not try to use theoc delete nodecommand for this task.

When you delete a node by using the CLI, the node object is deleted in Kubernetes, but the pods that exist on the node are not deleted. Any bare pods that are not backed by a replication controller become inaccessible to OpenShift Container Platform. Pods backed by replication controllers are rescheduled to other available nodes. You must delete local manifest pods.

If you are running cluster on bare metal, you cannot delete a node by editingMachineSetobjects. Compute machine sets are only available when a cluster is integrated with a cloud provider. Instead you must unschedule and drain the node before manually deleting it.

Procedure

- View the compute machine sets that are in the cluster by running the following command:oc get machinesets -n openshift-machine-api$oc get machinesets-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowThe compute machine sets are listed in the form of<cluster-id>-worker-<aws-region-az>.

View the compute machine sets that are in the cluster by running the following command:

The compute machine sets are listed in the form of<cluster-id>-worker-<aws-region-az>.

- Scale down the compute machine set by using one of the following methods:Specify the number of replicas to scale down to by running the following command:oc scale --replicas=2 machineset <machine-set-name> -n openshift-machine-api$oc scale--replicas=2machineset<machine-set-name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowEdit the compute machine set custom resource by running the following command:oc edit machineset <machine-set-name> -n openshift-machine-api$oc edit machineset<machine-set-name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  # ...
  name: <machine-set-name>
  namespace: openshift-machine-api
  # ...
spec:
  replicas: 2
  # ...apiVersion:machine.openshift.io/v1beta1kind:MachineSetmetadata:# ...name:<machine-set-name>namespace:openshift-machine-api# ...spec:replicas:2# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.replicasSpecifies the number of replicas to scale down to.

Scale down the compute machine set by using one of the following methods:

- Specify the number of replicas to scale down to by running the following command:oc scale --replicas=2 machineset <machine-set-name> -n openshift-machine-api$oc scale--replicas=2machineset<machine-set-name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflow

Specify the number of replicas to scale down to by running the following command:

- Edit the compute machine set custom resource by running the following command:oc edit machineset <machine-set-name> -n openshift-machine-api$oc edit machineset<machine-set-name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  # ...
  name: <machine-set-name>
  namespace: openshift-machine-api
  # ...
spec:
  replicas: 2
  # ...apiVersion:machine.openshift.io/v1beta1kind:MachineSetmetadata:# ...name:<machine-set-name>namespace:openshift-machine-api# ...spec:replicas:2# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.replicasSpecifies the number of replicas to scale down to.

Edit the compute machine set custom resource by running the following command:

Example output

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  # ...
  name: <machine-set-name>
  namespace: openshift-machine-api
  # ...
spec:
  replicas: 2
  # ...
```

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  # ...
  name: <machine-set-name>
  namespace: openshift-machine-api
  # ...
spec:
  replicas: 2
  # ...
```

where:

**spec.replicas**
  Specifies the number of replicas to scale down to.

#### 6.2.5.1. Deleting nodes from a bare metal clusterCopy linkLink copied to clipboard!

You can delete a node from a OpenShift Container Platform cluster that does not use machine sets by using theoc delete nodecommand and decommissioning the node.

When you delete a node using the CLI, the node object is deleted in Kubernetes, but the pods that exist on the node are not deleted. Any bare pods not backed by a replication controller become inaccessible to OpenShift Container Platform. Pods backed by replication controllers are rescheduled to other available nodes. You must delete local manifest pods.

The following procedure deletes a node from an OpenShift Container Platform cluster running on bare metal.

Procedure

- Mark the node as unschedulable:oc adm cordon <node_name>$oc adm cordon<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the node as unschedulable:

- Drain all pods on the node:oc adm drain <node_name> --force=true$oc adm drain<node_name>--force=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowThis step might fail if the node is offline or unresponsive. Even if the node does not respond, the node might still be running a workload that writes to shared storage. To avoid data corruption, power down the physical hardware before you proceed.

Drain all pods on the node:

This step might fail if the node is offline or unresponsive. Even if the node does not respond, the node might still be running a workload that writes to shared storage. To avoid data corruption, power down the physical hardware before you proceed.

- Delete the node from the cluster:oc delete node <node_name>$oc deletenode<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowAlthough the node object is now deleted from the cluster, it can still rejoin the cluster after reboot or if the kubelet service is restarted. To permanently delete the node and all its data, you mustdecommission the node.

Delete the node from the cluster:

Although the node object is now deleted from the cluster, it can still rejoin the cluster after reboot or if the kubelet service is restarted. To permanently delete the node and all its data, you mustdecommission the node.

- If you powered down the physical hardware, turn it back on so that the node can rejoin the cluster.

## 6.3. Managing nodesCopy linkLink copied to clipboard!

OpenShift Container Platform uses a KubeletConfig custom resource (CR) to manage the configuration of nodes. By creating an instance of aKubeletConfigobject, a managed machine config is created to override setting on the node.

Logging in to remote machines for the purpose of changing their configuration is not supported.

### 6.3.1. Modifying nodesCopy linkLink copied to clipboard!

To make configuration changes to a cluster, or machine pool, you must create a custom resource definition (CRD), orkubeletConfigobject. OpenShift Container Platform uses the Machine Config Controller to watch for changes introduced through the CRD to apply the changes to the cluster.

MostKubelet Configuration optionscan be set by the user. However, you cannot overwrite the following options:

- CgroupDriver
- ClusterDNS
- ClusterDomain
- StaticPodPath

If a single node contains more than 50 images, pod scheduling might be imbalanced across nodes. This is because the list of images on a node is shortened to 50 by default. You can disable the image limit by editing theKubeletConfigobject and setting the value ofnodeStatusMaxImagesto-1.

Because the fields in akubeletConfigobject are passed directly to the kubelet from upstream Kubernetes, the validation of those fields is handled directly by the kubelet itself. Please refer to the relevant Kubernetes documentation for the valid values for these fields. Invalid values in thekubeletConfigobject can render cluster nodes unusable.

Procedure

- Obtain the label associated with the static CRD, Machine Config Pool, for the type of node you want to configure. Perform one of the following steps:Check current labels of the desired machine config pool.For example:oc get machineconfigpool  --show-labels$oc get machineconfigpool  --show-labelsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      FalseNAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      FalseCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd a custom label to the desired machine config pool.For example:oc label machineconfigpool worker custom-kubelet=enabled$oc label machineconfigpool worker custom-kubelet=enabledCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain the label associated with the static CRD, Machine Config Pool, for the type of node you want to configure. Perform one of the following steps:

- Check current labels of the desired machine config pool.For example:oc get machineconfigpool  --show-labels$oc get machineconfigpool  --show-labelsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      FalseNAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      FalseCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check current labels of the desired machine config pool.

For example:

Example output

```
NAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      False
```

```
NAME      CONFIG                                             UPDATED   UPDATING   DEGRADED   LABELS
master    rendered-master-e05b81f5ca4db1d249a1bf32f9ec24fd   True      False      False      operator.machineconfiguration.openshift.io/required-for-upgrade=
worker    rendered-worker-f50e78e1bc06d8e82327763145bfcf62   True      False      False
```

- Add a custom label to the desired machine config pool.For example:oc label machineconfigpool worker custom-kubelet=enabled$oc label machineconfigpool worker custom-kubelet=enabledCopy to ClipboardCopied!Toggle word wrapToggle overflow

Add a custom label to the desired machine config pool.

For example:

- Create akubeletconfigcustom resource (CR) for your configuration change, as demonstrated in the following sample configuration for acustom-configCR:apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: custom-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      custom-kubelet: enabled
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
    systemReserved:
      cpu: 2000m
      memory: 1Gi
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:custom-configspec:machineConfigPoolSelector:matchLabels:custom-kubelet:enabledkubeletConfig:podsPerCore:10maxPods:250systemReserved:cpu:2000mmemory:1Gi#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:nameAssign a name to CR.custom-kubeletSpecify the label to apply the configuration change, this is the label you added to the machine config pool.kubeletConfigSpecify the new value(s) you want to change.

Create akubeletconfigcustom resource (CR) for your configuration change, as demonstrated in the following sample configuration for acustom-configCR:

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: custom-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      custom-kubelet: enabled
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
    systemReserved:
      cpu: 2000m
      memory: 1Gi
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: custom-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      custom-kubelet: enabled
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
    systemReserved:
      cpu: 2000m
      memory: 1Gi
#...
```

where:

**name**
  Assign a name to CR.

**custom-kubelet**
  Specify the label to apply the configuration change, this is the label you added to the machine config pool.

**kubeletConfig**
  Specify the new value(s) you want to change.
- Create the CR object:oc create -f <file-name>$oc create-f<file-name>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc create -f master-kube-config.yaml$oc create-fmaster-kube-config.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the CR object:

For example:

### 6.3.2. Updating boot imagesCopy linkLink copied to clipboard!

The Machine Config Operator (MCO) uses a boot image to bring up a Red Hat Enterprise Linux CoreOS (RHCOS) node. By default, OpenShift Container Platform does not manage the boot image.

This means that the boot image in your cluster is not updated along with your cluster. For example, if your cluster was originally created with OpenShift Container Platform 4.12, the boot image that the cluster uses to create nodes is the same 4.12 version, even if your cluster is at a later version. If the cluster is later upgraded to 4.13 or later, new nodes continue to scale with the same 4.12 image.

This process could cause the following issues:

- Extra time to start up nodes
- Certificate expiration issues
- Version skew issues

To avoid these issues, you can configure your cluster to update the boot image whenever you update your cluster. By modifying theMachineConfigurationobject, you can enable this feature. Currently, the ability to update the boot image is available for only Google Cloud clusters as a Generally Available (GA) feature and Amazon Web Services (AWS) clusters as a Technology Preview feature and is not supported for Cluster CAPI Operator managed clusters.

The updating boot image feature on AWS clusters is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

To view the current boot image used in your cluster, examine a machine set:

Example machine set with the boot image reference

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: ci-ln-hmy310k-72292-5f87z-worker-a
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    spec:
# ...
      providerSpec:
# ...
        value:
          disks:
          - autoDelete: true
            boot: true
            image: projects/rhcos-cloud/global/images/rhcos-412-85-202203181601-0-gcp-x86-64 
# ...
```

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  name: ci-ln-hmy310k-72292-5f87z-worker-a
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    spec:
# ...
      providerSpec:
# ...
        value:
          disks:
          - autoDelete: true
            boot: true
            image: projects/rhcos-cloud/global/images/rhcos-412-85-202203181601-0-gcp-x86-64
```

```
# ...
```

**1**
  This boot image is the same as the originally-installed OpenShift Container Platform version, in this example OpenShift Container Platform 4.12, regardless of the current version of the cluster. The way that the boot image is represented in the machine set depends on the platform, as the structure of theproviderSpecfield differs from platform to platform.

If you configure your cluster to update your boot images, the boot image referenced in your machine sets matches the current version of the cluster.

Prerequisites

- You have enabled theTechPreviewNoUpgradefeature set by using the feature gates. For more information, see "Enabling features using feature gates" in the "Additional resources" section.

Procedure

- Edit theMachineConfigurationobject, namedcluster, to enable the updating of boot images by running the following command:oc edit MachineConfiguration cluster$oc edit MachineConfiguration clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowOptional: Configure the boot image update feature for all the machine sets:apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: AllapiVersion:operator.openshift.io/v1kind:MachineConfigurationmetadata:name:clusternamespace:openshift-machine-config-operatorspec:# ...managedBootImages:1machineManagers:-resource:machinesetsapiGroup:machine.openshift.ioselection:mode:All2Copy to ClipboardCopied!Toggle word wrapToggle overflow1Activates the boot image update feature.2Specifies that all the machine sets in the cluster are to be updated.Optional: Configure the boot image update feature for specific machine sets:apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: Partial
          partial:
            machineResourceSelector:
              matchLabels:
                update-boot-image: "true"apiVersion:operator.openshift.io/v1kind:MachineConfigurationmetadata:name:clusternamespace:openshift-machine-config-operatorspec:# ...managedBootImages:1machineManagers:-resource:machinesetsapiGroup:machine.openshift.ioselection:mode:Partialpartial:machineResourceSelector:matchLabels:update-boot-image:"true"2Copy to ClipboardCopied!Toggle word wrapToggle overflow1Activates the boot image update feature.2Specifies that any machine set with this label is to be updated.If an appropriate label is not present on the machine set, add a key/value pair by running a command similar to following:oc label machineset.machine ci-ln-hmy310k-72292-5f87z-worker-a update-boot-image=true -n openshift-machine-api$ oc label machineset.machine ci-ln-hmy310k-72292-5f87z-worker-a update-boot-image=true -n openshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theMachineConfigurationobject, namedcluster, to enable the updating of boot images by running the following command:

- Optional: Configure the boot image update feature for all the machine sets:apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: AllapiVersion:operator.openshift.io/v1kind:MachineConfigurationmetadata:name:clusternamespace:openshift-machine-config-operatorspec:# ...managedBootImages:1machineManagers:-resource:machinesetsapiGroup:machine.openshift.ioselection:mode:All2Copy to ClipboardCopied!Toggle word wrapToggle overflow1Activates the boot image update feature.2Specifies that all the machine sets in the cluster are to be updated.

Optional: Configure the boot image update feature for all the machine sets:

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: All
```

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages:
```

```
machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: All
```

**1**
  Activates the boot image update feature.

**2**
  Specifies that all the machine sets in the cluster are to be updated.
- Optional: Configure the boot image update feature for specific machine sets:apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: Partial
          partial:
            machineResourceSelector:
              matchLabels:
                update-boot-image: "true"apiVersion:operator.openshift.io/v1kind:MachineConfigurationmetadata:name:clusternamespace:openshift-machine-config-operatorspec:# ...managedBootImages:1machineManagers:-resource:machinesetsapiGroup:machine.openshift.ioselection:mode:Partialpartial:machineResourceSelector:matchLabels:update-boot-image:"true"2Copy to ClipboardCopied!Toggle word wrapToggle overflow1Activates the boot image update feature.2Specifies that any machine set with this label is to be updated.If an appropriate label is not present on the machine set, add a key/value pair by running a command similar to following:oc label machineset.machine ci-ln-hmy310k-72292-5f87z-worker-a update-boot-image=true -n openshift-machine-api$ oc label machineset.machine ci-ln-hmy310k-72292-5f87z-worker-a update-boot-image=true -n openshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Configure the boot image update feature for specific machine sets:

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages: 
    machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: Partial
          partial:
            machineResourceSelector:
              matchLabels:
                update-boot-image: "true"
```

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
  namespace: openshift-machine-config-operator
spec:
# ...
  managedBootImages:
```

```
machineManagers:
    - resource: machinesets
      apiGroup: machine.openshift.io
      selection:
        mode: Partial
          partial:
            machineResourceSelector:
              matchLabels:
                update-boot-image: "true"
```

**1**
  Activates the boot image update feature.

**2**
  Specifies that any machine set with this label is to be updated.

If an appropriate label is not present on the machine set, add a key/value pair by running a command similar to following:

Verification

- Get the boot image version by running the following command:oc get machinesets <machineset_name> -n openshift-machine-api -o yaml$oc get machinesets<machineset_name>-nopenshift-machine-api-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample machine set with the boot image referenceapiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: ci-ln-77hmkpt-72292-d4pxp
    update-boot-image: "true"
  name: ci-ln-77hmkpt-72292-d4pxp-worker-a
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    spec:
# ...
      providerSpec:
# ...
        value:
          disks:
          - autoDelete: true
            boot: true
            image: projects/rhcos-cloud/global/images/rhcos-416-92-202402201450-0-gcp-x86-64 
# ...apiVersion:machine.openshift.io/v1beta1kind:MachineSetmetadata:labels:machine.openshift.io/cluster-api-cluster:ci-ln-77hmkpt-72292-d4pxpupdate-boot-image:"true"name:ci-ln-77hmkpt-72292-d4pxp-worker-anamespace:openshift-machine-apispec:# ...template:# ...spec:# ...providerSpec:# ...value:disks:-autoDelete:trueboot:trueimage:projects/rhcos-cloud/global/images/rhcos-416-92-202402201450-0-gcp-x86-641# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1This boot image is the same as the current OpenShift Container Platform version.

Get the boot image version by running the following command:

Example machine set with the boot image reference

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: ci-ln-77hmkpt-72292-d4pxp
    update-boot-image: "true"
  name: ci-ln-77hmkpt-72292-d4pxp-worker-a
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    spec:
# ...
      providerSpec:
# ...
        value:
          disks:
          - autoDelete: true
            boot: true
            image: projects/rhcos-cloud/global/images/rhcos-416-92-202402201450-0-gcp-x86-64 
# ...
```

```
apiVersion: machine.openshift.io/v1beta1
kind: MachineSet
metadata:
  labels:
    machine.openshift.io/cluster-api-cluster: ci-ln-77hmkpt-72292-d4pxp
    update-boot-image: "true"
  name: ci-ln-77hmkpt-72292-d4pxp-worker-a
  namespace: openshift-machine-api
spec:
# ...
  template:
# ...
    spec:
# ...
      providerSpec:
# ...
        value:
          disks:
          - autoDelete: true
            boot: true
            image: projects/rhcos-cloud/global/images/rhcos-416-92-202402201450-0-gcp-x86-64
```

```
# ...
```

**1**
  This boot image is the same as the current OpenShift Container Platform version.

#### 6.3.2.1. Disabling updated boot imagesCopy linkLink copied to clipboard!

To disable the updated boot image feature, edit theMachineConfigurationobject so that themachineManagersfield is an empty array.

If you disable this feature after some nodes have been created with the new boot image version, any existing nodes retain their current boot image. Turning off this feature does not rollback the nodes or machine sets to the originally-installed boot image. The machine sets retain the boot image version that was present when the feature was enabled and is not updated again when the cluster is upgraded to a new OpenShift Container Platform version in the future.

Procedure

- Disable updated boot images by editing theMachineConfigurationobject:oc edit MachineConfiguration cluster$oc edit MachineConfiguration clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Disable updated boot images by editing theMachineConfigurationobject:

- Make themachineManagersparameter an empty array:apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
spec:
# ...
  managedBootImages:
    machineManagers: []apiVersion:operator.openshift.io/v1kind:MachineConfigurationmetadata:name:clusterspec:# ...managedBootImages:machineManagers:[]Copy to ClipboardCopied!Toggle word wrapToggle overflowRemove the parameters listed undermachineManagersand add the[]characters to disable boot image updates.

Make themachineManagersparameter an empty array:

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
spec:
# ...
  managedBootImages:
    machineManagers: []
```

```
apiVersion: operator.openshift.io/v1
kind: MachineConfiguration
metadata:
  name: cluster
spec:
# ...
  managedBootImages:
    machineManagers: []
```

Remove the parameters listed undermachineManagersand add the[]characters to disable boot image updates.

### 6.3.3. Configuring control plane nodes as schedulableCopy linkLink copied to clipboard!

You can configure control plane nodes to be schedulable, meaning that new pods are allowed for placement on the control plane nodes.

By default, control plane nodes are not schedulable. You can set the control plane nodes to be schedulable, but you must retain the compute nodes.

You can deploy OpenShift Container Platform with no compute nodes on a bare-metal cluster. In this case, the control plane nodes are marked schedulable by default.

You can allow or disallow control plane nodes to be schedulable by configuring themastersSchedulablefield.

When you configure control plane nodes from the default unschedulable to schedulable, additional subscriptions are required. This is because control plane nodes then become compute nodes.

Procedure

- Edit theschedulers.config.openshift.ioresource.oc edit schedulers.config.openshift.io cluster$oc edit schedulers.config.openshift.io clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theschedulers.config.openshift.ioresource.

- Configure themastersSchedulablefield.apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  creationTimestamp: "2019-09-10T03:04:05Z"
  generation: 1
  name: cluster
  resourceVersion: "433"
  selfLink: /apis/config.openshift.io/v1/schedulers/cluster
  uid: a636d30a-d377-11e9-88d4-0a60097bee62
spec:
  mastersSchedulable: false
status: {}
#...apiVersion:config.openshift.io/v1kind:Schedulermetadata:creationTimestamp:"2019-09-10T03:04:05Z"generation:1name:clusterresourceVersion:"433"selfLink:/apis/config.openshift.io/v1/schedulers/clusteruid:a636d30a-d377-11e9-88d4-0a60097bee62spec:mastersSchedulable:falsestatus:{}#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.mastersSchedulableSpecifies whether the control plane nodes are schedulable. Set totrueto allow control plane nodes to be schedulable, orfalseto disallow control plane nodes from being schedulable.

Configure themastersSchedulablefield.

```
apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  creationTimestamp: "2019-09-10T03:04:05Z"
  generation: 1
  name: cluster
  resourceVersion: "433"
  selfLink: /apis/config.openshift.io/v1/schedulers/cluster
  uid: a636d30a-d377-11e9-88d4-0a60097bee62
spec:
  mastersSchedulable: false
status: {}
#...
```

```
apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  creationTimestamp: "2019-09-10T03:04:05Z"
  generation: 1
  name: cluster
  resourceVersion: "433"
  selfLink: /apis/config.openshift.io/v1/schedulers/cluster
  uid: a636d30a-d377-11e9-88d4-0a60097bee62
spec:
  mastersSchedulable: false
status: {}
#...
```

where:

**spec.mastersSchedulable**
  Specifies whether the control plane nodes are schedulable. Set totrueto allow control plane nodes to be schedulable, orfalseto disallow control plane nodes from being schedulable.
- Save the file to apply the changes.

### 6.3.4. Setting SELinux booleansCopy linkLink copied to clipboard!

OpenShift Container Platform allows you to enable and disable an SELinux boolean on a Red Hat Enterprise Linux CoreOS (RHCOS) node. The following procedure explains how to modify SELinux booleans on nodes using the Machine Config Operator (MCO). This procedure usescontainer_manage_cgroupas the example boolean. You can modify this value to whichever boolean you need.

Prerequisites

- You have installed the OpenShift CLI (oc).

Procedure

- Create a new YAML file with aMachineConfigobject, displayed in the following example:apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 99-worker-setsebool
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - contents: |
          [Unit]
          Description=Set SELinux booleans
          Before=kubelet.service

          [Service]
          Type=oneshot
          ExecStart=/sbin/setsebool container_manage_cgroup=on
          RemainAfterExit=true

          [Install]
          WantedBy=multi-user.target graphical.target
        enabled: true
        name: setsebool.service
#...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:workername:99-worker-setseboolspec:config:ignition:version:3.2.0systemd:units:-contents:|[Unit]
          Description=Set SELinux booleans
          Before=kubelet.service[Service]Type=oneshot
          ExecStart=/sbin/setsebool container_manage_cgroup=on
          RemainAfterExit=true[Install]WantedBy=multi-user.target graphical.targetenabled:truename:setsebool.service#...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Create a new YAML file with aMachineConfigobject, displayed in the following example:

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 99-worker-setsebool
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - contents: |
          [Unit]
          Description=Set SELinux booleans
          Before=kubelet.service

          [Service]
          Type=oneshot
          ExecStart=/sbin/setsebool container_manage_cgroup=on
          RemainAfterExit=true

          [Install]
          WantedBy=multi-user.target graphical.target
        enabled: true
        name: setsebool.service
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 99-worker-setsebool
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - contents: |
          [Unit]
          Description=Set SELinux booleans
          Before=kubelet.service

          [Service]
          Type=oneshot
          ExecStart=/sbin/setsebool container_manage_cgroup=on
          RemainAfterExit=true

          [Install]
          WantedBy=multi-user.target graphical.target
        enabled: true
        name: setsebool.service
#...
```

- Create the newMachineConfigobject by running the following command:oc create -f 99-worker-setsebool.yaml$oc create-f99-worker-setsebool.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowApplying any changes to theMachineConfigobject causes all affected nodes to gracefully reboot after the change is applied.

Create the newMachineConfigobject by running the following command:

Applying any changes to theMachineConfigobject causes all affected nodes to gracefully reboot after the change is applied.

### 6.3.5. Adding kernel arguments to nodesCopy linkLink copied to clipboard!

In some special cases, you can add kernel arguments to a set of nodes in your cluster to customize the kernel behavior to meet specific needs you might have.

You should add kernel arguments with caution and a clear understanding of the implications of the arguments you set.

Improper use of kernel arguments can result in your systems becoming unbootable.

Examples of kernel arguments you could set include:

- nosmt: Disables symmetric multithreading (SMT) in the kernel. Multithreading allows multiple logical threads for each CPU. You could considernosmtin multi-tenant environments to reduce risks from potential cross-thread attacks. By disabling SMT, you essentially choose security over performance.
- systemd.unified_cgroup_hierarchy: EnablesLinux control group version 2(cgroup v2). cgroup v2 is the next version of the kernelcontrol groupand offers multiple improvements.cgroup v1 is a deprecated feature. Deprecated functionality is still included in OpenShift Container Platform and continues to be supported; however, it will be removed in a future release of this product and is not recommended for new deployments.For the most recent list of major functionality that has been deprecated or removed within OpenShift Container Platform, refer to theDeprecated and removed featuressection of the OpenShift Container Platform release notes.

systemd.unified_cgroup_hierarchy: EnablesLinux control group version 2(cgroup v2). cgroup v2 is the next version of the kernelcontrol groupand offers multiple improvements.

cgroup v1 is a deprecated feature. Deprecated functionality is still included in OpenShift Container Platform and continues to be supported; however, it will be removed in a future release of this product and is not recommended for new deployments.

For the most recent list of major functionality that has been deprecated or removed within OpenShift Container Platform, refer to theDeprecated and removed featuressection of the OpenShift Container Platform release notes.

- enforcing=0: Configures Security Enhanced Linux (SELinux) to run in permissive mode. In permissive mode, the system acts as if SELinux is enforcing the loaded security policy, including labeling objects and emitting access denial entries in the logs, but it does not actually deny any operations. While not supported for production systems, permissive mode can be helpful for debugging.Disabling SELinux on RHCOS in production is not supported. After SELinux has been disabled on a node, it must be re-provisioned before re-inclusion in a production cluster.

enforcing=0: Configures Security Enhanced Linux (SELinux) to run in permissive mode. In permissive mode, the system acts as if SELinux is enforcing the loaded security policy, including labeling objects and emitting access denial entries in the logs, but it does not actually deny any operations. While not supported for production systems, permissive mode can be helpful for debugging.

Disabling SELinux on RHCOS in production is not supported. After SELinux has been disabled on a node, it must be re-provisioned before re-inclusion in a production cluster.

SeeKernel.org kernel parametersfor a list and descriptions of kernel arguments.

In the following procedure, you create aMachineConfigobject that identifies:

- A set of machines to which you want to add the kernel argument. In this case, machines with a worker role.
- Kernel arguments that are appended to the end of the existing kernel arguments.
- A label that indicates where in the list of machine configs the change is applied.

Prerequisites

- You havecluster-adminprivileges.
- Your cluster is running.

Procedure

- List existingMachineConfigobjects for your OpenShift Container Platform cluster to determine how to label your machine config:oc get MachineConfig$oc get MachineConfigCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33mNAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33mCopy to ClipboardCopied!Toggle word wrapToggle overflow

List existingMachineConfigobjects for your OpenShift Container Platform cluster to determine how to label your machine config:

Example output

```
NAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
```

```
NAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
```

- Create aMachineConfigobject file that identifies the kernel argument (for example,05-worker-kernelarg-selinuxpermissive.yaml)apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 05-worker-kernelarg-selinuxpermissive
spec:
  kernelArguments:
    - enforcing=0apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:workername:05-worker-kernelarg-selinuxpermissivespec:kernelArguments:-enforcing=0Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:machineconfiguration.openshift.io/roleSpecifies a label to apply changes to specific nodes.nameSpecifies a name to identify where it fits among the machine configs (05) and what it does (adds a kernel argument to configure SELinux permissive mode).kernelArgumentsSpecifies the exact kernel argument asenforcing=0.

Create aMachineConfigobject file that identifies the kernel argument (for example,05-worker-kernelarg-selinuxpermissive.yaml)

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 05-worker-kernelarg-selinuxpermissive
spec:
  kernelArguments:
    - enforcing=0
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: worker
  name: 05-worker-kernelarg-selinuxpermissive
spec:
  kernelArguments:
    - enforcing=0
```

where:

**machineconfiguration.openshift.io/role**
  Specifies a label to apply changes to specific nodes.

**name**
  Specifies a name to identify where it fits among the machine configs (05) and what it does (adds a kernel argument to configure SELinux permissive mode).

**kernelArguments**
  Specifies the exact kernel argument asenforcing=0.
- Create the new machine config:oc create -f 05-worker-kernelarg-selinuxpermissive.yaml$oc create-f05-worker-kernelarg-selinuxpermissive.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the new machine config:

- Check the machine configs to see that the new one was added:oc get MachineConfig$oc get MachineConfigCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
05-worker-kernelarg-selinuxpermissive                                                         3.4.0             105s
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33mNAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
05-worker-kernelarg-selinuxpermissive                                                         3.4.0             105s
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33mCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check the machine configs to see that the new one was added:

Example output

```
NAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
05-worker-kernelarg-selinuxpermissive                                                         3.4.0             105s
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
```

```
NAME                                               GENERATEDBYCONTROLLER                      IGNITIONVERSION   AGE
00-master                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
00-worker                                          52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-master-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-container-runtime                        52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
01-worker-kubelet                                  52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
05-worker-kernelarg-selinuxpermissive                                                         3.4.0             105s
99-master-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-master-ssh                                                                                 3.2.0             40m
99-worker-generated-registries                     52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
99-worker-ssh                                                                                 3.2.0             40m
rendered-master-23e785de7587df95a4b517e0647e5ab7   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
rendered-worker-5d596d9293ca3ea80c896a1191735bb1   52dd3ba6a9a527fc3ab42afac8d12b693534c8c9   3.4.0             33m
```

- Check the nodes:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                           STATUS                     ROLES    AGE   VERSION
ip-10-0-136-161.ec2.internal   Ready                      worker   28m   v1.30.3
ip-10-0-136-243.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-141-105.ec2.internal   Ready,SchedulingDisabled   worker   28m   v1.30.3
ip-10-0-142-249.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-153-11.ec2.internal    Ready                      worker   28m   v1.30.3
ip-10-0-153-150.ec2.internal   Ready                      master   34m   v1.30.3NAME                           STATUS                     ROLES    AGE   VERSION
ip-10-0-136-161.ec2.internal   Ready                      worker   28m   v1.30.3
ip-10-0-136-243.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-141-105.ec2.internal   Ready,SchedulingDisabled   worker   28m   v1.30.3
ip-10-0-142-249.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-153-11.ec2.internal    Ready                      worker   28m   v1.30.3
ip-10-0-153-150.ec2.internal   Ready                      master   34m   v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflowYou can see that scheduling on each worker node is disabled as the change is being applied.

Check the nodes:

Example output

```
NAME                           STATUS                     ROLES    AGE   VERSION
ip-10-0-136-161.ec2.internal   Ready                      worker   28m   v1.30.3
ip-10-0-136-243.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-141-105.ec2.internal   Ready,SchedulingDisabled   worker   28m   v1.30.3
ip-10-0-142-249.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-153-11.ec2.internal    Ready                      worker   28m   v1.30.3
ip-10-0-153-150.ec2.internal   Ready                      master   34m   v1.30.3
```

```
NAME                           STATUS                     ROLES    AGE   VERSION
ip-10-0-136-161.ec2.internal   Ready                      worker   28m   v1.30.3
ip-10-0-136-243.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-141-105.ec2.internal   Ready,SchedulingDisabled   worker   28m   v1.30.3
ip-10-0-142-249.ec2.internal   Ready                      master   34m   v1.30.3
ip-10-0-153-11.ec2.internal    Ready                      worker   28m   v1.30.3
ip-10-0-153-150.ec2.internal   Ready                      master   34m   v1.30.3
```

You can see that scheduling on each worker node is disabled as the change is being applied.

- Check that the kernel argument worked by going to one of the worker nodes and listing the kernel command-line arguments (in/proc/cmdlineon the host):oc debug node/ip-10-0-141-105.ec2.internal$oc debug node/ip-10-0-141-105.ec2.internalCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputStarting pod/ip-10-0-141-105ec2internal-debug ...
To use host binaries, run `chroot /host`

sh-4.2# cat /host/proc/cmdline
BOOT_IMAGE=/ostree/rhcos-... console=tty0 console=ttyS0,115200n8
rootflags=defaults,prjquota rw root=UUID=fd0... ostree=/ostree/boot.0/rhcos/16...
coreos.oem.id=qemu coreos.oem.id=ec2 ignition.platform.id=ec2 enforcing=0

sh-4.2# exitStarting pod/ip-10-0-141-105ec2internal-debug ...
To use host binaries, run `chroot /host`

sh-4.2# cat /host/proc/cmdline
BOOT_IMAGE=/ostree/rhcos-... console=tty0 console=ttyS0,115200n8
rootflags=defaults,prjquota rw root=UUID=fd0... ostree=/ostree/boot.0/rhcos/16...
coreos.oem.id=qemu coreos.oem.id=ec2 ignition.platform.id=ec2 enforcing=0

sh-4.2# exitCopy to ClipboardCopied!Toggle word wrapToggle overflowYou should see theenforcing=0argument added to the other kernel arguments.

Check that the kernel argument worked by going to one of the worker nodes and listing the kernel command-line arguments (in/proc/cmdlineon the host):

Example output

```
Starting pod/ip-10-0-141-105ec2internal-debug ...
To use host binaries, run `chroot /host`

sh-4.2# cat /host/proc/cmdline
BOOT_IMAGE=/ostree/rhcos-... console=tty0 console=ttyS0,115200n8
rootflags=defaults,prjquota rw root=UUID=fd0... ostree=/ostree/boot.0/rhcos/16...
coreos.oem.id=qemu coreos.oem.id=ec2 ignition.platform.id=ec2 enforcing=0

sh-4.2# exit
```

```
Starting pod/ip-10-0-141-105ec2internal-debug ...
To use host binaries, run `chroot /host`

sh-4.2# cat /host/proc/cmdline
BOOT_IMAGE=/ostree/rhcos-... console=tty0 console=ttyS0,115200n8
rootflags=defaults,prjquota rw root=UUID=fd0... ostree=/ostree/boot.0/rhcos/16...
coreos.oem.id=qemu coreos.oem.id=ec2 ignition.platform.id=ec2 enforcing=0

sh-4.2# exit
```

You should see theenforcing=0argument added to the other kernel arguments.

### 6.3.6. Allowing swap memory use on nodesCopy linkLink copied to clipboard!

You can allow workloads on the cluster nodes to use swap memory.

Swap memory support on nodes is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

Swap memory support is available only for container-native virtualization (CNV) users or use cases.

To allow swap memory usage on your nodes, create akubeletconfigcustom resource (CR) to set thefailSwapOnparameter tofalse.

Optionally, you can control swap memory usage by OpenShift Container Platform workloads on those nodes by setting theswapBehaviorparameter to one of the following values:

- NoSwapprevents OpenShift Container Platform worloads from using swap memory.
- LimitedSwapallows OpenShift Container Platform workloads that fall under the Burstable QoS class to use swap memory.

Regardless of theswapBehaviorsetting, any workloads that are not managed by OpenShift Container Platform on that node can still use swap memory if thefailSwapOnparameter isfalse.

Because the kubelet will not start in the presence of swap memory without this configuration, you must allow swap memory in OpenShift Container Platform before enabling swap memory on the nodes. If there is no swap memory present on a node, enabling swap memory in OpenShift Container Platform has no effect.

Using swap memory can negatively impact workload performance and out-of-resource handling. Do not enable swap memory on control plane nodes.

Prerequisites

- You have a running OpenShift Container Platform cluster that uses version 4.10 or later.
- Your cluster is configured to use cgroup v2. Swap memory is not supported on nodes in clusters that use cgroup v1.
- You are logged in to the cluster as a user with administrative privileges.
- You have enabled theTechPreviewNoUpgradefeature set on the cluster (seeNodesWorking with clustersEnabling features using feature gates).Enabling theTechPreviewNoUpgradefeature set cannot be undone and prevents minor version updates. These feature sets are not recommended on production clusters.

You have enabled theTechPreviewNoUpgradefeature set on the cluster (seeNodesWorking with clustersEnabling features using feature gates).

Enabling theTechPreviewNoUpgradefeature set cannot be undone and prevents minor version updates. These feature sets are not recommended on production clusters.

Procedure

- Apply a custom label to the machine config pool where you want to allow swap memory.oc label machineconfigpool worker kubelet-swap=enabled$oc label machineconfigpool worker kubelet-swap=enabledCopy to ClipboardCopied!Toggle word wrapToggle overflow

Apply a custom label to the machine config pool where you want to allow swap memory.

- Create a custom resource (CR) to enable and configure swap settings.apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: swap-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      kubelet-swap: enabled
  kubeletConfig:
    failSwapOn: false
    memorySwap:
      swapBehavior: LimitedSwap
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:swap-configspec:machineConfigPoolSelector:matchLabels:kubelet-swap:enabledkubeletConfig:failSwapOn:falsememorySwap:swapBehavior:LimitedSwap#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:failSwapOnSet tofalseto enable swap memory use on the associated nodes. Set totrueto disable swap memory use.swapBehaviorOptional: Specify the swap memory behavior for OpenShift Container Platform pods.NoSwap: OpenShift Container Platform pods cannot use swap. This is the default.LimitedSwap: OpenShift Container Platform pods of Burstable QoS class only are permitted to employ swap.

Create a custom resource (CR) to enable and configure swap settings.

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: swap-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      kubelet-swap: enabled
  kubeletConfig:
    failSwapOn: false
    memorySwap:
      swapBehavior: LimitedSwap
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: swap-config
spec:
  machineConfigPoolSelector:
    matchLabels:
      kubelet-swap: enabled
  kubeletConfig:
    failSwapOn: false
    memorySwap:
      swapBehavior: LimitedSwap
#...
```

where:

**failSwapOn**
  Set tofalseto enable swap memory use on the associated nodes. Set totrueto disable swap memory use.

**swapBehavior**
  Optional: Specify the swap memory behavior for OpenShift Container Platform pods.NoSwap: OpenShift Container Platform pods cannot use swap. This is the default.LimitedSwap: OpenShift Container Platform pods of Burstable QoS class only are permitted to employ swap.

Optional: Specify the swap memory behavior for OpenShift Container Platform pods.

- NoSwap: OpenShift Container Platform pods cannot use swap. This is the default.
- LimitedSwap: OpenShift Container Platform pods of Burstable QoS class only are permitted to employ swap.
- Enable swap memory on the nodes by setting theswapaccount=1kernel argument and configure swap memory as needed.

### 6.3.7. About configuring parallel container image pullsCopy linkLink copied to clipboard!

To help control bandwidth issues, you can configure the number of workload images that can be pulled at the same time.

By default, the cluster pulls images in parallel, which allows multiple workloads to pull images at the same time. Pulling multiple images in parallel can improve workload start-up time because workloads can pull needed images without waiting for each other. However, pulling too many images at the same time can use excessive network bandwidth and cause latency issues throughout your cluster.

The default setting allows unlimited simultaneous image pulls. But, you can configure the maximum number of images that can be pulled in parallel. You can also force serial image pulling, which means that only one image can be pulled at a time.

To control the number of images that can be pulled simultaneously, use a kubelet configuration to set themaxParallelImagePullsto specify a limit. Additional image pulls above this limit are held until one of the current pulls is complete.

To force serial image pulls, use a kubelet configuration to setserializeImagePullsfield totrue.

#### 6.3.7.1. Configuring parallel container image pullsCopy linkLink copied to clipboard!

You can control the number of images that can be pulled by your workload simultaneously by using a kubelet configuration. You can set a maximum number of images that can be pulled or force workloads to pull images one at a time.

Prerequisites

- You have a running OpenShift Container Platform cluster.
- You are logged in to the cluster as a user with administrative privileges.

Procedure

- Apply a custom label to the machine config pool where you want to configure parallel pulls by running a command similar to the following.oc label machineconfigpool <mcp_name> parallel-pulls=set$oc label machineconfigpool<mcp_name>parallel-pulls=setCopy to ClipboardCopied!Toggle word wrapToggle overflow

Apply a custom label to the machine config pool where you want to configure parallel pulls by running a command similar to the following.

- Create a custom resource (CR) to configure parallel image pulling.apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: parallel-image-pulls
# ...
spec:
  machineConfigPoolSelector:
    matchLabels:
      parallel-pulls: set
  kubeletConfig:
    serializeImagePulls: false
    maxParallelImagePulls: 3
# ...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:parallel-image-pulls# ...spec:machineConfigPoolSelector:matchLabels:parallel-pulls:setkubeletConfig:serializeImagePulls:falsemaxParallelImagePulls:3# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:serializeImagePullsSpecifies whether parallel pulling is enabled for the nodes in the associated machine config pool. Set tofalseto enable parallel image pulls. Set totrueto force serial image pulling. The default isfalse.maxParallelImagePullsSpecifies the maximum number of images that can be pulled in parallel. Enter a number or set tonilto specify no limit. This field cannot be set ifSerializeImagePullsistrue. The default isnil.

Create a custom resource (CR) to configure parallel image pulling.

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: parallel-image-pulls
# ...
spec:
  machineConfigPoolSelector:
    matchLabels:
      parallel-pulls: set
  kubeletConfig:
    serializeImagePulls: false
    maxParallelImagePulls: 3
# ...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: parallel-image-pulls
# ...
spec:
  machineConfigPoolSelector:
    matchLabels:
      parallel-pulls: set
  kubeletConfig:
    serializeImagePulls: false
    maxParallelImagePulls: 3
# ...
```

where:

**serializeImagePulls**
  Specifies whether parallel pulling is enabled for the nodes in the associated machine config pool. Set tofalseto enable parallel image pulls. Set totrueto force serial image pulling. The default isfalse.

**maxParallelImagePulls**
  Specifies the maximum number of images that can be pulled in parallel. Enter a number or set tonilto specify no limit. This field cannot be set ifSerializeImagePullsistrue. The default isnil.
- Create the new machine config by running a command similar to the following:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the new machine config by running a command similar to the following:

Verification

- Check the machine configs to see that a new one was added by running the following command:oc get MachineConfig$oc get MachineConfigCopy to ClipboardCopied!Toggle word wrapToggle overflowNAME                                                GENERATEDBYCONTROLLER                        IGNITIONVERSION   AGE
00-master                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
00-worker                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
# ...
99-parallel-generated-kubelet                       70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             15s
# ...
rendered-parallel-c634a80f644740974ceb40c054c79e50  70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             10sNAME                                                GENERATEDBYCONTROLLER                        IGNITIONVERSION   AGE
00-master                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
00-worker                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m#...99-parallel-generated-kubelet                       70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             15s#...rendered-parallel-c634a80f644740974ceb40c054c79e50  70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             10sCopy to ClipboardCopied!Toggle word wrapToggle overflowwhere:99-parallel-generated-kubeletSpecifies the new machine config. In this example, the machine config is for theparallelcustom machine config pool.rendered-parallel-<sha_numnber>Specifies the new rendered machine config. In this example, the machine config is for theparallelcustom machine config pool.

Check the machine configs to see that a new one was added by running the following command:

```
NAME                                                GENERATEDBYCONTROLLER                        IGNITIONVERSION   AGE
00-master                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
00-worker                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
# ...
99-parallel-generated-kubelet                       70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             15s
# ...
rendered-parallel-c634a80f644740974ceb40c054c79e50  70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             10s
```

```
NAME                                                GENERATEDBYCONTROLLER                        IGNITIONVERSION   AGE
00-master                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
00-worker                                           70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             133m
# ...
99-parallel-generated-kubelet                       70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             15s
# ...
rendered-parallel-c634a80f644740974ceb40c054c79e50  70025364a114fc3067b2e82ce47fdb0149630e4b     3.5.0             10s
```

where:

**99-parallel-generated-kubelet**
  Specifies the new machine config. In this example, the machine config is for theparallelcustom machine config pool.

**rendered-parallel-<sha_numnber>**
  Specifies the new rendered machine config. In this example, the machine config is for theparallelcustom machine config pool.
- Check to see that the nodes in theparallelmachine config pool are being updated by running the following command:oc get machineconfigpool$oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowNAME       CONFIG                                               UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
parallel   rendered-parallel-3904f0e69130d125b3b5ef0e981b1ce1   False     True       False      1              0                   0                     0                      65m
master     rendered-master-7536834c197384f3734c348c1d957c18     True      False      False      3              3                   3                     0                      140m
worker     rendered-worker-c634a80f644740974ceb40c054c79e50     True      False      False      2              2                   2                     0                      140mNAME       CONFIG                                               UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
parallel   rendered-parallel-3904f0e69130d125b3b5ef0e981b1ce1   False     True       False      1              0                   0                     0                      65m
master     rendered-master-7536834c197384f3734c348c1d957c18     True      False      False      3              3                   3                     0                      140m
worker     rendered-worker-c634a80f644740974ceb40c054c79e50     True      False      False      2              2                   2                     0                      140mCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check to see that the nodes in theparallelmachine config pool are being updated by running the following command:

```
NAME       CONFIG                                               UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
parallel   rendered-parallel-3904f0e69130d125b3b5ef0e981b1ce1   False     True       False      1              0                   0                     0                      65m
master     rendered-master-7536834c197384f3734c348c1d957c18     True      False      False      3              3                   3                     0                      140m
worker     rendered-worker-c634a80f644740974ceb40c054c79e50     True      False      False      2              2                   2                     0                      140m
```

```
NAME       CONFIG                                               UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
parallel   rendered-parallel-3904f0e69130d125b3b5ef0e981b1ce1   False     True       False      1              0                   0                     0                      65m
master     rendered-master-7536834c197384f3734c348c1d957c18     True      False      False      3              3                   3                     0                      140m
worker     rendered-worker-c634a80f644740974ceb40c054c79e50     True      False      False      2              2                   2                     0                      140m
```

- When the nodes are updated, verify that the parallel pull maximum was configured:Open anoc debugsession to a node by running a command similar to the following:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowSet/hostas the root directory within the debug shell by running the following command:chroot /hostsh-5.1# chroot /hostCopy to ClipboardCopied!Toggle word wrapToggle overflowExamine thekubelet.conffile by running the following command:cat /etc/kubernetes/kubelet.conf | grep -i maxParallelImagePullssh-5.1# cat /etc/kubernetes/kubelet.conf | grep -i maxParallelImagePullsCopy to ClipboardCopied!Toggle word wrapToggle overflowmaxParallelImagePulls: 3maxParallelImagePulls: 3Copy to ClipboardCopied!Toggle word wrapToggle overflow

When the nodes are updated, verify that the parallel pull maximum was configured:

- Open anoc debugsession to a node by running a command similar to the following:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Open anoc debugsession to a node by running a command similar to the following:

- Set/hostas the root directory within the debug shell by running the following command:chroot /hostsh-5.1# chroot /hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell by running the following command:

- Examine thekubelet.conffile by running the following command:cat /etc/kubernetes/kubelet.conf | grep -i maxParallelImagePullssh-5.1# cat /etc/kubernetes/kubelet.conf | grep -i maxParallelImagePullsCopy to ClipboardCopied!Toggle word wrapToggle overflowmaxParallelImagePulls: 3maxParallelImagePulls: 3Copy to ClipboardCopied!Toggle word wrapToggle overflow

Examine thekubelet.conffile by running the following command:

### 6.3.8. Migrating control plane nodes from one RHOSP host to another manuallyCopy linkLink copied to clipboard!

If control plane machine sets are not enabled on your cluster, you can run a script that moves a control plane node from one Red Hat OpenStack Platform (RHOSP) node to another.

Control plane machine sets are not enabled on clusters that run on user-provisioned infrastructure.

For information about control plane machine sets, see "Managing control plane machines with control plane machine sets".

Prerequisites

- The environment variableOS_CLOUDrefers to acloudsentry that has administrative credentials in aclouds.yamlfile.
- The environment variableKUBECONFIGrefers to a configuration that contains administrative OpenShift Container Platform credentials.

Procedure

- From a command line, run the following script:#!/usr/bin/env bash

set -Eeuo pipefail

if [ $# -lt 1 ]; then
	echo "Usage: '$0 node_name'"
	exit 64
fi

# Check for admin OpenStack credentials
openstack server list --all-projects >/dev/null || { >&2 echo "The script needs OpenStack admin credentials. Exiting"; exit 77; }

# Check for admin OpenShift credentials
oc adm top node >/dev/null || { >&2 echo "The script needs OpenShift admin credentials. Exiting"; exit 77; }

set -x

declare -r node_name="$1"
declare server_id
server_id="$(openstack server list --all-projects -f value -c ID -c Name | grep "$node_name" | cut -d' ' -f1)"
readonly server_id

# Drain the node
oc adm cordon "$node_name"
oc adm drain "$node_name" --delete-emptydir-data --ignore-daemonsets --force

# Power off the server
oc debug "node/${node_name}" -- chroot /host shutdown -h 1

# Verify the server is shut off
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Migrate the node
openstack server migrate --wait "$server_id"

# Resize the VM
openstack server resize confirm "$server_id"

# Wait for the resize confirm to finish
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Restart the VM
openstack server start "$server_id"

# Wait for the node to show up as Ready:
until oc get node "$node_name" | grep -q "^${node_name}[[:space:]]\+Ready"; do sleep 5; done

# Uncordon the node
oc adm uncordon "$node_name"

# Wait for cluster operators to stabilize
until oc get co -o go-template='statuses: {{ range .items }}{{ range .status.conditions }}{{ if eq .type "Degraded" }}{{ if ne .status "False" }}DEGRADED{{ end }}{{ else if eq .type "Progressing"}}{{ if ne .status "False" }}PROGRESSING{{ end }}{{ else if eq .type "Available"}}{{ if ne .status "True" }}NOTAVAILABLE{{ end }}{{ end }}{{ end }}{{ end }}' | grep -qv '\(DEGRADED\|PROGRESSING\|NOTAVAILABLE\)'; do sleep 5; done#!/usr/bin/env bashset-Eeuopipefailif[$#-lt1];thenecho"Usage: '$0node_name'"exit64fi# Check for admin OpenStack credentialsopenstack server list --all-projects>/dev/null||{>&2echo"The script needs OpenStack admin credentials. Exiting";exit77;}# Check for admin OpenShift credentialsoc admtopnode>/dev/null||{>&2echo"The script needs OpenShift admin credentials. Exiting";exit77;}set-xdeclare-rnode_name="$1"declareserver_idserver_id="$(openstack server list --all-projects-fvalue-cID-cName|grep"$node_name"|cut-d' '-f1)"readonlyserver_id# Drain the nodeoc adm cordon"$node_name"oc adm drain"$node_name"--delete-emptydir-data --ignore-daemonsets--force# Power off the serveroc debug"node/${node_name}"--chroot/hostshutdown-h1# Verify the server is shut offuntilopenstack server show"$server_id"-fvalue-cstatus|grep-q'SHUTOFF';dosleep5;done# Migrate the nodeopenstack server migrate--wait"$server_id"# Resize the VMopenstack server resize confirm"$server_id"# Wait for the resize confirm to finishuntilopenstack server show"$server_id"-fvalue-cstatus|grep-q'SHUTOFF';dosleep5;done# Restart the VMopenstack server start"$server_id"# Wait for the node to show up as Ready:untiloc getnode"$node_name"|grep-q"^${node_name}[[:space:]]\+Ready";dosleep5;done# Uncordon the nodeoc adm uncordon"$node_name"# Wait for cluster operators to stabilizeuntiloc get co-ogo-template='statuses: {{ range .items }}{{ range .status.conditions }}{{ if eq .type "Degraded" }}{{ if ne .status "False" }}DEGRADED{{ end }}{{ else if eq .type "Progressing"}}{{ if ne .status "False" }}PROGRESSING{{ end }}{{ else if eq .type "Available"}}{{ if ne .status "True" }}NOTAVAILABLE{{ end }}{{ end }}{{ end }}{{ end }}'|grep-qv'\(DEGRADED\|PROGRESSING\|NOTAVAILABLE\)';dosleep5;doneCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the script completes, the control plane machine is migrated to a new RHOSP node.

From a command line, run the following script:

```
#!/usr/bin/env bash

set -Eeuo pipefail

if [ $# -lt 1 ]; then
	echo "Usage: '$0 node_name'"
	exit 64
fi

# Check for admin OpenStack credentials
openstack server list --all-projects >/dev/null || { >&2 echo "The script needs OpenStack admin credentials. Exiting"; exit 77; }

# Check for admin OpenShift credentials
oc adm top node >/dev/null || { >&2 echo "The script needs OpenShift admin credentials. Exiting"; exit 77; }

set -x

declare -r node_name="$1"
declare server_id
server_id="$(openstack server list --all-projects -f value -c ID -c Name | grep "$node_name" | cut -d' ' -f1)"
readonly server_id

# Drain the node
oc adm cordon "$node_name"
oc adm drain "$node_name" --delete-emptydir-data --ignore-daemonsets --force

# Power off the server
oc debug "node/${node_name}" -- chroot /host shutdown -h 1

# Verify the server is shut off
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Migrate the node
openstack server migrate --wait "$server_id"

# Resize the VM
openstack server resize confirm "$server_id"

# Wait for the resize confirm to finish
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Restart the VM
openstack server start "$server_id"

# Wait for the node to show up as Ready:
until oc get node "$node_name" | grep -q "^${node_name}[[:space:]]\+Ready"; do sleep 5; done

# Uncordon the node
oc adm uncordon "$node_name"

# Wait for cluster operators to stabilize
until oc get co -o go-template='statuses: {{ range .items }}{{ range .status.conditions }}{{ if eq .type "Degraded" }}{{ if ne .status "False" }}DEGRADED{{ end }}{{ else if eq .type "Progressing"}}{{ if ne .status "False" }}PROGRESSING{{ end }}{{ else if eq .type "Available"}}{{ if ne .status "True" }}NOTAVAILABLE{{ end }}{{ end }}{{ end }}{{ end }}' | grep -qv '\(DEGRADED\|PROGRESSING\|NOTAVAILABLE\)'; do sleep 5; done
```

```
#!/usr/bin/env bash

set -Eeuo pipefail

if [ $# -lt 1 ]; then
	echo "Usage: '$0 node_name'"
	exit 64
fi

# Check for admin OpenStack credentials
openstack server list --all-projects >/dev/null || { >&2 echo "The script needs OpenStack admin credentials. Exiting"; exit 77; }

# Check for admin OpenShift credentials
oc adm top node >/dev/null || { >&2 echo "The script needs OpenShift admin credentials. Exiting"; exit 77; }

set -x

declare -r node_name="$1"
declare server_id
server_id="$(openstack server list --all-projects -f value -c ID -c Name | grep "$node_name" | cut -d' ' -f1)"
readonly server_id

# Drain the node
oc adm cordon "$node_name"
oc adm drain "$node_name" --delete-emptydir-data --ignore-daemonsets --force

# Power off the server
oc debug "node/${node_name}" -- chroot /host shutdown -h 1

# Verify the server is shut off
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Migrate the node
openstack server migrate --wait "$server_id"

# Resize the VM
openstack server resize confirm "$server_id"

# Wait for the resize confirm to finish
until openstack server show "$server_id" -f value -c status | grep -q 'SHUTOFF'; do sleep 5; done

# Restart the VM
openstack server start "$server_id"

# Wait for the node to show up as Ready:
until oc get node "$node_name" | grep -q "^${node_name}[[:space:]]\+Ready"; do sleep 5; done

# Uncordon the node
oc adm uncordon "$node_name"

# Wait for cluster operators to stabilize
until oc get co -o go-template='statuses: {{ range .items }}{{ range .status.conditions }}{{ if eq .type "Degraded" }}{{ if ne .status "False" }}DEGRADED{{ end }}{{ else if eq .type "Progressing"}}{{ if ne .status "False" }}PROGRESSING{{ end }}{{ else if eq .type "Available"}}{{ if ne .status "True" }}NOTAVAILABLE{{ end }}{{ end }}{{ end }}{{ end }}' | grep -qv '\(DEGRADED\|PROGRESSING\|NOTAVAILABLE\)'; do sleep 5; done
```

If the script completes, the control plane machine is migrated to a new RHOSP node.

## 6.4. Adding worker nodes to an on-premise clusterCopy linkLink copied to clipboard!

You can add worker nodes to on-premise clusters by using the OpenShift CLI (oc) to generate an ISO image, which can then be used to boot one or more nodes in your target cluster. This process can be used regardless of how you installed your cluster.

You can add one or more nodes at a time while customizing each node with more complex configurations, such as static network configuration, or you can specify only the MAC address of each node. Any required configurations that are not specified during ISO generation are retrieved from the target cluster and applied to the new nodes.

MachineorBareMetalHostresources are not automatically created after a node has been successfully added to the cluster.

Preflight validation checks are also performed when booting the ISO image to inform you of failure-causing issues before you attempt to boot each node.

**Supported platforms**
  The following platforms are supported for this method of adding nodes:baremetalvspherenone

The following platforms are supported for this method of adding nodes:

- baremetal
- vsphere
- none

**Supported architectures**
  The following architecture combinations have been validated to work when adding worker nodes using this process:amd64worker nodes onamd64orarm64clustersarm64worker nodes onamd64orarm64clusterss390xworker nodes ons390xclustersppc64leworker nodes onppc64leclusters

The following architecture combinations have been validated to work when adding worker nodes using this process:

- amd64worker nodes onamd64orarm64clusters
- arm64worker nodes onamd64orarm64clusters
- s390xworker nodes ons390xclusters
- ppc64leworker nodes onppc64leclusters

**Adding nodes to your cluster**
  You can add nodes with this method in the following two ways:Adding one or more nodes using a configuration file.You can specify configurations for one or more nodes in thenodes-config.yamlfile before running theoc adm node-image createcommand. This is useful if you want to add more than one node at a time, or if you are specifying complex configurations.Adding a single node using only command flags.You can add a node by running theoc adm node-image createcommand with flags to specify your configurations. This is useful if you want to add only a single node at a time, and have only simple configurations to specify for that node.

You can add nodes with this method in the following two ways:

- Adding one or more nodes using a configuration file.You can specify configurations for one or more nodes in thenodes-config.yamlfile before running theoc adm node-image createcommand. This is useful if you want to add more than one node at a time, or if you are specifying complex configurations.

Adding one or more nodes using a configuration file.

You can specify configurations for one or more nodes in thenodes-config.yamlfile before running theoc adm node-image createcommand. This is useful if you want to add more than one node at a time, or if you are specifying complex configurations.

- Adding a single node using only command flags.You can add a node by running theoc adm node-image createcommand with flags to specify your configurations. This is useful if you want to add only a single node at a time, and have only simple configurations to specify for that node.

Adding a single node using only command flags.

You can add a node by running theoc adm node-image createcommand with flags to specify your configurations. This is useful if you want to add only a single node at a time, and have only simple configurations to specify for that node.

### 6.4.1. Cluster configuration referenceCopy linkLink copied to clipboard!

When creating the ISO image, configurations are retrieved from the target cluster and are applied to the new nodes. You can override these configurations by specifying new values in either thenodes-config.yamlfile or any flags you add to theoc adm node-image createcommand before you create the ISO image.

**YAML file parameters**
  Configuration parameters that can be specified in thenodes-config.yamlfile are described in the following table:ExpandTable 6.2. nodes-config.yaml parametersParameterDescriptionValueshosts:hosts:Copy to ClipboardCopied!Toggle word wrapToggle overflowHost configuration.An array of host configuration objects.hosts:
  hostname:hosts:
  hostname:Copy to ClipboardCopied!Toggle word wrapToggle overflowHostname. Overrides the hostname obtained from either the Dynamic Host Configuration Protocol (DHCP) or a reverse DNS lookup. Each host must have a unique hostname supplied by one of these methods, although configuring a hostname through this parameter is optional.String.hosts:
  interfaces:hosts:
  interfaces:Copy to ClipboardCopied!Toggle word wrapToggle overflowProvides a table of the name and MAC address mappings for the interfaces on the host. If aNetworkConfigsection is provided in thenodes-config.yamlfile, this table must be included and the values must match the mappings provided in theNetworkConfigsection.An array of host configuration objects.hosts:
  interfaces:
    name:hosts:
  interfaces:
    name:Copy to ClipboardCopied!Toggle word wrapToggle overflowThe name of an interface on the host.String.hosts:
  interfaces:
    macAddress:hosts:
  interfaces:
    macAddress:Copy to ClipboardCopied!Toggle word wrapToggle overflowThe MAC address of an interface on the host.A MAC address such as the following example:00-B0-D0-63-C2-26.hosts:
  rootDeviceHints:hosts:
  rootDeviceHints:Copy to ClipboardCopied!Toggle word wrapToggle overflowEnables provisioning of the Red Hat Enterprise Linux CoreOS (RHCOS) image to a particular device. The node-adding tool examines the devices in the order it discovers them, and compares the discovered values with the hint values. It uses the first discovered device that matches the hint value.A dictionary of key-value pairs. For more information, see "Root device hints" in the "Setting up the environment for an OpenShift installation" page.hosts:
  rootDeviceHints:
    deviceName:hosts:
  rootDeviceHints:
    deviceName:Copy to ClipboardCopied!Toggle word wrapToggle overflowThe name of the device the RHCOS image is provisioned to.String.hosts:
  networkConfig:hosts:
  networkConfig:Copy to ClipboardCopied!Toggle word wrapToggle overflowThe host network definition. The configuration must match the Host Network Management API defined in thenmstate documentation.A dictionary of host network configuration objects.cpuArchitecturecpuArchitectureCopy to ClipboardCopied!Toggle word wrapToggle overflowOptional. Specifies the architecture of the nodes you are adding. This parameter allows you to override the default value from the cluster when required.String.sshKeysshKeyCopy to ClipboardCopied!Toggle word wrapToggle overflowOptional. The file containing the SSH key to authenticate access to your cluster machines.String.

Configuration parameters that can be specified in thenodes-config.yamlfile are described in the following table:

| Parameter | Description | Values |
| --- | --- | --- |
| hosts:hosts:Copy to ClipboardCopied!Toggle word wrapToggle overflow | Host configuration. | An array of host configuration objects. |
| hosts:
  hostname:hosts:
  hostname:Copy to ClipboardCopied!Toggle word wrapToggle overflow | Hostname. Overrides the hostname obtained from either the Dynamic Host Configuration Protocol (DHCP) | String. |
| hosts:
  interfaces:hosts:
  interfaces:Copy to ClipboardCopied!Toggle word wrapToggle overflow | Provides a table of the name and MAC address mappings for the interfaces on the host. If aNetworkCon | An array of host configuration objects. |
| hosts:
  interfaces:
    name:hosts:
  interfaces:
    name:Copy to ClipboardCopied!Toggle word wrap | The name of an interface on the host. | String. |
| hosts:
  interfaces:
    macAddress:hosts:
  interfaces:
    macAddress:Copy to ClipboardCopied!Togg | The MAC address of an interface on the host. | A MAC address such as the following example:00-B0-D0-63-C2-26. |
| hosts:
  rootDeviceHints:hosts:
  rootDeviceHints:Copy to ClipboardCopied!Toggle word wrapToggle ove | Enables provisioning of the Red Hat Enterprise Linux CoreOS (RHCOS) image to a particular device. Th | A dictionary of key-value pairs. For more information, see "Root device hints" in the "Setting up th |
| hosts:
  rootDeviceHints:
    deviceName:hosts:
  rootDeviceHints:
    deviceName:Copy to ClipboardC | The name of the device the RHCOS image is provisioned to. | String. |
| hosts:
  networkConfig:hosts:
  networkConfig:Copy to ClipboardCopied!Toggle word wrapToggle overflo | The host network definition. The configuration must match the Host Network Management API defined in | A dictionary of host network configuration objects. |
| cpuArchitecturecpuArchitectureCopy to ClipboardCopied!Toggle word wrapToggle overflow | Optional. Specifies the architecture of the nodes you are adding. This parameter allows you to overr | String. |
| sshKeysshKeyCopy to ClipboardCopied!Toggle word wrapToggle overflow | Optional. The file containing the SSH key to authenticate access to your cluster machines. | String. |

Host configuration.

An array of host configuration objects.

```
hosts:
  hostname:
```

```
hosts:
  hostname:
```

Hostname. Overrides the hostname obtained from either the Dynamic Host Configuration Protocol (DHCP) or a reverse DNS lookup. Each host must have a unique hostname supplied by one of these methods, although configuring a hostname through this parameter is optional.

String.

```
hosts:
  interfaces:
```

```
hosts:
  interfaces:
```

Provides a table of the name and MAC address mappings for the interfaces on the host. If aNetworkConfigsection is provided in thenodes-config.yamlfile, this table must be included and the values must match the mappings provided in theNetworkConfigsection.

An array of host configuration objects.

```
hosts:
  interfaces:
    name:
```

```
hosts:
  interfaces:
    name:
```

The name of an interface on the host.

String.

```
hosts:
  interfaces:
    macAddress:
```

```
hosts:
  interfaces:
    macAddress:
```

The MAC address of an interface on the host.

A MAC address such as the following example:00-B0-D0-63-C2-26.

```
hosts:
  rootDeviceHints:
```

```
hosts:
  rootDeviceHints:
```

Enables provisioning of the Red Hat Enterprise Linux CoreOS (RHCOS) image to a particular device. The node-adding tool examines the devices in the order it discovers them, and compares the discovered values with the hint values. It uses the first discovered device that matches the hint value.

A dictionary of key-value pairs. For more information, see "Root device hints" in the "Setting up the environment for an OpenShift installation" page.

```
hosts:
  rootDeviceHints:
    deviceName:
```

```
hosts:
  rootDeviceHints:
    deviceName:
```

The name of the device the RHCOS image is provisioned to.

String.

```
hosts:
  networkConfig:
```

```
hosts:
  networkConfig:
```

The host network definition. The configuration must match the Host Network Management API defined in thenmstate documentation.

A dictionary of host network configuration objects.

Optional. Specifies the architecture of the nodes you are adding. This parameter allows you to override the default value from the cluster when required.

String.

Optional. The file containing the SSH key to authenticate access to your cluster machines.

String.

**Command flag options**
  You can use command flags with theoc adm node-image createcommand to configure the nodes you are creating.The following table describes command flags that are not limited to the single-node use case:ExpandTable 6.3. General command flagsFlagDescriptionValues--certificate-authorityThe path to a certificate authority bundle to use when communicating with the managed container image registries. If the--insecureflag is used, this flag is ignored.String--dirThe path containing the configuration file, if provided. This path is also used to store the generated artifacts.String--insecureAllows push and pull operations to registries to be made over HTTP.Boolean-o,--output-nameThe name of the generated output image.String-a,--registry-configThe path to your registry credentials. Alternatively, you can specify theREGISTRY_AUTH_FILEenvironment variable. The default paths are${XDG_RUNTIME_DIR}/containers/auth.json,/run/containers/${UID}/auth.json,${XDG_CONFIG_HOME}/containers/auth.json,${DOCKER_CONFIG},~/.docker/config.json,~/.dockercfg.The order can be changed through the deprecatedREGISTRY_AUTH_PREFERENCEenvironment variable to a "docker" value, in order to prioritize Docker credentials over Podman.String--skip-verificationAn option to skip verifying the integrity of the retrieved content. This is not recommended, but might be necessary when importing images from older image registries. Bypass verification only if the registry is known to be trustworthy.BooleanThe following table describes command flags that can be used only when creating a single node:ExpandTable 6.4. Single-node only command flagsFlagDescriptionValues-c,--cpu-architectureThe CPU architecture to be used to install the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String--hostnameThe hostname to be set for the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String-m,--mac-addressThe MAC address used to identify the host to apply configurations to. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String--network-config-pathThe path to a YAML file containing NMState configurations to be applied to the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String--root-device-hintA hint for specifying the storage location for the image root filesystem. The accepted format is<hint_name>:<value>. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String-k,--ssh-key-pathThe path to the SSH key used to access the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.String

You can use command flags with theoc adm node-image createcommand to configure the nodes you are creating.

The following table describes command flags that are not limited to the single-node use case:

| Flag | Description | Values |
| --- | --- | --- |
| --certificate-authority | The path to a certificate authority bundle to use when communicating with the managed container imag | String |
| --dir | The path containing the configuration file, if provided. This path is also used to store the generat | String |
| --insecure | Allows push and pull operations to registries to be made over HTTP. | Boolean |
| -o,--output-name | The name of the generated output image. | String |
| -a,--registry-config | The path to your registry credentials. Alternatively, you can specify theREGISTRY_AUTH_FILEenvironme | String |
| --skip-verification | An option to skip verifying the integrity of the retrieved content. This is not recommended, but mig | Boolean |

--certificate-authority

The path to a certificate authority bundle to use when communicating with the managed container image registries. If the--insecureflag is used, this flag is ignored.

String

--dir

The path containing the configuration file, if provided. This path is also used to store the generated artifacts.

String

--insecure

Allows push and pull operations to registries to be made over HTTP.

Boolean

-o,--output-name

The name of the generated output image.

String

-a,--registry-config

The path to your registry credentials. Alternatively, you can specify theREGISTRY_AUTH_FILEenvironment variable. The default paths are${XDG_RUNTIME_DIR}/containers/auth.json,/run/containers/${UID}/auth.json,${XDG_CONFIG_HOME}/containers/auth.json,${DOCKER_CONFIG},~/.docker/config.json,~/.dockercfg.The order can be changed through the deprecatedREGISTRY_AUTH_PREFERENCEenvironment variable to a "docker" value, in order to prioritize Docker credentials over Podman.

String

--skip-verification

An option to skip verifying the integrity of the retrieved content. This is not recommended, but might be necessary when importing images from older image registries. Bypass verification only if the registry is known to be trustworthy.

Boolean

The following table describes command flags that can be used only when creating a single node:

| Flag | Description | Values |
| --- | --- | --- |
| -c,--cpu-architecture | The CPU architecture to be used to install the node. This flag can be used to create only a single n | String |
| --hostname | The hostname to be set for the node. This flag can be used to create only a single node, and the--ma | String |
| -m,--mac-address | The MAC address used to identify the host to apply configurations to. This flag can be used to creat | String |
| --network-config-path | The path to a YAML file containing NMState configurations to be applied to the node. This flag can b | String |
| --root-device-hint | A hint for specifying the storage location for the image root filesystem. The accepted format is<hin | String |
| -k,--ssh-key-path | The path to the SSH key used to access the node. This flag can be used to create only a single node, | String |

-c,--cpu-architecture

The CPU architecture to be used to install the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

--hostname

The hostname to be set for the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

-m,--mac-address

The MAC address used to identify the host to apply configurations to. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

--network-config-path

The path to a YAML file containing NMState configurations to be applied to the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

--root-device-hint

A hint for specifying the storage location for the image root filesystem. The accepted format is<hint_name>:<value>. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

-k,--ssh-key-path

The path to the SSH key used to access the node. This flag can be used to create only a single node, and the--mac-addressflag must be defined.

String

#### 6.4.1.1. Adding one or more nodes using a configuration fileCopy linkLink copied to clipboard!

You can add one or more nodes to your cluster by using thenodes-config.yamlfile to specify configurations for the new nodes.

Prerequisites

- You have installed the OpenShift CLI (oc)
- You have installed the Rsync utility
- You have an active connection to your target cluster
- You have a kubeconfig file available

Procedure

- Create a new YAML file that contains configurations for the nodes you are adding and is namednodes-config.yaml. You must provide a MAC address for each new node.In the following example file, two new workers are described with an initial static network configuration:Examplenodes-config.yamlfilehosts:
- hostname: extra-worker-1
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:00
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:00
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: false
- hostname: extra-worker-2
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:02
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:02
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: falsehosts:-hostname:extra-worker-1rootDeviceHints:deviceName:/dev/sdainterfaces:-macAddress:00:00:00:00:00:00name:eth0networkConfig:interfaces:-name:eth0type:ethernetstate:upmac-address:00:00:00:00:00:00ipv4:enabled:trueaddress:-ip:192.168.122.2prefix-length:23dhcp:false-hostname:extra-worker-2rootDeviceHints:deviceName:/dev/sdainterfaces:-macAddress:00:00:00:00:00:02name:eth0networkConfig:interfaces:-name:eth0type:ethernetstate:upmac-address:00:00:00:00:00:02ipv4:enabled:trueaddress:-ip:192.168.122.3prefix-length:23dhcp:falseCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a new YAML file that contains configurations for the nodes you are adding and is namednodes-config.yaml. You must provide a MAC address for each new node.

In the following example file, two new workers are described with an initial static network configuration:

Examplenodes-config.yamlfile

```
hosts:
- hostname: extra-worker-1
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:00
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:00
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: false
- hostname: extra-worker-2
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:02
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:02
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: false
```

```
hosts:
- hostname: extra-worker-1
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:00
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:00
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: false
- hostname: extra-worker-2
  rootDeviceHints:
   deviceName: /dev/sda
  interfaces:
   - macAddress: 00:00:00:00:00:02
     name: eth0
  networkConfig:
   interfaces:
     - name: eth0
       type: ethernet
       state: up
       mac-address: 00:00:00:00:00:02
       ipv4:
         enabled: true
         address:
           - ip: [REDACTED_PRIVATE_IP]
             prefix-length: 23
         dhcp: false
```

- Generate the ISO image by running the following command:oc adm node-image create$oc adm node-image createCopy to ClipboardCopied!Toggle word wrapToggle overflowIn order for thecreatecommand to fetch a release image that matches the target cluster version, you must specify a valid pull secret. You can specify the pull secret either by using the--registry-configflag or by setting theREGISTRY_AUTH_FILEenvironment variable beforehand.If the directory of thenodes-config.yamlfile is not specified by using the--dirflag, the tool looks for the file in the current directory.

Generate the ISO image by running the following command:

In order for thecreatecommand to fetch a release image that matches the target cluster version, you must specify a valid pull secret. You can specify the pull secret either by using the--registry-configflag or by setting theREGISTRY_AUTH_FILEenvironment variable beforehand.

If the directory of thenodes-config.yamlfile is not specified by using the--dirflag, the tool looks for the file in the current directory.

- Verify that a newnode.<arch>.isofile is present in the asset directory. The asset directory is your current directory, unless you specified a different one when creating the ISO image.
- Boot the selected node with the generated ISO image.
- Track progress of the node creation by running the following command:oc adm node-image monitor --ip-addresses <ip_addresses>$oc adm node-image monitor --ip-addresses<ip_addresses>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<ip_addresses>Specifies a list of the IP addresses of the nodes that are being added.If reverse DNS entries are not available for your node, theoc adm node-image monitorcommand skips checks for pending certificate signing requests (CSRs). If these checks are skipped, you must manually check for CSRs by running theoc get csrcommand.

Track progress of the node creation by running the following command:

where:

**<ip_addresses>**
  Specifies a list of the IP addresses of the nodes that are being added.If reverse DNS entries are not available for your node, theoc adm node-image monitorcommand skips checks for pending certificate signing requests (CSRs). If these checks are skipped, you must manually check for CSRs by running theoc get csrcommand.

Specifies a list of the IP addresses of the nodes that are being added.

If reverse DNS entries are not available for your node, theoc adm node-image monitorcommand skips checks for pending certificate signing requests (CSRs). If these checks are skipped, you must manually check for CSRs by running theoc get csrcommand.

- Approve the CSRs by running the following command for each CSR:oc adm certificate approve <csr_name>$oc adm certificate approve<csr_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Approve the CSRs by running the following command for each CSR:

#### 6.4.1.2. Adding a node with command flagsCopy linkLink copied to clipboard!

You can add a single node to your cluster by using command flags to specify configurations for the new node.

Prerequisites

- You have installed the OpenShift CLI (oc)
- You have installed the Rsync utility
- You have an active connection to your target cluster
- You have a kubeconfig file available

Procedure

- Generate the ISO image by running the following command. The MAC address must be specified using a command flag. See the "Cluster configuration reference" section for more flags that you can use with this command.oc adm node-image create --mac-address=<mac_address>$oc adm node-image create --mac-address=<mac_address>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<mac_address>Specifies the MAC address of the node that is being added.In order for thecreatecommand to fetch a release image that matches the target cluster version, you must specify a valid pull secret. You can specify the pull secret either by using the--registry-configflag or by setting theREGISTRY_AUTH_FILEenvironment variable beforehand.To see additional flags that can be used to configure your node, run the followingoc adm node-image create --helpcommand.

Generate the ISO image by running the following command. The MAC address must be specified using a command flag. See the "Cluster configuration reference" section for more flags that you can use with this command.

where:

**<mac_address>**
  Specifies the MAC address of the node that is being added.

In order for thecreatecommand to fetch a release image that matches the target cluster version, you must specify a valid pull secret. You can specify the pull secret either by using the--registry-configflag or by setting theREGISTRY_AUTH_FILEenvironment variable beforehand.

To see additional flags that can be used to configure your node, run the followingoc adm node-image create --helpcommand.

- Verify that a newnode.<arch>.isofile is present in the asset directory. The asset directory is your current directory, unless you specified a different one when creating the ISO image.
- Boot the node with the generated ISO image.
- Track progress of the node creation by running the following command:oc adm node-image monitor --ip-addresses <ip_address>$oc adm node-image monitor --ip-addresses<ip_address>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<ip_address>Specifies a list of the IP addresses of the nodes that are being added.If reverse DNS entries are not available for your node, theoc adm node-image monitorcommand skips checks for pending certificate signing requests (CSRs). If these checks are skipped, you must manually check for CSRs by running theoc get csrcommand.

Track progress of the node creation by running the following command:

where:

**<ip_address>**
  Specifies a list of the IP addresses of the nodes that are being added.

If reverse DNS entries are not available for your node, theoc adm node-image monitorcommand skips checks for pending certificate signing requests (CSRs). If these checks are skipped, you must manually check for CSRs by running theoc get csrcommand.

- Approve the pending CSRs by running the following command for each CSR:oc adm certificate approve <csr_name>$oc adm certificate approve<csr_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Approve the pending CSRs by running the following command for each CSR:

## 6.5. Managing the maximum number of pods per nodeCopy linkLink copied to clipboard!

In OpenShift Container Platform, you can configure the number of pods that can run on a node based on the number of processor cores on the node, a hard limit, or both. If you use both options, the lower of the two limits the number of pods on a node. Setting a maximum number of pods can prevent a node from running more pods than its underlying hardware can handle.

When both options are in use, the lower of the two values limits the number of pods on a node. Exceeding these values can result in the following conditions:

- Increased CPU utilization.
- Slow pod scheduling.
- Potential out-of-memory scenarios, depending on the amount of memory in the node.
- Exhausting the pool of IP addresses.
- Resource overcommitting, leading to poor user application performance.

In Kubernetes, a pod that is holding a single container actually uses two containers. The second container is used to set up networking prior to the actual container starting. Therefore, a system running 10 pods will actually have 20 containers running.

Disk IOPS throttling from the cloud provider might have an impact on CRI-O and kubelet. They might get overloaded when there are large number of I/O intensive pods running on the nodes. It is recommended that you monitor the disk I/O on the nodes and use volumes with sufficient throughput for the workload.

ThepodsPerCoreparameter sets the number of pods that the node can run based on the number of processor cores on the node. For example, ifpodsPerCoreis set to10on a node with 4 processor cores, the maximum number of pods allowed on the node is40.

```
kubeletConfig:
  podsPerCore: 10
```

```
kubeletConfig:
  podsPerCore: 10
```

SettingpodsPerCoreto0disables this limit. The default is0. The value of thepodsPerCoreparameter cannot exceed the value of themaxPodsparameter.

ThemaxPodsparameter sets the number of pods that the node can run to a fixed value, regardless of the properties of the node.

```
kubeletConfig:
    maxPods: 250
```

```
kubeletConfig:
    maxPods: 250
```

### 6.5.1. Configuring the maximum number of pods per nodeCopy linkLink copied to clipboard!

You can use thepodsPerCoreandmaxPodsparameters in a kublet configuration to control the maximum number of pods that can be scheduled to a node. If you use both options, the lower of the two limits the number of pods on a node. Setting an appropriate maximum can help ensure your nodes run efficiently.

For example, ifpodsPerCoreis set to10on a node with 4 processor cores, the maximum number of pods allowed on the node will be 40.

Prerequisites

- You have the label associated with the staticMachineConfigPoolCRD for the type of node you want to configure.

Procedure

- Create a custom resource (CR) for your configuration change.Sample configuration for amax-podsCRapiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-max-pods
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:set-max-podsspec:machineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""kubeletConfig:podsPerCore:10maxPods:250#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies a name for the CR.spec.machineConfigPoolSelector.matchLabelsSpecifies the label from the machine config pool.spec.kubeletConfig.podsPerCoreSpecifies the number of pods the node can run based on the number of processor cores on the node.spec.kubeletConfig.maxPodsSpecifies the number of pods the node can run to a fixed value, regardless of the properties of the node.SettingpodsPerCoreto0disables this limit.In the above example, the default value forpodsPerCoreis10and the default value formaxPodsis250. This means that unless the node has 25 cores or more, by default,podsPerCorewill be the limiting factor.

Create a custom resource (CR) for your configuration change.

Sample configuration for amax-podsCR

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-max-pods
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-max-pods
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    podsPerCore: 10
    maxPods: 250
#...
```

where:

**metadata.name**
  Specifies a name for the CR.

**spec.machineConfigPoolSelector.matchLabels**
  Specifies the label from the machine config pool.

**spec.kubeletConfig.podsPerCore**
  Specifies the number of pods the node can run based on the number of processor cores on the node.

**spec.kubeletConfig.maxPods**
  Specifies the number of pods the node can run to a fixed value, regardless of the properties of the node.SettingpodsPerCoreto0disables this limit.In the above example, the default value forpodsPerCoreis10and the default value formaxPodsis250. This means that unless the node has 25 cores or more, by default,podsPerCorewill be the limiting factor.

Specifies the number of pods the node can run to a fixed value, regardless of the properties of the node.

SettingpodsPerCoreto0disables this limit.

In the above example, the default value forpodsPerCoreis10and the default value formaxPodsis250. This means that unless the node has 25 cores or more, by default,podsPerCorewill be the limiting factor.

- Run the following command to create the CR:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to create the CR:

Verification

- List theMachineConfigPoolCRDs to check if the change is applied. TheUPDATINGcolumn reportsTrueif the change is picked up by the Machine Config Controller:oc get machineconfigpools$oc get machineconfigpoolsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     False      False
worker   worker-8cecd1236b33ee3f8a5e   False     True       FalseNAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     False      False
worker   worker-8cecd1236b33ee3f8a5e   False     True       FalseCopy to ClipboardCopied!Toggle word wrapToggle overflowAfter the change is complete, theUPDATEDcolumn reportsTrue.oc get machineconfigpools$oc get machineconfigpoolsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     True       False
worker   worker-8cecd1236b33ee3f8a5e   True      False      FalseNAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     True       False
worker   worker-8cecd1236b33ee3f8a5e   True      False      FalseCopy to ClipboardCopied!Toggle word wrapToggle overflow

List theMachineConfigPoolCRDs to check if the change is applied. TheUPDATINGcolumn reportsTrueif the change is picked up by the Machine Config Controller:

Example output

```
NAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     False      False
worker   worker-8cecd1236b33ee3f8a5e   False     True       False
```

```
NAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     False      False
worker   worker-8cecd1236b33ee3f8a5e   False     True       False
```

After the change is complete, theUPDATEDcolumn reportsTrue.

Example output

```
NAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     True       False
worker   worker-8cecd1236b33ee3f8a5e   True      False      False
```

```
NAME     CONFIG                        UPDATED   UPDATING   DEGRADED
master   master-9cc2c72f205e103bb534   False     True       False
worker   worker-8cecd1236b33ee3f8a5e   True      False      False
```

## 6.6. Using the Node Tuning OperatorCopy linkLink copied to clipboard!

The Node Tuning Operator in OpenShift Container Platform helps you manage node-level tuning by orchestrating the TuneD daemon. You can use this unified interface to apply custom tuning specifications and achieve low latency performance for high-performance applications.

The Node Tuning Operator helps you manage node-level tuning by orchestrating the TuneD daemon and achieves low latency performance by using the Performance Profile controller. The majority of high-performance applications require some level of kernel tuning. The Node Tuning Operator provides a unified management interface to users of node-level sysctls and more flexibility to add custom tuning specified by user needs.

The Operator manages the containerized TuneD daemon for OpenShift Container Platform as a Kubernetes daemon set. It ensures the custom tuning specification is passed to all containerized TuneD daemons running in the cluster in the format that the daemons understand. The daemons run on all nodes in the cluster, one per node.

Node-level settings applied by the containerized TuneD daemon are rolled back on an event that triggers a profile change or when the containerized TuneD daemon is terminated gracefully by receiving and handling a termination signal.

The Node Tuning Operator uses the Performance Profile controller to implement automatic tuning to achieve low latency performance for OpenShift Container Platform applications.

The cluster administrator configures a performance profile to define node-level settings such as the following:

- Updating the kernel to kernel-rt.
- Choosing CPUs for housekeeping.
- Choosing CPUs for running workloads.

The Node Tuning Operator is part of a standard OpenShift Container Platform installation in version 4.1 and later.

In earlier versions of OpenShift Container Platform, the Performance Addon Operator was used to implement automatic tuning to achieve low latency performance for OpenShift applications. In OpenShift Container Platform 4.11 and later, this functionality is part of the Node Tuning Operator.

### 6.6.1. Accessing an example Node Tuning Operator specificationCopy linkLink copied to clipboard!

Use this process to access an example Node Tuning Operator specification.

Procedure

- Run the following command to access an example Node Tuning Operator specification:oc get tuned.tuned.openshift.io/default -o yaml -n openshift-cluster-node-tuning-operatoroc get tuned.tuned.openshift.io/default -o yaml -n openshift-cluster-node-tuning-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to access an example Node Tuning Operator specification:

The default CR is meant for delivering standard node-level tuning for the OpenShift Container Platform platform and it can only be modified to set the Operator Management state. Any other custom changes to the default CR will be overwritten by the Operator. For custom tuning, create your own Tuned CRs. Newly created CRs will be combined with the default CR and custom tuning applied to OpenShift Container Platform nodes based on node or pod labels and profile priorities.

While in certain situations the support for pod labels can be a convenient way of automatically delivering required tuning, this practice is discouraged and strongly advised against, especially in large-scale clusters. The default Tuned CR ships without pod label matching. If a custom profile is created with pod label matching, then the functionality will be enabled at that time. The pod label functionality will be deprecated in future versions of the Node Tuning Operator.

### 6.6.2. Custom tuning specificationCopy linkLink copied to clipboard!

The custom resource (CR) for the Operator has two major sections. The first section,profile:, is a list of TuneD profiles and their names. The second,recommend:, defines the profile selection logic.

Multiple custom tuning specifications can co-exist as multiple CRs in the Operator’s namespace. The existence of new CRs or the deletion of old CRs is detected by the Operator. All existing custom tuning specifications are merged and appropriate objects for the containerized TuneD daemons are updated.

Management state

The Operator Management state is set by adjusting the default Tuned CR. By default, the Operator is in the Managed state and thespec.managementStatefield is not present in the default Tuned CR. Valid values for the Operator Management state are as follows:

- Managed: the Operator will update its operands as configuration resources are updated
- Unmanaged: the Operator will ignore changes to the configuration resources
- Removed: the Operator will remove its operands and resources the Operator provisioned

Profile data

Theprofile:section lists TuneD profiles and their names.

```
profile:
- name: tuned_profile_1
  data: |
    # TuneD profile specification
    [main]
    summary=Description of tuned_profile_1 profile

    [sysctl]
    net.ipv4.ip_forward=1
    # ... other sysctl's or other TuneD daemon plugins supported by the containerized TuneD

# ...

- name: tuned_profile_n
  data: |
    # TuneD profile specification
    [main]
    summary=Description of tuned_profile_n profile

    # tuned_profile_n profile settings
```

```
profile:
- name: tuned_profile_1
  data: |
    # TuneD profile specification
    [main]
    summary=Description of tuned_profile_1 profile

    [sysctl]
    net.ipv4.ip_forward=1
    # ... other sysctl's or other TuneD daemon plugins supported by the containerized TuneD

# ...

- name: tuned_profile_n
  data: |
    # TuneD profile specification
    [main]
    summary=Description of tuned_profile_n profile

    # tuned_profile_n profile settings
```

Recommended profiles

Theprofile:selection logic is defined by therecommend:section of the CR. Therecommend:section is a list of items to recommend the profiles based on a selection criteria.

```
recommend:
<recommend-item-1>
# ...
<recommend-item-n>
```

```
recommend:
<recommend-item-1>
# ...
<recommend-item-n>
```

The individual items of the list:

```
- machineConfigLabels: 
    <mcLabels> 
  match: 
    <match> 
  priority: <priority> 
  profile: <tuned_profile_name> 
  operand: 
    debug: <bool> 
    tunedConfig:
      reapply_sysctl: <bool>
```

```
<mcLabels>
```

```
match:
```

```
<match>
```

```
priority: <priority>
```

```
profile: <tuned_profile_name>
```

```
operand:
```

```
debug: <bool>
```

```
tunedConfig:
      reapply_sysctl: <bool>
```

**1**
  Optional.

**2**
  A dictionary of key/valueMachineConfiglabels. The keys must be unique.

**3**
  If omitted, profile match is assumed unless a profile with a higher priority matches first ormachineConfigLabelsis set.

**4**
  An optional list.

**5**
  Profile ordering priority. Lower numbers mean higher priority (0is the highest priority).

**6**
  A TuneD profile to apply on a match. For exampletuned_profile_1.

**7**
  Optional operand configuration.

**8**
  Turn debugging on or off for the TuneD daemon. Options aretruefor on orfalsefor off. The default isfalse.

**9**
  Turnreapply_sysctlfunctionality on or off for the TuneD daemon. Options aretruefor on andfalsefor off.

<match>is an optional list recursively defined as follows:

```
- label: <label_name> 
  value: <label_value> 
  type: <label_type> 
    <match>
```

```
value: <label_value>
```

```
type: <label_type>
```

```
<match>
```

**1**
  Node or pod label name.

**2**
  Optional node or pod label value. If omitted, the presence of<label_name>is enough to match.

**3**
  Optional object type (nodeorpod). If omitted,nodeis assumed.

**4**
  An optional<match>list.

If<match>is not omitted, all nested<match>sections must also evaluate totrue. Otherwise,falseis assumed and the profile with the respective<match>section will not be applied or recommended. Therefore, the nesting (child<match>sections) works as logical AND operator. Conversely, if any item of the<match>list matches, the entire<match>list evaluates totrue. Therefore, the list acts as logical OR operator.

IfmachineConfigLabelsis defined, machine config pool based matching is turned on for the givenrecommend:list item.<mcLabels>specifies the labels for a machine config. The machine config is created automatically to apply host settings, such as kernel boot parameters, for the profile<tuned_profile_name>. This involves finding all machine config pools with machine config selector matching<mcLabels>and setting the profile<tuned_profile_name>on all nodes that are assigned the found machine config pools. To target nodes that have both master and worker roles, you must use the master role.

The list itemsmatchandmachineConfigLabelsare connected by the logical OR operator. Thematchitem is evaluated first in a short-circuit manner. Therefore, if it evaluates totrue, themachineConfigLabelsitem is not considered.

When using machine config pool based matching, it is advised to group nodes with the same hardware configuration into the same machine config pool. Not following this practice might result in TuneD operands calculating conflicting kernel parameters for two or more nodes sharing the same machine config pool.

Example: Node or pod label based matching

```
- match:
  - label: tuned.openshift.io/elasticsearch
    match:
    - label: node-role.kubernetes.io/master
    - label: node-role.kubernetes.io/infra
    type: pod
  priority: 10
  profile: openshift-control-plane-es
- match:
  - label: node-role.kubernetes.io/master
  - label: node-role.kubernetes.io/infra
  priority: 20
  profile: openshift-control-plane
- priority: 30
  profile: openshift-node
```

```
- match:
  - label: tuned.openshift.io/elasticsearch
    match:
    - label: node-role.kubernetes.io/master
    - label: node-role.kubernetes.io/infra
    type: pod
  priority: 10
  profile: openshift-control-plane-es
- match:
  - label: node-role.kubernetes.io/master
  - label: node-role.kubernetes.io/infra
  priority: 20
  profile: openshift-control-plane
- priority: 30
  profile: openshift-node
```

The CR above is translated for the containerized TuneD daemon into itsrecommend.conffile based on the profile priorities. The profile with the highest priority (10) isopenshift-control-plane-esand, therefore, it is considered first. The containerized TuneD daemon running on a given node looks to see if there is a pod running on the same node with thetuned.openshift.io/elasticsearchlabel set. If not, the entire<match>section evaluates asfalse. If there is such a pod with the label, in order for the<match>section to evaluate totrue, the node label also needs to benode-role.kubernetes.io/masterornode-role.kubernetes.io/infra.

If the labels for the profile with priority10matched,openshift-control-plane-esprofile is applied and no other profile is considered. If the node/pod label combination did not match, the second highest priority profile (openshift-control-plane) is considered. This profile is applied if the containerized TuneD pod runs on a node with labelsnode-role.kubernetes.io/masterornode-role.kubernetes.io/infra.

Finally, the profileopenshift-nodehas the lowest priority of30. It lacks the<match>section and, therefore, will always match. It acts as a profile catch-all to setopenshift-nodeprofile, if no other profile with higher priority matches on a given node.

Example: Machine config pool based matching

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: openshift-node-custom
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=Custom OpenShift node profile with an additional kernel parameter
      include=openshift-node
      [bootloader]
      cmdline_openshift_node_custom=+skew_tick=1
    name: openshift-node-custom

  recommend:
  - machineConfigLabels:
      machineconfiguration.openshift.io/role: "worker-custom"
    priority: 20
    profile: openshift-node-custom
```

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: openshift-node-custom
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=Custom OpenShift node profile with an additional kernel parameter
      include=openshift-node
      [bootloader]
      cmdline_openshift_node_custom=+skew_tick=1
    name: openshift-node-custom

  recommend:
  - machineConfigLabels:
      machineconfiguration.openshift.io/role: "worker-custom"
    priority: 20
    profile: openshift-node-custom
```

To minimize node reboots, label the target nodes with a label the machine config pool’s node selector will match, then create the Tuned CR above and finally create the custom machine config pool itself.

Cloud provider-specific TuneD profiles

With this functionality, all Cloud provider-specific nodes can conveniently be assigned a TuneD profile specifically tailored to a given Cloud provider on a OpenShift Container Platform cluster. This can be accomplished without adding additional node labels or grouping nodes into machine config pools.

This functionality takes advantage ofspec.providerIDnode object values in the form of<cloud-provider>://<cloud-provider-specific-id>and writes the file/var/lib/ocp-tuned/providerwith the value<cloud-provider>in NTO operand containers. The content of this file is then used by TuneD to loadprovider-<cloud-provider>profile if such profile exists.

Theopenshiftprofile that bothopenshift-control-planeandopenshift-nodeprofiles inherit settings from is now updated to use this functionality through the use of conditional profile loading. Neither NTO nor TuneD currently include any Cloud provider-specific profiles. However, it is possible to create a custom profileprovider-<cloud-provider>that will be applied to all Cloud provider-specific cluster nodes.

Example GCE Cloud provider profile

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: provider-gce
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=GCE Cloud provider-specific profile
      # Your tuning for GCE Cloud provider goes here.
    name: provider-gce
```

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: provider-gce
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=GCE Cloud provider-specific profile
      # Your tuning for GCE Cloud provider goes here.
    name: provider-gce
```

Due to profile inheritance, any setting specified in theprovider-<cloud-provider>profile will be overwritten by theopenshiftprofile and its child profiles.

### 6.6.3. Default profiles set on a clusterCopy linkLink copied to clipboard!

The following are the default profiles set on a cluster.

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: default
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=Optimize systems running OpenShift (provider specific parent profile)
      include=-provider-${f:exec:cat:/var/lib/ocp-tuned/provider},openshift
    name: openshift
  recommend:
  - profile: openshift-control-plane
    priority: 30
    match:
    - label: node-role.kubernetes.io/master
    - label: node-role.kubernetes.io/infra
  - profile: openshift-node
    priority: 40
```

```
apiVersion: tuned.openshift.io/v1
kind: Tuned
metadata:
  name: default
  namespace: openshift-cluster-node-tuning-operator
spec:
  profile:
  - data: |
      [main]
      summary=Optimize systems running OpenShift (provider specific parent profile)
      include=-provider-${f:exec:cat:/var/lib/ocp-tuned/provider},openshift
    name: openshift
  recommend:
  - profile: openshift-control-plane
    priority: 30
    match:
    - label: node-role.kubernetes.io/master
    - label: node-role.kubernetes.io/infra
  - profile: openshift-node
    priority: 40
```

Starting with OpenShift Container Platform 4.9, all OpenShift TuneD profiles are shipped with the TuneD package. You can use theoc execcommand to view the contents of these profiles:

### 6.6.4. Supported TuneD daemon pluginsCopy linkLink copied to clipboard!

Excluding the[main]section, the following TuneD plugins are supported when using custom profiles defined in theprofile:section of the Tuned CR:

- audio
- cpu
- disk
- eeepc_she
- modules
- mounts
- net
- scheduler
- scsi_host
- selinux
- sysctl
- sysfs
- usb
- video
- vm
- bootloader

There is some dynamic tuning functionality provided by some of these plugins that is not supported. The following TuneD plugins are currently not supported:

- script
- systemd

The TuneD bootloader plugin only supports Red Hat Enterprise Linux CoreOS (RHCOS) worker nodes.

Additional resources

- Available TuneD Plugins
- Getting Started with TuneD

## 6.7. Remediating, fencing, and maintaining nodesCopy linkLink copied to clipboard!

When node-level failures occur, due to issues such as kernel hangs or network issues, it is important to isolate the node, known asfencing, before initiating recovery of the workload, known asremediation, and then you can attempt to recover the node.

During node failures, the work required from the cluster does not decrease and workloads from affected nodes need to be restarted somewhere. Failures affecting these workloads risk data loss, corruption, or both.

For more information on remediation, fencing, and maintaining nodes, see theWorkload Availability for Red Hat OpenShiftdocumentation.

## 6.8. Understanding node rebootingCopy linkLink copied to clipboard!

Review the following information to learn about rebooting a node without causing an outage for applications running on the platform by first evacuating the pods on the node.

For pods that are made highly available by the routing tier, nothing else needs to be done. For other pods needing storage, typically databases, it is critical to ensure that they can remain in operation with one pod temporarily going offline. While implementing resiliency for stateful pods is different for each application, in all cases it is important to configure the scheduler to use node anti-affinity to ensure that the pods are properly spread across available nodes.

Another challenge is how to handle nodes that are running critical infrastructure such as the router or the registry. The same node evacuation process applies, though it is important to understand certain edge cases.

### 6.8.1. About rebooting nodes running critical infrastructureCopy linkLink copied to clipboard!

When rebooting nodes that host critical OpenShift Container Platform infrastructure components, such as router pods, registry pods, and monitoring pods, ensure that there are at least three nodes available to run these components.

The following scenario demonstrates how service interruptions can occur with applications running on OpenShift Container Platform when only two nodes are available:

- Node A is marked unschedulable and all pods are evacuated.
- The registry pod running on that node is now redeployed on node B. Node B is now running both registry pods.
- Node B is now marked unschedulable and is evacuated.
- The service exposing the two pod endpoints on node B loses all endpoints, for a brief period of time, until they are redeployed to node A.

When using three nodes for infrastructure components, this process does not result in a service disruption. However, due to pod scheduling, the last node that is evacuated and brought back into rotation does not have a registry pod. One of the other nodes has two registry pods. To schedule the third registry pod on the last node, use pod anti-affinity to prevent the scheduler from locating two registry pods on the same node.

### 6.8.2. Rebooting a node using pod anti-affinityCopy linkLink copied to clipboard!

You can use pod anti-affinity to spread the workloads on a node to other nodes before performing a graceful node restart.

Pod anti-affinity is slightly different from node anti-affinity. Node anti-affinity can be violated if there are no other suitable locations to deploy a pod. Pod anti-affinity can be set to either required or preferred.

With this in place, if only two infrastructure nodes are available and one is rebooted, the container image registry pod is prevented from running on the other node.oc get podsreports the pod as unready until a suitable node is available. Once a node is available and all pods are back in ready state, the next node can be restarted.

The following procedure demonstrates how to reboot a node by using pod anti-affinity.

Procedure

- Edit the node specification to configure pod anti-affinity:apiVersion: v1
kind: Pod
metadata:
  name: with-pod-antiaffinity
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: registry
              operator: In
              values:
              - default
          topologyKey: kubernetes.io/hostname
#...apiVersion:v1kind:Podmetadata:name:with-pod-antiaffinityspec:affinity:podAntiAffinity:preferredDuringSchedulingIgnoredDuringExecution:-weight:100podAffinityTerm:labelSelector:matchExpressions:-key:registryoperator:Invalues:-defaulttopologyKey:kubernetes.io/hostname#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.affinity.podAntiAffinitySpecifies the stanza to configure pod anti-affinity.spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecutionSpecifies a preferred rule.spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.weightSpecifies a weight for a preferred rule. The node with the highest weight is preferred.spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.podAffinityTerm.labelSelector.matchExpressions.keySpecifies a pod label that determines when the anti-affinity rule applies. Define a key and value for the label.spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.podAffinityTerm.labelSelector.matchExpressions.operatorSpecifies the relationship between the label on the existing pod and the set of values in thematchExpressionparameters in the specification for the new pod. Can beIn,NotIn,Exists, orDoesNotExist.This example assumes the container image registry pod has a label ofregistry=default. Pod anti-affinity can use any Kubernetes match expression.

Edit the node specification to configure pod anti-affinity:

```
apiVersion: v1
kind: Pod
metadata:
  name: with-pod-antiaffinity
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: registry
              operator: In
              values:
              - default
          topologyKey: kubernetes.io/hostname
#...
```

```
apiVersion: v1
kind: Pod
metadata:
  name: with-pod-antiaffinity
spec:
  affinity:
    podAntiAffinity:
      preferredDuringSchedulingIgnoredDuringExecution:
      - weight: 100
        podAffinityTerm:
          labelSelector:
            matchExpressions:
            - key: registry
              operator: In
              values:
              - default
          topologyKey: kubernetes.io/hostname
#...
```

where:

**spec.affinity.podAntiAffinity**
  Specifies the stanza to configure pod anti-affinity.

**spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution**
  Specifies a preferred rule.

**spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.weight**
  Specifies a weight for a preferred rule. The node with the highest weight is preferred.

**spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.podAffinityTerm.labelSelector.matchExpressions.key**
  Specifies a pod label that determines when the anti-affinity rule applies. Define a key and value for the label.

**spec.affinity.podAntiAffinity.preferredDuringSchedulingIgnoredDuringExecution.podAffinityTerm.labelSelector.matchExpressions.operator**
  Specifies the relationship between the label on the existing pod and the set of values in thematchExpressionparameters in the specification for the new pod. Can beIn,NotIn,Exists, orDoesNotExist.This example assumes the container image registry pod has a label ofregistry=default. Pod anti-affinity can use any Kubernetes match expression.

Specifies the relationship between the label on the existing pod and the set of values in thematchExpressionparameters in the specification for the new pod. Can beIn,NotIn,Exists, orDoesNotExist.

This example assumes the container image registry pod has a label ofregistry=default. Pod anti-affinity can use any Kubernetes match expression.

- Enable theMatchInterPodAffinityscheduler predicate in the scheduling policy file.
- Perform a graceful restart of the node.

### 6.8.3. Understanding how to reboot nodes running routersCopy linkLink copied to clipboard!

Review the following information to learn how to reboot a node that hosts a router pod.

In most cases, a pod running an OpenShift Container Platform router exposes a host port.

ThePodFitsPortsscheduler predicate ensures that no router pods using the same port can run on the same node, and pod anti-affinity is achieved. If the routers are relying on IP failover for high availability, there is nothing else that is needed.

For router pods relying on an external service such as AWS Elastic Load Balancing for high availability, it is that service’s responsibility to react to router pod restarts.

In rare cases, a router pod may not have a host port configured. In those cases, it is important to follow the recommended restart process for infrastructure nodes.

### 6.8.4. Rebooting a node gracefullyCopy linkLink copied to clipboard!

You can perform a graceful restart of a node, where all workloads are moved to other nodes, without data loss or service disruption.

Before rebooting a node, it is recommended to backup etcd data to avoid any data loss on the node.

For single-node OpenShift clusters that require users to perform theoc logincommand rather than having the certificates inkubeconfigfile to manage the cluster, theoc admcommands might not be available after cordoning and draining the node. This is because theopenshift-oauth-apiserverpod is not running due to the cordon. You can use SSH to access the nodes as indicated in the following procedure.

In a single-node OpenShift cluster, pods cannot be rescheduled when cordoning and draining. However, doing so gives the pods, especially your workload pods, time to properly stop and release associated resources.

The following procedure demonstrates how to perform a graceful restart of a node.

Procedure

- Mark the node as unschedulable:oc adm cordon <node1>$oc adm cordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the node as unschedulable:

- Drain the node to remove all the running pods:oc adm drain <node1> --ignore-daemonsets --delete-emptydir-data --force$oc adm drain<node1>--ignore-daemonsets --delete-emptydir-data--forceCopy to ClipboardCopied!Toggle word wrapToggle overflowYou might receive errors that pods associated with custom pod disruption budgets (PDB) cannot be evicted.Example errorerror when evicting pods/"rails-postgresql-example-1-72v2w" -n "rails" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.error when evicting pods/"rails-postgresql-example-1-72v2w" -n "rails" (will retry after 5s): Cannot evict pod as it would violate the pod's disruption budget.Copy to ClipboardCopied!Toggle word wrapToggle overflowIn this case, run the drain command again, adding thedisable-evictionflag, which bypasses the PDB checks:oc adm drain <node1> --ignore-daemonsets --delete-emptydir-data --force --disable-eviction$oc adm drain<node1>--ignore-daemonsets --delete-emptydir-data--force--disable-evictionCopy to ClipboardCopied!Toggle word wrapToggle overflow

Drain the node to remove all the running pods:

You might receive errors that pods associated with custom pod disruption budgets (PDB) cannot be evicted.

Example error

In this case, run the drain command again, adding thedisable-evictionflag, which bypasses the PDB checks:

- Access the node in debug mode:oc debug node/<node1>$oc debug node/<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Access the node in debug mode:

- Change your root directory to/host:chroot /host$chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Change your root directory to/host:

- Restart the node:systemctl reboot$systemctlrebootCopy to ClipboardCopied!Toggle word wrapToggle overflowIn a moment, the node enters theNotReadystate.With some single-node OpenShift clusters, theoccommands might not be available after you cordon and drain the node because theopenshift-oauth-apiserverpod is not running. You can use SSH to connect to the node and perform the reboot.ssh core@<master-node>.<cluster_name>.<base_domain>$sshcore@<master-node>.<cluster_name>.<base_domain>Copy to ClipboardCopied!Toggle word wrapToggle overflowsudo systemctl reboot$sudosystemctlrebootCopy to ClipboardCopied!Toggle word wrapToggle overflow

Restart the node:

In a moment, the node enters theNotReadystate.

With some single-node OpenShift clusters, theoccommands might not be available after you cordon and drain the node because theopenshift-oauth-apiserverpod is not running. You can use SSH to connect to the node and perform the reboot.

- After the reboot is complete, mark the node as schedulable by running the following command:oc adm uncordon <node1>$oc adm uncordon<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowWith some single-node OpenShift clusters, theoccommands might not be available after you cordon and drain the node because theopenshift-oauth-apiserverpod is not running. You can use SSH to connect to the node and uncordon it.ssh core@<target_node>$sshcore@<target_node>Copy to ClipboardCopied!Toggle word wrapToggle overflowsudo oc adm uncordon <node> --kubeconfig /etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost.kubeconfig$sudooc adm uncordon<node>--kubeconfig/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigs/localhost.kubeconfigCopy to ClipboardCopied!Toggle word wrapToggle overflow

After the reboot is complete, mark the node as schedulable by running the following command:

With some single-node OpenShift clusters, theoccommands might not be available after you cordon and drain the node because theopenshift-oauth-apiserverpod is not running. You can use SSH to connect to the node and uncordon it.

- Verify that the node is ready:oc get node <node1>$oc getnode<node1>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME    STATUS  ROLES    AGE     VERSION
<node1> Ready   worker   6d22h   v1.18.3+b0068a8NAME    STATUS  ROLES    AGE     VERSION
<node1> Ready   worker   6d22h   v1.18.3+b0068a8Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the node is ready:

Example output

```
NAME    STATUS  ROLES    AGE     VERSION
<node1> Ready   worker   6d22h   v1.18.3+b0068a8
```

```
NAME    STATUS  ROLES    AGE     VERSION
<node1> Ready   worker   6d22h   v1.18.3+b0068a8
```

## 6.9. Freeing node resources using garbage collectionCopy linkLink copied to clipboard!

As an administrator, you can use OpenShift Container Platform to ensure that your nodes are running efficiently by freeing up resources through garbage collection.

The OpenShift Container Platform node performs two types of garbage collection:

- Container garbage collection: Removes terminated containers.
- Image garbage collection: Removes images not referenced by any running pods.

### 6.9.1. Understanding how terminated containers are removed through garbage collectionCopy linkLink copied to clipboard!

You can help ensure that your nodes are running efficiently by using container garbage collection to remove terminated containers.

When eviction thresholds are set for garbage collection, the node tries to keep any container for any pod accessible from the API. If the pod has been deleted, the containers will be as well. Containers are preserved as long the pod is not deleted and the eviction threshold is not reached. If the node is under disk pressure, it will remove containers and their logs will no longer be accessible usingoc logs.

- eviction-soft- A soft eviction threshold pairs an eviction threshold with a required administrator-specified grace period.
- eviction-hard- A hard eviction threshold has no grace period, and if observed, OpenShift Container Platform takes immediate action.

The following table lists the eviction thresholds:

| Node condition | Eviction signal | Description |
| --- | --- | --- |
| MemoryPressure | memory.available | The available memory on the node. |
| DiskPressure | nodefs.availablenodefs.inodesFreeimagefs.availableimagefs.inodesFree | The available disk space or inodes on the node root file system,nodefs, or image file system,imagefs |

MemoryPressure

memory.available

The available memory on the node.

DiskPressure

- nodefs.available
- nodefs.inodesFree
- imagefs.available
- imagefs.inodesFree

The available disk space or inodes on the node root file system,nodefs, or image file system,imagefs.

ForevictionHardyou must specify all of these parameters. If you do not specify all parameters, only the specified parameters are applied and the garbage collection will not function properly.

If a node is oscillating above and below a soft eviction threshold, but not exceeding its associated grace period, the corresponding node would constantly oscillate betweentrueandfalse. As a consequence, the scheduler could make poor scheduling decisions.

To protect against this oscillation, use theevictionpressure-transition-periodflag to control how long OpenShift Container Platform must wait before transitioning out of a pressure condition. OpenShift Container Platform will not set an eviction threshold as being met for the specified pressure condition for the period specified before toggling the condition back to false.

Setting theevictionPressureTransitionPeriodparameter to0configures the default value of 5 minutes. You cannot set an eviction pressure transition period to zero seconds.

### 6.9.2. Understanding how images are removed through garbage collectionCopy linkLink copied to clipboard!

You can help ensure that your nodes are running efficiently by using image garbage collection to removes images that are not referenced by any running pods.

OpenShift Container Platform determines which images to remove from a node based on the disk usage that is reported bycAdvisor.

The policy for image garbage collection is based on two conditions:

- The percent of disk usage (expressed as an integer) which triggers image garbage collection. The default is85.
- The percent of disk usage (expressed as an integer) to which image garbage collection attempts to free. Default is80.

For image garbage collection, you can modify any of the following variables using a custom resource.

| Setting | Description |
| --- | --- |
| imageMinimumGCAge | The minimum age for an unused image before the image is removed by garbage collection. The default i |
| imageGCHighThresholdPercent | The percent of disk usage, expressed as an integer, which triggers image garbage collection. The def |
| imageGCLowThresholdPercent | The percent of disk usage, expressed as an integer, to which image garbage collection attempts to fr |

imageMinimumGCAge

The minimum age for an unused image before the image is removed by garbage collection. The default is2m.

imageGCHighThresholdPercent

The percent of disk usage, expressed as an integer, which triggers image garbage collection. The default is85. This value must be greater than theimageGCLowThresholdPercentvalue.

imageGCLowThresholdPercent

The percent of disk usage, expressed as an integer, to which image garbage collection attempts to free. The default is80. This value must be less than theimageGCHighThresholdPercentvalue.

Two lists of images are retrieved in each garbage collector run:

- A list of images currently running in at least one pod.
- A list of images available on a host.

As new containers are run, new images appear. All images are marked with a time stamp. If the image is running (the first list above) or is newly detected (the second list above), it is marked with the current time. The remaining images are already marked from the previous spins. All images are then sorted by the time stamp.

Once the collection starts, the oldest images get deleted first until the stopping criterion is met.

### 6.9.3. Configuring garbage collection for containers and imagesCopy linkLink copied to clipboard!

As an administrator, you can configure how OpenShift Container Platform performs garbage collection by creating akubeletConfigobject for each machine config pool. Performing garbage collection helps ensure that your nodes are running efficiently.

OpenShift Container Platform supports only onekubeletConfigobject for each machine config pool.

You can configure any combination of the following:

- Soft eviction for containers
- Hard eviction for containers
- Eviction for images

Container garbage collection removes terminated containers. Image garbage collection removes images that are not referenced by any running pods.

Prerequisites

- Obtain the label associated with the staticMachineConfigPoolCRD for the type of node you want to configure by entering the following command:oc edit machineconfigpool <name>$oc edit machineconfigpool<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc edit machineconfigpool worker$oc edit machineconfigpool workerCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: ""
  name: worker
#...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPoolmetadata:creationTimestamp:"2022-11-16T15:34:25Z"generation:4labels:pools.operator.machineconfiguration.openshift.io/worker:""name:worker#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.labelsSpecifies a label to use with the kubelet configuration.If the label is not present, add a key/value pair such as:oc label machineconfigpool worker custom-kubelet=small-pods$ oc label machineconfigpool worker custom-kubelet=small-podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain the label associated with the staticMachineConfigPoolCRD for the type of node you want to configure by entering the following command:

For example:

Example output

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: ""
  name: worker
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: ""
  name: worker
#...
```

where:

**metadata.labels**
  Specifies a label to use with the kubelet configuration.If the label is not present, add a key/value pair such as:oc label machineconfigpool worker custom-kubelet=small-pods$ oc label machineconfigpool worker custom-kubelet=small-podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Specifies a label to use with the kubelet configuration.

If the label is not present, add a key/value pair such as:

Procedure

- Create a custom resource (CR) for your configuration change.If there is one file system, or if/var/lib/kubeletand/var/lib/containers/are in the same file system, the settings with the highest values trigger evictions, as those are met first. The file system triggers the eviction.Sample configuration for a container garbage collection CRapiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: worker-kubeconfig
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    evictionSoft:
      memory.available: "500Mi"
      nodefs.available: "10%"
      nodefs.inodesFree: "5%"
      imagefs.available: "15%"
      imagefs.inodesFree: "10%"
    evictionSoftGracePeriod:
      memory.available: "1m30s"
      nodefs.available: "1m30s"
      nodefs.inodesFree: "1m30s"
      imagefs.available: "1m30s"
      imagefs.inodesFree: "1m30s"
    evictionHard:
      memory.available: "200Mi"
      nodefs.available: "5%"
      nodefs.inodesFree: "4%"
      imagefs.available: "10%"
      imagefs.inodesFree: "5%"
    evictionPressureTransitionPeriod: 3m
    imageMinimumGCAge: 5m
    imageGCHighThresholdPercent: 80
    imageGCLowThresholdPercent: 75
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:worker-kubeconfigspec:machineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""kubeletConfig:evictionSoft:memory.available:"500Mi"nodefs.available:"10%"nodefs.inodesFree:"5%"imagefs.available:"15%"imagefs.inodesFree:"10%"evictionSoftGracePeriod:memory.available:"1m30s"nodefs.available:"1m30s"nodefs.inodesFree:"1m30s"imagefs.available:"1m30s"imagefs.inodesFree:"1m30s"evictionHard:memory.available:"200Mi"nodefs.available:"5%"nodefs.inodesFree:"4%"imagefs.available:"10%"imagefs.inodesFree:"5%"evictionPressureTransitionPeriod:3mimageMinimumGCAge:5mimageGCHighThresholdPercent:80imageGCLowThresholdPercent:75#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies a name for the object.spec.machineConfigPoolSelector.matchLabelsSpecifies the label from the machine config pool.spec.kubeletConfig.evictionSoftSpecifies a soft eviction and eviction thresholds for container garbage collection.spec.kubeletConfig.evictionSoftGracePeriodSpecifies a grace period for the soft eviction of containers. This parameter does not apply toeviction-hard.spec.kubeletConfig.evictionHardSpecifies a soft eviction and eviction thresholds for container garbage collection. ForevictionHardyou must specify all of these parameters. If you do not specify all parameters, only the specified parameters are applied and the garbage collection will not function properly.spec.kubeletConfig.evictionPressureTransitionPeriodSpecifies the duration to wait before transitioning out of an eviction pressure condition for container garbage collection. Setting theevictionPressureTransitionPeriodparameter to0configures the default value of 5 minutes.spec.kubeletConfig.imageMinimumGCAgeSpecifies the minimum age for an unused image before the image is removed by garbage collection.spec.kubeletConfig.imageGCHighThresholdPercentSpecifies the percent of disk usage, expressed as an integer, that triggers image garbage collection. This value must be greater than theimageGCLowThresholdPercentvalue.spec.kubeletConfig.imageGCHighThresholdPercentSpecifies the percent of disk usage, expressed as an integer, to which image garbage collection attempts to free. This value must be less than theimageGCHighThresholdPercentvalue.

Create a custom resource (CR) for your configuration change.

If there is one file system, or if/var/lib/kubeletand/var/lib/containers/are in the same file system, the settings with the highest values trigger evictions, as those are met first. The file system triggers the eviction.

Sample configuration for a container garbage collection CR

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: worker-kubeconfig
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    evictionSoft:
      memory.available: "500Mi"
      nodefs.available: "10%"
      nodefs.inodesFree: "5%"
      imagefs.available: "15%"
      imagefs.inodesFree: "10%"
    evictionSoftGracePeriod:
      memory.available: "1m30s"
      nodefs.available: "1m30s"
      nodefs.inodesFree: "1m30s"
      imagefs.available: "1m30s"
      imagefs.inodesFree: "1m30s"
    evictionHard:
      memory.available: "200Mi"
      nodefs.available: "5%"
      nodefs.inodesFree: "4%"
      imagefs.available: "10%"
      imagefs.inodesFree: "5%"
    evictionPressureTransitionPeriod: 3m
    imageMinimumGCAge: 5m
    imageGCHighThresholdPercent: 80
    imageGCLowThresholdPercent: 75
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: worker-kubeconfig
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
  kubeletConfig:
    evictionSoft:
      memory.available: "500Mi"
      nodefs.available: "10%"
      nodefs.inodesFree: "5%"
      imagefs.available: "15%"
      imagefs.inodesFree: "10%"
    evictionSoftGracePeriod:
      memory.available: "1m30s"
      nodefs.available: "1m30s"
      nodefs.inodesFree: "1m30s"
      imagefs.available: "1m30s"
      imagefs.inodesFree: "1m30s"
    evictionHard:
      memory.available: "200Mi"
      nodefs.available: "5%"
      nodefs.inodesFree: "4%"
      imagefs.available: "10%"
      imagefs.inodesFree: "5%"
    evictionPressureTransitionPeriod: 3m
    imageMinimumGCAge: 5m
    imageGCHighThresholdPercent: 80
    imageGCLowThresholdPercent: 75
#...
```

where:

**metadata.name**
  Specifies a name for the object.

**spec.machineConfigPoolSelector.matchLabels**
  Specifies the label from the machine config pool.

**spec.kubeletConfig.evictionSoft**
  Specifies a soft eviction and eviction thresholds for container garbage collection.

**spec.kubeletConfig.evictionSoftGracePeriod**
  Specifies a grace period for the soft eviction of containers. This parameter does not apply toeviction-hard.

**spec.kubeletConfig.evictionHard**
  Specifies a soft eviction and eviction thresholds for container garbage collection. ForevictionHardyou must specify all of these parameters. If you do not specify all parameters, only the specified parameters are applied and the garbage collection will not function properly.

**spec.kubeletConfig.evictionPressureTransitionPeriod**
  Specifies the duration to wait before transitioning out of an eviction pressure condition for container garbage collection. Setting theevictionPressureTransitionPeriodparameter to0configures the default value of 5 minutes.

**spec.kubeletConfig.imageMinimumGCAge**
  Specifies the minimum age for an unused image before the image is removed by garbage collection.

**spec.kubeletConfig.imageGCHighThresholdPercent**
  Specifies the percent of disk usage, expressed as an integer, that triggers image garbage collection. This value must be greater than theimageGCLowThresholdPercentvalue.

**spec.kubeletConfig.imageGCHighThresholdPercent**
  Specifies the percent of disk usage, expressed as an integer, to which image garbage collection attempts to free. This value must be less than theimageGCHighThresholdPercentvalue.
- Run the following command to create the CR:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc create -f gc-container.yaml$oc create-fgc-container.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputkubeletconfig.machineconfiguration.openshift.io/gc-container createdkubeletconfig.machineconfiguration.openshift.io/gc-container createdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to create the CR:

For example:

Example output

Verification

- Verify that garbage collection is active by entering the following command. The Machine Config Pool you specified in the custom resource appears withUPDATINGas 'true` until the change is fully implemented:oc get machineconfigpool$oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                                   UPDATED   UPDATING
master   rendered-master-546383f80705bd5aeaba93   True      False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False     TrueNAME     CONFIG                                   UPDATED   UPDATING
master   rendered-master-546383f80705bd5aeaba93   True      False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False     TrueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that garbage collection is active by entering the following command. The Machine Config Pool you specified in the custom resource appears withUPDATINGas 'true` until the change is fully implemented:

Example output

```
NAME     CONFIG                                   UPDATED   UPDATING
master   rendered-master-546383f80705bd5aeaba93   True      False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False     True
```

```
NAME     CONFIG                                   UPDATED   UPDATING
master   rendered-master-546383f80705bd5aeaba93   True      False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False     True
```

## 6.10. Allocating resources for nodes in an OpenShift Container Platform clusterCopy linkLink copied to clipboard!

To provide more reliable scheduling and minimize node resource overcommitment, reserve a portion of the CPU and memory resources for use by the underlying node components, such askubeletandkube-proxy, and the remaining system components, such assshdandNetworkManager. By specifying the resources to reserve, you provide the scheduler with more information about the remaining CPU and memory resources that a node has available for use by pods. You can allow OpenShift Container Platform toautomatically determine the optimalsystem-reservedCPU and memory resourcesfor your nodes or you canmanually determine and set the best resourcesfor your nodes.

To manually set resource values, you must use a kubelet config CR. You cannot use a machine config CR.

### 6.10.1. Understanding how to allocate resources for nodesCopy linkLink copied to clipboard!

You can manually reserve optimal CPU and memory resources for the node and system components on your nodes. Ensuring proper resources for these services can help ensure that your cluster is operating efficiently.

Thesystem-reservedsetting in theKubeletConfigcustom resource (CR) identifies the resources to reserve for the node components and system components, such as CRI-O and Kubelet. The default settings depend on the OpenShift Container Platform and Machine Config Operator versions. Confirm the defaultsystemReservedparameter on themachine-config-operatorrepository.

The KuberneteskubeReservedparameter is not supported in OpenShift Container Platform.

#### 6.10.1.1. How OpenShift Container Platform computes allocated resourcesCopy linkLink copied to clipboard!

An allocated amount of a resource is computed based on the following formula:

The withholding ofHard-Eviction-ThresholdsfromAllocatableimproves system reliability because the value forAllocatableis enforced for pods at the node level.

IfAllocatableis negative, it is set to0.

Each node reports the system resources that are used by the container runtime and kubelet. To simplify configuring thesystem-reservedparameter, view the resource use for the node by using the node summary API. The node summary is available at/api/v1/nodes/<node>/proxy/stats/summary.

#### 6.10.1.2. How nodes enforce resource constraintsCopy linkLink copied to clipboard!

The node is able to limit the total amount of resources that pods can consume based on the configured allocatable value. This feature significantly improves the reliability of the node by preventing pods from using CPU and memory resources that are needed by system services such as the container runtime and node agent. To improve node reliability, administrators should reserve resources based on a target for resource use.

The node enforces resource constraints by using a new cgroup hierarchy that enforces quality of service. All pods are launched in a dedicated cgroup hierarchy that is separate from system daemons.

Administrators should treat system daemons similar to pods that have a guaranteed quality of service. System daemons can burst within their bounding control groups and this behavior must be managed as part of cluster deployments. Reserve CPU and memory resources for system daemons by specifying the amount of CPU and memory resources insystem-reserved.

Enforcingsystem-reservedlimits can prevent critical system services from receiving CPU and memory resources. As a result, a critical system service can be ended by the out-of-memory killer. The recommendation is to enforcesystem-reservedonly if you have profiled the nodes exhaustively to determine precise estimates and you are confident that critical system services can recover if any process in that group is ended by the out-of-memory killer.

#### 6.10.1.3. Understanding Eviction ThresholdsCopy linkLink copied to clipboard!

If a node is under memory pressure, it can impact the entire node and all pods running on the node. For example, a system daemon that uses more than its reserved amount of memory can trigger an out-of-memory event. To avoid or reduce the probability of system out-of-memory events, the node provides out-of-resource handling.

You can reserve some memory using the--eviction-hardflag. The node attempts to evict pods whenever memory availability on the node drops below the absolute value or percentage. If system daemons do not exist on a node, pods are limited to the memorycapacity - eviction-hard. For this reason, resources set aside as a buffer for eviction before reaching out of memory conditions are not available for pods.

The following is an example to illustrate the impact of node allocatable for memory:

- Node capacity is32Gi
- --system-reserved is3Gi
- --eviction-hard is set to100Mi.

For this node, the effective node allocatable value is28.9Gi. If the node and system components use all their reservation, the memory available for pods is28.9Gi, and kubelet evicts pods when it exceeds this threshold.

If you enforce node allocatable,28.9Gi, with top-level cgroups, then pods can never exceed28.9Gi. Evictions are not performed unless system daemons consume more than3.1Giof memory.

If system daemons do not use up all their reservation, with the above example, pods would face memcg OOM kills from their bounding cgroup before node evictions kick in. To better enforce QoS under this situation, the node applies the hard eviction thresholds to the top-level cgroup for all pods to beNode Allocatable + Eviction Hard Thresholds.

If system daemons do not use up all their reservation, the node will evict pods whenever they consume more than28.9Giof memory. If eviction does not occur in time, a pod will be OOM killed if pods consume29Giof memory.

#### 6.10.1.4. How the scheduler determines resource availabilityCopy linkLink copied to clipboard!

The scheduler uses the value ofnode.Status.Allocatableinstead ofnode.Status.Capacityto decide if a node will become a candidate for pod scheduling.

By default, the node will report its machine capacity as fully schedulable by the cluster.

### 6.10.2. Understanding process ID limitsCopy linkLink copied to clipboard!

You can review the following information to learn how to limit the number of processes running on your nodes. Configuring an appropriate number of processes can help keep the nodes in your cluster running efficiently.

A process identifier (PID) is a unique identifier assigned by the Linux kernel to each process or thread currently running on a system. The number of processes that can run simultaneously on a system is limited to 4,194,304 by the Linux kernel. This number might also be affected by limited access to other system resources such as memory, CPU, and disk space.

In OpenShift Container Platform, consider these two supported limits for process ID (PID) usage before you schedule work on your cluster:

- Maximum number of PIDs per pod.The default value is 4,096 in OpenShift Container Platform 4.11 and later. This value is controlled by thepodPidsLimitparameter set on the node.You can view the current PID limit on a node by running the following command in achrootenvironment:cat /etc/kubernetes/kubelet.conf | grep -i pidssh-5.1# cat /etc/kubernetes/kubelet.conf | grep -i pidsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output"podPidsLimit": 4096,"podPidsLimit": 4096,Copy to ClipboardCopied!Toggle word wrapToggle overflowYou can change thepodPidsLimitby using aKubeletConfigobject. See "Creating a KubeletConfig CR to edit kubelet parameters".Containers inherit thepodPidsLimitvalue from the parent pod, so the kernel enforces the lower of the two limits. For example, if the container PID limit is set to the maximum, but the pod PID limit is4096, the PID limit of each container in the pod is confined to 4096.

Maximum number of PIDs per pod.

The default value is 4,096 in OpenShift Container Platform 4.11 and later. This value is controlled by thepodPidsLimitparameter set on the node.

You can view the current PID limit on a node by running the following command in achrootenvironment:

Example output

You can change thepodPidsLimitby using aKubeletConfigobject. See "Creating a KubeletConfig CR to edit kubelet parameters".

Containers inherit thepodPidsLimitvalue from the parent pod, so the kernel enforces the lower of the two limits. For example, if the container PID limit is set to the maximum, but the pod PID limit is4096, the PID limit of each container in the pod is confined to 4096.

- Maximum number of PIDs per node.The default value depends on node resources. In OpenShift Container Platform, this value is controlled by thesystemReservedparameter in a kubelet configuration, which reserves PIDs on each node based on the total resources of the node. For more information, see "Allocating resources for nodes in an OpenShift Container Platform cluster".

Maximum number of PIDs per node.

The default value depends on node resources. In OpenShift Container Platform, this value is controlled by thesystemReservedparameter in a kubelet configuration, which reserves PIDs on each node based on the total resources of the node. For more information, see "Allocating resources for nodes in an OpenShift Container Platform cluster".

When a pod exceeds the allowed maximum number of PIDs per pod, the pod might stop functioning correctly and might be evicted from the node. Seethe Kubernetes documentation for eviction signals and thresholdsfor more information.

When a node exceeds the allowed maximum number of PIDs per node, the node can become unstable because new processes cannot have PIDs assigned. If existing processes cannot complete without creating additional processes, the entire node can become unusable and require reboot. This situation can result in data loss, depending on the processes and applications being run. Customer administrators and Red Hat Site Reliability Engineering are notified when this threshold is reached, and aWorker node is experiencing PIDPressurewarning will appear in the cluster logs.

#### 6.10.2.1. Risks of setting higher process ID limits for OpenShift Container Platform podsCopy linkLink copied to clipboard!

You can review the following information to learn about some considerations about allowing a high maximum number of processes to run on your nodes. Configuring an appropriate number of processes can help keep the nodes in your cluster running efficiently.

You can increase the value forpodPidsLimitfrom the default of 4,096 to a maximum of 16,384. Changing this value might incur downtime for applications, because changing thepodPidsLimitrequires rebooting the affected node.

If you are running a large number of pods per node, and you have a highpodPidsLimitvalue on your nodes, you risk exceeding the PID maximum for the node.

To find the maximum number of pods that you can run simultaneously on a single node without exceeding the PID maximum for the node, divide 3,650,000 by yourpodPidsLimitvalue. For example, if yourpodPidsLimitvalue is 16,384, and you expect the pods to use close to that number of process IDs, you can safely run 222 pods on a single node.

Memory, CPU, and available storage can also limit the maximum number of pods that can run simultaneously, even when thepodPidsLimitvalue is set appropriately.

### 6.10.3. Automatically allocating resources for nodesCopy linkLink copied to clipboard!

You can configure OpenShift Container Platform to automatically determine the optimalsystem-reservedCPU and memory resources for nodes associated with a specific machine config pool. OpenShift Container Platform then updates the nodes with those values when the nodes start.

To automatically determine and allocate thesystem-reservedresources on nodes, create aKubeletConfigcustom resource (CR) to set theautoSizingReserved: trueparameter. A script on each node calculates the optimal values for the respective reserved resources based on the installed CPU and memory capacity on each node. The script takes into account that increased capacity requires a corresponding increase in the reserved resources.

Automatically determining the optimalsystem-reservedsettings ensures that your cluster is running efficiently and prevents node failure due to resource starvation of system components, such as CRI-O and kubelet, without your needing to manually calculate and update the values. By default, thesystem-reservedCPU is500mandsystem-reservedmemory is1Gi.

This feature is disabled by default.

Prerequisites

- You have the label associated with the staticMachineConfigPoolobject for the type of node you want to configure.

Procedure

- Create a custom resource (CR) for your configuration change:Sample configuration for a resource allocation CRapiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: dynamic-node
spec:
  autoSizingReserved: true
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:dynamic-nodespec:autoSizingReserved:truemachineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies a name for the CR.spec.autoSizingReservedSpecifies whether OpenShift Container Platform determines and allocates thesystem-reservedresources on the nodes associated with the specified label. Set totrueto allow automatic allocation on those nodes. Set tofalseto disable automatic allocation on those nodes.spec.machineConfigPoolSelector.matchLabelsSpecifies the label from the machine config pool where you want to enable or disable automatic resource allocation.The previous example enables automatic resource allocation on all worker nodes. OpenShift Container Platform drains the nodes, applies the kubelet config, and restarts the nodes.

Create a custom resource (CR) for your configuration change:

Sample configuration for a resource allocation CR

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: dynamic-node
spec:
  autoSizingReserved: true
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: dynamic-node
spec:
  autoSizingReserved: true
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

where:

**metadata.name**
  Specifies a name for the CR.

**spec.autoSizingReserved**
  Specifies whether OpenShift Container Platform determines and allocates thesystem-reservedresources on the nodes associated with the specified label. Set totrueto allow automatic allocation on those nodes. Set tofalseto disable automatic allocation on those nodes.

**spec.machineConfigPoolSelector.matchLabels**
  Specifies the label from the machine config pool where you want to enable or disable automatic resource allocation.

The previous example enables automatic resource allocation on all worker nodes. OpenShift Container Platform drains the nodes, applies the kubelet config, and restarts the nodes.

- Create the CR by entering the following command:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the CR by entering the following command:

Verification

- Log in to a node you configured by entering the following command:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Log in to a node you configured by entering the following command:

- Set/hostas the root directory within the debug shell:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell:

- View the/etc/node-sizing.envfile:Example outputSYSTEM_RESERVED_MEMORY=3Gi
SYSTEM_RESERVED_CPU=0.08SYSTEM_RESERVED_MEMORY=3Gi
SYSTEM_RESERVED_CPU=0.08Copy to ClipboardCopied!Toggle word wrapToggle overflowThe kubelet uses thesystem-reservedvalues in the/etc/node-sizing.envfile. In the previous example, the worker nodes are allocated0.08CPU and 3 Gi of memory. It can take several minutes for the optimal values to appear.

View the/etc/node-sizing.envfile:

Example output

```
SYSTEM_RESERVED_MEMORY=3Gi
SYSTEM_RESERVED_CPU=0.08
```

```
SYSTEM_RESERVED_MEMORY=3Gi
SYSTEM_RESERVED_CPU=0.08
```

The kubelet uses thesystem-reservedvalues in the/etc/node-sizing.envfile. In the previous example, the worker nodes are allocated0.08CPU and 3 Gi of memory. It can take several minutes for the optimal values to appear.

### 6.10.4. Manually allocating resources for nodesCopy linkLink copied to clipboard!

OpenShift Container Platform supports the CPU and memory resource types for allocation. Theephemeral-resourceresource type is also supported. For thecputype, you specify the resource quantity in units of cores, such as200m,0.5, or1. Formemoryandephemeral-storage, you specify the resource quantity in units of bytes, such as200Ki,50Mi, or5Gi. By default, thesystem-reservedCPU is500mandsystem-reservedmemory is1Gi.

As an administrator, you can set these values by using a kubelet config custom resource (CR) through a set of<resource_type>=<resource_quantity>pairs (e.g.,cpu=200m,memory=512Mi).

- For details on the recommendedsystem-reservedvalues, refer to therecommended system-reserved values.
- You must use a kubelet config CR to manually set resource values. You cannot use a machine config CR.

Prerequisites

- Obtain the label associated with the staticMachineConfigPoolCRD for the type of node you want to configure by entering the following command:oc edit machineconfigpool <name>$oc edit machineconfigpool<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc edit machineconfigpool worker$oc edit machineconfigpool workerCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: "" 
  name: worker
#...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPoolmetadata:creationTimestamp:"2022-11-16T15:34:25Z"generation:4labels:pools.operator.machineconfiguration.openshift.io/worker:""1name:worker#...Copy to ClipboardCopied!Toggle word wrapToggle overflow1The label appears under Labels.If the label is not present, add a key/value pair such as:oc label machineconfigpool worker custom-kubelet=small-pods$ oc label machineconfigpool worker custom-kubelet=small-podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain the label associated with the staticMachineConfigPoolCRD for the type of node you want to configure by entering the following command:

For example:

Example output

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: "" 
  name: worker
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
metadata:
  creationTimestamp: "2022-11-16T15:34:25Z"
  generation: 4
  labels:
    pools.operator.machineconfiguration.openshift.io/worker: ""
```

```
name: worker
#...
```

**1**
  The label appears under Labels.

If the label is not present, add a key/value pair such as:

Procedure

- Create a custom resource (CR) for your configuration change.Sample configuration for a resource allocation CRapiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-allocatable 
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: "" 
  kubeletConfig:
    systemReserved: 
      cpu: 1000m
      memory: 1Gi
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:set-allocatable1spec:machineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""2kubeletConfig:systemReserved:3cpu:1000mmemory:1Gi#...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Assign a name to CR.2Specify the label from the machine config pool.3Specify the resources to reserve for the node components and system components.

Create a custom resource (CR) for your configuration change.

Sample configuration for a resource allocation CR

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-allocatable 
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: "" 
  kubeletConfig:
    systemReserved: 
      cpu: 1000m
      memory: 1Gi
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-allocatable
```

```
spec:
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
```

```
kubeletConfig:
    systemReserved:
```

```
cpu: 1000m
      memory: 1Gi
#...
```

**1**
  Assign a name to CR.

**2**
  Specify the label from the machine config pool.

**3**
  Specify the resources to reserve for the node components and system components.
- Run the following command to create the CR:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to create the CR:

## 6.11. Allocating specific CPUs for nodes in a clusterCopy linkLink copied to clipboard!

When using the static CPU Manager policy, you can explicitly define a list of CPUs that are reserved for critical system processes on specific nodes. Reserving CPUs for critical system processes can help ensure cluster stability.

For example, on a system with 24 CPUs, you could reserve CPUs numbered 0 - 3 for the control plane allowing the compute nodes to use CPUs 4 - 23.

### 6.11.1. Reserving CPUs for nodesCopy linkLink copied to clipboard!

You can explicitly define a list of CPUs that are reserved for critical system processes on specific nodes by creating aKubeletConfigcustom resource (CR) to define thereservedSystemCPUsparameter. Reserving CPUs for critical system processes can help ensure cluster stability.

This list supersedes the CPUs that might be reserved by using thesystemReservedparameter.

For more information on thesystemReservedparameter, see "Allocating resources for nodes in an OpenShift Container Platform cluster".

Prerequisites

- You have the label associated with the machine config pool (MCP) for the type of node you want to configure:

Procedure

- Create a YAML file for theKubeletConfigCR:apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-reserved-cpus
spec:
  kubeletConfig:
    reservedSystemCPUs: "0,1,2,3"
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:set-reserved-cpusspec:kubeletConfig:reservedSystemCPUs:"0,1,2,3"machineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:metadata.nameSpecifies a name for the CR.spec.kubeletConfig.reservedSystemCPUsSpecifies the core IDs of the CPUs you want to reserve for the nodes associated with the MCP.spec.machineConfigPoolSelector.matchLabelsSpecifies the label from the MCP.

Create a YAML file for theKubeletConfigCR:

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-reserved-cpus
spec:
  kubeletConfig:
    reservedSystemCPUs: "0,1,2,3"
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-reserved-cpus
spec:
  kubeletConfig:
    reservedSystemCPUs: "0,1,2,3"
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

where:

**metadata.name**
  Specifies a name for the CR.

**spec.kubeletConfig.reservedSystemCPUs**
  Specifies the core IDs of the CPUs you want to reserve for the nodes associated with the MCP.

**spec.machineConfigPoolSelector.matchLabels**
  Specifies the label from the MCP.
- Create the CR object:oc create -f <file_name>.yaml$oc create-f<file_name>.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the CR object:

## 6.12. Enabling TLS security profiles for the kubeletCopy linkLink copied to clipboard!

You can use a TLS (Transport Layer Security) security profile to define which TLS ciphers are required by the kubelet when it is acting as an HTTP server. The kubelet uses its HTTP/GRPC server to communicate with the Kubernetes API server, which sends commands to pods, gathers logs, and run exec commands on pods through the kubelet.

A TLS security profile defines the TLS ciphers that the Kubernetes API server must use when connecting with the kubelet to protect communication between the kubelet and the Kubernetes API server.

By default, when the kubelet acts as a client with the Kubernetes API server, it automatically negotiates the TLS parameters with the API server.

### 6.12.1. Understanding TLS security profilesCopy linkLink copied to clipboard!

You can use a TLS (Transport Layer Security) security profile, as described in this section, to define which TLS ciphers are required by various OpenShift Container Platform components.

The OpenShift Container Platform TLS security profiles are based onMozilla recommended configurations.

You can specify one of the following TLS security profiles for each component:

| Profile | Description |
| --- | --- |
| Old | This profile is intended for use with legacy clients or libraries. The profile is based on theOld ba |
| Intermediate | This profile is the default TLS security profile for the Ingress Controller, kubelet, and control pl |
| Modern | This profile is intended for use with modern clients that have no need for backwards compatibility.  |
| Custom | This profile allows you to define the TLS version and ciphers to use.Use caution when using aCustomp |

Old

This profile is intended for use with legacy clients or libraries. The profile is based on theOld backward compatibilityrecommended configuration.

TheOldprofile requires a minimum TLS version of 1.0.

For the Ingress Controller, the minimum TLS version is converted from 1.0 to 1.1.

Intermediate

This profile is the default TLS security profile for the Ingress Controller, kubelet, and control plane. The profile is based on theIntermediate compatibilityrecommended configuration.

TheIntermediateprofile requires a minimum TLS version of 1.2.

This profile is the recommended configuration for the majority of clients.

Modern

This profile is intended for use with modern clients that have no need for backwards compatibility. This profile is based on theModern compatibilityrecommended configuration.

TheModernprofile requires a minimum TLS version of 1.3.

Custom

This profile allows you to define the TLS version and ciphers to use.

Use caution when using aCustomprofile, because invalid configurations can cause problems.

When using one of the predefined profile types, the effective profile configuration is subject to change between releases. For example, given a specification to use the Intermediate profile deployed on release X.Y.Z, an upgrade to release X.Y.Z+1 might cause a new profile configuration to be applied, resulting in a rollout.

### 6.12.2. Configuring the TLS security profile for the kubeletCopy linkLink copied to clipboard!

You can configure a TLS security profile for the kubelet when it is acting as an HTTP server by creating aKubeletConfigcustom resource (CR) to specify a predefined or custom TLS security profile for specific nodes.

If a TLS security profile is not configured, the default TLS security profile,Intermediate, is used.

SampleKubeletConfigCR that configures theOldTLS security profile on worker nodes

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
# ...
spec:
  tlsSecurityProfile:
    old: {}
    type: Old
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
# ...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
# ...
spec:
  tlsSecurityProfile:
    old: {}
    type: Old
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
# ...
```

You can see the ciphers and the minimum TLS version of the configured TLS security profile in thekubelet.conffile on a configured node.

Prerequisites

- You are logged in to OpenShift Container Platform as a user with thecluster-adminrole.

Procedure

- Create aKubeletConfigCR to configure the TLS security profile:SampleKubeletConfigCR for aCustomprofileapiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-kubelet-tls-security-profile
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...apiVersion:machineconfiguration.openshift.io/v1kind:KubeletConfigmetadata:name:set-kubelet-tls-security-profilespec:tlsSecurityProfile:type:Customcustom:ciphers:-ECDHE-ECDSA-CHACHA20-POLY1305-ECDHE-RSA-CHACHA20-POLY1305-ECDHE-RSA-AES128-GCM-SHA256-ECDHE-ECDSA-AES128-GCM-SHA256minTLSVersion:VersionTLS11machineConfigPoolSelector:matchLabels:pools.operator.machineconfiguration.openshift.io/worker:""#...Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.tlsSecurityProfile.typeSpecifies the TLS security profile type (Old,Intermediate, orCustom). The default isIntermediate.spec.tlsSecurityProfile.type.customSpecifies the appropriate field for the selected type:old: {}intermediate: {}custom:spec.tlsSecurityProfile.type.customFor thecustomtype, specifies a list of TLS ciphers and the minimum accepted TLS version.spec.machineConfigPoolSelector.matchLabels.customSpecifies the machine config pool label for the nodes you want to apply the TLS security profile. This parameter is optional.

Create aKubeletConfigCR to configure the TLS security profile:

SampleKubeletConfigCR for aCustomprofile

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-kubelet-tls-security-profile
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: KubeletConfig
metadata:
  name: set-kubelet-tls-security-profile
spec:
  tlsSecurityProfile:
    type: Custom
    custom:
      ciphers:
      - ECDHE-ECDSA-CHACHA20-POLY1305
      - ECDHE-RSA-CHACHA20-POLY1305
      - ECDHE-RSA-AES128-GCM-SHA256
      - ECDHE-ECDSA-AES128-GCM-SHA256
      minTLSVersion: VersionTLS11
  machineConfigPoolSelector:
    matchLabels:
      pools.operator.machineconfiguration.openshift.io/worker: ""
#...
```

where:

**spec.tlsSecurityProfile.type**
  Specifies the TLS security profile type (Old,Intermediate, orCustom). The default isIntermediate.

**spec.tlsSecurityProfile.type.custom**
  Specifies the appropriate field for the selected type:old: {}intermediate: {}custom:

Specifies the appropriate field for the selected type:

- old: {}
- intermediate: {}
- custom:

**spec.tlsSecurityProfile.type.custom**
  For thecustomtype, specifies a list of TLS ciphers and the minimum accepted TLS version.

**spec.machineConfigPoolSelector.matchLabels.custom**
  Specifies the machine config pool label for the nodes you want to apply the TLS security profile. This parameter is optional.
- Create theKubeletConfigobject:oc create -f <filename>$oc create-f<filename>Copy to ClipboardCopied!Toggle word wrapToggle overflowDepending on the number of worker nodes in the cluster, wait for the configured nodes to be rebooted one by one.

Create theKubeletConfigobject:

Depending on the number of worker nodes in the cluster, wait for the configured nodes to be rebooted one by one.

Verification

To verify that the profile is set, perform the following steps after the nodes are in theReadystate:

- Start a debug session for a configured node:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug session for a configured node:

- Set/hostas the root directory within the debug shell:chroot /hostsh-4.4# chroot /hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell:

- View thekubelet.conffile:cat /etc/kubernetes/kubelet.confsh-4.4# cat /etc/kubernetes/kubelet.confCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output"kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
#...
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
#..."kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
#...
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
#...Copy to ClipboardCopied!Toggle word wrapToggle overflow

View thekubelet.conffile:

Example output

```
"kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
#...
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
#...
```

```
"kind": "KubeletConfiguration",
  "apiVersion": "kubelet.config.k8s.io/v1beta1",
#...
  "tlsCipherSuites": [
    "TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256",
    "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384",
    "TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256",
    "TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256"
  ],
  "tlsMinVersion": "VersionTLS12",
#...
```

## 6.13. Creating infrastructure nodesCopy linkLink copied to clipboard!

You can use the advanced machine management and scaling capabilities only in clusters where the Machine API is operational. Clusters with user-provisioned infrastructure require additional validation and configuration to use the Machine API.

Clusters with the infrastructure platform typenonecannot use the Machine API. This limitation applies even if the compute machines that are attached to the cluster are installed on a platform that supports the feature. This parameter cannot be changed after installation.

To view the platform type for your cluster, run the following command:

You can use infrastructure machine sets to create machines that host only infrastructure components, such as the default router, the integrated container image registry, and the components for cluster metrics and monitoring. These infrastructure machines are not counted toward the total number of subscriptions that are required to run the environment.

After adding theNoScheduletaint on the infrastructure node, existing DNS pods running on that node are marked asmisscheduled. You must either delete oradd toleration onmisscheduledDNS pods.

### 6.13.1. OpenShift Container Platform infrastructure componentsCopy linkLink copied to clipboard!

You can review the following information to understand which components you can move to an infrastructure node. Components that you move to an infrastructure node do not need to be accounted for during sizing.

Each self-managed Red Hat OpenShift subscription includes entitlements for OpenShift Container Platform and other OpenShift-related components. These entitlements are included for running OpenShift Container Platform control plane and infrastructure workloads and do not need to be accounted for during sizing.

To qualify as an infrastructure node and use the included entitlement, only components that are supporting the cluster, and not part of an end-user application, can run on those instances. Examples include the following components:

- Kubernetes and OpenShift Container Platform control plane services
- The default router
- The integrated container image registry
- The HAProxy-based Ingress Controller
- The cluster metrics collection, or monitoring service, including components for monitoring user-defined projects
- Cluster aggregated logging
- Red Hat Quay
- Red Hat OpenShift Data Foundation
- Red Hat Advanced Cluster Management for Kubernetes
- Red Hat Advanced Cluster Security for Kubernetes
- Red Hat OpenShift GitOps
- Red Hat OpenShift Pipelines
- Red Hat OpenShift Service Mesh

Any node that runs any other container, pod, or component is a worker node that your subscription must cover.

For information about infrastructure nodes and which components can run on infrastructure nodes, see the "Red Hat OpenShift control plane and infrastructure nodes" section in theOpenShift sizing and subscription guide for enterprise Kubernetesdocument.

#### 6.13.1.1. Creating an infrastructure nodeCopy linkLink copied to clipboard!

See "Creating infrastructure machine sets" for installer-provisioned infrastructure environments or for any cluster where the control plane nodes are managed by the machine API.

You can use labels to configure worker nodes as infrastructure nodes, where you can move infrastructure resources.

After you create the infrastructure nodes, you can move appropriate workloads to those nodes by using taints and tolerations.

You can optionally create a default cluster-wide node selector. The default node selector is applied to pods created in all namespaces and creates an intersection with any existing node selectors on a pod, which additionally constrains the pod’s selector.

If the default node selector key conflicts with the key of a pod’s label, then the default node selector is not applied.

However, do not set a default node selector that might cause a pod to become unschedulable. For example, setting the default node selector to a specific node role, such asnode-role.kubernetes.io/infra="", when a pod’s label is set to a different node role, such asnode-role.kubernetes.io/master="", can cause the pod to become unschedulable. For this reason, use caution when setting the default node selector to specific node roles.

You can alternatively use a project node selector to avoid cluster-wide node selector key conflicts.

Procedure

- Add a label to the worker nodes that you want to act as infrastructure nodes:oc label node <node-name> node-role.kubernetes.io/infra=""$oc labelnode<node-name>node-role.kubernetes.io/infra=""Copy to ClipboardCopied!Toggle word wrapToggle overflow

Add a label to the worker nodes that you want to act as infrastructure nodes:

- Check to see if applicable nodes now have theinfrarole:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check to see if applicable nodes now have theinfrarole:

- Optional: Create a default cluster-wide node selector:Edit theSchedulerobject:oc edit scheduler cluster$oc edit scheduler clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd thedefaultNodeSelectorfield with the appropriate node selector:apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  name: cluster
spec:
  defaultNodeSelector: node-role.kubernetes.io/infra=""
# ...apiVersion:config.openshift.io/v1kind:Schedulermetadata:name:clusterspec:defaultNodeSelector:node-role.kubernetes.io/infra=""# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowThis example node selector deploys pods on infrastructure nodes by default.Save the file to apply the changes.You can now move infrastructure resources to the new infrastructure nodes. Also, remove any workloads that you do not want, or that do not belong, on the new infrastructure node. See the list of workloads supported for use on infrastructure nodes in "OpenShift Container Platform infrastructure components".

Optional: Create a default cluster-wide node selector:

- Edit theSchedulerobject:oc edit scheduler cluster$oc edit scheduler clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theSchedulerobject:

- Add thedefaultNodeSelectorfield with the appropriate node selector:apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  name: cluster
spec:
  defaultNodeSelector: node-role.kubernetes.io/infra=""
# ...apiVersion:config.openshift.io/v1kind:Schedulermetadata:name:clusterspec:defaultNodeSelector:node-role.kubernetes.io/infra=""# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowThis example node selector deploys pods on infrastructure nodes by default.

Add thedefaultNodeSelectorfield with the appropriate node selector:

```
apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  name: cluster
spec:
  defaultNodeSelector: node-role.kubernetes.io/infra=""
# ...
```

```
apiVersion: config.openshift.io/v1
kind: Scheduler
metadata:
  name: cluster
spec:
  defaultNodeSelector: node-role.kubernetes.io/infra=""
# ...
```

This example node selector deploys pods on infrastructure nodes by default.

- Save the file to apply the changes.

You can now move infrastructure resources to the new infrastructure nodes. Also, remove any workloads that you do not want, or that do not belong, on the new infrastructure node. See the list of workloads supported for use on infrastructure nodes in "OpenShift Container Platform infrastructure components".
