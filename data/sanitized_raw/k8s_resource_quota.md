<!-- source: k8s_resource_quota.md -->

# Policy - ResourceQuota

---
Source: https://kubernetes.io/docs/concepts/policy/resource-quotas/
---

# Resource Quotas

When several users or teams share a cluster with a fixed number of nodes,
there is a concern that one team could use more than its fair share of resources.

Resource quotasare a tool for administrators to address this concern.

A resource quota, defined by a ResourceQuota object, provides constraints that limit
aggregate resource consumption pernamespace. A ResourceQuota can also
limit thequantity of objects that can be created in a namespaceby API kind, as well as the total
amount ofinfrastructure resourcesthat may be consumed by
API objects found in that namespace.

#### Caution:

## How Kubernetes ResourceQuotas work

ResourceQuotas work like this:

- Different teams work in different namespaces. This separation can be enforced withRBACor any otherauthorizationmechanism.

Different teams work in different namespaces. This separation can be enforced withRBACor any otherauthorizationmechanism.

- A cluster administrator creates at least one ResourceQuota for each namespace.To make sure the enforcement stays enforced, the cluster administrator should also restrict access to delete or update
that ResourceQuota; for example, by defining aValidatingAdmissionPolicy.

A cluster administrator creates at least one ResourceQuota for each namespace.

- To make sure the enforcement stays enforced, the cluster administrator should also restrict access to delete or update
that ResourceQuota; for example, by defining aValidatingAdmissionPolicy.
- Users create resources (pods, services, etc.) in the namespace, and the quota system
tracks usage to ensure it does not exceed hard resource limits defined in a ResourceQuota.You can apply ascopeto a ResourceQuota to limit where it applies,

Users create resources (pods, services, etc.) in the namespace, and the quota system
tracks usage to ensure it does not exceed hard resource limits defined in a ResourceQuota.

You can apply ascopeto a ResourceQuota to limit where it applies,

- If creating or updating a resource violates a quota constraint, the control plane rejects that request with HTTP
status code403 Forbidden. The error includes a message explaining the constraint that would have been violated.

If creating or updating a resource violates a quota constraint, the control plane rejects that request with HTTP
status code403 Forbidden. The error includes a message explaining the constraint that would have been violated.

- If quotas are enabled in a namespace forresourcesuch ascpuandmemory, users must specify requests or limits for those values when they define a Pod; otherwise,
the quota system may reject pod creation.The resource quotawalkthroughshows an example of how to avoid this problem.

If quotas are enabled in a namespace forresourcesuch ascpuandmemory, users must specify requests or limits for those values when they define a Pod; otherwise,
the quota system may reject pod creation.

The resource quotawalkthroughshows an example of how to avoid this problem.

#### Note:

- You can define aLimitRangeto force defaults on pods that make no compute resource requirements (so that users don't have to remember to do that).

You often do not create Pods directly; for example, you more usually create aworkload managementobject such as aDeployment. If you create a Deployment that tries to use more
resources than are available, the creation of the Deployment (or other workload management object)succeeds, but
the Deployment may not be able to get all of the Pods it manages to exist. In that case you can check the status of
the Deployment, for example withkubectl describe, to see what has happened.

- Forcpuandmemoryresources, ResourceQuotas enforce thatevery(new) pod in that namespace sets a limit for that resource.
If you enforce a resource quota in a namespace for eithercpuormemory,
you and other clients,mustspecify eitherrequestsorlimitsfor that resource,
for every new Pod you submit. If you don't, the control plane may reject admission
for that Pod.
- For other resources: ResourceQuota works and will ignore pods in the namespace without
setting a limit or request for that resource. It means that you can create a new pod
without limit/request for ephemeral storage if the resource quota limits the ephemeral
storage of this namespace.

You can use aLimitRangeto automatically set
a default request for these resources.

The name of a ResourceQuota object must be a validDNS subdomain name.

Examples of policies that could be created using namespaces and quotas are:

- In a cluster with a capacity of 32 GiB RAM, and 16 cores, let team A use 20 GiB and 10 cores,
let B use 10GiB and 4 cores, and hold 2GiB and 2 cores in reserve for future allocation.
- Limit the "testing" namespace to using 1 core and 1GiB RAM. Let the "production" namespace
use any amount.

In the case where the total capacity of the cluster is less than the sum of the quotas of the namespaces,
there may be contention for resources. This is handled on a first-come-first-served basis.

## Enabling Resource Quota

ResourceQuota support is enabled by default for many Kubernetes distributions. It is
enabled when theAPI server--enable-admission-plugins=flag hasResourceQuotaas
one of its arguments.

A resource quota is enforced in a particular namespace when there is a
ResourceQuota in that namespace.

## Types of resource quota

The ResourceQuota mechanism lets you enforce different kinds of limits. This
section describes the types of limit that you can enforce.

### Quota for infrastructure resources

You can limit the total sum ofcompute resourcesthat can be requested in a given namespace.

The following resource types are supported:

| Resource Name | Description |
| --- | --- |
| limits.cpu | Across all pods in a non-terminal state, the sum of CPU limits cannot exceed this value. |
| limits.memory | Across all pods in a non-terminal state, the sum of memory limits cannot exceed this value. |
| requests.cpu | Across all pods in a non-terminal state, the sum of CPU requests cannot exceed this value. |
| requests.memory | Across all pods in a non-terminal state, the sum of memory requests cannot exceed this value. |
| hugepages-<size> | Across all pods in a non-terminal state, the number of huge page requests of the specified size cann |
| cpu | Same asrequests.cpu |
| memory | Same asrequests.memory |

### Quota for extended resources

In addition to the resources mentioned above, in release 1.10, quota support forextended resourcesis added.

As overcommit is not allowed for extended resources, it makes no sense to specify bothrequestsandlimitsfor the same extended resource in a quota. So for extended resources, only quota items
with prefixrequests.are allowed.

Take the GPU resource as an example, if the resource name isnvidia.com/gpu, and you want to
limit the total number of GPUs requested in a namespace to 4, you can define a quota as follows:

- requests.nvidia.com/gpu: 4

SeeViewing and Setting Quotasfor more details.

### Quota for DRA resource claims

DRA (Dynamic Resource Allocation) resource claims can request DRA resources by device class. For an example
device class namedexamplegpu, you want to limit the total number of GPUs requested in a namespace to 4,
you can define a quota as follows:

- examplegpu.deviceclass.resource.k8s.io/devices: 4

WhenExtended Resource allocation by DRAis enabled, the same device class namedexamplegpucan be requested via extended resource either explicitly
when the device class's ExtendedResourceName field is given, say,example.com/gpu, then you can define a quota as follows:

- requests.example.com/gpu: 4

or implicitly using the derived extended resource name from device class nameexamplegpu, you can define
a quota as follows:

- requests.deviceclass.resource.kubernetes.io/examplegpu: 4

All devices requested from resource claims or extended resources are counted towards all three quotas
listed above. The extended resource quota e.g.requests.example.com/gpu: 4, also counts the devices provided
by device plugin.

SeeViewing and Setting Quotasfor more details.

### Quota for storage

You can limit the total sum ofstoragefor volumes
that can be requested in a given namespace.

In addition, you can limit consumption of storage resources based on associatedStorageClass.

| Resource Name | Description |
| --- | --- |
| requests.storage | Across all persistent volume claims, the sum of storage requests cannot exceed this value. |
| persistentvolumeclaims | The total number ofPersistentVolumeClaimsthat can exist in the namespace. |
| <storage-class-name>.storageclass.storage.k8s.io/requests.storage | Across all persistent volume claims associated with the<storage-class-name>, the sum of storage requ |
| <storage-class-name>.storageclass.storage.k8s.io/persistentvolumeclaims | Across all persistent volume claims associated with the<storage-class-name>, the total number ofpers |

For example, if you want to quota storage withgoldStorageClass separate from
abronzeStorageClass, you can define a quota as follows:

- gold.storageclass.storage.k8s.io/requests.storage: 500Gi
- bronze.storageclass.storage.k8s.io/requests.storage: 100Gi

#### Quota for local ephemeral storage

| Resource Name | Description |
| --- | --- |
| requests.ephemeral-storage | Across all pods in the namespace, the sum of local ephemeral storage requests cannot exceed this val |
| limits.ephemeral-storage | Across all pods in the namespace, the sum of local ephemeral storage limits cannot exceed this value |
| ephemeral-storage | Same asrequests.ephemeral-storage. |

#### Note:

When using a CRI container runtime, container logs will count against the ephemeral storage quota.
This can result in the unexpected eviction of pods that have exhausted their storage quotas.

Refer toLogging Architecturefor details.

### Quota on object count

You can set quota forthe total number of one particularresourcekindin the Kubernetes API,
using the following syntax:

- count/<resource>.<group>for resources from non-core API groups
- count/<resource>for resources from the core API group

For example, the PodTemplate API is in the core API group and so if you want to limit the number of
PodTemplate objects in a namespace, you usecount/podtemplates.

These types of quotas are useful to protect against exhaustion of control plane storage. For example, you may
want to limit the number of Secrets in a server given their large size. Too many Secrets in a cluster can
actually prevent servers and controllers from starting. You can set a quota for Jobs to protect against
a poorly configured CronJob. CronJobs that create too many Jobs in a namespace can lead to a denial of service.

If you define a quota this way, it applies to Kubernetes' APIs that are part of the API server, and
to any custom resources backed by a CustomResourceDefinition.
For example, to create a quota on awidgetscustom resource in theexample.comAPI group,
usecount/widgets.example.com.
If you useAPI aggregationto
add additional, custom APIs that are not defined as CustomResourceDefinitions, the core Kubernetes
control plane does not enforce quota for the aggregated API. The extension API server is expected to
provide quota enforcement if that's appropriate for the custom API.

##### Generic syntax

This is a list of common examples of object kinds that you may want to put under object count quota,
listed by the configuration string that you would use.

- count/pods
- count/persistentvolumeclaims
- count/services
- count/secrets
- count/configmaps
- count/deployments.apps
- count/replicasets.apps
- count/statefulsets.apps
- count/jobs.batch
- count/cronjobs.batch

##### Specialized syntax

There is another syntax only to set the same type of quota, that only works for certain API kinds.
The following types are supported:

| Resource Name | Description |
| --- | --- |
| configmaps | The total number of ConfigMaps that can exist in the namespace. |
| persistentvolumeclaims | The total number ofPersistentVolumeClaimsthat can exist in the namespace. |
| pods | The total number of Pods in a non-terminal state that can exist in the namespace. A pod is in a term |
| replicationcontrollers | The total number of ReplicationControllers that can exist in the namespace. |
| resourcequotas | The total number of ResourceQuotas that can exist in the namespace. |
| services | The total number of Services that can exist in the namespace. |
| services.loadbalancers | The total number of Services of typeLoadBalancerthat can exist in the namespace. |
| services.nodeports | The total number ofNodePortsallocated to Services of typeNodePortorLoadBalancerthat can exist in the |
| secrets | The total number of Secrets that can exist in the namespace. |

For example,podsquota counts and enforces a maximum on the number ofpodscreated in a single namespace that are not terminal. You might want to set apodsquota on a namespace to avoid the case where a user creates many small pods and
exhausts the cluster's supply of Pod IPs.

You can find more examples onViewing and Setting Quotas.

## Viewing and Setting Quotas

kubectl supports creating, updating, and viewing quotas:

```
kubectl create namespace myspace
```

```
cat <<EOF > compute-resources.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-resources
spec:
  hard:
    requests.cpu: "1"
    requests.memory: "1Gi"
    limits.cpu: "2"
    limits.memory: "2Gi"
    requests.nvidia.com/gpu: 4
EOF
```

```
kubectl create -f ./compute-resources.yaml --namespace=myspace
```

```
cat <<EOF > object-counts.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: object-counts
spec:
  hard:
    configmaps: "10"
    persistentvolumeclaims: "4"
    pods: "4"
    replicationcontrollers: "20"
    secrets: "10"
    services: "10"
    services.loadbalancers: "2"
EOF
```

```
kubectl create -f ./object-counts.yaml --namespace=myspace
```

```
kubectl get quota --namespace=myspace
```

```
NAME                    AGE
compute-resources       30s
object-counts           32s
```

```
kubectl describe quota compute-resources --namespace=myspace
```

```
Name:                    compute-resources
Namespace:               myspace
Resource                 Used  Hard
--------                 ----  ----
limits.cpu               0     2
limits.memory            0     2Gi
requests.cpu             0     1
requests.memory          0     1Gi
requests.nvidia.com/gpu  0     4
```

```
kubectl describe quota object-counts --namespace=myspace
```

```
Name:                   object-counts
Namespace:              myspace
Resource                Used    Hard
--------                ----    ----
configmaps              0       10
persistentvolumeclaims  0       4
pods                    0       4
replicationcontrollers  0       20
secrets                 1       10
services                0       10
services.loadbalancers  0       2
```

kubectl also supports object count quota for all standard namespaced resources
using the syntaxcount/<resource>.<group>:

```
kubectl create namespace myspace
```

```
kubectl create quota test --hard=count/deployments.apps=2,count/replicasets.apps=4,count/pods=3,count/secrets=4 --namespace=myspace
```

```
kubectl create deployment nginx --image=nginx --namespace=myspace --replicas=2
```

```
kubectl describe quota --namespace=myspace
```

```
Name:                         test
Namespace:                    myspace
Resource                      Used  Hard
--------                      ----  ----
count/deployments.apps        1     2
count/pods                    2     3
count/replicasets.apps        1     4
count/secrets                 1     4
```

## Quota and Cluster Capacity

ResourceQuotas are independent of the cluster capacity. They are
expressed in absolute units. So, if you add nodes to your cluster, this doesnotautomatically give each namespace the ability to consume more resources.

Sometimes more complex policies may be desired, such as:

- Proportionally divide total cluster resources among several teams.
- Allow each tenant to grow resource usage as needed, but have a generous
limit to prevent accidental resource exhaustion.
- Detect demand from one namespace, add nodes, and increase quota.

Such policies could be implemented usingResourceQuotasas building blocks, by
writing a "controller" that watches the quota usage and adjusts the quota
hard limits of each namespace according to other signals.

Note that resource quota divides up aggregate cluster resources, but it creates no
restrictions around nodes: pods from several namespaces may run on the same node.

## Quota scopes

Each quota can have an associated set ofscopes. A quota will only measure usage for a resource if it matches
the intersection of enumerated scopes.

When a scope is added to the quota, it limits the number of resources it supports to those that pertain to the scope.
Resources specified on the quota outside of the allowed set results in a validation error.

Kubernetes 1.35 supports the following scopes:

| Scope | Description |
| --- | --- |
| BestEffort | Match pods that have best effort quality of service. |
| CrossNamespacePodAffinity | Match pods that have cross-namespace pod(anti)affinity terms. |
| NotBestEffort | Match pods that do not have best effort quality of service. |
| NotTerminating | Match pods where.spec.activeDeadlineSecondsisnil |
| PriorityClass | Match pods that references the specifiedpriority class. |
| Terminating | Match pods where.spec.activeDeadlineSeconds>=0 |
| VolumeAttributesClass | Match PersistentVolumeClaims that reference the specifiedvolume attributes class. |

ResourceQuotas with a scope set can also have a optionalscopeSelectorfield. You define one or morematch expressionsthat specify anoperatorsand, if relevant, a set ofvaluesto match. For example:

```
scopeSelector:
    matchExpressions:
      - scopeName: BestEffort # Match pods that have best effort quality of service
        operator: Exists # optional; "Exists" is implied for BestEffort scope
```

ThescopeSelectorsupports the following values in theoperatorfield:

- In
- NotIn
- Exists
- DoesNotExist

If theoperatorisInorNotIn, thevaluesfield must have at least
one value. For example:

```
scopeSelector:
    matchExpressions:
      - scopeName: PriorityClass
        operator: In
        values:
          - middle
```

If theoperatorisExistsorDoesNotExist, thevaluesfield mustNOTbe
specified.

### Best effort Pods scope

This scope only tracks quota consumed by Pods.
It only matches pods that have thebest effortQoS class.

Theoperatorfor ascopeSelectormust beExists.

### Not-best-effort Pods scope

This scope only tracks quota consumed by Pods.
It only matches pods that have theGuaranteedorBurstableQoS class.

Theoperatorfor ascopeSelectormust beExists.

### Non-terminating Pods scope

This scope only tracks quota consumed by Pods that are not terminating. Theoperatorfor ascopeSelectormust beExists.

A Pod is not terminating if the.spec.activeDeadlineSecondsfield is unset.

You can use a ResourceQuota with this scope to manage the following resources:

- count.pods
- pods
- cpu
- memory
- requests.cpu
- requests.memory
- limits.cpu
- limits.memory

### Terminating Pods scope

This scope only tracks quota consumed by Pods that are terminating. Theoperatorfor ascopeSelectormust beExists.

A Pod is considered asterminatingif the.spec.activeDeadlineSecondsfield is set to any number.

You can use a ResourceQuota with this scope to manage the following resources:

- count.pods
- pods
- cpu
- memory
- requests.cpu
- requests.memory
- limits.cpu
- limits.memory

### Cross-namespace pod affinity scope

You can useCrossNamespacePodAffinityquota scopeto limit which namespaces are allowed to
have pods with affinity terms that cross namespaces. Specifically, it controls which pods are allowed
to setnamespacesornamespaceSelectorfields in pod(anti)affinity terms.

Preventing users from using cross-namespace affinity terms might be desired since a pod
with anti-affinity constraints can block pods from all other namespaces
from getting scheduled in a failure domain.

Using this scope, you (as a cluster administrator) can prevent certain namespaces - such asfoo-nsin the example below -
from having pods that use cross-namespace pod affinity. You configure this creating a ResourceQuota object in
that namespace withCrossNamespacePodAffinityscope and hard limit of 0:

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: disable-cross-namespace-affinity
  namespace: foo-ns
spec:
  hard:
    pods: "0"
  scopeSelector:
    matchExpressions:
    - scopeName: CrossNamespacePodAffinity
      operator: Exists
```

If you want to disallow usingnamespacesandnamespaceSelectorby default, and
only allow it for specific namespaces, you could configureCrossNamespacePodAffinityas a limited resource by setting the kube-apiserver flag--admission-control-config-fileto the path of the following configuration file:

```
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: "ResourceQuota"
  configuration:
    apiVersion: apiserver.config.k8s.io/v1
    kind: ResourceQuotaConfiguration
    limitedResources:
    - resource: pods
      matchScopes:
      - scopeName: CrossNamespacePodAffinity
        operator: Exists
```

With the above configuration, pods can usenamespacesandnamespaceSelectorin pod affinity only
if the namespace where they are created have a resource quota object withCrossNamespacePodAffinityscope and a hard limit greater than or equal to the number of pods using those fields.

### PriorityClass scope

A ResourceQuota with a PriorityClass scope only matches Pods that have a particularpriority class, and only
if anyscopeSelectorin the quota spec selects a particular Pod.

Pods can be created at a specificpriority.
You can control a pod's consumption of system resources based on a pod's priority, by using thescopeSelectorfield in the quota spec.

When quota is scoped for PriorityClass using thescopeSelectorfield, the ResourceQuota
can only track (and limit) the following resources:

- pods
- cpu
- memory
- ephemeral-storage
- limits.cpu
- limits.memory
- limits.ephemeral-storage
- requests.cpu
- requests.memory
- requests.ephemeral-storage

#### Example

This example creates a ResourceQuota matches it with pods at specific priorities. The example
works as follows:

- Pods in the cluster have one of the threePriorityClasses, "low", "medium", "high".If you want to try this out, use a testing cluster and set up those three PriorityClasses before you continue.
- If you want to try this out, use a testing cluster and set up those three PriorityClasses before you continue.
- One quota object is created for each priority.

Inspect this set of ResourceQuotas:

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pods-high
spec:
  hard:
    cpu: "1000"
    memory: "200Gi"
    pods: "10"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values: ["high"]
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pods-medium
spec:
  hard:
    cpu: "10"
    memory: "20Gi"
    pods: "10"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values: ["medium"]
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pods-low
spec:
  hard:
    cpu: "5"
    memory: "10Gi"
    pods: "10"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values: ["low"]
```

Apply the YAML usingkubectl create.

```
kubectl create -f https://k8s.io/examples/policy/quota.yaml
```

```
resourcequota/pods-high created
resourcequota/pods-medium created
resourcequota/pods-low created
```

Verify thatUsedquota is0usingkubectl describe quota.

```
kubectl describe quota
```

```
Name:       pods-high
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         0     1k
memory      0     200Gi
pods        0     10

Name:       pods-low
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         0     5
memory      0     10Gi
pods        0     10

Name:       pods-medium
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         0     10
memory      0     20Gi
pods        0     10
```

Create a pod with priority "high".

```
apiVersion: v1
kind: Pod
metadata:
  name: high-priority
spec:
  containers:
  - name: high-priority
    image: ubuntu
    command: ["/bin/sh"]
    args: ["-c", "while true; do echo hello; sleep 10;done"]
    resources:
      requests:
        memory: "10Gi"
        cpu: "500m"
      limits:
        memory: "10Gi"
        cpu: "500m"
  priorityClassName: high
```

To create the Pod:

```
kubectl create -f https://k8s.io/examples/policy/high-priority-pod.yaml
```

Verify that "Used" stats for "high" priority quota,pods-high, has changed and that
the other two quotas are unchanged.

```
kubectl describe quota
```

```
Name:       pods-high
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         500m  1k
memory      10Gi  200Gi
pods        1     10

Name:       pods-low
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         0     5
memory      0     10Gi
pods        0     10

Name:       pods-medium
Namespace:  default
Resource    Used  Hard
--------    ----  ----
cpu         0     10
memory      0     20Gi
pods        0     10
```

#### Limiting PriorityClass consumption by default

It may be desired that pods at a particular priority, such as "cluster-services",
should be allowed in a namespace, if and only if, a matching quota object exists.

With this mechanism, operators are able to restrict usage of certain high
priority classes to a limited number of namespaces and not every namespace
will be able to consume these priority classes by default.

To enforce this,kube-apiserverflag--admission-control-config-fileshould be
used to pass path to the following configuration file:

```
apiVersion: apiserver.config.k8s.io/v1
kind: AdmissionConfiguration
plugins:
- name: "ResourceQuota"
  configuration:
    apiVersion: apiserver.config.k8s.io/v1
    kind: ResourceQuotaConfiguration
    limitedResources:
    - resource: pods
      matchScopes:
      - scopeName: PriorityClass
        operator: In
        values: ["cluster-services"]
```

Then, create a resource quota object in thekube-systemnamespace:

```
apiVersion: v1
kind: ResourceQuota
metadata:
  name: pods-cluster-services
spec:
  scopeSelector:
    matchExpressions:
      - operator : In
        scopeName: PriorityClass
        values: ["cluster-services"]
```

```
kubectl apply -f https://k8s.io/examples/policy/priority-class-resourcequota.yaml -n kube-system
```

```
resourcequota/pods-cluster-services created
```

In this case, a pod creation will be allowed if:

- the Pod'spriorityClassNameis not specified.
- the Pod'spriorityClassNameis specified to a value other thancluster-services.
- the Pod'spriorityClassNameis set tocluster-services, it is to be created
in thekube-systemnamespace, and it has passed the resource quota check.

A Pod creation request is rejected if itspriorityClassNameis set tocluster-servicesand it is to be created in a namespace other thankube-system.

### VolumeAttributesClass scope

This scope only tracks quota consumed by PersistentVolumeClaims.

PersistentVolumeClaims can be created with a specificVolumeAttributesClass, and might be modified after creation.
You can control a PVC's consumption of storage resources based on the associated
VolumeAttributesClasses, by using thescopeSelectorfield in the quota spec.

The PVC references the associated VolumeAttributesClass by the following fields:

- spec.volumeAttributesClassName
- status.currentVolumeAttributesClassName
- status.modifyVolumeStatus.targetVolumeAttributesClassName

A relevant ResourceQuota is matched and consumed only if the ResourceQuota has ascopeSelectorthat selects the PVC.

When the quota is scoped for the volume attributes class using thescopeSelectorfield, the quota object is restricted to track only the following resources:

- persistentvolumeclaims
- requests.storage

ReadLimit Storage Consumptionto learn more about this.

## What's next

- See adetailed example for how to use resource quota.
- Read the ResourceQuotaAPI reference
- Learn aboutLimitRanges
- You can read the historicalResourceQuota design documentfor more information.
- You can also read theQuota support for priority class design document.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
