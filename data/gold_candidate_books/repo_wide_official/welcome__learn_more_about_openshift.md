# Learn more about OpenShift Container Platform

Use the following sections to find content to help you learn about and better understand OpenShift Container Platform functions:

### Learning and support

| Learn about OpenShift Container Platform | Optional additional resources |
| --- | --- |
| [What's new in OpenShift Container Platform](https://www.openshift.com/learn/whats-new) | - |
| [OpenShift blog](https://www.openshift.com/blog?hsLang=en-us) | - |
| [OpenShift Container Platform Life Cycle Policy](https://access.redhat.com/support/policy/updates/openshift) | - |
| [OpenShift Container Platform life cycle](https://access.redhat.com/support/policy/updates/openshift#ocp4_phases) | - |
| [OpenShift Interactive Learning Portal](https://learn.openshift.com/?extIdCarryOver=true&sc_cid=701f2000001Css5AAC) | - |
| [OpenShift Knowledgebase articles](https://access.redhat.com/articles/4217411) | - |
| Getting Support | - |
| Gathering data about your cluster | - |

### Architecture

| Learn about OpenShift Container Platform | Optional additional resources |
| --- | --- |
| [Enterprise Kubernetes with OpenShift](https://www.openshift.com/blog/enterprise-kubernetes-with-openshift-part-one?extIdCarryOver=true&sc_cid=701f2000001Css5AAC) | - |
| [Tested platforms](https://access.redhat.com/articles/4128421) | - |
| Architecture | - |
| Security and compliance | - |
| Networking | - |
| OVN-Kubernetes architecture | - |
| Backup and restore | - |
| Restoring to a previous cluster state | - |

### Installation

Explore the following OpenShift Container Platform installation tasks:

| Learn about installation on OpenShift Container Platform | Optional additional resources |
| --- | --- |
| OpenShift Container Platform installation overview | - |
| Selecting a cluster installation method and preparing it for users | - |
| Installing a cluster in FIPS mode | - |
| About FIPS compliance | - |

### Other cluster installer tasks

| Learn about other installer tasks on OpenShift Container Platform | Optional additional resources |
| --- | --- |
| Troubleshooting installation issues | - |
| Validating an installation | - |
| Install {rh-storage-first} | - |
| {image-mode-os-lower} | - |

#### Install a cluster in a restricted network

| Learn about installing in a restricted network | Optional additional resources a|About disconnected installation mirroring a| If your cluster uses user-provisioned infrastructure, and the cluster does not have full access to the internet, you must mirror the OpenShift Container Platform installation images. * {aws-first} * {gcp-short} * {vmw-short} * {ibm-cloud-name} * {ibm-z-name} and {ibm-linuxone-name} * {ibm-power-name} * bare metal |
| --- | --- |

#### Install a cluster in an existing network

| Learn about installing in a restricted network | Optional additional resources |
| --- | --- |
| If you use an existing Virtual Private Cloud (VPC) in {aws-first} or {gcp-short} or an existing VNet on Microsoft Azure, you can install a cluster | - |
| Installing a cluster on {gcp-short} into a shared VPC | - |

### Cluster Administrator

| Learn about OpenShift Container Platform cluster activities | Optional additional resources |
| --- | --- |
| Understand OpenShift Container Platform management a|* Machine API * Operators * * etcd | - |
| Enable cluster capabilities | - |
| Optional cluster capabilities in OpenShift Container Platform 4.20 | - |

#### Managing and changing cluster components

##### Managing cluster components

| Learn about managing cluster components | Optional additional resources |
| --- | --- |
| Manage compute and control plane machines with machine sets | - |
| Deploy machine health checks | - |
| Apply autoscaling to an OpenShift Container Platform cluster | - |
| Including pod priority in pod scheduling decisions | - |
| Manage container registries | - |
| [{quay}](https://access.redhat.com/documentation/en-us/red_hat_quay/) | - |
| Manage users and groups | - |
| Impersonating the system:admin user | - |
| Manage authentication | - |
| Multiple identity providers | - |
| Manage Ingress, API server, and Service certificates | - |
| Network security | - |
| Manage networking a|* Cluster Network Operator * Multiple network interfaces * Network policy | - |
| Manage Operators | - |
| Creating applications from installed Operators | - |

Hiding until WMCO 10.19.0 releases, replace as the last row of the above table after WMCO GAs
| {productwinc} overview
| windows_containers/understanding-windows-container-workloads.adoc#understanding-windows-container-workloads_understanding-windows-container-workloads[Understanding Windows container workloads]

##### Changing cluster components

| Learn more about changing cluster components | Optional additional resources |
| --- | --- |
| Introduction to OpenShift updates a|* Updating a cluster using the web console * Updating using the CLI * Using the OpenShift Update Service in a disconnected environment | - |
| Use custom resource definitions (CRDs) to modify the cluster a|* Create a CRD * Manage resources from CRDs | - |
| Set resource quotas | - |
| Resource quotas across multiple projects | - |
| Prune and reclaim resources | - |
| Performing advanced builds | - |
| Scale and tune clusters | - |
| OpenShift Container Platform scalability and performance | - |

### Observe a cluster

| Learn about OpenShift Container Platform | Optional additional resources |
| --- | --- |
| [Release notes for the {DTProductName}](https://docs.redhat.com/en/documentation/red_hat_openshift_distributed_tracing_platform/latest/html/release_notes_for_the_distributed_tracing_platform/distr-tracing-rn) | - |
| [{DTProductName}](https://docs.redhat.com/en/documentation/red_hat_openshift_distributed_tracing_platform/latest) | - |
| [Red Hat build of OpenTelemetry](https://docs.redhat.com/en/documentation/red_hat_build_of_opentelemetry/latest/html/installing_red_hat_build_of_opentelemetry/install-otel) | - |
| [Receiving telemetry data from multiple clusters](https://docs.redhat.com/en/documentation/red_hat_build_of_opentelemetry/latest/html/receiving_telemetry_data/otel-receiving-telemetry-data) | - |
| About Network Observability a|* Using metrics with dashboards and alerts * Observing the network traffic from the Traffic flows view | - |
| [About OpenShift Container Platform monitoring](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/about_monitoring/about-ocp-monitoring) a|* Remote health monitoring * {PM-title-c} (Technology Preview) | - |

### Storage activities

| Learn about OpenShift Container Platform | Optional additional resources |
| --- | --- |
| Storage types a| * Persistent storage * Ephemeral storage | - |

### Application Site Reliability Engineer (App SRE)

| Learn about OpenShift Container Platform | Optional additional resources |
| --- | --- |
| Building applications overview | - |
| Projects | - |
| Operators | - |
| Cluster Operator reference | - |

### Developer

OpenShift Container Platform is a platform for developing and deploying containerized applications. Read the following OpenShift Container Platform documentation, so that you can better understand OpenShift Container Platform functions:

| Learn about application development in OpenShift Container Platform | Optional additional resources |
| --- | --- |
| [Getting started with OpenShift for developers (interactive tutorial)](https://developers.redhat.com/products/openshift/getting-started#assembly-field-sections-13455) a|* Understanding OpenShift Container Platform development * Working with projects * Create deployments | - |
| [Red Hat Developers site](https://developers.redhat.com/) | - |
| Understanding image builds | - |
| [{openshift-dev-spaces-productname} (formerly Red Hat CodeReady Workspaces)](https://developers.redhat.com/products/openshift-dev-spaces/overview) | - |
| Operators | - |
| Create container images | - |
| Managing images overview | - |
| [`odo`](https://odo.dev/docs/introduction/) | - |
| Developer-focused CLI | - |
| Viewing application composition using the Topology view | - |
| Exporting applications | - |
| [Understanding {pipelines-shortname}](https://docs.openshift.com/pipelines/1.15/about/understanding-openshift-pipelines.html) | - |
| [Create CI/CD Pipelines](https://docs.openshift.com/pipelines/latest/create/creating-applications-with-cicd-pipelines.html) | - |
| [Configuring an OpenShift cluster by deploying an application with cluster configurations](https://docs.openshift.com/gitops/latest/declarative_clusterconfig/configuring-an-openshift-cluster-by-deploying-an-application-with-cluster-configurations.html) a|* Controlling pod placement using node taints * Creating infrastructure machine sets | - |

### {hcp-capital}

| Learn about {hcp} | Optional additional resources |
| --- | --- |
| Hosted control planes overview a| Versioning for {hcp} | - |
| Preparing to deploy a| * Requirements for {hcp} * Sizing guidance for {hcp} * Overriding resource utilization measurements * Installing the {hcp} command-line interface * Distributing hosted cluster workloads * Enabling or disabling the {hcp} feature | - |
| Deploying {hcp} a| * Deploying {hcp} on {VirtProductName} * Deploying {hcp} on {aws-short} * Deploying {hcp} on bare metal * Deploying {hcp} on non-bare-metal agent machines * Deploying {hcp} on {ibm-z-title} * Deploying {hcp} on {ibm-power-title} | - |
| Deploying {hcp} in a disconnected environment a| * Deploying {hcp} on bare metal in a disconnected environment * Deploying {hcp} on {VirtProductName} in a disconnected environment | - |
| Troubleshooting {hcp} a| Gathering information to troubleshoot {hcp} | - |
