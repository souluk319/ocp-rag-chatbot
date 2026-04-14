# Backup and restore

## Overview

The OpenShift API for Data Protection (OADP) product safeguards customer applications on OpenShift Container Platform. It offers comprehensive disaster recovery protection, covering OpenShift Container Platform applications, application-related cluster resources, persistent volumes, and internal images. OADP is also capable of backing up both containerized applications and virtual machines (VMs).

However, OADP does not serve as a disaster recovery solution for `etcd` or OpenShift Operators.

## Architecture

AMD64

ARM64

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
