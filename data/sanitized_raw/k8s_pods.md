<!-- source: k8s_pods.md -->

# Workloads

---
Source: https://kubernetes.io/docs/concepts/workloads/pods/
---

# Pods

Podsare the smallest deployable units of computing that you can create and manage in Kubernetes.

APod(as in a pod of whales or pea pod) is a group of one or morecontainers, with shared storage and network resources, and a specification for how to run the containers. A Pod's contents are always co-located and
co-scheduled, and run in a shared context. A Pod models an
application-specific "logical host": it contains one or more application
containers which are relatively tightly coupled.In non-cloud contexts, applications executed on the same physical or virtual machine are analogous to cloud applications executed on the same logical host.

As well as application containers, a Pod can containinit containersthat run
during Pod startup. You can also injectephemeral containersfor debugging a running Pod.

## What is a Pod?

#### Note:

The shared context of a Pod is a set of Linux namespaces, cgroups, and
potentially other facets of isolation - the same things that isolate acontainer. Within a Pod's context, the individual applications may have
further sub-isolations applied.

A Pod is similar to a set of containers with shared namespaces and shared filesystem volumes.

Pods in a Kubernetes cluster are used in two main ways:

- Pods that run a single container. The "one-container-per-Pod" model is the
most common Kubernetes use case; in this case, you can think of a Pod as a
wrapper around a single container; Kubernetes manages Pods rather than managing
the containers directly.

Pods that run a single container. The "one-container-per-Pod" model is the
most common Kubernetes use case; in this case, you can think of a Pod as a
wrapper around a single container; Kubernetes manages Pods rather than managing
the containers directly.

- Pods that run multiple containers that need to work together. A Pod can
encapsulate an application composed ofmultiple co-located containersthat are
tightly coupled and need to share resources. These co-located containers
form a single cohesive unit.Grouping multiple co-located and co-managed containers in a single Pod is a
relatively advanced use case. You should use this pattern only in specific
instances in which your containers are tightly coupled.You don't need to run multiple containers to provide replication (for resilience
or capacity); if you need multiple replicas, seeWorkload management.

Pods that run multiple containers that need to work together. A Pod can
encapsulate an application composed ofmultiple co-located containersthat are
tightly coupled and need to share resources. These co-located containers
form a single cohesive unit.

Grouping multiple co-located and co-managed containers in a single Pod is a
relatively advanced use case. You should use this pattern only in specific
instances in which your containers are tightly coupled.

You don't need to run multiple containers to provide replication (for resilience
or capacity); if you need multiple replicas, seeWorkload management.

## Using Pods

The following is an example of a Pod which consists of a container running the imagenginx:1.14.2.

```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
```

To create the Pod shown above, run the following command:

```
kubectl apply -f https://k8s.io/examples/pods/simple-pod.yaml
```

Pods are generally not created directly and are created using workload resources.SeeWorking with Podsfor more information on how Pods are used
with workload resources.

### Workload resources for managing pods

Usually you don't need to create Pods directly, even singleton Pods. Instead, create them using workload resources such asDeploymentorJob.If your Pods need to track state, consider theStatefulSetresource.

Each Pod is meant to run a single instance of a given application. If you want to
scale your application horizontally (to provide more overall resources by running
more instances), you should use multiple Pods, one for each instance. In
Kubernetes, this is typically referred to asreplication.Replicated Pods are usually created and managed as a group by a workload resource
and itscontroller.

SeePods and controllersfor more information on how
Kubernetes uses workload resources, and their controllers, to implement application
scaling and auto-healing.

Pods natively provide two kinds of shared resources for their constituent containers:networkingandstorage.

## Working with Pods

You'll rarely create individual Pods directly in Kubernetes—even singleton Pods. This
is because Pods are designed as relatively ephemeral, disposable entities. When
a Pod gets created (directly by you, or indirectly by acontroller), the new Pod is
scheduled to run on aNodein your cluster.The Pod remains on that node until the Pod finishes execution, the Pod object is deleted,the Pod isevictedfor lack of resources, or the node fails.

#### Note:

The name of a Pod must be a validDNS subdomainvalue, but this can produce unexpected results for the Pod hostname. For best compatibility,the name should follow the more restrictive rules for aDNS label.

### Pod OS

You should set the.spec.os.namefield to eitherwindowsorlinuxto indicate the OS on
which you want the pod to run. These two are the only operating systems supported for now by
Kubernetes. In the future, this list may be expanded.

In Kubernetes v1.35, the value of.spec.os.namedoes not affect
how thekube-schedulerpicks a node for the Pod to run on. In any cluster where there is more than one operating system for
running nodes, you should set thekubernetes.io/oslabel correctly on each node, and define pods with anodeSelectorbased on the operating system
label. The kube-scheduler assigns your pod to a node based on other criteria and may or may not
succeed in picking a suitable node placement where the node OS is right for the containers in that Pod.ThePod security standardsalso use this
field to avoid enforcing policies that aren't relevant to the operating system.

### Pods and controllers

You can use workload resources to create and manage multiple Pods for you. A controller
for the resource handles replication and rollout and automatic healing in case of
Pod failure. For example, if a Node fails, a controller notices that Pods on that
Node have stopped working and creates a replacement Pod. The scheduler places the
replacement Pod onto a healthy Node.

Here are some examples of workload resources that manage one or more Pods:

- Deployment
- StatefulSet
- DaemonSet

### Specifying a Workload reference

By default, Kubernetes schedules every Pod individually. However, some tightly-coupled applications
need a group of Pods to be scheduled simultaneously to function correctly.

You can link a Pod to aWorkloadobject
using aWorkload reference.This tells thekube-schedulerthat the Pod is part of a specific group,enabling it to make coordinated placement decisions for the entire group at once.

### Pod templates

Controllers forworkloadresources create Pods
from apod templateand manage those Pods on your behalf.

PodTemplates are specifications for creating Pods, and are included in workload resources such asDeployments,Jobs, andDaemonSets.

Each controller for a workload resource uses thePodTemplateinside the workload
object to make actual Pods. ThePodTemplateis part of the desired state of whatever
workload resource you used to run your app.

When you create a Pod, you can includeenvironment variablesin the Pod template for the containers that run in the Pod.

The sample below is a manifest for a simple Job with atemplatethat starts one
container. The container in that Pod prints a message then pauses.

```
apiVersion: batch/v1
kind: Job
metadata:
  name: hello
spec:
  template:
    # This is the pod template
    spec:
      containers:
      - name: hello
        image: busybox:1.28
        command: ['sh', '-c', 'echo "Hello, Kubernetes!" && sleep 3600']
      restartPolicy: OnFailure
    # The pod template ends here
```

Modifying the pod template or switching to a new pod template has no direct effect
on the Pods that already exist. If you change the pod template for a workload
resource, that resource needs to create replacement Pods that use the updated template.

For example, the StatefulSet controller ensures that the running Pods match the current
pod template for each StatefulSet object. If you edit the StatefulSet to change its pod
template, the StatefulSet starts to create new Pods based on the updated template.Eventually, all of the old Pods are replaced with new Pods, and the update is complete.

Each workload resource implements its own rules for handling changes to the Pod template.If you want to read more about StatefulSet specifically, readUpdate strategyin the StatefulSet Basics tutorial.

On Nodes, thekubeletdoes not
directly observe or manage any of the details around pod templates and updates; those
details are abstracted away. That abstraction and separation of concerns simplifies
system semantics, and makes it feasible to extend the cluster's behavior without
changing existing code.

## Pod update and replacement

As mentioned in the previous section, when the Pod template for a workload
resource is changed, the controller creates new Pods based on the updated
template instead of updating or patching the existing Pods.

Kubernetes doesn't prevent you from managing Pods directly. It is possible to
update some fields of a running Pod, in place. However, Pod update operations
likepatch, andreplacehave some limitations:

- Most of the metadata about a Pod is immutable. For example, you cannot
change thenamespace,name,uid, orcreationTimestampfields.

Most of the metadata about a Pod is immutable. For example, you cannot
change thenamespace,name,uid, orcreationTimestampfields.

- If themetadata.deletionTimestampis set, no new entry can be added to themetadata.finalizerslist.

If themetadata.deletionTimestampis set, no new entry can be added to themetadata.finalizerslist.

- Pod updates may not change fields other thanspec.containers[*].image,spec.initContainers[*].image,spec.activeDeadlineSeconds,spec.terminationGracePeriodSeconds,spec.tolerationsorspec.schedulingGates. Forspec.tolerations, you can only add new entries.

Pod updates may not change fields other thanspec.containers[*].image,spec.initContainers[*].image,spec.activeDeadlineSeconds,spec.terminationGracePeriodSeconds,spec.tolerationsorspec.schedulingGates. Forspec.tolerations, you can only add new entries.

- When updating thespec.activeDeadlineSecondsfield, two types of updates
are allowed:setting the unassigned field to a positive number;updating the field from a positive number to a smaller, non-negative
number.

When updating thespec.activeDeadlineSecondsfield, two types of updates
are allowed:

- setting the unassigned field to a positive number;
- updating the field from a positive number to a smaller, non-negative
number.

### Pod subresources

The above update rules apply to regular pod updates, but other pod fields can be updated throughsubresources.

- Resize:Theresizesubresource allows container resources (spec.containers[*].resources) to be updated.SeeResize Container Resourcesfor more details.
- Ephemeral Containers:TheephemeralContainerssubresource allowsephemeral containersto be added to a Pod.SeeEphemeral Containersfor more details.
- Status:Thestatussubresource allows the pod status to be updated.This is typically only used by the Kubelet and other system controllers.
- Binding:Thebindingsubresource allows setting the pod'sspec.nodeNamevia aBindingrequest.This is typically only used by thescheduler.

### Pod generation

- Themetadata.generationfield is unique. It will be automatically set by the
system such that new pods have ametadata.generationof 1, and every update to
mutable fields in the pod's spec will increment themetadata.generationby 1.
- observedGenerationis a field that is captured in thestatussection of the Pod
object. The Kubelet will setstatus.observedGenerationto track the pod state to the current pod status. The pod'sstatus.observedGenerationwill reflect themetadata.generationof the pod at the point that the pod status is being reported.

#### Note:

Different status fields may either be associated with themetadata.generationof the current sync loop, or with themetadata.generationof the previous sync loop. The key distinction is whether a change in thespecis reflected
directly in thestatusor is an indirect result of a running process.

#### Direct Status Updates

For status fields where the allocated spec is directly reflected, theobservedGenerationwill
be associated with the currentmetadata.generation(Generation N).

This behavior applies to:

- Resize Status: The status of a resource resize operation.
- Allocated Resources: The resources allocated to the Pod after a resize.
- Ephemeral Containers: When a new ephemeral container is added, and it is inWaitingstate.

#### Indirect Status Updates

For status fields that are an indirect result of running the spec, theobservedGenerationwill be associated
with themetadata.generationof the previous sync loop (Generation N-1).

This behavior applies to:

- Container Image: TheContainerStatus.ImageIDreflects the image from the previous generation until the new image
is pulled and the container is updated.
- Actual Resources: During an in-progress resize, the actual resources in use still belong to the previous generation's
request.
- Container state: During an in-progress resize, with require restart policy reflects the previous generation's
request.
- activeDeadlineSeconds&terminationGracePeriodSeconds&deletionTimestamp: The effects of these fields on the
Pod's status are a result of the previously observed specification.

## Resource sharing and communication

Pods enable data sharing and communication among their constituent
containers.

### Storage in Pods

A Pod can specify a set of shared storagevolumes. All containers
in the Pod can access the shared volumes, allowing those containers to
share data. Volumes also allow persistent data in a Pod to survive
in case one of the containers within needs to be restarted. SeeStoragefor more information on how
Kubernetes implements shared storage and makes it available to Pods.

### Pod networking

Each Pod is assigned a unique IP address for each address family. Every
container in a Pod shares the network namespace, including the IP address and
network ports. Inside a Pod (andonlythen), the containers that belong to the Pod
can communicate with one another usinglocalhost. When containers in a Pod communicate
with entitiesoutside the Pod,they must coordinate how they use the shared network resources (such as ports).Within a Pod, containers share an IP address and port space, and
can find each other vialocalhost. The containers in a Pod can also communicate
with each other using standard inter-process communications like SystemV semaphores
or POSIX shared memory. Containers in different Pods have distinct IP addresses
and can not communicate by OS-level IPC without special configuration.Containers that want to interact with a container running in a different Pod can
use IP networking to communicate.

Containers within the Pod see the system hostname as being the same as the configurednamefor the Pod. There's more about this in thenetworkingsection.

## Pod security settings

To set security constraints on Pods and containers, you use thesecurityContextfield in the Pod specification. This field gives you
granular control over what a Pod or individual containers can do. SeeAdvanced Pod Configurationfor more details.

For basic security configuration, you should meet the Baseline Pod security standard and run containers as non-root. You can set simple security contexts:

```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: sec-ctx-demo
    image: busybox
    command: ["sh", "-c", "sleep 1h"]
```

For advanced security context configuration including capabilities, seccomp profiles, and detailed security options, see thesecurity conceptssection.

- To learn about kernel-level security constraints that you can use,seeLinux kernel security constraints for Pods and containers.
- To learn more about the Pod security context, seeConfigure a Security Context for a Pod or Container.

## Resource requests and limits

When you specify a Pod, you can optionally specify how much of each resource
a container needs. The most common resources to specify are CPU and memory (RAM).

When you specify the resourcerequestfor containers in a Pod, the
kube-scheduler uses this information to decide which node to place the Pod on.When you specify a resourcelimitfor a container, the kubelet enforces
those limits so that the running container is not allowed to use more of that
resource than the limit you set.

CPU limits are enforced by CPU throttling. When a container approaches its
CPU limit, the kernel restricts its access to CPU. Memory limits are enforced
by the kernel with out-of-memory (OOM) kills when a container exceeds its limit.

#### Note:

For details on resource units, enforcement behavior, and configuration examples,seeResource Management for Pods and Containers.

## Static Pods

Static Podsare managed directly by the kubelet daemon on a specific node,without theAPI serverobserving them.Whereas most Pods are managed by the control plane (for example, aDeployment), for static
Pods, the kubelet directly supervises each static Pod (and restarts it if it fails).

Static Pods are always bound to oneKubeleton a specific node.The main use for static Pods is to run a self-hosted control plane: in other words,using the kubelet to supervise the individualcontrol plane components.

The kubelet automatically tries to create amirror Podon the Kubernetes API server for each static Pod.This means that the Pods running on a node are visible on the API server,but cannot be controlled from there. See the guideCreate static Podsfor more information.

#### Note:

## Pods with multiple containers

Pods are designed to support multiple cooperating processes (as containers) that form
a cohesive unit of service. The containers in a Pod are automatically co-located and
co-scheduled on the same physical or virtual machine in the cluster. The containers
can share resources and dependencies, communicate with one another, and coordinate
when and how they are terminated.

Pods in a Kubernetes cluster are used in two main ways:

- Pods that run a single container. The "one-container-per-Pod" model is the
most common Kubernetes use case; in this case, you can think of a Pod as a
wrapper around a single container; Kubernetes manages Pods rather than managing
the containers directly.
- Pods that run multiple containers that need to work together. A Pod can
encapsulate an application composed of
multiple co-located containers that are
tightly coupled and need to share resources. These co-located containers
form a single cohesive unit of service—for example, one container serving data
stored in a shared volume to the public, while a separatesidecar containerrefreshes or updates those files.The Pod wraps these containers, storage resources, and an ephemeral network
identity together as a single unit.

For example, you might have a container that
acts as a web server for files in a shared volume, and a separatesidecar containerthat updates those files from a remote source, as in the following diagram:

Some Pods haveinit containersas well asapp containers.By default, init containers run and complete before the app containers are started.

You can also havesidecar containersthat provide auxiliary services to the main application Pod (for example: a service mesh).

Enabled by default, theSidecarContainersfeature gateallows you to specifyrestartPolicy: Alwaysfor init containers.Setting theAlwaysrestart policy ensures that the containers where you set it are
treated assidecarsthat are kept running during the entire lifetime of the Pod.Containers that you explicitly define as sidecar containers
start up before the main application Pod and remain running until the Pod is
shut down.

## Container probes

Aprobeis a diagnostic performed periodically by the kubelet on a container.To perform a diagnostic, the kubelet can invoke different actions:

- ExecAction(performed with the help of the container runtime)
- TCPSocketAction(checked directly by the kubelet)
- HTTPGetAction(checked directly by the kubelet)

You can read more aboutprobesin the Pod Lifecycle documentation.

## What's next

- Learn about thelifecycle of a Pod.
- Read aboutPodDisruptionBudgetand how you can use it to manage application availability during disruptions.
- Pod is a top-level resource in the Kubernetes REST API.ThePodobject definition describes the object in detail.
- The Distributed System Toolkit: Patterns for Composite Containersexplains common layouts for Pods with more than one container.
- Read aboutPod topology spread constraints
- ReadAdvanced Pod Configurationto learn the topic in detail.That page covers aspects of Pod configuration beyond the essentials, including:PriorityClassesRuntimeClassesadvanced ways to configurescheduling: the way that Kubernetes decides which node a Pod should run on.
- PriorityClasses
- RuntimeClasses
- advanced ways to configurescheduling: the way that Kubernetes decides which node a Pod should run on.

To understand the context for why Kubernetes wraps a common Pod API in other resources(such asStatefulSetsorDeployments),you can read about the prior art, including:

- Aurora
- Borg
- Marathon
- Omega
- Tupperware.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
