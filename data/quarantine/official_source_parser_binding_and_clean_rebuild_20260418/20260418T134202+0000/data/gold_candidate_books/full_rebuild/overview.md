# 개요

## Documentation

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/291_OpenShift_on_AWS_Intro_1122_docs.png" alt="{product-title}" kind="figure" diagram_type="image_figure"]
{product-title}
[/FIGURE]

_Source: `index.adoc` · asset `291_OpenShift_on_AWS_Intro_1122_docs.png`_


{toc}
{toc-title}

Welcome to the official {product-title} {product-version} documentation, where you can learn about {product-title} and start exploring its features.
Welcome to the official {product-title} documentation, where you can learn about {product-title} and start exploring its features.
To learn about {product-title}, interacting with {product-title} by using {cluster-manager-first} and command-line interface (CLI) tools, consumption experience, and integration with Amazon Web Services (AWS) services, start with
xref:../rosa_architecture/about-hcp.adoc#about-hcp[{product-title} overview].
xref:../rosa_architecture/rosa-understanding.adoc#rosa-understanding[the Introduction to ROSA documentation].

To navigate the {product-title} documentation, use the left navigation bar.

To navigate the {product-title} {product-version} documentation, you can use one of the following methods:

* Use the navigation bar to browse the documentation.
* Select the task that interests you from xref:../welcome/learn_more_about_openshift.adoc#learn_more_about_openshift[Learn more about {product-title}].
* {product-title} has a variety of layered offerings to add additional functionality and extend the capabilities of a cluster. For more information, see link:https://access.redhat.com/support/policy/updates/openshift_operators[{product-title} Operator Life Cycles]

To navigate the {product-title} data processing unit (DPU) documentation, use the left navigation bar.

For documentation that is not DPU-specific, see the link:https://docs.openshift.com/container-platform/latest/welcome/index.html[{product-title} documentation].

====
The telco core and telco RAN DU reference design specifications (RDS) are no longer published at this location.

For the latest version of the telco RDS, see link:https://docs.openshift.com/container-platform/{product-version}/scalability_and_performance/telco_ref_design_specs/telco-ref-design-specs-overview.html[Telco core and RAN DU reference design specifications].
====

To navigate the {product-title} documentation, use the navigation bar.

## Introduction to OpenShift Container Platform

{product-title} is a cloud-based Kubernetes container platform. The foundation of {product-title} is based on Kubernetes and therefore shares the same technology. It is designed to allow applications and the data centers that support them to expand from just a few machines and applications to thousands of machines that serve millions of clients.

{product-title} enables you to do the following:

* Provide developers and IT organizations with cloud application platforms that can be used for deploying applications on secure and scalable resources.

* Require minimal configuration and management overhead.

* Bring the Kubernetes platform to customer data centers and cloud.

* Meet security, privacy, compliance, and governance requirements.

With its foundation in Kubernetes, {product-title} incorporates the same technology that serves as the engine for massive telecommunications, streaming video, gaming, banking, and other applications. Its implementation in open Red Hat technologies lets you extend your containerized applications beyond a single cloud to on-premise and multi-cloud environments.

{product-title} is a platform for developing and running containerized applications. It is designed to allow applications and the data centers that support them to expand from just a few machines and applications to thousands of machines that serve millions of clients.

.Additional resources

* xref:../installing/installing_sno/install-sno-preparing-to-install-sno.adoc#preparing-to-install-sno[Preparing to install on a single node]

## Learn more about

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/oke-about-ocp-stack-image.png" alt="Red Hat {oke}" kind="figure" diagram_type="image_figure"]
Red Hat {oke}
[/FIGURE]

_Source: `oke_about.adoc` · asset `oke-about-ocp-stack-image.png`_


Use the following sections to find content to help you learn about and better understand {product-title} functions:

#### Learning and support

| Learn about {product-title} | Optional additional resources |
| --- | --- |
| link:https://www.openshift.com/learn/whats-new[What's new in {product-title}] | - |
| link:https://www.openshift.com/blog?hsLang=en-us[OpenShift blog] | - |
| link:https://access.redhat.com/support/policy/updates/openshift[{product-title} Life Cycle Policy] | - |
| link:https://access.redhat.com/support/policy/updates/openshift#ocp4_phases[{product-title} life cycle] | - |
| link:https://learn.openshift.com/?extIdCarryOver=true&sc_cid=701f2000001Css5AAC[OpenShift Interactive Learning Portal] | - |
| link:https://access.redhat.com/articles/4217411[OpenShift Knowledgebase articles] | - |
| xref:../support/getting-support.adoc#getting-support[Getting Support] | - |
| xref:../support/gathering-cluster-data.adoc#gathering-data[Gathering data about your cluster] | - |

#### Architecture

| Learn about {product-title} | Optional additional resources |
| --- | --- |
| link:https://www.openshift.com/blog/enterprise-kubernetes-with-openshift-part-one?extIdCarryOver=true&sc_cid=701f2000001Css5AAC[Enterprise Kubernetes with OpenShift] | - |
| link:https://access.redhat.com/articles/4128421[Tested platforms] | - |
| xref:../architecture/architecture.adoc#architecture[Architecture] | - |
| xref:../security/container_security/security-understanding.adoc#understanding-security[Security and compliance] | - |
| xref:../networking/networking_overview/understanding-networking.adoc#understanding-networking[Networking] | - |
| xref:../networking/ovn_kubernetes_network_provider/ovn-kubernetes-architecture-assembly.adoc#ovn-kubernetes-architecture-con[OVN-Kubernetes architecture] | - |
| xref:../backup_and_restore/index.adoc#backup-restore-overview[Backup and restore] | - |
| xref:../backup_and_restore/control_plane_backup_and_restore/disaster_recovery/scenario-2-restoring-cluster-state.adoc#scenario-2-restoring-cluster-state[Restoring to a previous cluster state] | - |

#### Installation

Explore the following {product-title} installation tasks:

| Learn about installation on {product-title} | Optional additional resources |
| --- | --- |
| xref:../installing/overview/index.adoc#ocp-installation-overview[{product-title} installation overview] | - |
| xref:../installing/overview/installing-preparing.adoc#installing-preparing[Selecting a cluster installation method and preparing it for users] | - |
| xref:../installing/overview/installing-fips.adoc#installing-fips-mode_installing-fips[Installing a cluster in FIPS mode] | - |
| xref:../installing/installing_with_agent_based_installer/preparing-to-install-with-agent-based-installer.adoc#agent-installer-fips-compliance_preparing-to-install-with-agent-based-installer[About FIPS compliance] | - |

#### Other cluster installer tasks

| Learn about other installer tasks on {product-title} | Optional additional resources |
| --- | --- |
| xref:../installing/validation_and_troubleshooting/installing-troubleshooting.adoc#installing-troubleshooting[Troubleshooting installation issues] | - |
| xref:../installing/validation_and_troubleshooting/validating-an-installation.adoc#validating-an-installation[Validating an installation] | - |
| xref:../storage/persistent_storage/persistent-storage-ocs.adoc#red-hat-openshift-data-foundation[Install {rh-storage-first}] | - |
| xref:../machine_configuration/mco-coreos-layering.adoc#mco-coreos-layering[{image-mode-os-lower}] | - |

##### Install a cluster in a restricted network

| Learn about installing in a restricted network | Optional additional resources a|xref:../disconnected/index.adoc#index[About disconnected installation mirroring] a| If your cluster uses user-provisioned infrastructure, and the cluster does not have full access to the internet, you must mirror the {product-title} installation images. * xref:../installing/installing_aws/upi/installing-restricted-networks-aws.adoc#installing-restricted-networks-aws[{aws-first}] * xref:../installing/installing_gcp/installing-restricted-networks-gcp.adoc#installing-restricted-networks-gcp[{gcp-short}] * xref:../installing/installing_vsphere/upi/installing-restricted-networks-vsphere.adoc#installing-restricted-networks-vsphere[{vmw-short}] * xref:../installing/installing_ibm_cloud/installing-ibm-cloud-restricted.adoc#installing-ibm-cloud-restricted[{ibm-cloud-name}] * xref:../installing/installing_ibm_z/preparing-to-install-on-ibm-z.adoc#preparing-to-install-on-ibm-z[{ibm-z-name} and {ibm-linuxone-name}] * xref:../installing/installing_ibm_power/installing-restricted-networks-ibm-power.adoc#installing-restricted-networks-ibm-power[{ibm-power-name}] * xref:../installing/installing_bare_metal/upi/installing-restricted-networks-bare-metal.adoc#installing-restricted-networks-bare-metal[bare metal] |
| --- | --- |

##### Install a cluster in an existing network

| Learn about installing in a restricted network | Optional additional resources |
| --- | --- |
| If you use an existing Virtual Private Cloud (VPC) in xref:../installing/installing_aws/ipi/installing-aws-vpc.adoc#installing-aws-vpc[{aws-first}] or xref:../installing/installing_gcp/installing-gcp-vpc.adoc#installing-gcp-vpc[{gcp-short}] or an existing xref:../installing/installing_azure/ipi/installing-azure-vnet.adoc#installing-azure-vnet[VNet] on Microsoft Azure, you can install a cluster | - |
| xref:../installing/installing_gcp/installing-gcp-shared-vpc.adoc#installation-gcp-shared-vpc-prerequisites_installing-gcp-shared-vpc[Installing a cluster on {gcp-short} into a shared VPC] | - |

#### Cluster Administrator

| Learn about {product-title} cluster activities | Optional additional resources |
| --- | --- |
| xref:../architecture/architecture.adoc#architecture-overview-architecture[Understand {product-title} management] a|* xref:../machine_management/index.adoc#machine-api-overview_overview-of-machine-management[Machine API] * xref:../architecture/control-plane.adoc#operators-overview_control-plane[Operators] * * xref:../etcd/etcd-overview.adoc#etc-overview[etcd] | - |
| xref:../installing/overview/cluster-capabilities.adoc#enabling-cluster-capabilities_cluster-capabilities[Enable cluster capabilities] | - |
| xref:../installing/overview/cluster-capabilities.adoc#explanation_of_capabilities_cluster-capabilities[Optional cluster capabilities in {product-title} {product-version}] | - |

##### Managing and changing cluster components

###### Managing cluster components

| Learn about managing cluster components | Optional additional resources |
| --- | --- |
| Manage xref:../machine_management/index.adoc#machine-mgmt-intro-managing-compute_overview-of-machine-management[compute] and xref:../machine_management/index.adoc#machine-mgmt-intro-managing-control-plane_overview-of-machine-management[control plane] machines with machine sets | - |
| xref:../machine_management/deploying-machine-health-checks.adoc#deploying-machine-health-checks[Deploy machine health checks] | - |
| xref:../machine_management/applying-autoscaling.adoc#applying-autoscaling[Apply autoscaling to an {product-title} cluster] | - |
| xref:../nodes/pods/nodes-pods-priority.adoc#nodes-pods-priority[Including pod priority in pod scheduling decisions] | - |
| xref:../registry/index.adoc#registry-overview[Manage container registries] | - |
| link:https://access.redhat.com/documentation/en-us/red_hat_quay/[{quay}] | - |
| xref:../authentication/understanding-authentication.adoc#understanding-authentication[Manage users and groups] | - |
| xref:../authentication/impersonating-system-admin.adoc#impersonating-system-admin[Impersonating the system:admin user] | - |
| xref:../authentication/understanding-authentication.adoc#understanding-authentication[Manage authentication] | - |
| xref:../authentication/understanding-identity-provider.adoc#supported-identity-providers[Multiple identity providers] | - |
| Manage xref:../security/certificates/replacing-default-ingress-certificate.adoc#replacing-default-ingress[Ingress], xref:../security/certificates/api-server.adoc#api-server-certificates[API server], and xref:../security/certificates/service-serving-certificate.adoc#add-service-serving[Service] certificates | - |
| xref:../networking/network_security/network-policy-apis.adoc#network-policy-apis[Network security] | - |
| xref:../networking/networking_overview/understanding-networking.adoc#understanding-networking[Manage networking] a|* xref:../networking/networking_operators/cluster-network-operator.adoc#nw-cluster-network-operator_cluster-network-operator[Cluster Network Operator] * xref:../networking/multiple_networks/understanding-multiple-networks.adoc#understanding-multiple-networks[Multiple network interfaces] * xref:../networking/network_security/network_policy/about-network-policy.adoc#about-network-policy[Network policy] | - |
| xref:../operators/understanding/olm-understanding-software-catalog.adoc#olm-understanding-software-catalog[Manage Operators] | - |
| xref:../operators/user/olm-creating-apps-from-installed-operators.adoc#olm-creating-apps-from-installed-operators[Creating applications from installed Operators] | - |

Hiding until WMCO 10.19.0 releases, replace as the last row of the above table after WMCO GAs
| xref:../windows_containers/index.adoc#index[{productwinc} overview]
| windows_containers/understanding-windows-container-workloads.adoc#understanding-windows-container-workloads_understanding-windows-container-workloads[Understanding Windows container workloads]

###### Changing cluster components

| Learn more about changing cluster components | Optional additional resources |
| --- | --- |
| xref:../updating/understanding_updates/intro-to-updates.adoc#intro-to-updates[Introduction to OpenShift updates] a|* xref:../updating/updating_a_cluster/updating-cluster-web-console.adoc#updating-cluster-web-console[Updating a cluster using the web console] * xref:../updating/updating_a_cluster/updating-cluster-cli.adoc#updating-cluster-cli[Updating using the CLI] * xref:../disconnected/updating/index.adoc#about-disconnected-updates[Using the OpenShift Update Service in a disconnected environment] | - |
| xref:../operators/understanding/crds/crd-extending-api-with-crds.adoc#crd-extending-api-with-crds[Use custom resource definitions (CRDs) to modify the cluster] a|* xref:../operators/understanding/crds/crd-extending-api-with-crds.adoc#crd-creating-custom-resources-definition_crd-extending-api-with-crds[Create a CRD] * xref:../operators/understanding/crds/crd-managing-resources-from-crds.adoc#crd-managing-resources-from-crds[Manage resources from CRDs] | - |
| xref:../applications/quotas/quotas-setting-per-project.adoc#quotas-setting-per-project[Set resource quotas] | - |
| xref:../applications/quotas/quotas-setting-across-multiple-projects.adoc#quotas-setting-across-multiple-projects[Resource quotas across multiple projects] | - |
| xref:../applications/pruning-objects.adoc#pruning-objects[Prune and reclaim resources] | - |
| xref:../cicd/builds/advanced-build-operations.adoc#builds-build-pruning-advanced-build-operations[Performing advanced builds] | - |
| xref:../scalability_and_performance/recommended-performance-scale-practices/recommended-infrastructure-practices.adoc#scaling-cluster-monitoring-operator[Scale] and xref:../scalability_and_performance/using-node-tuning-operator.adoc#using-node-tuning-operator[tune] clusters | - |
| xref:../scalability_and_performance/index.adoc#scalability-and-performance-overview[{product-title} scalability and performance] | - |

#### Observe a cluster

| Learn about {product-title} | Optional additional resources |
| --- | --- |
| link:https://docs.redhat.com/en/documentation/red_hat_openshift_distributed_tracing_platform/latest/html/release_notes_for_the_distributed_tracing_platform/distr-tracing-rn[Release notes for the {DTProductName}] | - |
| link:https://docs.redhat.com/en/documentation/red_hat_openshift_distributed_tracing_platform/latest[{DTProductName}] | - |
| link:https://docs.redhat.com/en/documentation/red_hat_build_of_opentelemetry/latest/html/installing_red_hat_build_of_opentelemetry/install-otel[Red Hat build of OpenTelemetry] | - |
| link:https://docs.redhat.com/en/documentation/red_hat_build_of_opentelemetry/latest/html/receiving_telemetry_data/otel-receiving-telemetry-data[Receiving telemetry data from multiple clusters] | - |
| xref:../observability/network_observability/network-observability-overview.adoc#network-observability-overview[About Network Observability] a|* xref:../observability/network_observability/metrics-alerts-dashboards.adoc#metrics-alerts-dashboards_metrics-alerts-dashboards[Using metrics with dashboards and alerts] * xref:../observability/network_observability/observing-network-traffic.adoc#network-observability-trafficflow_nw-observe-network-traffic[Observing the network traffic from the Traffic flows view] | - |
| link:https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/about_monitoring/about-ocp-monitoring[About {product-title} monitoring] a|* xref:../support/remote_health_monitoring/about-remote-health-monitoring.adoc#about-remote-health-monitoring_about-remote-health-monitoring[Remote health monitoring] * xref:../observability/power_monitoring/power-monitoring-overview.adoc#power-monitoring-overview[{PM-title-c} (Technology Preview)] | - |

#### Storage activities

| Learn about {product-title} | Optional additional resources |
| --- | --- |
| xref:../storage/index.adoc#storage-types[Storage types] a| * xref:../storage/understanding-persistent-storage.adoc#understanding-persistent-storage[Persistent storage] * xref:../storage/understanding-ephemeral-storage.adoc#understanding-ephemeral-storage[Ephemeral storage] | - |

#### Application Site Reliability Engineer (App SRE)

| Learn about {product-title} | Optional additional resources |
| --- | --- |
| xref:../applications/index.adoc#building-applications-overview[Building applications overview] | - |
| xref:../applications/projects/working-with-projects.adoc#working-with-projects[Projects] | - |
| xref:../operators/understanding/olm-what-operators-are.adoc#olm-what-operators-are[Operators] | - |
| xref:../operators/operator-reference.adoc#cluster-operator-reference[Cluster Operator reference] | - |

#### Developer

{product-title} is a platform for developing and deploying containerized applications. Read the following {product-title} documentation, so that you can better understand {product-title} functions:

| Learn about application development in {product-title} | Optional additional resources |
| --- | --- |
| link:https://developers.redhat.com/products/openshift/getting-started#assembly-field-sections-13455[Getting started with OpenShift for developers (interactive tutorial)] a|* xref:../architecture/understanding-development.adoc#understanding-development[Understanding {product-title} development] * xref:../applications/projects/working-with-projects.adoc#working-with-projects[Working with projects] * xref:../applications/deployments/what-deployments-are.adoc#what-deployments-are[Create deployments] | - |
| link:https://developers.redhat.com/[Red Hat Developers site] | - |
| xref:../cicd/builds/understanding-image-builds.adoc#understanding-image-builds[Understanding image builds] | - |
| link:https://developers.redhat.com/products/openshift-dev-spaces/overview[{openshift-dev-spaces-productname} (formerly Red Hat CodeReady Workspaces)] | - |
| xref:../operators/understanding/olm-what-operators-are.adoc#olm-what-operators-are[Operators] | - |
| xref:../openshift_images/index.adoc#overview-of-images[Create container images] | - |
| xref:../openshift_images/managing_images/managing-images-overview.adoc#managing-images-overview[Managing images overview] | - |
| link:https://odo.dev/docs/introduction/[`odo`] | - |
| xref:../cli_reference/odo-important-update.adoc#odo-important_update[Developer-focused CLI] | - |
| xref:../applications/odc-viewing-application-composition-using-topology-view.adoc#odc-viewing-application-topology_viewing-application-composition-using-topology-view[Viewing application composition using the Topology view] | - |
| xref:../applications/odc-exporting-applications.adoc#odc-exporting-applications[Exporting applications] | - |
| link:https://docs.openshift.com/pipelines/1.15/about/understanding-openshift-pipelines.html[Understanding {pipelines-shortname}] | - |
| link:https://docs.openshift.com/pipelines/latest/create/creating-applications-with-cicd-pipelines.html[Create CI/CD Pipelines] | - |
| link:https://docs.openshift.com/gitops/latest/declarative_clusterconfig/configuring-an-openshift-cluster-by-deploying-an-application-with-cluster-configurations.html[Configuring an OpenShift cluster by deploying an application with cluster configurations] a|* xref:../nodes/scheduling/nodes-scheduler-taints-tolerations.adoc#nodes-scheduler-taints-tolerations[Controlling pod placement using node taints] * xref:../machine_management/creating-infrastructure-machinesets.adoc#creating-infrastructure-machinesets[Creating infrastructure machine sets] | - |

#### 

| Learn about {hcp} | Optional additional resources |
| --- | --- |
| xref:../hosted_control_planes/index.adoc#hosted-control-planes-overview[Hosted control planes overview] a| xref:../hosted_control_planes/index.adoc#hosted-control-planes-version-support_hcp-overview[Versioning for {hcp}] | - |
| Preparing to deploy a| * xref:../hosted_control_planes/hcp-prepare/hcp-requirements.adoc#hcp-requirements[Requirements for {hcp}] * xref:../hosted_control_planes/hcp-prepare/hcp-sizing-guidance.adoc#hcp-sizing-guidance[Sizing guidance for {hcp}] * xref:../hosted_control_planes/hcp-prepare/hcp-override-resource-util.adoc#hcp-override-resource-util[Overriding resource utilization measurements] * xref:../hosted_control_planes/hcp-prepare/hcp-cli.adoc#hcp-cli[Installing the {hcp} command-line interface] * xref:../hosted_control_planes/hcp-prepare/hcp-distribute-workloads.adoc#hcp-distribute-workloads[Distributing hosted cluster workloads] * xref:../hosted_control_planes/hcp-prepare/hcp-enable-disable.adoc#hcp-enable-disable[Enabling or disabling the {hcp} feature] | - |
| Deploying {hcp} a| * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-virt.adoc#hcp-deploy-virt[Deploying {hcp} on {VirtProductName}] * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-aws.adoc#hcp-deploy-aws[Deploying {hcp} on {aws-short}] * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-bm.adoc#hcp-deploy-bm[Deploying {hcp} on bare metal] * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-non-bm.adoc#hcp-deploy-non-bm[Deploying {hcp} on non-bare-metal agent machines] * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-ibmz.adoc#hcp-deploy-ibmz[Deploying {hcp} on {ibm-z-title}] * xref:../hosted_control_planes/hcp-deploy/hcp-deploy-ibm-power.adoc#hcp-deploy-ibm-power[Deploying {hcp} on {ibm-power-title}] | - |
| Deploying {hcp} in a disconnected environment a| * xref:../hosted_control_planes/hcp-disconnected/hcp-deploy-dc-bm.adoc#hcp-deploy-dc-bm[Deploying {hcp} on bare metal in a disconnected environment] * xref:../hosted_control_planes/hcp-disconnected/hcp-deploy-dc-virt.adoc#hcp-deploy-dc-virt[Deploying {hcp} on {VirtProductName} in a disconnected environment] | - |
| xref:../hosted_control_planes/hcp-troubleshooting.adoc#hcp-troubleshooting[Troubleshooting {hcp}] a| xref:../hosted_control_planes/hcp-troubleshooting.adoc#hosted-control-planes-troubleshooting_hcp-troubleshooting[Gathering information to troubleshoot {hcp}] | - |

## Kubernetes overview

[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/247-OpenShift-Kubernetes-Overview.png" alt="247-OpenShift-Kubernetes-Overview" kind="figure" diagram_type="image_figure"]
247-OpenShift-Kubernetes-Overview
[/FIGURE]

_Source: `kubernetes-overview.adoc` · asset `247-OpenShift-Kubernetes-Overview.png`_


[FIGURE src="/playbooks/wiki-assets/full_rebuild/overview/247_OpenShift_Kubernetes_Overview-2.png" alt="247 OpenShift Kubernetes Overview-2" kind="figure" diagram_type="image_figure"]
247 OpenShift Kubernetes Overview-2
[/FIGURE]

_Source: `kubernetes-overview.adoc` · asset `247_OpenShift_Kubernetes_Overview-2.png`_


Kubernetes is an open source container orchestration tool developed by Google. You can run and manage container-based workloads by using Kubernetes. The most common Kubernetes use case is to deploy an array of interconnected microservices, building an application in a cloud native way. You can create Kubernetes clusters that can span hosts across on-premise, public, private, or hybrid clouds.

Traditionally, applications were deployed on top of a single operating system. With virtualization, you can split the physical host into several virtual hosts. Working on virtual instances on shared resources is not optimal for efficiency and scalability. Because a virtual machine (VM) consumes as many resources as a physical machine, providing resources to a VM such as CPU, RAM, and storage can be expensive. Also, you might see your application degrading in performance due to virtual instance usage on shared resources.

.Evolution of container technologies for classical deployments

To solve this problem, you can use containerization technologies that segregate applications in a containerized environment. Similar to a VM, a container has its own filesystem, vCPU, memory, process space, dependencies, and more. Containers are decoupled from the underlying infrastructure, and are portable across clouds and OS distributions. Containers are inherently much lighter than a fully-featured OS, and are lightweight isolated processes that run on the operating system kernel. VMs are slower to boot, and are an abstraction of physical hardware. VMs run on a single machine with the help of a hypervisor.

You can perform the following actions by using Kubernetes:

* Sharing resources
* Orchestrating containers across multiple hosts
* Installing new hardware configurations
* Running health checks and self-healing applications
* Scaling containerized applications

.Architecture of Kubernetes

A cluster is a single computational unit consisting of multiple nodes in a cloud environment. A Kubernetes cluster includes a control plane and worker nodes. You can run Kubernetes containers across various machines and environments. The control plane node controls and maintains the state of a cluster. You can run the Kubernetes application by using worker nodes. You can use the Kubernetes namespace to differentiate cluster resources in a cluster. Namespace scoping is applicable for resource objects, such as deployment, service, and pods. You cannot use namespace for cluster-wide resource objects such as storage class, nodes, and persistent volumes.

## Red Hat OpenShift editions

Red{nbsp}Hat OpenShift is offered in several editions to support a wide range of deployment models and operational preferences. Each edition delivers a consistent Kubernetes platform with integrated tools, security features, and developer experiences. OpenShift is available in cloud services and self-managed editions.

#### Cloud services editions

Red{nbsp}Hat OpenShift offers various cloud service editions to cater to different organizational needs. These editions provide fully managed application platforms from major cloud providers.

{product-rosa} (ROSA):: A fully managed application platform that helps organizations build, deploy, and scale applications in a native AWS environment.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/aws[{product-rosa}].

{azure-first} Red{nbsp}Hat OpenShift:: A fully managed application platform that helps organizations build, deploy, and scale applications on Azure.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/azure[{azure-first} Red{nbsp}Hat OpenShift].

{product-dedicated}:: A managed Red{nbsp}Hat OpenShift offering available on {gcp-first}.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/dedicated[{product-dedicated}].

Red{nbsp}Hat OpenShift on {ibm-cloud-title}:: A managed OpenShift cloud service that reduces operational complexity and helps developers build and scale applications on {ibm-cloud-title}.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/ibm[Red{nbsp}Hat OpenShift on {ibm-cloud-title}].

#### Self-managed editions

Red{nbsp}Hat OpenShift offers self-managed editions for organizations that prefer to deploy, configure, and manage OpenShift on their own infrastructure. These editions provide flexibility and control over the platform while leveraging the capabilities of OpenShift.

Red{nbsp}Hat {product-title} (OCP)::
Provides complete set of operations and developer services and tools for building and scaling containerized applications.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/container-platform[Red{nbsp}Hat {product-title}].

Red{nbsp}Hat {opp}::
Builds on the capabilities of {product-title}.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/platform-plus[Red{nbsp}Hat {opp}].

Red{nbsp}Hat {oke}::
Delivers the foundational, security-focused capabilities of enterprise Kubernetes on {op-system-first} to run containers in hybrid cloud environments.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/kubernetes-engine[Red Hat {oke}].

{ove-first}::
Provides the virtualization capabilities of Red Hat OpenShift in a streamlined, cost-effective solution to deploy, manage, and scale VMs exclusively.
For more information, see link:https://www.redhat.com/en/technologies/cloud-computing/openshift/virtualization-engine[{ove-first}].

## Glossary of common terms for

This glossary defines common Kubernetes and {product-title} terms.

access policies::
A set of roles that dictate how users, applications, and entities within a cluster interact with one another. An access policy increases cluster security.

admission plugins::
Admission plugins enforce security policies, resource limitations, or configuration requirements.

authentication::
To control access to an {product-title} cluster, a cluster administrator can configure user authentication to ensure only approved users access the cluster. To interact with an {product-title} cluster, you must authenticate with the {product-title} API. You can authenticate by providing an OAuth access token or an X.509 client certificate in your requests to the {product-title} API.
To control access to a {product-title} cluster, an administrator with the `dedicated-admin` role can configure user authentication to ensure only approved users access the cluster. To interact with a {product-title} cluster, you must authenticate with the {product-title} API. You can authenticate by providing an OAuth access token or an X.509 client certificate in your requests to the {product-title} API.
To control access to an {product-title} cluster, an administrator with the `dedicated-admin` role can configure user authentication to ensure only approved users access the cluster. To interact with an {product-title} cluster, you must authenticate with the {product-title} API. You can authenticate by providing an OAuth access token or an X.509 client certificate in your requests to the {product-title} API.

bootstrap::
A temporary machine that runs minimal Kubernetes and deploys the {product-title} control plane.

build::
A build is the process of transforming input parameters, such as source code, into a runnable container image. This process is defined by a BuildConfig object, which specifies the entire build workflow. {product-title} utilizes Kubernetes to create containers from the build images and push them to the integrated container registry.

certificate signing requests (CSRs)::
A resource requests a denoted signer to sign a certificate. This request might get approved or denied.

Cluster Version Operator (CVO)::
An Operator that checks with the {product-title} Update Service to see the valid updates and update paths based on current component versions and information in the graph.

compute nodes::
Nodes that are responsible for executing workloads for cluster users.

configuration drift::
A situation where the configuration on a node does not match what the machine config specifies.

container::
Container is a lightweight, portable application instance that runs in OCI-compliant environments on compute nodes. Each container is a runtime instance of an Open Container Initiative (OCI)-compliant image, which is a binary package containing the application and its dependencies. A single compute node can host multiple containers, with its capacity determined by the memory and CPU resources available, whether on cloud infrastructure, physical hardware, or virtualized environments.

container orchestration engine::
Software that automates the deployment, management, scaling, and networking of containers.

container workloads::
Applications that are packaged and deployed in containers.

control groups (cgroups)::
Partitions sets of processes into groups to manage and limit the resources processes consume.

control plane::
A container orchestration layer that exposes the API and interfaces to define, deploy, and manage the life cycle of containers. Control planes are also known as control plane machines.

CRI-O::
A Kubernetes native container runtime implementation that integrates with the operating system to deliver an efficient Kubernetes experience.

Deployment and DeploymentConfig::
{product-title} supports both Kubernetes Deployment objects and {product-title} DeploymentConfig objects for managing application rollout and scaling.
+
A Deployment object defines how an application is deployed as pods. It specifies the container image to pull from the registry, the number of replicas to maintain, and the labels that guide scheduling onto compute nodes. The Deployment creates and manages a ReplicaSet, which ensures the specified number of pods are running. Additionally, Deployment objects support various rollout strategies to update pods while maintaining application availability.
+
A DeploymentConfig object extends Deployment functionality by introducing change triggers, which automatically create new deployment versions when a new container image version becomes available or when other defined changes occur. This enables automated rollout management within {product-title}.

Dockerfile::
A text file that contains the user commands to perform on a terminal to assemble the image.

hosted control planes::
A {product-title} feature that enables hosting a control plane on the {product-title} cluster from its data plane and workers. This model performs the following actions:
+
* Optimize infrastructure costs required for the control planes.
* Improve the cluster creation time.
* Enable hosting the control plane using the Kubernetes native high level primitives. For example, deployments and stateful sets.
* Allow a strong network segmentation between the control plane and workloads.
hosted control planes::
A {product-title} feature that enables hosting a control plane on the {product-title} cluster from its data plane and workers. This model performs the following actions:

* Optimize infrastructure costs required for the control planes.
* Improve the cluster creation time.
* Enable hosting the control plane using the Kubernetes native high level primitives. For example, deployments and stateful sets.
* Allow a strong network segmentation between the control plane and workloads.

hybrid cloud deployments::
Deployments that deliver a consistent platform across bare metal, virtual, private, and public cloud environments. This offers speed, agility, and portability.

Ignition::
A utility that {op-system} uses to manipulate disks during initial configuration. It completes common disk tasks, including partitioning disks, formatting partitions, writing files, and configuring users.

installer-provisioned infrastructure::
The installation program deploys and configures the infrastructure that the cluster runs on.

kubelet::
A primary node agent that runs on each node in the cluster to ensure that containers are running in a pod.

Kubernetes::
Kubernetes is an open source container orchestration engine for automating deployment, scaling, and management of containerized applications.

kubernetes manifest::
Specifications of a Kubernetes API object in a JSON or YAML format. A configuration file can include deployments, config maps, secrets, daemon sets.

Machine Config Daemon (MCD)::
A daemon that regularly checks the nodes for configuration drift.

Machine Config Operator (MCO)::
An Operator that applies the new configuration to your cluster machines.

machine config pools (MCP)::
A group of machines, such as control plane components or user workloads, that are based on the resources that they handle.

metadata::
Additional information about cluster deployment artifacts.

microservices::
An approach to writing software. Applications can be separated into the smallest components, independent from each other by using microservices.

mirror registry::
A registry that holds the mirror of {product-title} images.

monolithic applications::
Applications that are self-contained, built, and packaged as a single piece.

namespaces::
A namespace isolates specific system resources that are visible to all processes. Inside a namespace, only processes that are members of that namespace can see those resources.

networking::
Network information of {product-title} cluster.

node::
A compute machine in the {product-title} cluster. A node is either a virtual machine (VM) or a physical machine.

OpenShift CLI (`oc`)::
A command line tool to run {product-title} commands on the terminal.

OpenShift Dedicated::
A managed {op-system-base} {product-title} offering on Amazon Web Services (AWS) and {gcp-first}. OpenShift Dedicated focuses on building and scaling applications.

OpenShift Update Service (OSUS)::
For clusters with internet access, {op-system-base-full} provides over-the-air updates by using an OpenShift update service as a hosted service located behind public APIs.

{product-registry}::
A registry provided by {product-title} to manage images.

Operator::
The preferred method of packaging, deploying, and managing a Kubernetes application in
a
an
{product-title} cluster. An Operator is a Kubernetes-native application designed to translate operational knowledge into a software that is packaged and shared with customers. Traditionally, tasks such as installation, configuration, scaling, updates, and failover were managed manually by administrators by using scripts or automation tools like Ansible. Operators bring these capabilities into Kubernetes, making them natively integrated and automated within the cluster.
+
Operators manage both Day 1 operations such as installation and configuration, and Day 2 operations such as scaling, updates, backups, failover and restores. By leveraging Kubernetes APIs and concepts, Operators provide an automated and consistent way to manage complex applications.

OperatorHub::
A platform that contains various {product-title} Operators to install.

Operator Lifecycle Manager (OLM)::
OLM helps you to install, update, and manage the lifecycle of Kubernetes native applications. OLM is an open source toolkit designed to manage Operators in an effective, automated, and scalable way.

OSTree::
An upgrade system for Linux-based operating systems that performs atomic upgrades of complete file system trees. OSTree tracks meaningful changes to the file system tree using an addressable object store, and is designed to complement existing package management systems.

over-the-air (OTA) updates::
The {product-title} Update Service (OSUS) provides over-the-air updates to {product-title}, including {op-system-first}.

pod::
A pod is one or more containers deployed together on one host. It consists of a colocated group of containers with shared resources such as volumes and IP addresses. A pod is also the smallest compute unit defined, deployed, and managed.
In {product-title}, pods replace individual application containers as the smallest deployable unit.
Pods are the orchestrated unit in {product-title}. {product-title} schedules and runs all containers in a pod on the same node. Complex applications are made up of multiple pods, each with their own containers. They interact externally and also with another inside the {product-title} environment.

private registry::
{product-title} can use any server implementing the container image registry API as a source of the image which helps the developers to push and pull their private container images.

project::
{product-title} uses projects to enable groups of users or developers to work together. A project defines the scope of resources, manages user access, and enforces resource quotas and limits.
+
A project is a Kubernetes namespace with additional annotations that provide role-based access control (RBAC) and management capabilities. It serves as the central mechanism for organizing resources, ensuring isolation between different user groups.

public registry::
{product-title} can use any server implementing the container image registry API as a source of the image which allows the developers to push and pull their public container images.

{op-system-base} {product-title} Cluster Manager::
A managed service where you can install, modify, operate, and upgrade your {product-title} clusters.

{op-system-base} Quay Container Registry::
A Quay.io container registry that serves most of the container images and Operators to {product-title} clusters.

replication controllers::
An asset that indicates how many pod replicas are required to run at a time.

ReplicaSet and ReplicationController::
The Kubernetes `ReplicaSet` and `ReplicationController` objects ensure that the desired number of pod replicas are running at all times. If a pod fails, exits, or is deleted, these controllers automatically create new pods to maintain the specified replica count. Conversely, if there are more pods than required, the ReplicaSet or ReplicationController scales down by terminating excess pods to match the defined replica count.

role-based access control (RBAC)::
A key security control to ensure that cluster users and workloads have only access to resources required to execute their roles.

route::
A route is a way to expose a service by giving it an externally reachable hostname, such as www.example.com. Each route consists of a route name, a service selector, and optionally, a security configuration.

router::
A router processes defined routes and their associated service endpoints, enabling external clients to access applications. While deploying a multi-tier application in {product-title} is straightforward, external traffic cannot reach the application without the routing layer.

scaling::
The increasing or decreasing of resource capacity.

service::
A service in {product-title} defines a logical set of pods and the access policies for reaching them. It provides a stable internal IP address and hostname, ensuring seamless communication between application components as pods are created and destroyed.

Source-to-Image (S2I) image::
An image created based on the programming language of the application source code in {product-title} to deploy applications.

storage::
{product-title} supports many types of storage, both for on-premise and cloud providers. You can manage container storage for persistent and non-persistent data in an {product-title} cluster.
{product-title} supports many types of storage for cloud providers. You can manage container storage for persistent and non-persistent data in a {product-title} cluster.
{product-title} supports many types of storage for cloud providers. You can manage container storage for persistent and non-persistent data in an {product-title} cluster.

telemetry::
A component to collect information such as size, health, and status of {product-title}.

template::
A template describes a set of objects that can be parameterized and processed to produce a list of objects for creation by {product-title}.

user-provisioned infrastructure::
You can install {product-title} on the infrastructure that you provide. You can use the installation program to generate the assets required to provision the cluster infrastructure, create the cluster infrastructure, and then deploy the cluster to the infrastructure that you provided.

web console::
A user interface (UI) to manage {product-title}.

## About

As of 27 April 2020, Red Hat has decided to rename Red Hat OpenShift Container Engine to Red Hat {oke}
to better communicate what value the product offering delivers.

Red Hat {oke} is a product offering from Red Hat that lets
you use an enterprise class Kubernetes platform as a production platform for
launching containers. You download and install {oke} the same way as {product-title}
as they are the same binary distribution, but {oke} offers a subset of the
features that {product-title} offers.

#### Similarities and differences

You can see the similarities and differences between {oke}
and {product-title} in the following table:

.Product comparison for {oke} and {product-title}
| Yes |
| --- |
| Yes 2+h|Over the Air Smart Upgrades |
| Yes |
| Yes 2+h|Enterprise Secured Kubernetes |
| Yes |
| Yes 2+h|Kubectl and oc automated command line |
| Yes |
| Yes 2+h|Operator Lifecycle Manager (OLM) |
| Yes |
| Yes 2+h|Administrator Web console |
| Yes |
| Yes 2+h|OpenShift Virtualization |
| Yes |
| Yes 2+h|User Workload Monitoring |
| Yes 2+h|Cluster Monitoring |
| Yes |
| Yes 2+h|Cost Management SaaS Service |
| Yes |
| Yes 2+h|Platform Logging |
| Yes 2+h|Developer Web Console |
| Yes 2+h|Developer Application Catalog |
| Yes 2+h|Source to Image and Builder Automation (Tekton) |
| Yes 2+h|OpenShift Service Mesh (Maistra and Kiali) |
| Yes 2+h|{DTShortName} |
| Yes 2+h|OpenShift Serverless (Knative) |
| Yes 2+h|OpenShift Pipelines (Jenkins and Tekton) |
| Yes 2+h|Embedded Component of {ibm-cloud-name} Pak and RHT MW Bundles |
| Yes 2+h|{osc} |
| Yes |

##### Core Kubernetes and container orchestration

{oke} offers full access to an enterprise-ready Kubernetes environment that is
easy to install and offers an extensive compatibility test matrix with many of
the software elements that you might use in your data center.

{oke} offers the same service level agreements, bug fixes, and common
vulnerabilities and errors protection as {product-title}. {oke} includes a
{op-system-base-full} Virtual Datacenter and {op-system-first} entitlement that
allows you to use an integrated Linux operating system with container runtime
from the same technology provider.

The {oke} subscription is compatible with the {productwinc} subscription.

##### Enterprise-ready configurations

{oke} uses the same security options and default settings as the {product-title}.
Default security context constraints, pod security policies, best practice
network and storage settings, service account configuration, SELinux integration,
HAproxy edge routing configuration, and all other standard protections that
{product-title} offers are available in {oke}. {oke} offers full access to the
integrated monitoring solution that {product-title} uses, which is based on
Prometheus and offers deep coverage and alerting for common Kubernetes issues.

{oke} uses the same installation and upgrade automation as {product-title}.

##### Standard infrastructure services

With an {oke} subscription, you receive support for all storage plugins that
{product-title} supports.

In terms of networking, {oke} offers full and
supported access to the Kubernetes Container Network Interface (CNI) and
therefore allows you to use any third-party SDN that supports {product-title}.
It also allows you to use the included Open vSwitch software defined network to
its fullest extent. {oke} allows you to take full advantage of the OVN
Kubernetes overlay, Multus, and Multus plugins that are supported on
{product-title}. {oke} allows customers to use a Kubernetes Network Policy to
create microsegmentation between deployed application services on the cluster.

You can also use the `Route` API objects that are found in {product-title},
including its sophisticated integration with the HAproxy edge routing layer as an
out of the box Kubernetes Ingress Controller.

##### Core user experience

{oke} users have full access to Kubernetes Operators, pod deployment strategies,
Helm, and {product-title} templates. {oke} users can use both the `oc` and
`kubectl` command-line interfaces. {oke} also offers an administrator web-based
console that shows all aspects of the deployed container services and offers a
container-as-a service experience. {oke} grants access to the Operator Life
Cycle Manager that helps you control access to content on the cluster and life
cycle operator-enabled services that you use. With an {oke} subscription, you
receive access to the Kubernetes namespace, the OpenShift `Project` API object,
and cluster-level Prometheus monitoring metrics and events.

##### Maintained and curated content

With an {oke} subscription, you receive access to the {product-title}
content from the Red Hat Ecosystem Catalog and Red Hat Connect ISV marketplace.
You can access all maintained and curated content that the {product-title}
eco-system offers.

##### OpenShift Data Foundation compatible

{oke} is compatible and supported with your purchase of {rh-storage}.

##### Red Hat Middleware compatible

{oke} is compatible and supported with individual Red Hat Middleware product solutions.
Red Hat Middleware Bundles that include OpenShift embedded in them only contain
{product-title}.

##### OpenShift Serverless

{oke} does not include OpenShift Serverless support. Use {product-title}
for this support.

##### Quay Integration compatible

{oke} is compatible and supported with a {quay} purchase.

##### OpenShift Virtualization

{oke} includes support for the Red Hat product offerings derived from
the kubevirt.io open source project.

##### Advanced cluster management

{oke} is compatible with your additional purchase of {rh-rhacm-first} for
Kubernetes. An {oke} subscription does not offer a cluster-wide log aggregation
solution.
{SMProductName} capabilities derived from the open-source istio.io and kiali.io
projects that offer OpenTracing observability for containerized services on
{product-title} are not supported in {oke}.

##### Advanced networking

The standard networking solutions in {product-title} are supported with an
{oke} subscription. The {product-title} Kubernetes CNI plugin for automation of
multi-tenant network segmentation between {product-title} projects is
entitled for use with {oke}. {oke} offers all the granular control of the
source IP addresses that are used by application services on the cluster.
Those egress IP address controls are entitled for use with {oke}.
{product-title} offers ingress routing to on cluster services that use
non-standard ports when no public cloud provider is in use via the VIP pods
found in {product-title}. That ingress solution is supported in {oke}.
{oke} users are supported for the Kubernetes ingress control object, which
offers integrations with public cloud providers. Red Hat Service Mesh, which is
derived from the istio.io open source project, is not supported in {oke}. Also,
the Kourier Ingress Controller found in OpenShift Serverless is not supported
on {oke}.

##### 

{oke} does not include {osc}. Use {product-title} for this support.

##### Developer experience

With {oke}, the following capabilities are not supported:

* The {product-title} developer experience utilities and tools, such as {openshift-dev-spaces-productname}.
* The {product-title} pipeline feature that integrates a streamlined,
Kubernetes-enabled Jenkins and Tekton experience in the user's project space.
* The {product-title} source-to-image feature, which allows you to easily
deploy source code, dockerfiles, or container images across the cluster.
* Build strategies, builder pods, or Tekton for end user container
deployments.
* The `odo` developer command line.
* The developer persona in the {product-title} web console.

##### Feature summary

The following table is a summary of the feature availability in {oke} and {product-title}. Where applicable, it includes the name of the Operator that enables a feature.

.Features in {oke} and {product-title}
| Feature | {oke} | {product-title} | Operator name |
| --- | --- | --- | --- |
| Fully Automated Installers (IPI) | Included | Included | N/A |
| Customizable Installers (UPI) | Included | Included | N/A |
| Disconnected Installation | Included | Included | N/A |
| {op-system-base-full} or {op-system-first} entitlement | Included | Included | N/A |
| Existing RHEL manual attach to cluster (BYO) | Included | Included | N/A |
| CRIO Runtime | Included | Included | N/A |
| Over the Air Smart Upgrades and Operating System ({op-system}) Management | Included | Included | N/A |
| Enterprise Secured Kubernetes | Included | Included | N/A |
| Kubectl and `oc` automated command line | Included | Included | N/A |
| Auth Integrations, RBAC, SCC, Multi-Tenancy Admission Controller | Included | Included | N/A |
| Operator Lifecycle Manager (OLM) | Included | Included | N/A |
| Administrator web console | Included | Included | N/A |
| OpenShift Virtualization | Included | Included | OpenShift Virtualization Operator |
| Compliance Operator provided by Red Hat | Included | Included | Compliance Operator |
| File Integrity Operator | Included | Included | File Integrity Operator |
| Gatekeeper Operator | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Gatekeeper Operator |
| Klusterlet | Not Included - Requires separate subscription | Not Included - Requires separate subscription | N/A |
| {descheduler-operator} provided by Red Hat | Included | Included | {descheduler-operator} |
| Local Storage provided by Red Hat | Included | Included | Local Storage Operator |
| Node Feature Discovery provided by Red Hat | Included | Included | Node Feature Discovery Operator |
| Performance Profile controller | Included | Included | N/A |
| PTP Operator provided by Red Hat | Included | Included | PTP Operator |
| Service Telemetry Operator provided by Red Hat | Not Included | Included | Service Telemetry Operator |
| SR-IOV Network Operator | Included | Included | SR-IOV Network Operator |
| Vertical Pod Autoscaler | Included | Included | Vertical Pod Autoscaler |
| Cluster Monitoring (Prometheus) | Included | Included | Cluster Monitoring |
| Device Manager (for example, GPU) | Included | Included | N/A |
| Log Forwarding | Included | Included | Red Hat OpenShift Logging Operator |
| Telemeter and Insights Connected Experience | Included | Included | N/A s| Feature s| {oke} s| {product-title} s| Operator name |
| OpenShift Cloud Manager SaaS Service | Included | Included | N/A |
| OVS and OVN SDN | Included | Included | N/A |
| MetalLB | Included | Included | MetalLB Operator |
| HAProxy Ingress Controller | Included | Included | N/A |
| Ingress Cluster-wide Firewall | Included | Included | N/A |
| Egress Pod and Namespace Granular Control | Included | Included | N/A |
| Ingress Non-Standard Ports | Included | Included | N/A |
| Multus and Available Multus Plugins | Included | Included | N/A |
| Network Policies | Included | Included | N/A |
| IPv6 Single and Dual Stack | Included | Included | N/A |
| CNI Plugin ISV Compatibility | Included | Included | N/A |
| CSI Plugin ISV Compatibility | Included | Included | N/A |
| RHT and {ibm-name} middleware à la carte purchases (not included in {product-title} or {oke}) | Included | Included | N/A |
| ISV or Partner Operator and Container Compatibility (not included in {product-title} or {oke}) | Included | Included | N/A |
| Embedded software catalog | Included | Included | N/A |
| Embedded Marketplace | Included | Included | N/A |
| Quay Compatibility (not included) | Included | Included | N/A |
| OpenShift API for Data Protection (OADP) | Included | Included | OADP Operator |
| RHEL Software Collections and RHT SSO Common Service (included) | Included | Included | N/A |
| Embedded Registry | Included | Included | N/A |
| Helm | Included | Included | N/A |
| User Workload Monitoring | Not Included | Included | N/A |
| Cost Management SaaS Service | Included | Included | Cost Management Metrics Operator |
| Platform Logging | Not Included | Included | Red Hat OpenShift Logging Operator |
| Developer Web Console | Not Included | Included | N/A |
| Developer Application Catalog | Not Included | Included | N/A |
| Source to Image and Builder Automation (Tekton) | Not Included | Included | N/A |
| OpenShift Service Mesh | Not Included | Included | OpenShift Service Mesh Operator s| Feature s| {oke} s| {product-title} s| Operator name |
| Red Hat OpenShift Serverless | Not Included | Included | OpenShift Serverless Operator |
| Web Terminal provided by Red Hat | Not Included | Included | Web Terminal Operator |
| Red Hat OpenShift Pipelines Operator | Not Included | Included | OpenShift Pipelines Operator |
| Embedded Component of {ibm-cloud-name} Pak and RHT MW Bundles | Not Included | Included | N/A |
| Red Hat OpenShift GitOps | Not Included | Included | OpenShift GitOps |
| {openshift-dev-spaces-productname} | Not Included | Included | {openshift-dev-spaces-productname} |
| {openshift-local-productname} | Not Included | Included | N/A |
| Quay Bridge Operator provided by Red Hat | Not Included | Included | Quay Bridge Operator |
| Quay Container Security provided by Red Hat | Not Included | Included | Quay Operator |
| Red Hat OpenShift distributed tracing platform | Not Included | Included | Red Hat OpenShift distributed tracing platform Operator |
| Red Hat OpenShift Kiali | Not Included | Included | Kiali Operator |
| Metering provided by Red Hat (deprecated) | Not Included | Included | N/A |
| Migration Toolkit for Containers Operator | Not Included | Included | Migration Toolkit for Containers Operator |
| Cost management for OpenShift | Not included | Included | N/A |
| JBoss Web Server provided by Red Hat | Not included | Included | JWS Operator |
| Red Hat Build of Quarkus | Not included | Included | N/A |
| Kourier Ingress Controller | Not included | Included | N/A |
| RHT Middleware Bundles Sub Compatibility (not included in {product-title}) | Not included | Included | N/A |
| {ibm-cloud-name}  Pak Sub Compatibility (not included in {product-title}) | Not included | Included | N/A |
| OpenShift Do (`odo`) | Not included | Included | N/A |
| Source to Image and Tekton Builders | Not included | Included | N/A |
| OpenShift Serverless FaaS | Not included | Included | N/A |
| IDE Integrations | Not included | Included | N/A |
| {osc} | Not included | Not included | {osc-operator} |
| Windows Machine Config Operator | Community Windows Machine Config Operator included - no subscription required | Red Hat Windows Machine Config Operator included - Requires separate subscription | Windows Machine Config Operator |
| {quay} | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Quay Operator |
| Red Hat Advanced Cluster Management | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Advanced Cluster Management for Kubernetes |
| Red Hat Advanced Cluster Security | Not Included - Requires separate subscription | Not Included - Requires separate subscription | N/A |
| {rh-storage} | Not Included - Requires separate subscription | Not Included - Requires separate subscription | {rh-storage} s| Feature s| {oke} s| {product-title} s| Operator name |
| Ansible Automation Platform Resource Operator | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Ansible Automation Platform Resource Operator |
| Business Automation provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Business Automation Operator |
| Data Grid provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Data Grid Operator |
| Red Hat Integration provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Red Hat Integration Operator |
| Red Hat Integration - 3Scale provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | 3scale |
| Red Hat Integration - 3Scale APICast gateway provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | 3scale APIcast |
| Red Hat Integration - AMQ Broker | Not Included - Requires separate subscription | Not Included - Requires separate subscription | AMQ Broker |
| Red Hat Integration - AMQ Broker LTS | Not Included - Requires separate subscription | Not Included - Requires separate subscription | - |
| Red Hat Integration - AMQ Interconnect | Not Included - Requires separate subscription | Not Included - Requires separate subscription | AMQ Interconnect |
| Red Hat Integration - AMQ Online | Not Included - Requires separate subscription | Not Included - Requires separate subscription | - |
| Red Hat Integration - AMQ Streams | Not Included - Requires separate subscription | Not Included - Requires separate subscription | AMQ Streams |
| Red Hat Integration - Camel K | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Camel K |
| Red Hat Integration - Fuse Console | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Fuse Console |
| Red Hat Integration - Fuse Online | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Fuse Online |
| Red Hat Integration - Service Registry Operator | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Service Registry |
| API Designer provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | API Designer |
| JBoss EAP provided by Red Hat | Not Included - Requires separate subscription | Not Included - Requires separate subscription | JBoss EAP |
| Smart Gateway Operator | Not Included - Requires separate subscription | Not Included - Requires separate subscription | Smart Gateway Operator |
| Kubernetes NMState Operator | Included | Included | N/A |

#### Subscription limitations

{oke} is a subscription offering that provides {product-title} with a limited set
of supported features at a lower list price. {oke} and {product-title} are the
same product and, therefore, all software and features are delivered in both.
There is only one download, {product-title}. {oke} uses the {product-title}
documentation and support services and bug errata for this reason.

## Providing feedback on documentation

To report an error or to improve our documentation, log in to your Red Hat Jira account and submit an issue. If you do not have a Red Hat Jira account, then you will be prompted to create an account.

.Procedure

. Click one of the following links:
** To create a link:https://issues.redhat.com/secure/CreateIssueDetails!init.jspa?pid=12332330&summary=Documentation_issue&issuetype=1&components=12367614&priority=10200&versions=12436721[Jira issue] for {product-title}
** To create a link:https://issues.redhat.com/secure/CreateIssueDetails!init.jspa?pid=12323181&issuetype=1&priority=10200[Jira issue] for {VirtProductName}
. Enter a brief description of the issue in the *Summary*.
. Provide a detailed description of the issue or enhancement in the *Description*. Include a URL to where the issue occurs in the documentation.
. Click *Create* to create the issue.
