<!-- source: k8s_task_debug_pods.md -->

# Tasks - Troubleshooting

---
Source: https://kubernetes.io/docs/tasks/debug/debug-application/debug-pods/
---

# Debug Pods

This guide is to help users debug applications that are deployed into Kubernetes
and not behaving correctly. This isnota guide for people who want to debug their cluster.
For that you should check outthis guide.

## Diagnosing the problem

The first step in troubleshooting is triage. What is the problem?
Is it your Pods, your Replication Controller or your Service?

- Debugging Pods
- Debugging Replication Controllers
- Debugging Services

### Debugging Pods

The first step in debugging a Pod is taking a look at it. Check the current
state of the Pod and recent events with the following command:

```
kubectl describe pods ${POD_NAME}
```

Look at the state of the containers in the pod. Are they allRunning?
Have there been recent restarts?

Continue debugging depending on the state of the pods.

#### My pod stays pending

If a Pod is stuck inPendingit means that it can not be scheduled onto a node.
Generally this is because there are insufficient resources of one type or another
that prevent scheduling. Look at the output of thekubectl describe ...command above.
There should be messages from the scheduler about why it can not schedule your pod.
Reasons include:

- You don't have enough resources: You may have exhausted the supply of CPU
or Memory in your cluster, in this case you need to delete Pods, adjust resource
requests, or add new nodes to your cluster. SeeCompute Resources documentfor more information.

You don't have enough resources: You may have exhausted the supply of CPU
or Memory in your cluster, in this case you need to delete Pods, adjust resource
requests, or add new nodes to your cluster. SeeCompute Resources documentfor more information.

- You are usinghostPort: When you bind a Pod to ahostPortthere are a
limited number of places that pod can be scheduled. In most cases,hostPortis unnecessary, try using a Service object to expose your Pod. If you do requirehostPortthen you can only schedule as many Pods as there are nodes in your Kubernetes cluster.

You are usinghostPort: When you bind a Pod to ahostPortthere are a
limited number of places that pod can be scheduled. In most cases,hostPortis unnecessary, try using a Service object to expose your Pod. If you do requirehostPortthen you can only schedule as many Pods as there are nodes in your Kubernetes cluster.

#### My pod stays waiting

If a Pod is stuck in theWaitingstate, then it has been scheduled to a worker node,
but it can't run on that machine. Again, the information fromkubectl describe ...should be informative. The most common cause ofWaitingpods is a failure to pull the image.
There are three things to check:

- Make sure that you have the name of the image correct.
- Have you pushed the image to the registry?
- Try to manually pull the image to see if the image can be pulled. For example,
if you use Docker on your PC, rundocker pull <image>.

#### My pod stays terminating

If a Pod is stuck in theTerminatingstate, it means that a deletion has been
issued for the Pod, but the control plane is unable to delete the Pod object.

This typically happens if the Pod has afinalizerand there is anadmission webhookinstalled in the cluster that prevents the control plane from removing the
finalizer.

To identify this scenario, check if your cluster has any
ValidatingWebhookConfiguration or MutatingWebhookConfiguration that targetUPDATEoperations forpodsresources.

If the webhook is provided by a third-party:

- Make sure you are using the latest version.
- Disable the webhook forUPDATEoperations.
- Report an issue with the corresponding provider.

If you are the author of the webhook:

- For a mutating webhook, make sure it never changes immutable fields onUPDATEoperations. For example, changes to containers are usually not allowed.
- For a validating webhook, make sure that your validation policies only apply
to new changes. In other words, you should allow Pods with existing violations
to pass validation. This allows Pods that were created before the validating
webhook was installed to continue running.

#### My pod is crashing or otherwise unhealthy

Once your pod has been scheduled, the methods described inDebug Running Podsare available for debugging.

#### My pod is running but not doing what I told it to do

If your pod is not behaving as you expected, it may be that there was an error in your
pod description (e.g.mypod.yamlfile on your local machine), and that the error
was silently ignored when you created the pod. Often a section of the pod description
is nested incorrectly, or a key name is typed incorrectly, and so the key is ignored.
For example, if you misspelledcommandascommndthen the pod will be created but
will not use the command line you intended it to use.

The first thing to do is to delete your pod and try creating it again with the--validateoption.
For example, runkubectl apply --validate -f mypod.yaml.
If you misspelledcommandascommndthen will give an error like this:

```
I0805 10:43:25.129850   46757 schema.go:126] unknown field: commnd
I0805 10:43:25.129973   46757 schema.go:129] this may be a false alarm, see https://github.com/kubernetes/kubernetes/issues/6842
pods/mypod
```

The next thing to check is whether the pod on the apiserver
matches the pod you meant to create (e.g. in a yaml file on your local machine).
For example, runkubectl get pods/mypod -o yaml > mypod-on-apiserver.yamland then
manually compare the original pod description,mypod.yamlwith the one you got
back from apiserver,mypod-on-apiserver.yaml. There will typically be some
lines on the "apiserver" version that are not on the original version. This is
expected. However, if there are lines on the original that are not on the apiserver
version, then this may indicate a problem with your pod spec.

### Debugging Replication Controllers

Replication controllers are fairly straightforward. They can either create Pods or they can't.
If they can't create pods, then please refer to theinstructions aboveto debug your pods.

You can also usekubectl describe rc ${CONTROLLER_NAME}to introspect events
related to the replication controller.

### Debugging Services

Services provide load balancing across a set of pods. There are several common problems that can make Services
not work properly. The following instructions should help debug Service problems.

First, verify that there are endpoints for the service. For every Service object,
the apiserver makes one or moreEndpointSliceresources available.

You can view these resources with:

```
kubectl get endpointslices -l kubernetes.io/service-name=${SERVICE_NAME}
```

Make sure that the endpoints in the EndpointSlices match up with the number of pods that you expect to be members of your service.
For example, if your Service is for an nginx container with 3 replicas, you would expect to see three different
IP addresses in the Service's endpoint slices.

#### My service is missing endpoints

If you are missing endpoints, try listing pods using the labels that Service uses.
Imagine that you have a Service where the labels are:

```
...
spec:
  - selector:
     name: nginx
     type: frontend
```

You can use:

```
kubectl get pods --selector=name=nginx,type=frontend
```

to list pods that match this selector. Verify that the list matches the Pods that you expect to provide your Service.
Verify that the pod'scontainerPortmatches up with the Service'stargetPort

#### Network traffic is not forwarded

Please seedebugging servicefor more information.

## What's next

If none of the above solves your problem, follow the instructions inDebugging Service documentto make sure that yourServiceis running, hasEndpoints, and yourPodsare
actually serving; you have DNS working, iptables rules installed, and kube-proxy
does not seem to be misbehaving.

You may also visittroubleshooting documentfor more information.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
