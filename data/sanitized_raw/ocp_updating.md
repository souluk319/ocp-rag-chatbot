<!-- source: ocp_updating.md -->

# Updating

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/updating_clusters/understanding-openshift-updates-1
---

# Chapter 1. Understanding OpenShift updates

## 1.1. Introduction to OpenShift updatesCopy linkLink copied to clipboard!

With OpenShift Container Platform 4, you can update an OpenShift Container Platform cluster with a single operation by using the web console or the OpenShift CLI (oc).

Platform administrators can view new update options either by going toAdministrationCluster Settingsin the web console or by looking at the output of theoc adm upgradecommand.

### 1.1.1. Cluster update overviewCopy linkLink copied to clipboard!

OpenShift Container Platform updates involve several services, Operators, and processes working in tandem to change the cluster to the desired version.

Red Hat hosts a public OpenShift Update Service (OSUS), which serves a graph of update possibilities based on the OpenShift Container Platform release images in the official registry. The graph contains update information for any public release. OpenShift Container Platform clusters are configured to connect to the OSUS by default, and the OSUS responds to clusters with information about known update targets.

An update begins when either a cluster administrator or an automatic update controller edits the custom resource (CR) of the Cluster Version Operator (CVO) with a new version. To reconcile the cluster with the newly specified version, the CVO retrieves the target release image from an image registry and begins to apply changes to the cluster.

Operators previously installed through Operator Lifecycle Manager (OLM) follow a different process for updates. SeeUpdating installed Operatorsfor more information.

The target release image contains manifest files for all cluster components that form a specific OCP version. When updating the cluster to a new version, the CVO applies manifests in separate stages called Runlevels. Most, but not all, manifests support one of the cluster Operators. As the CVO applies a manifest to a cluster Operator, the Operator might perform update tasks to reconcile itself with its new specified version.

The CVO monitors the state of each applied resource and the states reported by all cluster Operators. The CVO only proceeds with the update when all manifests and cluster Operators in the active Runlevel reach a stable condition. After the CVO updates the entire control plane through this process, the Machine Config Operator (MCO) updates the operating system and configuration of every node in the cluster.

### 1.1.2. Common questions about update availabilityCopy linkLink copied to clipboard!

There are several factors that affect if and when an update is made available to an OpenShift Container Platform cluster.

The following list provides common questions regarding the availability of an update:

What are the differences between each of the update channels?

- A new release is initially added to thecandidatechannel.
- After successful final testing, a release on thecandidatechannel is promoted to thefastchannel, an errata is published, and the release is now fully supported.
- After a delay, a release on thefastchannel is finally promoted to thestablechannel. This delay represents the only difference between thefastandstablechannels.For the latest z-stream releases, this delay may generally be a week or two. However, the delay for initial updates to the latest minor version may take much longer, generally 45-90 days.

After a delay, a release on thefastchannel is finally promoted to thestablechannel. This delay represents the only difference between thefastandstablechannels.

For the latest z-stream releases, this delay may generally be a week or two. However, the delay for initial updates to the latest minor version may take much longer, generally 45-90 days.

- Releases promoted to thestablechannel are simultaneously promoted to theeuschannel. The primary purpose of theeuschannel is to serve as a convenience for clusters performing a Control Plane Only update.

Is a release on thestablechannel safer or more supported than a release on thefastchannel?

- If a regression is identified for a release on afastchannel, it will be resolved and managed to the same extent as if that regression was identified for a release on thestablechannel.
- The only difference between releases on thefastandstablechannels is that a release only appears on thestablechannel after it has been on thefastchannel for some time, which provides more time for new update risks to be discovered.
- A release that is available on thefastchannel always becomes available on thestablechannel after this delay.

What does it mean if an update has known issues?

- Red Hat continuously evaluates data from multiple sources to determine whether updates from one version to another have any declared issues. Identified issues are typically documented in the version’s release notes. Even if the update path has known issues, customers are still supported if they perform the update.
- Red Hat does not block users from updating to a certain version. Red Hat may declare conditional update risks, which may or may not apply to a particular cluster.Declared risks provide cluster administrators more context about a supported update. Cluster administrators can still accept the risk and update to that particular target version.

Red Hat does not block users from updating to a certain version. Red Hat may declare conditional update risks, which may or may not apply to a particular cluster.

- Declared risks provide cluster administrators more context about a supported update. Cluster administrators can still accept the risk and update to that particular target version.

What if I see that an update to a particular release is no longer recommended?

- If Red Hat removes update recommendations from any supported release due to a regression, a superseding update recommendation will be provided to a future version that corrects the regression. There may be a delay while the defect is corrected, tested, and promoted to your selected channel.

How long until the next z-stream release is made available on the fast and stable channels?

- While the specific cadence can vary based on a number of factors, new z-stream releases for the latest minor version are typically made available about every week. Older minor versions, which have become more stable over time, may take much longer for new z-stream releases to be made available.These are only estimates based on past data about z-stream releases. Red Hat reserves the right to change the release frequency as needed. Any number of issues could cause irregularities and delays in this release cadence.

While the specific cadence can vary based on a number of factors, new z-stream releases for the latest minor version are typically made available about every week. Older minor versions, which have become more stable over time, may take much longer for new z-stream releases to be made available.

These are only estimates based on past data about z-stream releases. Red Hat reserves the right to change the release frequency as needed. Any number of issues could cause irregularities and delays in this release cadence.

- Once a z-stream release is published, it also appears in thefastchannel for that minor version. After a delay, the z-stream release may then appear in that minor version’sstablechannel.

### 1.1.3. About the OpenShift Update ServiceCopy linkLink copied to clipboard!

The OpenShift Update Service (OSUS) provides update recommendations to OpenShift Container Platform, including Red Hat Enterprise Linux CoreOS (RHCOS). It provides a graph, or diagram, that contains theverticesof component Operators and theedgesthat connect them.

The edges in the graph show which versions you can safely update to. The vertices are update payloads that specify the intended state of the managed cluster components.

The Cluster Version Operator (CVO) in your cluster checks with the OpenShift Update Service to see the valid updates and update paths based on current component versions and information in the graph. When you request an update, the CVO uses the corresponding release image to update your cluster. The release artifacts are hosted in Quay as container images.

To allow the OpenShift Update Service to provide only compatible updates, a release verification pipeline drives automation. Each release artifact is verified for compatibility with supported cloud platforms and system architectures, as well as other component packages. After the pipeline confirms the suitability of a release, the OpenShift Update Service notifies you that it is available.

The OpenShift Update Service (OSUS) supports a single-stream release model, where only one release version is active and supported at any given time. When a new release is deployed, it fully replaces the previous release.

The updated release provides support for upgrades from all OpenShift Container Platform versions starting after 4.8 up to the new release version.

The OpenShift Update Service displays all recommended updates for your current cluster. If an update path is not recommended by the OpenShift Update Service, it might be because of a known issue related to the update path, such as incompatibility or availability.

Two controllers run during continuous update mode. The first controller continuously updates the payload manifests, applies the manifests to the cluster, and outputs the controlled rollout status of the Operators to indicate whether they are available, upgrading, or failed. The second controller polls the OpenShift Update Service to determine if updates are available.

Only updating to a newer version is supported. Reverting or rolling back your cluster to a previous version is not supported. If your update fails, contact Red Hat support.

During the update process, the Machine Config Operator (MCO) applies the new configuration to your cluster machines. The MCO cordons the number of nodes specified by themaxUnavailablefield on the machine configuration pool and marks them unavailable. By default, this value is set to1. The MCO updates the affected nodes alphabetically by zone, based on thetopology.kubernetes.io/zonelabel. If a zone has more than one node, the oldest nodes are updated first. For nodes that do not use zones, such as in bare metal deployments, the nodes are updated by age, with the oldest nodes updated first. The MCO updates the number of nodes as specified by themaxUnavailablefield on the machine configuration pool at a time. The MCO then applies the new configuration and reboots the machine.

The default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

If you use Red Hat Enterprise Linux (RHEL) machines as workers, the MCO does not update the kubelet because you must update the OpenShift API on the machines first.

With the specification for the new version applied to the old kubelet, the RHEL machine cannot return to theReadystate. You cannot complete the update until the machines are available. However, the maximum number of unavailable nodes is set to ensure that normal cluster operations can continue with that number of machines out of service.

The OpenShift Update Service is composed of an Operator and one or more application instances.

### 1.1.4. Understanding cluster Operator condition typesCopy linkLink copied to clipboard!

The status of cluster Operators includes their condition type, which informs you of the current state of your Operator’s health.

The following definitions cover a list of some common ClusterOperator condition types. Operators that have additional condition types and use Operator-specific language have been omitted.

The Cluster Version Operator (CVO) is responsible for collecting the status conditions from cluster Operators so that cluster administrators can better understand the state of the OpenShift Container Platform cluster.

- Available: The condition typeAvailableindicates that an Operator is functional and available in the cluster. If the status isFalse, at least one part of the operand is non-functional and the condition requires an administrator to intervene.
- Progressing: The condition typeProgressingindicates that an Operator is actively rolling out new code, propagating configuration changes, or otherwise moving from one steady state to another.Operators do not report the condition typeProgressingasTruewhen they are reconciling a previous known state. If the observed cluster state has changed and the Operator is reacting to it, then the status reports back asTrue, since it is moving from one steady state to another.

Progressing: The condition typeProgressingindicates that an Operator is actively rolling out new code, propagating configuration changes, or otherwise moving from one steady state to another.

Operators do not report the condition typeProgressingasTruewhen they are reconciling a previous known state. If the observed cluster state has changed and the Operator is reacting to it, then the status reports back asTrue, since it is moving from one steady state to another.

- Degraded: The condition typeDegradedindicates that an Operator has a current state that does not match its required state over a period of time. The period of time can vary by component, but aDegradedstatus represents persistent observation of an Operator’s condition. As a result, an Operator does not fluctuate in and out of theDegradedstate.There might be a different condition type if the transition from one state to another does not persist over a long enough period to reportDegraded. An Operator does not reportDegradedduring the course of a normal update. An Operator may reportDegradedin response to a persistent infrastructure failure that requires eventual administrator intervention.This condition type is only an indication that something may need investigation and adjustment. As long as the Operator is available, theDegradedcondition does not cause user workload failure or application downtime.

Degraded: The condition typeDegradedindicates that an Operator has a current state that does not match its required state over a period of time. The period of time can vary by component, but aDegradedstatus represents persistent observation of an Operator’s condition. As a result, an Operator does not fluctuate in and out of theDegradedstate.

There might be a different condition type if the transition from one state to another does not persist over a long enough period to reportDegraded. An Operator does not reportDegradedduring the course of a normal update. An Operator may reportDegradedin response to a persistent infrastructure failure that requires eventual administrator intervention.

This condition type is only an indication that something may need investigation and adjustment. As long as the Operator is available, theDegradedcondition does not cause user workload failure or application downtime.

- Upgradeable: The condition typeUpgradeableindicates whether the Operator is safe to update based on the current cluster state. The message field contains a human-readable description of what the administrator needs to do for the cluster to successfully update. The CVO allows updates when this condition isTrue,Unknownor missing.When theUpgradeablestatus isFalse, only minor updates are impacted, and the CVO prevents the cluster from performing impacted updates unless forced.

Upgradeable: The condition typeUpgradeableindicates whether the Operator is safe to update based on the current cluster state. The message field contains a human-readable description of what the administrator needs to do for the cluster to successfully update. The CVO allows updates when this condition isTrue,Unknownor missing.

When theUpgradeablestatus isFalse, only minor updates are impacted, and the CVO prevents the cluster from performing impacted updates unless forced.

### 1.1.5. Understanding cluster version condition typesCopy linkLink copied to clipboard!

The Cluster Version Operator (CVO) monitors cluster Operators and other components, and is responsible for collecting the status of both the cluster version and its Operators. This status includes the condition type, which informs you of the health and current state of the OpenShift Container Platform cluster.

In addition toAvailable,Progressing, andUpgradeable, there are condition types that affect cluster versions and Operators.

- Failing: The cluster version condition typeFailingindicates that a cluster cannot reach its desired state, is unhealthy, and requires an administrator to intervene.
- Invalid: The cluster version condition typeInvalidindicates that the cluster version has an error that prevents the server from taking action. The CVO only reconciles the current state as long as this condition is set.
- RetrievedUpdates: The cluster version condition typeRetrievedUpdatesindicates whether or not available updates have been retrieved from the upstream update server. The condition isUnknownbefore retrieval,Falseif the updates either recently failed or could not be retrieved, orTrueif theavailableUpdatesfield is both recent and accurate.
- ReleaseAccepted: The cluster version condition typeReleaseAcceptedwith aTruestatus indicates that the requested release payload was successfully loaded without failure during image verification and precondition checking.
- ImplicitlyEnabledCapabilities: The cluster version condition typeImplicitlyEnabledCapabilitieswith aTruestatus indicates that there are enabled capabilities that the user is not currently requesting throughspec.capabilities. The CVO does not support disabling capabilities if any associated resources were previously managed by the CVO.

### 1.1.6. Common termsCopy linkLink copied to clipboard!

Some terms are commonly used in the context of OpenShift Container Platform updates, which might be useful to learn.

**Control plane**
  Thecontrol plane, which is composed of control plane machines, manages the OpenShift Container Platform cluster. The control plane machines manage workloads on the compute machines, which are also known as worker machines.

**Cluster Version Operator**
  TheCluster Version Operator(CVO) starts the update process for the cluster. It checks with OSUS based on the current cluster version and retrieves the graph which contains available or possible update paths.

**Machine Config Operator**
  TheMachine Config Operator(MCO) is a cluster-level Operator that manages the operating system and machine configurations. Through the MCO, platform administrators can configure and update systemd, CRI-O and Kubelet, the kernel, NetworkManager, and other system features on the worker nodes.

**OpenShift Update Service**
  TheOpenShift Update Service(OSUS) provides over-the-air updates to OpenShift Container Platform, including to Red Hat Enterprise Linux CoreOS (RHCOS). It provides a graph, or diagram, that contains the vertices of component Operators and the edges that connect them.

**Channels**
  Channelsdeclare an update strategy tied to minor versions of OpenShift Container Platform. The OSUS uses this configured strategy to recommend update edges consistent with that strategy.

**Recommended update edge**
  Arecommended update edgeis a recommended update between OpenShift Container Platform releases. Whether a given update is recommended can depend on the cluster’s configured channel, current version, known bugs, and other information. OSUS communicates the recommended edges to the CVO, which runs in every cluster.

## 1.2. How cluster updates workCopy linkLink copied to clipboard!

The Cluster Version Operator (CVO) is the primary component that orchestrates the OpenShift Container Platform update process. During standard cluster operation, the CVO compares manifests of cluster Operators to in-cluster resources and reconciles discrepancies between the actual state of these resources and their desired state.

The following sections describe each major aspect of the OpenShift Container Platform (OCP) update process in detail. For a general overview of how updates work, see theIntroduction to OpenShift updates.

### 1.2.1. The ClusterVersion objectCopy linkLink copied to clipboard!

One of the resources that the Cluster Version Operator (CVO) monitors is theClusterVersionresource.

Administrators and OpenShift Container Platform components can communicate or interact with the CVO through theClusterVersionobject. The desired CVO state is declared through theClusterVersionobject and the current CVO state is reflected in the object’s status.

Do not directly modify theClusterVersionobject. Instead, use interfaces such as theocCLI or the web console to declare your update target.

The CVO continually reconciles the cluster with the target state declared in thespecproperty of theClusterVersionresource. When the desired release differs from the actual release, that reconciliation updates the cluster.

#### 1.2.1.1. Update availability dataCopy linkLink copied to clipboard!

TheClusterVersionresource also contains information about updates that are available to the cluster. This includes updates that are available, but not recommended due to a known risk that applies to the cluster. These updates are known as conditional updates. To learn how the CVO maintains this information about available updates in theClusterVersionresource, see the "Evaluation of update availability" section.

You can inspect all available updates with the following command:

The additional--include-not-recommendedparameter includes updates that are available with known issues that apply to the cluster.

Example output

```
Cluster version is 4.13.40

Upstream is unset, so the cluster will use an appropriate default.
Channel: stable-4.14 (available channels: candidate-4.13, candidate-4.14, eus-4.14, fast-4.13, fast-4.14, stable-4.13, stable-4.14)

Recommended updates:

  VERSION     IMAGE
  4.14.27     quay.io/openshift-release-dev/ocp-release@sha256:4d30b359aa6600a89ed49ce6a9a5fdab54092bcb821a25480fdfbc47e66af9ec
  4.14.26     quay.io/openshift-release-dev/ocp-release@sha256:4fe7d4ccf4d967a309f83118f1a380a656a733d7fcee1dbaf4d51752a6372890
  4.14.25     quay.io/openshift-release-dev/ocp-release@sha256:a0ef946ef8ae75aef726af1d9bbaad278559ad8cab2c1ed1088928a0087990b6
  4.14.24     quay.io/openshift-release-dev/ocp-release@sha256:0a34eac4b834e67f1bca94493c237e307be2c0eae7b8956d4d8ef1c0c462c7b0
  4.14.23     quay.io/openshift-release-dev/ocp-release@sha256:f8465817382128ec7c0bc676174bad0fb43204c353e49c146ddd83a5b3d58d92
  4.13.42     quay.io/openshift-release-dev/ocp-release@sha256:dcf5c3ad7384f8bee3c275da8f886b0bc9aea7611d166d695d0cf0fff40a0b55
  4.13.41     quay.io/openshift-release-dev/ocp-release@sha256:dbb8aa0cf53dc5ac663514e259ad2768d8c82fd1fe7181a4cfb484e3ffdbd3ba

Updates with known issues:

  Version: 4.14.22
  Image: quay.io/openshift-release-dev/ocp-release@sha256:7093fa606debe63820671cc92a1384e14d0b70058d4b4719d666571e1fc62190
  Reason: MultipleReasons
  Message: Exposure to AzureRegistryImageMigrationUserProvisioned is unknown due to an evaluation failure: client-side throttling: only 18.061µs has elapsed since the last match call completed for this cluster condition backend; this cached cluster condition request has been queued for later execution
  In Azure clusters with the user-provisioned registry storage, the in-cluster image registry component may struggle to complete the cluster update. https://issues.redhat.com/browse/IR-468

  Incoming HTTP requests to services exposed by Routes may fail while routers reload their configuration, especially when made with Apache HTTPClient versions before 5.0. The problem is more likely to occur in clusters with higher number of Routes and corresponding endpoints. https://issues.redhat.com/browse/NE-1689

  Version: 4.14.21
  Image: quay.io/openshift-release-dev/ocp-release@sha256:6e3fba19a1453e61f8846c6b0ad3abf41436a3550092cbfd364ad4ce194582b7
  Reason: MultipleReasons
  Message: Exposure to AzureRegistryImageMigrationUserProvisioned is unknown due to an evaluation failure: client-side throttling: only 33.991µs has elapsed since the last match call completed for this cluster condition backend; this cached cluster condition request has been queued for later execution
  In Azure clusters with the user-provisioned registry storage, the in-cluster image registry component may struggle to complete the cluster update. https://issues.redhat.com/browse/IR-468

  Incoming HTTP requests to services exposed by Routes may fail while routers reload their configuration, especially when made with Apache HTTPClient versions before 5.0. The problem is more likely to occur in clusters with higher number of Routes and corresponding endpoints. https://issues.redhat.com/browse/NE-1689
```

```
Cluster version is 4.13.40

Upstream is unset, so the cluster will use an appropriate default.
Channel: stable-4.14 (available channels: candidate-4.13, candidate-4.14, eus-4.14, fast-4.13, fast-4.14, stable-4.13, stable-4.14)

Recommended updates:

  VERSION     IMAGE
  4.14.27     quay.io/openshift-release-dev/ocp-release@sha256:4d30b359aa6600a89ed49ce6a9a5fdab54092bcb821a25480fdfbc47e66af9ec
  4.14.26     quay.io/openshift-release-dev/ocp-release@sha256:4fe7d4ccf4d967a309f83118f1a380a656a733d7fcee1dbaf4d51752a6372890
  4.14.25     quay.io/openshift-release-dev/ocp-release@sha256:a0ef946ef8ae75aef726af1d9bbaad278559ad8cab2c1ed1088928a0087990b6
  4.14.24     quay.io/openshift-release-dev/ocp-release@sha256:0a34eac4b834e67f1bca94493c237e307be2c0eae7b8956d4d8ef1c0c462c7b0
  4.14.23     quay.io/openshift-release-dev/ocp-release@sha256:f8465817382128ec7c0bc676174bad0fb43204c353e49c146ddd83a5b3d58d92
  4.13.42     quay.io/openshift-release-dev/ocp-release@sha256:dcf5c3ad7384f8bee3c275da8f886b0bc9aea7611d166d695d0cf0fff40a0b55
  4.13.41     quay.io/openshift-release-dev/ocp-release@sha256:dbb8aa0cf53dc5ac663514e259ad2768d8c82fd1fe7181a4cfb484e3ffdbd3ba

Updates with known issues:

  Version: 4.14.22
  Image: quay.io/openshift-release-dev/ocp-release@sha256:7093fa606debe63820671cc92a1384e14d0b70058d4b4719d666571e1fc62190
  Reason: MultipleReasons
  Message: Exposure to AzureRegistryImageMigrationUserProvisioned is unknown due to an evaluation failure: client-side throttling: only 18.061µs has elapsed since the last match call completed for this cluster condition backend; this cached cluster condition request has been queued for later execution
  In Azure clusters with the user-provisioned registry storage, the in-cluster image registry component may struggle to complete the cluster update. https://issues.redhat.com/browse/IR-468

  Incoming HTTP requests to services exposed by Routes may fail while routers reload their configuration, especially when made with Apache HTTPClient versions before 5.0. The problem is more likely to occur in clusters with higher number of Routes and corresponding endpoints. https://issues.redhat.com/browse/NE-1689

  Version: 4.14.21
  Image: quay.io/openshift-release-dev/ocp-release@sha256:6e3fba19a1453e61f8846c6b0ad3abf41436a3550092cbfd364ad4ce194582b7
  Reason: MultipleReasons
  Message: Exposure to AzureRegistryImageMigrationUserProvisioned is unknown due to an evaluation failure: client-side throttling: only 33.991µs has elapsed since the last match call completed for this cluster condition backend; this cached cluster condition request has been queued for later execution
  In Azure clusters with the user-provisioned registry storage, the in-cluster image registry component may struggle to complete the cluster update. https://issues.redhat.com/browse/IR-468

  Incoming HTTP requests to services exposed by Routes may fail while routers reload their configuration, especially when made with Apache HTTPClient versions before 5.0. The problem is more likely to occur in clusters with higher number of Routes and corresponding endpoints. https://issues.redhat.com/browse/NE-1689
```

Theoc adm upgradecommand queries theClusterVersionresource for information about available updates and presents it in a human-readable format.

One way to directly inspect the underlying availability data created by the CVO is by querying theClusterVersionresource with the following command:

Example output

```
[
  {
    "channels": [
      "candidate-4.11",
      "candidate-4.12",
      "fast-4.11",
      "fast-4.12"
    ],
    "image": "quay.io/openshift-release-dev/ocp-release@sha256:400267c7f4e61c6bfa0a59571467e8bd85c9188e442cbd820cc8263809be3775",
    "url": "https://access.redhat.com/errata/RHBA-2023:3213",
    "version": "4.11.41"
  },
  ...
]
```

```
[
  {
    "channels": [
      "candidate-4.11",
      "candidate-4.12",
      "fast-4.11",
      "fast-4.12"
    ],
    "image": "quay.io/openshift-release-dev/ocp-release@sha256:400267c7f4e61c6bfa0a59571467e8bd85c9188e442cbd820cc8263809be3775",
    "url": "https://access.redhat.com/errata/RHBA-2023:3213",
    "version": "4.11.41"
  },
  ...
]
```

A similar command can be used to check conditional updates:

Example output

```
[
  {
    "conditions": [
      {
        "lastTransitionTime": "2023-05-30T16:28:59Z",
        "message": "The 4.11.36 release only resolves an installation issue https://issues.redhat.com//browse/OCPBUGS-11663 , which does not affect already running clusters. 4.11.36 does not include fixes delivered in recent 4.11.z releases and therefore upgrading from these versions would cause fixed bugs to reappear. Red Hat does not recommend upgrading clusters to 4.11.36 version for this reason. https://access.redhat.com/solutions/7007136",
        "reason": "PatchesOlderRelease",
        "status": "False",
        "type": "Recommended"
      }
    ],
    "release": {
      "channels": [...],
      "image": "quay.io/openshift-release-dev/ocp-release@sha256:8c04176b771a62abd801fcda3e952633566c8b5ff177b93592e8e8d2d1f8471d",
      "url": "https://access.redhat.com/errata/RHBA-2023:1733",
      "version": "4.11.36"
    },
    "risks": [...]
  },
  ...
]
```

```
[
  {
    "conditions": [
      {
        "lastTransitionTime": "2023-05-30T16:28:59Z",
        "message": "The 4.11.36 release only resolves an installation issue https://issues.redhat.com//browse/OCPBUGS-11663 , which does not affect already running clusters. 4.11.36 does not include fixes delivered in recent 4.11.z releases and therefore upgrading from these versions would cause fixed bugs to reappear. Red Hat does not recommend upgrading clusters to 4.11.36 version for this reason. https://access.redhat.com/solutions/7007136",
        "reason": "PatchesOlderRelease",
        "status": "False",
        "type": "Recommended"
      }
    ],
    "release": {
      "channels": [...],
      "image": "quay.io/openshift-release-dev/ocp-release@sha256:8c04176b771a62abd801fcda3e952633566c8b5ff177b93592e8e8d2d1f8471d",
      "url": "https://access.redhat.com/errata/RHBA-2023:1733",
      "version": "4.11.36"
    },
    "risks": [...]
  },
  ...
]
```

### 1.2.2. Evaluation of update availabilityCopy linkLink copied to clipboard!

The Cluster Version Operator (CVO) periodically queries the OpenShift Update Service (OSUS) for the most recent data about update possibilities.

This data is based on the cluster’s subscribed channel. The CVO then saves information about update recommendations into either theavailableUpdatesorconditionalUpdatesfield of itsClusterVersionresource.

The CVO periodically checks the conditional updates for update risks. These risks are conveyed through the data served by the OSUS, which contains information for each version about known issues that might affect a cluster updated to that version. Most risks are limited to clusters with specific characteristics, such as clusters with a certain size or clusters that are deployed in a particular cloud platform.

The CVO continuously evaluates its cluster characteristics against the conditional risk information for each conditional update. If the CVO finds that the cluster matches the criteria, the CVO stores this information in theconditionalUpdatesfield of itsClusterVersionresource. If the CVO finds that the cluster does not match the risks of an update, or that there are no risks associated with the update, it stores the target version in theavailableUpdatesfield of itsClusterVersionresource.

The user interface, either the web console or the OpenShift CLI (oc), presents this information in sectioned headings to the administrator. Each known issue associated with the update path contains a link to further resources about the risk so that the administrator can make an informed decision about the update.

### 1.2.3. Release imagesCopy linkLink copied to clipboard!

A release image is the delivery mechanism for a specific OpenShift Container Platform (OCP) version.

It contains the release metadata, a Cluster Version Operator (CVO) binary matching the release version, every manifest needed to deploy individual cluster Operators, and a list of SHA digest-versioned references to all container images that make up this version.

You can extract a specific release image by running the following command:

Example command

Example output

After the release image is extracted, you can inspect its contents by running the following command:

Example output

```
0000_03_authorization-openshift_01_rolebindingrestriction.crd.yaml
0000_03_config-operator_01_proxy.crd.yaml
0000_03_marketplace-operator_01_operatorhub.crd.yaml
0000_03_marketplace-operator_02_operatorhub.cr.yaml
0000_03_quota-openshift_01_clusterresourcequota.crd.yaml
...
0000_90_service-ca-operator_02_prometheusrolebinding.yaml
0000_90_service-ca-operator_03_servicemonitor.yaml
0000_99_machine-api-operator_00_tombstones.yaml
image-references
release-metadata
```

```
0000_03_authorization-openshift_01_rolebindingrestriction.crd.yaml
0000_03_config-operator_01_proxy.crd.yaml
0000_03_marketplace-operator_01_operatorhub.crd.yaml
0000_03_marketplace-operator_02_operatorhub.cr.yaml
0000_03_quota-openshift_01_clusterresourcequota.crd.yaml
...
0000_90_service-ca-operator_02_prometheusrolebinding.yaml
0000_90_service-ca-operator_03_servicemonitor.yaml
0000_99_machine-api-operator_00_tombstones.yaml
image-references
release-metadata
```

In this example output, the following contents can be seen:

- 0000_03_quota-openshift_01_clusterresourcequota.crd.yamlis the manifest for theClusterResourceQuotaCRD, to be applied on Runlevel 03.
- 0000_90_service-ca-operator_02_prometheusrolebinding.yamlis the manifest for thePrometheusRoleBindingresource for theservice-ca-operator, to be applied on Runlevel 90.
- image-referencesis the list of SHA digest-versioned references to all required images.

### 1.2.4. Update process workflowCopy linkLink copied to clipboard!

When you initiate a cluster update, the Cluster Version Operator (CVO) begins a specific sequence of events to orchestrate the update.

The following steps represent a detailed workflow of the OpenShift Container Platform update process:

- The target version is stored in thespec.desiredUpdate.versionfield of theClusterVersionresource, which may be managed through the web console or the CLI.
- The CVO detects that thedesiredUpdatefield in theClusterVersionresource differs from the current cluster version. Using graph data from the OpenShift Update Service, the CVO resolves the desired cluster version to a pull spec for the release image.
- The CVO validates the integrity and authenticity of the release image. Red Hat publishes cryptographically-signed statements about published release images at predefined locations by using image SHA digests as unique and immutable release image identifiers. The CVO utilizes a list of built-in public keys to validate the presence and signatures of the statement matching the checked release image.
- The CVO creates a job namedversion-$version-$hashin theopenshift-cluster-versionnamespace. This job uses containers that are executing the release image, so the cluster downloads the image through the container runtime. The job then extracts the manifests and metadata from the release image to a shared volume that is accessible to the CVO.
- The CVO validates the extracted manifests and metadata.
- The CVO checks some preconditions to ensure that no problematic condition is detected in the cluster. Certain conditions can prevent updates from proceeding. These conditions are either determined by the CVO itself, or reported by individual cluster Operators that detect some details about the cluster that the Operator considers problematic for the update.
- The CVO records the accepted release instatus.desiredand creates astatus.historyentry about the new update.
- The CVO begins reconciling the manifests from the release image. Cluster Operators are updated in separate stages called Runlevels, and the CVO ensures that all Operators in a Runlevel finish updating before it proceeds to the next level.
- Manifests for the CVO itself are applied early in the process. When the CVO deployment is applied, the current CVO pod stops, and a CVO pod that uses the new version starts. The new CVO proceeds to reconcile the remaining manifests.
- The update proceeds until the entire control plane is updated to the new version. Individual cluster Operators might perform update tasks on their domain of the cluster, and while they do so, they report their state through theProgressing=Truecondition.
- The Machine Config Operator (MCO) manifests are applied towards the end of the process. The updated MCO then begins updating the system configuration and operating system of every node. Each node might be drained, updated, and rebooted before it starts to accept workloads again.

The cluster reports as updated after the control plane update is finished, usually before all nodes are updated. After the update, the CVO maintains all cluster resources to match the state delivered in the release image.

### 1.2.5. Understanding how manifests are applied during an updateCopy linkLink copied to clipboard!

Some manifests supplied in a release image must be applied in a certain order because of the dependencies between them.

For example, theCustomResourceDefinitionresource must be created before the matching custom resources. Additionally, there is a logical order in which the individual cluster Operators must be updated to minimize disruption in the cluster. The Cluster Version Operator (CVO) implements this logical order through the concept of Runlevels.

These dependencies are encoded in the filenames of the manifests in the release image:

For example:

The CVO internally builds a dependency graph for the manifests, where the CVO obeys the following rules:

- During an update, manifests at a lower Runlevel are applied before those at a higher Runlevel.
- Within one Runlevel, manifests for different components can be applied in parallel.
- Within one Runlevel, manifests for a single component are applied in lexicographic order.

The CVO then applies manifests following the generated dependency graph.

For some resource types, the CVO monitors the resource after its manifest is applied, and considers it to be successfully updated only after the resource reaches a stable state. Achieving this state can take some time. This is especially true forClusterOperatorresources, while the CVO waits for a cluster Operator to update itself and then update itsClusterOperatorstatus.

The CVO waits until all cluster Operators in the Runlevel meet the following conditions before it proceeds to the next Runlevel:

- The cluster Operators have anAvailable=Truecondition.
- The cluster Operators have aDegraded=Falsecondition.
- The cluster Operators declare they have achieved the desired version in their ClusterOperator resource.

Some actions can take significant time to finish. The CVO waits for the actions to complete in order to ensure the subsequent Runlevels can proceed safely. Initially reconciling the new release’s manifests is expected to take 60 to 120 minutes in total; seeUnderstanding OpenShift Container Platform update durationfor more information about factors that influence update duration.

In the previous example diagram, the CVO is waiting until all work is completed at Runlevel 20. The CVO has applied all manifests to the Operators in the Runlevel, but thekube-apiserver-operator ClusterOperatorperforms some actions after its new version was deployed. Thekube-apiserver-operator ClusterOperatordeclares this progress through theProgressing=Truecondition and by not declaring the new version as reconciled in itsstatus.versions. The CVO waits until the ClusterOperator reports an acceptable status, and then it will start reconciling manifests at Runlevel 25.

### 1.2.6. Understanding how the Machine Config Operator updates nodesCopy linkLink copied to clipboard!

The Machine Config Operator (MCO) applies a new machine configuration to each control plane node and compute node. During the machine configuration update, control plane nodes and compute nodes are organized into their own machine config pools, where the pools of machines are updated in parallel.

The.spec.maxUnavailableparameter, which has a default value of1, determines how many nodes in a machine config pool can simultaneously undergo the update process.

The default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

When the machine configuration update process begins, the MCO checks the amount of currently unavailable nodes in a pool. If there are fewer unavailable nodes than the value of.spec.maxUnavailable, the MCO initiates the following sequence of actions on available nodes in the pool:

- Cordon and drain the nodeWhen a node is cordoned, workloads cannot be scheduled to it.

Cordon and drain the node

When a node is cordoned, workloads cannot be scheduled to it.

- Update the system configuration and operating system (OS) of the node
- Reboot the node
- Uncordon the node

A node undergoing this process is unavailable until it is uncordoned and workloads can be scheduled to it again. The MCO begins updating nodes until the number of unavailable nodes is equal to the value of.spec.maxUnavailable.

As a node completes its update and becomes available, the number of unavailable nodes in the machine config pool is once again fewer than.spec.maxUnavailable. If there are remaining nodes that need to be updated, the MCO initiates the update process on a node until the.spec.maxUnavailablelimit is once again reached. This process repeats until each control plane node and compute node has been updated.

The following example workflow describes how this process might occur in a machine config pool with 5 nodes, where.spec.maxUnavailableis 3 and all nodes are initially available:

- The MCO cordons nodes 1, 2, and 3, and begins to drain them.
- Node 2 finishes draining, reboots, and becomes available again. The MCO cordons node 4 and begins draining it.
- Node 1 finishes draining, reboots, and becomes available again. The MCO cordons node 5 and begins draining it.
- Node 3 finishes draining, reboots, and becomes available again.
- Node 5 finishes draining, reboots, and becomes available again.
- Node 4 finishes draining, reboots, and becomes available again.

Because the update process for each node is independent of other nodes, some nodes in the example above finish their update out of the order in which they were cordoned by the MCO.

You can check the status of the machine configuration update by running the following command:

Example output

```
NAME         CONFIG                                                 UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
master       rendered-master-acd1358917e9f98cbdb599aea622d78b       True      False      False      3              3                   3                     0                      22h
worker       rendered-worker-1d871ac76e1951d32b2fe92369879826       False     True       False      2              1                   1                     0                      22h
```

```
NAME         CONFIG                                                 UPDATED   UPDATING   DEGRADED   MACHINECOUNT   READYMACHINECOUNT   UPDATEDMACHINECOUNT   DEGRADEDMACHINECOUNT   AGE
master       rendered-master-acd1358917e9f98cbdb599aea622d78b       True      False      False      3              3                   3                     0                      22h
worker       rendered-worker-1d871ac76e1951d32b2fe92369879826       False     True       False      2              1                   1                     0                      22h
```

## 1.3. Understanding update channels and releasesCopy linkLink copied to clipboard!

Update channels are the mechanism by which users declare the OpenShift Container Platform minor version they intend to update their clusters to. They also allow users to choose the timing and level of support their updates will have through thefast,stable,candidate, andeuschannel options.

The Cluster Version Operator uses an update graph based on the channel declaration, along with other conditional information, to provide a list of recommended and conditional updates available to the cluster.

### 1.3.1. Overview of update channelsCopy linkLink copied to clipboard!

Update channels correspond to a minor version of OpenShift Container Platform. The version number in the channel represents the target minor version that the cluster will eventually be updated to, even if it is higher than the cluster’s current minor version.

For instance, OpenShift Container Platform 4.10 update channels provide the following recommendations:

- Updates within 4.10.
- Updates within 4.9.
- Updates from 4.9 to 4.10, allowing all 4.9 clusters to eventually update to 4.10, even if they do not immediately meet the minimum z-stream version requirements.
- eus-4.10only: updates within 4.8.
- eus-4.10only: updates from 4.8 to 4.9 to 4.10, allowing all 4.8 clusters to eventually update to 4.10.

4.10 update channels do not recommend updates to 4.11 or later releases. This strategy ensures that administrators must explicitly decide to update to the next minor version of OpenShift Container Platform.

Update channels control only release selection and do not impact the version of the cluster that you install. Theopenshift-installbinary file for a specific version of OpenShift Container Platform always installs that version.

OpenShift Container Platform 4.17 offers the following update channels:

- stable-4.17
- eus-4.y(only offered for EUS versions and meant to facilitate updates between EUS versions)
- fast-4.17
- candidate-4.17

If you do not want the Cluster Version Operator to fetch available updates from the update recommendation service, you can use theoc adm upgrade channelcommand in the OpenShift CLI to configure an empty channel. This configuration can be helpful if, for example, a cluster has restricted network access and there is no local, reachable update recommendation service.

Red Hat recommends updating only to versions suggested by OpenShift Update Service. For a minor version update, versions must be contiguous. Red Hat does not test updates to noncontiguous versions and cannot guarantee compatibility with earlier versions.

### 1.3.2. Update channelsCopy linkLink copied to clipboard!

OpenShift Container Platform offers several update channels for you to choose from, depending on your desired update strategy.

#### 1.3.2.1. fast-4.17 channelCopy linkLink copied to clipboard!

Thefast-4.17channel is updated with new versions of OpenShift Container Platform 4.17 as soon as Red Hat declares the version as a general availability (GA) release. As such, these releases are fully supported and purposed to be used in production environments.

#### 1.3.2.2. stable-4.17 channelCopy linkLink copied to clipboard!

While thefast-4.17channel contains releases as soon as their errata are published, releases are added to thestable-4.17channel after a delay. During this delay, data is collected from multiple sources and analyzed for indications of product regressions. Once a significant number of data points have been collected, these releases are added to the stable channel.

Since the time required to obtain a significant number of data points varies based on many factors, Service LeveL Objective (SLO) is not offered for the delay duration between fast and stable channels. For more information, please see "Choosing the correct channel for your cluster"

Newly installed clusters default to using stable channels.

#### 1.3.2.3. eus-4.y channelCopy linkLink copied to clipboard!

In addition to the stable channel, all even-numbered minor versions of OpenShift Container Platform offerExtended Update Support(EUS). Releases promoted to the stable channel are also simultaneously promoted to the EUS channels. The primary purpose of the EUS channels is to serve as a convenience for clusters performing a Control Plane Only update.

Both standard and non-EUS subscribers can access all EUS repositories and necessary RPMs (rhel-*-eus-rpms) to be able to support critical purposes such as debugging and building drivers.

#### 1.3.2.4. candidate-4.17 channelCopy linkLink copied to clipboard!

Thecandidate-4.17channel offers unsupported early access to releases as soon as they are built. Releases present only in candidate channels may not contain the full feature set of eventual GA releases or features may be removed prior to GA. Additionally, these releases have not been subject to full Red Hat Quality Assurance and may not offer update paths to later GA releases. Given these caveats, the candidate channel is only suitable for testing purposes where destroying and recreating a cluster is acceptable.

### 1.3.3. Restricted network clustersCopy linkLink copied to clipboard!

If you manage the container images for your OpenShift Container Platform clusters yourself, you must consult the Red Hat errata that is associated with product releases and note any comments that impact updates.

During an update, the user interface might warn you about switching between these versions, so you must ensure that you selected an appropriate version before you bypass those warnings.

### 1.3.4. Update recommendations in the channelCopy linkLink copied to clipboard!

OpenShift Container Platform maintains an update recommendation service that knows your installed OpenShift Container Platform version and the path to take within the channel to get you to the next release.

Update paths are also limited to versions relevant to your currently selected channel and its promotion characteristics.

You can imagine seeing the following releases in your channel:

- 4.17.0
- 4.17.1
- 4.17.3
- 4.17.4

The service recommends only updates that have been tested and have no known serious regressions. For example, if your cluster is on 4.17.1 and OpenShift Container Platform suggests 4.17.4, then it is recommended to update from 4.17.1 to 4.17.4.

Do not rely on consecutive patch numbers. In this example, 4.17.2 is not and never was available in the channel, therefore updates to 4.17.2 are not recommended or supported.

### 1.3.5. Update recommendations and Conditional UpdatesCopy linkLink copied to clipboard!

Red Hat monitors newly released versions and update paths associated with those versions before and after they are added to supported channels.

If Red Hat removes update recommendations from any supported release, a superseding update recommendation will be provided to a future version that corrects the regression. There may however be a delay while the defect is corrected, tested, and promoted to your selected channel.

Beginning in OpenShift Container Platform 4.10, when update risks are confirmed, they are declared as Conditional Update risks for the relevant updates. Each known risk may apply to all clusters or only clusters matching certain conditions. Some examples include having thePlatformset toNoneor the CNI provider set toOpenShiftSDN. The Cluster Version Operator (CVO) continually evaluates known risks against the current cluster state. If no risks match, the update is recommended. If the risk matches, those update paths are labeled asupdates with known issues, and a reference link to the known issues is provided. The reference link helps the cluster admin decide if they want to accept the risk and continue to update their cluster.

When Red Hat chooses to declare Conditional Update risks, that action is taken in all relevant channels simultaneously. Declaration of a Conditional Update risk may happen either before or after the update has been promoted to supported channels.

### 1.3.6. What to consider when choosing an update channelCopy linkLink copied to clipboard!

Choosing the appropriate update channel for your cluster involves two decisions.

First, select the minor version you want for your cluster update. Selecting a channel which matches your current version ensures that you only apply z-stream updates and do not receive feature updates. Selecting an available channel which has a version greater than your current version will ensure that after one or more updates your cluster will have updated to that version. Your cluster will only be offered channels which match its current version, the next version, or the next EUS version.

Due to the complexity involved in planning updates between versions many minors apart, channels that assist in planning updates beyond a single Control Plane Only update are not offered.

Second, you should choose your desired rollout strategy. You may choose to update as soon as Red Hat declares a release GA by selecting from fast channels or you may want to wait for Red Hat to promote releases to the stable channel. Update recommendations offered in thefast-4.17andstable-4.17are both fully supported and benefit equally from ongoing data analysis. The promotion delay before promoting a release to the stable channel represents the only difference between the two channels. Updates to the latest z-streams are generally promoted to the stable channel within a week or two, however the delay when initially rolling out updates to the latest minor is much longer, generally 45-90 days. Please consider the promotion delay when choosing your desired channel, as waiting for promotion to the stable channel may affect your scheduling plans.

Additionally, there are several factors which may lead an organization to move clusters to the fast channel either permanently or temporarily including the following:

- The desire to apply a specific fix known to affect your environment without delay.
- Application of CVE fixes without delay. CVE fixes may introduce regressions, so promotion delays still apply to z-streams with CVE fixes.
- Internal testing processes. If it takes your organization several weeks to qualify releases it is best test concurrently with our promotion process rather than waiting. This also assures that any telemetry signal provided to Red Hat is a factored into our rollout, so issues relevant to you can be fixed faster.

### 1.3.7. Considerations for switching between channelsCopy linkLink copied to clipboard!

You can switch your cluster’s update channel through the web console or the CLI, in order to access different update recommendations for your cluster.

You can switch the channel from the CLI by running the following command:

The web console will display an alert if you switch to a channel that does not include the current release. The web console does not recommend any updates while on a channel without the current release. You can return to the original channel at any point, however.

Changing your channel might impact the supportability of your cluster. The following conditions might apply:

- Your cluster is still supported if you change from thestable-4.17channel to thefast-4.17channel.
- You can switch to thecandidate-4.17channel at any time, but some releases for this channel might be unsupported.
- You can switch from thecandidate-4.17channel to thefast-4.17channel if your current release is a general availability release.
- You can always switch from thefast-4.17channel to thestable-4.17channel. There is a possible delay of up to a day for the release to be promoted tostable-4.17if the current release was recently promoted.

## 1.4. Understanding OpenShift Container Platform update durationCopy linkLink copied to clipboard!

OpenShift Container Platform update duration varies based on the deployment topology. You can understand the factors that affect update duration and use them to estimate how long the cluster update takes in your environment.

### 1.4.1. Factors affecting update durationCopy linkLink copied to clipboard!

The duration of OpenShift Container Platform updates vary for several reasons.

The following factors can affect your cluster update duration:

- The reboot of compute nodes to the new machine configuration by Machine Config Operator (MCO)The value ofMaxUnavailablein the machine config poolThe default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.The minimum number or percentages of replicas set in pod disruption budget (PDB)

The reboot of compute nodes to the new machine configuration by Machine Config Operator (MCO)

- The value ofMaxUnavailablein the machine config poolThe default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

The value ofMaxUnavailablein the machine config pool

The default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

- The minimum number or percentages of replicas set in pod disruption budget (PDB)
- The number of nodes in the cluster
- The health of the cluster nodes

### 1.4.2. Cluster update phasesCopy linkLink copied to clipboard!

OpenShift Container Platform updates are done in multiple phases.

The cluster update happens in the following two phases:

- Cluster Version Operator (CVO) target update payload deployment
- Machine Config Operator (MCO) node updates

#### 1.4.2.1. Cluster Version Operator target update payload deploymentCopy linkLink copied to clipboard!

In the first phase of the update, the Cluster Version Operator (CVO) retrieves the target update release image and applies to the cluster.

All components which run as pods are updated during this phase, whereas the host components are updated by the Machine Config Operator (MCO). This process might take 60 to 120 minutes.

The CVO phase of the update does not restart the nodes.

#### 1.4.2.2. Machine Config Operator node updatesCopy linkLink copied to clipboard!

In the second phase of the update, the Machine Config Operator (MCO) applies a new machine configuration to each control plane and compute node.

During this process, the MCO performs the following sequential actions on each node of the cluster:

- Cordon and drain all the nodes
- Update the operating system (OS)
- Reboot the nodes
- Uncordon all nodes and schedule workloads on the node

When a node is cordoned, workloads cannot be scheduled to it.

The time to complete this process depends on several factors including the node and infrastructure configuration. This process might take 5 or more minutes to complete per node.

In addition to MCO, you should consider the impact of the following parameters:

- The control plane node update duration is predictable and oftentimes shorter than compute nodes, because the control plane workloads are tuned for graceful updates and quick drains.
- You can update the compute nodes in parallel by setting themaxUnavailablefield to greater than1in the Machine Config Pool (MCP). The MCO cordons the number of nodes specified inmaxUnavailableand marks them unavailable for update.
- When you increasemaxUnavailableon the MCP, it can help the pool to update more quickly. However, ifmaxUnavailableis set too high, and several nodes are cordoned simultaneously, the pod disruption budget (PDB) guarded workloads could fail to drain because a schedulable node cannot be found to run the replicas. If you increasemaxUnavailablefor the MCP, ensure that you still have sufficient schedulable nodes to allow PDB guarded workloads to drain.
- Before you begin the update, you must ensure that all the nodes are available. Any unavailable nodes can significantly impact the update duration because the node unavailability affects themaxUnavailableand pod disruption budgets.To check the status of nodes from the terminal, run the following command:oc get node$oc getnodeCopy to ClipboardCopied!Toggle word wrapToggle overflowExample OutputNAME                                        STATUS                      ROLES   AGE     VERSION
ip-10-0-137-31.us-east-2.compute.internal   Ready,SchedulingDisabled    worker  12d     v1.23.5+3afdacb
ip-10-0-151-208.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-176-138.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-183-194.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
ip-10-0-204-102.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-207-224.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacbNAME                                        STATUS                      ROLES   AGE     VERSION
ip-10-0-137-31.us-east-2.compute.internal   Ready,SchedulingDisabled    worker  12d     v1.23.5+3afdacb
ip-10-0-151-208.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-176-138.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-183-194.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
ip-10-0-204-102.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-207-224.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacbCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the status of the node isNotReadyorSchedulingDisabled, then the node is not available and this impacts the update duration.You can also check the status of nodes from theAdministratorperspective in the web console by expandingComputeNodes.

Before you begin the update, you must ensure that all the nodes are available. Any unavailable nodes can significantly impact the update duration because the node unavailability affects themaxUnavailableand pod disruption budgets.

To check the status of nodes from the terminal, run the following command:

Example Output

```
NAME                                        STATUS                      ROLES   AGE     VERSION
ip-10-0-137-31.us-east-2.compute.internal   Ready,SchedulingDisabled    worker  12d     v1.23.5+3afdacb
ip-10-0-151-208.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-176-138.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-183-194.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
ip-10-0-204-102.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-207-224.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
```

```
NAME                                        STATUS                      ROLES   AGE     VERSION
ip-10-0-137-31.us-east-2.compute.internal   Ready,SchedulingDisabled    worker  12d     v1.23.5+3afdacb
ip-10-0-151-208.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-176-138.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-183-194.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
ip-10-0-204-102.us-east-2.compute.internal  Ready                       master  12d     v1.23.5+3afdacb
ip-10-0-207-224.us-east-2.compute.internal  Ready                       worker  12d     v1.23.5+3afdacb
```

If the status of the node isNotReadyorSchedulingDisabled, then the node is not available and this impacts the update duration.

You can also check the status of nodes from theAdministratorperspective in the web console by expandingComputeNodes.

#### 1.4.2.3. Example update duration of cluster OperatorsCopy linkLink copied to clipboard!

You can review an example of the update duration for cluster Operators to better understand the factors that affect the duration of the update.

The previous diagram shows an example of the time that cluster Operators might take to update to their new versions. The example is based on a three-node AWS OVN cluster, which has a healthy computeMachineConfigPooland no workloads that take long to drain, updating from 4.13 to 4.14.

- The specific update duration of a cluster and its Operators can vary based on several cluster characteristics, such as the target version, the amount of nodes, and the types of workloads scheduled to the nodes.
- Some Operators, such as the Cluster Version Operator, update themselves in a short amount of time. These Operators have either been omitted from the diagram or are included in the broader group of Operators labeled "Other Operators in parallel".

Each cluster Operator has characteristics that affect the time it takes to update itself. For instance, the Kube API Server Operator in this example took more than eleven minutes to update becausekube-apiserverprovides graceful termination support, meaning that existing, in-flight requests are allowed to complete gracefully. This might result in a longer shutdown of thekube-apiserver. In the case of this Operator, update speed is sacrificed to help prevent and limit disruptions to cluster functionality during an update.

Another characteristic that affects the update duration of an Operator is whether the Operator utilizes DaemonSets. The Network and DNS Operators utilize full-cluster DaemonSets, which can take time to roll out their version changes, and this is one of several reasons why these Operators might take longer to update themselves.

Additionally, the update duration for some Operators is heavily dependent on characteristics of the cluster itself. For example, the Machine Config Operator update applies machine configuration changes to each node in the cluster. A cluster with many nodes has a longer update duration for the Machine Config Operator compared to a cluster with fewer nodes.

Each cluster Operator is assigned a stage during which it can be updated. Operators within the same stage can update simultaneously, and Operators in a given stage cannot begin updating until all previous stages have been completed. For more information, see "Understanding how manifests are applied during an update".

### 1.4.3. How to estimate cluster update timeCopy linkLink copied to clipboard!

Historical update duration of similar clusters provides you the best estimate for the future cluster updates. If you do not have historical data, you can calculate an estimate of the update duration.

You can use the following convention to estimate your cluster update time:

A node update iteration consists of one or more nodes updated in parallel. The control plane nodes are always updated in parallel with the compute nodes. In addition, one or more compute nodes can be updated in parallel based on themaxUnavailablevalue.

The default setting formaxUnavailableis1for all the machine config pools in OpenShift Container Platform. It is recommended to not change this value and update one control plane node at a time. Do not change this value to3for the control plane pool.

For example, to estimate the update time, consider an OpenShift Container Platform cluster with three control plane nodes and six compute nodes, where each host takes about 5 minutes to reboot.

The time it takes to reboot a particular node varies significantly. In cloud instances, the reboot might take about 1 to 2 minutes, whereas in physical bare metal hosts the reboot might take more than 15 minutes.

In a scenario where you setmaxUnavailableto1for both the control plane and compute nodes Machine Config Pool (MCP), then all the six compute nodes will update one after another in each iteration:

In a scenario where you setmaxUnavailableto2for the compute node MCP, then two compute nodes will update in parallel in each iteration. Therefore it takes total three iterations to update all the nodes.

The default setting formaxUnavailableis1for all the MCPs in OpenShift Container Platform. It is recommended that you do not change themaxUnavailablein the control plane MCP.

### 1.4.4. Red Hat Enterprise Linux (RHEL) compute nodesCopy linkLink copied to clipboard!

Red Hat Enterprise Linux (RHEL) compute nodes require an additional usage ofopenshift-ansibleto update node binary components. The actual time spent updating RHEL compute nodes should not be significantly different from Red Hat Enterprise Linux CoreOS (RHCOS) compute nodes.
