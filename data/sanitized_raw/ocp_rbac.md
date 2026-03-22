<!-- source: ocp_rbac.md -->

# Security

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/authentication_and_authorization/using-rbac
---

# Chapter 8. Using RBAC to define and apply permissions

## 8.1. RBAC overviewCopy linkLink copied to clipboard!

Role-based access control (RBAC) objects determine whether a user is allowed to perform a given action within a project.

Cluster administrators can use the cluster roles and bindings to control who has various access levels to the OpenShift Container Platform platform itself and all projects.

Developers can use local roles and bindings to control who has access to their projects. Note that authorization is a separate step from authentication, which is more about determining the identity of who is taking the action.

Authorization is managed using:

| Authorization object | Description |
| --- | --- |
| Rules | Sets of permitted verbs on a set of objects. For example, whether a user or service account cancreat |
| Roles | Collections of rules. You can associate, or bind, users and groups to multiple roles. |
| Bindings | Associations between users and/or groups with a role. |

Rules

Sets of permitted verbs on a set of objects. For example, whether a user or service account cancreatepods.

Roles

Collections of rules. You can associate, or bind, users and groups to multiple roles.

Bindings

Associations between users and/or groups with a role.

There are two levels of RBAC roles and bindings that control authorization:

| RBAC level | Description |
| --- | --- |
| Cluster RBAC | Roles and bindings that are applicable across all projects.Cluster rolesexist cluster-wide, andclust |
| Local RBAC | Roles and bindings that are scoped to a given project. Whilelocal rolesexist only in a single projec |

Cluster RBAC

Roles and bindings that are applicable across all projects.Cluster rolesexist cluster-wide, andcluster role bindingscan reference only cluster roles.

Local RBAC

Roles and bindings that are scoped to a given project. Whilelocal rolesexist only in a single project, local role bindings can referencebothcluster and local roles.

A cluster role binding is a binding that exists at the cluster level. A role binding exists at the project level. The cluster roleviewmust be bound to a user using a local role binding for that user to view the project. Create local roles only if a cluster role does not provide the set of permissions needed for a particular situation.

This two-level hierarchy allows reuse across multiple projects through the cluster roles while allowing customization inside of individual projects through local roles.

During evaluation, both the cluster role bindings and the local role bindings are used. For example:

- Cluster-wide "allow" rules are checked.
- Locally-bound "allow" rules are checked.
- Deny by default.

### 8.1.1. Default cluster rolesCopy linkLink copied to clipboard!

OpenShift Container Platform includes a set of default cluster roles that you can bind to users and groups cluster-wide or locally.

It is not recommended to manually modify the default cluster roles. Modifications to these system roles can prevent a cluster from functioning properly.

| Default cluster role | Description |
| --- | --- |
| admin | A project manager. If used in a local binding, anadminhas rights to view any resource in the project |
| basic-user | A user that can get basic information about projects and users. |
| cluster-admin | A super-user that can perform any action in any project. When bound to a user with a local binding,  |
| cluster-status | A user that can get basic cluster status information. |
| cluster-reader | A user that can get or view most of the objects but cannot modify them. |
| edit | A user that can modify most objects in a project but does not have the power to view or modify roles |
| self-provisioner | A user that can create their own projects. |
| view | A user who cannot make any modifications, but can see most objects in a project. They cannot view or |

admin

A project manager. If used in a local binding, anadminhas rights to view any resource in the project and modify any resource in the project except for quota.

basic-user

A user that can get basic information about projects and users.

cluster-admin

A super-user that can perform any action in any project. When bound to a user with a local binding, they have full control over quota and every action on every resource in the project.

cluster-status

A user that can get basic cluster status information.

cluster-reader

A user that can get or view most of the objects but cannot modify them.

edit

A user that can modify most objects in a project but does not have the power to view or modify roles or bindings.

self-provisioner

A user that can create their own projects.

view

A user who cannot make any modifications, but can see most objects in a project. They cannot view or modify roles or bindings.

Be mindful of the difference between local and cluster bindings. For example, if you bind thecluster-adminrole to a user by using a local role binding, it might appear that this user has the privileges of a cluster administrator. This is not the case. Binding thecluster-adminto a user in a project grants super administrator privileges for only that project to the user. That user has the permissions of the cluster roleadmin, plus a few additional permissions like the ability to edit rate limits, for that project. This binding can be confusing via the web console UI, which does not list cluster role bindings that are bound to true cluster administrators. However, it does list local role bindings that you can use to locally bindcluster-admin.

The relationships between cluster roles, local roles, cluster role bindings, local role bindings, users, groups and service accounts are illustrated below.

Theget pods/exec,get pods/*, andget *rules grant execution privileges when they are applied to a role. Apply the principle of least privilege and assign only the minimal RBAC rights required for users and agents. For more information, seeRBAC rules allow execution privileges.

### 8.1.2. Evaluating authorizationCopy linkLink copied to clipboard!

OpenShift Container Platform evaluates authorization by using:

**Identity**
  The user name and list of groups that the user belongs to.

**Action**
  The action you perform. In most cases, this consists of:Project: The project you access. A project is a Kubernetes namespace with additional annotations that allows a community of users to organize and manage their content in isolation from other communities.Verb: The action itself:get,list,create,update,delete,deletecollection, orwatch.Resource name: The API endpoint that you access.

The action you perform. In most cases, this consists of:

- Project: The project you access. A project is a Kubernetes namespace with additional annotations that allows a community of users to organize and manage their content in isolation from other communities.
- Verb: The action itself:get,list,create,update,delete,deletecollection, orwatch.
- Resource name: The API endpoint that you access.

**Bindings**
  The full list of bindings, the associations between users or groups with a role.

OpenShift Container Platform evaluates authorization by using the following steps:

- The identity and the project-scoped action is used to find all bindings that apply to the user or their groups.
- Bindings are used to locate all the roles that apply.
- Roles are used to find all the rules that apply.
- The action is checked against each rule to find a match.
- If no matching rule is found, the action is then denied by default.

Remember that users and groups can be associated with, or bound to, multiple roles at the same time.

Project administrators can use the CLI to view local roles and bindings, including a matrix of the verbs and resources each are associated with.

The cluster role bound to the project administrator is limited in a project through a local binding. It is not bound cluster-wide like the cluster roles granted to thecluster-adminorsystem:admin.

Cluster roles are roles defined at the cluster level but can be bound either at the cluster level or at the project level.

#### 8.1.2.1. Cluster role aggregationCopy linkLink copied to clipboard!

The default admin, edit, view, and cluster-reader cluster roles supportcluster role aggregation, where the cluster rules for each role are dynamically updated as new rules are created. This feature is relevant only if you extend the Kubernetes API by creating custom resources.

## 8.2. Projects and namespacesCopy linkLink copied to clipboard!

A Kubernetesnamespaceprovides a mechanism to scope resources in a cluster. TheKubernetes documentationhas more information on namespaces.

Namespaces provide a unique scope for:

- Named resources to avoid basic naming collisions.
- Delegated management authority to trusted users.
- The ability to limit community resource consumption.

Most objects in the system are scoped by namespace, but some are excepted and have no namespace, including nodes and users.

Aprojectis a Kubernetes namespace with additional annotations and is the central vehicle by which access to resources for regular users is managed. A project allows a community of users to organize and manage their content in isolation from other communities. Users must be given access to projects by administrators, or if allowed to create projects, automatically have access to their own projects.

Projects can have a separatename,displayName, anddescription.

- The mandatorynameis a unique identifier for the project and is most visible when using the CLI tools or API. The maximum name length is 63 characters.
- The optionaldisplayNameis how the project is displayed in the web console (defaults toname).
- The optionaldescriptioncan be a more detailed description of the project and is also visible in the web console.

Each project scopes its own set of:

| Object | Description |
| --- | --- |
| Objects | Pods, services, replication controllers, etc. |
| Policies | Rules for which users can or cannot perform actions on objects. |
| Constraints | Quotas for each kind of object that can be limited. |
| Service accounts | Service accounts act automatically with designated access to objects in the project. |

Objects

Pods, services, replication controllers, etc.

Policies

Rules for which users can or cannot perform actions on objects.

Constraints

Quotas for each kind of object that can be limited.

Service accounts

Service accounts act automatically with designated access to objects in the project.

Cluster administrators can create projects and delegate administrative rights for the project to any member of the user community. Cluster administrators can also allow developers to create their own projects.

Developers and administrators can interact with projects by using the CLI or the web console.

## 8.3. Default projectsCopy linkLink copied to clipboard!

OpenShift Container Platform comes with a number of default projects, and projects starting withopenshift-are the most essential to users. These projects host master components that run as pods and other infrastructure components. The pods created in these namespaces that have acritical pod annotationare considered critical, and the have guaranteed admission by kubelet. Pods created for master components in these namespaces are already marked as critical.

Do not run workloads in or share access to default projects. Default projects are reserved for running core cluster components.

The following default projects are considered highly privileged:default,kube-public,kube-system,openshift,openshift-infra,openshift-node, and other system-created projects that have theopenshift.io/run-levellabel set to0or1. Functionality that relies on admission plugins, such as pod security admission, security context constraints, cluster resource quotas, and image reference resolution, does not work in highly privileged projects.

## 8.4. Viewing cluster roles and bindingsCopy linkLink copied to clipboard!

You can use theocCLI to view cluster roles and bindings by using theoc describecommand.

Prerequisites

- Install theocCLI.
- Obtain permission to view the cluster roles and bindings.

Users with thecluster-admindefault cluster role bound cluster-wide can perform any action on any resource, including viewing cluster roles and bindings.

Procedure

- To view the cluster roles and their associated rule sets:oc describe clusterrole.rbac$oc describe clusterrole.rbacCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
  Resources                                                  Non-Resource URLs  Resource Names  Verbs
  ---------                                                  -----------------  --------------  -----
  .packages.apps.redhat.com                                  []                 []              [* create update patch delete get list watch]
  imagestreams                                               []                 []              [create delete deletecollection get list patch update watch create get list watch]
  imagestreams.image.openshift.io                            []                 []              [create delete deletecollection get list patch update watch create get list watch]
  secrets                                                    []                 []              [create delete deletecollection get list patch update watch get list watch create delete deletecollection patch update]
  buildconfigs/webhooks                                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs                                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs/scale                                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings                                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates                                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes                                                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io/scale                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io/webhooks                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs.build.openshift.io                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages.image.openshift.io                       []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings.image.openshift.io                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags.image.openshift.io                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes.route.openshift.io                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates.template.openshift.io                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs.template.openshift.io                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances.template.openshift.io                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates.template.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  serviceaccounts                                            []                 []              [create delete deletecollection get list patch update watch impersonate create delete deletecollection patch update get list watch]
  imagestreams/secrets                                       []                 []              [create delete deletecollection get list patch update watch]
  rolebindings                                               []                 []              [create delete deletecollection get list patch update watch]
  roles                                                      []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.authorization.openshift.io                    []                 []              [create delete deletecollection get list patch update watch]
  roles.authorization.openshift.io                           []                 []              [create delete deletecollection get list patch update watch]
  imagestreams.image.openshift.io/secrets                    []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.rbac.authorization.k8s.io                     []                 []              [create delete deletecollection get list patch update watch]
  roles.rbac.authorization.k8s.io                            []                 []              [create delete deletecollection get list patch update watch]
  networkpolicies.extensions                                 []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  networkpolicies.networking.k8s.io                          []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  configmaps                                                 []                 []              [create delete deletecollection patch update get list watch]
  endpoints                                                  []                 []              [create delete deletecollection patch update get list watch]
  persistentvolumeclaims                                     []                 []              [create delete deletecollection patch update get list watch]
  pods                                                       []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers                                     []                 []              [create delete deletecollection patch update get list watch]
  services                                                   []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.apps                                            []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps/scale                                    []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps                                          []                 []              [create delete deletecollection patch update get list watch]
  horizontalpodautoscalers.autoscaling                       []                 []              [create delete deletecollection patch update get list watch]
  cronjobs.batch                                             []                 []              [create delete deletecollection patch update get list watch]
  jobs.batch                                                 []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.extensions                                      []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  ingresses.extensions                                       []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers.extensions/scale                    []                 []              [create delete deletecollection patch update get list watch]
  poddisruptionbudgets.policy                                []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/rollback                                  []                 []              [create delete deletecollection patch update]
  deployments.extensions/rollback                            []                 []              [create delete deletecollection patch update]
  catalogsources.operators.coreos.com                        []                 []              [create update patch delete get list watch]
  clusterserviceversions.operators.coreos.com                []                 []              [create update patch delete get list watch]
  installplans.operators.coreos.com                          []                 []              [create update patch delete get list watch]
  packagemanifests.operators.coreos.com                      []                 []              [create update patch delete get list watch]
  subscriptions.operators.coreos.com                         []                 []              [create update patch delete get list watch]
  buildconfigs/instantiate                                   []                 []              [create]
  buildconfigs/instantiatebinary                             []                 []              [create]
  builds/clone                                               []                 []              [create]
  deploymentconfigrollbacks                                  []                 []              [create]
  deploymentconfigs/instantiate                              []                 []              [create]
  deploymentconfigs/rollback                                 []                 []              [create]
  imagestreamimports                                         []                 []              [create]
  localresourceaccessreviews                                 []                 []              [create]
  localsubjectaccessreviews                                  []                 []              [create]
  podsecuritypolicyreviews                                   []                 []              [create]
  podsecuritypolicyselfsubjectreviews                        []                 []              [create]
  podsecuritypolicysubjectreviews                            []                 []              [create]
  resourceaccessreviews                                      []                 []              [create]
  routes/custom-host                                         []                 []              [create]
  subjectaccessreviews                                       []                 []              [create]
  subjectrulesreviews                                        []                 []              [create]
  deploymentconfigrollbacks.apps.openshift.io                []                 []              [create]
  deploymentconfigs.apps.openshift.io/instantiate            []                 []              [create]
  deploymentconfigs.apps.openshift.io/rollback               []                 []              [create]
  localsubjectaccessreviews.authorization.k8s.io             []                 []              [create]
  localresourceaccessreviews.authorization.openshift.io      []                 []              [create]
  localsubjectaccessreviews.authorization.openshift.io       []                 []              [create]
  resourceaccessreviews.authorization.openshift.io           []                 []              [create]
  subjectaccessreviews.authorization.openshift.io            []                 []              [create]
  subjectrulesreviews.authorization.openshift.io             []                 []              [create]
  buildconfigs.build.openshift.io/instantiate                []                 []              [create]
  buildconfigs.build.openshift.io/instantiatebinary          []                 []              [create]
  builds.build.openshift.io/clone                            []                 []              [create]
  imagestreamimports.image.openshift.io                      []                 []              [create]
  routes.route.openshift.io/custom-host                      []                 []              [create]
  podsecuritypolicyreviews.security.openshift.io             []                 []              [create]
  podsecuritypolicyselfsubjectreviews.security.openshift.io  []                 []              [create]
  podsecuritypolicysubjectreviews.security.openshift.io      []                 []              [create]
  jenkins.build.openshift.io                                 []                 []              [edit view view admin edit view]
  builds                                                     []                 []              [get create delete deletecollection get list patch update watch get list watch]
  builds.build.openshift.io                                  []                 []              [get create delete deletecollection get list patch update watch get list watch]
  projects                                                   []                 []              [get delete get delete get patch update]
  projects.project.openshift.io                              []                 []              [get delete get delete get patch update]
  namespaces                                                 []                 []              [get get list watch]
  pods/attach                                                []                 []              [get list watch create delete deletecollection patch update]
  pods/exec                                                  []                 []              [get list watch create delete deletecollection patch update]
  pods/portforward                                           []                 []              [get list watch create delete deletecollection patch update]
  pods/proxy                                                 []                 []              [get list watch create delete deletecollection patch update]
  services/proxy                                             []                 []              [get list watch create delete deletecollection patch update]
  routes/status                                              []                 []              [get list watch update]
  routes.route.openshift.io/status                           []                 []              [get list watch update]
  appliedclusterresourcequotas                               []                 []              [get list watch]
  bindings                                                   []                 []              [get list watch]
  builds/log                                                 []                 []              [get list watch]
  deploymentconfigs/log                                      []                 []              [get list watch]
  deploymentconfigs/status                                   []                 []              [get list watch]
  events                                                     []                 []              [get list watch]
  imagestreams/status                                        []                 []              [get list watch]
  limitranges                                                []                 []              [get list watch]
  namespaces/status                                          []                 []              [get list watch]
  pods/log                                                   []                 []              [get list watch]
  pods/status                                                []                 []              [get list watch]
  replicationcontrollers/status                              []                 []              [get list watch]
  resourcequotas/status                                      []                 []              [get list watch]
  resourcequotas                                             []                 []              [get list watch]
  resourcequotausages                                        []                 []              [get list watch]
  rolebindingrestrictions                                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/log                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/status                 []                 []              [get list watch]
  controllerrevisions.apps                                   []                 []              [get list watch]
  rolebindingrestrictions.authorization.openshift.io         []                 []              [get list watch]
  builds.build.openshift.io/log                              []                 []              [get list watch]
  imagestreams.image.openshift.io/status                     []                 []              [get list watch]
  appliedclusterresourcequotas.quota.openshift.io            []                 []              [get list watch]
  imagestreams/layers                                        []                 []              [get update get]
  imagestreams.image.openshift.io/layers                     []                 []              [get update get]
  builds/details                                             []                 []              [update]
  builds.build.openshift.io/details                          []                 []              [update]

Name:         basic-user
Labels:       <none>
Annotations:  openshift.io/description: A user that can get basic information about projects.
	              rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
	Resources                                           Non-Resource URLs  Resource Names  Verbs
	  ---------                                           -----------------  --------------  -----
	  selfsubjectrulesreviews                             []                 []              [create]
	  selfsubjectaccessreviews.authorization.k8s.io       []                 []              [create]
	  selfsubjectrulesreviews.authorization.openshift.io  []                 []              [create]
	  clusterroles.rbac.authorization.k8s.io              []                 []              [get list watch]
	  clusterroles                                        []                 []              [get list]
	  clusterroles.authorization.openshift.io             []                 []              [get list]
	  storageclasses.storage.k8s.io                       []                 []              [get list]
	  users                                               []                 [~]             [get]
	  users.user.openshift.io                             []                 [~]             [get]
	  projects                                            []                 []              [list watch]
	  projects.project.openshift.io                       []                 []              [list watch]
	  projectrequests                                     []                 []              [list]
	  projectrequests.project.openshift.io                []                 []              [list]

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
Resources  Non-Resource URLs  Resource Names  Verbs
---------  -----------------  --------------  -----
*.*        []                 []              [*]
           [*]                []              [*]

...Name:         admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
  Resources                                                  Non-Resource URLs  Resource Names  Verbs
  ---------                                                  -----------------  --------------  -----
  .packages.apps.redhat.com                                  []                 []              [* create update patch delete get list watch]
  imagestreams                                               []                 []              [create delete deletecollection get list patch update watch create get list watch]
  imagestreams.image.openshift.io                            []                 []              [create delete deletecollection get list patch update watch create get list watch]
  secrets                                                    []                 []              [create delete deletecollection get list patch update watch get list watch create delete deletecollection patch update]
  buildconfigs/webhooks                                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs                                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs/scale                                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings                                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates                                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes                                                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io/scale                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io/webhooks                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs.build.openshift.io                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages.image.openshift.io                       []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings.image.openshift.io                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags.image.openshift.io                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes.route.openshift.io                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates.template.openshift.io                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs.template.openshift.io                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances.template.openshift.io                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates.template.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  serviceaccounts                                            []                 []              [create delete deletecollection get list patch update watch impersonate create delete deletecollection patch update get list watch]
  imagestreams/secrets                                       []                 []              [create delete deletecollection get list patch update watch]
  rolebindings                                               []                 []              [create delete deletecollection get list patch update watch]
  roles                                                      []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.authorization.openshift.io                    []                 []              [create delete deletecollection get list patch update watch]
  roles.authorization.openshift.io                           []                 []              [create delete deletecollection get list patch update watch]
  imagestreams.image.openshift.io/secrets                    []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.rbac.authorization.k8s.io                     []                 []              [create delete deletecollection get list patch update watch]
  roles.rbac.authorization.k8s.io                            []                 []              [create delete deletecollection get list patch update watch]
  networkpolicies.extensions                                 []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  networkpolicies.networking.k8s.io                          []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  configmaps                                                 []                 []              [create delete deletecollection patch update get list watch]
  endpoints                                                  []                 []              [create delete deletecollection patch update get list watch]
  persistentvolumeclaims                                     []                 []              [create delete deletecollection patch update get list watch]
  pods                                                       []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers                                     []                 []              [create delete deletecollection patch update get list watch]
  services                                                   []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.apps                                            []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps/scale                                    []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps                                          []                 []              [create delete deletecollection patch update get list watch]
  horizontalpodautoscalers.autoscaling                       []                 []              [create delete deletecollection patch update get list watch]
  cronjobs.batch                                             []                 []              [create delete deletecollection patch update get list watch]
  jobs.batch                                                 []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.extensions                                      []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  ingresses.extensions                                       []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers.extensions/scale                    []                 []              [create delete deletecollection patch update get list watch]
  poddisruptionbudgets.policy                                []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/rollback                                  []                 []              [create delete deletecollection patch update]
  deployments.extensions/rollback                            []                 []              [create delete deletecollection patch update]
  catalogsources.operators.coreos.com                        []                 []              [create update patch delete get list watch]
  clusterserviceversions.operators.coreos.com                []                 []              [create update patch delete get list watch]
  installplans.operators.coreos.com                          []                 []              [create update patch delete get list watch]
  packagemanifests.operators.coreos.com                      []                 []              [create update patch delete get list watch]
  subscriptions.operators.coreos.com                         []                 []              [create update patch delete get list watch]
  buildconfigs/instantiate                                   []                 []              [create]
  buildconfigs/instantiatebinary                             []                 []              [create]
  builds/clone                                               []                 []              [create]
  deploymentconfigrollbacks                                  []                 []              [create]
  deploymentconfigs/instantiate                              []                 []              [create]
  deploymentconfigs/rollback                                 []                 []              [create]
  imagestreamimports                                         []                 []              [create]
  localresourceaccessreviews                                 []                 []              [create]
  localsubjectaccessreviews                                  []                 []              [create]
  podsecuritypolicyreviews                                   []                 []              [create]
  podsecuritypolicyselfsubjectreviews                        []                 []              [create]
  podsecuritypolicysubjectreviews                            []                 []              [create]
  resourceaccessreviews                                      []                 []              [create]
  routes/custom-host                                         []                 []              [create]
  subjectaccessreviews                                       []                 []              [create]
  subjectrulesreviews                                        []                 []              [create]
  deploymentconfigrollbacks.apps.openshift.io                []                 []              [create]
  deploymentconfigs.apps.openshift.io/instantiate            []                 []              [create]
  deploymentconfigs.apps.openshift.io/rollback               []                 []              [create]
  localsubjectaccessreviews.authorization.k8s.io             []                 []              [create]
  localresourceaccessreviews.authorization.openshift.io      []                 []              [create]
  localsubjectaccessreviews.authorization.openshift.io       []                 []              [create]
  resourceaccessreviews.authorization.openshift.io           []                 []              [create]
  subjectaccessreviews.authorization.openshift.io            []                 []              [create]
  subjectrulesreviews.authorization.openshift.io             []                 []              [create]
  buildconfigs.build.openshift.io/instantiate                []                 []              [create]
  buildconfigs.build.openshift.io/instantiatebinary          []                 []              [create]
  builds.build.openshift.io/clone                            []                 []              [create]
  imagestreamimports.image.openshift.io                      []                 []              [create]
  routes.route.openshift.io/custom-host                      []                 []              [create]
  podsecuritypolicyreviews.security.openshift.io             []                 []              [create]
  podsecuritypolicyselfsubjectreviews.security.openshift.io  []                 []              [create]
  podsecuritypolicysubjectreviews.security.openshift.io      []                 []              [create]
  jenkins.build.openshift.io                                 []                 []              [edit view view admin edit view]
  builds                                                     []                 []              [get create delete deletecollection get list patch update watch get list watch]
  builds.build.openshift.io                                  []                 []              [get create delete deletecollection get list patch update watch get list watch]
  projects                                                   []                 []              [get delete get delete get patch update]
  projects.project.openshift.io                              []                 []              [get delete get delete get patch update]
  namespaces                                                 []                 []              [get get list watch]
  pods/attach                                                []                 []              [get list watch create delete deletecollection patch update]
  pods/exec                                                  []                 []              [get list watch create delete deletecollection patch update]
  pods/portforward                                           []                 []              [get list watch create delete deletecollection patch update]
  pods/proxy                                                 []                 []              [get list watch create delete deletecollection patch update]
  services/proxy                                             []                 []              [get list watch create delete deletecollection patch update]
  routes/status                                              []                 []              [get list watch update]
  routes.route.openshift.io/status                           []                 []              [get list watch update]
  appliedclusterresourcequotas                               []                 []              [get list watch]
  bindings                                                   []                 []              [get list watch]
  builds/log                                                 []                 []              [get list watch]
  deploymentconfigs/log                                      []                 []              [get list watch]
  deploymentconfigs/status                                   []                 []              [get list watch]
  events                                                     []                 []              [get list watch]
  imagestreams/status                                        []                 []              [get list watch]
  limitranges                                                []                 []              [get list watch]
  namespaces/status                                          []                 []              [get list watch]
  pods/log                                                   []                 []              [get list watch]
  pods/status                                                []                 []              [get list watch]
  replicationcontrollers/status                              []                 []              [get list watch]
  resourcequotas/status                                      []                 []              [get list watch]
  resourcequotas                                             []                 []              [get list watch]
  resourcequotausages                                        []                 []              [get list watch]
  rolebindingrestrictions                                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/log                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/status                 []                 []              [get list watch]
  controllerrevisions.apps                                   []                 []              [get list watch]
  rolebindingrestrictions.authorization.openshift.io         []                 []              [get list watch]
  builds.build.openshift.io/log                              []                 []              [get list watch]
  imagestreams.image.openshift.io/status                     []                 []              [get list watch]
  appliedclusterresourcequotas.quota.openshift.io            []                 []              [get list watch]
  imagestreams/layers                                        []                 []              [get update get]
  imagestreams.image.openshift.io/layers                     []                 []              [get update get]
  builds/details                                             []                 []              [update]
  builds.build.openshift.io/details                          []                 []              [update]

Name:         basic-user
Labels:       <none>
Annotations:  openshift.io/description: A user that can get basic information about projects.
	              rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
	Resources                                           Non-Resource URLs  Resource Names  Verbs
	  ---------                                           -----------------  --------------  -----
	  selfsubjectrulesreviews                             []                 []              [create]
	  selfsubjectaccessreviews.authorization.k8s.io       []                 []              [create]
	  selfsubjectrulesreviews.authorization.openshift.io  []                 []              [create]
	  clusterroles.rbac.authorization.k8s.io              []                 []              [get list watch]
	  clusterroles                                        []                 []              [get list]
	  clusterroles.authorization.openshift.io             []                 []              [get list]
	  storageclasses.storage.k8s.io                       []                 []              [get list]
	  users                                               []                 [~]             [get]
	  users.user.openshift.io                             []                 [~]             [get]
	  projects                                            []                 []              [list watch]
	  projects.project.openshift.io                       []                 []              [list watch]
	  projectrequests                                     []                 []              [list]
	  projectrequests.project.openshift.io                []                 []              [list]

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
Resources  Non-Resource URLs  Resource Names  Verbs
---------  -----------------  --------------  -----
*.*        []                 []              [*]
           [*]                []              [*]

...Copy to ClipboardCopied!Toggle word wrapToggle overflow

To view the cluster roles and their associated rule sets:

Example output

```
Name:         admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
  Resources                                                  Non-Resource URLs  Resource Names  Verbs
  ---------                                                  -----------------  --------------  -----
  .packages.apps.redhat.com                                  []                 []              [* create update patch delete get list watch]
  imagestreams                                               []                 []              [create delete deletecollection get list patch update watch create get list watch]
  imagestreams.image.openshift.io                            []                 []              [create delete deletecollection get list patch update watch create get list watch]
  secrets                                                    []                 []              [create delete deletecollection get list patch update watch get list watch create delete deletecollection patch update]
  buildconfigs/webhooks                                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs                                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs/scale                                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings                                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates                                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes                                                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io/scale                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io/webhooks                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs.build.openshift.io                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages.image.openshift.io                       []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings.image.openshift.io                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags.image.openshift.io                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes.route.openshift.io                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates.template.openshift.io                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs.template.openshift.io                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances.template.openshift.io                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates.template.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  serviceaccounts                                            []                 []              [create delete deletecollection get list patch update watch impersonate create delete deletecollection patch update get list watch]
  imagestreams/secrets                                       []                 []              [create delete deletecollection get list patch update watch]
  rolebindings                                               []                 []              [create delete deletecollection get list patch update watch]
  roles                                                      []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.authorization.openshift.io                    []                 []              [create delete deletecollection get list patch update watch]
  roles.authorization.openshift.io                           []                 []              [create delete deletecollection get list patch update watch]
  imagestreams.image.openshift.io/secrets                    []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.rbac.authorization.k8s.io                     []                 []              [create delete deletecollection get list patch update watch]
  roles.rbac.authorization.k8s.io                            []                 []              [create delete deletecollection get list patch update watch]
  networkpolicies.extensions                                 []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  networkpolicies.networking.k8s.io                          []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  configmaps                                                 []                 []              [create delete deletecollection patch update get list watch]
  endpoints                                                  []                 []              [create delete deletecollection patch update get list watch]
  persistentvolumeclaims                                     []                 []              [create delete deletecollection patch update get list watch]
  pods                                                       []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers                                     []                 []              [create delete deletecollection patch update get list watch]
  services                                                   []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.apps                                            []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps/scale                                    []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps                                          []                 []              [create delete deletecollection patch update get list watch]
  horizontalpodautoscalers.autoscaling                       []                 []              [create delete deletecollection patch update get list watch]
  cronjobs.batch                                             []                 []              [create delete deletecollection patch update get list watch]
  jobs.batch                                                 []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.extensions                                      []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  ingresses.extensions                                       []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers.extensions/scale                    []                 []              [create delete deletecollection patch update get list watch]
  poddisruptionbudgets.policy                                []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/rollback                                  []                 []              [create delete deletecollection patch update]
  deployments.extensions/rollback                            []                 []              [create delete deletecollection patch update]
  catalogsources.operators.coreos.com                        []                 []              [create update patch delete get list watch]
  clusterserviceversions.operators.coreos.com                []                 []              [create update patch delete get list watch]
  installplans.operators.coreos.com                          []                 []              [create update patch delete get list watch]
  packagemanifests.operators.coreos.com                      []                 []              [create update patch delete get list watch]
  subscriptions.operators.coreos.com                         []                 []              [create update patch delete get list watch]
  buildconfigs/instantiate                                   []                 []              [create]
  buildconfigs/instantiatebinary                             []                 []              [create]
  builds/clone                                               []                 []              [create]
  deploymentconfigrollbacks                                  []                 []              [create]
  deploymentconfigs/instantiate                              []                 []              [create]
  deploymentconfigs/rollback                                 []                 []              [create]
  imagestreamimports                                         []                 []              [create]
  localresourceaccessreviews                                 []                 []              [create]
  localsubjectaccessreviews                                  []                 []              [create]
  podsecuritypolicyreviews                                   []                 []              [create]
  podsecuritypolicyselfsubjectreviews                        []                 []              [create]
  podsecuritypolicysubjectreviews                            []                 []              [create]
  resourceaccessreviews                                      []                 []              [create]
  routes/custom-host                                         []                 []              [create]
  subjectaccessreviews                                       []                 []              [create]
  subjectrulesreviews                                        []                 []              [create]
  deploymentconfigrollbacks.apps.openshift.io                []                 []              [create]
  deploymentconfigs.apps.openshift.io/instantiate            []                 []              [create]
  deploymentconfigs.apps.openshift.io/rollback               []                 []              [create]
  localsubjectaccessreviews.authorization.k8s.io             []                 []              [create]
  localresourceaccessreviews.authorization.openshift.io      []                 []              [create]
  localsubjectaccessreviews.authorization.openshift.io       []                 []              [create]
  resourceaccessreviews.authorization.openshift.io           []                 []              [create]
  subjectaccessreviews.authorization.openshift.io            []                 []              [create]
  subjectrulesreviews.authorization.openshift.io             []                 []              [create]
  buildconfigs.build.openshift.io/instantiate                []                 []              [create]
  buildconfigs.build.openshift.io/instantiatebinary          []                 []              [create]
  builds.build.openshift.io/clone                            []                 []              [create]
  imagestreamimports.image.openshift.io                      []                 []              [create]
  routes.route.openshift.io/custom-host                      []                 []              [create]
  podsecuritypolicyreviews.security.openshift.io             []                 []              [create]
  podsecuritypolicyselfsubjectreviews.security.openshift.io  []                 []              [create]
  podsecuritypolicysubjectreviews.security.openshift.io      []                 []              [create]
  jenkins.build.openshift.io                                 []                 []              [edit view view admin edit view]
  builds                                                     []                 []              [get create delete deletecollection get list patch update watch get list watch]
  builds.build.openshift.io                                  []                 []              [get create delete deletecollection get list patch update watch get list watch]
  projects                                                   []                 []              [get delete get delete get patch update]
  projects.project.openshift.io                              []                 []              [get delete get delete get patch update]
  namespaces                                                 []                 []              [get get list watch]
  pods/attach                                                []                 []              [get list watch create delete deletecollection patch update]
  pods/exec                                                  []                 []              [get list watch create delete deletecollection patch update]
  pods/portforward                                           []                 []              [get list watch create delete deletecollection patch update]
  pods/proxy                                                 []                 []              [get list watch create delete deletecollection patch update]
  services/proxy                                             []                 []              [get list watch create delete deletecollection patch update]
  routes/status                                              []                 []              [get list watch update]
  routes.route.openshift.io/status                           []                 []              [get list watch update]
  appliedclusterresourcequotas                               []                 []              [get list watch]
  bindings                                                   []                 []              [get list watch]
  builds/log                                                 []                 []              [get list watch]
  deploymentconfigs/log                                      []                 []              [get list watch]
  deploymentconfigs/status                                   []                 []              [get list watch]
  events                                                     []                 []              [get list watch]
  imagestreams/status                                        []                 []              [get list watch]
  limitranges                                                []                 []              [get list watch]
  namespaces/status                                          []                 []              [get list watch]
  pods/log                                                   []                 []              [get list watch]
  pods/status                                                []                 []              [get list watch]
  replicationcontrollers/status                              []                 []              [get list watch]
  resourcequotas/status                                      []                 []              [get list watch]
  resourcequotas                                             []                 []              [get list watch]
  resourcequotausages                                        []                 []              [get list watch]
  rolebindingrestrictions                                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/log                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/status                 []                 []              [get list watch]
  controllerrevisions.apps                                   []                 []              [get list watch]
  rolebindingrestrictions.authorization.openshift.io         []                 []              [get list watch]
  builds.build.openshift.io/log                              []                 []              [get list watch]
  imagestreams.image.openshift.io/status                     []                 []              [get list watch]
  appliedclusterresourcequotas.quota.openshift.io            []                 []              [get list watch]
  imagestreams/layers                                        []                 []              [get update get]
  imagestreams.image.openshift.io/layers                     []                 []              [get update get]
  builds/details                                             []                 []              [update]
  builds.build.openshift.io/details                          []                 []              [update]

Name:         basic-user
Labels:       <none>
Annotations:  openshift.io/description: A user that can get basic information about projects.
	              rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
	Resources                                           Non-Resource URLs  Resource Names  Verbs
	  ---------                                           -----------------  --------------  -----
	  selfsubjectrulesreviews                             []                 []              [create]
	  selfsubjectaccessreviews.authorization.k8s.io       []                 []              [create]
	  selfsubjectrulesreviews.authorization.openshift.io  []                 []              [create]
	  clusterroles.rbac.authorization.k8s.io              []                 []              [get list watch]
	  clusterroles                                        []                 []              [get list]
	  clusterroles.authorization.openshift.io             []                 []              [get list]
	  storageclasses.storage.k8s.io                       []                 []              [get list]
	  users                                               []                 [~]             [get]
	  users.user.openshift.io                             []                 [~]             [get]
	  projects                                            []                 []              [list watch]
	  projects.project.openshift.io                       []                 []              [list watch]
	  projectrequests                                     []                 []              [list]
	  projectrequests.project.openshift.io                []                 []              [list]

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
Resources  Non-Resource URLs  Resource Names  Verbs
---------  -----------------  --------------  -----
*.*        []                 []              [*]
           [*]                []              [*]

...
```

```
Name:         admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
  Resources                                                  Non-Resource URLs  Resource Names  Verbs
  ---------                                                  -----------------  --------------  -----
  .packages.apps.redhat.com                                  []                 []              [* create update patch delete get list watch]
  imagestreams                                               []                 []              [create delete deletecollection get list patch update watch create get list watch]
  imagestreams.image.openshift.io                            []                 []              [create delete deletecollection get list patch update watch create get list watch]
  secrets                                                    []                 []              [create delete deletecollection get list patch update watch get list watch create delete deletecollection patch update]
  buildconfigs/webhooks                                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs                                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs/scale                                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings                                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates                                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes                                                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs                                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances                                          []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates                                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io/scale                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  deploymentconfigs.apps.openshift.io                        []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io/webhooks                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildconfigs.build.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  buildlogs.build.openshift.io                               []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamimages.image.openshift.io                       []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreammappings.image.openshift.io                     []                 []              [create delete deletecollection get list patch update watch get list watch]
  imagestreamtags.image.openshift.io                         []                 []              [create delete deletecollection get list patch update watch get list watch]
  routes.route.openshift.io                                  []                 []              [create delete deletecollection get list patch update watch get list watch]
  processedtemplates.template.openshift.io                   []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateconfigs.template.openshift.io                      []                 []              [create delete deletecollection get list patch update watch get list watch]
  templateinstances.template.openshift.io                    []                 []              [create delete deletecollection get list patch update watch get list watch]
  templates.template.openshift.io                            []                 []              [create delete deletecollection get list patch update watch get list watch]
  serviceaccounts                                            []                 []              [create delete deletecollection get list patch update watch impersonate create delete deletecollection patch update get list watch]
  imagestreams/secrets                                       []                 []              [create delete deletecollection get list patch update watch]
  rolebindings                                               []                 []              [create delete deletecollection get list patch update watch]
  roles                                                      []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.authorization.openshift.io                    []                 []              [create delete deletecollection get list patch update watch]
  roles.authorization.openshift.io                           []                 []              [create delete deletecollection get list patch update watch]
  imagestreams.image.openshift.io/secrets                    []                 []              [create delete deletecollection get list patch update watch]
  rolebindings.rbac.authorization.k8s.io                     []                 []              [create delete deletecollection get list patch update watch]
  roles.rbac.authorization.k8s.io                            []                 []              [create delete deletecollection get list patch update watch]
  networkpolicies.extensions                                 []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  networkpolicies.networking.k8s.io                          []                 []              [create delete deletecollection patch update create delete deletecollection get list patch update watch get list watch]
  configmaps                                                 []                 []              [create delete deletecollection patch update get list watch]
  endpoints                                                  []                 []              [create delete deletecollection patch update get list watch]
  persistentvolumeclaims                                     []                 []              [create delete deletecollection patch update get list watch]
  pods                                                       []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers                                     []                 []              [create delete deletecollection patch update get list watch]
  services                                                   []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.apps                                            []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps/scale                                     []                 []              [create delete deletecollection patch update get list watch]
  replicasets.apps                                           []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps/scale                                    []                 []              [create delete deletecollection patch update get list watch]
  statefulsets.apps                                          []                 []              [create delete deletecollection patch update get list watch]
  horizontalpodautoscalers.autoscaling                       []                 []              [create delete deletecollection patch update get list watch]
  cronjobs.batch                                             []                 []              [create delete deletecollection patch update get list watch]
  jobs.batch                                                 []                 []              [create delete deletecollection patch update get list watch]
  daemonsets.extensions                                      []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  deployments.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  ingresses.extensions                                       []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions/scale                               []                 []              [create delete deletecollection patch update get list watch]
  replicasets.extensions                                     []                 []              [create delete deletecollection patch update get list watch]
  replicationcontrollers.extensions/scale                    []                 []              [create delete deletecollection patch update get list watch]
  poddisruptionbudgets.policy                                []                 []              [create delete deletecollection patch update get list watch]
  deployments.apps/rollback                                  []                 []              [create delete deletecollection patch update]
  deployments.extensions/rollback                            []                 []              [create delete deletecollection patch update]
  catalogsources.operators.coreos.com                        []                 []              [create update patch delete get list watch]
  clusterserviceversions.operators.coreos.com                []                 []              [create update patch delete get list watch]
  installplans.operators.coreos.com                          []                 []              [create update patch delete get list watch]
  packagemanifests.operators.coreos.com                      []                 []              [create update patch delete get list watch]
  subscriptions.operators.coreos.com                         []                 []              [create update patch delete get list watch]
  buildconfigs/instantiate                                   []                 []              [create]
  buildconfigs/instantiatebinary                             []                 []              [create]
  builds/clone                                               []                 []              [create]
  deploymentconfigrollbacks                                  []                 []              [create]
  deploymentconfigs/instantiate                              []                 []              [create]
  deploymentconfigs/rollback                                 []                 []              [create]
  imagestreamimports                                         []                 []              [create]
  localresourceaccessreviews                                 []                 []              [create]
  localsubjectaccessreviews                                  []                 []              [create]
  podsecuritypolicyreviews                                   []                 []              [create]
  podsecuritypolicyselfsubjectreviews                        []                 []              [create]
  podsecuritypolicysubjectreviews                            []                 []              [create]
  resourceaccessreviews                                      []                 []              [create]
  routes/custom-host                                         []                 []              [create]
  subjectaccessreviews                                       []                 []              [create]
  subjectrulesreviews                                        []                 []              [create]
  deploymentconfigrollbacks.apps.openshift.io                []                 []              [create]
  deploymentconfigs.apps.openshift.io/instantiate            []                 []              [create]
  deploymentconfigs.apps.openshift.io/rollback               []                 []              [create]
  localsubjectaccessreviews.authorization.k8s.io             []                 []              [create]
  localresourceaccessreviews.authorization.openshift.io      []                 []              [create]
  localsubjectaccessreviews.authorization.openshift.io       []                 []              [create]
  resourceaccessreviews.authorization.openshift.io           []                 []              [create]
  subjectaccessreviews.authorization.openshift.io            []                 []              [create]
  subjectrulesreviews.authorization.openshift.io             []                 []              [create]
  buildconfigs.build.openshift.io/instantiate                []                 []              [create]
  buildconfigs.build.openshift.io/instantiatebinary          []                 []              [create]
  builds.build.openshift.io/clone                            []                 []              [create]
  imagestreamimports.image.openshift.io                      []                 []              [create]
  routes.route.openshift.io/custom-host                      []                 []              [create]
  podsecuritypolicyreviews.security.openshift.io             []                 []              [create]
  podsecuritypolicyselfsubjectreviews.security.openshift.io  []                 []              [create]
  podsecuritypolicysubjectreviews.security.openshift.io      []                 []              [create]
  jenkins.build.openshift.io                                 []                 []              [edit view view admin edit view]
  builds                                                     []                 []              [get create delete deletecollection get list patch update watch get list watch]
  builds.build.openshift.io                                  []                 []              [get create delete deletecollection get list patch update watch get list watch]
  projects                                                   []                 []              [get delete get delete get patch update]
  projects.project.openshift.io                              []                 []              [get delete get delete get patch update]
  namespaces                                                 []                 []              [get get list watch]
  pods/attach                                                []                 []              [get list watch create delete deletecollection patch update]
  pods/exec                                                  []                 []              [get list watch create delete deletecollection patch update]
  pods/portforward                                           []                 []              [get list watch create delete deletecollection patch update]
  pods/proxy                                                 []                 []              [get list watch create delete deletecollection patch update]
  services/proxy                                             []                 []              [get list watch create delete deletecollection patch update]
  routes/status                                              []                 []              [get list watch update]
  routes.route.openshift.io/status                           []                 []              [get list watch update]
  appliedclusterresourcequotas                               []                 []              [get list watch]
  bindings                                                   []                 []              [get list watch]
  builds/log                                                 []                 []              [get list watch]
  deploymentconfigs/log                                      []                 []              [get list watch]
  deploymentconfigs/status                                   []                 []              [get list watch]
  events                                                     []                 []              [get list watch]
  imagestreams/status                                        []                 []              [get list watch]
  limitranges                                                []                 []              [get list watch]
  namespaces/status                                          []                 []              [get list watch]
  pods/log                                                   []                 []              [get list watch]
  pods/status                                                []                 []              [get list watch]
  replicationcontrollers/status                              []                 []              [get list watch]
  resourcequotas/status                                      []                 []              [get list watch]
  resourcequotas                                             []                 []              [get list watch]
  resourcequotausages                                        []                 []              [get list watch]
  rolebindingrestrictions                                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/log                    []                 []              [get list watch]
  deploymentconfigs.apps.openshift.io/status                 []                 []              [get list watch]
  controllerrevisions.apps                                   []                 []              [get list watch]
  rolebindingrestrictions.authorization.openshift.io         []                 []              [get list watch]
  builds.build.openshift.io/log                              []                 []              [get list watch]
  imagestreams.image.openshift.io/status                     []                 []              [get list watch]
  appliedclusterresourcequotas.quota.openshift.io            []                 []              [get list watch]
  imagestreams/layers                                        []                 []              [get update get]
  imagestreams.image.openshift.io/layers                     []                 []              [get update get]
  builds/details                                             []                 []              [update]
  builds.build.openshift.io/details                          []                 []              [update]

Name:         basic-user
Labels:       <none>
Annotations:  openshift.io/description: A user that can get basic information about projects.
	              rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
	Resources                                           Non-Resource URLs  Resource Names  Verbs
	  ---------                                           -----------------  --------------  -----
	  selfsubjectrulesreviews                             []                 []              [create]
	  selfsubjectaccessreviews.authorization.k8s.io       []                 []              [create]
	  selfsubjectrulesreviews.authorization.openshift.io  []                 []              [create]
	  clusterroles.rbac.authorization.k8s.io              []                 []              [get list watch]
	  clusterroles                                        []                 []              [get list]
	  clusterroles.authorization.openshift.io             []                 []              [get list]
	  storageclasses.storage.k8s.io                       []                 []              [get list]
	  users                                               []                 [~]             [get]
	  users.user.openshift.io                             []                 [~]             [get]
	  projects                                            []                 []              [list watch]
	  projects.project.openshift.io                       []                 []              [list watch]
	  projectrequests                                     []                 []              [list]
	  projectrequests.project.openshift.io                []                 []              [list]

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
PolicyRule:
Resources  Non-Resource URLs  Resource Names  Verbs
---------  -----------------  --------------  -----
*.*        []                 []              [*]
           [*]                []              [*]

...
```

- To view the current set of cluster role bindings, which shows the users and groups that are bound to various roles:oc describe clusterrolebinding.rbac$oc describe clusterrolebinding.rbacCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         alertmanager-main
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  alertmanager-main
Subjects:
  Kind            Name               Namespace
  ----            ----               ---------
  ServiceAccount  alertmanager-main  openshift-monitoring

Name:         basic-users
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  basic-user
Subjects:
  Kind   Name                  Namespace
  ----   ----                  ---------
  Group  system:authenticated

Name:         cloud-credential-operator-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cloud-credential-operator-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-cloud-credential-operator

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name            Namespace
  ----   ----            ---------
  Group  system:masters

Name:         cluster-admins
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name                   Namespace
  ----   ----                   ---------
  Group  system:cluster-admins
  User   system:admin

Name:         cluster-api-manager-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cluster-api-manager-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-machine-api

...Name:         alertmanager-main
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  alertmanager-main
Subjects:
  Kind            Name               Namespace
  ----            ----               ---------
  ServiceAccount  alertmanager-main  openshift-monitoring

Name:         basic-users
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  basic-user
Subjects:
  Kind   Name                  Namespace
  ----   ----                  ---------
  Group  system:authenticated

Name:         cloud-credential-operator-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cloud-credential-operator-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-cloud-credential-operator

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name            Namespace
  ----   ----            ---------
  Group  system:masters

Name:         cluster-admins
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name                   Namespace
  ----   ----                   ---------
  Group  system:cluster-admins
  User   system:admin

Name:         cluster-api-manager-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cluster-api-manager-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-machine-api

...Copy to ClipboardCopied!Toggle word wrapToggle overflow

To view the current set of cluster role bindings, which shows the users and groups that are bound to various roles:

Example output

```
Name:         alertmanager-main
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  alertmanager-main
Subjects:
  Kind            Name               Namespace
  ----            ----               ---------
  ServiceAccount  alertmanager-main  openshift-monitoring

Name:         basic-users
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  basic-user
Subjects:
  Kind   Name                  Namespace
  ----   ----                  ---------
  Group  system:authenticated

Name:         cloud-credential-operator-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cloud-credential-operator-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-cloud-credential-operator

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name            Namespace
  ----   ----            ---------
  Group  system:masters

Name:         cluster-admins
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name                   Namespace
  ----   ----                   ---------
  Group  system:cluster-admins
  User   system:admin

Name:         cluster-api-manager-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cluster-api-manager-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-machine-api

...
```

```
Name:         alertmanager-main
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  alertmanager-main
Subjects:
  Kind            Name               Namespace
  ----            ----               ---------
  ServiceAccount  alertmanager-main  openshift-monitoring

Name:         basic-users
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  basic-user
Subjects:
  Kind   Name                  Namespace
  ----   ----                  ---------
  Group  system:authenticated

Name:         cloud-credential-operator-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cloud-credential-operator-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-cloud-credential-operator

Name:         cluster-admin
Labels:       kubernetes.io/bootstrapping=rbac-defaults
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name            Namespace
  ----   ----            ---------
  Group  system:masters

Name:         cluster-admins
Labels:       <none>
Annotations:  rbac.authorization.kubernetes.io/autoupdate: true
Role:
  Kind:  ClusterRole
  Name:  cluster-admin
Subjects:
  Kind   Name                   Namespace
  ----   ----                   ---------
  Group  system:cluster-admins
  User   system:admin

Name:         cluster-api-manager-rolebinding
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  cluster-api-manager-role
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  default  openshift-machine-api

...
```

## 8.5. Viewing local roles and bindingsCopy linkLink copied to clipboard!

You can use theocCLI to view local roles and bindings by using theoc describecommand.

Prerequisites

- Install theocCLI.
- Obtain permission to view the local roles and bindings:Users with thecluster-admindefault cluster role bound cluster-wide can perform any action on any resource, including viewing local roles and bindings.Users with theadmindefault cluster role bound locally can view and manage roles and bindings in that project.

Obtain permission to view the local roles and bindings:

- Users with thecluster-admindefault cluster role bound cluster-wide can perform any action on any resource, including viewing local roles and bindings.
- Users with theadmindefault cluster role bound locally can view and manage roles and bindings in that project.

Procedure

- To view the current set of local role bindings, which show the users and groups that are bound to various roles for the current project:oc describe rolebinding.rbac$oc describe rolebinding.rbacCopy to ClipboardCopied!Toggle word wrapToggle overflow

To view the current set of local role bindings, which show the users and groups that are bound to various roles for the current project:

- To view the local role bindings for a different project, add the-nflag to the command:oc describe rolebinding.rbac -n joe-project$oc describe rolebinding.rbac-njoe-projectCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe-project

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe-project

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe-projectName:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe-project

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe-project

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe-projectCopy to ClipboardCopied!Toggle word wrapToggle overflow

To view the local role bindings for a different project, add the-nflag to the command:

Example output

```
Name:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe-project

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe-project

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe-project
```

```
Name:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe-project

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe-project

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe-project
```

## 8.6. Adding roles to usersCopy linkLink copied to clipboard!

You can use theoc admadministrator CLI to manage the roles and bindings.

Binding, or adding, a role to users or groups gives the user or group the access that is granted by the role. You can add and remove roles to and from users and groups usingoc adm policycommands.

You can bind any of the default cluster roles to local users or groups in your project.

Procedure

- Add a role to a user in a specific project:oc adm policy add-role-to-user <role> <user> -n <project>$oc adm policy add-role-to-user<role><user>-n<project>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, you can add theadminrole to thealiceuser injoeproject by running:oc adm policy add-role-to-user admin alice -n joe$oc adm policy add-role-to-user admin alice-njoeCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can alternatively apply the following YAML to add the role to the user:[REDACTED_ACCOUNT] rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-0
  namespace: joe
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: aliceapiVersion:rbac.authorization.k8s.io/v1kind:RoleBindingmetadata:name:admin-0namespace:joeroleRef:apiGroup:rbac.authorization.k8s.iokind:ClusterRolename:adminsubjects:-apiGroup:rbac.authorization.k8s.iokind:Username:[REDACTED_ACCOUNT] to ClipboardCopied!Toggle word wrapToggle overflow

Add a role to a user in a specific project:

For example, you can add theadminrole to thealiceuser injoeproject by running:

You can alternatively apply the following YAML to add the role to the user:

[REDACTED_ACCOUNT]
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-0
  namespace: joe
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: alice
```

```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-0
  namespace: joe
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: admin
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: alice
```

- View the local role bindings and verify the addition in the output:oc describe rolebinding.rbac -n <project>$oc describe rolebinding.rbac-n<project>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, to view the local role bindings for thejoeproject:oc describe rolebinding.rbac -n joe$oc describe rolebinding.rbac-njoeCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         admin-0
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name   Namespace
  ----  ----   ---------
  User  alice 

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joeName:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         admin-0
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name   Namespace
  ----  ----   ---------
  User  alice1Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joeCopy to ClipboardCopied!Toggle word wrapToggle overflow1Thealiceuser has been added to theadminsRoleBinding.

View the local role bindings and verify the addition in the output:

For example, to view the local role bindings for thejoeproject:

Example output

```
Name:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         admin-0
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name   Namespace
  ----  ----   ---------
  User  alice 

Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe
```

```
Name:         admin
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name        Namespace
  ----  ----        ---------
  User  kube:admin

Name:         admin-0
Labels:       <none>
Annotations:  <none>
Role:
  Kind:  ClusterRole
  Name:  admin
Subjects:
  Kind  Name   Namespace
  ----  ----   ---------
  User  alice
```

```
Name:         system:deployers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows deploymentconfigs in this namespace to rollout pods in
                this namespace.  It is auto-managed by a controller; remove
                subjects to disa...
Role:
  Kind:  ClusterRole
  Name:  system:deployer
Subjects:
  Kind            Name      Namespace
  ----            ----      ---------
  ServiceAccount  deployer  joe

Name:         system:image-builders
Labels:       <none>
Annotations:  openshift.io/description:
                Allows builds in this namespace to push images to this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-builder
Subjects:
  Kind            Name     Namespace
  ----            ----     ---------
  ServiceAccount  builder  joe

Name:         system:image-pullers
Labels:       <none>
Annotations:  openshift.io/description:
                Allows all pods in this namespace to pull images from this
                namespace.  It is auto-managed by a controller; remove subjects
                to disable.
Role:
  Kind:  ClusterRole
  Name:  system:image-puller
Subjects:
  Kind   Name                                Namespace
  ----   ----                                ---------
  Group  system:serviceaccounts:joe
```

**1**
  Thealiceuser has been added to theadminsRoleBinding.

## 8.7. Creating a local roleCopy linkLink copied to clipboard!

You can create a local role for a project and then bind it to a user.

Procedure

- To create a local role for a project, run the following command:oc create role <name> --verb=<verb> --resource=<resource> -n <project>$oc create role<name>--verb=<verb>--resource=<resource>-n<project>Copy to ClipboardCopied!Toggle word wrapToggle overflowIn this command, specify:<name>, the local role’s name<verb>, a comma-separated list of the verbs to apply to the role<resource>, the resources that the role applies to<project>, the project nameFor example, to create a local role that allows a user to view pods in theblueproject, run the following command:oc create role podview --verb=get --resource=pod -n blue$oc create role podview--verb=get--resource=pod-nblueCopy to ClipboardCopied!Toggle word wrapToggle overflow

To create a local role for a project, run the following command:

In this command, specify:

- <name>, the local role’s name
- <verb>, a comma-separated list of the verbs to apply to the role
- <resource>, the resources that the role applies to
- <project>, the project name

For example, to create a local role that allows a user to view pods in theblueproject, run the following command:

- To bind the new role to a user, run the following command:oc adm policy add-role-to-user podview user2 --role-namespace=blue -n blue$oc adm policy add-role-to-user podview user2 --role-namespace=blue-nblueCopy to ClipboardCopied!Toggle word wrapToggle overflow

To bind the new role to a user, run the following command:

## 8.8. Creating a cluster roleCopy linkLink copied to clipboard!

You can create a cluster role.

Procedure

- To create a cluster role, run the following command:oc create clusterrole <name> --verb=<verb> --resource=<resource>$oc create clusterrole<name>--verb=<verb>--resource=<resource>Copy to ClipboardCopied!Toggle word wrapToggle overflowIn this command, specify:<name>, the local role’s name<verb>, a comma-separated list of the verbs to apply to the role<resource>, the resources that the role applies toFor example, to create a cluster role that allows a user to view pods, run the following command:oc create clusterrole podviewonly --verb=get --resource=pod$oc create clusterrole podviewonly--verb=get--resource=podCopy to ClipboardCopied!Toggle word wrapToggle overflow

To create a cluster role, run the following command:

In this command, specify:

- <name>, the local role’s name
- <verb>, a comma-separated list of the verbs to apply to the role
- <resource>, the resources that the role applies to

For example, to create a cluster role that allows a user to view pods, run the following command:

## 8.9. Local role binding commandsCopy linkLink copied to clipboard!

When you manage a user or group’s associated roles for local role bindings using the following operations, a project may be specified with the-nflag. If it is not specified, then the current project is used.

You can use the following commands for local RBAC management.

| Command | Description |
| --- | --- |
| $ oc adm policy who-can<verb><resource> | Indicates which users can perform an action on a resource. |
| $ oc adm policy add-role-to-user<role><username> | Binds a specified role to specified users in the current project. |
| $ oc adm policy remove-role-from-user<role><username> | Removes a given role from specified users in the current project. |
| $ oc adm policy remove-user<username> | Removes specified users and all of their roles in the current project. |
| $ oc adm policy add-role-to-group<role><groupname> | Binds a given role to specified groups in the current project. |
| $ oc adm policy remove-role-from-group<role><groupname> | Removes a given role from specified groups in the current project. |
| $ oc adm policy remove-group<groupname> | Removes specified groups and all of their roles in the current project. |

$ oc adm policy who-can<verb><resource>

Indicates which users can perform an action on a resource.

$ oc adm policy add-role-to-user<role><username>

Binds a specified role to specified users in the current project.

$ oc adm policy remove-role-from-user<role><username>

Removes a given role from specified users in the current project.

$ oc adm policy remove-user<username>

Removes specified users and all of their roles in the current project.

$ oc adm policy add-role-to-group<role><groupname>

Binds a given role to specified groups in the current project.

$ oc adm policy remove-role-from-group<role><groupname>

Removes a given role from specified groups in the current project.

$ oc adm policy remove-group<groupname>

Removes specified groups and all of their roles in the current project.

## 8.10. Cluster role binding commandsCopy linkLink copied to clipboard!

You can also manage cluster role bindings using the following operations. The-nflag is not used for these operations because cluster role bindings use non-namespaced resources.

| Command | Description |
| --- | --- |
| $ oc adm policy add-cluster-role-to-user<role><username> | Binds a given role to specified users for all projects in the cluster. |
| $ oc adm policy remove-cluster-role-from-user<role><username> | Removes a given role from specified users for all projects in the cluster. |
| $ oc adm policy add-cluster-role-to-group<role><groupname> | Binds a given role to specified groups for all projects in the cluster. |
| $ oc adm policy remove-cluster-role-from-group<role><groupname> | Removes a given role from specified groups for all projects in the cluster. |

$ oc adm policy add-cluster-role-to-user<role><username>

Binds a given role to specified users for all projects in the cluster.

$ oc adm policy remove-cluster-role-from-user<role><username>

Removes a given role from specified users for all projects in the cluster.

$ oc adm policy add-cluster-role-to-group<role><groupname>

Binds a given role to specified groups for all projects in the cluster.

$ oc adm policy remove-cluster-role-from-group<role><groupname>

Removes a given role from specified groups for all projects in the cluster.

## 8.11. Creating a cluster adminCopy linkLink copied to clipboard!

Thecluster-adminrole is required to perform administrator level tasks on the OpenShift Container Platform cluster, such as modifying cluster resources.

Prerequisites

- You must have created a user to define as the cluster admin.

Procedure

- Define the user as a cluster admin:oc adm policy add-cluster-role-to-user cluster-admin <user>$oc adm policy add-cluster-role-to-user cluster-admin<user>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Define the user as a cluster admin:

## 8.12. Cluster role bindings for unauthenticated groupsCopy linkLink copied to clipboard!

Before OpenShift Container Platform 4.17, unauthenticated groups were allowed access to some cluster roles. Clusters updated from versions before OpenShift Container Platform 4.17 retain this access for unauthenticated groups.

For security reasons OpenShift Container Platform 4.17 does not allow unauthenticated groups to have default access to cluster roles.

There are use cases where it might be necessary to addsystem:unauthenticatedto a cluster role.

Cluster administrators can add unauthenticated users to the following cluster roles:

- system:scope-impersonation
- system:webhook
- system:oauth-token-deleter
- self-access-reviewer

Always verify compliance with your organization’s security standards when modifying unauthenticated access.
