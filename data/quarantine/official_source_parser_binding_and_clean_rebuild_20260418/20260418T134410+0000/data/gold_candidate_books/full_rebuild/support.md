# 지원

Red Hat offers cluster administrators tools for gathering data for your cluster, monitoring, and troubleshooting.

### Get support

Get support: Visit the Red Hat Customer Portal to review knowledge base articles, submit a support case, and review additional product documentation and resources.

### Remote health monitoring issues

Remote health monitoring issues:
OpenShift Container Platform collects telemetry and configuration data about your cluster and reports it to Red Hat by using the Telemeter Client and the {insights-operator}. Red Hat uses this data to understand and resolve issues in a _connected cluster_. Similar to connected clusters, you can Use remote health monitoring in a restricted network. OpenShift Container Platform collects data and monitors health using the following:

### Remote health monitoring issues

Remote health monitoring issues:
OpenShift Container Platform collects telemetry and configuration data about your cluster and reports it to Red Hat by using the Telemeter Client and the {insights-operator}. Red Hat uses this data to understand and resolve issues in a _connected cluster_. OpenShift Container Platform collects data and monitors health using the following:

* *Telemetry*: The Telemetry Client gathers and uploads the metrics values to Red Hat every four minutes and thirty seconds. Red Hat uses this data to:

** Monitor the clusters.
** Roll out OpenShift Container Platform upgrades.
** Improve the upgrade experience.

* *{insights-operator}*: By default, OpenShift Container Platform installs and enables the {insights-operator}, which reports configuration and component failure status every two hours. The {insights-operator} helps to:

** Identify potential cluster issues proactively.
** Provide a solution and preventive action in {cluster-manager-first}.

You can review telemetry information.

If you have enabled remote health reporting, Using {red-hat-lightspeed} to identify issues with your cluster. You can optionally disable remote health reporting.

### Gather data about your cluster

Gather data about your cluster: Red Hat recommends gathering your debugging information when opening a support case. This helps Red Hat Support to perform a root cause analysis. A cluster administrator can use the following to gather data about your cluster:

* *must-gather tool*: Use the `must-gather` tool to collect information about your cluster and to debug the issues.
* *sosreport*:  Use the `sosreport` tool to collect configuration details, system information, and diagnostic data for debugging purposes.
* *Cluster ID*: Obtain the unique identifier for your cluster, when providing information to Red Hat Support.
* *Bootstrap node journal logs*: Gather `bootkube.service` `journald` unit logs and container logs from the bootstrap node to troubleshoot bootstrap-related issues.
* *Cluster node journal logs*: Gather `journald` unit logs and logs within `/var/log` on individual cluster nodes to troubleshoot node-related issues.
* *Network trace*: Provide a network packet trace from a specific OpenShift Container Platform cluster node or a container to Red Hat Support to help troubleshoot network-related issues.

### Troubleshooting issues

A cluster administrator can monitor and troubleshoot the following OpenShift Container Platform component issues:

* Installation issues: OpenShift Container Platform installation proceeds through various stages. You can perform the following:

** Monitor the installation stages.
** Determine at which stage installation issues occur.
** Investigate multiple installation issues.
** Gather logs from a failed installation.

* Node issues: A cluster administrator can verify and troubleshoot node-related issues by reviewing the status, resource usage, and configuration of a node. You can query the following:

** Kubelet's status on a node.
** Cluster node journal logs.

* Crio issues: A cluster administrator can verify CRI-O container runtime engine status on each cluster node. If you experience container runtime issues, perform the following:

** Gather CRI-O journald unit logs.
** Cleaning CRI-O storage.

* Operating system issues: OpenShift Container Platform  runs on Red Hat Enterprise Linux CoreOS. If you experience operating system issues, you can investigate kernel crash procedures. Ensure the following:

** Enable kdump.
** Test the kdump configuration.
** Analyze a core dump.

* Network issues: To troubleshoot Open vSwitch issues, a cluster administrator can perform the following:

** Configure the Open vSwitch log level temporarily.
** Configure the Open vSwitch log level permanently.
** Display Open vSwitch logs.

* Operator issues: A cluster administrator can do the following to resolve Operator issues:

** Verify Operator subscription status.
** Check Operator pod health.
** Gather Operator logs.

* Pod issues: A cluster administrator can troubleshoot pod-related issues by reviewing the status of a pod and completing the following:

** Review pod and container logs.
** Start debug pods with root access.

* Source-to-image issues: A cluster administrator can observe the S2I stages to determine where in the S2I process a failure occurred. Gather the following to resolve Source-to-Image (S2I) issues:

** Source-to-Image diagnostic data.
** Application diagnostic data to investigate application failure.

* Storage issues: A multi-attach storage error occurs when the mounting volume on a new node is not possible because the failed node cannot unmount the attached volume. A cluster administrator can do the following to resolve multi-attach storage issues:

** Enable multiple attachments by using RWX volumes.
** Recover or delete the failed node when using an RWO volume.

* Monitoring issues: A cluster administrator can follow the procedures on the troubleshooting page for monitoring. If the metrics for your user-defined projects are unavailable or if Prometheus is consuming a lot of disk space, check the following:

** Investigate why user-defined metrics are unavailable.
** Determine why Prometheus is consuming a lot of disk space.

----
* xref :../observability/logging/cluster-logging.adoc#cluster-logging[Logging issues]: A cluster administrator can follow the procedures in the "Support" and "Troubleshooting logging" sections to resolve logging issues:

** xref :../observability/logging/troubleshooting/cluster-logging-cluster-status.adoc#cluster-logging-clo-status_cluster-logging-cluster-status[Viewing the status of the {clo}]
** xref :../observability/logging/troubleshooting/cluster-logging-cluster-status.adoc#cluster-logging-clo-status-comp_cluster-logging-cluster-status[Viewing the status of {logging} components]
** xref :../observability/logging/troubleshooting/troubleshooting-logging-alerts.adoc#troubleshooting-logging-alerts[Troubleshooting logging alerts]
** xref :../observability/logging/cluster-logging-support.adoc#cluster-logging-must-gather-collecting_cluster-logging-support[Collecting information about your logging environment by using the `oc adm must-gather` command]
----

* {oc-first} issues: Investigate {oc-first} issues by increasing the log level.
