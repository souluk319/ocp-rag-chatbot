<!-- source: ocp_must_gather.md -->

# Troubleshooting - Data Gathering

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/support/gathering-cluster-data
---

# Chapter 5. Gathering data about your cluster

When opening a support case, it is helpful to provide debugging information about your cluster to Red Hat Support.

It is recommended to provide:

- Data gathered using theoc adm must-gathercommand
- Theunique cluster ID

## 5.1. About the must-gather toolCopy linkLink copied to clipboard!

Theoc adm must-gatherCLI command collects the information from your cluster that is most likely needed for debugging issues, including:

- Resource definitions
- Service logs

By default, theoc adm must-gathercommand uses the default plugin image and writes into./must-gather.local.

Alternatively, you can collect specific information by running the command with the appropriate arguments as described in the following sections:

- To collect data related to one or more specific features, use the--imageargument with an image, as listed in a following section.For example:oc adm must-gather \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43$oc adm must-gather\--image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43Copy to ClipboardCopied!Toggle word wrapToggle overflowTo collect the audit logs, use the-- /usr/bin/gather_audit_logsargument, as described in a following section.For example:oc adm must-gather -- /usr/bin/gather_audit_logs$oc adm must-gather -- /usr/bin/gather_audit_logsCopy to ClipboardCopied!Toggle word wrapToggle overflowAudit logs are not collected as part of the default set of information to reduce the size of the files.On a Windows operating system, install thecwRsyncclient and add to thePATHvariable for use with theoc rsynccommand.

To collect data related to one or more specific features, use the--imageargument with an image, as listed in a following section.

For example:

```
oc adm must-gather \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

```
$ oc adm must-gather \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

- To collect the audit logs, use the-- /usr/bin/gather_audit_logsargument, as described in a following section.For example:oc adm must-gather -- /usr/bin/gather_audit_logs$oc adm must-gather -- /usr/bin/gather_audit_logsCopy to ClipboardCopied!Toggle word wrapToggle overflowAudit logs are not collected as part of the default set of information to reduce the size of the files.On a Windows operating system, install thecwRsyncclient and add to thePATHvariable for use with theoc rsynccommand.

To collect the audit logs, use the-- /usr/bin/gather_audit_logsargument, as described in a following section.

For example:

- Audit logs are not collected as part of the default set of information to reduce the size of the files.
- On a Windows operating system, install thecwRsyncclient and add to thePATHvariable for use with theoc rsynccommand.

When you runoc adm must-gather, a new pod with a random name is created in a new project on the cluster. The data is collected on that pod and saved in a new directory that starts withmust-gather.localin the current working directory.

For example:

```
NAMESPACE                      NAME                 READY   STATUS      RESTARTS      AGE
...
openshift-must-gather-5drcj    must-gather-bklx4    2/2     Running     0             72s
openshift-must-gather-5drcj    must-gather-s8sdh    2/2     Running     0             72s
...
```

```
NAMESPACE                      NAME                 READY   STATUS      RESTARTS      AGE
...
openshift-must-gather-5drcj    must-gather-bklx4    2/2     Running     0             72s
openshift-must-gather-5drcj    must-gather-s8sdh    2/2     Running     0             72s
...
```

Optionally, you can run theoc adm must-gathercommand in a specific namespace by using the--run-namespaceoption.

For example:

```
oc adm must-gather --run-namespace <namespace> \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

```
$ oc adm must-gather --run-namespace <namespace> \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

### 5.1.1. Gathering data about your cluster for Red Hat SupportCopy linkLink copied to clipboard!

You can gather debugging information about your cluster by using theoc adm must-gatherCLI command.

If you are gathering information to debug a self-managed hosted cluster, see "Gathering information to troubleshoot hosted control planes".

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- The OpenShift Container Platform CLI (oc) is installed.

Procedure

- Navigate to the directory where you want to store themust-gatherdata.If your cluster is in a disconnected environment, you must take additional steps. If your mirror registry has a trusted CA, you must first add the trusted CA to the cluster. For all clusters in disconnected environments, you must import the defaultmust-gatherimage as an image stream.oc import-image is/must-gather -n openshift$oc import-image is/must-gather-nopenshiftCopy to ClipboardCopied!Toggle word wrapToggle overflow

Navigate to the directory where you want to store themust-gatherdata.

If your cluster is in a disconnected environment, you must take additional steps. If your mirror registry has a trusted CA, you must first add the trusted CA to the cluster. For all clusters in disconnected environments, you must import the defaultmust-gatherimage as an image stream.

- Run theoc adm must-gathercommand:oc adm must-gather$oc adm must-gatherCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you are in a disconnected environment, use the--imageflag as part of must-gather and point to the payload image.Because this command picks a random control plane node by default, the pod might be scheduled to a control plane node that is in theNotReadyandSchedulingDisabledstate.If this command fails, for example, if you cannot schedule a pod on your cluster, then use theoc adm inspectcommand to gather information for particular resources.Contact Red Hat Support for the recommended resources to gather.

Run theoc adm must-gathercommand:

If you are in a disconnected environment, use the--imageflag as part of must-gather and point to the payload image.

Because this command picks a random control plane node by default, the pod might be scheduled to a control plane node that is in theNotReadyandSchedulingDisabledstate.

- If this command fails, for example, if you cannot schedule a pod on your cluster, then use theoc adm inspectcommand to gather information for particular resources.Contact Red Hat Support for the recommended resources to gather.

If this command fails, for example, if you cannot schedule a pod on your cluster, then use theoc adm inspectcommand to gather information for particular resources.

Contact Red Hat Support for the recommended resources to gather.

- Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:tar cvaf must-gather-`date +"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz <must_gather_local_dir>$tarcvaf must-gather-`date+"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz<must_gather_local_dir>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<must_gather_local_dir>with the actual directory name.

Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:

**1**
  Replace<must_gather_local_dir>with the actual directory name.
- Attach the compressed file to your support case on thetheCustomer Supportpageof the Red Hat Customer Portal.

### 5.1.2. Must-gather flagsCopy linkLink copied to clipboard!

The flags listed in the following table are available to use with theoc adm must-gathercommand.

| Flag | Example command | Description |
| --- | --- | --- |
| --all-images | oc adm must-gather --all-images=false | Collectmust-gatherdata by using the default image for all Operators on the cluster that are annotate |
| --dest-dir | oc adm must-gather --dest-dir='<directory_name>' | Set a specific directory on the local machine where the gathered data is written. |
| --host-network | oc adm must-gather --host-network=false | Runmust-gatherpods ashostNetwork: true. Relevant if a specific command and image needs to capture ho |
| --image | oc adm must-gather --image=[<plugin_image>] | Specify amust-gatherplugin image to run. If not specified, OpenShift Container Platform’s defaultmus |
| --image-stream | oc adm must-gather --image-stream=[<image_stream>] | Specify an`<image_stream>` using a namespace or name:tag value containing amust-gatherplugin image t |
| --node-name | oc adm must-gather --node-name='<node>' | Set a specific node to use. If not specified, by default a random master is used. |
| --node-selector | oc adm must-gather --node-selector='<node_selector_name>' | Set a specific node selector to use. Only relevant when specifying a command and image which needs t |
| --run-namespace | oc adm must-gather --run-namespace='<namespace>' | An existing privileged namespace wheremust-gatherpods should run. If not specified, a temporary name |
| --since | oc adm must-gather --since=<time> | Only return logs newer than the specified duration. Defaults to all logs. Plugins are encouraged but |
| --since-time | oc adm must-gather --since-time='<date_and_time>' | Only return logs after a specific date and time, expressed in (RFC3339) format. Defaults to all logs |
| --source-dir | oc adm must-gather --source-dir='/<directory_name>/' | Set the specific directory on the pod where you copy the gathered data from. |
| --timeout | oc adm must-gather --timeout='<time>' | The length of time to gather data before timing out, expressed as seconds, minutes, or hours, for ex |
| --volume-percentage | oc adm must-gather --volume-percentage=<percent> | Specify maximum percentage of pod’s allocated volume that can be used formust-gather. If this limit  |

--all-images

oc adm must-gather --all-images=false

Collectmust-gatherdata by using the default image for all Operators on the cluster that are annotated withoperators.openshift.io/must-gather-image.

--dest-dir

oc adm must-gather --dest-dir='<directory_name>'

Set a specific directory on the local machine where the gathered data is written.

--host-network

oc adm must-gather --host-network=false

Runmust-gatherpods ashostNetwork: true. Relevant if a specific command and image needs to capture host-level data.

--image

oc adm must-gather --image=[<plugin_image>]

Specify amust-gatherplugin image to run. If not specified, OpenShift Container Platform’s defaultmust-gatherimage is used.

--image-stream

oc adm must-gather --image-stream=[<image_stream>]

Specify an`<image_stream>` using a namespace or name:tag value containing amust-gatherplugin image to run.

--node-name

oc adm must-gather --node-name='<node>'

Set a specific node to use. If not specified, by default a random master is used.

--node-selector

oc adm must-gather --node-selector='<node_selector_name>'

Set a specific node selector to use. Only relevant when specifying a command and image which needs to capture data on a set of cluster nodes simultaneously.

--run-namespace

oc adm must-gather --run-namespace='<namespace>'

An existing privileged namespace wheremust-gatherpods should run. If not specified, a temporary namespace is generated.

--since

oc adm must-gather --since=<time>

Only return logs newer than the specified duration. Defaults to all logs. Plugins are encouraged but not required to support this. Only onesince-timeorsincemay be used.

--since-time

oc adm must-gather --since-time='<date_and_time>'

Only return logs after a specific date and time, expressed in (RFC3339) format. Defaults to all logs. Plugins are encouraged but not required to support this. Only onesince-timeorsincemay be used.

--source-dir

oc adm must-gather --source-dir='/<directory_name>/'

Set the specific directory on the pod where you copy the gathered data from.

--timeout

oc adm must-gather --timeout='<time>'

The length of time to gather data before timing out, expressed as seconds, minutes, or hours, for example, 3s, 5m, or 2h. Time specified must be higher than zero. Defaults to 10 minutes if not specified.

--volume-percentage

oc adm must-gather --volume-percentage=<percent>

Specify maximum percentage of pod’s allocated volume that can be used formust-gather. If this limit is exceeded,must-gatherstops gathering, but still copies gathered data. Defaults to 30% if not specified.

### 5.1.3. Gathering data about specific featuresCopy linkLink copied to clipboard!

You can gather debugging information about specific features by using theoc adm must-gatherCLI command with the--imageor--image-streamargument. Themust-gathertool supports multiple images, so you can gather data about more than one feature by running a single command.

| Image | Purpose |
| --- | --- |
| registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43 | Data collection for OpenShift Virtualization. |
| registry.redhat.io/openshift-serverless-1/svls-must-gather-rhel8 | Data collection for OpenShift Serverless. |
| registry.redhat.io/openshift-service-mesh/istio-must-gather-rhel8:<installed_version_service_mesh> | Data collection for Red Hat OpenShift Service Mesh. |
| registry.redhat.io/multicluster-engine/must-gather-rhel8 | Data collection for hosted control planes. |
| registry.redhat.io/rhmtc/openshift-migration-must-gather-rhel8:v<installed_version_migration_toolkit | Data collection for the Migration Toolkit for Containers. |
| registry.redhat.io/odf4/odf-must-gather-rhel9:v<installed_version_ODF> | Data collection for Red Hat OpenShift Data Foundation. |
| registry.redhat.io/openshift-logging/cluster-logging-rhel9-operator:v<installed_version_logging> | Data collection for logging. |
| quay.io/netobserv/must-gather | Data collection for the Network Observability Operator. |
| registry.redhat.io/openshift4/ose-csi-driver-shared-resource-mustgather-rhel8 | Data collection for OpenShift Shared Resource CSI Driver. |
| registry.redhat.io/openshift4/ose-local-storage-mustgather-rhel9:v<installed_version_LSO> | Data collection for Local Storage Operator. |
| registry.redhat.io/openshift-sandboxed-containers/osc-must-gather-rhel8:v<installed_version_sandboxe | Data collection for OpenShift sandboxed containers. |
| registry.redhat.io/workload-availability/node-healthcheck-must-gather-rhel8:v<installed_version_NHC> | Data collection for the Red Hat Workload Availability Operators, including the Self Node Remediation |
| registry.redhat.io/workload-availability/node-healthcheck-must-gather-rhel9:v<installed_version_NHC> | Data collection for the Red Hat Workload Availability Operators, including the Self Node Remediation |
| registry.redhat.io/numaresources/numaresources-must-gather-rhel9:v<installed-version-nro> | Data collection for the NUMA Resources Operator (NRO). |
| registry.redhat.io/openshift4/ptp-must-gather-rhel8:v<installed-version-ptp> | Data collection for the PTP Operator. |
| registry.redhat.io/openshift-gitops-1/must-gather-rhel8:v<installed_version_GitOps> | Data collection for Red Hat OpenShift GitOps. |
| registry.redhat.io/openshift4/ose-secrets-store-csi-mustgather-rhel9:v<installed_version_secret_stor | Data collection for the Secrets Store CSI Driver Operator. |
| registry.redhat.io/lvms4/lvms-must-gather-rhel9:v<installed_version_LVMS> | Data collection for the LVM Operator. |
| registry.redhat.io/compliance/openshift-compliance-must-gather-rhel8:<digest-version> | Data collection for the Compliance Operator. |

registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43

Data collection for OpenShift Virtualization.

registry.redhat.io/openshift-serverless-1/svls-must-gather-rhel8

Data collection for OpenShift Serverless.

registry.redhat.io/openshift-service-mesh/istio-must-gather-rhel8:<installed_version_service_mesh>

Data collection for Red Hat OpenShift Service Mesh.

registry.redhat.io/multicluster-engine/must-gather-rhel8

Data collection for hosted control planes.

registry.redhat.io/rhmtc/openshift-migration-must-gather-rhel8:v<installed_version_migration_toolkit>

Data collection for the Migration Toolkit for Containers.

registry.redhat.io/odf4/odf-must-gather-rhel9:v<installed_version_ODF>

Data collection for Red Hat OpenShift Data Foundation.

registry.redhat.io/openshift-logging/cluster-logging-rhel9-operator:v<installed_version_logging>

Data collection for logging.

quay.io/netobserv/must-gather

Data collection for the Network Observability Operator.

registry.redhat.io/openshift4/ose-csi-driver-shared-resource-mustgather-rhel8

Data collection for OpenShift Shared Resource CSI Driver.

registry.redhat.io/openshift4/ose-local-storage-mustgather-rhel9:v<installed_version_LSO>

Data collection for Local Storage Operator.

registry.redhat.io/openshift-sandboxed-containers/osc-must-gather-rhel8:v<installed_version_sandboxed_containers>

Data collection for OpenShift sandboxed containers.

registry.redhat.io/workload-availability/node-healthcheck-must-gather-rhel8:v<installed_version_NHC>

Data collection for the Red Hat Workload Availability Operators, including the Self Node Remediation (SNR) Operator, the Fence Agents Remediation (FAR) Operator, the Machine Deletion Remediation (MDR) Operator, the Node Health Check (NHC) Operator, and the Node Maintenance Operator (NMO).

Use this image if your NHC Operator version isearlier than 0.9.0.

For more information, see the "Gathering data" section for the specific Operator inRemediation, fencing, and maintenance(Workload Availability for Red Hat OpenShift documentation).

registry.redhat.io/workload-availability/node-healthcheck-must-gather-rhel9:v<installed_version_NHC>

Data collection for the Red Hat Workload Availability Operators, including the Self Node Remediation (SNR) Operator, the Fence Agents Remediation (FAR) Operator, the Machine Deletion Remediation (MDR) Operator, the Node Health Check (NHC) Operator, and the Node Maintenance Operator (NMO).

Use this image if your NHC Operator version is0.9.0. or later.

For more information, see the "Gathering data" section for the specific Operator inRemediation, fencing, and maintenance(Workload Availability for Red Hat OpenShift documentation).

registry.redhat.io/numaresources/numaresources-must-gather-rhel9:v<installed-version-nro>

Data collection for the NUMA Resources Operator (NRO).

registry.redhat.io/openshift4/ptp-must-gather-rhel8:v<installed-version-ptp>

Data collection for the PTP Operator.

registry.redhat.io/openshift-gitops-1/must-gather-rhel8:v<installed_version_GitOps>

Data collection for Red Hat OpenShift GitOps.

registry.redhat.io/openshift4/ose-secrets-store-csi-mustgather-rhel9:v<installed_version_secret_store>

Data collection for the Secrets Store CSI Driver Operator.

registry.redhat.io/lvms4/lvms-must-gather-rhel9:v<installed_version_LVMS>

Data collection for the LVM Operator.

registry.redhat.io/compliance/openshift-compliance-must-gather-rhel8:<digest-version>

Data collection for the Compliance Operator.

To determine the latest version for an OpenShift Container Platform component’s image, see theOpenShift Operator Life Cyclesweb page on the Red Hat Customer Portal.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- The OpenShift Container Platform CLI (oc) is installed.

Procedure

- Navigate to the directory where you want to store themust-gatherdata.
- Run theoc adm must-gathercommand with one or more--imageor--image-streamarguments.To collect the defaultmust-gatherdata in addition to specific feature data, add the--image-stream=openshift/must-gatherargument.For information on gathering data about the Custom Metrics Autoscaler, see the Additional resources section that follows.For example, the following command gathers both the default cluster data and information specific to OpenShift Virtualization:oc adm must-gather \
  --image-stream=openshift/must-gather \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43$oc adm must-gather\--image-stream=openshift/must-gather\1--image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.432Copy to ClipboardCopied!Toggle word wrapToggle overflow1The default OpenShift Container Platformmust-gatherimage2The must-gather image for OpenShift VirtualizationYou can use themust-gathertool with additional arguments to gather data that is specifically related to OpenShift Logging and the Red Hat OpenShift Logging Operator in your cluster. For OpenShift Logging, run the following command:oc adm must-gather --image=$(oc -n openshift-logging get deployment.apps/cluster-logging-operator \
  -o jsonpath='{.spec.template.spec.containers[?(@.name == "cluster-logging-operator")].image}')$oc adm must-gather--image=$(oc-nopenshift-logging get deployment.apps/cluster-logging-operator\-ojsonpath='{.spec.template.spec.containers[?(@.name == "cluster-logging-operator")].image}')Copy to ClipboardCopied!Toggle word wrapToggle overflowExample 5.1. Examplemust-gatheroutput for OpenShift Logging├── cluster-logging
│  ├── clo
│  │  ├── cluster-logging-operator-74dd5994f-6ttgt
│  │  ├── clusterlogforwarder_cr
│  │  ├── cr
│  │  ├── csv
│  │  ├── deployment
│  │  └── logforwarding_cr
│  ├── collector
│  │  ├── fluentd-2tr64
│  ├── eo
│  │  ├── csv
│  │  ├── deployment
│  │  └── elasticsearch-operator-7dc7d97b9d-jb4r4
│  ├── es
│  │  ├── cluster-elasticsearch
│  │  │  ├── aliases
│  │  │  ├── health
│  │  │  ├── indices
│  │  │  ├── latest_documents.json
│  │  │  ├── nodes
│  │  │  ├── nodes_stats.json
│  │  │  └── thread_pool
│  │  ├── cr
│  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  │  └── logs
│  │     ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  ├── install
│  │  ├── co_logs
│  │  ├── install_plan
│  │  ├── olmo_logs
│  │  └── subscription
│  └── kibana
│     ├── cr
│     ├── kibana-9d69668d4-2rkvz
├── cluster-scoped-resources
│  └── core
│     ├── nodes
│     │  ├── ip-10-0-146-180.eu-west-1.compute.internal.yaml
│     └── persistentvolumes
│        ├── pvc-0a8d65d9-54aa-4c44-9ecc-33d9381e41c1.yaml
├── event-filter.html
├── gather-debug.log
└── namespaces
   ├── openshift-logging
   │  ├── apps
   │  │  ├── daemonsets.yaml
   │  │  ├── deployments.yaml
   │  │  ├── replicasets.yaml
   │  │  └── statefulsets.yaml
   │  ├── batch
   │  │  ├── cronjobs.yaml
   │  │  └── jobs.yaml
   │  ├── core
   │  │  ├── configmaps.yaml
   │  │  ├── endpoints.yaml
   │  │  ├── events
   │  │  │  ├── elasticsearch-im-app-1596020400-gm6nl.1626341a296c16a1.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-9l9n4.1626341a2af81bbd.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-v98tk.1626341a2d821069.yaml
   │  │  │  ├── elasticsearch-im-app-1596020400-cc5vc.1626341a3019b238.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-s8d5s.1626341a31f7b315.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-7mgv8.1626341a35ea59ed.yaml
   │  │  ├── events.yaml
   │  │  ├── persistentvolumeclaims.yaml
   │  │  ├── pods.yaml
   │  │  ├── replicationcontrollers.yaml
   │  │  ├── secrets.yaml
   │  │  └── services.yaml
   │  ├── openshift-logging.yaml
   │  ├── pods
   │  │  ├── cluster-logging-operator-74dd5994f-6ttgt
   │  │  │  ├── cluster-logging-operator
   │  │  │  │  └── cluster-logging-operator
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  └── cluster-logging-operator-74dd5994f-6ttgt.yaml
   │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff
   │  │  │  ├── cluster-logging-operator-registry
   │  │  │  │  └── cluster-logging-operator-registry
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff.yaml
   │  │  │  └── mutate-csv-and-generate-sqlite-db
   │  │  │     └── mutate-csv-and-generate-sqlite-db
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
   │  │  ├── elasticsearch-im-app-1596030300-bpgcx
   │  │  │  ├── elasticsearch-im-app-1596030300-bpgcx.yaml
   │  │  │  └── indexmanagement
   │  │  │     └── indexmanagement
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── fluentd-2tr64
   │  │  │  ├── fluentd
   │  │  │  │  └── fluentd
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── fluentd-2tr64.yaml
   │  │  │  └── fluentd-init
   │  │  │     └── fluentd-init
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── kibana-9d69668d4-2rkvz
   │  │  │  ├── kibana
   │  │  │  │  └── kibana
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── kibana-9d69668d4-2rkvz.yaml
   │  │  │  └── kibana-proxy
   │  │  │     └── kibana-proxy
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  └── route.openshift.io
   │     └── routes.yaml
   └── openshift-operators-redhat
      ├── ...├── cluster-logging
│  ├── clo
│  │  ├── cluster-logging-operator-74dd5994f-6ttgt
│  │  ├── clusterlogforwarder_cr
│  │  ├── cr
│  │  ├── csv
│  │  ├── deployment
│  │  └── logforwarding_cr
│  ├── collector
│  │  ├── fluentd-2tr64
│  ├── eo
│  │  ├── csv
│  │  ├── deployment
│  │  └── elasticsearch-operator-7dc7d97b9d-jb4r4
│  ├── es
│  │  ├── cluster-elasticsearch
│  │  │  ├── aliases
│  │  │  ├── health
│  │  │  ├── indices
│  │  │  ├── latest_documents.json
│  │  │  ├── nodes
│  │  │  ├── nodes_stats.json
│  │  │  └── thread_pool
│  │  ├── cr
│  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  │  └── logs
│  │     ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  ├── install
│  │  ├── co_logs
│  │  ├── install_plan
│  │  ├── olmo_logs
│  │  └── subscription
│  └── kibana
│     ├── cr
│     ├── kibana-9d69668d4-2rkvz
├── cluster-scoped-resources
│  └── core
│     ├── nodes
│     │  ├── ip-10-0-146-180.eu-west-1.compute.internal.yaml
│     └── persistentvolumes
│        ├── pvc-0a8d65d9-54aa-4c44-9ecc-33d9381e41c1.yaml
├── event-filter.html
├── gather-debug.log
└── namespaces
   ├── openshift-logging
   │  ├── apps
   │  │  ├── daemonsets.yaml
   │  │  ├── deployments.yaml
   │  │  ├── replicasets.yaml
   │  │  └── statefulsets.yaml
   │  ├── batch
   │  │  ├── cronjobs.yaml
   │  │  └── jobs.yaml
   │  ├── core
   │  │  ├── configmaps.yaml
   │  │  ├── endpoints.yaml
   │  │  ├── events
   │  │  │  ├── elasticsearch-im-app-1596020400-gm6nl.1626341a296c16a1.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-9l9n4.1626341a2af81bbd.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-v98tk.1626341a2d821069.yaml
   │  │  │  ├── elasticsearch-im-app-1596020400-cc5vc.1626341a3019b238.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-s8d5s.1626341a31f7b315.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-7mgv8.1626341a35ea59ed.yaml
   │  │  ├── events.yaml
   │  │  ├── persistentvolumeclaims.yaml
   │  │  ├── pods.yaml
   │  │  ├── replicationcontrollers.yaml
   │  │  ├── secrets.yaml
   │  │  └── services.yaml
   │  ├── openshift-logging.yaml
   │  ├── pods
   │  │  ├── cluster-logging-operator-74dd5994f-6ttgt
   │  │  │  ├── cluster-logging-operator
   │  │  │  │  └── cluster-logging-operator
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  └── cluster-logging-operator-74dd5994f-6ttgt.yaml
   │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff
   │  │  │  ├── cluster-logging-operator-registry
   │  │  │  │  └── cluster-logging-operator-registry
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff.yaml
   │  │  │  └── mutate-csv-and-generate-sqlite-db
   │  │  │     └── mutate-csv-and-generate-sqlite-db
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
   │  │  ├── elasticsearch-im-app-1596030300-bpgcx
   │  │  │  ├── elasticsearch-im-app-1596030300-bpgcx.yaml
   │  │  │  └── indexmanagement
   │  │  │     └── indexmanagement
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── fluentd-2tr64
   │  │  │  ├── fluentd
   │  │  │  │  └── fluentd
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── fluentd-2tr64.yaml
   │  │  │  └── fluentd-init
   │  │  │     └── fluentd-init
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── kibana-9d69668d4-2rkvz
   │  │  │  ├── kibana
   │  │  │  │  └── kibana
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── kibana-9d69668d4-2rkvz.yaml
   │  │  │  └── kibana-proxy
   │  │  │     └── kibana-proxy
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  └── route.openshift.io
   │     └── routes.yaml
   └── openshift-operators-redhat
      ├── ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run theoc adm must-gathercommand with one or more--imageor--image-streamarguments.

- To collect the defaultmust-gatherdata in addition to specific feature data, add the--image-stream=openshift/must-gatherargument.
- For information on gathering data about the Custom Metrics Autoscaler, see the Additional resources section that follows.

For example, the following command gathers both the default cluster data and information specific to OpenShift Virtualization:

```
oc adm must-gather \
  --image-stream=openshift/must-gather \
  --image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

```
$ oc adm must-gather \
  --image-stream=openshift/must-gather \
```

```
--image=registry.redhat.io/container-native-virtualization/cnv-must-gather-rhel9:v4.17.43
```

**1**
  The default OpenShift Container Platformmust-gatherimage

**2**
  The must-gather image for OpenShift Virtualization

You can use themust-gathertool with additional arguments to gather data that is specifically related to OpenShift Logging and the Red Hat OpenShift Logging Operator in your cluster. For OpenShift Logging, run the following command:

```
oc adm must-gather --image=$(oc -n openshift-logging get deployment.apps/cluster-logging-operator \
  -o jsonpath='{.spec.template.spec.containers[?(@.name == "cluster-logging-operator")].image}')
```

```
$ oc adm must-gather --image=$(oc -n openshift-logging get deployment.apps/cluster-logging-operator \
  -o jsonpath='{.spec.template.spec.containers[?(@.name == "cluster-logging-operator")].image}')
```

Example 5.1. Examplemust-gatheroutput for OpenShift Logging

```
├── cluster-logging
│  ├── clo
│  │  ├── cluster-logging-operator-74dd5994f-6ttgt
│  │  ├── clusterlogforwarder_cr
│  │  ├── cr
│  │  ├── csv
│  │  ├── deployment
│  │  └── logforwarding_cr
│  ├── collector
│  │  ├── fluentd-2tr64
│  ├── eo
│  │  ├── csv
│  │  ├── deployment
│  │  └── elasticsearch-operator-7dc7d97b9d-jb4r4
│  ├── es
│  │  ├── cluster-elasticsearch
│  │  │  ├── aliases
│  │  │  ├── health
│  │  │  ├── indices
│  │  │  ├── latest_documents.json
│  │  │  ├── nodes
│  │  │  ├── nodes_stats.json
│  │  │  └── thread_pool
│  │  ├── cr
│  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  │  └── logs
│  │     ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  ├── install
│  │  ├── co_logs
│  │  ├── install_plan
│  │  ├── olmo_logs
│  │  └── subscription
│  └── kibana
│     ├── cr
│     ├── kibana-9d69668d4-2rkvz
├── cluster-scoped-resources
│  └── core
│     ├── nodes
│     │  ├── ip-10-0-146-180.eu-west-1.compute.internal.yaml
│     └── persistentvolumes
│        ├── pvc-0a8d65d9-54aa-4c44-9ecc-33d9381e41c1.yaml
├── event-filter.html
├── gather-debug.log
└── namespaces
   ├── openshift-logging
   │  ├── apps
   │  │  ├── daemonsets.yaml
   │  │  ├── deployments.yaml
   │  │  ├── replicasets.yaml
   │  │  └── statefulsets.yaml
   │  ├── batch
   │  │  ├── cronjobs.yaml
   │  │  └── jobs.yaml
   │  ├── core
   │  │  ├── configmaps.yaml
   │  │  ├── endpoints.yaml
   │  │  ├── events
   │  │  │  ├── elasticsearch-im-app-1596020400-gm6nl.1626341a296c16a1.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-9l9n4.1626341a2af81bbd.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-v98tk.1626341a2d821069.yaml
   │  │  │  ├── elasticsearch-im-app-1596020400-cc5vc.1626341a3019b238.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-s8d5s.1626341a31f7b315.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-7mgv8.1626341a35ea59ed.yaml
   │  │  ├── events.yaml
   │  │  ├── persistentvolumeclaims.yaml
   │  │  ├── pods.yaml
   │  │  ├── replicationcontrollers.yaml
   │  │  ├── secrets.yaml
   │  │  └── services.yaml
   │  ├── openshift-logging.yaml
   │  ├── pods
   │  │  ├── cluster-logging-operator-74dd5994f-6ttgt
   │  │  │  ├── cluster-logging-operator
   │  │  │  │  └── cluster-logging-operator
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  └── cluster-logging-operator-74dd5994f-6ttgt.yaml
   │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff
   │  │  │  ├── cluster-logging-operator-registry
   │  │  │  │  └── cluster-logging-operator-registry
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff.yaml
   │  │  │  └── mutate-csv-and-generate-sqlite-db
   │  │  │     └── mutate-csv-and-generate-sqlite-db
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
   │  │  ├── elasticsearch-im-app-1596030300-bpgcx
   │  │  │  ├── elasticsearch-im-app-1596030300-bpgcx.yaml
   │  │  │  └── indexmanagement
   │  │  │     └── indexmanagement
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── fluentd-2tr64
   │  │  │  ├── fluentd
   │  │  │  │  └── fluentd
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── fluentd-2tr64.yaml
   │  │  │  └── fluentd-init
   │  │  │     └── fluentd-init
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── kibana-9d69668d4-2rkvz
   │  │  │  ├── kibana
   │  │  │  │  └── kibana
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── kibana-9d69668d4-2rkvz.yaml
   │  │  │  └── kibana-proxy
   │  │  │     └── kibana-proxy
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  └── route.openshift.io
   │     └── routes.yaml
   └── openshift-operators-redhat
      ├── ...
```

```
├── cluster-logging
│  ├── clo
│  │  ├── cluster-logging-operator-74dd5994f-6ttgt
│  │  ├── clusterlogforwarder_cr
│  │  ├── cr
│  │  ├── csv
│  │  ├── deployment
│  │  └── logforwarding_cr
│  ├── collector
│  │  ├── fluentd-2tr64
│  ├── eo
│  │  ├── csv
│  │  ├── deployment
│  │  └── elasticsearch-operator-7dc7d97b9d-jb4r4
│  ├── es
│  │  ├── cluster-elasticsearch
│  │  │  ├── aliases
│  │  │  ├── health
│  │  │  ├── indices
│  │  │  ├── latest_documents.json
│  │  │  ├── nodes
│  │  │  ├── nodes_stats.json
│  │  │  └── thread_pool
│  │  ├── cr
│  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  │  └── logs
│  │     ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
│  ├── install
│  │  ├── co_logs
│  │  ├── install_plan
│  │  ├── olmo_logs
│  │  └── subscription
│  └── kibana
│     ├── cr
│     ├── kibana-9d69668d4-2rkvz
├── cluster-scoped-resources
│  └── core
│     ├── nodes
│     │  ├── ip-10-0-146-180.eu-west-1.compute.internal.yaml
│     └── persistentvolumes
│        ├── pvc-0a8d65d9-54aa-4c44-9ecc-33d9381e41c1.yaml
├── event-filter.html
├── gather-debug.log
└── namespaces
   ├── openshift-logging
   │  ├── apps
   │  │  ├── daemonsets.yaml
   │  │  ├── deployments.yaml
   │  │  ├── replicasets.yaml
   │  │  └── statefulsets.yaml
   │  ├── batch
   │  │  ├── cronjobs.yaml
   │  │  └── jobs.yaml
   │  ├── core
   │  │  ├── configmaps.yaml
   │  │  ├── endpoints.yaml
   │  │  ├── events
   │  │  │  ├── elasticsearch-im-app-1596020400-gm6nl.1626341a296c16a1.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-9l9n4.1626341a2af81bbd.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-v98tk.1626341a2d821069.yaml
   │  │  │  ├── elasticsearch-im-app-1596020400-cc5vc.1626341a3019b238.yaml
   │  │  │  ├── elasticsearch-im-audit-1596020400-s8d5s.1626341a31f7b315.yaml
   │  │  │  ├── elasticsearch-im-infra-1596020400-7mgv8.1626341a35ea59ed.yaml
   │  │  ├── events.yaml
   │  │  ├── persistentvolumeclaims.yaml
   │  │  ├── pods.yaml
   │  │  ├── replicationcontrollers.yaml
   │  │  ├── secrets.yaml
   │  │  └── services.yaml
   │  ├── openshift-logging.yaml
   │  ├── pods
   │  │  ├── cluster-logging-operator-74dd5994f-6ttgt
   │  │  │  ├── cluster-logging-operator
   │  │  │  │  └── cluster-logging-operator
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  └── cluster-logging-operator-74dd5994f-6ttgt.yaml
   │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff
   │  │  │  ├── cluster-logging-operator-registry
   │  │  │  │  └── cluster-logging-operator-registry
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── cluster-logging-operator-registry-6df49d7d4-mxxff.yaml
   │  │  │  └── mutate-csv-and-generate-sqlite-db
   │  │  │     └── mutate-csv-and-generate-sqlite-db
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── elasticsearch-cdm-lp8l38m0-1-794d6dd989-4jxms
   │  │  ├── elasticsearch-im-app-1596030300-bpgcx
   │  │  │  ├── elasticsearch-im-app-1596030300-bpgcx.yaml
   │  │  │  └── indexmanagement
   │  │  │     └── indexmanagement
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── fluentd-2tr64
   │  │  │  ├── fluentd
   │  │  │  │  └── fluentd
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── fluentd-2tr64.yaml
   │  │  │  └── fluentd-init
   │  │  │     └── fluentd-init
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  │  ├── kibana-9d69668d4-2rkvz
   │  │  │  ├── kibana
   │  │  │  │  └── kibana
   │  │  │  │     └── logs
   │  │  │  │        ├── current.log
   │  │  │  │        ├── previous.insecure.log
   │  │  │  │        └── previous.log
   │  │  │  ├── kibana-9d69668d4-2rkvz.yaml
   │  │  │  └── kibana-proxy
   │  │  │     └── kibana-proxy
   │  │  │        └── logs
   │  │  │           ├── current.log
   │  │  │           ├── previous.insecure.log
   │  │  │           └── previous.log
   │  └── route.openshift.io
   │     └── routes.yaml
   └── openshift-operators-redhat
      ├── ...
```

- Run theoc adm must-gathercommand with one or more--imageor--image-streamarguments. For example, the following command gathers both the default cluster data and information specific to KubeVirt:oc adm must-gather \
 --image-stream=openshift/must-gather \
 --image=quay.io/kubevirt/must-gather$oc adm must-gather\--image-stream=openshift/must-gather\1--image=quay.io/kubevirt/must-gather2Copy to ClipboardCopied!Toggle word wrapToggle overflow1The default OpenShift Container Platformmust-gatherimage2The must-gather image for KubeVirt

Run theoc adm must-gathercommand with one or more--imageor--image-streamarguments. For example, the following command gathers both the default cluster data and information specific to KubeVirt:

```
oc adm must-gather \
 --image-stream=openshift/must-gather \
 --image=quay.io/kubevirt/must-gather
```

```
$ oc adm must-gather \
 --image-stream=openshift/must-gather \
```

```
--image=quay.io/kubevirt/must-gather
```

**1**
  The default OpenShift Container Platformmust-gatherimage

**2**
  The must-gather image for KubeVirt
- Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:tar cvaf must-gather-`date +"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz <must_gather_local_dir>$tarcvaf must-gather-`date+"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz<must_gather_local_dir>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<must_gather_local_dir>with the actual directory name.

Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:

**1**
  Replace<must_gather_local_dir>with the actual directory name.
- Attach the compressed file to your support case on thetheCustomer Supportpageof the Red Hat Customer Portal.

### 5.1.4. Gathering network logsCopy linkLink copied to clipboard!

You can gather network logs on all nodes in a cluster.

Procedure

- Run theoc adm must-gathercommand with-- gather_network_logs:oc adm must-gather -- gather_network_logs$oc adm must-gather -- gather_network_logsCopy to ClipboardCopied!Toggle word wrapToggle overflowBy default, themust-gathertool collects the OVNnbdbandsbdbdatabases from all of the nodes in the cluster. Adding the-- gather_network_logsoption to include additional logs that contain OVN-Kubernetes transactions for OVNnbdbdatabase.

Run theoc adm must-gathercommand with-- gather_network_logs:

By default, themust-gathertool collects the OVNnbdbandsbdbdatabases from all of the nodes in the cluster. Adding the-- gather_network_logsoption to include additional logs that contain OVN-Kubernetes transactions for OVNnbdbdatabase.

- Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:tar cvaf must-gather-`date +"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz <must_gather_local_dir>$tarcvaf must-gather-`date+"%m-%d-%Y-%H-%M-%S"`-<cluster_id>.tar.gz<must_gather_local_dir>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<must_gather_local_dir>with the actual directory name.

Create a compressed file from themust-gatherdirectory that was just created in your working directory. Make sure you provide the date and cluster ID for the unique must-gather data. For more information about how to find the cluster ID, seeHow to find the cluster-id or name on OpenShift cluster. For example, on a computer that uses a Linux operating system, run the following command:

**1**
  Replace<must_gather_local_dir>with the actual directory name.
- Attach the compressed file to your support case on thetheCustomer Supportpageof the Red Hat Customer Portal.

### 5.1.5. Changing the must-gather storage limitCopy linkLink copied to clipboard!

When using theoc adm must-gathercommand to collect data the default maximum storage for the information is 30% of the storage capacity of the container. After the 30% limit is reached the container is killed and the gathering process stops. Information already gathered is downloaded to your local storage. To run the must-gather command again, you need either a container with more storage capacity or to adjust the maximum volume percentage.

If the container reaches the storage limit, an error message similar to the following example is generated.

Example output

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- The OpenShift CLI (oc) is installed.

Procedure

- Run theoc adm must-gathercommand with thevolume-percentageflag. The new value cannot exceed 100.oc adm must-gather --volume-percentage <storage_percentage>$oc adm must-gather --volume-percentage<storage_percentage>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run theoc adm must-gathercommand with thevolume-percentageflag. The new value cannot exceed 100.

## 5.2. Obtaining your cluster IDCopy linkLink copied to clipboard!

When providing information to Red Hat Support, it is helpful to provide the unique identifier for your cluster. You can have your cluster ID autofilled by using the OpenShift Container Platform web console. You can also manually obtain your cluster ID by using the web console or the OpenShift CLI (oc).

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have access to the web console or the OpenShift CLI (oc) installed.

Procedure

- To open a support case and have your cluster ID autofilled using the web console:From the toolbar, navigate to(?) Helpand selectShare Feedbackfrom the list.ClickOpen a support casefrom theTell us about your experiencewindow.

To open a support case and have your cluster ID autofilled using the web console:

- From the toolbar, navigate to(?) Helpand selectShare Feedbackfrom the list.
- ClickOpen a support casefrom theTell us about your experiencewindow.
- To manually obtain your cluster ID using the web console:Navigate toHomeOverview.The value is available in theCluster IDfield of theDetailssection.

To manually obtain your cluster ID using the web console:

- Navigate toHomeOverview.
- The value is available in theCluster IDfield of theDetailssection.
- To obtain your cluster ID using the OpenShift CLI (oc), run the following command:oc get clusterversion -o jsonpath='{.items[].spec.clusterID}{"\n"}'$oc get clusterversion-ojsonpath='{.items[].spec.clusterID}{"\n"}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

To obtain your cluster ID using the OpenShift CLI (oc), run the following command:

## 5.3. About sosreportCopy linkLink copied to clipboard!

sosreportis a tool that collects configuration details, system information, and diagnostic data from Red Hat Enterprise Linux (RHEL) and Red Hat Enterprise Linux CoreOS (RHCOS) systems.sosreportprovides a standardized way to collect diagnostic information relating to a node, which can then be provided to Red Hat Support for issue diagnosis.

In some support interactions, Red Hat Support may ask you to collect asosreportarchive for a specific OpenShift Container Platform node. For example, it might sometimes be necessary to review system logs or other node-specific data that is not included within the output ofoc adm must-gather.

## 5.4. Generating a sosreport archive for an OpenShift Container Platform cluster nodeCopy linkLink copied to clipboard!

The recommended way to generate asosreportfor an OpenShift Container Platform 4.17 cluster node is through a debug pod.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have SSH access to your hosts.
- You have installed the OpenShift CLI (oc).
- You have a Red Hat standard or premium Subscription.
- You have a Red Hat Customer Portal account.
- You have an existing Red Hat Support case ID.

Procedure

- Obtain a list of cluster nodes:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a list of cluster nodes:

- Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:oc debug node/my-cluster-node$oc debug node/my-cluster-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowTo enter into a debug session on the target node that is tainted with theNoExecuteeffect, add a toleration to a dummy namespace, and start the debug pod in the dummy namespace:oc new-project dummy$oc new-project dummyCopy to ClipboardCopied!Toggle word wrapToggle overflowoc patch namespace dummy --type=merge -p '{"metadata": {"annotations": { "scheduler.alpha.kubernetes.io/defaultTolerations": "[{\"operator\": \"Exists\"}]"}}}'$oc patch namespace dummy--type=merge-p'{"metadata": {"annotations": { "scheduler.alpha.kubernetes.io/defaultTolerations": "[{\"operator\": \"Exists\"}]"}}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowoc debug node/my-cluster-node$oc debug node/my-cluster-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:

To enter into a debug session on the target node that is tainted with theNoExecuteeffect, add a toleration to a dummy namespace, and start the debug pod in the dummy namespace:

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- Start atoolboxcontainer, which includes the required binaries and plugins to runsosreport:toolbox#toolboxCopy to ClipboardCopied!Toggle word wrapToggle overflowIf an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. Remove the running toolbox container withpodman rm toolbox-and spawn a new toolbox container, to avoid issues withsosreportplugins.

Start atoolboxcontainer, which includes the required binaries and plugins to runsosreport:

If an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. Remove the running toolbox container withpodman rm toolbox-and spawn a new toolbox container, to avoid issues withsosreportplugins.

- Collect asosreportarchive.Run thesos reportcommand to collect necessary troubleshooting data oncrioandpodman:sos report -k crio.all=on -k crio.logs=on  -k podman.all=on -k podman.logs=on#sos report-kcrio.all=on-kcrio.logs=on-kpodman.all=on-kpodman.logs=on1Copy to ClipboardCopied!Toggle word wrapToggle overflow1-kenables you to definesosreportplugin parameters outside of the defaults.Optional: To include information on OVN-Kubernetes networking configurations from a node in your report, run the following command:sos report --all-logs#sos report --all-logsCopy to ClipboardCopied!Toggle word wrapToggle overflowPressEnterwhen prompted, to continue.Provide the Red Hat Support case ID.sosreportadds the ID to the archive’s file name.Thesosreportoutput provides the archive’s location and checksum. The following sample output references support case ID01234567:Your sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz 

The checksum is: 382ffc167510fd71b4f12a4f40b97a4eYour sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz1The checksum is: 382ffc167510fd71b4f12a4f40b97a4eCopy to ClipboardCopied!Toggle word wrapToggle overflow1Thesosreportarchive’s file path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.

Collect asosreportarchive.

- Run thesos reportcommand to collect necessary troubleshooting data oncrioandpodman:sos report -k crio.all=on -k crio.logs=on  -k podman.all=on -k podman.logs=on#sos report-kcrio.all=on-kcrio.logs=on-kpodman.all=on-kpodman.logs=on1Copy to ClipboardCopied!Toggle word wrapToggle overflow1-kenables you to definesosreportplugin parameters outside of the defaults.

Run thesos reportcommand to collect necessary troubleshooting data oncrioandpodman:

**1**
  -kenables you to definesosreportplugin parameters outside of the defaults.
- Optional: To include information on OVN-Kubernetes networking configurations from a node in your report, run the following command:sos report --all-logs#sos report --all-logsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: To include information on OVN-Kubernetes networking configurations from a node in your report, run the following command:

- PressEnterwhen prompted, to continue.
- Provide the Red Hat Support case ID.sosreportadds the ID to the archive’s file name.
- Thesosreportoutput provides the archive’s location and checksum. The following sample output references support case ID01234567:Your sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz 

The checksum is: 382ffc167510fd71b4f12a4f40b97a4eYour sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz1The checksum is: 382ffc167510fd71b4f12a4f40b97a4eCopy to ClipboardCopied!Toggle word wrapToggle overflow1Thesosreportarchive’s file path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.

Thesosreportoutput provides the archive’s location and checksum. The following sample output references support case ID01234567:

```
Your sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz 

The checksum is: 382ffc167510fd71b4f12a4f40b97a4e
```

```
Your sosreport has been generated and saved in:
  /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz
```

```
The checksum is: 382ffc167510fd71b4f12a4f40b97a4e
```

**1**
  Thesosreportarchive’s file path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.
- Provide thesosreportarchive to Red Hat Support for analysis, using one of the following methods.Upload the file to an existing Red Hat support case.Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz' > /tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz'>/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring asosreportarchive from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy asosreportarchive from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.SelectAttach filesand follow the prompts to upload the file.

Provide thesosreportarchive to Red Hat Support for analysis, using one of the following methods.

- Upload the file to an existing Red Hat support case.Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz' > /tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz'>/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring asosreportarchive from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy asosreportarchive from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.SelectAttach filesand follow the prompts to upload the file.

Upload the file to an existing Red Hat support case.

- Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz' > /tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz'>/tmp/sosreport-my-cluster-node-01234567-2020-05-28-eyjknxt.tar.xz1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring asosreportarchive from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy asosreportarchive from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:

**1**
  The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring asosreportarchive from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy asosreportarchive from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

- Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.
- SelectAttach filesand follow the prompts to upload the file.

## 5.5. Querying bootstrap node journal logsCopy linkLink copied to clipboard!

If you experience bootstrap-related issues, you can gatherbootkube.servicejournaldunit logs and container logs from the bootstrap node.

Prerequisites

- You have SSH access to your bootstrap node.
- You have the fully qualified domain name of the bootstrap node.

Procedure

- Querybootkube.servicejournaldunit logs from a bootstrap node during OpenShift Container Platform installation. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> journalctl -b -f -u bootkube.service$sshcore@<bootstrap_fqdn>journalctl-b-f-ubootkube.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowThebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

Querybootkube.servicejournaldunit logs from a bootstrap node during OpenShift Container Platform installation. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

Thebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

- Collect logs from the bootstrap node containers usingpodmanon the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> 'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'$sshcore@<bootstrap_fqdn>'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Collect logs from the bootstrap node containers usingpodmanon the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

## 5.6. Querying cluster node journal logsCopy linkLink copied to clipboard!

You can gatherjournaldunit logs and other logs within/var/logon individual cluster nodes.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- Your API service is still functional.
- You have SSH access to your hosts.

Procedure

- Querykubeletjournaldunit logs from OpenShift Container Platform cluster nodes. The following example queries control plane nodes only:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubelet1Copy to ClipboardCopied!Toggle word wrapToggle overflowkubelet: Replace as appropriate to query other unit logs.

Querykubeletjournaldunit logs from OpenShift Container Platform cluster nodes. The following example queries control plane nodes only:

- kubelet: Replace as appropriate to query other unit logs.
- Collect logs from specific subdirectories under/var/log/on cluster nodes.Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflowInspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Collect logs from specific subdirectories under/var/log/on cluster nodes.

- Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:

- Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:

- If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

## 5.7. Network trace methodsCopy linkLink copied to clipboard!

Collecting network traces, in the form of packet capture records, can assist Red Hat Support with troubleshooting network issues.

OpenShift Container Platform supports two ways of performing a network trace. Review the following table and choose the method that meets your needs.

| Method | Benefits and capabilities |
| --- | --- |
| Collecting a host network trace | You perform a packet capture for a duration that you specify on one or more nodes at the same time.  |
| Collecting a network trace from an OpenShift Container Platform node or container | You perform a packet capture on one node or one container. You run thetcpdumpcommand interactively,  |

Collecting a host network trace

You perform a packet capture for a duration that you specify on one or more nodes at the same time. The packet capture files are transferred from nodes to the client machine when the specified duration is met.

You can troubleshoot why a specific action triggers network communication issues. Run the packet capture, perform the action that triggers the issue, and use the logs to diagnose the issue.

Collecting a network trace from an OpenShift Container Platform node or container

You perform a packet capture on one node or one container. You run thetcpdumpcommand interactively, so you can control the duration of the packet capture.

You can start the packet capture manually, trigger the network communication issue, and then stop the packet capture manually.

This method uses thecatcommand and shell redirection to copy the packet capture data from the node or container to the client machine.

## 5.8. Collecting a host network traceCopy linkLink copied to clipboard!

Sometimes, troubleshooting a network-related issue is simplified by tracing network communication and capturing packets on multiple nodes at the same time.

You can use a combination of theoc adm must-gathercommand and theregistry.redhat.io/openshift4/network-tools-rhel8container image to gather packet captures from nodes. Analyzing packet captures can help you troubleshoot network communication issues.

Theoc adm must-gathercommand is used to run thetcpdumpcommand in pods on specific nodes. Thetcpdumpcommand records the packet captures in the pods. When thetcpdumpcommand exits, theoc adm must-gathercommand transfers the files with the packet captures from the pods to your client machine.

The sample command in the following procedure demonstrates performing a packet capture with thetcpdumpcommand. However, you can run any command in the container image that is specified in the--imageargument to gather troubleshooting information from multiple nodes at the same time.

Prerequisites

- You are logged in to OpenShift Container Platform as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Run a packet capture from the host network on some nodes by running the following command:oc adm must-gather \
    --dest-dir /tmp/captures \// <.>
    --source-dir '/tmp/tcpdump/' \// <.>
    --image registry.redhat.io/openshift4/network-tools-rhel8:latest \// <.>
    --node-selector 'node-role.kubernetes.io/worker' \// <.>
    --host-network=true \// <.>
    --timeout 30s \// <.>
    -- \
    tcpdump -i any \// <.>
    -w /tmp/tcpdump/%Y-%m-%dT%H:%M:%S.pcap -W 1 -G 300$oc adm must-gather\--dest-dir /tmp/captures\//<.>--source-dir '/tmp/tcpdump/' \// <.>
    --image registry.redhat.io/openshift4/network-tools-rhel8:latest \// <.>
    --node-selector 'node-role.kubernetes.io/worker' \// <.>
    --host-network=true \// <.>
    --timeout 30s \// <.>
    -- \
    tcpdump -i any \// <.>
    -w /tmp/tcpdump/%Y-%m-%dT%H:%M:%S.pcap -W 1 -G 300Copy to ClipboardCopied!Toggle word wrapToggle overflow<.> The--dest-dirargument specifies thatoc adm must-gatherstores the packet captures in directories that are relative to/tmp/captureson the client machine. You can specify any writable directory. <.> Whentcpdumpis run in the debug pod thatoc adm must-gatherstarts, the--source-dirargument specifies that the packet captures are temporarily stored in the/tmp/tcpdumpdirectory on the pod. <.> The--imageargument specifies a container image that includes thetcpdumpcommand. <.> The--node-selectorargument and example value specifies to perform the packet captures on the worker nodes. As an alternative, you can specify the--node-nameargument instead to run the packet capture on a single node. If you omit both the--node-selectorand the--node-nameargument, the packet captures are performed on all nodes. <.> The--host-network=trueargument is required so that the packet captures are performed on the network interfaces of the node. <.> The--timeoutargument and value specify to run the debug pod for 30 seconds. If you do not specify the--timeoutargument and a duration, the debug pod runs for 10 minutes. <.> The-i anyargument for thetcpdumpcommand specifies to capture packets on all network interfaces. As an alternative, you can specify a network interface name.

Run a packet capture from the host network on some nodes by running the following command:

```
oc adm must-gather \
    --dest-dir /tmp/captures \// <.>
    --source-dir '/tmp/tcpdump/' \// <.>
    --image registry.redhat.io/openshift4/network-tools-rhel8:latest \// <.>
    --node-selector 'node-role.kubernetes.io/worker' \// <.>
    --host-network=true \// <.>
    --timeout 30s \// <.>
    -- \
    tcpdump -i any \// <.>
    -w /tmp/tcpdump/%Y-%m-%dT%H:%M:%S.pcap -W 1 -G 300
```

```
$ oc adm must-gather \
    --dest-dir /tmp/captures \// <.>
    --source-dir '/tmp/tcpdump/' \// <.>
    --image registry.redhat.io/openshift4/network-tools-rhel8:latest \// <.>
    --node-selector 'node-role.kubernetes.io/worker' \// <.>
    --host-network=true \// <.>
    --timeout 30s \// <.>
    -- \
    tcpdump -i any \// <.>
    -w /tmp/tcpdump/%Y-%m-%dT%H:%M:%S.pcap -W 1 -G 300
```

<.> The--dest-dirargument specifies thatoc adm must-gatherstores the packet captures in directories that are relative to/tmp/captureson the client machine. You can specify any writable directory. <.> Whentcpdumpis run in the debug pod thatoc adm must-gatherstarts, the--source-dirargument specifies that the packet captures are temporarily stored in the/tmp/tcpdumpdirectory on the pod. <.> The--imageargument specifies a container image that includes thetcpdumpcommand. <.> The--node-selectorargument and example value specifies to perform the packet captures on the worker nodes. As an alternative, you can specify the--node-nameargument instead to run the packet capture on a single node. If you omit both the--node-selectorand the--node-nameargument, the packet captures are performed on all nodes. <.> The--host-network=trueargument is required so that the packet captures are performed on the network interfaces of the node. <.> The--timeoutargument and value specify to run the debug pod for 30 seconds. If you do not specify the--timeoutargument and a duration, the debug pod runs for 10 minutes. <.> The-i anyargument for thetcpdumpcommand specifies to capture packets on all network interfaces. As an alternative, you can specify a network interface name.

- Perform the action, such as accessing a web application, that triggers the network communication issue while the network trace captures packets.
- Review the packet capture files thatoc adm must-gathertransferred from the pods to your client machine:tmp/captures
├── event-filter.html
├── ip-10-0-192-217-ec2-internal  
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:31.pcap
├── ip-10-0-201-178-ec2-internal  
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:30.pcap
├── ip-...
└── timestamptmp/captures
├── event-filter.html
├── ip-10-0-192-217-ec2-internal1│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:31.pcap
├── ip-10-0-201-178-ec2-internal2│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:30.pcap
├── ip-...
└── timestampCopy to ClipboardCopied!Toggle word wrapToggle overflow112The packet captures are stored in directories that identify the hostname, container, and file name. If you did not specify the--node-selectorargument, then the directory level for the hostname is not present.

Review the packet capture files thatoc adm must-gathertransferred from the pods to your client machine:

```
tmp/captures
├── event-filter.html
├── ip-10-0-192-217-ec2-internal  
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:31.pcap
├── ip-10-0-201-178-ec2-internal  
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:30.pcap
├── ip-...
└── timestamp
```

```
tmp/captures
├── event-filter.html
├── ip-10-0-192-217-ec2-internal
```

```
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:31.pcap
├── ip-10-0-201-178-ec2-internal
```

```
│   └── registry-redhat-io-openshift4-network-tools-rhel8-sha256-bca...
│       └── 2022-01-13T19:31:30.pcap
├── ip-...
└── timestamp
```

**112**
  The packet captures are stored in directories that identify the hostname, container, and file name. If you did not specify the--node-selectorargument, then the directory level for the hostname is not present.

## 5.9. Collecting a network trace from an OpenShift Container Platform node or containerCopy linkLink copied to clipboard!

When investigating potential network-related OpenShift Container Platform issues, Red Hat Support might request a network packet trace from a specific OpenShift Container Platform cluster node or from a specific container. The recommended method to capture a network trace in OpenShift Container Platform is through a debug pod.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have an existing Red Hat Support case ID.
- You have a Red Hat standard or premium Subscription.
- You have a Red Hat Customer Portal account.
- You have SSH access to your hosts.

Procedure

- Obtain a list of cluster nodes:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a list of cluster nodes:

- Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:oc debug node/my-cluster-node$oc debug node/my-cluster-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- From within thechrootenvironment console, obtain the node’s interface names:ip ad#ipadCopy to ClipboardCopied!Toggle word wrapToggle overflow

From within thechrootenvironment console, obtain the node’s interface names:

- Start atoolboxcontainer, which includes the required binaries and plugins to runsosreport:toolbox#toolboxCopy to ClipboardCopied!Toggle word wrapToggle overflowIf an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. To avoidtcpdumpissues, remove the running toolbox container withpodman rm toolbox-and spawn a new toolbox container.

Start atoolboxcontainer, which includes the required binaries and plugins to runsosreport:

If an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. To avoidtcpdumpissues, remove the running toolbox container withpodman rm toolbox-and spawn a new toolbox container.

- Initiate atcpdumpsession on the cluster node and redirect output to a capture file. This example usesens5as the interface name:tcpdump -nn -s 0 -i ens5 -w /host/var/tmp/my-cluster-node_$(date +%d_%m_%Y-%H_%M_%S-%Z).pcap$tcpdump-nn-s0-iens5-w/host/var/tmp/my-cluster-node_$(date+%d_%m_%Y-%H_%M_%S-%Z).pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Thetcpdumpcapture file’s path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.

Initiate atcpdumpsession on the cluster node and redirect output to a capture file. This example usesens5as the interface name:

**1**
  Thetcpdumpcapture file’s path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.
- If atcpdumpcapture is required for a specific container on the node, follow these steps.Determine the target container ID. Thechroot hostcommand precedes thecrictlcommand in this step because the toolbox container mounts the host’s root directory at/host:chroot /host crictl ps#chroot/host crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflowDetermine the container’s process ID. In this example, the container ID isa7fe32346b120:chroot /host crictl inspect --output yaml a7fe32346b120 | grep 'pid' | awk '{print $2}'#chroot/host crictl inspect--outputyaml a7fe32346b120|grep'pid'|awk'{print $2}'Copy to ClipboardCopied!Toggle word wrapToggle overflowInitiate atcpdumpsession on the container and redirect output to a capture file. This example uses49628as the container’s process ID andens5as the interface name. Thensentercommand enters the namespace of a target process and runs a command in its namespace. because the target process in this example is a container’s process ID, thetcpdumpcommand is run in the container’s namespace from the host:nsenter -n -t 49628 -- tcpdump -nn -i ens5 -w /host/var/tmp/my-cluster-node-my-container_$(date +%d_%m_%Y-%H_%M_%S-%Z).pcap#nsenter-n-t49628-- tcpdump-nn-iens5-w/host/var/tmp/my-cluster-node-my-container_$(date+%d_%m_%Y-%H_%M_%S-%Z).pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Thetcpdumpcapture file’s path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.

If atcpdumpcapture is required for a specific container on the node, follow these steps.

- Determine the target container ID. Thechroot hostcommand precedes thecrictlcommand in this step because the toolbox container mounts the host’s root directory at/host:chroot /host crictl ps#chroot/host crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Determine the target container ID. Thechroot hostcommand precedes thecrictlcommand in this step because the toolbox container mounts the host’s root directory at/host:

- Determine the container’s process ID. In this example, the container ID isa7fe32346b120:chroot /host crictl inspect --output yaml a7fe32346b120 | grep 'pid' | awk '{print $2}'#chroot/host crictl inspect--outputyaml a7fe32346b120|grep'pid'|awk'{print $2}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Determine the container’s process ID. In this example, the container ID isa7fe32346b120:

- Initiate atcpdumpsession on the container and redirect output to a capture file. This example uses49628as the container’s process ID andens5as the interface name. Thensentercommand enters the namespace of a target process and runs a command in its namespace. because the target process in this example is a container’s process ID, thetcpdumpcommand is run in the container’s namespace from the host:nsenter -n -t 49628 -- tcpdump -nn -i ens5 -w /host/var/tmp/my-cluster-node-my-container_$(date +%d_%m_%Y-%H_%M_%S-%Z).pcap#nsenter-n-t49628-- tcpdump-nn-iens5-w/host/var/tmp/my-cluster-node-my-container_$(date+%d_%m_%Y-%H_%M_%S-%Z).pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Thetcpdumpcapture file’s path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.

Initiate atcpdumpsession on the container and redirect output to a capture file. This example uses49628as the container’s process ID andens5as the interface name. Thensentercommand enters the namespace of a target process and runs a command in its namespace. because the target process in this example is a container’s process ID, thetcpdumpcommand is run in the container’s namespace from the host:

**1**
  Thetcpdumpcapture file’s path is outside of thechrootenvironment because the toolbox container mounts the host’s root directory at/host.
- Provide thetcpdumpcapture file to Red Hat Support for analysis, using one of the following methods.Upload the file to an existing Red Hat support case.Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/my-tcpdump-capture-file.pcap' > /tmp/my-tcpdump-capture-file.pcap$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/my-tcpdump-capture-file.pcap'>/tmp/my-tcpdump-capture-file.pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring atcpdumpcapture file from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy atcpdumpcapture file from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.SelectAttach filesand follow the prompts to upload the file.

Provide thetcpdumpcapture file to Red Hat Support for analysis, using one of the following methods.

- Upload the file to an existing Red Hat support case.Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/my-tcpdump-capture-file.pcap' > /tmp/my-tcpdump-capture-file.pcap$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/my-tcpdump-capture-file.pcap'>/tmp/my-tcpdump-capture-file.pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring atcpdumpcapture file from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy atcpdumpcapture file from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.SelectAttach filesand follow the prompts to upload the file.

Upload the file to an existing Red Hat support case.

- Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/my-tcpdump-capture-file.pcap' > /tmp/my-tcpdump-capture-file.pcap$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/my-tcpdump-capture-file.pcap'>/tmp/my-tcpdump-capture-file.pcap1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring atcpdumpcapture file from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy atcpdumpcapture file from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

Concatenate thesosreportarchive by running theoc debug node/<node_name>command and redirect the output to a file. This command assumes you have exited the previousoc debugsession:

**1**
  The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring atcpdumpcapture file from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy atcpdumpcapture file from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

- Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.
- SelectAttach filesand follow the prompts to upload the file.

## 5.10. Providing diagnostic data to Red Hat SupportCopy linkLink copied to clipboard!

When investigating OpenShift Container Platform issues, Red Hat Support might ask you to upload diagnostic data to a support case. Files can be uploaded to a support case through the Red Hat Customer Portal.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have a Red Hat standard or premium Subscription.
- You have a Red Hat Customer Portal account.
- You have an existing Red Hat Support case ID.

Procedure

- Upload diagnostic data to an existing Red Hat support case through the Red Hat Customer Portal.Concatenate a diagnostic file contained on an OpenShift Container Platform node by using theoc debug node/<node_name>command and redirect the output to a file. The following example copies/host/var/tmp/my-diagnostic-data.tar.gzfrom a debug container to/var/tmp/my-diagnostic-data.tar.gz:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/my-diagnostic-data.tar.gz' > /var/tmp/my-diagnostic-data.tar.gz$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/my-diagnostic-data.tar.gz'>/var/tmp/my-diagnostic-data.tar.gz1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring files from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy diagnostic files from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.SelectAttach filesand follow the prompts to upload the file.

Upload diagnostic data to an existing Red Hat support case through the Red Hat Customer Portal.

- Concatenate a diagnostic file contained on an OpenShift Container Platform node by using theoc debug node/<node_name>command and redirect the output to a file. The following example copies/host/var/tmp/my-diagnostic-data.tar.gzfrom a debug container to/var/tmp/my-diagnostic-data.tar.gz:oc debug node/my-cluster-node -- bash -c 'cat /host/var/tmp/my-diagnostic-data.tar.gz' > /var/tmp/my-diagnostic-data.tar.gz$oc debug node/my-cluster-node --bash-c'cat /host/var/tmp/my-diagnostic-data.tar.gz'>/var/tmp/my-diagnostic-data.tar.gz1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring files from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy diagnostic files from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

Concatenate a diagnostic file contained on an OpenShift Container Platform node by using theoc debug node/<node_name>command and redirect the output to a file. The following example copies/host/var/tmp/my-diagnostic-data.tar.gzfrom a debug container to/var/tmp/my-diagnostic-data.tar.gz:

**1**
  The debug container mounts the host’s root directory at/host. Reference the absolute path from the debug container’s root directory, including/host, when specifying target files for concatenation.

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Transferring files from a cluster node by usingscpis not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to copy diagnostic files from a node by runningscp core@<node>.<cluster_name>.<base_domain>:<file_path> <local_path>.

- Navigate to an existing support case withintheCustomer Supportpageof the Red Hat Customer Portal.
- SelectAttach filesand follow the prompts to upload the file.

## 5.11. About toolboxCopy linkLink copied to clipboard!

toolboxis a tool that starts a container on a Red Hat Enterprise Linux CoreOS (RHCOS) system. The tool is primarily used to start a container that includes the required binaries and plugins that are needed to run commands such assosreport.

The primary purpose for atoolboxcontainer is to gather diagnostic information and to provide it to Red Hat Support. However, if additional diagnostic tools are required, you can add RPM packages or run an image that is an alternative to the standard support tools image.

### 5.11.1. Installing packages to a toolbox containerCopy linkLink copied to clipboard!

By default, running thetoolboxcommand starts a container with theregistry.redhat.io/rhel9/support-tools:latestimage. This image contains the most frequently used support tools. If you need to collect node-specific data that requires a support tool that is not part of the image, you can install additional packages.

Prerequisites

- You have accessed a node with theoc debug node/<node_name>command.
- You can access your system as a user with root privileges.

Procedure

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

- Start the toolbox container:toolbox#toolboxCopy to ClipboardCopied!Toggle word wrapToggle overflow

Start the toolbox container:

- Install the additional package, such aswget:dnf install -y <package_name>#dnfinstall-y<package_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Install the additional package, such aswget:

### 5.11.2. Starting an alternative image with toolboxCopy linkLink copied to clipboard!

By default, running thetoolboxcommand starts a container with theregistry.redhat.io/rhel9/support-tools:latestimage.

You can start an alternative image by creating a.toolboxrcfile and specifying the image to run. However, running an older version of thesupport-toolsimage, such asregistry.redhat.io/rhel8/support-tools:latest, is not supported on OpenShift Container Platform 4.17.

Prerequisites

- You have accessed a node with theoc debug node/<node_name>command.
- You can access your system as a user with root privileges.

Procedure

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

- Optional: If you need to use an alternative image instead of the default image, create a.toolboxrcfile in the home directory for the root user ID, and specify the image metadata:REGISTRY=quay.io             
IMAGE=fedora/fedora:latest   
TOOLBOX_NAME=toolbox-fedora-latestREGISTRY=quay.io1IMAGE=fedora/fedora:latest2TOOLBOX_NAME=toolbox-fedora-latest3Copy to ClipboardCopied!Toggle word wrapToggle overflow1Optional: Specify an alternative container registry.2Specify an alternative image to start.3Optional: Specify an alternative name for the toolbox container.

Optional: If you need to use an alternative image instead of the default image, create a.toolboxrcfile in the home directory for the root user ID, and specify the image metadata:

```
REGISTRY=quay.io             
IMAGE=fedora/fedora:latest   
TOOLBOX_NAME=toolbox-fedora-latest
```

```
IMAGE=fedora/fedora:latest
```

```
TOOLBOX_NAME=toolbox-fedora-latest
```

**1**
  Optional: Specify an alternative container registry.

**2**
  Specify an alternative image to start.

**3**
  Optional: Specify an alternative name for the toolbox container.
- Start a toolbox container by entering the following command:toolbox#toolboxCopy to ClipboardCopied!Toggle word wrapToggle overflowIf an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. To avoid issues withsosreportplugins, remove the running toolbox container withpodman rm toolbox-and then spawn a new toolbox container.

Start a toolbox container by entering the following command:

If an existingtoolboxpod is already running, thetoolboxcommand outputs'toolbox-' already exists. Trying to start…​. To avoid issues withsosreportplugins, remove the running toolbox container withpodman rm toolbox-and then spawn a new toolbox container.
