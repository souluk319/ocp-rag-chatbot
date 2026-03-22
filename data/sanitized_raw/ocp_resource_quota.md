<!-- source: ocp_resource_quota.md -->

# Resource Management

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/building_applications/quotas
---

# Chapter 8. Quotas

## 8.1. Resource quotas per projectCopy linkLink copied to clipboard!

Aresource quota, defined by aResourceQuotaobject, provides constraints that limit aggregate resource consumption per project. It can limit the quantity of objects that can be created in a project by type, as well as the total amount of compute resources and storage that might be consumed by resources in that project.

This guide describes how resource quotas work, how cluster administrators can set and manage resource quotas on a per project basis, and how developers and cluster administrators can view them.

### 8.1.1. Resources managed by quotasCopy linkLink copied to clipboard!

The following describes the set of compute resources and object types that can be managed by a quota.

A pod is in a terminal state ifstatus.phase in (Failed, Succeeded)is true.

| Resource Name | Description |
| --- | --- |
| cpu | The sum of CPU requests across all pods in a non-terminal state cannot exceed this value.cpuandreque |
| memory | The sum of memory requests across all pods in a non-terminal state cannot exceed this value.memoryan |
| requests.cpu | The sum of CPU requests across all pods in a non-terminal state cannot exceed this value.cpuandreque |
| requests.memory | The sum of memory requests across all pods in a non-terminal state cannot exceed this value.memoryan |
| limits.cpu | The sum of CPU limits across all pods in a non-terminal state cannot exceed this value. |
| limits.memory | The sum of memory limits across all pods in a non-terminal state cannot exceed this value. |

cpu

The sum of CPU requests across all pods in a non-terminal state cannot exceed this value.cpuandrequests.cpuare the same value and can be used interchangeably.

memory

The sum of memory requests across all pods in a non-terminal state cannot exceed this value.memoryandrequests.memoryare the same value and can be used interchangeably.

requests.cpu

The sum of CPU requests across all pods in a non-terminal state cannot exceed this value.cpuandrequests.cpuare the same value and can be used interchangeably.

requests.memory

The sum of memory requests across all pods in a non-terminal state cannot exceed this value.memoryandrequests.memoryare the same value and can be used interchangeably.

limits.cpu

The sum of CPU limits across all pods in a non-terminal state cannot exceed this value.

limits.memory

The sum of memory limits across all pods in a non-terminal state cannot exceed this value.

| Resource Name | Description |
| --- | --- |
| requests.storage | The sum of storage requests across all persistent volume claims in any state cannot exceed this valu |
| persistentvolumeclaims | The total number of persistent volume claims that can exist in the project. |
| <storage-class-name>.storageclass.storage.k8s.io/requests.storage | The sum of storage requests across all persistent volume claims in any state that have a matching st |
| <storage-class-name>.storageclass.storage.k8s.io/persistentvolumeclaims | The total number of persistent volume claims with a matching storage class that can exist in the pro |
| ephemeral-storage | The sum of local ephemeral storage requests across all pods in a non-terminal state cannot exceed th |
| requests.ephemeral-storage | The sum of ephemeral storage requests across all pods in a non-terminal state cannot exceed this val |
| limits.ephemeral-storage | The sum of ephemeral storage limits across all pods in a non-terminal state cannot exceed this value |

requests.storage

The sum of storage requests across all persistent volume claims in any state cannot exceed this value.

persistentvolumeclaims

The total number of persistent volume claims that can exist in the project.

<storage-class-name>.storageclass.storage.k8s.io/requests.storage

The sum of storage requests across all persistent volume claims in any state that have a matching storage class, cannot exceed this value.

<storage-class-name>.storageclass.storage.k8s.io/persistentvolumeclaims

The total number of persistent volume claims with a matching storage class that can exist in the project.

ephemeral-storage

The sum of local ephemeral storage requests across all pods in a non-terminal state cannot exceed this value.ephemeral-storageandrequests.ephemeral-storageare the same value and can be used interchangeably.

requests.ephemeral-storage

The sum of ephemeral storage requests across all pods in a non-terminal state cannot exceed this value.ephemeral-storageandrequests.ephemeral-storageare the same value and can be used interchangeably.

limits.ephemeral-storage

The sum of ephemeral storage limits across all pods in a non-terminal state cannot exceed this value.

| Resource Name | Description |
| --- | --- |
| pods | The total number of pods in a non-terminal state that can exist in the project. |
| replicationcontrollers | The total number of ReplicationControllers that can exist in the project. |
| resourcequotas | The total number of resource quotas that can exist in the project. |
| services | The total number of services that can exist in the project. |
| services.loadbalancers | The total number of services of typeLoadBalancerthat can exist in the project. |
| services.nodeports | The total number of services of typeNodePortthat can exist in the project. |
| secrets | The total number of secrets that can exist in the project. |
| configmaps | The total number ofConfigMapobjects that can exist in the project. |
| persistentvolumeclaims | The total number of persistent volume claims that can exist in the project. |
| openshift.io/imagestreams | The total number of imagestreams that can exist in the project. |

pods

The total number of pods in a non-terminal state that can exist in the project.

replicationcontrollers

The total number of ReplicationControllers that can exist in the project.

resourcequotas

The total number of resource quotas that can exist in the project.

services

The total number of services that can exist in the project.

services.loadbalancers

The total number of services of typeLoadBalancerthat can exist in the project.

services.nodeports

The total number of services of typeNodePortthat can exist in the project.

secrets

The total number of secrets that can exist in the project.

configmaps

The total number ofConfigMapobjects that can exist in the project.

persistentvolumeclaims

The total number of persistent volume claims that can exist in the project.

openshift.io/imagestreams

The total number of imagestreams that can exist in the project.

### 8.1.2. Quota scopesCopy linkLink copied to clipboard!

Each quota can have an associated set ofscopes. A quota only measures usage for a resource if it matches the intersection of enumerated scopes.

Adding a scope to a quota restricts the set of resources to which that quota can apply. Specifying a resource outside of the allowed set results in a validation error.

| Scope | Description |
| --- | --- |
| BestEffort | Match pods that have best effort quality of service for eithercpuormemory. |
| NotBestEffort | Match pods that do not have best effort quality of service forcpuandmemory. |

Scope

Description

BestEffort

Match pods that have best effort quality of service for eithercpuormemory.

NotBestEffort

Match pods that do not have best effort quality of service forcpuandmemory.

ABestEffortscope restricts a quota to limiting the following resources:

- pods

ANotBestEffortscope restricts a quota to tracking the following resources:

- pods
- memory
- requests.memory
- limits.memory
- cpu
- requests.cpu
- limits.cpu

### 8.1.3. Quota enforcementCopy linkLink copied to clipboard!

After a resource quota for a project is first created, the project restricts the ability to create any new resources that may violate a quota constraint until it has calculated updated usage statistics.

After a quota is created and usage statistics are updated, the project accepts the creation of new content. When you create or modify resources, your quota usage is incremented immediately upon the request to create or modify the resource.

When you delete a resource, your quota use is decremented during the next full recalculation of quota statistics for the project. A configurable amount of time determines how long it takes to reduce quota usage statistics to their current observed system value.

If project modifications exceed a quota usage limit, the server denies the action, and an appropriate error message is returned to the user explaining the quota constraint violated, and what their currently observed usage statistics are in the system.

### 8.1.4. Requests versus limitsCopy linkLink copied to clipboard!

When allocating compute resources, each container might specify a request and a limit value each for CPU, memory, and ephemeral storage. Quotas can restrict any of these values.

If the quota has a value specified forrequests.cpuorrequests.memory, then it requires that every incoming container make an explicit request for those resources. If the quota has a value specified forlimits.cpuorlimits.memory, then it requires that every incoming container specify an explicit limit for those resources.

### 8.1.5. Sample resource quota definitionsCopy linkLink copied to clipboard!

core-object-counts.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: core-object-counts
spec:
  hard:
    configmaps: "10" 
    persistentvolumeclaims: "4" 
    replicationcontrollers: "20" 
    secrets: "10" 
    services: "10" 
    services.loadbalancers: "2"
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: core-object-counts
spec:
  hard:
    configmaps: "10"
```

```
persistentvolumeclaims: "4"
```

```
replicationcontrollers: "20"
```

```
secrets: "10"
```

```
services: "10"
```

```
services.loadbalancers: "2"
```

**1**
  The total number ofConfigMapobjects that can exist in the project.

**2**
  The total number of persistent volume claims (PVCs) that can exist in the project.

**3**
  The total number of replication controllers that can exist in the project.

**4**
  The total number of secrets that can exist in the project.

**5**
  The total number of services that can exist in the project.

**6**
  The total number of services of typeLoadBalancerthat can exist in the project.

openshift-object-counts.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: openshift-object-counts
spec:
  hard:
    openshift.io/imagestreams: "10"
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: openshift-object-counts
spec:
  hard:
    openshift.io/imagestreams: "10"
```

**1**
  The total number of image streams that can exist in the project.

compute-resources.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    pods: "4" 
    requests.cpu: "1" 
    requests.memory: 1Gi 
    limits.cpu: "2" 
    limits.memory: 2Gi
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    pods: "4"
```

```
requests.cpu: "1"
```

```
requests.memory: 1Gi
```

```
limits.cpu: "2"
```

```
limits.memory: 2Gi
```

**1**
  The total number of pods in a non-terminal state that can exist in the project.

**2**
  Across all pods in a non-terminal state, the sum of CPU requests cannot exceed 1 core.

**3**
  Across all pods in a non-terminal state, the sum of memory requests cannot exceed 1Gi.

**4**
  Across all pods in a non-terminal state, the sum of CPU limits cannot exceed 2 cores.

**5**
  Across all pods in a non-terminal state, the sum of memory limits cannot exceed 2Gi.

besteffort.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: besteffort
spec:
  hard:
    pods: "1" 
  scopes:
  - BestEffort
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: besteffort
spec:
  hard:
    pods: "1"
```

```
scopes:
  - BestEffort
```

**1**
  The total number of pods in a non-terminal state withBestEffortquality of service that can exist in the project.

**2**
  Restricts the quota to only matching pods that haveBestEffortquality of service for either memory or CPU.

compute-resources-long-running.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources-long-running
spec:
  hard:
    pods: "4" 
    limits.cpu: "4" 
    limits.memory: "2Gi" 
  scopes:
  - NotTerminating
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources-long-running
spec:
  hard:
    pods: "4"
```

```
limits.cpu: "4"
```

```
limits.memory: "2Gi"
```

```
scopes:
  - NotTerminating
```

**1**
  The total number of pods in a non-terminal state.

**2**
  Across all pods in a non-terminal state, the sum of CPU limits cannot exceed this value.

**3**
  Across all pods in a non-terminal state, the sum of memory limits cannot exceed this value.

**4**
  Restricts the quota to only matching pods wherespec.activeDeadlineSecondsis set tonil. Build pods fall underNotTerminatingunless theRestartNeverpolicy is applied.

compute-resources-time-bound.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources-time-bound
spec:
  hard:
    pods: "2" 
    limits.cpu: "1" 
    limits.memory: "1Gi" 
  scopes:
  - Terminating
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources-time-bound
spec:
  hard:
    pods: "2"
```

```
limits.cpu: "1"
```

```
limits.memory: "1Gi"
```

```
scopes:
  - Terminating
```

**1**
  The total number of pods in a terminating state.

**2**
  Across all pods in a terminating state, the sum of CPU limits cannot exceed this value.

**3**
  Across all pods in a terminating state, the sum of memory limits cannot exceed this value.

**4**
  Restricts the quota to only matching pods wherespec.activeDeadlineSeconds >=0. For example, this quota charges for build or deployer pods, but not long running pods like a web server or database.

storage-consumption.yaml

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-consumption
spec:
  hard:
    persistentvolumeclaims: "10" 
    requests.storage: "50Gi" 
    gold.storageclass.storage.k8s.io/requests.storage: "10Gi" 
    silver.storageclass.storage.k8s.io/requests.storage: "20Gi" 
    silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5" 
    bronze.storageclass.storage.k8s.io/requests.storage: "0" 
    bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0" 
    requests.ephemeral-storage: 2Gi 
    limits.ephemeral-storage: 4Gi
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: storage-consumption
spec:
  hard:
    persistentvolumeclaims: "10"
```

```
requests.storage: "50Gi"
```

```
gold.storageclass.storage.k8s.io/requests.storage: "10Gi"
```

```
silver.storageclass.storage.k8s.io/requests.storage: "20Gi"
```

```
silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5"
```

```
bronze.storageclass.storage.k8s.io/requests.storage: "0"
```

```
bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"
```

```
requests.ephemeral-storage: 2Gi
```

```
limits.ephemeral-storage: 4Gi
```

**1**
  The total number of persistent volume claims in a project

**2**
  Across all persistent volume claims in a project, the sum of storage requested cannot exceed this value.

**3**
  Across all persistent volume claims in a project, the sum of storage requested in the gold storage class cannot exceed this value.

**4**
  Across all persistent volume claims in a project, the sum of storage requested in the silver storage class cannot exceed this value.

**5**
  Across all persistent volume claims in a project, the total number of claims in the silver storage class cannot exceed this value.

**6**
  Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this is set to0, it means bronze storage class cannot request storage.

**7**
  Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this is set to0, it means bronze storage class cannot create claims.

**8**
  Across all pods in a non-terminal state, the sum of ephemeral storage requests cannot exceed 2Gi.

**9**
  Across all pods in a non-terminal state, the sum of ephemeral storage limits cannot exceed 4Gi.

### 8.1.6. Creating a quotaCopy linkLink copied to clipboard!

You can create a quota to constrain resource usage in a given project.

Procedure

- Define the quota in a file.
- Use the file to create the quota and apply it to a project:oc create -f <file> [-n <project_name>]$oc create-f<file>[-n<project_name>]Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc create -f core-object-counts.yaml -n demoproject$oc create-fcore-object-counts.yaml-ndemoprojectCopy to ClipboardCopied!Toggle word wrapToggle overflow

Use the file to create the quota and apply it to a project:

For example:

#### 8.1.6.1. Creating object count quotasCopy linkLink copied to clipboard!

You can create an object count quota for all standard namespaced resource types on OpenShift Container Platform, such asBuildConfigandDeploymentConfigobjects. An object quota count places a defined quota on all standard namespaced resource types.

When using a resource quota, an object is charged against the quota upon creation. These types of quotas are useful to protect against exhaustion of resources. The quota can only be created if there are enough spare resources within the project.

Procedure

To configure an object count quota for a resource:

- Run the following command:oc create quota <name> \
    --hard=count/<resource>.<group>=<quota>,count/<resource>.<group>=<quota>$oc createquota<name>\--hard=count/<resource>.<group>=<quota>,count/<resource>.<group>=<quota>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The<resource>variable is the name of the resource, and<group>is the API group, if applicable. Use theoc api-resourcescommand for a list of resources and their associated API groups.For example:oc create quota test \
    --hard=count/deployments.apps=2,count/replicasets.apps=4,count/pods=3,count/secrets=4$oc createquotatest\--hard=count/deployments.apps=2,count/replicasets.apps=4,count/pods=3,count/secrets=4Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputresourcequota "test" createdresourcequota "test" createdCopy to ClipboardCopied!Toggle word wrapToggle overflowThis example limits the listed resources to the hard limit in each project in the cluster.

Run the following command:

```
oc create quota <name> \
    --hard=count/<resource>.<group>=<quota>,count/<resource>.<group>=<quota>
```

```
$ oc create quota <name> \
    --hard=count/<resource>.<group>=<quota>,count/<resource>.<group>=<quota>
```

**1**
  The<resource>variable is the name of the resource, and<group>is the API group, if applicable. Use theoc api-resourcescommand for a list of resources and their associated API groups.

For example:

```
oc create quota test \
    --hard=count/deployments.apps=2,count/replicasets.apps=4,count/pods=3,count/secrets=4
```

```
$ oc create quota test \
    --hard=count/deployments.apps=2,count/replicasets.apps=4,count/pods=3,count/secrets=4
```

Example output

This example limits the listed resources to the hard limit in each project in the cluster.

- Verify that the quota was created:oc describe quota test$oc describequotatestCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:                         test
Namespace:                    quota
Resource                      Used  Hard
--------                      ----  ----
count/deployments.apps        0     2
count/pods                    0     3
count/replicasets.apps        0     4
count/secrets                 0     4Name:                         test
Namespace:                    quota
Resource                      Used  Hard
--------                      ----  ----
count/deployments.apps        0     2
count/pods                    0     3
count/replicasets.apps        0     4
count/secrets                 0     4Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the quota was created:

Example output

```
Name:                         test
Namespace:                    quota
Resource                      Used  Hard
--------                      ----  ----
count/deployments.apps        0     2
count/pods                    0     3
count/replicasets.apps        0     4
count/secrets                 0     4
```

```
Name:                         test
Namespace:                    quota
Resource                      Used  Hard
--------                      ----  ----
count/deployments.apps        0     2
count/pods                    0     3
count/replicasets.apps        0     4
count/secrets                 0     4
```

#### 8.1.6.2. Setting resource quota for extended resourcesCopy linkLink copied to clipboard!

Overcommitment of resources is not allowed for extended resources, so you must specifyrequestsandlimitsfor the same extended resource in a quota. Currently, only quota items with the prefixrequests.is allowed for extended resources. The following is an example scenario of how to set resource quota for the GPU resourcenvidia.com/gpu.

Procedure

- Determine how many GPUs are available on a node in your cluster. For example:oc describe node ip-172-31-27-209.us-west-2.compute.internal | egrep 'Capacity|Allocatable|gpu'#oc describenodeip-172-31-27-209.us-west-2.compute.internal|egrep'Capacity|Allocatable|gpu'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputopenshift.com/gpu-accelerator=true
Capacity:
 nvidia.com/gpu:  2
Allocatable:
 nvidia.com/gpu:  2
  nvidia.com/gpu  0           0openshift.com/gpu-accelerator=true
Capacity:
 nvidia.com/gpu:  2
Allocatable:
 nvidia.com/gpu:  2
  nvidia.com/gpu  0           0Copy to ClipboardCopied!Toggle word wrapToggle overflowIn this example, 2 GPUs are available.

Determine how many GPUs are available on a node in your cluster. For example:

Example output

```
openshift.com/gpu-accelerator=true
Capacity:
 nvidia.com/gpu:  2
Allocatable:
 nvidia.com/gpu:  2
  nvidia.com/gpu  0           0
```

```
openshift.com/gpu-accelerator=true
Capacity:
 nvidia.com/gpu:  2
Allocatable:
 nvidia.com/gpu:  2
  nvidia.com/gpu  0           0
```

In this example, 2 GPUs are available.

- Create aResourceQuotaobject to set a quota in the namespacenvidia. In this example, the quota is1:Example outputapiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: nvidia
spec:
  hard:
    requests.nvidia.com/gpu: 1apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: nvidia
spec:
  hard:
    requests.nvidia.com/gpu: 1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Create aResourceQuotaobject to set a quota in the namespacenvidia. In this example, the quota is1:

Example output

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: nvidia
spec:
  hard:
    requests.nvidia.com/gpu: 1
```

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: gpu-quota
  namespace: nvidia
spec:
  hard:
    requests.nvidia.com/gpu: 1
```

- Create the quota:oc create -f gpu-quota.yaml#oc create-fgpu-quota.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputresourcequota/gpu-quota createdresourcequota/gpu-quota createdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the quota:

Example output

- Verify that the namespace has the correct quota set:oc describe quota gpu-quota -n nvidia#oc describequotagpu-quota-nnvidiaCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  0     1Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  0     1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the namespace has the correct quota set:

Example output

```
Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  0     1
```

```
Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  0     1
```

- Define a pod that asks for a single GPU. The following example definition file is calledgpu-pod.yaml:apiVersion: v1
kind: Pod
metadata:
  generateName: gpu-pod-
  namespace: nvidia
spec:
  restartPolicy: OnFailure
  containers:
  - name: rhel7-gpu-pod
    image: rhel7
    env:
      - name: NVIDIA_VISIBLE_DEVICES
        value: all
      - name: NVIDIA_DRIVER_CAPABILITIES
        value: "compute,utility"
      - name: NVIDIA_REQUIRE_CUDA
        value: "cuda>=5.0"
    command: ["sleep"]
    args: ["infinity"]
    resources:
      limits:
        nvidia.com/gpu: 1apiVersion:v1kind:Podmetadata:generateName:gpu-pod-namespace:nvidiaspec:restartPolicy:OnFailurecontainers:-name:rhel7-gpu-podimage:rhel7env:-name:NVIDIA_VISIBLE_DEVICESvalue:all-name:NVIDIA_DRIVER_CAPABILITIESvalue:"compute,utility"-name:NVIDIA_REQUIRE_CUDAvalue:"cuda>=5.0"command:["sleep"]args:["infinity"]resources:limits:nvidia.com/gpu:1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Define a pod that asks for a single GPU. The following example definition file is calledgpu-pod.yaml:

```
apiVersion: v1
kind: Pod
metadata:
  generateName: gpu-pod-
  namespace: nvidia
spec:
  restartPolicy: OnFailure
  containers:
  - name: rhel7-gpu-pod
    image: rhel7
    env:
      - name: NVIDIA_VISIBLE_DEVICES
        value: all
      - name: NVIDIA_DRIVER_CAPABILITIES
        value: "compute,utility"
      - name: NVIDIA_REQUIRE_CUDA
        value: "cuda>=5.0"
    command: ["sleep"]
    args: ["infinity"]
    resources:
      limits:
        nvidia.com/gpu: 1
```

```
apiVersion: v1
kind: Pod
metadata:
  generateName: gpu-pod-
  namespace: nvidia
spec:
  restartPolicy: OnFailure
  containers:
  - name: rhel7-gpu-pod
    image: rhel7
    env:
      - name: NVIDIA_VISIBLE_DEVICES
        value: all
      - name: NVIDIA_DRIVER_CAPABILITIES
        value: "compute,utility"
      - name: NVIDIA_REQUIRE_CUDA
        value: "cuda>=5.0"
    command: ["sleep"]
    args: ["infinity"]
    resources:
      limits:
        nvidia.com/gpu: 1
```

- Create the pod:oc create -f gpu-pod.yaml#oc create-fgpu-pod.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the pod:

- Verify that the pod is running:oc get pods#oc get podsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME              READY     STATUS      RESTARTS   AGE
gpu-pod-s46h7     1/1       Running     0          1mNAME              READY     STATUS      RESTARTS   AGE
gpu-pod-s46h7     1/1       Running     0          1mCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the pod is running:

Example output

```
NAME              READY     STATUS      RESTARTS   AGE
gpu-pod-s46h7     1/1       Running     0          1m
```

```
NAME              READY     STATUS      RESTARTS   AGE
gpu-pod-s46h7     1/1       Running     0          1m
```

- Verify that the quotaUsedcounter is correct:oc describe quota gpu-quota -n nvidia#oc describequotagpu-quota-nnvidiaCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  1     1Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  1     1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the quotaUsedcounter is correct:

Example output

```
Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  1     1
```

```
Name:                    gpu-quota
Namespace:               nvidia
Resource                 Used  Hard
--------                 ----  ----
requests.nvidia.com/gpu  1     1
```

- Attempt to create a second GPU pod in thenvidianamespace. This is technically available on the node because it has 2 GPUs:oc create -f gpu-pod.yaml#oc create-fgpu-pod.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputError from server (Forbidden): error when creating "gpu-pod.yaml": pods "gpu-pod-f7z2w" is forbidden: exceeded quota: gpu-quota, requested: requests.nvidia.com/gpu=1, used: requests.nvidia.com/gpu=1, limited: requests.nvidia.com/gpu=1Error from server (Forbidden): error when creating "gpu-pod.yaml": pods "gpu-pod-f7z2w" is forbidden: exceeded quota: gpu-quota, requested: requests.nvidia.com/gpu=1, used: requests.nvidia.com/gpu=1, limited: requests.nvidia.com/gpu=1Copy to ClipboardCopied!Toggle word wrapToggle overflowThisForbiddenerror message is expected because you have a quota of 1 GPU and this pod tried to allocate a second GPU, which exceeds its quota.

Attempt to create a second GPU pod in thenvidianamespace. This is technically available on the node because it has 2 GPUs:

Example output

ThisForbiddenerror message is expected because you have a quota of 1 GPU and this pod tried to allocate a second GPU, which exceeds its quota.

### 8.1.7. Viewing a quotaCopy linkLink copied to clipboard!

You can view usage statistics related to any hard limits defined in a quota for a project by navigating in the web console to the project’sQuotapage.

You can also use the CLI to view quota details.

Procedure

- Get the list of quotas defined in the project. For example, for a project calleddemoproject:oc get quota -n demoproject$oc getquota-ndemoprojectCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                           AGE    REQUEST                                                                                                      LIMIT
besteffort                     4s     pods: 1/2
compute-resources-time-bound   10m    pods: 0/2                                                                                                    limits.cpu: 0/1, limits.memory: 0/1Gi
core-object-counts             109s   configmaps: 2/10, persistentvolumeclaims: 1/4, replicationcontrollers: 1/20, secrets: 9/10, services: 2/10NAME                           AGE    REQUEST                                                                                                      LIMIT
besteffort                     4s     pods: 1/2
compute-resources-time-bound   10m    pods: 0/2                                                                                                    limits.cpu: 0/1, limits.memory: 0/1Gi
core-object-counts             109s   configmaps: 2/10, persistentvolumeclaims: 1/4, replicationcontrollers: 1/20, secrets: 9/10, services: 2/10Copy to ClipboardCopied!Toggle word wrapToggle overflow

Get the list of quotas defined in the project. For example, for a project calleddemoproject:

Example output

```
NAME                           AGE    REQUEST                                                                                                      LIMIT
besteffort                     4s     pods: 1/2
compute-resources-time-bound   10m    pods: 0/2                                                                                                    limits.cpu: 0/1, limits.memory: 0/1Gi
core-object-counts             109s   configmaps: 2/10, persistentvolumeclaims: 1/4, replicationcontrollers: 1/20, secrets: 9/10, services: 2/10
```

```
NAME                           AGE    REQUEST                                                                                                      LIMIT
besteffort                     4s     pods: 1/2
compute-resources-time-bound   10m    pods: 0/2                                                                                                    limits.cpu: 0/1, limits.memory: 0/1Gi
core-object-counts             109s   configmaps: 2/10, persistentvolumeclaims: 1/4, replicationcontrollers: 1/20, secrets: 9/10, services: 2/10
```

- Describe the quota you are interested in, for example thecore-object-countsquota:oc describe quota core-object-counts -n demoproject$oc describequotacore-object-counts-ndemoprojectCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:			core-object-counts
Namespace:		demoproject
Resource		Used	Hard
--------		----	----
configmaps		3	10
persistentvolumeclaims	0	4
replicationcontrollers	3	20
secrets			9	10
services		2	10Name:			core-object-counts
Namespace:		demoproject
Resource		Used	Hard
--------		----	----
configmaps		3	10
persistentvolumeclaims	0	4
replicationcontrollers	3	20
secrets			9	10
services		2	10Copy to ClipboardCopied!Toggle word wrapToggle overflow

Describe the quota you are interested in, for example thecore-object-countsquota:

Example output

```
Name:			core-object-counts
Namespace:		demoproject
Resource		Used	Hard
--------		----	----
configmaps		3	10
persistentvolumeclaims	0	4
replicationcontrollers	3	20
secrets			9	10
services		2	10
```

```
Name:			core-object-counts
Namespace:		demoproject
Resource		Used	Hard
--------		----	----
configmaps		3	10
persistentvolumeclaims	0	4
replicationcontrollers	3	20
secrets			9	10
services		2	10
```

### 8.1.8. Configuring explicit resource quotasCopy linkLink copied to clipboard!

Configure explicit resource quotas in a project request template to apply specific resource quotas in new projects.

Prerequisites

- Access to the cluster as a user with the cluster-admin role.
- Install the OpenShift CLI (oc).

Procedure

- Add a resource quota definition to a project request template:If a project request template does not exist in a cluster:Create a bootstrap project template and output it to a file calledtemplate.yaml:oc adm create-bootstrap-project-template -o yaml > template.yaml$oc adm create-bootstrap-project-template-oyaml>template.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd a resource quota definition totemplate.yaml. The following example defines a resource quota named 'storage-consumption'. The definition must be added before theparameters:section in the template:- apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: storage-consumption
    namespace: ${PROJECT_NAME}
  spec:
    hard:
      persistentvolumeclaims: "10" 
      requests.storage: "50Gi" 
      gold.storageclass.storage.k8s.io/requests.storage: "10Gi" 
      silver.storageclass.storage.k8s.io/requests.storage: "20Gi" 
      silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5" 
      bronze.storageclass.storage.k8s.io/requests.storage: "0" 
      bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"-apiVersion:v1kind:ResourceQuotametadata:name:storage-consumptionnamespace:${PROJECT_NAME}spec:hard:persistentvolumeclaims:"10"1requests.storage:"50Gi"2gold.storageclass.storage.k8s.io/requests.storage:"10Gi"3silver.storageclass.storage.k8s.io/requests.storage:"20Gi"4silver.storageclass.storage.k8s.io/persistentvolumeclaims:"5"5bronze.storageclass.storage.k8s.io/requests.storage:"0"6bronze.storageclass.storage.k8s.io/persistentvolumeclaims:"0"7Copy to ClipboardCopied!Toggle word wrapToggle overflow1The total number of persistent volume claims in a project.2Across all persistent volume claims in a project, the sum of storage requested cannot exceed this value.3Across all persistent volume claims in a project, the sum of storage requested in the gold storage class cannot exceed this value.4Across all persistent volume claims in a project, the sum of storage requested in the silver storage class cannot exceed this value.5Across all persistent volume claims in a project, the total number of claims in the silver storage class cannot exceed this value.6Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot request storage.7Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot create claims.Create a project request template from the modifiedtemplate.yamlfile in theopenshift-confignamespace:oc create -f template.yaml -n openshift-config$oc create-ftemplate.yaml-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowTo include the configuration as akubectl.kubernetes.io/last-applied-configurationannotation, add the--save-configoption to theoc createcommand.By default, the template is calledproject-request.If a project request template already exists within a cluster:If you declaratively or imperatively manage objects within your cluster by using configuration files, edit the existing project request template through those files instead.List templates in theopenshift-confignamespace:oc get templates -n openshift-config$oc get templates-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowEdit an existing project request template:oc edit template <project_request_template> -n openshift-config$oc edit template<project_request_template>-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd a resource quota definition, such as the precedingstorage-consumptionexample, into the existing template. The definition must be added before theparameters:section in the template.

Add a resource quota definition to a project request template:

- If a project request template does not exist in a cluster:Create a bootstrap project template and output it to a file calledtemplate.yaml:oc adm create-bootstrap-project-template -o yaml > template.yaml$oc adm create-bootstrap-project-template-oyaml>template.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd a resource quota definition totemplate.yaml. The following example defines a resource quota named 'storage-consumption'. The definition must be added before theparameters:section in the template:- apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: storage-consumption
    namespace: ${PROJECT_NAME}
  spec:
    hard:
      persistentvolumeclaims: "10" 
      requests.storage: "50Gi" 
      gold.storageclass.storage.k8s.io/requests.storage: "10Gi" 
      silver.storageclass.storage.k8s.io/requests.storage: "20Gi" 
      silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5" 
      bronze.storageclass.storage.k8s.io/requests.storage: "0" 
      bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"-apiVersion:v1kind:ResourceQuotametadata:name:storage-consumptionnamespace:${PROJECT_NAME}spec:hard:persistentvolumeclaims:"10"1requests.storage:"50Gi"2gold.storageclass.storage.k8s.io/requests.storage:"10Gi"3silver.storageclass.storage.k8s.io/requests.storage:"20Gi"4silver.storageclass.storage.k8s.io/persistentvolumeclaims:"5"5bronze.storageclass.storage.k8s.io/requests.storage:"0"6bronze.storageclass.storage.k8s.io/persistentvolumeclaims:"0"7Copy to ClipboardCopied!Toggle word wrapToggle overflow1The total number of persistent volume claims in a project.2Across all persistent volume claims in a project, the sum of storage requested cannot exceed this value.3Across all persistent volume claims in a project, the sum of storage requested in the gold storage class cannot exceed this value.4Across all persistent volume claims in a project, the sum of storage requested in the silver storage class cannot exceed this value.5Across all persistent volume claims in a project, the total number of claims in the silver storage class cannot exceed this value.6Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot request storage.7Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot create claims.Create a project request template from the modifiedtemplate.yamlfile in theopenshift-confignamespace:oc create -f template.yaml -n openshift-config$oc create-ftemplate.yaml-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowTo include the configuration as akubectl.kubernetes.io/last-applied-configurationannotation, add the--save-configoption to theoc createcommand.By default, the template is calledproject-request.

If a project request template does not exist in a cluster:

- Create a bootstrap project template and output it to a file calledtemplate.yaml:oc adm create-bootstrap-project-template -o yaml > template.yaml$oc adm create-bootstrap-project-template-oyaml>template.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a bootstrap project template and output it to a file calledtemplate.yaml:

- Add a resource quota definition totemplate.yaml. The following example defines a resource quota named 'storage-consumption'. The definition must be added before theparameters:section in the template:- apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: storage-consumption
    namespace: ${PROJECT_NAME}
  spec:
    hard:
      persistentvolumeclaims: "10" 
      requests.storage: "50Gi" 
      gold.storageclass.storage.k8s.io/requests.storage: "10Gi" 
      silver.storageclass.storage.k8s.io/requests.storage: "20Gi" 
      silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5" 
      bronze.storageclass.storage.k8s.io/requests.storage: "0" 
      bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"-apiVersion:v1kind:ResourceQuotametadata:name:storage-consumptionnamespace:${PROJECT_NAME}spec:hard:persistentvolumeclaims:"10"1requests.storage:"50Gi"2gold.storageclass.storage.k8s.io/requests.storage:"10Gi"3silver.storageclass.storage.k8s.io/requests.storage:"20Gi"4silver.storageclass.storage.k8s.io/persistentvolumeclaims:"5"5bronze.storageclass.storage.k8s.io/requests.storage:"0"6bronze.storageclass.storage.k8s.io/persistentvolumeclaims:"0"7Copy to ClipboardCopied!Toggle word wrapToggle overflow1The total number of persistent volume claims in a project.2Across all persistent volume claims in a project, the sum of storage requested cannot exceed this value.3Across all persistent volume claims in a project, the sum of storage requested in the gold storage class cannot exceed this value.4Across all persistent volume claims in a project, the sum of storage requested in the silver storage class cannot exceed this value.5Across all persistent volume claims in a project, the total number of claims in the silver storage class cannot exceed this value.6Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot request storage.7Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot create claims.

Add a resource quota definition totemplate.yaml. The following example defines a resource quota named 'storage-consumption'. The definition must be added before theparameters:section in the template:

```
- apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: storage-consumption
    namespace: ${PROJECT_NAME}
  spec:
    hard:
      persistentvolumeclaims: "10" 
      requests.storage: "50Gi" 
      gold.storageclass.storage.k8s.io/requests.storage: "10Gi" 
      silver.storageclass.storage.k8s.io/requests.storage: "20Gi" 
      silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5" 
      bronze.storageclass.storage.k8s.io/requests.storage: "0" 
      bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"
```

```
- apiVersion: v1
  kind: ResourceQuota
  metadata:
    name: storage-consumption
    namespace: ${PROJECT_NAME}
  spec:
    hard:
      persistentvolumeclaims: "10"
```

```
requests.storage: "50Gi"
```

```
gold.storageclass.storage.k8s.io/requests.storage: "10Gi"
```

```
silver.storageclass.storage.k8s.io/requests.storage: "20Gi"
```

```
silver.storageclass.storage.k8s.io/persistentvolumeclaims: "5"
```

```
bronze.storageclass.storage.k8s.io/requests.storage: "0"
```

```
bronze.storageclass.storage.k8s.io/persistentvolumeclaims: "0"
```

**1**
  The total number of persistent volume claims in a project.

**2**
  Across all persistent volume claims in a project, the sum of storage requested cannot exceed this value.

**3**
  Across all persistent volume claims in a project, the sum of storage requested in the gold storage class cannot exceed this value.

**4**
  Across all persistent volume claims in a project, the sum of storage requested in the silver storage class cannot exceed this value.

**5**
  Across all persistent volume claims in a project, the total number of claims in the silver storage class cannot exceed this value.

**6**
  Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot request storage.

**7**
  Across all persistent volume claims in a project, the sum of storage requested in the bronze storage class cannot exceed this value. When this value is set to0, the bronze storage class cannot create claims.
- Create a project request template from the modifiedtemplate.yamlfile in theopenshift-confignamespace:oc create -f template.yaml -n openshift-config$oc create-ftemplate.yaml-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowTo include the configuration as akubectl.kubernetes.io/last-applied-configurationannotation, add the--save-configoption to theoc createcommand.By default, the template is calledproject-request.

Create a project request template from the modifiedtemplate.yamlfile in theopenshift-confignamespace:

To include the configuration as akubectl.kubernetes.io/last-applied-configurationannotation, add the--save-configoption to theoc createcommand.

By default, the template is calledproject-request.

- If a project request template already exists within a cluster:If you declaratively or imperatively manage objects within your cluster by using configuration files, edit the existing project request template through those files instead.List templates in theopenshift-confignamespace:oc get templates -n openshift-config$oc get templates-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowEdit an existing project request template:oc edit template <project_request_template> -n openshift-config$oc edit template<project_request_template>-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflowAdd a resource quota definition, such as the precedingstorage-consumptionexample, into the existing template. The definition must be added before theparameters:section in the template.

If a project request template already exists within a cluster:

If you declaratively or imperatively manage objects within your cluster by using configuration files, edit the existing project request template through those files instead.

- List templates in theopenshift-confignamespace:oc get templates -n openshift-config$oc get templates-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflow

List templates in theopenshift-confignamespace:

- Edit an existing project request template:oc edit template <project_request_template> -n openshift-config$oc edit template<project_request_template>-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit an existing project request template:

- Add a resource quota definition, such as the precedingstorage-consumptionexample, into the existing template. The definition must be added before theparameters:section in the template.
- If you created a project request template, reference it in the cluster’s project configuration resource:Access the project configuration resource for editing:By using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.By using the CLI:Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflowUpdate thespecsection of the project configuration resource to include theprojectRequestTemplateandnameparameters. The following example references the default project request template nameproject-request:apiVersion: config.openshift.io/v1
kind: Project
metadata:
#  ...
spec:
  projectRequestTemplate:
    name: project-requestapiVersion:config.openshift.io/v1kind:Projectmetadata:#  ...spec:projectRequestTemplate:name:project-requestCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you created a project request template, reference it in the cluster’s project configuration resource:

- Access the project configuration resource for editing:By using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.By using the CLI:Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Access the project configuration resource for editing:

- By using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.

By using the web console:

- Navigate to theAdministrationCluster Settingspage.
- ClickConfigurationto view all configuration resources.
- Find the entry forProjectand clickEdit YAML.
- By using the CLI:Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

By using the CLI:

- Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theproject.config.openshift.io/clusterresource:

- Update thespecsection of the project configuration resource to include theprojectRequestTemplateandnameparameters. The following example references the default project request template nameproject-request:apiVersion: config.openshift.io/v1
kind: Project
metadata:
#  ...
spec:
  projectRequestTemplate:
    name: project-requestapiVersion:config.openshift.io/v1kind:Projectmetadata:#  ...spec:projectRequestTemplate:name:project-requestCopy to ClipboardCopied!Toggle word wrapToggle overflow

Update thespecsection of the project configuration resource to include theprojectRequestTemplateandnameparameters. The following example references the default project request template nameproject-request:

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
#  ...
spec:
  projectRequestTemplate:
    name: project-request
```

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
#  ...
spec:
  projectRequestTemplate:
    name: project-request
```

- Verify that the resource quota is applied when projects are created:Create a project:oc new-project <project_name>$oc new-project<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowList the project’s resource quotas:oc get resourcequotas$oc get resourcequotasCopy to ClipboardCopied!Toggle word wrapToggle overflowDescribe the resource quota in detail:oc describe resourcequotas <resource_quota_name>$oc describe resourcequotas<resource_quota_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the resource quota is applied when projects are created:

- Create a project:oc new-project <project_name>$oc new-project<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Create a project:

- List the project’s resource quotas:oc get resourcequotas$oc get resourcequotasCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the project’s resource quotas:

- Describe the resource quota in detail:oc describe resourcequotas <resource_quota_name>$oc describe resourcequotas<resource_quota_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Describe the resource quota in detail:

## 8.2. Resource quotas across multiple projectsCopy linkLink copied to clipboard!

A multi-project quota, defined by aClusterResourceQuotaobject, allows quotas to be shared across multiple projects. Resources used in each selected project are aggregated and that aggregate is used to limit resources across all the selected projects.

This guide describes how cluster administrators can set and manage resource quotas across multiple projects.

Do not run workloads in or share access to default projects. Default projects are reserved for running core cluster components.

The following default projects are considered highly privileged:default,kube-public,kube-system,openshift,openshift-infra,openshift-node, and other system-created projects that have theopenshift.io/run-levellabel set to0or1. Functionality that relies on admission plugins, such as pod security admission, security context constraints, cluster resource quotas, and image reference resolution, does not work in highly privileged projects.

### 8.2.1. Selecting multiple projects during quota creationCopy linkLink copied to clipboard!

When creating quotas, you can select multiple projects based on annotation selection, label selection, or both.

Procedure

- To select projects based on annotations, run the following command:oc create clusterquota for-user \
     --project-annotation-selector openshift.io/requester=<user_name> \
     --hard pods=10 \
     --hard secrets=20$oc create clusterquota for-user\--project-annotation-selector openshift.io/requester=<user_name>\--hardpods=10\--hardsecrets=20Copy to ClipboardCopied!Toggle word wrapToggle overflowThis creates the followingClusterResourceQuotaobject:apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  name: for-user
spec:
  quota: 
    hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations: 
      openshift.io/requester: <user_name>
    labels: null 
status:
  namespaces: 
  - namespace: ns-one
    status:
      hard:
        pods: "10"
        secrets: "20"
      used:
        pods: "1"
        secrets: "9"
  total: 
    hard:
      pods: "10"
      secrets: "20"
    used:
      pods: "1"
      secrets: "9"apiVersion:quota.openshift.io/v1kind:ClusterResourceQuotametadata:name:for-userspec:quota:1hard:pods:"10"secrets:"20"selector:annotations:2openshift.io/requester:<user_name>labels:null3status:namespaces:4-namespace:ns-onestatus:hard:pods:"10"secrets:"20"used:pods:"1"secrets:"9"total:5hard:pods:"10"secrets:"20"used:pods:"1"secrets:"9"Copy to ClipboardCopied!Toggle word wrapToggle overflow1TheResourceQuotaSpecobject that will be enforced over the selected projects.2A simple key-value selector for annotations.3A label selector that can be used to select projects.4A per-namespace map that describes current quota usage in each selected project.5The aggregate usage across all selected projects.This multi-project quota document controls all projects requested by<user_name>using the default project request endpoint. You are limited to 10 pods and 20 secrets.

To select projects based on annotations, run the following command:

```
oc create clusterquota for-user \
     --project-annotation-selector openshift.io/requester=<user_name> \
     --hard pods=10 \
     --hard secrets=20
```

```
$ oc create clusterquota for-user \
     --project-annotation-selector openshift.io/requester=<user_name> \
     --hard pods=10 \
     --hard secrets=20
```

This creates the followingClusterResourceQuotaobject:

```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  name: for-user
spec:
  quota: 
    hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations: 
      openshift.io/requester: <user_name>
    labels: null 
status:
  namespaces: 
  - namespace: ns-one
    status:
      hard:
        pods: "10"
        secrets: "20"
      used:
        pods: "1"
        secrets: "9"
  total: 
    hard:
      pods: "10"
      secrets: "20"
    used:
      pods: "1"
      secrets: "9"
```

```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  name: for-user
spec:
  quota:
```

```
hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations:
```

```
openshift.io/requester: <user_name>
    labels: null
```

```
status:
  namespaces:
```

```
- namespace: ns-one
    status:
      hard:
        pods: "10"
        secrets: "20"
      used:
        pods: "1"
        secrets: "9"
  total:
```

```
hard:
      pods: "10"
      secrets: "20"
    used:
      pods: "1"
      secrets: "9"
```

**1**
  TheResourceQuotaSpecobject that will be enforced over the selected projects.

**2**
  A simple key-value selector for annotations.

**3**
  A label selector that can be used to select projects.

**4**
  A per-namespace map that describes current quota usage in each selected project.

**5**
  The aggregate usage across all selected projects.

This multi-project quota document controls all projects requested by<user_name>using the default project request endpoint. You are limited to 10 pods and 20 secrets.

- Similarly, to select projects based on labels, run this command:oc create clusterresourcequota for-name \
    --project-label-selector=name=frontend \
    --hard=pods=10 --hard=secrets=20$oc create clusterresourcequota for-name\1--project-label-selector=name=frontend \2--hard=pods=10 --hard=secrets=20Copy to ClipboardCopied!Toggle word wrapToggle overflow1Bothclusterresourcequotaandclusterquotaare aliases of the same command.for-nameis the name of theClusterResourceQuotaobject.2To select projects by label, provide a key-value pair by using the format--project-label-selector=key=value.This creates the followingClusterResourceQuotaobject definition:apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  creationTimestamp: null
  name: for-name
spec:
  quota:
    hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations: null
    labels:
      matchLabels:
        name: frontendapiVersion:quota.openshift.io/v1kind:ClusterResourceQuotametadata:creationTimestamp:nullname:for-namespec:quota:hard:pods:"10"secrets:"20"selector:annotations:nulllabels:matchLabels:name:frontendCopy to ClipboardCopied!Toggle word wrapToggle overflow

Similarly, to select projects based on labels, run this command:

```
oc create clusterresourcequota for-name \
    --project-label-selector=name=frontend \
    --hard=pods=10 --hard=secrets=20
```

```
--project-label-selector=name=frontend \
```

```
--hard=pods=10 --hard=secrets=20
```

**1**
  Bothclusterresourcequotaandclusterquotaare aliases of the same command.for-nameis the name of theClusterResourceQuotaobject.

**2**
  To select projects by label, provide a key-value pair by using the format--project-label-selector=key=value.

This creates the followingClusterResourceQuotaobject definition:

```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  creationTimestamp: null
  name: for-name
spec:
  quota:
    hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations: null
    labels:
      matchLabels:
        name: frontend
```

```
apiVersion: quota.openshift.io/v1
kind: ClusterResourceQuota
metadata:
  creationTimestamp: null
  name: for-name
spec:
  quota:
    hard:
      pods: "10"
      secrets: "20"
  selector:
    annotations: null
    labels:
      matchLabels:
        name: frontend
```

### 8.2.2. Viewing applicable cluster resource quotasCopy linkLink copied to clipboard!

A project administrator is not allowed to create or modify the multi-project quota that limits his or her project, but the administrator is allowed to view the multi-project quota documents that are applied to his or her project. The project administrator can do this via theAppliedClusterResourceQuotaresource.

Procedure

- To view quotas applied to a project, run:oc describe AppliedClusterResourceQuota$oc describe AppliedClusterResourceQuotaCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:   for-user
Namespace:  <none>
Created:  19 hours ago
Labels:   <none>
Annotations:  <none>
Label Selector: <null>
AnnotationSelector: map[openshift.io/requester:<user-name>]
Resource  Used  Hard
--------  ----  ----
pods        1     10
secrets     9     20Name:   for-user
Namespace:  <none>
Created:  19 hours ago
Labels:   <none>
Annotations:  <none>
Label Selector: <null>
AnnotationSelector: map[openshift.io/requester:<user-name>]
Resource  Used  Hard
--------  ----  ----
pods        1     10
secrets     9     20Copy to ClipboardCopied!Toggle word wrapToggle overflow

To view quotas applied to a project, run:

Example output

```
Name:   for-user
Namespace:  <none>
Created:  19 hours ago
Labels:   <none>
Annotations:  <none>
Label Selector: <null>
AnnotationSelector: map[openshift.io/requester:<user-name>]
Resource  Used  Hard
--------  ----  ----
pods        1     10
secrets     9     20
```

```
Name:   for-user
Namespace:  <none>
Created:  19 hours ago
Labels:   <none>
Annotations:  <none>
Label Selector: <null>
AnnotationSelector: map[openshift.io/requester:<user-name>]
Resource  Used  Hard
--------  ----  ----
pods        1     10
secrets     9     20
```

### 8.2.3. Selection granularityCopy linkLink copied to clipboard!

Because of the locking consideration when claiming quota allocations, the number of active projects selected by a multi-project quota is an important consideration. Selecting more than 100 projects under a single multi-project quota can have detrimental effects on API server responsiveness in those projects.
