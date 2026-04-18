# 인증 및 권한 부여

### About authentication in {product-title}

To control access to an {product-title} cluster,
a cluster administrator
an administrator with the `dedicated-admin` role
can configure user authentication and ensure only approved users access the cluster.

To interact with an {product-title} cluster, users must first authenticate to the {product-title} API in some way. You can authenticate by providing an OAuth access token or an X.509 client certificate in your requests to the {product-title} API.

> If you do not present a valid access token or certificate, your request is unauthenticated and you receive an HTTP 401 error.

An administrator can configure authentication by configuring an identity provider. You can define any supported identity provider in {product-title} and add it to your cluster.

An administrator can configure authentication through the following tasks:

* Configuring an identity provider: You can define any supported identity provider in {product-title} and add it to your cluster.

* Configuring the internal OAuth server: The {product-title} control plane includes a built-in OAuth server that determines the user's identity from the configured identity provider and creates an access token. You can configure the token duration and inactivity timeout, and customize the internal OAuth server URL.
> Users can view and manage OAuth tokens owned by them.

* Registering an OAuth client: {product-title} includes several default OAuth clients. You can register and configure additional OAuth clients.
> When users send a request for an OAuth token, they must specify either a default or custom OAuth client that receives and uses the token.

* Managing cloud provider credentials using the Cloud Credentials Operator: Cluster components use cloud provider credentials to get permissions required to perform cluster-related tasks.
* Impersonating a system admin user: You can grant cluster administrator permissions to a user by impersonating a system admin user.

### About authorization in {product-title}

Authorization involves determining whether the identified user has permissions to perform the requested action.

Administrators can define permissions and assign them to users using the RBAC objects, such as rules, roles, and bindings. To understand how authorization works in {product-title}, see Evaluating authorization.

You can also control access to an {product-title} cluster through projects and namespaces.

Along with controlling user access to a cluster, you can also control the actions a pod can perform and the resources it can access using security context constraints (SCCs).

You can manage authorization for {product-title} through the following tasks:

* Viewing local and cluster roles and bindings.

* Creating a local role and assigning it to a user or group.

* Creating a cluster role and assigning it to a user or group: {product-title} includes a set of default cluster roles. You can create additional cluster roles and add them to a user or group.
* Assigning a cluster role to a user or group: {product-title} includes a set of default cluster roles. You can add them to a user or group.

* Creating a cluster-admin user: By default, your cluster has only one cluster administrator called `kubeadmin`. You can create another cluster administrator. Before creating a cluster administrator, ensure that you have configured an identity provider.
> After creating the cluster admin user, delete the existing kubeadmin user to improve cluster security.

* Creating cluster-admin and dedicated-admin users: The user who created the {product-title} cluster can grant access to other `cluster-admin` and `dedicated-admin` users.

* Granting administrator privileges to users: You can grant `dedicated-admin` privileges to users.

* Creating service accounts: Service accounts provide a flexible way to control API access without sharing a regular user’s credentials. A user can create and use a service account in applications and also as an OAuth client.

* Scoping tokens: A scoped token is a token that identifies as a specific user who can perform only specific operations. You can create scoped tokens to delegate some of your permissions to another user or a service account.

* Syncing LDAP groups: You can manage user groups in one place by syncing the groups stored in an LDAP server with the {product-title} user groups.
