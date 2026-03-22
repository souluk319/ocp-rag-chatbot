<!-- source: k8s_task_hpa.md -->

# Tasks - Autoscaling

---
Source: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale-walkthrough/
---

# HorizontalPodAutoscaler Walkthrough

AHorizontalPodAutoscaler(HPA for short)
automatically updates a workload resource (such as
aDeploymentorStatefulSet), with the
aim of automatically scaling the workload to match demand.

Horizontal scaling means that the response to increased load is to deploy morePods.
This is different fromverticalscaling, which for Kubernetes would mean
assigning more resources (for example: memory or CPU) to the Pods that are already
running for the workload.

If the load decreases, and the number of Pods is above the configured minimum,
the HorizontalPodAutoscaler instructs the workload resource (the Deployment, StatefulSet,
or other similar resource) to scale back down.

This document walks you through an example of enabling HorizontalPodAutoscaler to
automatically manage scale for an example web app. This example workload is Apache
httpd running some PHP code.

## Before you begin

You need to have a Kubernetes cluster, and the kubectl command-line tool must
be configured to communicate with your cluster. It is recommended to run this tutorial on a cluster with at least two nodes that are not acting as control plane hosts. If you do not already have a
cluster, you can create one by usingminikubeor you can use one of these Kubernetes playgrounds:

- iximiuz Labs
- Killercoda
- KodeKloud

To check the version, enterkubectl version.

To follow this walkthrough, you also need to use a cluster that has aMetrics Serverdeployed and configured.
The Kubernetes Metrics Server collects resource metrics from
thekubeletsin your cluster, and exposes those metrics
through theKubernetes API,
using anAPIServiceto add
new kinds of resource that represent metric readings.

To learn how to deploy the Metrics Server, see themetrics-server documentation.

If you are runningMinikube, run the following command to enable metrics-server:

```
minikube addons enable metrics-server
```

## Run and expose php-apache server

To demonstrate a HorizontalPodAutoscaler, you will first start a Deployment that runs a container using thehpa-exampleimage, and expose it as aServiceusing the following manifest:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: php-apache
spec:
  selector:
    matchLabels:
      run: php-apache
  template:
    metadata:
      labels:
        run: php-apache
    spec:
      containers:
      - name: php-apache
        image: registry.k8s.io/hpa-example
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: 500m
          requests:
            cpu: 200m
---
apiVersion: v1
kind: Service
metadata:
  name: php-apache
  labels:
    run: php-apache
spec:
  ports:
  - port: 80
  selector:
    run: php-apache
```

To do so, run the following command:

```
kubectl apply -f https://k8s.io/examples/application/php-apache.yaml
```

```
deployment.apps/php-apache created
service/php-apache created
```

## Create the HorizontalPodAutoscaler

Now that the server is running, create the autoscaler usingkubectl. Thekubectl autoscalesubcommand,
part ofkubectl, helps you do this.

You will shortly run a command that creates a HorizontalPodAutoscaler that maintains
between 1 and 10 replicas of the Pods controlled by the php-apache Deployment that
you created in the first step of these instructions.

Roughly speaking, the HPAcontrollerwill increase and decrease
the number of replicas (by updating the Deployment) to maintain an average CPU utilization across all Pods of 50%.
The Deployment then updates the ReplicaSet - this is part of how all Deployments work in Kubernetes -
and then the ReplicaSet either adds or removes Pods based on the change to its.spec.

Since each pod requests 200 milli-cores bykubectl run, this means an average CPU usage of 100 milli-cores.
SeeAlgorithm detailsfor more details
on the algorithm.

Create the HorizontalPodAutoscaler:

```
kubectl autoscale deployment php-apache --cpu-percent=50 --min=1 --max=10
```

```
horizontalpodautoscaler.autoscaling/php-apache autoscaled
```

You can check the current status of the newly-made HorizontalPodAutoscaler, by running:

```
# You can use "hpa" or "horizontalpodautoscaler"; either name works OK.
kubectl get hpa
```

The output is similar to:

```
NAME         REFERENCE                     TARGET    MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache/scale   0% / 50%  1         10        1          18s
```

(if you see other HorizontalPodAutoscalers with different names, that means they already existed,
and isn't usually a problem).

Please note that the current CPU consumption is 0% as there are no clients sending requests to the server
(theTARGETcolumn shows the average across all the Pods controlled by the corresponding deployment).

## Increase the load

Next, see how the autoscaler reacts to increased load.
To do this, you'll start a different Pod to act as a client. The container within the client Pod
runs in an infinite loop, sending queries to the php-apache service.

```
# Run this in a separate terminal
# so that the load generation continues and you can carry on with the rest of the steps
kubectl run -i --tty load-generator --rm --image=busybox:1.28 --restart=Never -- /bin/sh -c "while sleep 0.01; do wget -q -O- http://php-apache; done"
```

Now run:

```
# type Ctrl+C to end the watch when you're ready
kubectl get hpa php-apache --watch
```

Within a minute or so, you should see the higher CPU load; for example:

```
NAME         REFERENCE                     TARGET      MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache/scale   305% / 50%  1         10        1          3m
```

and then, more replicas. For example:

```
NAME         REFERENCE                     TARGET      MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache/scale   305% / 50%  1         10        7          3m
```

Here, CPU consumption has increased to 305% of the request.
As a result, the Deployment was resized to 7 replicas:

```
kubectl get deployment php-apache
```

You should see the replica count matching the figure from the HorizontalPodAutoscaler

```
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   7/7      7           7           19m
```

#### Note:

## Stop generating load

To finish the example, stop sending the load.

In the terminal where you created the Pod that runs abusyboximage, terminate
the load generation by typing<Ctrl> + C.

Then verify the result state (after a minute or so):

```
# type Ctrl+C to end the watch when you're ready
kubectl get hpa php-apache --watch
```

The output is similar to:

```
NAME         REFERENCE                     TARGET       MINPODS   MAXPODS   REPLICAS   AGE
php-apache   Deployment/php-apache/scale   0% / 50%     1         10        1          11m
```

and the Deployment also shows that it has scaled down:

```
kubectl get deployment php-apache
```

```
NAME         READY   UP-TO-DATE   AVAILABLE   AGE
php-apache   1/1     1            1           27m
```

Once CPU utilization dropped to 0, the HPA automatically scaled the number of replicas back down to 1.

Autoscaling the replicas may take a few minutes.

## Autoscaling on multiple metrics and custom metrics

You can introduce additional metrics to use when autoscaling thephp-apacheDeployment
by making use of theautoscaling/v2API version.

First, get the YAML of your HorizontalPodAutoscaler in theautoscaling/v2form:

```
kubectl get hpa php-apache -o yaml > /tmp/hpa-v2.yaml
```

Open the/tmp/hpa-v2.yamlfile in an editor, and you should see YAML which looks like this:

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
status:
  observedGeneration: 1
  lastScaleTime: <some-time>
  currentReplicas: 1
  desiredReplicas: 1
  currentMetrics:
  - type: Resource
    resource:
      name: cpu
      current:
        averageUtilization: 0
        averageValue: 0
```

Notice that thetargetCPUUtilizationPercentagefield has been replaced with an array calledmetrics.
The CPU utilization metric is aresource metric, since it is represented as a percentage of a resource
specified on pod containers. Notice that you can specify other resource metrics besides CPU. By default,
the only other supported resource metric ismemory. These resources do not change names from cluster
to cluster, and should always be available, as long as themetrics.k8s.ioAPI is available.

You can also specify resource metrics in terms of direct values, instead of as percentages of the
requested value, by using atarget.typeofAverageValueinstead ofUtilization, and
setting the correspondingtarget.averageValuefield instead of thetarget.averageUtilization.

```
metrics:
  - type: Resource
    resource:
      name: memory
      target:
        type: AverageValue
        averageValue: 500Mi
```

There are two other types of metrics, both of which are consideredcustom metrics: pod metrics and
object metrics. These metrics may have names which are cluster specific, and require a more
advanced cluster monitoring setup.

The first of these alternative metric types ispod metrics. These metrics describe Pods, and
are averaged together across Pods and compared with a target value to determine the replica count.
They work much like resource metrics, except that theyonlysupport atargettype ofAverageValue.

Pod metrics are specified using a metric block like this:

```
type: Pods
pods:
  metric:
    name: packets-per-second
  target:
    type: AverageValue
    averageValue: 1k
```

The second alternative metric type isobject metrics. These metrics describe a different
object in the same namespace, instead of describing Pods. The metrics are not necessarily
fetched from the object; they only describe it. Object metrics supporttargettypes of
bothValueandAverageValue. WithValue, the target is compared directly to the returned
metric from the API. WithAverageValue, the value returned from the custom metrics API is divided
by the number of Pods before being compared to the target. The following example is the YAML
representation of therequests-per-secondmetric.

```
type: Object
object:
  metric:
    name: requests-per-second
  describedObject:
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    name: main-route
  target:
    type: Value
    value: 2k
```

If you provide multiple such metric blocks, the HorizontalPodAutoscaler will consider each metric in turn.
The HorizontalPodAutoscaler will calculate proposed replica counts for each metric, and then choose the
one with the highest replica count.

For example, if you had your monitoring system collecting metrics about network traffic,
you could update the definition above usingkubectl editto look like this:

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
  - type: Pods
    pods:
      metric:
        name: packets-per-second
      target:
        type: AverageValue
        averageValue: 1k
  - type: Object
    object:
      metric:
        name: requests-per-second
      describedObject:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: main-route
      target:
        type: Value
        value: 10k
status:
  observedGeneration: 1
  lastScaleTime: <some-time>
  currentReplicas: 1
  desiredReplicas: 1
  currentMetrics:
  - type: Resource
    resource:
      name: cpu
    current:
      averageUtilization: 0
      averageValue: 0
  - type: Object
    object:
      metric:
        name: requests-per-second
      describedObject:
        apiVersion: networking.k8s.io/v1
        kind: Ingress
        name: main-route
      current:
        value: 10k
```

Then, your HorizontalPodAutoscaler would attempt to ensure that each pod was consuming roughly
50% of its requested CPU, serving 1000 packets per second, and that all pods behind the main-route
Ingress were serving a total of 10000 requests per second.

### Autoscaling on more specific metrics

Many metrics pipelines allow you to describe metrics either by name or by a set of additional
descriptors calledlabels. For all non-resource metric types (pod, object, and external,
described below), you can specify an additional label selector which is passed to your metric
pipeline. For instance, if you collect a metrichttp_requestswith theverblabel, you can specify the following metric block to scale only on GET requests:

```
type: Object
object:
  metric:
    name: http_requests
    selector: {matchLabels: {verb: GET}}
```

This selector uses the same syntax as the full Kubernetes label selectors. The monitoring pipeline
determines how to collapse multiple series into a single value, if the name and selector
match multiple series. The selector is additive, and cannot select metrics
that describe objects that arenotthe target object (the target pods in the case of thePodstype, and the described object in the case of theObjecttype).

### Autoscaling on metrics not related to Kubernetes objects

Applications running on Kubernetes may need to autoscale based on metrics that don't have an obvious
relationship to any object in the Kubernetes cluster, such as metrics describing a hosted service with
no direct correlation to Kubernetes namespaces. In Kubernetes 1.10 and later, you can address this use case
withexternal metrics.

Using external metrics requires knowledge of your monitoring system; the setup is
similar to that required when using custom metrics. External metrics allow you to autoscale your cluster
based on any metric available in your monitoring system. Provide ametricblock with anameandselector, as above, and use theExternalmetric type instead ofObject.
If multiple time series are matched by themetricSelector,
the sum of their values is used by the HorizontalPodAutoscaler.
External metrics support both theValueandAverageValuetarget types, which function exactly the same
as when you use theObjecttype.

For example if your application processes tasks from a hosted queue service, you could add the following
section to your HorizontalPodAutoscaler manifest to specify that you need one worker per 30 outstanding tasks.

```
- type: External
  external:
    metric:
      name: queue_messages_ready
      selector:
        matchLabels:
          queue: "worker_tasks"
    target:
      type: AverageValue
      averageValue: 30
```

When possible, it's preferable to use the custom metric target types instead of external metrics, since it's
easier for cluster administrators to secure the custom metrics API. The external metrics API potentially allows
access to any metric, so cluster administrators should take care when exposing it.

## Appendix: Horizontal Pod Autoscaler Status Conditions

When using theautoscaling/v2form of the HorizontalPodAutoscaler, you will be able to seestatus conditionsset by Kubernetes on the HorizontalPodAutoscaler. These status conditions indicate
whether or not the HorizontalPodAutoscaler is able to scale, and whether or not it is currently restricted
in any way.

The conditions appear in thestatus.conditionsfield. To see the conditions affecting a HorizontalPodAutoscaler,
we can usekubectl describe hpa:

```
kubectl describe hpa cm-test
```

```
Name:                           cm-test
Namespace:                      prom
Labels:                         <none>
Annotations:                    <none>
CreationTimestamp:              Fri, 16 Jun 2017 18:09:22 +0000
Reference:                      ReplicationController/cm-test
Metrics:                        ( current / target )
  "http_requests" on pods:      66m / 500m
Min replicas:                   1
Max replicas:                   4
ReplicationController pods:     1 current / 1 desired
Conditions:
  Type                  Status  Reason                  Message
  ----                  ------  ------                  -------
  AbleToScale           True    ReadyForNewScale        the last scale time was sufficiently old as to warrant a new scale
  ScalingActive         True    ValidMetricFound        the HPA was able to successfully calculate a replica count from pods metric http_requests
  ScalingLimited        False   DesiredWithinRange      the desired replica count is within the acceptable range
Events:
```

For this HorizontalPodAutoscaler, you can see several conditions in a healthy state. The first,AbleToScale, indicates whether or not the HPA is able to fetch and update scales, as well as
whether or not any backoff-related conditions would prevent scaling. The second,ScalingActive,
indicates whether or not the HPA is enabled (i.e. the replica count of the target is not zero) and
is able to calculate desired scales. When it isFalse, it generally indicates problems with
fetching metrics. Finally, the last condition,ScalingLimited, indicates that the desired scale
was capped by the maximum or minimum of the HorizontalPodAutoscaler. This is an indication that
you may wish to raise or lower the minimum or maximum replica count constraints on your
HorizontalPodAutoscaler.

## Quantities

All metrics in the HorizontalPodAutoscaler and metrics APIs are specified using
a special whole-number notation known in Kubernetes as aquantity. For example,
the quantity10500mwould be written as10.5in decimal notation. The metrics APIs
will return whole numbers without a suffix when possible, and will generally return
quantities in milli-units otherwise. This means you might see your metric value fluctuate
between1and1500m, or1and1.5when written in decimal notation.

## Other possible scenarios

### Creating the autoscaler declaratively

Instead of usingkubectl autoscalecommand to create a HorizontalPodAutoscaler imperatively we
can use the following manifest to create it declaratively:

```
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: php-apache
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: php-apache
  minReplicas: 1
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 50
```

Then, create the autoscaler by executing the following command:

```
kubectl create -f https://k8s.io/examples/application/hpa/php-apache.yaml
```

```
horizontalpodautoscaler.autoscaling/php-apache created
```

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
