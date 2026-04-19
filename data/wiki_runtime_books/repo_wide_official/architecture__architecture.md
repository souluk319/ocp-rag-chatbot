# Product architecture

## OpenShift Container Platform

[FIGURE src="/playbooks/wiki-assets/repo_wide_official/architecture__architecture/525-OpenShift-arch-012025.png" alt="Red Hat OpenShift Kubernetes Engine" kind="diagram" diagram_type="semantic_diagram"]
Red Hat OpenShift Kubernetes Engine
[/FIGURE]

_Source: `architecture-platform-introduction.adoc` · asset `525-OpenShift-arch-012025.png`_


[FIGURE src="/playbooks/wiki-assets/repo_wide_official/architecture__architecture/ocp_arch_lifecycle.png" alt="High-level OpenShift Container Platform flow" kind="diagram" diagram_type="semantic_diagram"]
High-level OpenShift Container Platform flow
[/FIGURE]

_Source: `architecture-platform-benefits.adoc` · asset `ocp_arch_lifecycle.png`_


### User facing components

* Workloads (Deployments, Jobs, ReplicaSets, etc)
* Operator Lifecycle Manager
* Builds - The build component
provides an API and infrastructure for producing new container images using a
variety of techniques including industry standard Dockerfiles and publishing
them to either the cluster image registry, or an external registry. It also
provides integration with Jenkins based pipeline continuous integration
workflows.
* Image Registry -
The image registry provides a scalable repository for storing and retrieving
container images that are produced by and run on the cluster. Image access is
integrated with the cluster's role-based access controls and user authentication
system.
* xref:../openshift_images/images-understand.adoc[Image
streams] - The imagestream API provides an abstraction over container images
that exist in registries. It allows workloads to reference an image indirectly,
retains a history of the images that have been referenced, and allows
notification when an image is updated with a new version.
