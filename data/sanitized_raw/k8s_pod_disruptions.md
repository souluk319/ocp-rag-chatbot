<!-- source: k8s_pod_disruptions.md -->

# Workloads - PDB

---
Source: https://kubernetes.io/docs/concepts/workloads/pods/disruptions/
---

# Disruptions

This guide is for application owners who want to build
highly available applications, and thus need to understand
what types of disruptions can happen to Pods.

It is also for cluster administrators who want to perform automated
cluster actions, like upgrading and autoscaling clusters.

## Voluntary and involuntary disruptions

Pods do not disappear until someone (a person or a controller) destroys them, or
there is an unavoidable hardware or system software error.

We call these unavoidable casesinvoluntary disruptionsto
an application. Examples are:

- a hardware failure of the physical machine backing the node
- cluster administrator deletes VM (instance) by mistake
- cloud provider or hypervisor failure makes VM disappear
- a kernel panic
- the node disappears from the cluster due to cluster network partition
- eviction of a pod due to the node beingout-of-resources.

Except for the out-of-resources condition, all these conditions
should be familiar to most users; they are not specific
to Kubernetes.

We call other casesvoluntary disruptions. These include both
actions initiated by the application owner and those initiated by a Cluster
Administrator. Typical application owner actions include:

- deleting the deployment or other controller that manages the pod
- updating a deployment's pod template causing a restart
- directly deleting a pod (e.g. by accident)

Cluster administrator actions include:

- Draining a nodefor repair or upgrade.
- Draining a node from a cluster to scale the cluster down (learn aboutNode Autoscaling).
- Removing a pod from a node to permit something else to fit on that node.

These actions might be taken directly by the cluster administrator, or by automation
run by the cluster administrator, or by your cluster hosting provider.

Ask your cluster administrator or consult your cloud provider or distribution documentation
to determine if any sources of voluntary disruptions are enabled for your cluster.
If none are enabled, you can skip creating Pod Disruption Budgets.

#### Caution:

## Dealing with disruptions

Here are some ways to mitigate involuntary disruptions:

- Ensure your podrequests the resourcesit needs.
- Replicate your application if you need higher availability. (Learn about running replicatedstatelessandstatefulapplications.)
- For even higher availability when running replicated applications,
spread applications across racks (usinganti-affinity)
or across zones (if using amulti-zone cluster.)

The frequency of voluntary disruptions varies. On a basic Kubernetes cluster, there are
no automated voluntary disruptions (only user-triggered ones). However, your cluster administrator or hosting provider
may run some additional services which cause voluntary disruptions. For example,
rolling out node software updates can cause voluntary disruptions. Also, some implementations
of cluster (node) autoscaling may cause voluntary disruptions to defragment and compact nodes.
Your cluster administrator or hosting provider should have documented what level of voluntary
disruptions, if any, to expect. Certain configuration options, such asusing PriorityClassesin your pod spec can also cause voluntary (and involuntary) disruptions.

## Pod disruption budgets

Kubernetes offers features to help you run highly available applications even when you
introduce frequent voluntary disruptions.

As an application owner, you can create a PodDisruptionBudget (PDB) for each application.
A PDB limits the number of Pods of a replicated application that are down simultaneously from
voluntary disruptions. For example, a quorum-based application would
like to ensure that the number of replicas running is never brought below the
number needed for a quorum. A web front end might want to
ensure that the number of replicas serving load never falls below a certain
percentage of the total.

Cluster managers and hosting providers should use tools which
respect PodDisruptionBudgets by calling theEviction APIinstead of directly deleting pods or deployments.

For example, thekubectl drainsubcommand lets you mark a node as going out of
service. When you runkubectl drain, the tool tries to evict all of the Pods on
the Node you're taking out of service. The eviction request thatkubectlsubmits on
your behalf may be temporarily rejected, so the tool periodically retries all failed
requests until all Pods on the target node are terminated, or until a configurable timeout
is reached.

A PDB specifies the number of replicas that an application can tolerate having, relative to how
many it is intended to have. For example, a Deployment which has a.spec.replicas: 5is
supposed to have 5 pods at any given time. If its PDB allows for there to be 4 at a time,
then the Eviction API will allow voluntary disruption of one (but not two) pods at a time.

The group of pods that comprise the application is specified using a label selector, the same
as the one used by the application's controller (deployment, stateful-set, etc).

The "intended" number of pods is computed from the.spec.replicasof the workload resource
that is managing those pods. The control plane discovers the owning workload resource by
examining the.metadata.ownerReferencesof the Pod.

Involuntary disruptionscannot be prevented by PDBs; however they
do count against the budget.

Pods which are deleted or unavailable due to a rolling upgrade to an application do count
against the disruption budget, but workload resources (such as Deployment and StatefulSet)
are not limited by PDBs when doing rolling upgrades. Instead, the handling of failures
during application updates is configured in the spec for the specific workload resource.

It is recommended to setAlwaysAllowUnhealthy Pod Eviction Policyto your PodDisruptionBudgets to support eviction of misbehaving applications during a node drain.
The default behavior is to wait for the application pods to becomehealthybefore the drain can proceed.

When a pod is evicted using the eviction API, it is gracefullyterminated, honoring theterminationGracePeriodSecondssetting in itsPodSpec.

## PodDisruptionBudget example

Consider a cluster with 3 nodes,node-1throughnode-3.
The cluster is running several applications. One of them has 3 replicas initially calledpod-a,pod-b, andpod-c. Another, unrelated pod without a PDB, calledpod-x, is also shown.
Initially, the pods are laid out as follows:

| node-1 | node-2 | node-3 |
| --- | --- | --- |
| pod-aavailable | pod-bavailable | pod-cavailable |
| pod-xavailable |  |  |

All 3 pods are part of a deployment, and they collectively have a PDB which requires
there be at least 2 of the 3 pods to be available at all times.

For example, assume the cluster administrator wants to reboot into a new kernel version to fix a bug in the kernel.
The cluster administrator first tries to drainnode-1using thekubectl draincommand.
That tool tries to evictpod-aandpod-x. This succeeds immediately.
Both pods go into theterminatingstate at the same time.
This puts the cluster in this state:

| node-1draining | node-2 | node-3 |
| --- | --- | --- |
| pod-aterminating | pod-bavailable | pod-cavailable |
| pod-xterminating |  |  |

The deployment notices that one of the pods is terminating, so it creates a replacement
calledpod-d. Sincenode-1is cordoned, it lands on another node. Something has
also createdpod-yas a replacement forpod-x.

(Note: for a StatefulSet,pod-a, which would be called something likepod-0, would need
to terminate completely before its replacement, which is also calledpod-0but has a
different UID, could be created. Otherwise, the example applies to a StatefulSet as well.)

Now the cluster is in this state:

| node-1draining | node-2 | node-3 |
| --- | --- | --- |
| pod-aterminating | pod-bavailable | pod-cavailable |
| pod-xterminating | pod-dstarting | pod-y |

At some point, the pods terminate, and the cluster looks like this:

| node-1drained | node-2 | node-3 |
| --- | --- | --- |
|  | pod-bavailable | pod-cavailable |
|  | pod-dstarting | pod-y |

At this point, if an impatient cluster administrator tries to drainnode-2ornode-3, the drain command will block, because there are only 2 available
pods for the deployment, and its PDB requires at least 2. After some time passes,pod-dbecomes available.

The cluster state now looks like this:

| node-1drained | node-2 | node-3 |
| --- | --- | --- |
|  | pod-bavailable | pod-cavailable |
|  | pod-davailable | pod-y |

Now, the cluster administrator tries to drainnode-2.
The drain command will try to evict the two pods in some order, saypod-bfirst and thenpod-d. It will succeed at evictingpod-b.
But, when it tries to evictpod-d, it will be refused because that would leave only
one pod available for the deployment.

The deployment creates a replacement forpod-bcalledpod-e.
Because there are not enough resources in the cluster to schedulepod-ethe drain will again block. The cluster may end up in this
state:

| node-1drained | node-2 | node-3 | no node |
| --- | --- | --- | --- |
|  | pod-bterminating | pod-cavailable | pod-epending |
|  | pod-davailable | pod-y |  |

At this point, the cluster administrator needs to
add a node back to the cluster to proceed with the upgrade.

You can see how Kubernetes varies the rate at which disruptions
can happen, according to:

- how many replicas an application needs
- how long it takes to gracefully shutdown an instance
- how long it takes a new instance to start up
- the type of controller
- the cluster's resource capacity

## Pod disruption conditions

A dedicated PodDisruptionTargetconditionis added to indicate
that the Pod is about to be deleted due to adisruption.
Thereasonfield of the condition additionally
indicates one of the following reasons for the Pod termination:

**PreemptionByScheduler**
  Pod is due to bepreemptedby a scheduler in order to accommodate a new Pod with a higher priority. For more information, seePod priority preemption.

**DeletionByTaintManager**
  Pod is due to be deleted by Taint Manager (which is part of the node lifecycle controller withinkube-controller-manager) due to aNoExecutetaint that the Pod does not tolerate; seetaint-based evictions.

**EvictionByEvictionAPI**
  Pod has been marked foreviction using the Kubernetes API.

**DeletionByPodGC**
  Pod, that is bound to a no longer existing Node, is due to be deleted byPod garbage collection.

**TerminationByKubelet**
  Pod has been terminated by the kubelet, because of eithernode pressure eviction,
thegraceful node shutdown,
or preemption forsystem critical pods.

In all other disruption scenarios, like eviction due to exceedingPod container limits,
Pods don't receive theDisruptionTargetcondition because the disruptions were
probably caused by the Pod and would reoccur on retry.

#### Note:

Along with cleaning up the pods, the Pod garbage collector (PodGC) will also mark them as failed if they are in a non-terminal
phase (see alsoPod garbage collection).

When using a Job (or CronJob), you may want to use these Pod disruption conditions as part of your Job'sPod failure policy.

## Separating Cluster Owner and Application Owner Roles

Often, it is useful to think of the Cluster Manager
and Application Owner as separate roles with limited knowledge
of each other. This separation of responsibilities
may make sense in these scenarios:

- when there are many application teams sharing a Kubernetes cluster, and
there is natural specialization of roles
- when third-party tools or services are used to automate cluster management

Pod Disruption Budgets support this separation of roles by providing an
interface between the roles.

If you do not have such a separation of responsibilities in your organization,
you may not need to use Pod Disruption Budgets.

## How to perform Disruptive Actions on your Cluster

If you are a Cluster Administrator, and you need to perform a disruptive action on all
the nodes in your cluster, such as a node or system software upgrade, here are some options:

- Accept downtime during the upgrade.
- Failover to another complete replica cluster.No downtime, but may be costly both for the duplicated nodes
and for human effort to orchestrate the switchover.
- No downtime, but may be costly both for the duplicated nodes
and for human effort to orchestrate the switchover.
- Write disruption tolerant applications and use PDBs.No downtime.Minimal resource duplication.Allows more automation of cluster administration.Writing disruption-tolerant applications is tricky, but the work to tolerate voluntary
disruptions largely overlaps with work to support autoscaling and tolerating
involuntary disruptions.
- No downtime.
- Minimal resource duplication.
- Allows more automation of cluster administration.
- Writing disruption-tolerant applications is tricky, but the work to tolerate voluntary
disruptions largely overlaps with work to support autoscaling and tolerating
involuntary disruptions.

## What's next

- Follow steps to protect your application byconfiguring a Pod Disruption Budget.

Follow steps to protect your application byconfiguring a Pod Disruption Budget.

- Learn more aboutdraining nodes

Learn more aboutdraining nodes

- Learn aboutupdating a deploymentincluding steps to maintain its availability during the rollout.

Learn aboutupdating a deploymentincluding steps to maintain its availability during the rollout.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
