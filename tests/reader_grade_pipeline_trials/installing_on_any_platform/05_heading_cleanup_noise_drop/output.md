# Installing on any platform

## Overview

This document describes how to install OpenShift Container Platform on any platform.

## Architecture

You can install RHCOS by running at the command prompt, after booting into the RHCOS live environment from an ISO image.

```shell coreos-installer install <options> <device> ```

## Procedure

To add machines to a cluster, verify the status of the certificate signing requests (CSRs) generated for each machine. If manual approval is required, approve the client requests first, followed by the server requests.

Prerequisites

You added machines to your cluster.

Procedure

```shell-session $ oc get nodes ```

```shell-session NAME STATUS ROLES AGE VERSION master-0 Ready master 63m v1.33.4 master-1 Ready master 63m v1.33.4 master-2 Ready master 64m v1.33.4 ```

The output lists all of the machines that you created.

Note

The preceding output might not include the compute nodes, also known as worker nodes, until some CSRs are approved.

Review the pending CSRs and ensure that you see the client requests with the `Pending` or `Approved` status for each machine that you added to the cluster:

```shell-session $ oc get csr ```

```shell-session NAME AGE REQUESTOR CONDITION csr-8b2br 15m system:serviceaccount:openshift-machine-config-operator:node-bootstrapper Pending csr-8vnps 15m system:serviceaccount:openshift-machine-config-operator:node-bootstrapper Pending ... ```

In this example, two machines are joining the cluster. You might see more approved CSRs in the list.

If the CSRs were not approved, after all of the pending CSRs for the machines you added are in `Pending` status, approve the CSRs for your cluster machines:

Because the CSRs rotate automatically, approve your CSRs within an hour of adding the machines to the cluster. If you do not approve them within an hour, the certificates will rotate, and more than two certificates will be present for each node. You must approve all of these certificates. After the client CSR is approved, the Kubelet creates a secondary CSR for the serving certificate, which requires manual approval. Then, subsequent serving certificate renewal requests are automatically approved by the `machine-approver` if the Kubelet requests a new certificate with identical parameters.

For clusters running on platforms that are not machine API enabled, such as bare metal and other user-provisioned infrastructure, you must implement a method of automatically approving the kubelet serving certificate requests (CSRs). If a request is not approved, then the,, and commands cannot succeed, because a serving certificate is required when the API server connects to the kubelet. Any operation that contacts the Kubelet endpoint requires this certificate approval to be in place. The method must watch for new CSRs, confirm that the CSR was submitted by the `node-bootstrapper` service account in the `system:node` or `system:admin` groups, and confirm the identity of the node.
