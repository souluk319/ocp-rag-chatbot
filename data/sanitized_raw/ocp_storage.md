<!-- source: ocp_storage.md -->

# Storage

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/storage/understanding-persistent-storage
---

# Chapter 3. Understanding persistent storage

## 3.1. Persistent storage overviewCopy linkLink copied to clipboard!

Stateful applications deployed in containers require persistent storage. {microshift-short} uses a pre-provisioned storage framework called persistent volumes (PV) to allow node administrators to provision persistent storage. The data inside these volumes can exist beyond the lifecycle of an individual pod. Developers can use persistent volume claims (PVCs) to request storage requirements.

Managing storage is a distinct problem from managing compute resources. OpenShift Container Platform uses the Kubernetes persistent volume (PV) framework to allow cluster administrators to provision persistent storage for a cluster. Developers can use persistent volume claims (PVCs) to request PV resources without having specific knowledge of the underlying storage infrastructure.

PVCs are specific to a project, and are created and used by developers as a means to use a PV. PV resources on their own are not scoped to any single project; they can be shared across the entire OpenShift Container Platform node and claimed from any project. After a PV is bound to a PVC, that PV can not then be bound to additional PVCs. This has the effect of scoping a bound PV to a single namespace, that of the binding project.

PVs are defined by aPersistentVolumeAPI object, which represents a piece of existing storage in the cluster that was either statically provisioned by the cluster administrator or dynamically provisioned using aStorageClassobject. It is a resource in the cluster just like a node is a cluster resource.

PVs are volume plugins likeVolumesbut have a lifecycle that is independent of any individual pod that uses the PV. PV objects capture the details of the implementation of the storage, be that NFS, iSCSI, or a cloud-provider-specific storage system.

High availability of storage in the infrastructure is left to the underlying storage provider.

PVCs are defined by aPersistentVolumeClaimAPI object, which represents a request for storage by a developer. It is similar to a pod in that pods consume node resources and PVCs consume PV resources. For example, pods can request specific levels of resources, such as CPU and memory, while PVCs can request specific storage capacity and access modes. For example, they can be mounted once read-write or many times read-only.

## 3.2. Lifecycle of a volume and claimCopy linkLink copied to clipboard!

PVs are resources in the cluster. PVCs are requests for those resources and also act as claim checks to the resource. The interaction between PVs and PVCs have the following lifecycle.

### 3.2.1. Provision storageCopy linkLink copied to clipboard!

In response to requests from a developer defined in a PVC, a cluster administrator configures one or more dynamic provisioners that provision storage and a matching PV.

Alternatively, a cluster administrator can create a number of PVs in advance that carry the details of the real storage that is available for use. PVs exist in the API and are available for use.

### 3.2.2. Bind claimsCopy linkLink copied to clipboard!

When you create a PVC, you request a specific amount of storage, specify the required access mode, and create a storage class to describe and classify the storage. The control loop in the master watches for new PVCs and binds the new PVC to an appropriate PV. If an appropriate PV does not exist, a provisioner for the storage class creates one.

The size of all PVs might exceed your PVC size. This is especially true with manually provisioned PVs. To minimize the excess, OpenShift Container Platform binds to the smallest PV that matches all other criteria.

Claims remain unbound indefinitely if a matching volume does not exist or can not be created with any available provisioner servicing a storage class. Claims are bound as matching volumes become available. For example, a cluster with many manually provisioned 50Gi volumes would not match a PVC requesting 100Gi. The PVC can be bound when a 100Gi PV is added to the cluster.

### 3.2.3. Use pods and claimed PVsCopy linkLink copied to clipboard!

Pods use claims as volumes. The cluster inspects the claim to find the bound volume and mounts that volume for a pod. For those volumes that support multiple access modes, you must specify which mode applies when you use the claim as a volume in a pod.

Once you have a claim and that claim is bound, the bound PV belongs to you for as long as you need it. You can schedule pods and access claimed PVs by includingpersistentVolumeClaimin the pod’s volumes block.

If you attach persistent volumes that have high file counts to pods, those pods can fail or can take a long time to start. For more information, seeWhen using Persistent Volumes with high file counts in OpenShift, why do pods fail to start or take an excessive amount of time to achieve "Ready" state?.

### 3.2.4. Storage Object in Use ProtectionCopy linkLink copied to clipboard!

The Storage Object in Use Protection feature ensures that PVCs in active use by a pod and PVs that are bound to PVCs are not removed from the system, as this can result in data loss.

Storage Object in Use Protection is enabled by default.

A PVC is in active use by a pod when aPodobject exists that uses the PVC.

If a user deletes a PVC that is in active use by a pod, the PVC is not removed immediately. PVC removal is postponed until the PVC is no longer actively used by any pods. Also, if a cluster admin deletes a PV that is bound to a PVC, the PV is not removed immediately. PV removal is postponed until the PV is no longer bound to a PVC.

### 3.2.5. Release a persistent volumeCopy linkLink copied to clipboard!

When you are finished with a volume, you can delete the PVC object from the API, which allows reclamation of the resource. The volume is considered released when the claim is deleted, but it is not yet available for another claim. The previous claimant’s data remains on the volume and must be handled according to policy.

### 3.2.6. Reclaim policy for persistent volumesCopy linkLink copied to clipboard!

The reclaim policy of a persistent volume tells the cluster what to do with the volume after it is released. A volume’s reclaim policy can beRetain,Recycle, orDelete.

- Retainreclaim policy allows manual reclamation of the resource for those volume plugins that support it.
- Recyclereclaim policy recycles the volume back into the pool of unbound persistent volumes once it is released from its claim.

TheRecyclereclaim policy is deprecated in OpenShift Container Platform 4. Dynamic provisioning is recommended for equivalent and better functionality.

- Deletereclaim policy deletes both thePersistentVolumeobject from OpenShift Container Platform and the associated storage asset in external infrastructure, such as Amazon Elastic Block Store (Amazon EBS) or VMware vSphere.

Dynamically provisioned volumes are always deleted.

### 3.2.7. Reclaiming a persistent volume manuallyCopy linkLink copied to clipboard!

When a persistent volume claim (PVC) is deleted, the persistent volume (PV) still exists and is considered "released". However, the PV is not yet available for another claim because the data of the previous claimant remains on the volume.

Procedure

To manually reclaim the PV as a cluster administrator:

- Delete the PV by running the following command:oc delete pv <pv_name>$oc deletepv<pv_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowThe associated storage asset in the external infrastructure, such as an AWS EBS, GCE PD, Azure Disk, or Cinder volume, still exists after the PV is deleted.

Delete the PV by running the following command:

The associated storage asset in the external infrastructure, such as an AWS EBS, GCE PD, Azure Disk, or Cinder volume, still exists after the PV is deleted.

- Clean up the data on the associated storage asset.
- Delete the associated storage asset. Alternately, to reuse the same storage asset, create a new PV with the storage asset definition.

The reclaimed PV is now available for use by another PVC.

### 3.2.8. Changing the reclaim policy of a persistent volumeCopy linkLink copied to clipboard!

You can change the reclaim policy of a persistent volume.

Procedure

- List the persistent volumes in your cluster:oc get pv$oc getpvCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim3    manual                     3sNAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim3    manual                     3sCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the persistent volumes in your cluster:

Example output

```
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim3    manual                     3s
```

```
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim3    manual                     3s
```

- Choose one of your persistent volumes and change its reclaim policy:oc patch pv <your-pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'$oc patchpv<your-pv-name>-p'{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Choose one of your persistent volumes and change its reclaim policy:

- Verify that your chosen persistent volume has the right policy:oc get pv$oc getpvCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Retain          Bound     default/claim3    manual                     3sNAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Retain          Bound     default/claim3    manual                     3sCopy to ClipboardCopied!Toggle word wrapToggle overflowIn the preceding output, the volume bound to claimdefault/claim3now has aRetainreclaim policy. The volume will not be automatically deleted when a user deletes claimdefault/claim3.

Verify that your chosen persistent volume has the right policy:

Example output

```
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Retain          Bound     default/claim3    manual                     3s
```

```
NAME                                       CAPACITY   ACCESSMODES   RECLAIMPOLICY   STATUS    CLAIM             STORAGECLASS     REASON    AGE
 pvc-b6efd8da-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim1    manual                     10s
 pvc-b95650f8-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Delete          Bound     default/claim2    manual                     6s
 pvc-bb3ca71d-b7b5-11e6-9d58-0ed433a7dd94   4Gi        RWO           Retain          Bound     default/claim3    manual                     3s
```

In the preceding output, the volume bound to claimdefault/claim3now has aRetainreclaim policy. The volume will not be automatically deleted when a user deletes claimdefault/claim3.

## 3.3. Persistent volumesCopy linkLink copied to clipboard!

Each PV contains aspecandstatus, which is the specification and status of the volume, for example:

PersistentVolumeobject definition example

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001 
spec:
  capacity:
    storage: 5Gi 
  accessModes:
    - ReadWriteOnce 
  persistentVolumeReclaimPolicy: Retain 
  ...
status:
  ...
```

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
```

```
spec:
  capacity:
    storage: 5Gi
```

```
accessModes:
    - ReadWriteOnce
```

```
persistentVolumeReclaimPolicy: Retain
```

```
...
status:
  ...
```

**1**
  Name of the persistent volume.

**2**
  The amount of storage available to the volume.

**3**
  The access mode, defining the read-write and mount permissions.

**4**
  The reclaim policy, indicating how the resource should be handled once it is released.

### 3.3.1. Types of PVsCopy linkLink copied to clipboard!

OpenShift Container Platform supports the following persistent volume plugins:

- AWS Elastic Block Store (EBS)
- AWS Elastic File Store (EFS)
- Azure Disk
- Azure File
- Cinder
- Fibre Channel
- GCP Persistent Disk
- GCP Filestore
- IBM Power Virtual Server Block
- IBM Cloud® VPC Block
- HostPath
- iSCSI
- Local volume
- LVM Storage
- NFS
- OpenStack Manila
- Red Hat OpenShift Data Foundation
- CIFS/SMB
- VMware vSphere

### 3.3.2. CapacityCopy linkLink copied to clipboard!

Generally, a persistent volume (PV) has a specific storage capacity. This is set by using thecapacityattribute of the PV.

Currently, storage capacity is the only resource that can be set or requested. Future attributes may include IOPS, throughput, and so on.

### 3.3.3. Access modesCopy linkLink copied to clipboard!

A persistent volume can be mounted on a host in any way supported by the resource provider. Providers have different capabilities and each PV’s access modes are set to the specific modes supported by that particular volume. For example, NFS can support multiple read-write clients, but a specific NFS PV might be exported on the server as read-only. Each PV gets its own set of access modes describing that specific PV’s capabilities.

Claims are matched to volumes with similar access modes. The only two matching criteria are access modes and size. A claim’s access modes represent a request. Therefore, you might be granted more, but never less. For example, if a claim requests RWO, but the only volume available is an NFS PV (RWO+ROX+RWX), the claim would then match NFS because it supports RWO.

Direct matches are always attempted first. The volume’s modes must match or contain more modes than you requested. The size must be greater than or equal to what is expected. If two types of volumes, such as NFS and iSCSI, have the same set of access modes, either of them can match a claim with those modes. There is no ordering between types of volumes and no way to choose one type over another.

All volumes with the same modes are grouped, and then sorted by size, smallest to largest. The binder gets the group with matching modes and iterates over each, in size order, until one size matches.

Volume access modes describe volume capabilities. They are not enforced constraints. The storage provider is responsible for runtime errors resulting from invalid use of the resource. Errors in the provider show up at runtime as mount errors.

For example, NFS offersReadWriteOnceaccess mode. If you want to use the volume’s ROX capability, mark the claims asReadOnlyMany.

iSCSI and Fibre Channel volumes do not currently have any fencing mechanisms. You must ensure the volumes are only used by one node at a time. In certain situations, such as draining a node, the volumes can be used simultaneously by two nodes. Before draining the node, delete the pods that use the volumes.

The following table lists the access modes:

| Access Mode | CLI abbreviation | Description |
| --- | --- | --- |
| ReadWriteOnce | RWO | The volume can be mounted as read-write by a single node. |
| ReadWriteOncePod[1] | RWOP | The volume can be mounted as read-write by a single pod on a single node. |
| ReadOnlyMany | ROX | The volume can be mounted as read-only by many nodes. |
| ReadWriteMany | RWX | The volume can be mounted as read-write by many nodes. |

ReadWriteOnce

RWO

The volume can be mounted as read-write by a single node.

ReadWriteOncePod[1]

RWOP

The volume can be mounted as read-write by a single pod on a single node.

ReadOnlyMany

ROX

The volume can be mounted as read-only by many nodes.

ReadWriteMany

RWX

The volume can be mounted as read-write by many nodes.

- RWOP uses the SELinux mount feature. This feature is driver dependent, and enabled by default in ODF, AWS EBS, Azure Disk, GCP PD, IBM Cloud Block Storage volume, Cinder, and vSphere. For third-party drivers, please contact your storage vendor.
| Volume plugin | ReadWriteOnce[1] | ReadWriteOncePod | ReadOnlyMany | ReadWriteMany |
| --- | --- | --- | --- | --- |
| AWS EBS[2] | ✅ | ✅ |  |  |
| AWS EFS | ✅ | ✅ | ✅ | ✅ |
| Azure File | ✅ | ✅ | ✅ | ✅ |
| Azure Disk | ✅ | ✅ |  |  |
| CIFS/SMB | ✅ | ✅ | ✅ | ✅ |
| Cinder | ✅ | ✅ |  |  |
| Fibre Channel | ✅ | ✅ | ✅ | ✅[3] |
| GCP Persistent Disk | ✅ | ✅ |  |  |
| GCP Filestore | ✅ | ✅ | ✅ | ✅ |
| HostPath | ✅ | ✅ |  |  |
| IBM Power Virtual Server Disk | ✅ | ✅ | ✅ | ✅ |
| IBM Cloud® VPC Disk | ✅ | ✅ |  |  |
| iSCSI | ✅ | ✅ | ✅ | ✅[3] |
| Local volume | ✅ | ✅ |  |  |
| LVM Storage | ✅ | ✅ |  |  |
| NFS | ✅ | ✅ | ✅ | ✅ |
| OpenStack Manila |  | ✅ |  | ✅ |
| Red Hat OpenShift Data Foundation | ✅ | ✅ |  | ✅ |
| VMware vSphere | ✅ | ✅ |  | ✅[4] |

AWS EBS[2]

✅

✅

AWS EFS

✅

✅

✅

✅

Azure File

✅

✅

✅

✅

Azure Disk

✅

✅

CIFS/SMB

✅

✅

✅

✅

Cinder

✅

✅

Fibre Channel

✅

✅

✅

✅[3]

GCP Persistent Disk

✅

✅

GCP Filestore

✅

✅

✅

✅

HostPath

✅

✅

IBM Power Virtual Server Disk

✅

✅

✅

✅

IBM Cloud® VPC Disk

✅

✅

iSCSI

✅

✅

✅

✅[3]

Local volume

✅

✅

LVM Storage

✅

✅

NFS

✅

✅

✅

✅

OpenStack Manila

✅

✅

Red Hat OpenShift Data Foundation

✅

✅

✅

VMware vSphere

✅

✅

✅[4]

- ReadWriteOnce (RWO) volumes cannot be mounted on multiple nodes. If a node fails, the system does not allow the attached RWO volume to be mounted on a new node because it is already assigned to the failed node. If you encounter a multi-attach error message as a result, force delete the pod on a shutdown or crashed node to avoid data loss in critical workloads, such as when dynamic persistent volumes are attached.
- Use a recreate deployment strategy for pods that rely on AWS EBS.
- Only raw block volumes support the ReadWriteMany (RWX) access mode for Fibre Channel and iSCSI. For more information, see "Block volume support".
- If the underlying vSphere environment supports the vSAN file service, then the vSphere Container Storage Interface (CSI) Driver Operator installed by OpenShift Container Platform supports provisioning of ReadWriteMany (RWX) volumes. If you do not have vSAN file service configured, and you request RWX, the volume fails to get created and an error is logged. For more information, see "Using Container Storage Interface""VMware vSphere CSI Driver Operator".

### 3.3.4. PhaseCopy linkLink copied to clipboard!

Volumes can be found in one of the following phases:

| Phase | Description |
| --- | --- |
| Available | A free resource not yet bound to a claim. |
| Bound | The volume is bound to a claim. |
| Released | The claim was deleted, but the resource is not yet reclaimed by the cluster. |
| Failed | The volume has failed its automatic reclamation. |

Available

A free resource not yet bound to a claim.

Bound

The volume is bound to a claim.

Released

The claim was deleted, but the resource is not yet reclaimed by the cluster.

Failed

The volume has failed its automatic reclamation.

You can view the name of the PVC that is bound to the PV by running the following command:

#### 3.3.4.1. Mount optionsCopy linkLink copied to clipboard!

You can specify mount options while mounting a PV by using the attributemountOptions.

For example:

Mount options example

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  mountOptions: 
    - nfsvers=4.1
  nfs:
    path: /tmp
    server: [REDACTED_PRIVATE_IP]
  persistentVolumeReclaimPolicy: Retain
  claimRef:
    name: claim1
    namespace: default
```

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv0001
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  mountOptions:
```

```
- nfsvers=4.1
  nfs:
    path: /tmp
    server: [REDACTED_PRIVATE_IP]
  persistentVolumeReclaimPolicy: Retain
  claimRef:
    name: claim1
    namespace: default
```

**1**
  Specified mount options are used while mounting the PV to the disk.

The following PV types support mount options:

- AWS Elastic Block Store (EBS)
- Azure Disk
- Azure File
- Cinder
- GCE Persistent Disk
- iSCSI
- Local volume
- NFS
- Red Hat OpenShift Data Foundation (Ceph RBD only)
- CIFS/SMB
- VMware vSphere

Fibre Channel and HostPath PVs do not support mount options.

## 3.4. Persistent volume claimsCopy linkLink copied to clipboard!

To define storage requirements for your workloads, review the structure of aPersistentVolumeClaim(PVC). This object includes aspecfield to configure the request and astatusfield to monitor the current state of the claim.

PersistentVolumeClaimobject definition example

```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myclaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
  storageClassName: gold
status:
# ...
```

```
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: myclaim
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 8Gi
  storageClassName: gold
status:
# ...
```

where:

**apiVersion**
  Specifies the name of the PVC.

**spec.accessModes**
  Specifies the access mode, defining the read/write and mount permissions.

**requests.storage**
  Specifies the amount of storage available to the PVC.

**storageClassName**
  Specifies the name of theStorageClassrequired by the claim.

## 3.5. Block volume supportCopy linkLink copied to clipboard!

OpenShift Container Platform can statically provision raw block volumes. These volumes do not have a file system, and can provide performance benefits for applications that either write to the disk directly or implement their own storage service.

Raw block volumes are provisioned by specifyingvolumeMode: Blockin the PV and PVC specification.

Pods using raw block volumes must be configured to allow privileged containers.

The following table displays which volume plugins support block volumes.

| Volume Plugin | Manually provisioned | Dynamically provisioned | Fully supported |
| --- | --- | --- | --- |
| Amazon Elastic Block Store (Amazon EBS) | ✅ | ✅ | ✅ |
| Amazon Elastic File Storage (Amazon EFS) |  |  |  |
| Azure Disk | ✅ | ✅ | ✅ |
| Azure File |  |  |  |
| Cinder | ✅ | ✅ | ✅ |
| Fibre Channel | ✅ |  | ✅ |
| GCP | ✅ | ✅ | ✅ |
| HostPath |  |  |  |
| IBM Cloud Block Storage volume | ✅ | ✅ | ✅ |
| iSCSI | ✅ |  | ✅ |
| Local volume | ✅ |  | ✅ |
| LVM Storage | ✅ | ✅ | ✅ |
| NFS |  |  |  |
| Red Hat OpenShift Data Foundation | ✅ | ✅ | ✅ |
| CIFS/SMB |  |  |  |
| VMware vSphere | ✅ | ✅ | ✅ |

Amazon Elastic Block Store (Amazon EBS)

✅

✅

✅

Amazon Elastic File Storage (Amazon EFS)

Azure Disk

✅

✅

✅

Azure File

Cinder

✅

✅

✅

Fibre Channel

✅

✅

GCP

✅

✅

✅

HostPath

IBM Cloud Block Storage volume

✅

✅

✅

iSCSI

✅

✅

Local volume

✅

✅

LVM Storage

✅

✅

✅

NFS

Red Hat OpenShift Data Foundation

✅

✅

✅

CIFS/SMB

VMware vSphere

✅

✅

✅

Using any of the block volumes that can be provisioned manually, but are not provided as fully supported, is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

### 3.5.1. Block volume examplesCopy linkLink copied to clipboard!

PV example

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: block-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  volumeMode: Block 
  persistentVolumeReclaimPolicy: Retain
  fc:
    targetWWNs: ["50060e801049cfd1"]
    lun: 0
    readOnly: false
```

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: block-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  volumeMode: Block
```

```
persistentVolumeReclaimPolicy: Retain
  fc:
    targetWWNs: ["50060e801049cfd1"]
    lun: 0
    readOnly: false
```

**1**
  volumeModemust be set toBlockto indicate that this PV is a raw block volume.

PVC example

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block 
  resources:
    requests:
      storage: 10Gi
```

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: block-pvc
spec:
  accessModes:
    - ReadWriteOnce
  volumeMode: Block
```

```
resources:
    requests:
      storage: 10Gi
```

**1**
  volumeModemust be set toBlockto indicate that a raw block PVC is requested.

Podspecification example

```
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-block-volume
spec:
  containers:
    - name: fc-container
      image: fedora:26
      command: ["/bin/sh", "-c"]
      args: [ "tail -f /dev/null" ]
      volumeDevices:  
        - name: data
          devicePath: /dev/xvda 
  volumes:
    - name: data
      persistentVolumeClaim:
        claimName: block-pvc
```

```
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-block-volume
spec:
  containers:
    - name: fc-container
      image: fedora:26
      command: ["/bin/sh", "-c"]
      args: [ "tail -f /dev/null" ]
      volumeDevices:
```

```
- name: data
          devicePath: /dev/xvda
```

```
volumes:
    - name: data
      persistentVolumeClaim:
        claimName: block-pvc
```

**1**
  volumeDevices, instead ofvolumeMounts, is used for block devices. OnlyPersistentVolumeClaimsources can be used with raw block volumes.

**2**
  devicePath, instead ofmountPath, represents the path to the physical device where the raw block is mapped to the system.

**3**
  The volume source must be of typepersistentVolumeClaimand must match the name of the PVC as expected.
| Value | Default |
| --- | --- |
| Filesystem | Yes |
| Block | No |

Filesystem

Yes

Block

No

| PVvolumeMode | PVCvolumeMode | Binding result |
| --- | --- | --- |
| Filesystem | Filesystem | Bind |
| Unspecified | Unspecified | Bind |
| Filesystem | Unspecified | Bind |
| Unspecified | Filesystem | Bind |
| Block | Block | Bind |
| Unspecified | Block | No Bind |
| Block | Unspecified | No Bind |
| Filesystem | Block | No Bind |
| Block | Filesystem | No Bind |

Filesystem

Filesystem

Bind

Unspecified

Unspecified

Bind

Filesystem

Unspecified

Bind

Unspecified

Filesystem

Bind

Block

Block

Bind

Unspecified

Block

No Bind

Block

Unspecified

No Bind

Filesystem

Block

No Bind

Block

Filesystem

No Bind

Unspecified values result in the default value ofFilesystem.

## 3.6. Reduce pod timeouts by using fsGroupCopy linkLink copied to clipboard!

To reduce pod timeouts when using a storage volume with many files, configure thefsGroupfield. By specifying this field, you can manage how file ownership and permissions are applied, preventing delays caused by the default recursive permission changes on large volumes.

If a storage volume contains many files (~1,000,000 or greater), you may experience pod timeouts.

This can occur because, by default, OpenShift Container Platform recursively changes ownership and permissions for the contents of each volume to match thefsGroupspecified in thesecurityContextof the pod when that volume is mounted. For volumes with many files, checking and changing ownership and permissions can be time consuming, slowing pod startup. You can use thefsGroupChangePolicyfield inside asecurityContextto control the way that OpenShift Container Platform checks and manages ownership and permissions for a volume.

fsGroupChangePolicydefines behavior for changing ownership and permission of the volume before being exposed inside a pod. This field only applies to volume types that supportfsGroup-controlled ownership and permissions. This field has two possible values:

- OnRootMismatch: Only change permissions and ownership if permission and ownership of root directory does not match with expected permissions of the volume. This can help shorten the time it takes to change ownership and permission of a volume to reduce pod timeouts.
- Always: Always change permission and ownership of the volume when a volume is mounted.

fsGroupChangePolicyexample

```
securityContext:
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  fsGroupChangePolicy: "OnRootMismatch" 
  ...
```

```
securityContext:
  runAsUser: 1000
  runAsGroup: 3000
  fsGroup: 2000
  fsGroupChangePolicy: "OnRootMismatch"
```

```
...
```

**1**
  OnRootMismatchspecifies skipping recursive permission change, thus helping to avoid pod timeout problems.

The fsGroupChangePolicyfield has no effect on ephemeral volume types, such as secret, configMap, and emptydir.
