<!-- source: ocp_scc.md -->

# Security

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/authentication_and_authorization/managing-pod-security-policies
---

# Chapter 15. Managing security context constraints

In OpenShift Container Platform, you can use security context constraints (SCCs) to control permissions for the pods in your cluster.

Default SCCs are created during installation and when you install some Operators or other components. As a cluster administrator, you can also create your own SCCs by using the OpenShift CLI (oc).

Do not modify the default SCCs. Customizing the default SCCs can lead to issues when some of the platform pods deploy or OpenShift Container Platform is upgraded. Additionally, the default SCC values are reset to the defaults during some cluster upgrades, which discards all customizations to those SCCs.

Instead of modifying the default SCCs, create and modify your own SCCs as needed. For detailed steps, seeCreating security context constraints.

## 15.1. About security context constraintsCopy linkLink copied to clipboard!

Similar to the way that RBAC resources control user access, administrators can use security context constraints (SCCs) to control permissions for pods. These permissions determine the actions that a pod can perform and what resources it can access. You can use SCCs to define a set of conditions that a pod must run with to be accepted into the system.

Security context constraints allow an administrator to control:

- Whether a pod can run privileged containers with theallowPrivilegedContainerflag
- Whether a pod is constrained with theallowPrivilegeEscalationflag
- The capabilities that a container can request
- The use of host directories as volumes
- The SELinux context of the container
- The container user ID
- The use of host namespaces and networking
- The allocation of anFSGroupthat owns the pod volumes
- The configuration of allowable supplemental groups
- Whether a container requires write access to its root file system
- The usage of volume types
- The configuration of allowableseccompprofiles

Do not set theopenshift.io/run-levellabel on any namespaces in OpenShift Container Platform. This label is for use by internal OpenShift Container Platform components to manage the startup of major API groups, such as the Kubernetes API server and OpenShift API server. If theopenshift.io/run-levellabel is set, no SCCs are applied to pods in that namespace, causing any workloads running in that namespace to be highly privileged.

### 15.1.1. Default security context constraintsCopy linkLink copied to clipboard!

The cluster contains several default security context constraints (SCCs) as described in the table below. Additional SCCs might be installed when you install Operators or other components to OpenShift Container Platform.

Do not modify the default SCCs. Customizing the default SCCs can lead to issues when some of the platform pods deploy or OpenShift Container Platform is upgraded. Additionally, the default SCC values are reset to the defaults during some cluster upgrades, which discards all customizations to those SCCs.

Instead of modifying the default SCCs, create and modify your own SCCs as needed. For detailed steps, seeCreating security context constraints.

| Security context constraint | Description |
| --- | --- |
| anyuid | Provides all features of therestrictedSCC, but allows users to run with any UID and any GID. |
| hostaccess | Allows access to all host namespaces but still requires pods to be run with a UID and SELinux contex |
| hostmount-anyuid | Provides all the features of therestrictedSCC, but allows host mounts and running as any UID and any |
| hostnetwork | Allows using host networking and host ports but still requires pods to be run with a UID and SELinux |
| hostnetwork-v2 | Like thehostnetworkSCC, but with the following differences:ALLcapabilities are dropped from containe |
| node-exporter | Used for the Prometheus node exporter.This SCC allows host file system access as any UID, including  |
| nonroot | Provides all features of therestrictedSCC, but allows users to run with any non-root UID. The user m |
| nonroot-v2 | Like thenonrootSCC, but with the following differences:ALLcapabilities are dropped from containers.T |
| privileged | Allows access to all privileged and host features and the ability to run as any user, any group, any |
| restricted | Denies access to all host features and requires pods to be run with a UID, and SELinux context that  |
| restricted-v2 | Like therestrictedSCC, but with the following differences:ALLcapabilities are dropped from container |

anyuid

Provides all features of therestrictedSCC, but allows users to run with any UID and any GID.

hostaccess

Allows access to all host namespaces but still requires pods to be run with a UID and SELinux context that are allocated to the namespace.

This SCC allows host access to namespaces, file systems, and PIDs. It should only be used by trusted pods. Grant with caution.

hostmount-anyuid

Provides all the features of therestrictedSCC, but allows host mounts and running as any UID and any GID on the system.

This SCC allows host file system access as any UID, including UID 0. Grant with caution.

hostnetwork

Allows using host networking and host ports but still requires pods to be run with a UID and SELinux context that are allocated to the namespace.

If additional workloads are run on control plane hosts, use caution when providing access tohostnetwork. A workload that runshostnetworkon a control plane host is effectively root on the cluster and must be trusted accordingly.

hostnetwork-v2

Like thehostnetworkSCC, but with the following differences:

- ALLcapabilities are dropped from containers.
- TheNET_BIND_SERVICEcapability can be added explicitly.
- seccompProfileis set toruntime/defaultby default.
- allowPrivilegeEscalationmust be unset or set tofalsein security contexts.

node-exporter

Used for the Prometheus node exporter.

This SCC allows host file system access as any UID, including UID 0. Grant with caution.

nonroot

Provides all features of therestrictedSCC, but allows users to run with any non-root UID. The user must specify the UID or it must be specified in the manifest of the container runtime.

nonroot-v2

Like thenonrootSCC, but with the following differences:

- ALLcapabilities are dropped from containers.
- TheNET_BIND_SERVICEcapability can be added explicitly.
- seccompProfileis set toruntime/defaultby default.
- allowPrivilegeEscalationmust be unset or set tofalsein security contexts.

privileged

Allows access to all privileged and host features and the ability to run as any user, any group, any FSGroup, and with any SELinux context.

This is the most relaxed SCC and should be used only for cluster administration. Grant with caution.

TheprivilegedSCC allows:

- Users to run privileged pods
- Pods to mount host directories as volumes
- Pods to run as any user
- Pods to run with any MCS label
- Pods to use the host’s IPC namespace
- Pods to use the host’s PID namespace
- Pods to use any FSGroup
- Pods to use any supplemental group
- Pods to use any seccomp profiles
- Pods to request any capabilities

Settingprivileged: truein the pod specification does not necessarily select theprivilegedSCC. The SCC that hasallowPrivilegedContainer: trueand has the highest prioritization will be chosen if the user has the permissions to use it.

restricted

Denies access to all host features and requires pods to be run with a UID, and SELinux context that are allocated to the namespace.

TherestrictedSCC:

- Ensures that pods cannot run as privileged
- Ensures that pods cannot mount host directory volumes
- Requires that a pod is run as a user in a pre-allocated range of UIDs
- Requires that a pod is run with a pre-allocated MCS label
- Requires that a pod is run with a preallocated FSGroup
- Allows pods to use any supplemental group

In clusters that were upgraded from OpenShift Container Platform 4.10 or earlier, this SCC is available for use by any authenticated user. TherestrictedSCC is no longer available to users of new OpenShift Container Platform 4.11 or later installations, unless the access is explicitly granted.

restricted-v2

Like therestrictedSCC, but with the following differences:

- ALLcapabilities are dropped from containers.
- TheNET_BIND_SERVICEcapability can be added explicitly.
- seccompProfileis set toruntime/defaultby default.
- allowPrivilegeEscalationmust be unset or set tofalsein security contexts.

This is the most restrictive SCC provided by a new installation and will be used by default for authenticated users.

Therestricted-v2SCC is the most restrictive of the SCCs that is included by default with the system. However, you can create a custom SCC that is even more restrictive. For example, you can create an SCC that restrictsreadOnlyRootFilesystemtotrue.

### 15.1.2. Security context constraints settingsCopy linkLink copied to clipboard!

Security context constraints (SCCs) are composed of settings and strategies that control the security features a pod has access to. These settings fall into three categories:

| Category | Description |
| --- | --- |
| Controlled by a boolean | Fields of this type default to the most restrictive value. For example,AllowPrivilegedContaineris al |
| Controlled by an allowable set | Fields of this type are checked against the set to ensure their value is allowed. |
| Controlled by a strategy | Items that have a strategy to generate a value provide:A mechanism to generate the value, andA mecha |

Controlled by a boolean

Fields of this type default to the most restrictive value. For example,AllowPrivilegedContaineris always set tofalseif unspecified.

Controlled by an allowable set

Fields of this type are checked against the set to ensure their value is allowed.

Controlled by a strategy

Items that have a strategy to generate a value provide:

- A mechanism to generate the value, and
- A mechanism to ensure that a specified value falls into the set of allowable values.

CRI-O has the following default list of capabilities that are allowed for each container of a pod:

- CHOWN
- DAC_OVERRIDE
- FSETID
- FOWNER
- SETGID
- SETUID
- SETPCAP
- NET_BIND_SERVICE
- KILL

The containers use the capabilities from this default list, but pod manifest authors can alter the list by requesting additional capabilities or removing some of the default behaviors. Use theallowedCapabilities,defaultAddCapabilities, andrequiredDropCapabilitiesparameters to control such requests from the pods. With these parameters you can specify which capabilities can be requested, which ones must be added to each container, and which ones must be forbidden, or dropped, from each container.

You can drop all capabilites from containers by setting therequiredDropCapabilitiesparameter toALL. This is what therestricted-v2SCC does.

### 15.1.3. Security context constraints strategiesCopy linkLink copied to clipboard!

RunAsUser

- MustRunAs- Requires arunAsUserto be configured. Uses the configuredrunAsUseras the default. Validates against the configuredrunAsUser.ExampleMustRunAssnippet...
runAsUser:
  type: MustRunAs
  uid: <id>
......runAsUser:type:MustRunAsuid:<id>...Copy to ClipboardCopied!Toggle word wrapToggle overflow

MustRunAs- Requires arunAsUserto be configured. Uses the configuredrunAsUseras the default. Validates against the configuredrunAsUser.

ExampleMustRunAssnippet

```
...
runAsUser:
  type: MustRunAs
  uid: <id>
...
```

```
...
runAsUser:
  type: MustRunAs
  uid: <id>
...
```

- MustRunAsRange- Requires minimum and maximum values to be defined if not using pre-allocated values. Uses the minimum as the default. Validates against the entire allowable range.ExampleMustRunAsRangesnippet...
runAsUser:
  type: MustRunAsRange
  uidRangeMax: <maxvalue>
  uidRangeMin: <minvalue>
......runAsUser:type:MustRunAsRangeuidRangeMax:<maxvalue>uidRangeMin:<minvalue>...Copy to ClipboardCopied!Toggle word wrapToggle overflow

MustRunAsRange- Requires minimum and maximum values to be defined if not using pre-allocated values. Uses the minimum as the default. Validates against the entire allowable range.

ExampleMustRunAsRangesnippet

```
...
runAsUser:
  type: MustRunAsRange
  uidRangeMax: <maxvalue>
  uidRangeMin: <minvalue>
...
```

```
...
runAsUser:
  type: MustRunAsRange
  uidRangeMax: <maxvalue>
  uidRangeMin: <minvalue>
...
```

- MustRunAsNonRoot- Requires that the pod be submitted with a non-zerorunAsUseror have theUSERdirective defined in the image. No default provided.ExampleMustRunAsNonRootsnippet...
runAsUser:
  type: MustRunAsNonRoot
......runAsUser:type:MustRunAsNonRoot...Copy to ClipboardCopied!Toggle word wrapToggle overflow

MustRunAsNonRoot- Requires that the pod be submitted with a non-zerorunAsUseror have theUSERdirective defined in the image. No default provided.

ExampleMustRunAsNonRootsnippet

```
...
runAsUser:
  type: MustRunAsNonRoot
...
```

```
...
runAsUser:
  type: MustRunAsNonRoot
...
```

- RunAsAny- No default provided. Allows anyrunAsUserto be specified.ExampleRunAsAnysnippet...
runAsUser:
  type: RunAsAny
......runAsUser:type:RunAsAny...Copy to ClipboardCopied!Toggle word wrapToggle overflow

RunAsAny- No default provided. Allows anyrunAsUserto be specified.

ExampleRunAsAnysnippet

```
...
runAsUser:
  type: RunAsAny
...
```

```
...
runAsUser:
  type: RunAsAny
...
```

SELinuxContext

- MustRunAs- RequiresseLinuxOptionsto be configured if not using pre-allocated values. UsesseLinuxOptionsas the default. Validates againstseLinuxOptions.
- RunAsAny- No default provided. Allows anyseLinuxOptionsto be specified.

SupplementalGroups

- MustRunAs- Requires at least one range to be specified if not using pre-allocated values. Uses the minimum value of the first range as the default. Validates against all ranges.
- RunAsAny- No default provided. Allows anysupplementalGroupsto be specified.

FSGroup

- MustRunAs- Requires at least one range to be specified if not using pre-allocated values. Uses the minimum value of the first range as the default. Validates against the first ID in the first range.
- RunAsAny- No default provided. Allows anyfsGroupID to be specified.

### 15.1.4. Controlling volumesCopy linkLink copied to clipboard!

The usage of specific volume types can be controlled by setting thevolumesfield of the SCC.

The allowable values of this field correspond to the volume sources that are defined when creating a volume:

- awsElasticBlockStore
- azureDisk
- azureFile
- cephFS
- cinder
- configMap
- csi
- downwardAPI
- emptyDir
- fc
- flexVolume
- flocker
- gcePersistentDisk
- ephemeral
- gitRepo
- glusterfs
- hostPath
- iscsi
- nfs
- persistentVolumeClaim
- photonPersistentDisk
- portworxVolume
- projected
- quobyte
- rbd
- scaleIO
- secret
- storageos
- vsphereVolume
- *(A special value to allow the use of all volume types.)
- none(A special value to disallow the use of all volumes types. Exists only for backwards compatibility.)

The recommended minimum set of allowed volumes for new SCCs areconfigMap,downwardAPI,emptyDir,persistentVolumeClaim,secret, andprojected.

This list of allowable volume types is not exhaustive because new types are added with each release of OpenShift Container Platform.

For backwards compatibility, the usage ofallowHostDirVolumePluginoverrides settings in thevolumesfield. For example, ifallowHostDirVolumePluginis set to false but allowed in thevolumesfield, then thehostPathvalue will be removed fromvolumes.

### 15.1.5. Admission controlCopy linkLink copied to clipboard!

Admission controlwith SCCs allows for control over the creation of resources based on the capabilities granted to a user.

In terms of the SCCs, this means that an admission controller can inspect the user information made available in the context to retrieve an appropriate set of SCCs. Doing so ensures the pod is authorized to make requests about its operating environment or to generate a set of constraints to apply to the pod.

The set of SCCs that admission uses to authorize a pod are determined by the user identity and groups that the user belongs to. Additionally, if the pod specifies a service account, the set of allowable SCCs includes any constraints accessible to the service account.

When you create a workload resource, such as deployment, only the service account is used to find the SCCs and admit the pods when they are created.

Admission uses the following approach to create the final security context for the pod:

- Retrieve all SCCs available for use.
- Generate field values for security context settings that were not specified on the request.
- Validate the final settings against the available constraints.

If a matching set of constraints is found, then the pod is accepted. If the request cannot be matched to an SCC, the pod is rejected.

A pod must validate every field against the SCC. The following are examples for just two of the fields that must be validated:

These examples are in the context of a strategy using the pre-allocated values.

An FSGroup SCC strategy ofMustRunAs

If the pod defines afsGroupID, then that ID must equal the defaultfsGroupID. Otherwise, the pod is not validated by that SCC and the next SCC is evaluated.

If theSecurityContextConstraints.fsGroupfield has valueRunAsAnyand the pod specification omits thePod.spec.securityContext.fsGroup, then this field is considered valid. Note that it is possible that during validation, other SCC settings will reject other pod fields and thus cause the pod to fail.

ASupplementalGroupsSCC strategy ofMustRunAs

If the pod specification defines one or moresupplementalGroupsIDs, then the pod’s IDs must equal one of the IDs in the namespace’sopenshift.io/sa.scc.supplemental-groupsannotation. Otherwise, the pod is not validated by that SCC and the next SCC is evaluated.

If theSecurityContextConstraints.supplementalGroupsfield has valueRunAsAnyand the pod specification omits thePod.spec.securityContext.supplementalGroups, then this field is considered valid. Note that it is possible that during validation, other SCC settings will reject other pod fields and thus cause the pod to fail.

### 15.1.6. Security context constraints prioritizationCopy linkLink copied to clipboard!

Security context constraints (SCCs) have a priority field that affects the ordering when attempting to validate a request by the admission controller.

A priority value of0is the lowest possible priority. A nil priority is considered a0, or lowest, priority. Higher priority SCCs are moved to the front of the set when sorting.

When the complete set of available SCCs is determined, the SCCs are ordered in the following manner:

- The highest priority SCCs are ordered first.
- If the priorities are equal, the SCCs are sorted from most restrictive to least restrictive.
- If both the priorities and restrictions are equal, the SCCs are sorted by name.

By default, theanyuidSCC granted to cluster administrators is given priority in their SCC set. This allows cluster administrators to run pods as any user by specifyingRunAsUserin the pod’sSecurityContext.

## 15.2. About pre-allocated security context constraints valuesCopy linkLink copied to clipboard!

The admission controller is aware of certain conditions in the security context constraints (SCCs) that trigger it to look up pre-allocated values from a namespace and populate the SCC before processing the pod. Each SCC strategy is evaluated independently of other strategies, with the pre-allocated values, where allowed, for each policy aggregated with pod specification values to make the final values for the various IDs defined in the running pod.

The following SCCs cause the admission controller to look for pre-allocated values when no ranges are defined in the pod specification:

- ARunAsUserstrategy ofMustRunAsRangewith no minimum or maximum set. Admission looks for theopenshift.io/sa.scc.uid-rangeannotation to populate range fields.
- AnSELinuxContextstrategy ofMustRunAswith no level set. Admission looks for theopenshift.io/sa.scc.mcsannotation to populate the level.
- AFSGroupstrategy ofMustRunAs. Admission looks for theopenshift.io/sa.scc.supplemental-groupsannotation.
- ASupplementalGroupsstrategy ofMustRunAs. Admission looks for theopenshift.io/sa.scc.supplemental-groupsannotation.

During the generation phase, the security context provider uses default values for any parameter values that are not specifically set in the pod. Default values are based on the selected strategy:

- RunAsAnyandMustRunAsNonRootstrategies do not provide default values. If the pod needs a parameter value, such as a group ID, you must define the value in the pod specification.
- MustRunAs(single value) strategies provide a default value that is always used. For example, for group IDs, even if the pod specification defines its own ID value, the namespace’s default parameter value also appears in the pod’s groups.
- MustRunAsRangeandMustRunAs(range-based) strategies provide the minimum value of the range. As with a single valueMustRunAsstrategy, the namespace’s default parameter value appears in the running pod. If a range-based strategy is configurable with multiple ranges, it provides the minimum value of the first configured range.

FSGroupandSupplementalGroupsstrategies fall back to theopenshift.io/sa.scc.uid-rangeannotation if theopenshift.io/sa.scc.supplemental-groupsannotation does not exist on the namespace. If neither exists, the SCC is not created.

By default, the annotation-basedFSGroupstrategy configures itself with a single range based on the minimum value for the annotation. For example, if your annotation reads1/3, theFSGroupstrategy configures itself with a minimum and maximum value of1. If you want to allow more groups to be accepted for theFSGroupfield, you can configure a custom SCC that does not use the annotation.

Theopenshift.io/sa.scc.supplemental-groupsannotation accepts a comma-delimited list of blocks in the format of<start>/<lengthor<start>-<end>. Theopenshift.io/sa.scc.uid-rangeannotation accepts only a single block.

## 15.3. Example security context constraintsCopy linkLink copied to clipboard!

The following examples show the security context constraints (SCC) format and annotations:

AnnotatedprivilegedSCC

```
allowHostDirVolumePlugin: true
allowHostIPC: true
allowHostNetwork: true
allowHostPID: true
allowHostPorts: true
allowPrivilegedContainer: true
allowedCapabilities: 
- '*'
apiVersion: security.openshift.io/v1
defaultAddCapabilities: [] 
fsGroup: 
  type: RunAsAny
groups: 
- system:cluster-admins
- system:nodes
kind: SecurityContextConstraints
metadata:
  annotations:
    kubernetes.io/description: 'privileged allows access to all privileged and host
      features and the ability to run as any user, any group, any fsGroup, and with
      any SELinux context.  WARNING: this is the most relaxed SCC and should be used
      only for cluster administration. Grant with caution.'
  creationTimestamp: null
  name: privileged
priority: null
readOnlyRootFilesystem: false
requiredDropCapabilities: null 
runAsUser: 
  type: RunAsAny
seLinuxContext: 
  type: RunAsAny
seccompProfiles:
- '*'
supplementalGroups: 
  type: RunAsAny
users: 
- system:serviceaccount:default:registry
- system:serviceaccount:default:router
- system:serviceaccount:openshift-infra:build-controller
volumes: 
- '*'
```

```
allowHostDirVolumePlugin: true
allowHostIPC: true
allowHostNetwork: true
allowHostPID: true
allowHostPorts: true
allowPrivilegedContainer: true
allowedCapabilities:
```

```
- '*'
apiVersion: security.openshift.io/v1
defaultAddCapabilities: []
```

```
fsGroup:
```

```
type: RunAsAny
groups:
```

```
- system:cluster-admins
- system:nodes
kind: SecurityContextConstraints
metadata:
  annotations:
    kubernetes.io/description: 'privileged allows access to all privileged and host
      features and the ability to run as any user, any group, any fsGroup, and with
      any SELinux context.  WARNING: this is the most relaxed SCC and should be used
      only for cluster administration. Grant with caution.'
  creationTimestamp: null
  name: privileged
priority: null
readOnlyRootFilesystem: false
requiredDropCapabilities: null
```

```
runAsUser:
```

```
type: RunAsAny
seLinuxContext:
```

```
type: RunAsAny
seccompProfiles:
- '*'
supplementalGroups:
```

```
type: RunAsAny
users:
```

```
- system:serviceaccount:default:registry
- system:serviceaccount:default:router
- system:serviceaccount:openshift-infra:build-controller
volumes:
```

```
- '*'
```

**1**
  A list of capabilities that a pod can request. An empty list means that none of capabilities can be requested while the special symbol*allows any capabilities.

**2**
  A list of additional capabilities that are added to any pod.

**3**
  TheFSGroupstrategy, which dictates the allowable values for the security context.

**4**
  The groups that can access this SCC.

**5**
  A list of capabilities to drop from a pod. Or, specifyALLto drop all capabilities.

**6**
  TherunAsUserstrategy type, which dictates the allowable values for the security context.

**7**
  TheseLinuxContextstrategy type, which dictates the allowable values for the security context.

**8**
  ThesupplementalGroupsstrategy, which dictates the allowable supplemental groups for the security context.

**9**
  The users who can access this SCC.

**10**
  The allowable volume types for the security context. In the example,*allows the use of all volume types.

Theusersandgroupsfields on the SCC control which users can access the SCC. By default, cluster administrators, nodes, and the build controller are granted access to the privileged SCC. All authenticated users are granted access to therestricted-v2SCC.

When verifying access to an SCC, be aware of the following command behaviors:

- Theoc adm policy who-can use scc <scc_name>andoc auth can-i use scc/<scc_name>commands evaluate only RBAC policies (RoleBindingorClusterRoleBindingresources). Their output does not include users or groups configured directly in the SCCusersandgroupsfields.
- Theoc describe scc <scc_name>command displays only the users and groups configured directly within the SCC object. Its output does not include access granted through RBAC policies.

Without explicitrunAsUsersetting

```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext: 
  containers:
  - name: sec-ctx-demo
    image: gcr.io/google-samples/node-hello:1.0
```

```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
```

```
containers:
  - name: sec-ctx-demo
    image: gcr.io/google-samples/node-hello:1.0
```

**1**
  When a container or pod does not request a user ID under which it should be run, the effective UID depends on the SCC that emits this pod. Because therestricted-v2SCC is granted to all authenticated users by default, it will be available to all users and service accounts and used in most cases. Therestricted-v2SCC usesMustRunAsRangestrategy for constraining and defaulting the possible values of thesecurityContext.runAsUserfield. The admission plugin will look for theopenshift.io/sa.scc.uid-rangeannotation on the current project to populate range fields, as it does not provide this range. In the end, a container will haverunAsUserequal to the first value of the range that is hard to predict because every project has different ranges.

With explicitrunAsUsersetting

```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000 
  containers:
    - name: sec-ctx-demo
      image: gcr.io/google-samples/node-hello:1.0
```

```
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsUser: 1000
```

```
containers:
    - name: sec-ctx-demo
      image: gcr.io/google-samples/node-hello:1.0
```

**1**
  A container or pod that requests a specific user ID will be accepted by OpenShift Container Platform only when a service account or a user is granted access to a SCC that allows such a user ID. The SCC can allow arbitrary IDs, an ID that falls into a range, or the exact user ID specific to the request.

This configuration is valid for SELinux, fsGroup, and Supplemental Groups.

## 15.4. Creating security context constraintsCopy linkLink copied to clipboard!

If the default security context constraints (SCCs) do not satisfy your application workload requirements, you can create a custom SCC by using the OpenShift CLI (oc).

Creating and modifying your own SCCs are advanced operations that might cause instability to your cluster. If you have questions about using your own SCCs, contact Red Hat Support. For information about contacting Red Hat support, seeGetting support.

Prerequisites

- Install the OpenShift CLI (oc).
- Log in to the cluster as a user with thecluster-adminrole.

Procedure

- Define the SCC in a YAML file namedscc-admin.yaml:kind: SecurityContextConstraints
apiVersion: security.openshift.io/v1
metadata:
  name: scc-admin
allowPrivilegedContainer: true
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
fsGroup:
  type: RunAsAny
supplementalGroups:
  type: RunAsAny
users:
- my-admin-user
groups:
- my-admin-groupkind:SecurityContextConstraintsapiVersion:security.openshift.io/v1metadata:name:scc-adminallowPrivilegedContainer:truerunAsUser:type:RunAsAnyseLinuxContext:type:RunAsAnyfsGroup:type:RunAsAnysupplementalGroups:type:RunAsAnyusers:-my-admin-usergroups:-my-admin-groupCopy to ClipboardCopied!Toggle word wrapToggle overflowOptionally, you can drop specific capabilities for an SCC by setting therequiredDropCapabilitiesfield with the desired values. Any specified capabilities are dropped from the container. To drop all capabilities, specifyALL. For example, to create an SCC that drops theKILL,MKNOD, andSYS_CHROOTcapabilities, add the following to the SCC object:requiredDropCapabilities:
- KILL
- MKNOD
- SYS_CHROOTrequiredDropCapabilities:-KILL-MKNOD-SYS_CHROOTCopy to ClipboardCopied!Toggle word wrapToggle overflowYou cannot list a capability in bothallowedCapabilitiesandrequiredDropCapabilities.CRI-O supports the same list of capability values that are found in theDocker documentation.

Define the SCC in a YAML file namedscc-admin.yaml:

```
kind: SecurityContextConstraints
apiVersion: security.openshift.io/v1
metadata:
  name: scc-admin
allowPrivilegedContainer: true
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
fsGroup:
  type: RunAsAny
supplementalGroups:
  type: RunAsAny
users:
- my-admin-user
groups:
- my-admin-group
```

```
kind: SecurityContextConstraints
apiVersion: security.openshift.io/v1
metadata:
  name: scc-admin
allowPrivilegedContainer: true
runAsUser:
  type: RunAsAny
seLinuxContext:
  type: RunAsAny
fsGroup:
  type: RunAsAny
supplementalGroups:
  type: RunAsAny
users:
- my-admin-user
groups:
- my-admin-group
```

Optionally, you can drop specific capabilities for an SCC by setting therequiredDropCapabilitiesfield with the desired values. Any specified capabilities are dropped from the container. To drop all capabilities, specifyALL. For example, to create an SCC that drops theKILL,MKNOD, andSYS_CHROOTcapabilities, add the following to the SCC object:

```
requiredDropCapabilities:
- KILL
- MKNOD
- SYS_CHROOT
```

```
requiredDropCapabilities:
- KILL
- MKNOD
- SYS_CHROOT
```

You cannot list a capability in bothallowedCapabilitiesandrequiredDropCapabilities.

CRI-O supports the same list of capability values that are found in theDocker documentation.

- Create the SCC by passing in the file:oc create -f scc-admin.yaml$oc create-fscc-admin.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputsecuritycontextconstraints "scc-admin" createdsecuritycontextconstraints "scc-admin" createdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the SCC by passing in the file:

Example output

Verification

- Verify that the SCC was created:oc get scc scc-admin$oc get scc scc-adminCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME        PRIV      CAPS      SELINUX    RUNASUSER   FSGROUP    SUPGROUP   PRIORITY   READONLYROOTFS   VOLUMES
scc-admin   true      []        RunAsAny   RunAsAny    RunAsAny   RunAsAny   <none>     false            [awsElasticBlockStore azureDisk azureFile cephFS cinder configMap downwardAPI emptyDir fc flexVolume flocker gcePersistentDisk gitRepo glusterfs iscsi nfs persistentVolumeClaim photonPersistentDisk quobyte rbd secret vsphere]NAME        PRIV      CAPS      SELINUX    RUNASUSER   FSGROUP    SUPGROUP   PRIORITY   READONLYROOTFS   VOLUMES
scc-admin   true      []        RunAsAny   RunAsAny    RunAsAny   RunAsAny   <none>     false            [awsElasticBlockStore azureDisk azureFile cephFS cinder configMap downwardAPI emptyDir fc flexVolume flocker gcePersistentDisk gitRepo glusterfs iscsi nfs persistentVolumeClaim photonPersistentDisk quobyte rbd secret vsphere]Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the SCC was created:

Example output

```
NAME        PRIV      CAPS      SELINUX    RUNASUSER   FSGROUP    SUPGROUP   PRIORITY   READONLYROOTFS   VOLUMES
scc-admin   true      []        RunAsAny   RunAsAny    RunAsAny   RunAsAny   <none>     false            [awsElasticBlockStore azureDisk azureFile cephFS cinder configMap downwardAPI emptyDir fc flexVolume flocker gcePersistentDisk gitRepo glusterfs iscsi nfs persistentVolumeClaim photonPersistentDisk quobyte rbd secret vsphere]
```

```
NAME        PRIV      CAPS      SELINUX    RUNASUSER   FSGROUP    SUPGROUP   PRIORITY   READONLYROOTFS   VOLUMES
scc-admin   true      []        RunAsAny   RunAsAny    RunAsAny   RunAsAny   <none>     false            [awsElasticBlockStore azureDisk azureFile cephFS cinder configMap downwardAPI emptyDir fc flexVolume flocker gcePersistentDisk gitRepo glusterfs iscsi nfs persistentVolumeClaim photonPersistentDisk quobyte rbd secret vsphere]
```

## 15.5. Configuring a workload to require a specific SCCCopy linkLink copied to clipboard!

You can configure a workload to require a certain security context constraint (SCC). This is useful in scenarios where you want to pin a specific SCC to the workload or if you want to prevent your required SCC from being preempted by another SCC in the cluster.

To require a specific SCC, set theopenshift.io/required-sccannotation on your workload. You can set this annotation on any resource that can set a pod manifest template, such as a deployment or daemon set.

The SCC must exist in the cluster and must be applicable to the workload, otherwise pod admission fails. An SCC is considered applicable to the workload if the user creating the pod or the pod’s service account hasusepermissions for the SCC in the pod’s namespace.

Do not change theopenshift.io/required-sccannotation in the live pod’s manifest, because doing so causes the pod admission to fail. To change the required SCC, update the annotation in the underlying pod template, which causes the pod to be deleted and re-created.

Prerequisites

- The SCC must exist in the cluster.

Procedure

- Create a YAML file for the deployment and specify a required SCC by setting theopenshift.io/required-sccannotation:Exampledeployment.yamlapiVersion: config.openshift.io/v1
kind: Deployment
apiVersion: apps/v1
spec:
# ...
  template:
    metadata:
      annotations:
        openshift.io/required-scc: "my-scc" 
# ...apiVersion:config.openshift.io/v1kind:DeploymentapiVersion:apps/v1spec:# ...template:metadata:annotations:openshift.io/required-scc:"my-scc"1# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Specify the name of the SCC to require.

Create a YAML file for the deployment and specify a required SCC by setting theopenshift.io/required-sccannotation:

Exampledeployment.yaml

```
apiVersion: config.openshift.io/v1
kind: Deployment
apiVersion: apps/v1
spec:
# ...
  template:
    metadata:
      annotations:
        openshift.io/required-scc: "my-scc" 
# ...
```

```
apiVersion: config.openshift.io/v1
kind: Deployment
apiVersion: apps/v1
spec:
# ...
  template:
    metadata:
      annotations:
        openshift.io/required-scc: "my-scc"
```

```
# ...
```

**1**
  Specify the name of the SCC to require.
- Create the resource by running the following command:oc create -f deployment.yaml$oc create-fdeployment.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the resource by running the following command:

Verification

- Verify that the deployment used the specified SCC:View the value of the pod’sopenshift.io/sccannotation by running the following command:oc get pod <pod_name> -o jsonpath='{.metadata.annotations.openshift\.io\/scc}{"\n"}'$oc get pod<pod_name>-ojsonpath='{.metadata.annotations.openshift\.io\/scc}{"\n"}'1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<pod_name>with the name of your deployment pod.Examine the output and confirm that the displayed SCC matches the SCC that you defined in the deployment:Example outputmy-sccmy-sccCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the deployment used the specified SCC:

- View the value of the pod’sopenshift.io/sccannotation by running the following command:oc get pod <pod_name> -o jsonpath='{.metadata.annotations.openshift\.io\/scc}{"\n"}'$oc get pod<pod_name>-ojsonpath='{.metadata.annotations.openshift\.io\/scc}{"\n"}'1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<pod_name>with the name of your deployment pod.

View the value of the pod’sopenshift.io/sccannotation by running the following command:

**1**
  Replace<pod_name>with the name of your deployment pod.
- Examine the output and confirm that the displayed SCC matches the SCC that you defined in the deployment:Example outputmy-sccmy-sccCopy to ClipboardCopied!Toggle word wrapToggle overflow

Examine the output and confirm that the displayed SCC matches the SCC that you defined in the deployment:

Example output

## 15.6. Role-based access to security context constraintsCopy linkLink copied to clipboard!

You can specify SCCs as resources that are handled by RBAC. This allows you to scope access to your SCCs to a certain project or to the entire cluster. Assigning users, groups, or service accounts directly to an SCC retains cluster-wide scope.

Do not run workloads in or share access to default projects. Default projects are reserved for running core cluster components.

The following default projects are considered highly privileged:default,kube-public,kube-system,openshift,openshift-infra,openshift-node, and other system-created projects that have theopenshift.io/run-levellabel set to0or1. Functionality that relies on admission plugins, such as pod security admission, security context constraints, cluster resource quotas, and image reference resolution, does not work in highly privileged projects.

To include access to SCCs for your role, specify thesccresource when creating a role.

This results in the following role definition:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
...
  name: role-name 
  namespace: namespace 
...
rules:
- apiGroups:
  - security.openshift.io 
  resourceNames:
  - scc-name 
  resources:
  - securitycontextconstraints 
  verbs: 
  - use
```

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
...
  name: role-name
```

```
namespace: namespace
```

```
...
rules:
- apiGroups:
  - security.openshift.io
```

```
resourceNames:
  - scc-name
```

```
resources:
  - securitycontextconstraints
```

```
verbs:
```

```
- use
```

**1**
  The role’s name.

**2**
  Namespace of the defined role. Defaults todefaultif not specified.

**3**
  The API group that includes theSecurityContextConstraintsresource. Automatically defined whensccis specified as a resource.

**4**
  An example name for an SCC you want to have access.

**5**
  Name of the resource group that allows users to specify SCC names in theresourceNamesfield.

**6**
  A list of verbs to apply to the role.

A local or cluster role with such a rule allows the subjects that are bound to it with a role binding or a cluster role binding to use the user-defined SCC calledscc-name.

Because RBAC is designed to prevent escalation, even project administrators are unable to grant access to an SCC. By default, they are not allowed to use the verbuseon SCC resources, including therestricted-v2SCC.

## 15.7. Reference of security context constraints commandsCopy linkLink copied to clipboard!

You can manage security context constraints (SCCs) in your instance as normal API objects by using the OpenShift CLI (oc).

You must havecluster-adminprivileges to manage SCCs.

### 15.7.1. Listing security context constraintsCopy linkLink copied to clipboard!

To get a current list of SCCs:

Example output

```
NAME                              PRIV    CAPS                   SELINUX     RUNASUSER          FSGROUP     SUPGROUP    PRIORITY     READONLYROOTFS   VOLUMES
anyuid                            false   <no value>             MustRunAs   RunAsAny           RunAsAny    RunAsAny    10           false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
hostaccess                        false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","hostPath","persistentVolumeClaim","projected","secret"]
hostmount-anyuid                  false   <no value>             MustRunAs   RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","hostPath","nfs","persistentVolumeClaim","projected","secret"]
hostnetwork                       false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   MustRunAs   <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
hostnetwork-v2                    false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsRange     MustRunAs   MustRunAs   <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
node-exporter                     true    <no value>             RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
nonroot                           false   <no value>             MustRunAs   MustRunAsNonRoot   RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
nonroot-v2                        false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsNonRoot   RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
privileged                        true    ["*"]                  RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
restricted                        false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
restricted-v2                     false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
```

```
NAME                              PRIV    CAPS                   SELINUX     RUNASUSER          FSGROUP     SUPGROUP    PRIORITY     READONLYROOTFS   VOLUMES
anyuid                            false   <no value>             MustRunAs   RunAsAny           RunAsAny    RunAsAny    10           false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
hostaccess                        false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","hostPath","persistentVolumeClaim","projected","secret"]
hostmount-anyuid                  false   <no value>             MustRunAs   RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","hostPath","nfs","persistentVolumeClaim","projected","secret"]
hostnetwork                       false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   MustRunAs   <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
hostnetwork-v2                    false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsRange     MustRunAs   MustRunAs   <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
node-exporter                     true    <no value>             RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
nonroot                           false   <no value>             MustRunAs   MustRunAsNonRoot   RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
nonroot-v2                        false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsNonRoot   RunAsAny    RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
privileged                        true    ["*"]                  RunAsAny    RunAsAny           RunAsAny    RunAsAny    <no value>   false            ["*"]
restricted                        false   <no value>             MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
restricted-v2                     false   ["NET_BIND_SERVICE"]   MustRunAs   MustRunAsRange     MustRunAs   RunAsAny    <no value>   false            ["configMap","downwardAPI","emptyDir","persistentVolumeClaim","projected","secret"]
```

### 15.7.2. Examining security context constraintsCopy linkLink copied to clipboard!

You can view information about a particular SCC, including which users, service accounts, and groups the SCC is applied to.

For example, to examine therestrictedSCC:

Example output

```
Name:                                  restricted
Priority:                              <none>
Access:
  Users:                               <none> 
  Groups:                              <none> 
Settings:
  Allow Privileged:                    false
  Allow Privilege Escalation:          true
  Default Add Capabilities:            <none>
  Required Drop Capabilities:          KILL,MKNOD,SETUID,SETGID
  Allowed Capabilities:                <none>
  Allowed Seccomp Profiles:            <none>
  Allowed Volume Types:                configMap,downwardAPI,emptyDir,persistentVolumeClaim,projected,secret
  Allowed Flexvolumes:                 <all>
  Allowed Unsafe Sysctls:              <none>
  Forbidden Sysctls:                   <none>
  Allow Host Network:                  false
  Allow Host Ports:                    false
  Allow Host PID:                      false
  Allow Host IPC:                      false
  Read Only Root Filesystem:           false
  Run As User Strategy: MustRunAsRange
    UID:                               <none>
    UID Range Min:                     <none>
    UID Range Max:                     <none>
  SELinux Context Strategy: MustRunAs
    User:                              [REDACTED_ACCOUNT]
    Role:                              <none>
    Type:                              <none>
    Level:                             <none>
  FSGroup Strategy: MustRunAs
    Ranges:                            <none>
  Supplemental Groups Strategy: RunAsAny
    Ranges:                            <none>
```

```
Name:                                  restricted
Priority:                              <none>
Access:
  Users:                               <none>
```

```
Groups:                              <none>
```

```
Settings:
  Allow Privileged:                    false
  Allow Privilege Escalation:          true
  Default Add Capabilities:            <none>
  Required Drop Capabilities:          KILL,MKNOD,SETUID,SETGID
  Allowed Capabilities:                <none>
  Allowed Seccomp Profiles:            <none>
  Allowed Volume Types:                configMap,downwardAPI,emptyDir,persistentVolumeClaim,projected,secret
  Allowed Flexvolumes:                 <all>
  Allowed Unsafe Sysctls:              <none>
  Forbidden Sysctls:                   <none>
  Allow Host Network:                  false
  Allow Host Ports:                    false
  Allow Host PID:                      false
  Allow Host IPC:                      false
  Read Only Root Filesystem:           false
  Run As User Strategy: MustRunAsRange
    UID:                               <none>
    UID Range Min:                     <none>
    UID Range Max:                     <none>
  SELinux Context Strategy: MustRunAs
    User:                              [REDACTED_ACCOUNT]
    Role:                              <none>
    Type:                              <none>
    Level:                             <none>
  FSGroup Strategy: MustRunAs
    Ranges:                            <none>
  Supplemental Groups Strategy: RunAsAny
    Ranges:                            <none>
```

**1**
  Lists which users and service accounts the SCC is applied to.

**2**
  Lists which groups the SCC is applied to.

To preserve customized SCCs during upgrades, do not edit settings on the default SCCs.

### 15.7.3. Updating security context constraintsCopy linkLink copied to clipboard!

If your custom SCC no longer satisfies your application workloads requirements, you can update your SCC by using the OpenShift CLI (oc).

To update an existing SCC:

To preserve customized SCCs during upgrades, do not edit settings on the default SCCs.

### 15.7.4. Deleting security context constraintsCopy linkLink copied to clipboard!

If you no longer require your custom SCC, you can delete the SCC by using the OpenShift CLI (oc).

To delete an SCC:

Do not delete default SCCs. If you delete a default SCC, it is regenerated by the Cluster Version Operator.
