<!-- source: k8s_rbac.md -->

# Security - RBAC

---
Source: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
---

# Using RBAC Authorization

Role-based access control (RBAC) is a method of regulating access to computer or
network resources based on the roles of individual users within your organization.

RBAC authorization uses therbac.authorization.k8s.ioAPI groupto drive authorization
decisions, allowing you to dynamically configure policies through the Kubernetes API.

To enable RBAC, start theAPI serverwith the--authorization-configflag set to a file that includes theRBACauthorizer; for example:

```
apiVersion: apiserver.config.k8s.io/v1
kind: AuthorizationConfiguration
authorizers:
  ...
  - type: RBAC
  ...
```

Or, start theAPI serverwith
the--authorization-modeflag set to a comma-separated list that includesRBAC;
for example:

```
kube-apiserver --authorization-mode=...,RBAC --other-options --more-options
```

## API objects

The RBAC API declares four kinds of Kubernetes object:Role,ClusterRole,RoleBindingandClusterRoleBinding. You can describe or amend the RBACobjectsusing tools such askubectl, just like any other Kubernetes object.

#### Caution:

### Role and ClusterRole

An RBACRoleorClusterRolecontains rules that represent a set of permissions.
Permissions are purely additive (there are no "deny" rules).

A Role always sets permissions within a particularnamespace;
when you create a Role, you have to specify the namespace it belongs in.

ClusterRole, by contrast, is a non-namespaced resource. The resources have different names (Role
and ClusterRole) because a Kubernetes object always has to be either namespaced or not namespaced;
it can't be both.

ClusterRoles have several uses. You can use a ClusterRole to:

- define permissions on namespaced resources and be granted access within individual namespace(s)
- define permissions on namespaced resources and be granted access across all namespaces
- define permissions on cluster-scoped resources

If you want to define a role within a namespace, use a Role; if you want to define
a role cluster-wide, use a ClusterRole.

#### Role example

Here's an example Role in the "default" namespace that can be used to grant read access topods:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### ClusterRole example

A ClusterRole can be used to grant the same permissions as a Role.
Because ClusterRoles are cluster-scoped, you can also use them to grant access to:

- cluster-scoped resources (likenodes)

cluster-scoped resources (likenodes)

- non-resource endpoints (like/healthz)

non-resource endpoints (like/healthz)

- namespaced resources (like Pods), across all namespacesFor example: you can use a ClusterRole to allow a particular user to runkubectl get pods --all-namespaces

namespaced resources (like Pods), across all namespaces

For example: you can use a ClusterRole to allow a particular user to runkubectl get pods --all-namespaces

Here is an example of a ClusterRole that can be used to grant read access tosecretsin any particular namespace,
or across all namespaces (depending on how it isbound):

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  # "namespace" omitted since ClusterRoles are not namespaced
  name: secret-reader
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing Secret
  # objects is "secrets"
  resources: ["secrets"]
  verbs: ["get", "watch", "list"]
```

The name of a Role or a ClusterRole object must be a validpath segment name.

### RoleBinding and ClusterRoleBinding

A role binding grants the permissions defined in a role to a user or set of users.
It holds a list ofsubjects(users, groups, or service accounts), and a reference to the
role being granted.
A RoleBinding grants permissions within a specific namespace whereas a ClusterRoleBinding
grants that access cluster-wide.

A RoleBinding may reference any Role in the same namespace. Alternatively, a RoleBinding
can reference a ClusterRole and bind that ClusterRole to the namespace of the RoleBinding.
If you want to bind a ClusterRole to all the namespaces in your cluster, you use a
ClusterRoleBinding.

The name of a RoleBinding or ClusterRoleBinding object must be a validpath segment name.

#### RoleBinding examples

Here is an example of a RoleBinding that grants the "pod-reader" Role to the user "jane"
within the "default" namespace.
This allows "jane" to read pods in the "default" namespace.

```
apiVersion: rbac.authorization.k8s.io/v1
# This role binding allows "jane" to read pods in the "default" namespace.
# You need to already have a Role named "pod-reader" in that namespace.
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
# You can specify more than one "subject"
- kind: User
  name: jane # "name" is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  # "roleRef" specifies the binding to a Role / ClusterRole
  kind: Role #this must be Role or ClusterRole
  name: pod-reader # this must match the name of the Role or ClusterRole you wish to bind to
  apiGroup: rbac.authorization.k8s.io
```

A RoleBinding can also reference a ClusterRole to grant the permissions defined in that
ClusterRole to resources inside the RoleBinding's namespace. This kind of reference
lets you define a set of common roles across your cluster, then reuse them within
multiple namespaces.

For instance, even though the following RoleBinding refers to a ClusterRole,
"dave" (the subject, case sensitive) will only be able to read Secrets in the "development"
namespace, because the RoleBinding's namespace (in its metadata) is "development".

```
apiVersion: rbac.authorization.k8s.io/v1
# This role binding allows "dave" to read secrets in the "development" namespace.
# You need to already have a ClusterRole named "secret-reader".
kind: RoleBinding
metadata:
  name: read-secrets
  #
  # The namespace of the RoleBinding determines where the permissions are granted.
  # This only grants permissions within the "development" namespace.
  namespace: development
subjects:
- kind: User
  name: dave # Name is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

#### ClusterRoleBinding example

To grant permissions across a whole cluster, you can use a ClusterRoleBinding.
The following ClusterRoleBinding allows any user in the group "manager" to read
secrets in any namespace.

```
apiVersion: rbac.authorization.k8s.io/v1
# This cluster role binding allows anyone in the "manager" group to read secrets in any namespace.
kind: ClusterRoleBinding
metadata:
  name: read-secrets-global
subjects:
- kind: Group
  name: manager # Name is case sensitive
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: secret-reader
  apiGroup: rbac.authorization.k8s.io
```

After you create a binding, you cannot change the Role or ClusterRole that it refers to.
If you try to change a binding'sroleRef, you get a validation error. If you do want
to change theroleReffor a binding, you need to remove the binding object and create
a replacement.

There are two reasons for this restriction:

- MakingroleRefimmutable allows granting someoneupdatepermission on an existing binding
object, so that they can manage the list of subjects, without being able to change
the role that is granted to those subjects.
- A binding to a different role is a fundamentally different binding.
Requiring a binding to be deleted/recreated in order to change theroleRefensures the full list of subjects in the binding is intended to be granted
the new role (as opposed to enabling or accidentally modifying only the roleRef
without verifying all of the existing subjects should be given the new role's
permissions).

Thekubectl auth reconcilecommand-line utility creates or updates a manifest file containing RBAC objects,
and handles deleting and recreating binding objects if required to change the role they refer to.
Seecommand usage and examplesfor more information.

### Referring to resources

In the Kubernetes API, most resources are represented and accessed using a string representation of
their object name, such aspodsfor a Pod. RBAC refers to resources using exactly the same
name that appears in the URL for the relevant API endpoint.
Some Kubernetes APIs involve asubresource, such as the logs for a Pod. A request for a Pod's logs looks like:

```
GET /api/v1/namespaces/{namespace}/pods/{name}/log
```

In this case,podsis the namespaced resource for Pod resources, andlogis a
subresource ofpods. To represent this in an RBAC role, use a slash (/) to
delimit the resource and subresource. To allow a subject to readpodsand
also access thelogsubresource for each of those Pods, you write:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-and-pod-logs-reader
rules:
- apiGroups: [""]
  resources: ["pods", "pods/log"]
  verbs: ["get", "list"]
```

You can also refer to resources by name for certain requests through theresourceNameslist.
When specified, requests can be restricted to individual instances of a resource.
Here is an example that restricts its subject to onlygetorupdateaConfigMapnamedmy-configmap:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: configmap-updater
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing ConfigMap
  # objects is "configmaps"
  resources: ["configmaps"]
  resourceNames: ["my-configmap"]
  verbs: ["update", "get"]
```

#### Note:

Rather than referring to individualresources,apiGroups, andverbs,
you can use the wildcard*symbol to refer to all such objects.
FornonResourceURLs, you can use the wildcard*as a suffix glob match.
ForresourceNames, an empty set means that everything is allowed.
Here is an example that allows access to perform any current and future action on
all current and future resources in theexample.comAPI group.
This is similar to the built-incluster-adminrole.

```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: example.com-superuser # DO NOT USE THIS ROLE, IT IS JUST AN EXAMPLE
rules:
- apiGroups: ["example.com"]
  resources: ["*"]
  verbs: ["*"]
```

#### Caution:

### Aggregated ClusterRoles

You canaggregateseveral ClusterRoles into one combined ClusterRole.
A controller, running as part of the cluster control plane, watches for ClusterRole
objects with anaggregationRuleset. TheaggregationRuledefines a labelselectorthat the controller
uses to match other ClusterRole objects that should be combined into therulesfield of this one.

#### Caution:

Here is an example aggregated ClusterRole:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring
aggregationRule:
  clusterRoleSelectors:
  - matchLabels:
      rbac.example.com/aggregate-to-monitoring: "true"
rules: [] # The control plane automatically fills in the rules
```

If you create a new ClusterRole that matches the label selector of an existing aggregated ClusterRole,
that change triggers adding the new rules into the aggregated ClusterRole.
Here is an example that adds rules to the "monitoring" ClusterRole, by creating another
ClusterRole labeledrbac.example.com/aggregate-to-monitoring: true.

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: monitoring-endpointslices
  labels:
    rbac.example.com/aggregate-to-monitoring: "true"
# When you create the "monitoring-endpointslices" ClusterRole,
# the rules below will be added to the "monitoring" ClusterRole.
rules:
- apiGroups: [""]
  resources: ["services", "pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["discovery.k8s.io"]
  resources: ["endpointslices"]
  verbs: ["get", "list", "watch"]
```

Thedefault user-facing rolesuse ClusterRole aggregation. This lets you,
as a cluster administrator, include rules for custom resources, such as those served byCustomResourceDefinitionsor aggregated API servers, to extend the default roles.

For example: the following ClusterRoles let the "admin" and "edit" default roles manage the custom resource
named CronTab, whereas the "view" role can perform only read actions on CronTab resources.
You can assume that CronTab objects are named"crontabs"in URLs as seen by the API server.

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: aggregate-cron-tabs-edit
  labels:
    # Add these permissions to the "admin" and "edit" default roles.
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
rules:
- apiGroups: ["stable.example.com"]
  resources: ["crontabs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
---
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: aggregate-cron-tabs-view
  labels:
    # Add these permissions to the "view" default role.
    rbac.authorization.k8s.io/aggregate-to-view: "true"
rules:
- apiGroups: ["stable.example.com"]
  resources: ["crontabs"]
  verbs: ["get", "list", "watch"]
```

#### Role examples

The following examples are excerpts from Role or ClusterRole objects, showing only
therulessection.

Allow reading"pods"resources in the coreAPI Group:

```
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing Pod
  # objects is "pods"
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

Allow reading/writing Deployments (at the HTTP level: objects with"deployments"in the resource part of their URL) in the"apps"API groups:

```
rules:
- apiGroups: ["apps"]
  #
  # at the HTTP level, the name of the resource for accessing Deployment
  # objects is "deployments"
  resources: ["deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

Allow reading Pods in the core API group, as well as reading or writing Job
resources in the"batch"API group:

```
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing Pod
  # objects is "pods"
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
- apiGroups: ["batch"]
  #
  # at the HTTP level, the name of the resource for accessing Job
  # objects is "jobs"
  resources: ["jobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

Allow reading a ConfigMap named "my-config" (must be bound with a
RoleBinding to limit to a single ConfigMap in a single namespace):

```
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing ConfigMap
  # objects is "configmaps"
  resources: ["configmaps"]
  resourceNames: ["my-config"]
  verbs: ["get"]
```

Allow reading the resource"nodes"in the core group (because a
Node is cluster-scoped, this must be in a ClusterRole bound with a
ClusterRoleBinding to be effective):

```
rules:
- apiGroups: [""]
  #
  # at the HTTP level, the name of the resource for accessing Node
  # objects is "nodes"
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
```

Allow GET and POST requests to the non-resource endpoint/healthzand
all subpaths (must be in a ClusterRole bound with a ClusterRoleBinding
to be effective):

```
rules:
- nonResourceURLs: ["/healthz", "/healthz/*"] # '*' in a nonResourceURL is a suffix glob match
  verbs: ["get", "post"]
```

### Referring to subjects

A RoleBinding or ClusterRoleBinding binds a role to subjects.
Subjects can be groups, users orServiceAccounts.

Kubernetes represents usernames as strings.
These can be: plain names, such as "alice"; email-style names, like "[REDACTED_EMAIL]";
or numeric user IDs represented as a string. It is up to you as a cluster administrator
to configure theauthentication modulesso that authentication produces usernames in the format you want.

#### Caution:

In Kubernetes, Authenticator modules provide group information.
Groups, like users, are represented as strings, and that string has no format requirements,
other than that the prefixsystem:is reserved.

ServiceAccountshave names prefixed
withsystem:serviceaccount:, and belong to groups that have names prefixed withsystem:serviceaccounts:.

#### Note:

- system:serviceaccount:(singular) is the prefix for service account usernames.
- system:serviceaccounts:(plural) is the prefix for service account groups.

#### RoleBinding examples

The following examples areRoleBindingexcerpts that only
show thesubjectssection.

For a user [REDACTED_EMAIL]:

```
subjects:
- kind: User
  name: "[REDACTED_EMAIL]"
  apiGroup: rbac.authorization.k8s.io
```

For a group namedfrontend-admins:

```
subjects:
- kind: Group
  name: "frontend-admins"
  apiGroup: rbac.authorization.k8s.io
```

For the default service account in the "kube-system" namespace:

```
subjects:
- kind: ServiceAccount
  name: default
  namespace: kube-system
```

For all service accounts in the "qa" namespace:

```
subjects:
- kind: Group
  name: system:serviceaccounts:qa
  apiGroup: rbac.authorization.k8s.io
```

For all service accounts in any namespace:

```
subjects:
- kind: Group
  name: system:serviceaccounts
  apiGroup: rbac.authorization.k8s.io
```

For all authenticated users:

```
subjects:
- kind: Group
  name: system:authenticated
  apiGroup: rbac.authorization.k8s.io
```

For all unauthenticated users:

```
subjects:
- kind: Group
  name: system:unauthenticated
  apiGroup: rbac.authorization.k8s.io
```

For all users:

```
subjects:
- kind: Group
  name: system:authenticated
  apiGroup: rbac.authorization.k8s.io
- kind: Group
  name: system:unauthenticated
  apiGroup: rbac.authorization.k8s.io
```

## Default roles and role bindings

API servers create a set of default ClusterRole and ClusterRoleBinding objects.
Many of these aresystem:prefixed, which indicates that the resource is directly
managed by the cluster control plane.
All of the default ClusterRoles and ClusterRoleBindings are labeled withkubernetes.io/bootstrapping=rbac-defaults.

#### Caution:

### Auto-reconciliation

At each start-up, the API server updates default cluster roles with any missing permissions,
and updates default cluster role bindings with any missing subjects.
This allows the cluster to repair accidental modifications, and helps to keep roles and role bindings
up-to-date as permissions and subjects change in new Kubernetes releases.

To opt out of this reconciliation, set therbac.authorization.kubernetes.io/autoupdateannotation on a default cluster role or default cluster RoleBinding tofalse.
Be aware that missing default permissions and subjects can result in non-functional clusters.

Auto-reconciliation is enabled by default if the RBAC authorizer is active.

### API discovery roles

Default cluster role bindings authorize unauthenticated and authenticated users to read API information
that is deemed safe to be publicly accessible (including CustomResourceDefinitions).
To disable anonymous unauthenticated access, add--anonymous-auth=falseflag to
the API server configuration.

To view the configuration of these roles viakubectlrun:

```
kubectl get clusterroles system:discovery -o yaml
```

#### Note:

| Default ClusterRole | Default ClusterRoleBinding | Description |
| --- | --- | --- |
| system:basic-user | system:authenticatedgroup | Allows a user read-only access to basic information about themselves. Prior to v1.14, this role was  |
| system:discovery | system:authenticatedgroup | Allows read-only access to API discovery endpoints needed to discover and negotiate an API level. Pr |
| system:public-info-viewer | system:authenticatedandsystem:unauthenticatedgroups | Allows read-only access to non-sensitive information about the cluster. Introduced in Kubernetes v1. |

### User-facing roles

Some of the default ClusterRoles are notsystem:prefixed. These are intended to be user-facing roles.
They include super-user roles (cluster-admin), roles intended to be granted cluster-wide
using ClusterRoleBindings, and roles intended to be granted within particular
namespaces using RoleBindings (admin,edit,view).

User-facing ClusterRoles useClusterRole aggregationto allow admins to include
rules for custom resources on these ClusterRoles. To add rules to theadmin,edit, orviewroles, create
a ClusterRole with one or more of the following labels:

```
metadata:
  labels:
    rbac.authorization.k8s.io/aggregate-to-admin: "true"
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
    rbac.authorization.k8s.io/aggregate-to-view: "true"
```

| Default ClusterRole | Default ClusterRoleBinding | Description |
| --- | --- | --- |
| cluster-admin | system:mastersgroup | Allows super-user access to perform any action on any resource.
When used in aClusterRoleBinding, it |
| admin | None | Allows admin access, intended to be granted within a namespace using aRoleBinding.If used in aRoleBi |
| edit | None | Allows read/write access to most objects in a namespace.This role does not allow viewing or modifyin |
| view | None | Allows read-only access to see most objects in a namespace.
It does not allow viewing roles or role  |

If used in aRoleBinding, allows read/write access to most resources in a namespace,
including the ability to create roles and role bindings within the namespace.
This role does not allow write access to resource quota or to the namespace itself.
This role also does not allow write access to EndpointSlices in clusters created
using Kubernetes v1.22+. More information is available in the"Write Access for EndpointSlices" section.

This role does not allow viewing or modifying roles or role bindings.
However, this role allows accessing Secrets and running Pods as any ServiceAccount in
the namespace, so it can be used to gain the API access levels of any ServiceAccount in
the namespace. This role also does not allow write access to EndpointSlices in
clusters created using Kubernetes v1.22+. More information is available in the"Write Access for EndpointSlices" section.

This role does not allow viewing Secrets, since reading
the contents of Secrets enables access to ServiceAccount credentials
in the namespace, which would allow API access as any ServiceAccount
in the namespace (a form of privilege escalation).

### Core component roles

| Default ClusterRole | Default ClusterRoleBinding | Description |
| --- | --- | --- |
| system:kube-scheduler | system:kube-scheduleruser | Allows access to the resources required by theschedulercomponent. |
| system:volume-scheduler | system:kube-scheduleruser | Allows access to the volume resources required by the kube-scheduler component. |
| system:kube-controller-manager | system:kube-controller-manageruser | Allows access to the resources required by thecontroller managercomponent.
The permissions required  |
| system:node | None | Allows access to resources required by the kubelet,including read access to all secrets, and write a |
| system:node-proxier | system:kube-proxyuser | Allows access to the resources required by thekube-proxycomponent. |

You should use theNode authorizerandNodeRestriction admission plugininstead of thesystem:noderole, and allow granting API access to kubelets based on the Pods scheduled to run on them.

Thesystem:noderole only exists for compatibility with Kubernetes clusters upgraded from versions prior to v1.8.

### Other component roles

| Default ClusterRole | Default ClusterRoleBinding | Description |
| --- | --- | --- |
| system:auth-delegator | None | Allows delegated authentication and authorization checks.
This is commonly used by add-on API server |
| system:heapster | None | Role for theHeapstercomponent (deprecated). |
| system:kube-aggregator | None | Role for thekube-aggregatorcomponent. |
| system:kube-dns | kube-dnsservice account in thekube-systemnamespace | Role for thekube-dnscomponent. |
| system:kubelet-api-admin | None | Allows full access to the kubelet API. |
| system:node-bootstrapper | None | Allows access to the resources required to performkubelet TLS bootstrapping. |
| system:node-problem-detector | None | Role for thenode-problem-detectorcomponent. |
| system:persistent-volume-provisioner | None | Allows access to the resources required by mostdynamic volume provisioners. |
| system:monitoring | system:monitoringgroup | Allows read access to control-plane monitoring endpoints (i.e.kube-apiserverliveness and readiness e |

### Roles for built-in controllers

The Kubernetescontroller managerrunscontrollersthat are built in to the Kubernetes
control plane.
When invoked with--use-service-account-credentials, kube-controller-manager starts each controller
using a separate service account.
Corresponding roles exist for each built-in controller, prefixed withsystem:controller:.
If the controller manager is not started with--use-service-account-credentials, it runs all control loops
using its own credential, which must be granted all the relevant roles.
These roles include:

- system:controller:attachdetach-controller
- system:controller:certificate-controller
- system:controller:clusterrole-aggregation-controller
- system:controller:cronjob-controller
- system:controller:daemon-set-controller
- system:controller:deployment-controller
- system:controller:disruption-controller
- system:controller:endpoint-controller
- system:controller:expand-controller
- system:controller:generic-garbage-collector
- system:controller:horizontal-pod-autoscaler
- system:controller:job-controller
- system:controller:namespace-controller
- system:controller:node-controller
- system:controller:persistent-volume-binder
- system:controller:pod-garbage-collector
- system:controller:pv-protection-controller
- system:controller:pvc-protection-controller
- system:controller:replicaset-controller
- system:controller:replication-controller
- system:controller:resourcequota-controller
- system:controller:root-ca-cert-publisher
- system:controller:route-controller
- system:controller:service-account-controller
- system:controller:service-controller
- system:controller:statefulset-controller
- system:controller:ttl-controller

## Privilege escalation prevention and bootstrapping

The RBAC API prevents users from escalating privileges by editing roles or role bindings.
Because this is enforced at the API level, it applies even when the RBAC authorizer is not in use.

### Restrictions on role creation or update

You can only create/update a role if at least one of the following things is true:

- You already have all the permissions contained in the role, at the same scope as the object being modified
(cluster-wide for a ClusterRole, within the same namespace or cluster-wide for a Role).
- You are granted explicit permission to perform theescalateverb on therolesorclusterrolesresource in therbac.authorization.k8s.ioAPI group.

For example, ifuser-1does not have the ability to list Secrets cluster-wide, they cannot create a ClusterRole
containing that permission. To allow a user to create/update roles:

- Grant them a role that allows them to create/update Role or ClusterRole objects, as desired.
- Grant them permission to include specific permissions in the roles they create/update:implicitly, by giving them those permissions (if they attempt to create or modify a Role or
ClusterRole with permissions they themselves have not been granted, the API request will be forbidden)or explicitly allow specifying any permission in aRoleorClusterRoleby giving them
permission to perform theescalateverb onrolesorclusterrolesresources in therbac.authorization.k8s.ioAPI group
- implicitly, by giving them those permissions (if they attempt to create or modify a Role or
ClusterRole with permissions they themselves have not been granted, the API request will be forbidden)
- or explicitly allow specifying any permission in aRoleorClusterRoleby giving them
permission to perform theescalateverb onrolesorclusterrolesresources in therbac.authorization.k8s.ioAPI group

### Restrictions on role binding creation or update

You can only create/update a role binding if you already have all the permissions contained in the referenced role
(at the same scope as the role binding)orif you have been authorized to perform thebindverb on the referenced role.
For example, ifuser-1does not have the ability to list Secrets cluster-wide, they cannot create a ClusterRoleBinding
to a role that grants that permission. To allow a user to create/update role bindings:

- Grant them a role that allows them to create/update RoleBinding or ClusterRoleBinding objects, as desired.
- Grant them permissions needed to bind a particular role:implicitly, by giving them the permissions contained in the role.explicitly, by giving them permission to perform thebindverb on the particular Role (or ClusterRole).
- implicitly, by giving them the permissions contained in the role.
- explicitly, by giving them permission to perform thebindverb on the particular Role (or ClusterRole).

For example, this ClusterRole and RoleBinding would allowuser-1to grant other users theadmin,edit, andviewroles in the namespaceuser-1-namespace:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: role-grantor
rules:
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["rolebindings"]
  verbs: ["create"]
- apiGroups: ["rbac.authorization.k8s.io"]
  resources: ["clusterroles"]
  verbs: ["bind"]
  # omit resourceNames to allow binding any ClusterRole
  resourceNames: ["admin","edit","view"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: role-grantor-binding
  namespace: user-1-namespace
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: role-grantor
subjects:
- apiGroup: rbac.authorization.k8s.io
  kind: User
  name: user-1
```

When bootstrapping the first roles and role bindings, it is necessary for the initial user to grant permissions they do not yet have.
To bootstrap initial roles and role bindings:

- Use a credential with the "system:masters" group, which is bound to the "cluster-admin" super-user role by the default bindings.

## Command-line utilities

### kubectl create role

Creates a Role object defining permissions within a single namespace. Examples:

- Create a Role named "pod-reader" that allows users to performget,watchandliston pods:kubectl create role pod-reader --verb=get --verb=list --verb=watch --resource=pods

Create a Role named "pod-reader" that allows users to performget,watchandliston pods:

```
kubectl create role pod-reader --verb=get --verb=list --verb=watch --resource=pods
```

- Create a Role named "pod-reader" with resourceNames specified:kubectl create role pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod

Create a Role named "pod-reader" with resourceNames specified:

```
kubectl create role pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod
```

- Create a Role named "foo" with apiGroups specified:kubectl create role foo --verb=get,list,watch --resource=replicasets.apps

Create a Role named "foo" with apiGroups specified:

```
kubectl create role foo --verb=get,list,watch --resource=replicasets.apps
```

- Create a Role named "foo" with subresource permissions:kubectl create role foo --verb=get,list,watch --resource=pods,pods/status

Create a Role named "foo" with subresource permissions:

```
kubectl create role foo --verb=get,list,watch --resource=pods,pods/status
```

- Create a Role named "my-component-lease-holder" with permissions to get/update a resource with a specific name:kubectl create role my-component-lease-holder --verb=get,list,watch,update --resource=lease --resource-name=my-component

Create a Role named "my-component-lease-holder" with permissions to get/update a resource with a specific name:

```
kubectl create role my-component-lease-holder --verb=get,list,watch,update --resource=lease --resource-name=my-component
```

### kubectl create clusterrole

Creates a ClusterRole. Examples:

- Create a ClusterRole named "pod-reader" that allows user to performget,watchandliston pods:kubectl create clusterrole pod-reader --verb=get,list,watch --resource=pods

Create a ClusterRole named "pod-reader" that allows user to performget,watchandliston pods:

```
kubectl create clusterrole pod-reader --verb=get,list,watch --resource=pods
```

- Create a ClusterRole named "pod-reader" with resourceNames specified:kubectl create clusterrole pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod

Create a ClusterRole named "pod-reader" with resourceNames specified:

```
kubectl create clusterrole pod-reader --verb=get --resource=pods --resource-name=readablepod --resource-name=anotherpod
```

- Create a ClusterRole named "foo" with apiGroups specified:kubectl create clusterrole foo --verb=get,list,watch --resource=replicasets.apps

Create a ClusterRole named "foo" with apiGroups specified:

```
kubectl create clusterrole foo --verb=get,list,watch --resource=replicasets.apps
```

- Create a ClusterRole named "foo" with subresource permissions:kubectl create clusterrole foo --verb=get,list,watch --resource=pods,pods/status

Create a ClusterRole named "foo" with subresource permissions:

```
kubectl create clusterrole foo --verb=get,list,watch --resource=pods,pods/status
```

- Create a ClusterRole named "foo" with nonResourceURL specified:kubectl create clusterrole"foo"--verb=get --non-resource-url=/logs/*

Create a ClusterRole named "foo" with nonResourceURL specified:

```
kubectl create clusterrole "foo" --verb=get --non-resource-url=/logs/*
```

- Create a ClusterRole named "monitoring" with an aggregationRule specified:kubectl create clusterrole monitoring --aggregation-rule="rbac.example.com/aggregate-to-monitoring=true"

Create a ClusterRole named "monitoring" with an aggregationRule specified:

```
kubectl create clusterrole monitoring --aggregation-rule="rbac.example.com/aggregate-to-monitoring=true"
```

### kubectl create rolebinding

Grants a Role or ClusterRole within a specific namespace. Examples:

- Within the namespace "acme", grant the permissions in the "admin" ClusterRole to a user named "bob":kubectl create rolebinding bob-admin-binding --clusterrole=admin --user=[REDACTED_ACCOUNT] --namespace=acme

Within the namespace "acme", grant the permissions in the "admin" ClusterRole to a user named "bob":

```
kubectl create rolebinding bob-admin-binding --clusterrole=admin --user=[REDACTED_ACCOUNT] --namespace=acme
```

- Within the namespace "acme", grant the permissions in the "view" ClusterRole to the service account in the namespace "acme" named "myapp":kubectl create rolebinding myapp-view-binding --clusterrole=view --serviceaccount=acme:myapp --namespace=acme

Within the namespace "acme", grant the permissions in the "view" ClusterRole to the service account in the namespace "acme" named "myapp":

```
kubectl create rolebinding myapp-view-binding --clusterrole=view --serviceaccount=acme:myapp --namespace=acme
```

- Within the namespace "acme", grant the permissions in the "view" ClusterRole to a service account in the namespace "myappnamespace" named "myapp":kubectl create rolebinding myappnamespace-myapp-view-binding --clusterrole=view --serviceaccount=myappnamespace:myapp --namespace=acme

Within the namespace "acme", grant the permissions in the "view" ClusterRole to a service account in the namespace "myappnamespace" named "myapp":

```
kubectl create rolebinding myappnamespace-myapp-view-binding --clusterrole=view --serviceaccount=myappnamespace:myapp --namespace=acme
```

### kubectl create clusterrolebinding

Grants a ClusterRole across the entire cluster (all namespaces). Examples:

- Across the entire cluster, grant the permissions in the "cluster-admin" ClusterRole to a user named "root":kubectl create clusterrolebinding root-cluster-admin-binding --clusterrole=cluster-admin --user=[REDACTED_ACCOUNT]

Across the entire cluster, grant the permissions in the "cluster-admin" ClusterRole to a user named "root":

```
kubectl create clusterrolebinding root-cluster-admin-binding --clusterrole=cluster-admin --user=[REDACTED_ACCOUNT]
```

- Across the entire cluster, grant the permissions in the "system:node-proxier" ClusterRole to a user named "system:kube-proxy":kubectl create clusterrolebinding kube-proxy-binding --clusterrole=system:node-proxier --user=[REDACTED_ACCOUNT]

Across the entire cluster, grant the permissions in the "system:node-proxier" ClusterRole to a user named "system:kube-proxy":

```
kubectl create clusterrolebinding kube-proxy-binding --clusterrole=system:node-proxier --user=[REDACTED_ACCOUNT]
```

- Across the entire cluster, grant the permissions in the "view" ClusterRole to a service account named "myapp" in the namespace "acme":kubectl create clusterrolebinding myapp-view-binding --clusterrole=view --serviceaccount=acme:myapp

Across the entire cluster, grant the permissions in the "view" ClusterRole to a service account named "myapp" in the namespace "acme":

```
kubectl create clusterrolebinding myapp-view-binding --clusterrole=view --serviceaccount=acme:myapp
```

### kubectl auth reconcile

Creates or updatesrbac.authorization.k8s.io/v1API objects from a manifest file.

Missing objects are created, and the containing namespace is created for namespaced objects, if required.

Existing roles are updated to include the permissions in the input objects,
and remove extra permissions if--remove-extra-permissionsis specified.

Existing bindings are updated to include the subjects in the input objects,
and remove extra subjects if--remove-extra-subjectsis specified.

Examples:

- Test applying a manifest file of RBAC objects, displaying changes that would be made:kubectl auth reconcile -f my-rbac-rules.yaml --dry-run=client

Test applying a manifest file of RBAC objects, displaying changes that would be made:

```
kubectl auth reconcile -f my-rbac-rules.yaml --dry-run=client
```

- Apply a manifest file of RBAC objects, preserving any extra permissions (in roles) and any extra subjects (in bindings):kubectl auth reconcile -f my-rbac-rules.yaml

Apply a manifest file of RBAC objects, preserving any extra permissions (in roles) and any extra subjects (in bindings):

```
kubectl auth reconcile -f my-rbac-rules.yaml
```

- Apply a manifest file of RBAC objects, removing any extra permissions (in roles) and any extra subjects (in bindings):kubectl auth reconcile -f my-rbac-rules.yaml --remove-extra-subjects --remove-extra-permissions

Apply a manifest file of RBAC objects, removing any extra permissions (in roles) and any extra subjects (in bindings):

```
kubectl auth reconcile -f my-rbac-rules.yaml --remove-extra-subjects --remove-extra-permissions
```

## ServiceAccount permissions

Default RBAC policies grant scoped permissions to control-plane components, nodes,
and controllers, but grantno permissionsto service accounts outside thekube-systemnamespace
(beyond the permissions given byAPI discovery roles).

This allows you to grant particular roles to particular ServiceAccounts as needed.
Fine-grained role bindings provide greater security, but require more effort to administrate.
Broader grants can give unnecessary (and potentially escalating) API access to
ServiceAccounts, but are easier to administrate.

In order from most secure to least secure, the approaches are:

- Grant a role to an application-specific service account (best practice)This requires the application to specify aserviceAccountNamein its pod spec,
and for the service account to be created (via the API, application manifest,kubectl create serviceaccount, etc.).For example, grant read-only permission within "my-namespace" to the "my-sa" service account:[REDACTED_ACCOUNT] create rolebinding my-sa-view\--clusterrole=view\--serviceaccount=my-namespace:my-sa\--namespace=my-namespace

Grant a role to an application-specific service account (best practice)

This requires the application to specify aserviceAccountNamein its pod spec,
and for the service account to be created (via the API, application manifest,kubectl create serviceaccount, etc.).

For example, grant read-only permission within "my-namespace" to the "my-sa" service account:

[REDACTED_ACCOUNT]
kubectl create rolebinding my-sa-view \
  --clusterrole=view \
  --serviceaccount=my-namespace:my-sa \
  --namespace=my-namespace
```

- Grant a role to the "default" service account in a namespaceIf an application does not specify aserviceAccountName, it uses the "default" service account.Note:Permissions given to the "default" service account are available to any pod
in the namespace that does not specify aserviceAccountName.For example, grant read-only permission within "my-namespace" to the "default" service account:[REDACTED_ACCOUNT] create rolebinding default-view\--clusterrole=view\--serviceaccount=my-namespace:default\--namespace=my-namespaceManyadd-onsrun as the
"default" service account in thekube-systemnamespace.
To allow those add-ons to run with super-user access, grant cluster-admin
permissions to the "default" service account in thekube-systemnamespace.Caution:Enabling this means thekube-systemnamespace contains Secrets
that grant super-user access to your cluster's API.kubectl create clusterrolebinding add-on-cluster-admin\--clusterrole=cluster-admin\--serviceaccount=kube-system:default

Grant a role to the "default" service account in a namespace

If an application does not specify aserviceAccountName, it uses the "default" service account.

#### Note:

For example, grant read-only permission within "my-namespace" to the "default" service account:

[REDACTED_ACCOUNT]
kubectl create rolebinding default-view \
  --clusterrole=view \
  --serviceaccount=my-namespace:default \
  --namespace=my-namespace
```

Manyadd-onsrun as the
"default" service account in thekube-systemnamespace.
To allow those add-ons to run with super-user access, grant cluster-admin
permissions to the "default" service account in thekube-systemnamespace.

#### Caution:

```
kubectl create clusterrolebinding add-on-cluster-admin \
  --clusterrole=cluster-admin \
  --serviceaccount=kube-system:default
```

- Grant a role to all service accounts in a namespaceIf you want all applications in a namespace to have a role, no matter what service account they use,
you can grant a role to the service account group for that namespace.For example, grant read-only permission within "my-namespace" to all service accounts in that namespace:kubectl create rolebinding serviceaccounts-view\--clusterrole=view\--group=system:serviceaccounts:my-namespace\--namespace=my-namespace

Grant a role to all service accounts in a namespace

If you want all applications in a namespace to have a role, no matter what service account they use,
you can grant a role to the service account group for that namespace.

For example, grant read-only permission within "my-namespace" to all service accounts in that namespace:

```
kubectl create rolebinding serviceaccounts-view \
  --clusterrole=view \
  --group=system:serviceaccounts:my-namespace \
  --namespace=my-namespace
```

- Grant a limited role to all service accounts cluster-wide (discouraged)If you don't want to manage permissions per-namespace, you can grant a cluster-wide role to all service accounts.For example, grant read-only permission across all namespaces to all service accounts in the cluster:kubectl create clusterrolebinding serviceaccounts-view\--clusterrole=view\--group=system:serviceaccounts

Grant a limited role to all service accounts cluster-wide (discouraged)

If you don't want to manage permissions per-namespace, you can grant a cluster-wide role to all service accounts.

For example, grant read-only permission across all namespaces to all service accounts in the cluster:

```
kubectl create clusterrolebinding serviceaccounts-view \
  --clusterrole=view \
 --group=system:serviceaccounts
```

- Grant super-user access to all service accounts cluster-wide (strongly discouraged)If you don't care about partitioning permissions at all, you can grant super-user access to all service accounts.Warning:This allows any application full access to your cluster, and also grants
any user with read access to Secrets (or the ability to create any pod)
full access to your cluster.kubectl create clusterrolebinding serviceaccounts-cluster-admin\--clusterrole=cluster-admin\--group=system:serviceaccounts

Grant super-user access to all service accounts cluster-wide (strongly discouraged)

If you don't care about partitioning permissions at all, you can grant super-user access to all service accounts.

#### Warning:

```
kubectl create clusterrolebinding serviceaccounts-cluster-admin \
  --clusterrole=cluster-admin \
  --group=system:serviceaccounts
```

## Write access for EndpointSlices

Kubernetes clusters created before Kubernetes v1.22 include write access to
EndpointSlices (and the now-deprecated Endpoints API) in the aggregated "edit" and "admin" roles.
As a mitigation forCVE-2021-25740,
this access is not part of the aggregated roles in clusters that you create using
Kubernetes v1.22 or later.

Existing clusters that have been upgraded to Kubernetes v1.22 will not be
subject to this change. TheCVE
announcementincludes
guidance for restricting this access in existing clusters.

If you want new clusters to retain this level of access in the aggregated roles,
you can create the following ClusterRole:

```
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  annotations:
    kubernetes.io/description: |-
      Add endpoints write permissions to the edit and admin roles. This was
      removed by default in 1.22 because of CVE-2021-25740. See
      https://issue.k8s.io/103675. This can allow writers to direct LoadBalancer
      or Ingress implementations to expose backend IPs that would not otherwise
      be accessible, and can circumvent network policies or security controls
      intended to prevent/isolate access to those backends.
      EndpointSlices were never included in the edit or admin roles, so there
      is nothing to restore for the EndpointSlice API.      
  labels:
    rbac.authorization.k8s.io/aggregate-to-edit: "true"
  name: custom:aggregate-to-edit:endpoints # you can change this if you wish
rules:
  - apiGroups: [""]
    resources: ["endpoints"]
    verbs: ["create", "delete", "deletecollection", "patch", "update"]
```

## Upgrading from ABAC

Clusters that originally ran older Kubernetes versions often used
permissive ABAC policies, including granting full API access to all
service accounts.

Default RBAC policies grant scoped permissions to control-plane components, nodes,
and controllers, but grantno permissionsto service accounts outside thekube-systemnamespace
(beyond the permissions given byAPI discovery roles).

While far more secure, this can be disruptive to existing workloads expecting to automatically receive API permissions.
Here are two approaches for managing this transition:

### Parallel authorizers

Run both the RBAC and ABAC authorizers, and specify a policy file that contains
thelegacy ABAC policy:

```
--authorization-mode=...,RBAC,ABAC --authorization-policy-file=mypolicy.json
```

To explain that first command line option in detail: if earlier authorizers, such as Node,
deny a request, then the RBAC authorizer attempts to authorize the API request. If RBAC
also denies that API request, the ABAC authorizer is then run. This means that any request
allowed byeitherthe RBAC or ABAC policies is allowed.

When the kube-apiserver is run with a log level of 5 or higher for the RBAC component
(--vmodule=rbac*=5or--v=5), you can see RBAC denials in the API server log
(prefixed withRBAC).
You can use that information to determine which roles need to be granted to which users, groups, or service accounts.

Once you havegranted roles to service accountsand workloads
are running with no RBAC denial messages in the server logs, you can remove the ABAC authorizer.

### Permissive RBAC permissions

You can replicate a permissive ABAC policy using RBAC role bindings.

#### Warning:

The following policy allowsALLservice accounts to act as cluster administrators.
Any application running in a container receives service account credentials automatically,
and could perform any action against the API, including viewing secrets and modifying permissions.
This is not a recommended policy.

```
kubectl create clusterrolebinding permissive-binding \
  --clusterrole=cluster-admin \
  --user=[REDACTED_ACCOUNT] \
  --user=[REDACTED_ACCOUNT] \
  --group=system:serviceaccounts
```

After you have transitioned to use RBAC, you should adjust the access controls
for your cluster to ensure that these meet your information security needs.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
