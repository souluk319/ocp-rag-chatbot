# 백업 및 복구 운영 플레이북

### Control plane backup and restore operations

As a cluster administrator, you might need to stop an {product-title} cluster for a period and restart it later. Some reasons for restarting a cluster are that you need to perform maintenance on a cluster or want to reduce resource costs. In {product-title}, you can perform a graceful shutdown of a cluster so that you can easily restart the cluster later.

You must back up etcd data before shutting down a cluster; etcd is the key-value store for {product-title}, which persists the state of all resource objects. An etcd backup plays a crucial role in disaster recovery. In {product-title}, you can also replace an unhealthy etcd member.

When you want to get your cluster running again, restart the cluster gracefully.

> A cluster's certificates expire one year after the installation date. You can shut down a cluster and expect it to restart gracefully while the certificates are still valid. Although the cluster automatically retrieves the expired control plane certificates, you must still approve the certificate signing requests (CSRs).

You might run into several situations where {product-title}  does not work as expected, such as:

* You have a cluster that is not functional after the restart because of unexpected conditions, such as node failure or network connectivity issues.
* You have deleted something critical in the cluster by mistake.
* You have lost the majority of your control plane hosts, leading to etcd quorum loss.

You can always recover from a disaster situation by restoring your cluster to its previous state using the saved etcd snapshots.

Additional resources
* Quorum protection with machine lifecycle hooks

### Application backup and restore operations

As a cluster administrator, you can back up and restore applications running on {product-title} by using the OpenShift API for Data Protection (OADP).

OADP backs up and restores Kubernetes resources and internal images, at the granularity of a namespace, by using the version of Velero that is appropriate for the version of OADP you install, according to the table in Downloading the Velero CLI tool.  OADP backs up and restores persistent volumes (PVs) by using snapshots or Restic. For details, see OADP features.

#### OADP requirements

OADP has the following requirements:

* You must be logged in as a user with a `cluster-admin` role.
* You must have object storage for storing backups, such as one of the following storage types:

** OpenShift Data Foundation
** Amazon Web Services
** Microsoft Azure
** {gcp-full}
** S3-compatible object storage
** {ibm-cloud-name} Object Storage S3

* To back up PVs with snapshots, you must have cloud storage that has a native snapshot API or supports Container Storage Interface (CSI) snapshots, such as the following providers:

** Amazon Web Services
** Microsoft Azure
** {gcp-full}
** CSI snapshot-enabled cloud storage, such as Ceph RBD or Ceph FS

> If you do not want to back up PVs by using snapshots, you can use [Restic](https://restic.net/), which is installed by the OADP Operator by default.

#### Backing up and restoring applications

You back up applications by creating a `Backup` custom resource (CR). See Creating a Backup CR. You can configure the following backup options:

* Creating backup hooks to run commands before or after the backup operation

* Scheduling backups

* Backing up applications with File System Backup: Kopia or Restic

* You restore application backups by creating a `Restore` (CR). See Creating a Restore CR.
* You can configure restore hooks to run commands in init containers or in the application container during the restore operation.
