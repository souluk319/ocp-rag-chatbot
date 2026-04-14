# Backup and restore

## Procedure

This procedure details the steps to replace a bare metal etcd member that is unhealthy either because the machine is not running or because the node is not ready.

If you are running installer-provisioned infrastructure or you used the Machine API to create your machines, follow these steps. Otherwise you must create the new control plane node using the same method that was used to originally create it.

Prerequisites

You have identified the unhealthy bare metal etcd member.

You have verified that either the machine is not running or the node is not ready.

You have access to the cluster as a user with the `cluster-admin` role.

You have taken an etcd backup.

Important

You must take an etcd backup before performing this procedure so that your cluster can be restored if you encounter any issues.

Procedure

Verify and remove the unhealthy member.

In a terminal that has access to the cluster as a `cluster-admin` user, run the following command:

```shell-session $ oc -n openshift-etcd get pods -l k8s-app=etcd -o wide ```

```shell-session etcd-openshift-control-plane-0 5/5 Running 11 3h56m 192.168.10.9 openshift-control-plane-0 <none> <none> etcd-openshift-control-plane-1 5/5 Running 0 3h54m 192.168.10.10 openshift-control-plane-1 <none> <none> etcd-openshift-control-plane-2 5/5 Running 0 3h58m 192.168.10.11 openshift-control-plane-2 <none> <none> ```

```shell-session $ oc rsh -n openshift-etcd etcd-openshift-control-plane-0 ```

## Verify

You can verify the OpenShift API for Data Protection (OADP) upgrade by using the following procedure.

Verify that the `DataProtectionApplication` (DPA) has been reconciled successfully:

```shell-session $ oc get dpa dpa-sample -n openshift-adp ```

## Failure Signals

Resolve a partial failure of Restic restore on OpenShift Container Platform 4.14 onward caused by Pod Security Admission (PSA) policy enforcement by adjusting the `restore-resource-priorities` field in your `DataProtectionApplication` (DPA) custom resource (CR). By doing so, you ensure that `SecurityContextConstraints` (SCC) resources are restored before pods. This helps you to complete restore operations successfully when PSA policies deny pod admission due to Velero resource restore order.

From 4.14 onward, OpenShift Container Platform enforces a PSA policy that can hinder the readiness of pods during a Restic restore process. If an SCC resource is not found when a pod is created, and the PSA policy on the pod is not set up to meet the required standards, pod admission is denied.

```plaintext \"level=error\" in line#2273: time=\"2023-06-12T06:50:04Z\" level=error msg=\"error restoring mysql-869f9f44f6-tp5lv: pods\\\ "mysql-869f9f44f6-tp5lv\\\" is forbidden: violates PodSecurity\\\ "restricted:v1.24\\\": privil eged (container \\\"mysql\\\ " must not set securityContext.privileged=true), allowPrivilegeEscalation != false (containers \\\ "restic-wait\\\", \\\"mysql\\\" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (containers \\\ "restic-wait\\\", \\\"mysql\\\" must set securityContext.capabilities.drop=[\\\"ALL\\\"]), seccompProfile (pod or containers \\\ "restic-wait\\\", \\\"mysql\\\" must set securityContext.seccompProfile.type to \\\ "RuntimeDefault\\\" or \\\"Localhost\\\")\" logSource=\"/remote-source/velero/app/pkg/restore/restore.go:1388\" restore=openshift-adp/todolist-backup-0780518c-08ed-11ee-805c-0a580a80e92c\n velero container contains \"level=error\" in line#2447: time=\"2023-06-12T06:50:05Z\" level=error msg=\"Namespace todolist-mariadb, resource restore error: error restoring pods/todolist-mariadb/mysql-869f9f44f6-tp5lv: pods \\\ "mysql-869f9f44f6-tp5lv\\\" is forbidden: violates PodSecurity \\\"restricted:v1.24\\\": privileged (container \\\ "mysql\\\" must not set securityContext.privileged=true), allowPrivilegeEscalation != false (containers \\\ "restic-wait\\\",\\\"mysql\\\" must set securityContext.allowPrivilegeEscalation=false), unrestricted capabilities (containers \\\ "restic-wait\\\", \\\"mysql\\\" must set securityContext.capabilities.drop=[\\\"ALL\\\"]), seccompProfile (pod or containers \\\ "restic-wait\\\", \\\"mysql\\\" must set securityContext.seccompProfile.type to \\\ "RuntimeDefault\\\" or \\\"Localhost\\\")\" logSource=\"/remote-source/velero/app/pkg/controller/restore_controller.go:510\" restore=openshift-adp/todolist-backup-0780518c-08ed-11ee-805c-0a580a80e92c\n]", ```
