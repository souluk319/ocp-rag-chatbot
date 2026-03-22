<!-- source: k8s_workloads.md -->

# Workloads

---
Source: https://kubernetes.io/docs/concepts/workloads/
---

# Workloads

A workload is an application running on Kubernetes.
Whether your workload is a single component or several that work together, on Kubernetes you run
it inside a set ofpods.In Kubernetes, a Pod represents a set of runningcontainerson your cluster.

Kubernetes pods have adefined lifecycle.For example, once a pod is running in your cluster then a critical fault on thenodewhere that pod is running means that
all the pods on that node fail. Kubernetes treats that level of failure as final: you
would need to create a new Pod to recover, even if the node later becomes healthy.

However, to make life considerably easier, you don't need to manage each Pod directly.Instead, you can useworkload resourcesthat manage a set of pods on your behalf.These resources configurecontrollersthat make sure the right number of the right kind of pod are running, to match the state
you specified.

Kubernetes provides several built-in workload resources:

- DeploymentandReplicaSet(replacing the legacy resourceReplicationController).Deployment is a good fit for managing a stateless application workload on your cluster,where any Pod in the Deployment is interchangeable and can be replaced if needed.
- StatefulSetlets you
run one or more related Pods that do track state somehow. For example, if your workload
records data persistently, you can run a StatefulSet that matches each Pod with aPersistentVolume. Your code, running in the
Pods for that StatefulSet, can replicate data to other Pods in the same StatefulSet
to improve overall resilience.
- DaemonSetdefines Pods that provide
facilities that are local to nodes.Every time you add a node to your cluster that matches the specification in a DaemonSet,the control plane schedules a Pod for that DaemonSet onto the new node.Each pod in a DaemonSet performs a job similar to a system daemon on a classic Unix / POSIX
server. A DaemonSet might be fundamental to the operation of your cluster, such as
a plugin to runcluster networking,it might help you to manage the node,or it could provide optional behavior that enhances the container platform you are running.
- JobandCronJobprovide different ways to
define tasks that run to completion and then stop.You can use aJobto
define a task that runs to completion, just once. You can use aCronJobto run
the same Job multiple times according a schedule.

In the wider Kubernetes ecosystem, you can find third-party workload resources that provide
additional behaviors. Using acustom resource definition,you can add in a third-party workload resource if you want a specific behavior that's not part
of Kubernetes' core. For example, if you wanted to run a group of Pods for your application but
stop work unlessallthe Pods are available (perhaps for some high-throughput distributed task),then you can implement or install an extension that does provide that feature.

## Workload placement

While standard workload resources (like Deployments and Jobs) manage the lifecycle of Pods,you may have complex scheduling requirements where groups of Pods must be treated as a single unit.

TheWorkload APIallows you to define a group of Pods
and apply advanced scheduling policies to them, such asgang scheduling.This is particularly useful for batch processing and machine learning workloads
where "all-or-nothing" placement is required.

## What's next

As well as reading about each API kind for workload management, you can read how to
do specific tasks:

- Run a stateless application using a Deployment
- Run a stateful application either as asingle instanceor as areplicated set
- Run automated tasks with a CronJob

To learn about Kubernetes' mechanisms for separating code from configuration,visitConfiguration.

There are two supporting concepts that provide backgrounds about how Kubernetes manages pods
for applications:

- Garbage collectiontidies up objects
from your cluster after theirowning resourcehas been removed.
- Thetime-to-live after finishedcontrollerremoves Jobs once a defined time has passed since they completed.

Once your application is running, you might want to make it available on the internet as
aServiceor, for web application only,using anIngress.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
