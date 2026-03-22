<!-- source: ocp_deployments.md -->

# Workloads

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/building_applications/deployments
---

# Chapter 7. Deployments

## 7.1. Understanding deploymentsCopy linkLink copied to clipboard!

TheDeploymentandDeploymentConfigAPI objects in OpenShift Container Platform provide two similar but different methods for fine-grained management over common user applications. They are composed of the following separate API objects:

- ADeploymentorDeploymentConfigobject, either of which describes the desired state of a particular component of the application as a pod template.
- Deploymentobjects involve one or morereplica sets, which contain a point-in-time record of the state of a deployment as a pod template. Similarly,DeploymentConfigobjects involve one or morereplication controllers, which preceded replica sets.
- One or more pods, which represent an instance of a particular version of an application.

UseDeploymentobjects unless you need a specific feature or behavior provided byDeploymentConfigobjects.

As of OpenShift Container Platform 4.14,DeploymentConfigobjects are deprecated.DeploymentConfigobjects are still supported, but are not recommended for new installations. Only security-related and critical issues will be fixed.

Instead, useDeploymentobjects or another alternative to provide declarative updates for pods.

### 7.1.1. Building blocks of a deploymentCopy linkLink copied to clipboard!

Deployments and deployment configs are enabled by the use of native Kubernetes API objectsReplicaSetandReplicationController, respectively, as their building blocks.

Users do not have to manipulate replica sets, replication controllers, or pods owned byDeploymentorDeploymentConfigobjects. The deployment systems ensure changes are propagated appropriately.

If the existing deployment strategies are not suited for your use case and you must run manual steps during the lifecycle of your deployment, then you should consider creating a custom deployment strategy.

The following sections provide further details on these objects.

#### 7.1.1.1. Replica setsCopy linkLink copied to clipboard!

AReplicaSetis a native Kubernetes API object that ensures a specified number of pod replicas are running at any given time.

Only use replica sets if you require custom update orchestration or do not require updates at all. Otherwise, use deployments. Replica sets can be used independently, but are used by deployments to orchestrate pod creation, deletion, and updates. Deployments manage their replica sets automatically, provide declarative updates to pods, and do not have to manually manage the replica sets that they create.

The following is an exampleReplicaSetdefinition:

```
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend-1
  labels:
    tier: frontend
spec:
  replicas: 3
  selector: 
    matchLabels: 
      tier: frontend
    matchExpressions: 
      - {key: tier, operator: In, values: [frontend]}
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
```

```
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: frontend-1
  labels:
    tier: frontend
spec:
  replicas: 3
  selector:
```

```
matchLabels:
```

```
tier: frontend
    matchExpressions:
```

```
- {key: tier, operator: In, values: [frontend]}
  template:
    metadata:
      labels:
        tier: frontend
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
```

**1**
  A label query over a set of resources. The result ofmatchLabelsandmatchExpressionsare logically conjoined.

**2**
  Equality-based selector to specify resources with labels that match the selector.

**3**
  Set-based selector to filter keys. This selects all resources with key equal totierand value equal tofrontend.

#### 7.1.1.2. Replication controllersCopy linkLink copied to clipboard!

Similar to a replica set, a replication controller ensures that a specified number of replicas of a pod are running at all times. If pods exit or are deleted, the replication controller instantiates more up to the defined number. Likewise, if there are more running than desired, it deletes as many as necessary to match the defined amount. The difference between a replica set and a replication controller is that a replica set supports set-based selector requirements whereas a replication controller only supports equality-based selector requirements.

A replication controller configuration consists of:

- The number of replicas desired, which can be adjusted at run time.
- APoddefinition to use when creating a replicated pod.
- A selector for identifying managed pods.

A selector is a set of labels assigned to the pods that are managed by the replication controller. These labels are included in thePoddefinition that the replication controller instantiates. The replication controller uses the selector to determine how many instances of the pod are already running in order to adjust as needed.

The replication controller does not perform auto-scaling based on load or traffic, as it does not track either. Rather, this requires its replica count to be adjusted by an external auto-scaler.

Use aDeploymentConfigto create a replication controller instead of creating replication controllers directly.

If you require custom orchestration or do not require updates, use replica sets instead of replication controllers.

The following is an example definition of a replication controller:

```
apiVersion: v1
kind: ReplicationController
metadata:
  name: frontend-1
spec:
  replicas: 1  
  selector:    
    name: frontend
  template:    
    metadata:
      labels:  
        name: frontend 
    spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
```

```
apiVersion: v1
kind: ReplicationController
metadata:
  name: frontend-1
spec:
  replicas: 1
```

```
selector:
```

```
name: frontend
  template:
```

```
metadata:
      labels:
```

```
name: frontend
```

```
spec:
      containers:
      - image: openshift/hello-openshift
        name: helloworld
        ports:
        - containerPort: 8080
          protocol: TCP
      restartPolicy: Always
```

**1**
  The number of copies of the pod to run.

**2**
  The label selector of the pod to run.

**3**
  A template for the pod the controller creates.

**4**
  Labels on the pod should include those from the label selector.

**5**
  The maximum name length after expanding any parameters is 63 characters.

### 7.1.2. DeploymentsCopy linkLink copied to clipboard!

Kubernetes provides a first-class, native API object type in OpenShift Container Platform calledDeployment.Deploymentobjects describe the desired state of a particular component of an application as a pod template. Deployments create replica sets, which orchestrate pod lifecycles.

For example, the following deployment definition creates a replica set to bring up onehello-openshiftpod:

Deployment definition

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-openshift
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-openshift
  template:
    metadata:
      labels:
        app: hello-openshift
    spec:
      containers:
      - name: hello-openshift
        image: openshift/hello-openshift:latest
        ports:
        - containerPort: 80
```

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: hello-openshift
spec:
  replicas: 1
  selector:
    matchLabels:
      app: hello-openshift
  template:
    metadata:
      labels:
        app: hello-openshift
    spec:
      containers:
      - name: hello-openshift
        image: openshift/hello-openshift:latest
        ports:
        - containerPort: 80
```

### 7.1.3. DeploymentConfig objectsCopy linkLink copied to clipboard!

As of OpenShift Container Platform 4.14,DeploymentConfigobjects are deprecated.DeploymentConfigobjects are still supported, but are not recommended for new installations. Only security-related and critical issues will be fixed.

Instead, useDeploymentobjects or another alternative to provide declarative updates for pods.

Building on replication controllers, OpenShift Container Platform adds expanded support for the software development and deployment lifecycle with the concept ofDeploymentConfigobjects. In the simplest case, aDeploymentConfigobject creates a new replication controller and lets it start up pods.

However, OpenShift Container Platform deployments fromDeploymentConfigobjects also provide the ability to transition from an existing deployment of an image to a new one and also define hooks to be run before or after creating the replication controller.

TheDeploymentConfigdeployment system provides the following capabilities:

- ADeploymentConfigobject, which is a template for running applications.
- Triggers that drive automated deployments in response to events.
- User-customizable deployment strategies to transition from the previous version to the new version. A strategy runs inside a pod commonly referred as the deployment process.
- A set of hooks (lifecycle hooks) for executing custom behavior in different points during the lifecycle of a deployment.
- Versioning of your application to support rollbacks either manually or automatically in case of deployment failure.
- Manual replication scaling and autoscaling.

When you create aDeploymentConfigobject, a replication controller is created representing theDeploymentConfigobject’s pod template. If the deployment changes, a new replication controller is created with the latest pod template, and a deployment process runs to scale down the old replication controller and scale up the new one.

Instances of your application are automatically added and removed from both service load balancers and routers as they are created. As long as your application supports graceful shutdown when it receives theTERMsignal, you can ensure that running user connections are given a chance to complete normally.

The OpenShift Container PlatformDeploymentConfigobject defines the following details:

- The elements of aReplicationControllerdefinition.
- Triggers for creating a new deployment automatically.
- The strategy for transitioning between deployments.
- Lifecycle hooks.

Each time a deployment is triggered, whether manually or automatically, a deployer pod manages the deployment (including scaling down the old replication controller, scaling up the new one, and running hooks). The deployment pod remains for an indefinite amount of time after it completes the deployment to retain its logs of the deployment. When a deployment is superseded by another, the previous replication controller is retained to enable easy rollback if needed.

ExampleDeploymentConfigdefinition

```
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: frontend
spec:
  replicas: 5
  selector:
    name: frontend
  template: { ... }
  triggers:
  - type: ConfigChange 
  - imageChangeParams:
      automatic: true
      containerNames:
      - helloworld
      from:
        kind: ImageStreamTag
        name: hello-openshift:latest
    type: ImageChange  
  strategy:
    type: Rolling
```

```
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: frontend
spec:
  replicas: 5
  selector:
    name: frontend
  template: { ... }
  triggers:
  - type: ConfigChange
```

```
- imageChangeParams:
      automatic: true
      containerNames:
      - helloworld
      from:
        kind: ImageStreamTag
        name: hello-openshift:latest
    type: ImageChange
```

```
strategy:
    type: Rolling
```

**1**
  A configuration change trigger results in a new replication controller whenever changes are detected in the pod template of the deployment configuration.

**2**
  An image change trigger causes a new deployment to be created each time a new version of the backing image is available in the named image stream.

**3**
  The defaultRollingstrategy makes a downtime-free transition between deployments.

### 7.1.4. Comparing Deployment and DeploymentConfig objectsCopy linkLink copied to clipboard!

Both KubernetesDeploymentobjects and OpenShift Container Platform-providedDeploymentConfigobjects are supported in OpenShift Container Platform; however, it is recommended to useDeploymentobjects unless you need a specific feature or behavior provided byDeploymentConfigobjects.

The following sections go into more detail on the differences between the two object types to further help you decide which type to use.

As of OpenShift Container Platform 4.14,DeploymentConfigobjects are deprecated.DeploymentConfigobjects are still supported, but are not recommended for new installations. Only security-related and critical issues will be fixed.

Instead, useDeploymentobjects or another alternative to provide declarative updates for pods.

#### 7.1.4.1. DesignCopy linkLink copied to clipboard!

One important difference betweenDeploymentandDeploymentConfigobjects is the properties of theCAP theoremthat each design has chosen for the rollout process.DeploymentConfigobjects prefer consistency, whereasDeploymentsobjects take availability over consistency.

ForDeploymentConfigobjects, if a node running a deployer pod goes down, it will not get replaced. The process waits until the node comes back online or is manually deleted. Manually deleting the node also deletes the corresponding pod. This means that you can not delete the pod to unstick the rollout, as the kubelet is responsible for deleting the associated pod.

However, deployment rollouts are driven from a controller manager. The controller manager runs in high availability mode on masters and uses leader election algorithms to value availability over consistency. During a failure it is possible for other masters to act on the same deployment at the same time, but this issue will be reconciled shortly after the failure occurs.

#### 7.1.4.2. Deployment-specific featuresCopy linkLink copied to clipboard!

##### 7.1.4.2.1. RolloverCopy linkLink copied to clipboard!

The deployment process forDeploymentobjects is driven by a controller loop, in contrast toDeploymentConfigobjects that use deployer pods for every new rollout. This means that theDeploymentobject can have as many active replica sets as possible, and eventually the deployment controller will scale down all old replica sets and scale up the newest one.

DeploymentConfigobjects can have at most one deployer pod running, otherwise multiple deployers might conflict when trying to scale up what they think should be the newest replication controller. Because of this, only two replication controllers can be active at any point in time. Ultimately, this results in faster rapid rollouts forDeploymentobjects.

##### 7.1.4.2.2. Proportional scalingCopy linkLink copied to clipboard!

Because the deployment controller is the sole source of truth for the sizes of new and old replica sets owned by aDeploymentobject, it can scale ongoing rollouts. Additional replicas are distributed proportionally based on the size of each replica set.

DeploymentConfigobjects cannot be scaled when a rollout is ongoing because the controller will have issues with the deployer process about the size of the new replication controller.

##### 7.1.4.2.3. Pausing mid-rolloutCopy linkLink copied to clipboard!

Deployments can be paused at any point in time, meaning you can also pause ongoing rollouts. However, you currently cannot pause deployer pods; if you try to pause a deployment in the middle of a rollout, the deployer process is not affected and continues until it finishes.

#### 7.1.4.3. DeploymentConfig object-specific featuresCopy linkLink copied to clipboard!

##### 7.1.4.3.1. Automatic rollbacksCopy linkLink copied to clipboard!

Currently, deployments do not support automatically rolling back to the last successfully deployed replica set in case of a failure.

##### 7.1.4.3.2. TriggersCopy linkLink copied to clipboard!

Deployments have an implicit config change trigger in that every change in the pod template of a deployment automatically triggers a new rollout. If you do not want new rollouts on pod template changes, pause the deployment:

##### 7.1.4.3.3. Lifecycle hooksCopy linkLink copied to clipboard!

Deployments do not yet support any lifecycle hooks.

##### 7.1.4.3.4. Custom strategiesCopy linkLink copied to clipboard!

Deployments do not support user-specified custom deployment strategies.

## 7.2. Managing deployment processesCopy linkLink copied to clipboard!

### 7.2.1. Managing DeploymentConfig objectsCopy linkLink copied to clipboard!

As of OpenShift Container Platform 4.14,DeploymentConfigobjects are deprecated.DeploymentConfigobjects are still supported, but are not recommended for new installations. Only security-related and critical issues will be fixed.

Instead, useDeploymentobjects or another alternative to provide declarative updates for pods.

DeploymentConfigobjects can be managed from the OpenShift Container Platform web console’sWorkloadspage or using theocCLI. The following procedures show CLI usage unless otherwise stated.

#### 7.2.1.1. Starting a deploymentCopy linkLink copied to clipboard!

You can start a rollout to begin the deployment process of your application.

Procedure

- To start a new deployment process from an existingDeploymentConfigobject, run the following command:oc rollout latest dc/<name>$oc rollout latest dc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf a deployment process is already in progress, the command displays a message and a new replication controller will not be deployed.

To start a new deployment process from an existingDeploymentConfigobject, run the following command:

If a deployment process is already in progress, the command displays a message and a new replication controller will not be deployed.

#### 7.2.1.2. Viewing a deploymentCopy linkLink copied to clipboard!

You can view a deployment to get basic information about all the available revisions of your application.

Procedure

- To show details about all recently created replication controllers for the providedDeploymentConfigobject, including any currently running deployment process, run the following command:oc rollout history dc/<name>$oc rollouthistorydc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

To show details about all recently created replication controllers for the providedDeploymentConfigobject, including any currently running deployment process, run the following command:

- To view details specific to a revision, add the--revisionflag:oc rollout history dc/<name> --revision=1$oc rollouthistorydc/<name>--revision=1Copy to ClipboardCopied!Toggle word wrapToggle overflow

To view details specific to a revision, add the--revisionflag:

- For more detailed information about aDeploymentConfigobject and its latest revision, use theoc describecommand:oc describe dc <name>$oc describedc<name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

For more detailed information about aDeploymentConfigobject and its latest revision, use theoc describecommand:

#### 7.2.1.3. Retrying a deploymentCopy linkLink copied to clipboard!

If the current revision of yourDeploymentConfigobject failed to deploy, you can restart the deployment process.

Procedure

- To restart a failed deployment process:oc rollout retry dc/<name>$oc rollout retry dc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the latest revision of it was deployed successfully, the command displays a message and the deployment process is not retried.Retrying a deployment restarts the deployment process and does not create a new deployment revision. The restarted replication controller has the same configuration it had when it failed.

To restart a failed deployment process:

If the latest revision of it was deployed successfully, the command displays a message and the deployment process is not retried.

Retrying a deployment restarts the deployment process and does not create a new deployment revision. The restarted replication controller has the same configuration it had when it failed.

#### 7.2.1.4. Rolling back a deploymentCopy linkLink copied to clipboard!

Rollbacks revert an application back to a previous revision and can be performed using the REST API, the CLI, or the web console.

Procedure

- To rollback to the last successful deployed revision of your configuration:oc rollout undo dc/<name>$oc rollout undo dc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowTheDeploymentConfigobject’s template is reverted to match the deployment revision specified in the undo command, and a new replication controller is started. If no revision is specified with--to-revision, then the last successfully deployed revision is used.

To rollback to the last successful deployed revision of your configuration:

TheDeploymentConfigobject’s template is reverted to match the deployment revision specified in the undo command, and a new replication controller is started. If no revision is specified with--to-revision, then the last successfully deployed revision is used.

- Image change triggers on theDeploymentConfigobject are disabled as part of the rollback to prevent accidentally starting a new deployment process soon after the rollback is complete.To re-enable the image change triggers:oc set triggers dc/<name> --auto$ocsettriggers dc/<name>--autoCopy to ClipboardCopied!Toggle word wrapToggle overflow

Image change triggers on theDeploymentConfigobject are disabled as part of the rollback to prevent accidentally starting a new deployment process soon after the rollback is complete.

To re-enable the image change triggers:

Deployment configs also support automatically rolling back to the last successful revision of the configuration in case the latest deployment process fails. In that case, the latest template that failed to deploy stays intact by the system and it is up to users to fix their configurations.

#### 7.2.1.5. Executing commands inside a containerCopy linkLink copied to clipboard!

You can add a command to a container, which modifies the container’s startup behavior by overruling the image’sENTRYPOINT. This is different from a lifecycle hook, which instead can be run once per deployment at a specified time.

Procedure

- Add thecommandparameters to thespecfield of theDeploymentConfigobject. You can also add anargsfield, which modifies thecommand(or theENTRYPOINTifcommanddoes not exist).kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
     containers:
     - name: <container_name>
       image: 'image'
       command:
         - '<command>'
       args:
         - '<argument_1>'
         - '<argument_2>'
         - '<argument_3>'kind:DeploymentConfigapiVersion:apps.openshift.io/v1metadata:name:example-dc# ...spec:template:# ...spec:containers:-name:<container_name>image:'image'command:-'<command>'args:-'<argument_1>'-'<argument_2>'-'<argument_3>'Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, to execute thejavacommand with the-jarand/opt/app-root/springboots2idemo.jararguments:kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
      containers:
        - name: example-spring-boot
          image: 'image'
          command:
            - java
          args:
            - '-jar'
            - /opt/app-root/springboots2idemo.jar
# ...kind:DeploymentConfigapiVersion:apps.openshift.io/v1metadata:name:example-dc# ...spec:template:# ...spec:containers:-name:example-spring-bootimage:'image'command:-javaargs:-'-jar'-/opt/app-root/springboots2idemo.jar# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Add thecommandparameters to thespecfield of theDeploymentConfigobject. You can also add anargsfield, which modifies thecommand(or theENTRYPOINTifcommanddoes not exist).

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
     containers:
     - name: <container_name>
       image: 'image'
       command:
         - '<command>'
       args:
         - '<argument_1>'
         - '<argument_2>'
         - '<argument_3>'
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
     containers:
     - name: <container_name>
       image: 'image'
       command:
         - '<command>'
       args:
         - '<argument_1>'
         - '<argument_2>'
         - '<argument_3>'
```

For example, to execute thejavacommand with the-jarand/opt/app-root/springboots2idemo.jararguments:

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
      containers:
        - name: example-spring-boot
          image: 'image'
          command:
            - java
          args:
            - '-jar'
            - /opt/app-root/springboots2idemo.jar
# ...
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
  template:
# ...
    spec:
      containers:
        - name: example-spring-boot
          image: 'image'
          command:
            - java
          args:
            - '-jar'
            - /opt/app-root/springboots2idemo.jar
# ...
```

#### 7.2.1.6. Viewing deployment logsCopy linkLink copied to clipboard!

Procedure

- To stream the logs of the latest revision for a givenDeploymentConfigobject:oc logs -f dc/<name>$oc logs-fdc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the latest revision is running or failed, the command returns the logs of the process that is responsible for deploying your pods. If it is successful, it returns the logs from a pod of your application.

To stream the logs of the latest revision for a givenDeploymentConfigobject:

If the latest revision is running or failed, the command returns the logs of the process that is responsible for deploying your pods. If it is successful, it returns the logs from a pod of your application.

- You can also view logs from older failed deployment processes, if and only if these processes (old replication controllers and their deployer pods) exist and have not been pruned or deleted manually:oc logs --version=1 dc/<name>$oc logs--version=1dc/<name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

You can also view logs from older failed deployment processes, if and only if these processes (old replication controllers and their deployer pods) exist and have not been pruned or deleted manually:

#### 7.2.1.7. Deployment triggersCopy linkLink copied to clipboard!

ADeploymentConfigobject can contain triggers, which drive the creation of new deployment processes in response to events inside the cluster.

If no triggers are defined on aDeploymentConfigobject, a config change trigger is added by default. If triggers are defined as an empty field, deployments must be started manually.

##### 7.2.1.7.1. Config change deployment triggersCopy linkLink copied to clipboard!

The config change trigger results in a new replication controller whenever configuration changes are detected in the pod template of theDeploymentConfigobject.

If a config change trigger is defined on aDeploymentConfigobject, the first replication controller is automatically created soon after theDeploymentConfigobject itself is created and it is not paused.

Config change deployment trigger

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  triggers:
    - type: "ConfigChange"
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  triggers:
    - type: "ConfigChange"
```

##### 7.2.1.7.2. Image change deployment triggersCopy linkLink copied to clipboard!

The image change trigger results in a new replication controller whenever the content of an image stream tag changes (when a new version of the image is pushed).

Image change deployment trigger

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  triggers:
    - type: "ImageChange"
      imageChangeParams:
        automatic: true 
        from:
          kind: "ImageStreamTag"
          name: "origin-ruby-sample:latest"
          namespace: "myproject"
        containerNames:
          - "helloworld"
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  triggers:
    - type: "ImageChange"
      imageChangeParams:
        automatic: true
```

```
from:
          kind: "ImageStreamTag"
          name: "origin-ruby-sample:latest"
          namespace: "myproject"
        containerNames:
          - "helloworld"
```

**1**
  If theimageChangeParams.automaticfield is set tofalse, the trigger is disabled.

With the above example, when thelatesttag value of theorigin-ruby-sampleimage stream changes and the new image value differs from the current image specified in theDeploymentConfigobject’shelloworldcontainer, a new replication controller is created using the new image for thehelloworldcontainer.

If an image change trigger is defined on aDeploymentConfigobject (with a config change trigger andautomatic=false, or withautomatic=true) and the image stream tag pointed by the image change trigger does not exist yet, the initial deployment process will automatically start as soon as an image is imported or pushed by a build to the image stream tag.

##### 7.2.1.7.3. Setting deployment triggersCopy linkLink copied to clipboard!

Procedure

- You can set deployment triggers for aDeploymentConfigobject using theoc set triggerscommand. For example, to set a image change trigger, use the following command:oc set triggers dc/<dc_name> \
    --from-image=<project>/<image>:<tag> -c <container_name>$ocsettriggers dc/<dc_name>\--from-image=<project>/<image>:<tag>-c<container_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

You can set deployment triggers for aDeploymentConfigobject using theoc set triggerscommand. For example, to set a image change trigger, use the following command:

```
oc set triggers dc/<dc_name> \
    --from-image=<project>/<image>:<tag> -c <container_name>
```

```
$ oc set triggers dc/<dc_name> \
    --from-image=<project>/<image>:<tag> -c <container_name>
```

#### 7.2.1.8. Setting deployment resourcesCopy linkLink copied to clipboard!

A deployment is completed by a pod that consumes resources (memory, CPU, and ephemeral storage) on a node. By default, pods consume unbounded node resources. However, if a project specifies default container limits, then pods consume resources up to those limits.

The minimum memory limit for a deployment is 12 MB. If a container fails to start due to aCannot allocate memorypod event, the memory limit is too low. Either increase or remove the memory limit. Removing the limit allows pods to consume unbounded node resources.

You can also limit resource use by specifying resource limits as part of the deployment strategy. Deployment resources can be used with the recreate, rolling, or custom deployment strategies.

Procedure

- In the following example, each ofresources,cpu,memory, andephemeral-storageis optional:kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    limits:
      cpu: "100m" 
      memory: "256Mi" 
      ephemeral-storage: "1Gi"kind:DeploymentapiVersion:apps/v1metadata:name:hello-openshift# ...spec:# ...type:"Recreate"resources:limits:cpu:"100m"1memory:"256Mi"2ephemeral-storage:"1Gi"3Copy to ClipboardCopied!Toggle word wrapToggle overflow1cpuis in CPU units:100mrepresents 0.1 CPU units (100 * 1e-3).2memoryis in bytes:256Mirepresents 268435456 bytes (256 * 2 ^ 20).3ephemeral-storageis in bytes:1Girepresents 1073741824 bytes (2 ^ 30).However, if a quota has been defined for your project, one of the following two items is required:Aresourcessection set with an explicitrequests:kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    requests: 
      cpu: "100m"
      memory: "256Mi"
      ephemeral-storage: "1Gi"kind:DeploymentapiVersion:apps/v1metadata:name:hello-openshift# ...spec:# ...type:"Recreate"resources:requests:1cpu:"100m"memory:"256Mi"ephemeral-storage:"1Gi"Copy to ClipboardCopied!Toggle word wrapToggle overflow1Therequestsobject contains the list of resources that correspond to the list of resources in the quota.A limit range defined in your project, where the defaults from theLimitRangeobject apply to pods created during the deployment process.To set deployment resources, choose one of the above options. Otherwise, deploy pod creation fails, citing a failure to satisfy quota.

In the following example, each ofresources,cpu,memory, andephemeral-storageis optional:

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    limits:
      cpu: "100m" 
      memory: "256Mi" 
      ephemeral-storage: "1Gi"
```

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    limits:
      cpu: "100m"
```

```
memory: "256Mi"
```

```
ephemeral-storage: "1Gi"
```

**1**
  cpuis in CPU units:100mrepresents 0.1 CPU units (100 * 1e-3).

**2**
  memoryis in bytes:256Mirepresents 268435456 bytes (256 * 2 ^ 20).

**3**
  ephemeral-storageis in bytes:1Girepresents 1073741824 bytes (2 ^ 30).

However, if a quota has been defined for your project, one of the following two items is required:

- Aresourcessection set with an explicitrequests:kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    requests: 
      cpu: "100m"
      memory: "256Mi"
      ephemeral-storage: "1Gi"kind:DeploymentapiVersion:apps/v1metadata:name:hello-openshift# ...spec:# ...type:"Recreate"resources:requests:1cpu:"100m"memory:"256Mi"ephemeral-storage:"1Gi"Copy to ClipboardCopied!Toggle word wrapToggle overflow1Therequestsobject contains the list of resources that correspond to the list of resources in the quota.

Aresourcessection set with an explicitrequests:

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    requests: 
      cpu: "100m"
      memory: "256Mi"
      ephemeral-storage: "1Gi"
```

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  type: "Recreate"
  resources:
    requests:
```

```
cpu: "100m"
      memory: "256Mi"
      ephemeral-storage: "1Gi"
```

**1**
  Therequestsobject contains the list of resources that correspond to the list of resources in the quota.
- A limit range defined in your project, where the defaults from theLimitRangeobject apply to pods created during the deployment process.

To set deployment resources, choose one of the above options. Otherwise, deploy pod creation fails, citing a failure to satisfy quota.

#### 7.2.1.9. Scaling manuallyCopy linkLink copied to clipboard!

In addition to rollbacks, you can exercise fine-grained control over the number of replicas by manually scaling them.

Pods can also be auto-scaled using theoc autoscalecommand.

Procedure

- To manually scale aDeploymentConfigobject, use theoc scalecommand. For example, the following command sets the replicas in thefrontendDeploymentConfigobject to3.oc scale dc frontend --replicas=3$oc scaledcfrontend--replicas=3Copy to ClipboardCopied!Toggle word wrapToggle overflowThe number of replicas eventually propagates to the desired and current state of the deployment configured by theDeploymentConfigobjectfrontend.

To manually scale aDeploymentConfigobject, use theoc scalecommand. For example, the following command sets the replicas in thefrontendDeploymentConfigobject to3.

The number of replicas eventually propagates to the desired and current state of the deployment configured by theDeploymentConfigobjectfrontend.

#### 7.2.1.10. Accessing private repositories from DeploymentConfig objectsCopy linkLink copied to clipboard!

You can add a secret to yourDeploymentConfigobject so that it can access images from a private repository. This procedure shows the OpenShift Container Platform web console method.

Procedure

- Create a new project.
- Navigate toWorkloadsSecrets.
- Create a secret that contains credentials for accessing a private image repository.
- Navigate toWorkloadsDeploymentConfigs.
- Create aDeploymentConfigobject.
- On theDeploymentConfigobject editor page, set thePull Secretand save your changes.

#### 7.2.1.11. Assigning pods to specific nodesCopy linkLink copied to clipboard!

You can use node selectors in conjunction with labeled nodes to control pod placement.

Cluster administrators can set the default node selector for a project in order to restrict pod placement to specific nodes. As a developer, you can set a node selector on aPodconfiguration to restrict nodes even further.

Procedure

- To add a node selector when creating a pod, edit thePodconfiguration, and add thenodeSelectorvalue. This can be added to a singlePodconfiguration, or in aPodtemplate:apiVersion: v1
kind: Pod
metadata:
  name: my-pod
# ...
spec:
  nodeSelector:
    disktype: ssd
# ...apiVersion:v1kind:Podmetadata:name:my-pod# ...spec:nodeSelector:disktype:ssd# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowPods created when the node selector is in place are assigned to nodes with the specified labels. The labels specified here are used in conjunction with the labels added by a cluster administrator.For example, if a project has thetype=user-nodeandregion=eastlabels added to a project by the cluster administrator, and you add the abovedisktype: ssdlabel to a pod, the pod is only ever scheduled on nodes that have all three labels.Labels can only be set to one value, so setting a node selector ofregion=westin aPodconfiguration that hasregion=eastas the administrator-set default, results in a pod that will never be scheduled.

To add a node selector when creating a pod, edit thePodconfiguration, and add thenodeSelectorvalue. This can be added to a singlePodconfiguration, or in aPodtemplate:

```
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
# ...
spec:
  nodeSelector:
    disktype: ssd
# ...
```

```
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
# ...
spec:
  nodeSelector:
    disktype: ssd
# ...
```

Pods created when the node selector is in place are assigned to nodes with the specified labels. The labels specified here are used in conjunction with the labels added by a cluster administrator.

For example, if a project has thetype=user-nodeandregion=eastlabels added to a project by the cluster administrator, and you add the abovedisktype: ssdlabel to a pod, the pod is only ever scheduled on nodes that have all three labels.

Labels can only be set to one value, so setting a node selector ofregion=westin aPodconfiguration that hasregion=eastas the administrator-set default, results in a pod that will never be scheduled.

#### 7.2.1.12. Running a pod with a different service accountCopy linkLink copied to clipboard!

You can run a pod with a service account other than the default.

Procedure

- Edit theDeploymentConfigobject:oc edit dc/<deployment_config>$oc edit dc/<deployment_config>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theDeploymentConfigobject:

- Add theserviceAccountandserviceAccountNameparameters to thespecfield, and specify the service account you want to use:apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: example-dc
# ...
spec:
# ...
  securityContext: {}
  serviceAccount: <service_account>
  serviceAccountName: <service_account>apiVersion:apps.openshift.io/v1kind:DeploymentConfigmetadata:name:example-dc# ...spec:# ...securityContext:{}serviceAccount:<service_account>serviceAccountName:<service_account>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Add theserviceAccountandserviceAccountNameparameters to thespecfield, and specify the service account you want to use:

```
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: example-dc
# ...
spec:
# ...
  securityContext: {}
  serviceAccount: <service_account>
  serviceAccountName: <service_account>
```

```
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: example-dc
# ...
spec:
# ...
  securityContext: {}
  serviceAccount: <service_account>
  serviceAccountName: <service_account>
```

## 7.3. Using deployment strategiesCopy linkLink copied to clipboard!

Deployment strategiesare used to change or upgrade applications without downtime so that users barely notice a change.

Because users generally access applications through a route handled by a router, deployment strategies can focus onDeploymentConfigobject features or routing features. Strategies that focus onDeploymentConfigobject features impact all routes that use the application. Strategies that use router features target individual routes.

Most deployment strategies are supported through theDeploymentConfigobject, and some additional strategies are supported through router features.

### 7.3.1. Choosing a deployment strategyCopy linkLink copied to clipboard!

Consider the following when choosing a deployment strategy:

- Long-running connections must be handled gracefully.
- Database conversions can be complex and must be done and rolled back along with the application.
- If the application is a hybrid of microservices and traditional components, downtime might be required to complete the transition.
- You must have the infrastructure to do this.
- If you have a non-isolated test environment, you can break both new and old versions.

A deployment strategy uses readiness checks to determine if a new pod is ready for use. If a readiness check fails, theDeploymentConfigobject retries to run the pod until it times out. The default timeout is10m, a value set inTimeoutSecondsindc.spec.strategy.*params.

### 7.3.2. Rolling strategyCopy linkLink copied to clipboard!

A rolling deployment slowly replaces instances of the previous version of an application with instances of the new version of the application. The rolling strategy is the default deployment strategy used if no strategy is specified on aDeploymentConfigobject.

A rolling deployment typically waits for new pods to becomereadyvia a readiness check before scaling down the old components. If a significant issue occurs, the rolling deployment can be aborted.

When to use a rolling deployment:

- When you want to take no downtime during an application update.
- When your application supports having old code and new code running at the same time.

A rolling deployment means you have both old and new versions of your code running at the same time. This typically requires that your application handle N-1 compatibility.

Example rolling strategy definition

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Rolling
    rollingParams:
      updatePeriodSeconds: 1 
      intervalSeconds: 1 
      timeoutSeconds: 120 
      maxSurge: "20%" 
      maxUnavailable: "10%" 
      pre: {} 
     post: {}
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Rolling
    rollingParams:
      updatePeriodSeconds: 1
```

```
intervalSeconds: 1
```

```
timeoutSeconds: 120
```

```
maxSurge: "20%"
```

```
maxUnavailable: "10%"
```

```
pre: {}
```

```
post: {}
```

**1**
  The time to wait between individual pod updates. If unspecified, this value defaults to1.

**2**
  The time to wait between polling the deployment status after update. If unspecified, this value defaults to1.

**3**
  The time to wait for a scaling event before giving up. Optional; the default is600. Here,giving upmeans automatically rolling back to the previous complete deployment.

**4**
  maxSurgeis optional and defaults to25%if not specified. See the information below the following procedure.

**5**
  maxUnavailableis optional and defaults to25%if not specified. See the information below the following procedure.

**6**
  preandpostare both lifecycle hooks.

The rolling strategy:

- Executes anyprelifecycle hook.
- Scales up the new replication controller based on the surge count.
- Scales down the old replication controller based on the max unavailable count.
- Repeats this scaling until the new replication controller has reached the desired replica count and the old replication controller has been scaled to zero.
- Executes anypostlifecycle hook.

When scaling down, the rolling strategy waits for pods to become ready so it can decide whether further scaling would affect availability. If scaled up pods never become ready, the deployment process will eventually time out and result in a deployment failure.

ThemaxUnavailableparameter is the maximum number of pods that can be unavailable during the update. ThemaxSurgeparameter is the maximum number of pods that can be scheduled above the original number of pods. Both parameters can be set to either a percentage (e.g.,10%) or an absolute value (e.g.,2). The default value for both is25%.

These parameters allow the deployment to be tuned for availability and speed. For example:

- maxUnavailable*=0andmaxSurge*=20%ensures full capacity is maintained during the update and rapid scale up.
- maxUnavailable*=10%andmaxSurge*=0performs an update using no extra capacity (an in-place update).
- maxUnavailable*=10%andmaxSurge*=10%scales up and down quickly with some potential for capacity loss.

Generally, if you want fast rollouts, usemaxSurge. If you have to take into account resource quota and can accept partial unavailability, usemaxUnavailable.

The default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

#### 7.3.2.1. Canary deploymentsCopy linkLink copied to clipboard!

All rolling deployments in OpenShift Container Platform arecanary deployments; a new version (the canary) is tested before all of the old instances are replaced. If the readiness check never succeeds, the canary instance is removed and theDeploymentConfigobject will be automatically rolled back.

The readiness check is part of the application code and can be as sophisticated as necessary to ensure the new instance is ready to be used. If you must implement more complex checks of the application (such as sending real user workloads to the new instance), consider implementing a custom deployment or using a blue-green deployment strategy.

#### 7.3.2.2. Creating a rolling deploymentCopy linkLink copied to clipboard!

Rolling deployments are the default type in OpenShift Container Platform. You can create a rolling deployment using the CLI.

Procedure

- Create an application based on the example deployment images found inQuay.io:oc new-app quay.io/openshifttest/deployment-example:latest$oc new-app quay.io/openshifttest/deployment-example:latestCopy to ClipboardCopied!Toggle word wrapToggle overflowThis image does not expose any ports. If you want to expose your applications over an external LoadBalancer service or enable access to the application over the public internet, create a service by using theoc expose dc/deployment-example --port=<port>command after completing this procedure.

Create an application based on the example deployment images found inQuay.io:

This image does not expose any ports. If you want to expose your applications over an external LoadBalancer service or enable access to the application over the public internet, create a service by using theoc expose dc/deployment-example --port=<port>command after completing this procedure.

- If you have the router installed, make the application available via a route or use the service IP directly.oc expose svc/deployment-example$oc expose svc/deployment-exampleCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you have the router installed, make the application available via a route or use the service IP directly.

- Browse to the application atdeployment-example.<project>.<router_domain>to verify you see thev1image.
- Scale theDeploymentConfigobject up to three replicas:oc scale dc/deployment-example --replicas=3$oc scale dc/deployment-example--replicas=3Copy to ClipboardCopied!Toggle word wrapToggle overflow

Scale theDeploymentConfigobject up to three replicas:

- Trigger a new deployment automatically by tagging a new version of the example as thelatesttag:oc tag deployment-example:v2 deployment-example:latest$oc tag deployment-example:v2 deployment-example:latestCopy to ClipboardCopied!Toggle word wrapToggle overflow

Trigger a new deployment automatically by tagging a new version of the example as thelatesttag:

- In your browser, refresh the page until you see thev2image.
- When using the CLI, the following command shows how many pods are on version 1 and how many are on version 2. In the web console, the pods are progressively added to v2 and removed from v1:oc describe dc deployment-example$oc describedcdeployment-exampleCopy to ClipboardCopied!Toggle word wrapToggle overflow

When using the CLI, the following command shows how many pods are on version 1 and how many are on version 2. In the web console, the pods are progressively added to v2 and removed from v1:

During the deployment process, the new replication controller is incrementally scaled up. After the new pods are marked asready(by passing their readiness check), the deployment process continues.

If the pods do not become ready, the process aborts, and the deployment rolls back to its previous version.

#### 7.3.2.3. Editing a deployment by using the Developer perspectiveCopy linkLink copied to clipboard!

You can edit the deployment strategy, image settings, environment variables, and advanced options for your deployment by using theDeveloperperspective.

Prerequisites

- You are in theDeveloperperspective of the web console.
- You have created an application.

Procedure

- Navigate to theTopologyview.
- Click your application to see theDetailspanel.
- In theActionsdrop-down menu, selectEdit Deploymentto view theEdit Deploymentpage.
- You can edit the followingAdvanced optionsfor your deployment:Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.

You can edit the followingAdvanced optionsfor your deployment:

- Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.

By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

- Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.
- ClickSave.

#### 7.3.2.4. Starting a rolling deployment using the Developer perspectiveCopy linkLink copied to clipboard!

You can upgrade an application by starting a rolling deployment.

Prerequisites

- You are in theDeveloperperspective of the web console.
- You have created an application.

Procedure

- In theTopologyview, click the application node to see theOverviewtab in the side panel. Note that theUpdate Strategyis set to the defaultRollingstrategy.
- In theActionsdrop-down menu, selectStart Rolloutto start a rolling update. The rolling deployment spins up the new version of the application and then terminates the old one.Figure 7.1. Rolling update

In theActionsdrop-down menu, selectStart Rolloutto start a rolling update. The rolling deployment spins up the new version of the application and then terminates the old one.

Figure 7.1. Rolling update

### 7.3.3. Recreate strategyCopy linkLink copied to clipboard!

The recreate strategy has basic rollout behavior and supports lifecycle hooks for injecting code into the deployment process.

Example recreate strategy definition

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  strategy:
    type: Recreate
    recreateParams: 
      pre: {} 
      mid: {}
      post: {}
```

```
kind: Deployment
apiVersion: apps/v1
metadata:
  name: hello-openshift
# ...
spec:
# ...
  strategy:
    type: Recreate
    recreateParams:
```

```
pre: {}
```

```
mid: {}
      post: {}
```

**1**
  recreateParamsare optional.

**2**
  pre,mid, andpostare lifecycle hooks.

The recreate strategy:

- Executes anyprelifecycle hook.
- Scales down the previous deployment to zero.
- Executes anymidlifecycle hook.
- Scales up the new deployment.
- Executes anypostlifecycle hook.

During scale up, if the replica count of the deployment is greater than one, the first replica of the deployment will be validated for readiness before fully scaling up the deployment. If the validation of the first replica fails, the deployment will be considered a failure.

When to use a recreate deployment:

- When you must run migrations or other data transformations before your new code starts.
- When you do not support having new and old versions of your application code running at the same time.
- When you want to use a RWO volume, which is not supported being shared between multiple replicas.

A recreate deployment incurs downtime because, for a brief period, no instances of your application are running. However, your old code and new code do not run at the same time.

#### 7.3.3.1. Editing a deployment by using the Developer perspectiveCopy linkLink copied to clipboard!

You can edit the deployment strategy, image settings, environment variables, and advanced options for your deployment by using theDeveloperperspective.

Prerequisites

- You are in theDeveloperperspective of the web console.
- You have created an application.

Procedure

- Navigate to theTopologyview.
- Click your application to see theDetailspanel.
- In theActionsdrop-down menu, selectEdit Deploymentto view theEdit Deploymentpage.
- You can edit the followingAdvanced optionsfor your deployment:Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.

You can edit the followingAdvanced optionsfor your deployment:

- Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.

By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

- Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.
- ClickSave.

#### 7.3.3.2. Starting a recreate deployment using the Developer perspectiveCopy linkLink copied to clipboard!

You can switch the deployment strategy from the default rolling update to a recreate update using theDeveloperperspective in the web console.

Prerequisites

- Ensure that you are in theDeveloperperspective of the web console.
- Ensure that you have created an application using theAddview and see it deployed in theTopologyview.

Procedure

To switch to a recreate update strategy and to upgrade an application:

- Click your application to see theDetailspanel.
- In theActionsdrop-down menu, selectEdit Deployment Configto see the deployment configuration details of the application.
- In the YAML editor, change thespec.strategy.typetoRecreateand clickSave.
- In theTopologyview, select the node to see theOverviewtab in the side panel. TheUpdate Strategyis now set toRecreate.
- Use theActionsdrop-down menu to selectStart Rolloutto start an update using the recreate strategy. The recreate strategy first terminates pods for the older version of the application and then spins up pods for the new version.Figure 7.2. Recreate update

Use theActionsdrop-down menu to selectStart Rolloutto start an update using the recreate strategy. The recreate strategy first terminates pods for the older version of the application and then spins up pods for the new version.

Figure 7.2. Recreate update

### 7.3.4. Custom strategyCopy linkLink copied to clipboard!

The custom strategy allows you to provide your own deployment behavior.

Example custom strategy definition

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Custom
    customParams:
      image: organization/strategy
      command: [ "command", "arg1" ]
      environment:
        - name: ENV_1
          value: VALUE_1
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Custom
    customParams:
      image: organization/strategy
      command: [ "command", "arg1" ]
      environment:
        - name: ENV_1
          value: VALUE_1
```

In the above example, theorganization/strategycontainer image provides the deployment behavior. The optionalcommandarray overrides anyCMDdirective specified in the image’sDockerfile. The optional environment variables provided are added to the execution environment of the strategy process.

Additionally, OpenShift Container Platform provides the following environment variables to the deployment process:

| Environment variable | Description |
| --- | --- |
| OPENSHIFT_DEPLOYMENT_NAME | The name of the new deployment, a replication controller. |
| OPENSHIFT_DEPLOYMENT_NAMESPACE | The name space of the new deployment. |

OPENSHIFT_DEPLOYMENT_NAME

The name of the new deployment, a replication controller.

OPENSHIFT_DEPLOYMENT_NAMESPACE

The name space of the new deployment.

The replica count of the new deployment will initially be zero. The responsibility of the strategy is to make the new deployment active using the logic that best serves the needs of the user.

Alternatively, use thecustomParamsobject to inject the custom deployment logic into the existing deployment strategies. Provide a custom shell script logic and call theopenshift-deploybinary. Users do not have to supply their custom deployer container image; in this case, the default OpenShift Container Platform deployer image is used instead:

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Rolling
    customParams:
      command:
      - /bin/sh
      - -c
      - |
        set -e
        openshift-deploy --until=50%
        echo Halfway there
        openshift-deploy
        echo Complete
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: example-dc
# ...
spec:
# ...
  strategy:
    type: Rolling
    customParams:
      command:
      - /bin/sh
      - -c
      - |
        set -e
        openshift-deploy --until=50%
        echo Halfway there
        openshift-deploy
        echo Complete
```

This results in following deployment:

```
Started deployment #2
--> Scaling up custom-deployment-2 from 0 to 2, scaling down custom-deployment-1 from 2 to 0 (keep 2 pods available, don't exceed 3 pods)
    Scaling custom-deployment-2 up to 1
--> Reached 50% (currently 50%)
Halfway there
--> Scaling up custom-deployment-2 from 1 to 2, scaling down custom-deployment-1 from 2 to 0 (keep 2 pods available, don't exceed 3 pods)
    Scaling custom-deployment-1 down to 1
    Scaling custom-deployment-2 up to 2
    Scaling custom-deployment-1 down to 0
--> Success
Complete
```

```
Started deployment #2
--> Scaling up custom-deployment-2 from 0 to 2, scaling down custom-deployment-1 from 2 to 0 (keep 2 pods available, don't exceed 3 pods)
    Scaling custom-deployment-2 up to 1
--> Reached 50% (currently 50%)
Halfway there
--> Scaling up custom-deployment-2 from 1 to 2, scaling down custom-deployment-1 from 2 to 0 (keep 2 pods available, don't exceed 3 pods)
    Scaling custom-deployment-1 down to 1
    Scaling custom-deployment-2 up to 2
    Scaling custom-deployment-1 down to 0
--> Success
Complete
```

If the custom deployment strategy process requires access to the OpenShift Container Platform API or the Kubernetes API the container that executes the strategy can use the service account token available inside the container for authentication.

#### 7.3.4.1. Editing a deployment by using the Developer perspectiveCopy linkLink copied to clipboard!

You can edit the deployment strategy, image settings, environment variables, and advanced options for your deployment by using theDeveloperperspective.

Prerequisites

- You are in theDeveloperperspective of the web console.
- You have created an application.

Procedure

- Navigate to theTopologyview.
- Click your application to see theDetailspanel.
- In theActionsdrop-down menu, selectEdit Deploymentto view theEdit Deploymentpage.
- You can edit the followingAdvanced optionsfor your deployment:Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.

You can edit the followingAdvanced optionsfor your deployment:

- Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

Optional: You can pause rollouts by clickingPause rollouts, and then selecting thePause rollouts for this deploymentcheckbox.

By pausing rollouts, you can make changes to your application without triggering a rollout. You can resume rollouts at any time.

- Optional: ClickScalingto change the number of instances of your image by modifying the number ofReplicas.
- ClickSave.

### 7.3.5. Lifecycle hooksCopy linkLink copied to clipboard!

The rolling and recreate strategies supportlifecycle hooks, or deployment hooks, which allow behavior to be injected into the deployment process at predefined points within the strategy:

Exampleprelifecycle hook

```
pre:
  failurePolicy: Abort
  execNewPod: {}
```

```
pre:
  failurePolicy: Abort
  execNewPod: {}
```

**1**
  execNewPodis a pod-based lifecycle hook.

Every hook has afailure policy, which defines the action the strategy should take when a hook failure is encountered:

| Abort | The deployment process will be considered a failure if the hook fails. |
| --- | --- |
| Retry | The hook execution should be retried until it succeeds. |
| Ignore | Any hook failure should be ignored and the deployment should proceed. |

Abort

The deployment process will be considered a failure if the hook fails.

Retry

The hook execution should be retried until it succeeds.

Ignore

Any hook failure should be ignored and the deployment should proceed.

Hooks have a type-specific field that describes how to execute the hook. Currently, pod-based hooks are the only supported hook type, specified by theexecNewPodfield.

#### 7.3.5.1. Pod-based lifecycle hookCopy linkLink copied to clipboard!

Pod-based lifecycle hooks execute hook code in a new pod derived from the template in aDeploymentConfigobject.

The following simplified example deployment uses the rolling strategy. Triggers and some other minor details are omitted for brevity:

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: frontend
spec:
  template:
    metadata:
      labels:
        name: frontend
    spec:
      containers:
        - name: helloworld
          image: openshift/origin-ruby-sample
  replicas: 5
  selector:
    name: frontend
  strategy:
    type: Rolling
    rollingParams:
      pre:
        failurePolicy: Abort
        execNewPod:
          containerName: helloworld 
          command: [ "/usr/bin/command", "arg1", "arg2" ] 
          env: 
            - name: CUSTOM_VAR1
              value: custom_value1
          volumes:
            - data
```

```
kind: DeploymentConfig
apiVersion: apps.openshift.io/v1
metadata:
  name: frontend
spec:
  template:
    metadata:
      labels:
        name: frontend
    spec:
      containers:
        - name: helloworld
          image: openshift/origin-ruby-sample
  replicas: 5
  selector:
    name: frontend
  strategy:
    type: Rolling
    rollingParams:
      pre:
        failurePolicy: Abort
        execNewPod:
          containerName: helloworld
```

```
command: [ "/usr/bin/command", "arg1", "arg2" ]
```

```
env:
```

```
- name: CUSTOM_VAR1
              value: custom_value1
          volumes:
            - data
```

**1**
  Thehelloworldname refers tospec.template.spec.containers[0].name.

**2**
  Thiscommandoverrides anyENTRYPOINTdefined by theopenshift/origin-ruby-sampleimage.

**3**
  envis an optional set of environment variables for the hook container.

**4**
  volumesis an optional set of volume references for the hook container.

In this example, theprehook will be executed in a new pod using theopenshift/origin-ruby-sampleimage from thehelloworldcontainer. The hook pod has the following properties:

- The hook command is/usr/bin/command arg1 arg2.
- The hook container has theCUSTOM_VAR1=custom_value1environment variable.
- The hook failure policy isAbort, meaning the deployment process fails if the hook fails.
- The hook pod inherits thedatavolume from theDeploymentConfigobject pod.

#### 7.3.5.2. Setting lifecycle hooksCopy linkLink copied to clipboard!

You can set lifecycle hooks, or deployment hooks, for a deployment using the CLI.

Procedure

- Use theoc set deployment-hookcommand to set the type of hook you want:--pre,--mid, or--post. For example, to set a pre-deployment hook:oc set deployment-hook dc/frontend \
    --pre -c helloworld -e CUSTOM_VAR1=custom_value1 \
    --volumes data --failure-policy=abort -- /usr/bin/command arg1 arg2$ocsetdeployment-hook dc/frontend\--pre-chelloworld-eCUSTOM_VAR1=custom_value1\--volumesdata --failure-policy=abort -- /usr/bin/command arg1 arg2Copy to ClipboardCopied!Toggle word wrapToggle overflow

Use theoc set deployment-hookcommand to set the type of hook you want:--pre,--mid, or--post. For example, to set a pre-deployment hook:

```
oc set deployment-hook dc/frontend \
    --pre -c helloworld -e CUSTOM_VAR1=custom_value1 \
    --volumes data --failure-policy=abort -- /usr/bin/command arg1 arg2
```

```
$ oc set deployment-hook dc/frontend \
    --pre -c helloworld -e CUSTOM_VAR1=custom_value1 \
    --volumes data --failure-policy=abort -- /usr/bin/command arg1 arg2
```

## 7.4. Using route-based deployment strategiesCopy linkLink copied to clipboard!

Deployment strategies provide a way for the application to evolve. Some strategies useDeploymentobjects to make changes that are seen by users of all routes that resolve to the application. Other advanced strategies, such as the ones described in this section, use router features in conjunction withDeploymentobjects to impact specific routes.

The most common route-based strategy is to use ablue-green deployment. The new version (the green version) is brought up for testing and evaluation, while the users still use the stable version (the blue version). When ready, the users are switched to the green version. If a problem arises, you can switch back to the blue version.

Alternatively, you can use anA/B versionsstrategy in which both versions are active at the same time. With this strategy, some users can useversion A, and other users can useversion B. You can use this strategy to experiment with user interface changes or other features in order to get user feedback. You can also use it to verify proper operation in a production context where problems impact a limited number of users.

A canary deployment tests the new version but when a problem is detected it quickly falls back to the previous version. This can be done with both of the above strategies.

The route-based deployment strategies do not scale the number of pods in the services. To maintain desired performance characteristics the deployment configurations might have to be scaled.

### 7.4.1. Proxy shards and traffic splittingCopy linkLink copied to clipboard!

In production environments, you can precisely control the distribution of traffic that lands on a particular shard. When dealing with large numbers of instances, you can use the relative scale of individual shards to implement percentage based traffic. That combines well with aproxy shard, which forwards or splits the traffic it receives to a separate service or application running elsewhere.

In the simplest configuration, the proxy forwards requests unchanged. In more complex setups, you can duplicate the incoming requests and send to both a separate cluster as well as to a local instance of the application, and compare the result. Other patterns include keeping the caches of a DR installation warm, or sampling incoming traffic for analysis purposes.

Any TCP (or UDP) proxy could be run under the desired shard. Use theoc scalecommand to alter the relative number of instances serving requests under the proxy shard. For more complex traffic management, consider customizing the OpenShift Container Platform router with proportional balancing capabilities.

### 7.4.2. N-1 compatibilityCopy linkLink copied to clipboard!

Applications that have new code and old code running at the same time must be careful to ensure that data written by the new code can be read and handled (or gracefully ignored) by the old version of the code. This is sometimes calledschema evolutionand is a complex problem.

This can take many forms: data stored on disk, in a database, in a temporary cache, or that is part of a user’s browser session. While most web applications can support rolling deployments, it is important to test and design your application to handle it.

For some applications, the period of time that old code and new code is running side by side is short, so bugs or some failed user transactions are acceptable. For others, the failure pattern may result in the entire application becoming non-functional.

One way to validate N-1 compatibility is to use an A/B deployment: run the old code and new code at the same time in a controlled way in a test environment, and verify that traffic that flows to the new deployment does not cause failures in the old deployment.

### 7.4.3. Graceful terminationCopy linkLink copied to clipboard!

OpenShift Container Platform and Kubernetes give application instances time to shut down before removing them from load balancing rotations. However, applications must ensure they cleanly terminate user connections as well before they exit.

On shutdown, OpenShift Container Platform sends aTERMsignal to the processes in the container. Application code, on receivingSIGTERM, stop accepting new connections. This ensures that load balancers route traffic to other active instances. The application code then waits until all open connections are closed, or gracefully terminate individual connections at the next opportunity, before exiting.

After the graceful termination period expires, a process that has not exited is sent theKILLsignal, which immediately ends the process. TheterminationGracePeriodSecondsattribute of a pod or pod template controls the graceful termination period (default 30 seconds) and can be customized per application as necessary.

### 7.4.4. Blue-green deploymentsCopy linkLink copied to clipboard!

Blue-green deployments involve running two versions of an application at the same time and moving traffic from the in-production version (the blue version) to the newer version (the green version). You can use a rolling strategy or switch services in a route.

Because many applications depend on persistent data, you must have an application that supportsN-1 compatibility, which means it shares data and implements live migration between the database, store, or disk by creating two copies of the data layer.

Consider the data used in testing the new version. If it is the production data, a bug in the new version can break the production version.

#### 7.4.4.1. Setting up a blue-green deploymentCopy linkLink copied to clipboard!

Blue-green deployments use twoDeploymentobjects. Both are running, and the one in production depends on the service the route specifies, with eachDeploymentobject exposed to a different service.

Routes are intended for web (HTTP and HTTPS) traffic, so this technique is best suited for web applications.

You can create a new route to the new version and test it. When ready, change the service in the production route to point to the new service and the new (green) version is live.

If necessary, you can roll back to the older (blue) version by switching the service back to the previous version.

Procedure

- Create two independent application components.Create a copy of the example application running thev1image under theexample-blueservice:oc new-app openshift/deployment-example:v1 --name=example-blue$oc new-app openshift/deployment-example:v1--name=example-blueCopy to ClipboardCopied!Toggle word wrapToggle overflowCreate a second copy that uses thev2image under theexample-greenservice:oc new-app openshift/deployment-example:v2 --name=example-green$oc new-app openshift/deployment-example:v2--name=example-greenCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create two independent application components.

- Create a copy of the example application running thev1image under theexample-blueservice:oc new-app openshift/deployment-example:v1 --name=example-blue$oc new-app openshift/deployment-example:v1--name=example-blueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a copy of the example application running thev1image under theexample-blueservice:

- Create a second copy that uses thev2image under theexample-greenservice:oc new-app openshift/deployment-example:v2 --name=example-green$oc new-app openshift/deployment-example:v2--name=example-greenCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a second copy that uses thev2image under theexample-greenservice:

- Create a route that points to the old service:oc expose svc/example-blue --name=bluegreen-example$oc expose svc/example-blue--name=bluegreen-exampleCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a route that points to the old service:

- Browse to the application atbluegreen-example-<project>.<router_domain>to verify you see thev1image.
- Edit the route and change the service name toexample-green:oc patch route/bluegreen-example -p '{"spec":{"to":{"name":"example-green"}}}'$oc patch route/bluegreen-example-p'{"spec":{"to":{"name":"example-green"}}}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Edit the route and change the service name toexample-green:

- To verify that the route has changed, refresh the browser until you see thev2image.

### 7.4.5. A/B deploymentsCopy linkLink copied to clipboard!

The A/B deployment strategy lets you try a new version of the application in a limited way in the production environment. You can specify that the production version gets most of the user requests while a limited fraction of requests go to the new version.

Because you control the portion of requests to each version, as testing progresses you can increase the fraction of requests to the new version and ultimately stop using the previous version. As you adjust the request load on each version, the number of pods in each service might have to be scaled as well to provide the expected performance.

In addition to upgrading software, you can use this feature to experiment with versions of the user interface. Since some users get the old version and some the new, you can evaluate the user’s reaction to the different versions to inform design decisions.

For this to be effective, both the old and new versions must be similar enough that both can run at the same time. This is common with bug fix releases and when new features do not interfere with the old. The versions require N-1 compatibility to properly work together.

OpenShift Container Platform supports N-1 compatibility through the web console as well as the CLI.

#### 7.4.5.1. Load balancing for A/B testingCopy linkLink copied to clipboard!

The user sets up a route with multiple services. Each service handles a version of the application.

Each service is assigned aweightand the portion of requests to each service is theservice_weightdivided by thesum_of_weights. Theweightfor each service is distributed to the service’s endpoints so that the sum of the endpointweightsis the serviceweight.

The route can have up to four services. Theweightfor the service can be between0and256. When theweightis0, the service does not participate in load balancing but continues to serve existing persistent connections. When the serviceweightis not0, each endpoint has a minimumweightof1. Because of this, a service with a lot of endpoints can end up with higherweightthan intended. In this case, reduce the number of pods to get the expected load balanceweight.

Procedure

To set up the A/B environment:

- Create the two applications and give them different names. Each creates aDeploymentobject. The applications are versions of the same program; one is usually the current production version and the other the proposed new version.Create the first application. The following example creates an application calledab-example-a:oc new-app openshift/deployment-example --name=ab-example-a$oc new-app openshift/deployment-example--name=ab-example-aCopy to ClipboardCopied!Toggle word wrapToggle overflowCreate the second application:oc new-app openshift/deployment-example:v2 --name=ab-example-b$oc new-app openshift/deployment-example:v2--name=ab-example-bCopy to ClipboardCopied!Toggle word wrapToggle overflowBoth applications are deployed and services are created.

Create the two applications and give them different names. Each creates aDeploymentobject. The applications are versions of the same program; one is usually the current production version and the other the proposed new version.

- Create the first application. The following example creates an application calledab-example-a:oc new-app openshift/deployment-example --name=ab-example-a$oc new-app openshift/deployment-example--name=ab-example-aCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the first application. The following example creates an application calledab-example-a:

- Create the second application:oc new-app openshift/deployment-example:v2 --name=ab-example-b$oc new-app openshift/deployment-example:v2--name=ab-example-bCopy to ClipboardCopied!Toggle word wrapToggle overflowBoth applications are deployed and services are created.

Create the second application:

Both applications are deployed and services are created.

- Make the application available externally via a route. At this point, you can expose either. It can be convenient to expose the current production version first and later modify the route to add the new version.oc expose svc/ab-example-a$oc expose svc/ab-example-aCopy to ClipboardCopied!Toggle word wrapToggle overflowBrowse to the application atab-example-a.<project>.<router_domain>to verify that you see the expected version.

Make the application available externally via a route. At this point, you can expose either. It can be convenient to expose the current production version first and later modify the route to add the new version.

Browse to the application atab-example-a.<project>.<router_domain>to verify that you see the expected version.

- When you deploy the route, the router balances the traffic according to theweightsspecified for the services. At this point, there is a single service with defaultweight=1so all requests go to it. Adding the other service as analternateBackendsand adjusting theweightsbrings the A/B setup to life. This can be done by theoc set route-backendscommand or by editing the route.When usingalternateBackends, also use theroundrobinload balancing strategy to ensure requests are distributed as expected to the services based on weight.roundrobincan be set for a route by using a route annotation. See theAdditional resourcessection for more information about route annotations.Setting theoc set route-backendto0means the service does not participate in load balancing, but continues to serve existing persistent connections.Changes to the route just change the portion of traffic to the various services. You might have to scale the deployment to adjust the number of pods to handle the anticipated loads.To edit the route, run:oc edit route <route_name>$oc edit route<route_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-alternate-service
  annotations:
    haproxy.router.openshift.io/balance: roundrobin
# ...
spec:
  host: ab-example.my-project.my-domain
  to:
    kind: Service
    name: ab-example-a
    weight: 10
  alternateBackends:
  - kind: Service
    name: ab-example-b
    weight: 15
# ...apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-alternate-service
  annotations:
    haproxy.router.openshift.io/balance: roundrobin#...spec:
  host: ab-example.my-project.my-domain
  to:
    kind: Service
    name: ab-example-a
    weight: 10
  alternateBackends:
  - kind: Service
    name: ab-example-b
    weight: 15#...Copy to ClipboardCopied!Toggle word wrapToggle overflow

When you deploy the route, the router balances the traffic according to theweightsspecified for the services. At this point, there is a single service with defaultweight=1so all requests go to it. Adding the other service as analternateBackendsand adjusting theweightsbrings the A/B setup to life. This can be done by theoc set route-backendscommand or by editing the route.

When usingalternateBackends, also use theroundrobinload balancing strategy to ensure requests are distributed as expected to the services based on weight.roundrobincan be set for a route by using a route annotation. See theAdditional resourcessection for more information about route annotations.

Setting theoc set route-backendto0means the service does not participate in load balancing, but continues to serve existing persistent connections.

Changes to the route just change the portion of traffic to the various services. You might have to scale the deployment to adjust the number of pods to handle the anticipated loads.

To edit the route, run:

Example output

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-alternate-service
  annotations:
    haproxy.router.openshift.io/balance: roundrobin
# ...
spec:
  host: ab-example.my-project.my-domain
  to:
    kind: Service
    name: ab-example-a
    weight: 10
  alternateBackends:
  - kind: Service
    name: ab-example-b
    weight: 15
# ...
```

```
apiVersion: route.openshift.io/v1
kind: Route
metadata:
  name: route-alternate-service
  annotations:
    haproxy.router.openshift.io/balance: roundrobin
# ...
spec:
  host: ab-example.my-project.my-domain
  to:
    kind: Service
    name: ab-example-a
    weight: 10
  alternateBackends:
  - kind: Service
    name: ab-example-b
    weight: 15
# ...
```

##### 7.4.5.1.1. Managing weights of an existing route using the web consoleCopy linkLink copied to clipboard!

Procedure

- Navigate to theNetworkingRoutespage.
- Click the Options menunext to the route you want to edit and selectEdit Route.
- Edit the YAML file. Update theweightto be an integer between0and256that specifies the relative weight of the target against other target reference objects. The value0suppresses requests to this back end. The default is100. Runoc explain routes.spec.alternateBackendsfor more information about the options.
- ClickSave.

##### 7.4.5.1.2. Managing weights of an new route using the web consoleCopy linkLink copied to clipboard!

- Navigate to theNetworkingRoutespage.
- ClickCreate Route.
- Enter the routeName.
- Select theService.
- ClickAdd Alternate Service.
- Enter a value forWeightandAlternate Service Weight. Enter a number between0and255that depicts relative weight compared with other targets. The default is100.
- Select theTarget Port.
- ClickCreate.

##### 7.4.5.1.3. Managing weights using the CLICopy linkLink copied to clipboard!

Procedure

- To manage the services and corresponding weights load balanced by the route, use theoc set route-backendscommand:oc set route-backends ROUTENAME \
    [--zero|--equal] [--adjust] SERVICE=WEIGHT[%] [...] [options]$ocsetroute-backends ROUTENAME\[--zero|--equal][--adjust]SERVICE=WEIGHT[%][...][options]Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, the following setsab-example-aas the primary service withweight=198andab-example-bas the first alternate service with aweight=2:oc set route-backends ab-example ab-example-a=198 ab-example-b=2$ocsetroute-backends ab-example ab-example-a=198ab-example-b=2Copy to ClipboardCopied!Toggle word wrapToggle overflowThis means 99% of traffic is sent to serviceab-example-aand 1% to serviceab-example-b.This command does not scale the deployment. You might be required to do so to have enough pods to handle the request load.

To manage the services and corresponding weights load balanced by the route, use theoc set route-backendscommand:

```
oc set route-backends ROUTENAME \
    [--zero|--equal] [--adjust] SERVICE=WEIGHT[%] [...] [options]
```

```
$ oc set route-backends ROUTENAME \
    [--zero|--equal] [--adjust] SERVICE=WEIGHT[%] [...] [options]
```

For example, the following setsab-example-aas the primary service withweight=198andab-example-bas the first alternate service with aweight=2:

This means 99% of traffic is sent to serviceab-example-aand 1% to serviceab-example-b.

This command does not scale the deployment. You might be required to do so to have enough pods to handle the request load.

- Run the command with no flags to verify the current configuration:oc set route-backends ab-example$ocsetroute-backends ab-exampleCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                    KIND     TO           WEIGHT
routes/ab-example       Service  ab-example-a 198 (99%)
routes/ab-example       Service  ab-example-b 2   (1%)NAME                    KIND     TO           WEIGHT
routes/ab-example       Service  ab-example-a 198 (99%)
routes/ab-example       Service  ab-example-b 2   (1%)Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run the command with no flags to verify the current configuration:

Example output

```
NAME                    KIND     TO           WEIGHT
routes/ab-example       Service  ab-example-a 198 (99%)
routes/ab-example       Service  ab-example-b 2   (1%)
```

```
NAME                    KIND     TO           WEIGHT
routes/ab-example       Service  ab-example-a 198 (99%)
routes/ab-example       Service  ab-example-b 2   (1%)
```

- To override the default values for the load balancing algorithm, adjust the annotation on the route by setting the algorithm toroundrobin. For a route on OpenShift Container Platform, the default load balancing algorithm is set torandomorsourcevalues.To set the algorithm toroundrobin, run the command:oc annotate routes/<route-name> haproxy.router.openshift.io/balance=roundrobin$oc annotate routes/<route-name>haproxy.router.openshift.io/balance=roundrobinCopy to ClipboardCopied!Toggle word wrapToggle overflowFor Transport Layer Security (TLS) passthrough routes, the default value issource. For all other routes, the default israndom.

To override the default values for the load balancing algorithm, adjust the annotation on the route by setting the algorithm toroundrobin. For a route on OpenShift Container Platform, the default load balancing algorithm is set torandomorsourcevalues.

To set the algorithm toroundrobin, run the command:

For Transport Layer Security (TLS) passthrough routes, the default value issource. For all other routes, the default israndom.

- To alter the weight of an individual service relative to itself or to the primary service, use the--adjustflag. Specifying a percentage adjusts the service relative to either the primary or the first alternate (if you specify the primary). If there are other backends, their weights are kept proportional to the changed.The following example alters the weight ofab-example-aandab-example-bservices:oc set route-backends ab-example --adjust ab-example-a=200 ab-example-b=10$ocsetroute-backends ab-example--adjustab-example-a=200ab-example-b=10Copy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, alter the weight of a service by specifying a percentage:oc set route-backends ab-example --adjust ab-example-b=5%$ocsetroute-backends ab-example--adjustab-example-b=5%Copy to ClipboardCopied!Toggle word wrapToggle overflowBy specifying+before the percentage declaration, you can adjust a weighting relative to the current setting. For example:oc set route-backends ab-example --adjust ab-example-b=+15%$ocsetroute-backends ab-example--adjustab-example-b=+15%Copy to ClipboardCopied!Toggle word wrapToggle overflowThe--equalflag sets theweightof all services to100:oc set route-backends ab-example --equal$ocsetroute-backends ab-example--equalCopy to ClipboardCopied!Toggle word wrapToggle overflowThe--zeroflag sets theweightof all services to0. All requests then return with a 503 error.Not all routers may support multiple or weighted backends.

To alter the weight of an individual service relative to itself or to the primary service, use the--adjustflag. Specifying a percentage adjusts the service relative to either the primary or the first alternate (if you specify the primary). If there are other backends, their weights are kept proportional to the changed.

The following example alters the weight ofab-example-aandab-example-bservices:

Alternatively, alter the weight of a service by specifying a percentage:

By specifying+before the percentage declaration, you can adjust a weighting relative to the current setting. For example:

The--equalflag sets theweightof all services to100:

The--zeroflag sets theweightof all services to0. All requests then return with a 503 error.

Not all routers may support multiple or weighted backends.

##### 7.4.5.1.4. One service, multiple Deployment objectsCopy linkLink copied to clipboard!

Procedure

- Create a new application, adding a labelab-example=truethat will be common to all shards:oc new-app openshift/deployment-example --name=ab-example-a --as-deployment-config=true --labels=ab-example=true --env=SUBTITLE\=shardA$oc new-app openshift/deployment-example--name=ab-example-a --as-deployment-config=true--labels=ab-example=true--env=SUBTITLE\=shardACopy to ClipboardCopied!Toggle word wrapToggle overflowoc delete svc/ab-example-a$oc delete svc/ab-example-aCopy to ClipboardCopied!Toggle word wrapToggle overflowThe application is deployed and a service is created. This is the first shard.

Create a new application, adding a labelab-example=truethat will be common to all shards:

The application is deployed and a service is created. This is the first shard.

- Make the application available via a route, or use the service IP directly:oc expose deployment ab-example-a --name=ab-example --selector=ab-example\=true$oc expose deployment ab-example-a--name=ab-example--selector=ab-example\=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowoc expose service ab-example$oc exposeserviceab-exampleCopy to ClipboardCopied!Toggle word wrapToggle overflow

Make the application available via a route, or use the service IP directly:

- Browse to the application atab-example-<project_name>.<router_domain>to verify you see thev1image.
- Create a second shard based on the same source image and label as the first shard, but with a different tagged version and unique environment variables:oc new-app openshift/deployment-example:v2 \
    --name=ab-example-b --labels=ab-example=true \
    SUBTITLE="shard B" COLOR="red" --as-deployment-config=true$oc new-app openshift/deployment-example:v2\--name=ab-example-b--labels=ab-example=true\SUBTITLE="shard B"COLOR="red"--as-deployment-config=trueCopy to ClipboardCopied!Toggle word wrapToggle overflowoc delete svc/ab-example-b$oc delete svc/ab-example-bCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a second shard based on the same source image and label as the first shard, but with a different tagged version and unique environment variables:

```
oc new-app openshift/deployment-example:v2 \
    --name=ab-example-b --labels=ab-example=true \
    SUBTITLE="shard B" COLOR="red" --as-deployment-config=true
```

```
$ oc new-app openshift/deployment-example:v2 \
    --name=ab-example-b --labels=ab-example=true \
    SUBTITLE="shard B" COLOR="red" --as-deployment-config=true
```

- At this point, both sets of pods are being served under the route. However, because both browsers (by leaving a connection open) and the router (by default, through a cookie) attempt to preserve your connection to a back-end server, you might not see both shards being returned to you.To force your browser to one or the other shard:Use theoc scalecommand to reduce replicas ofab-example-ato0.oc scale dc/ab-example-a --replicas=0$oc scale dc/ab-example-a--replicas=0Copy to ClipboardCopied!Toggle word wrapToggle overflowRefresh your browser to showv2andshard B(in red).Scaleab-example-ato1replica andab-example-bto0:oc scale dc/ab-example-a --replicas=1; oc scale dc/ab-example-b --replicas=0$oc scale dc/ab-example-a--replicas=1;oc scale dc/ab-example-b--replicas=0Copy to ClipboardCopied!Toggle word wrapToggle overflowRefresh your browser to showv1andshard A(in blue).

At this point, both sets of pods are being served under the route. However, because both browsers (by leaving a connection open) and the router (by default, through a cookie) attempt to preserve your connection to a back-end server, you might not see both shards being returned to you.

To force your browser to one or the other shard:

- Use theoc scalecommand to reduce replicas ofab-example-ato0.oc scale dc/ab-example-a --replicas=0$oc scale dc/ab-example-a--replicas=0Copy to ClipboardCopied!Toggle word wrapToggle overflowRefresh your browser to showv2andshard B(in red).

Use theoc scalecommand to reduce replicas ofab-example-ato0.

Refresh your browser to showv2andshard B(in red).

- Scaleab-example-ato1replica andab-example-bto0:oc scale dc/ab-example-a --replicas=1; oc scale dc/ab-example-b --replicas=0$oc scale dc/ab-example-a--replicas=1;oc scale dc/ab-example-b--replicas=0Copy to ClipboardCopied!Toggle word wrapToggle overflowRefresh your browser to showv1andshard A(in blue).

Scaleab-example-ato1replica andab-example-bto0:

Refresh your browser to showv1andshard A(in blue).

- If you trigger a deployment on either shard, only the pods in that shard are affected. You can trigger a deployment by changing theSUBTITLEenvironment variable in eitherDeploymentobject:oc edit dc/ab-example-a$oc edit dc/ab-example-aCopy to ClipboardCopied!Toggle word wrapToggle overfloworoc edit dc/ab-example-b$oc edit dc/ab-example-bCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you trigger a deployment on either shard, only the pods in that shard are affected. You can trigger a deployment by changing theSUBTITLEenvironment variable in eitherDeploymentobject:

or
