<!-- source: ocp_projects.md -->

# Projects

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/building_applications/projects
---

# Chapter 2. Projects

## 2.1. Working with projectsCopy linkLink copied to clipboard!

Aprojectallows a community of users to organize and manage their content in isolation from other communities.

Projects starting withopenshift-andkube-aredefault projects. These projects host cluster components that run as pods and other infrastructure components. As such, OpenShift Container Platform does not allow you to create projects starting withopenshift-orkube-using theoc new-projectcommand. Cluster administrators can create these projects using theoc adm new-projectcommand.

Do not run workloads in or share access to default projects. Default projects are reserved for running core cluster components.

The following default projects are considered highly privileged:default,kube-public,kube-system,openshift,openshift-infra,openshift-node, and other system-created projects that have theopenshift.io/run-levellabel set to0or1. Functionality that relies on admission plugins, such as pod security admission, security context constraints, cluster resource quotas, and image reference resolution, does not work in highly privileged projects.

### 2.1.1. Creating a projectCopy linkLink copied to clipboard!

You can use the OpenShift Container Platform web console or the OpenShift CLI (oc) to create a project in your cluster.

#### 2.1.1.1. Creating a project by using the web consoleCopy linkLink copied to clipboard!

You can use the OpenShift Container Platform web console to create a project in your cluster.

Projects starting withopenshift-andkube-are considered critical by OpenShift Container Platform. As such, OpenShift Container Platform does not allow you to create projects starting withopenshift-using the web console.

Prerequisites

- Ensure that you have the appropriate roles and permissions to create projects, applications, and other workloads in OpenShift Container Platform.

Procedure

- If you are using theAdministratorperspective:Navigate toHomeProjects.ClickCreate Project:In theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.Optional: Add theDisplay nameandDescriptiondetails for the project.ClickCreate.The dashboard for your project is displayed.Optional: Select theDetailstab to view the project details.Optional: If you have adequate permissions for a project, you can use theProject Accesstab to provide or revoke admin, edit, and view privileges for the project.

If you are using theAdministratorperspective:

- Navigate toHomeProjects.
- ClickCreate Project:In theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.Optional: Add theDisplay nameandDescriptiondetails for the project.ClickCreate.The dashboard for your project is displayed.

ClickCreate Project:

- In theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.
- Optional: Add theDisplay nameandDescriptiondetails for the project.
- ClickCreate.The dashboard for your project is displayed.

ClickCreate.

The dashboard for your project is displayed.

- Optional: Select theDetailstab to view the project details.
- Optional: If you have adequate permissions for a project, you can use theProject Accesstab to provide or revoke admin, edit, and view privileges for the project.
- If you are using theDeveloperperspective:Click theProjectmenu and selectCreate Project:Figure 2.1. Create projectIn theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.Optional: Add theDisplay nameandDescriptiondetails for the project.ClickCreate.Optional: Use the left navigation panel to navigate to theProjectview and see the dashboard for your project.Optional: In the project dashboard, select theDetailstab to view the project details.Optional: If you have adequate permissions for a project, you can use theProject Accesstab of the project dashboard to provide or revoke admin, edit, and view privileges for the project.

If you are using theDeveloperperspective:

- Click theProjectmenu and selectCreate Project:Figure 2.1. Create projectIn theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.Optional: Add theDisplay nameandDescriptiondetails for the project.ClickCreate.

Click theProjectmenu and selectCreate Project:

Figure 2.1. Create project

- In theCreate Projectdialog box, enter a unique name, such asmyproject, in theNamefield.
- Optional: Add theDisplay nameandDescriptiondetails for the project.
- ClickCreate.
- Optional: Use the left navigation panel to navigate to theProjectview and see the dashboard for your project.
- Optional: In the project dashboard, select theDetailstab to view the project details.
- Optional: If you have adequate permissions for a project, you can use theProject Accesstab of the project dashboard to provide or revoke admin, edit, and view privileges for the project.

Additional resources

- Customizing the available cluster roles using the web console

#### 2.1.1.2. Creating a project by using the CLICopy linkLink copied to clipboard!

If allowed by your cluster administrator, you can create a new project.

Projects starting withopenshift-andkube-are considered critical by OpenShift Container Platform. As such, OpenShift Container Platform does not allow you to create Projects starting withopenshift-orkube-using theoc new-projectcommand. Cluster administrators can create these projects using theoc adm new-projectcommand.

Procedure

- Run:oc new-project <project_name> \
    --description="<description>" --display-name="<display_name>"$oc new-project<project_name>\--description="<description>"--display-name="<display_name>"Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:oc new-project hello-openshift \
    --description="This is an example project" \
    --display-name="Hello OpenShift"$oc new-project hello-openshift\--description="This is an example project"\--display-name="Hello OpenShift"Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run:

```
oc new-project <project_name> \
    --description="<description>" --display-name="<display_name>"
```

```
$ oc new-project <project_name> \
    --description="<description>" --display-name="<display_name>"
```

For example:

```
oc new-project hello-openshift \
    --description="This is an example project" \
    --display-name="Hello OpenShift"
```

```
$ oc new-project hello-openshift \
    --description="This is an example project" \
    --display-name="Hello OpenShift"
```

The number of projects you are allowed to create might be limited by the system administrator. After your limit is reached, you might have to delete an existing project in order to create a new one.

### 2.1.2. Viewing a projectCopy linkLink copied to clipboard!

You can use the OpenShift Container Platform web console or the OpenShift CLI (oc) to view a project in your cluster.

#### 2.1.2.1. Viewing a project by using the web consoleCopy linkLink copied to clipboard!

You can view the projects that you have access to by using the OpenShift Container Platform web console.

Procedure

- If you are using theAdministratorperspective:Navigate toHomeProjectsin the navigation menu.Select a project to view. TheOverviewtab includes a dashboard for your project.Select theDetailstab to view the project details.Select theYAMLtab to view and update the YAML configuration for the project resource.Select theWorkloadstab to see workloads in the project.Select theRoleBindingstab to view and create role bindings for your project.

If you are using theAdministratorperspective:

- Navigate toHomeProjectsin the navigation menu.
- Select a project to view. TheOverviewtab includes a dashboard for your project.
- Select theDetailstab to view the project details.
- Select theYAMLtab to view and update the YAML configuration for the project resource.
- Select theWorkloadstab to see workloads in the project.
- Select theRoleBindingstab to view and create role bindings for your project.
- If you are using theDeveloperperspective:Navigate to theProjectpage in the navigation menu.SelectAll Projectsfrom theProjectdrop-down menu at the top of the screen to list all of the projects in your cluster.Select a project to view. TheOverviewtab includes a dashboard for your project.Select theDetailstab to view the project details.If you have adequate permissions for a project, select theProject accesstab view and update the privileges for the project.

If you are using theDeveloperperspective:

- Navigate to theProjectpage in the navigation menu.
- SelectAll Projectsfrom theProjectdrop-down menu at the top of the screen to list all of the projects in your cluster.
- Select a project to view. TheOverviewtab includes a dashboard for your project.
- Select theDetailstab to view the project details.
- If you have adequate permissions for a project, select theProject accesstab view and update the privileges for the project.

#### 2.1.2.2. Viewing a project using the CLICopy linkLink copied to clipboard!

When viewing projects, you are restricted to seeing only the projects you have access to view based on the authorization policy.

Procedure

- To view a list of projects, run:oc get projects$oc get projectsCopy to ClipboardCopied!Toggle word wrapToggle overflow

To view a list of projects, run:

- You can change from the current project to a different project for CLI operations. The specified project is then used in all subsequent operations that manipulate project-scoped content:oc project <project_name>$oc project<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

You can change from the current project to a different project for CLI operations. The specified project is then used in all subsequent operations that manipulate project-scoped content:

### 2.1.3. Providing access permissions to your project using the Developer perspectiveCopy linkLink copied to clipboard!

You can use theProjectview in theDeveloperperspective to grant or revoke access permissions to your project.

Prerequisites

- You have created a project.

Procedure

To add users to your project and provideAdmin,Edit, orViewaccess to them:

- In theDeveloperperspective, navigate to theProjectpage.
- Select your project from theProjectmenu.
- Select theProject Accesstab.
- ClickAdd accessto add a new row of permissions to the default ones.Figure 2.2. Project permissions

ClickAdd accessto add a new row of permissions to the default ones.

Figure 2.2. Project permissions

- Enter the user name, click theSelect a roledrop-down list, and select an appropriate role.
- ClickSaveto add the new permissions.

You can also use:

- TheSelect a roledrop-down list, to modify the access permissions of an existing user.
- TheRemove Accessicon, to completely remove the access permissions of an existing user to the project.

Advanced role-based access control is managed in theRolesandRoles Bindingviews in theAdministratorperspective.

### 2.1.4. Customizing the available cluster roles using the web consoleCopy linkLink copied to clipboard!

In theDeveloperperspective of the web console, theProjectProject accesspage enables a project administrator to grant roles to users in a project. By default, the available cluster roles that can be granted to users in a project are admin, edit, and view.

As a cluster administrator, you can define which cluster roles are available in theProject accesspage for all projects cluster-wide. You can specify the available roles by customizing thespec.customization.projectAccess.availableClusterRolesobject in theConsoleconfiguration resource.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.

Procedure

- In theAdministratorperspective, navigate toAdministrationCluster settings.
- Click theConfigurationtab.
- From theConfiguration resourcelist, selectConsoleoperator.openshift.io.
- Navigate to theYAMLtab to view and edit the YAML code.
- In the YAML code underspec, customize the list of available cluster roles for project access. The following example specifies the defaultadmin,edit, andviewroles:apiVersion: operator.openshift.io/v1
kind: Console
metadata:
  name: cluster
# ...
spec:
  customization:
    projectAccess:
      availableClusterRoles:
      - admin
      - edit
      - viewapiVersion:operator.openshift.io/v1kind:Consolemetadata:name:cluster# ...spec:customization:projectAccess:availableClusterRoles:-admin-edit-viewCopy to ClipboardCopied!Toggle word wrapToggle overflow

In the YAML code underspec, customize the list of available cluster roles for project access. The following example specifies the defaultadmin,edit, andviewroles:

```
apiVersion: operator.openshift.io/v1
kind: Console
metadata:
  name: cluster
# ...
spec:
  customization:
    projectAccess:
      availableClusterRoles:
      - admin
      - edit
      - view
```

```
apiVersion: operator.openshift.io/v1
kind: Console
metadata:
  name: cluster
# ...
spec:
  customization:
    projectAccess:
      availableClusterRoles:
      - admin
      - edit
      - view
```

- ClickSaveto save the changes to theConsoleconfiguration resource.

Verification

- In theDeveloperperspective, navigate to theProjectpage.
- Select a project from theProjectmenu.
- Select theProject accesstab.
- Click the menu in theRolecolumn and verify that the available roles match the configuration that you applied to theConsoleresource configuration.

### 2.1.5. Adding to a projectCopy linkLink copied to clipboard!

You can add items to your project by using the+Addpage in theDeveloperperspective.

Prerequisites

- You have created a project.

Procedure

- In theDeveloperperspective, navigate to the+Addpage.
- Select your project from theProjectmenu.
- Click on an item on the+Addpage and then follow the workflow.

You can also use the search feature in theAdd* page to find additional items to add to your project. Click *underAddat the top of the page and type the name of a component in the search field.

### 2.1.6. Checking the project statusCopy linkLink copied to clipboard!

You can use the OpenShift Container Platform web console or the OpenShift CLI (oc) to view the status of your project.

#### 2.1.6.1. Checking project status by using the web consoleCopy linkLink copied to clipboard!

You can review the status of your project by using the web console.

Prerequisites

- You have created a project.

Procedure

- If you are using theAdministratorperspective:Navigate toHomeProjects.Select a project from the list.Review the project status in theOverviewpage.

If you are using theAdministratorperspective:

- Navigate toHomeProjects.
- Select a project from the list.
- Review the project status in theOverviewpage.
- If you are using theDeveloperperspective:Navigate to theProjectpage.Select a project from theProjectmenu.Review the project status in theOverviewpage.

If you are using theDeveloperperspective:

- Navigate to theProjectpage.
- Select a project from theProjectmenu.
- Review the project status in theOverviewpage.

#### 2.1.6.2. Checking project status by using the CLICopy linkLink copied to clipboard!

You can review the status of your project by using the OpenShift CLI (oc).

Prerequisites

- You have installed the OpenShift CLI (oc).
- You have created a project.

Procedure

- Switch to your project:oc project <project_name>$oc project<project_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<project_name>with the name of your project.

Switch to your project:

**1**
  Replace<project_name>with the name of your project.
- Obtain a high-level overview of the project:oc status$oc statusCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a high-level overview of the project:

### 2.1.7. Deleting a projectCopy linkLink copied to clipboard!

You can use the OpenShift Container Platform web console or the OpenShift CLI (oc) to delete a project.

When you delete a project, the server updates the project status toTerminatingfromActive. Then, the server clears all content from a project that is in theTerminatingstate before finally removing the project. While a project is inTerminatingstatus, you cannot add new content to the project. Projects can be deleted from the CLI or the web console.

#### 2.1.7.1. Deleting a project by using the web consoleCopy linkLink copied to clipboard!

You can delete a project by using the web console.

Prerequisites

- You have created a project.
- You have the required permissions to delete the project.

Procedure

- If you are using theAdministratorperspective:Navigate toHomeProjects.Select a project from the list.Click theActionsdrop-down menu for the project and selectDelete Project.TheDelete Projectoption is not available if you do not have the required permissions to delete the project.In theDelete Project?pane, confirm the deletion by entering the name of your project.ClickDelete.

If you are using theAdministratorperspective:

- Navigate toHomeProjects.
- Select a project from the list.
- Click theActionsdrop-down menu for the project and selectDelete Project.TheDelete Projectoption is not available if you do not have the required permissions to delete the project.In theDelete Project?pane, confirm the deletion by entering the name of your project.ClickDelete.

Click theActionsdrop-down menu for the project and selectDelete Project.

TheDelete Projectoption is not available if you do not have the required permissions to delete the project.

- In theDelete Project?pane, confirm the deletion by entering the name of your project.
- ClickDelete.
- If you are using theDeveloperperspective:Navigate to theProjectpage.Select the project that you want to delete from theProjectmenu.Click theActionsdrop-down menu for the project and selectDelete Project.If you do not have the required permissions to delete the project, theDelete Projectoption is not available.In theDelete Project?pane, confirm the deletion by entering the name of your project.ClickDelete.

If you are using theDeveloperperspective:

- Navigate to theProjectpage.
- Select the project that you want to delete from theProjectmenu.
- Click theActionsdrop-down menu for the project and selectDelete Project.If you do not have the required permissions to delete the project, theDelete Projectoption is not available.In theDelete Project?pane, confirm the deletion by entering the name of your project.ClickDelete.

Click theActionsdrop-down menu for the project and selectDelete Project.

If you do not have the required permissions to delete the project, theDelete Projectoption is not available.

- In theDelete Project?pane, confirm the deletion by entering the name of your project.
- ClickDelete.

#### 2.1.7.2. Deleting a project by using the CLICopy linkLink copied to clipboard!

You can delete a project by using the OpenShift CLI (oc).

Prerequisites

- You have installed the OpenShift CLI (oc).
- You have created a project.
- You have the required permissions to delete the project.

Procedure

- Delete your project:oc delete project <project_name>$oc delete project<project_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<project_name>with the name of the project that you want to delete.

Delete your project:

**1**
  Replace<project_name>with the name of the project that you want to delete.

## 2.2. Creating a project as another userCopy linkLink copied to clipboard!

Impersonation allows you to create a project as a different user.

### 2.2.1. API impersonationCopy linkLink copied to clipboard!

You can configure a request to the OpenShift Container Platform API to act as though it originated from another user. For more information, seeUser impersonationin the Kubernetes documentation.

### 2.2.2. Impersonating a user when you create a projectCopy linkLink copied to clipboard!

You can impersonate a different user when you create a project request. Becausesystem:authenticated:oauthis the only bootstrap group that can create project requests, you must impersonate that group.

Procedure

- To create a project request on behalf of a different user:[REDACTED_ACCOUNT] new-project <project> --as=<user> \
    --as-group=system:authenticated --as-group=system:authenticated:oauth$oc new-project<project>--as=<user>\--as-group=system:authenticated --as-group=system:authenticated:oauthCopy to ClipboardCopied!Toggle word wrapToggle overflow

To create a project request on behalf of a different user:

[REDACTED_ACCOUNT]
oc new-project <project> --as=<user> \
    --as-group=system:authenticated --as-group=system:authenticated:oauth
```

```
$ oc new-project <project> --as=<user> \
    --as-group=system:authenticated --as-group=system:authenticated:oauth
```

## 2.3. Configuring project creationCopy linkLink copied to clipboard!

In OpenShift Container Platform,projectsare used to group and isolate related objects. When a request is made to create a new project using the web console oroc new-projectcommand, an endpoint in OpenShift Container Platform is used to provision the project according to a template, which can be customized.

As a cluster administrator, you can allow and configure how developers and service accounts can create, orself-provision, their own projects.

### 2.3.1. About project creationCopy linkLink copied to clipboard!

The OpenShift Container Platform API server automatically provisions new projects based on the project template that is identified by theprojectRequestTemplateparameter in the cluster’s project configuration resource. If the parameter is not defined, the API server creates a default template that creates a project with the requested name, and assigns the requesting user to theadminrole for that project.

When a project request is submitted, the API substitutes the following parameters into the template:

| Parameter | Description |
| --- | --- |
| PROJECT_NAME | The name of the project. Required. |
| PROJECT_DISPLAYNAME | The display name of the project. May be empty. |
| PROJECT_DESCRIPTION | The description of the project. May be empty. |
| PROJECT_ADMIN_USER | The user name of the administrating user. |
| PROJECT_REQUESTING_USER | The user name of the requesting user. |

PROJECT_NAME

The name of the project. Required.

PROJECT_DISPLAYNAME

The display name of the project. May be empty.

PROJECT_DESCRIPTION

The description of the project. May be empty.

PROJECT_ADMIN_USER

The user name of the administrating user.

PROJECT_REQUESTING_USER

The user name of the requesting user.

Access to the API is granted to developers with theself-provisionerrole and theself-provisionerscluster role binding. This role is available to all authenticated developers by default.

### 2.3.2. Modifying the template for new projectsCopy linkLink copied to clipboard!

As a cluster administrator, you can modify the default project template so that new projects are created using your custom requirements.

To create your own custom project template:

Prerequisites

- You have access to an OpenShift Container Platform cluster using an account withcluster-adminpermissions.

Procedure

- Log in as a user withcluster-adminprivileges.
- Generate the default project template:oc adm create-bootstrap-project-template -o yaml > template.yaml$oc adm create-bootstrap-project-template-oyaml>template.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Generate the default project template:

- Use a text editor to modify the generatedtemplate.yamlfile by adding objects or modifying existing objects.
- The project template must be created in theopenshift-confignamespace. Load your modified template:oc create -f template.yaml -n openshift-config$oc create-ftemplate.yaml-nopenshift-configCopy to ClipboardCopied!Toggle word wrapToggle overflow

The project template must be created in theopenshift-confignamespace. Load your modified template:

- Edit the project configuration resource using the web console or CLI.Using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.Using the CLI:Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit the project configuration resource using the web console or CLI.

- Using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.

Using the web console:

- Navigate to theAdministrationCluster Settingspage.
- ClickConfigurationto view all configuration resources.
- Find the entry forProjectand clickEdit YAML.
- Using the CLI:Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Using the CLI:

- Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theproject.config.openshift.io/clusterresource:

- Update thespecsection to include theprojectRequestTemplateandnameparameters, and set the name of your uploaded project template. The default name isproject-request.Project configuration resource with custom project templateapiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestTemplate:
    name: <template_name>
# ...apiVersion:config.openshift.io/v1kind:Projectmetadata:# ...spec:projectRequestTemplate:name:<template_name># ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Update thespecsection to include theprojectRequestTemplateandnameparameters, and set the name of your uploaded project template. The default name isproject-request.

Project configuration resource with custom project template

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestTemplate:
    name: <template_name>
# ...
```

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestTemplate:
    name: <template_name>
# ...
```

- After you save your changes, create a new project to verify that your changes were successfully applied.

### 2.3.3. Disabling project self-provisioningCopy linkLink copied to clipboard!

You can prevent an authenticated user group from self-provisioning new projects.

Procedure

- Log in as a user withcluster-adminprivileges.
- View theself-provisionerscluster role binding usage by running the following command:oc describe clusterrolebinding.rbac self-provisioners$oc describe clusterrolebinding.rbac self-provisionersCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:		self-provisioners
Labels:		<none>
Annotations:	rbac.authorization.kubernetes.io/autoupdate=true
Role:
  Kind:	ClusterRole
  Name:	self-provisioner
Subjects:
  Kind	Name				Namespace
  ----	----				---------
  Group	system:authenticated:oauthName:		self-provisioners
Labels:		<none>
Annotations:	rbac.authorization.kubernetes.io/autoupdate=true
Role:
  Kind:	ClusterRole
  Name:	self-provisioner
Subjects:
  Kind	Name				Namespace
  ----	----				---------
  Group	system:authenticated:oauthCopy to ClipboardCopied!Toggle word wrapToggle overflowReview the subjects in theself-provisionerssection.

View theself-provisionerscluster role binding usage by running the following command:

Example output

```
Name:		self-provisioners
Labels:		<none>
Annotations:	rbac.authorization.kubernetes.io/autoupdate=true
Role:
  Kind:	ClusterRole
  Name:	self-provisioner
Subjects:
  Kind	Name				Namespace
  ----	----				---------
  Group	system:authenticated:oauth
```

```
Name:		self-provisioners
Labels:		<none>
Annotations:	rbac.authorization.kubernetes.io/autoupdate=true
Role:
  Kind:	ClusterRole
  Name:	self-provisioner
Subjects:
  Kind	Name				Namespace
  ----	----				---------
  Group	system:authenticated:oauth
```

Review the subjects in theself-provisionerssection.

- Remove theself-provisionercluster role from the groupsystem:authenticated:oauth.If theself-provisionerscluster role binding binds only theself-provisionerrole to thesystem:authenticated:oauthgroup, run the following command:oc patch clusterrolebinding.rbac self-provisioners -p '{"subjects": null}'$oc patch clusterrolebinding.rbac self-provisioners-p'{"subjects": null}'Copy to ClipboardCopied!Toggle word wrapToggle overflowIf theself-provisionerscluster role binding binds theself-provisionerrole to more users, groups, or service accounts than thesystem:authenticated:oauthgroup, run the following command:oc adm policy \
    remove-cluster-role-from-group self-provisioner \
    system:authenticated:oauth$oc adm policy\remove-cluster-role-from-group self-provisioner\system:authenticated:oauthCopy to ClipboardCopied!Toggle word wrapToggle overflow

Remove theself-provisionercluster role from the groupsystem:authenticated:oauth.

- If theself-provisionerscluster role binding binds only theself-provisionerrole to thesystem:authenticated:oauthgroup, run the following command:oc patch clusterrolebinding.rbac self-provisioners -p '{"subjects": null}'$oc patch clusterrolebinding.rbac self-provisioners-p'{"subjects": null}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

If theself-provisionerscluster role binding binds only theself-provisionerrole to thesystem:authenticated:oauthgroup, run the following command:

- If theself-provisionerscluster role binding binds theself-provisionerrole to more users, groups, or service accounts than thesystem:authenticated:oauthgroup, run the following command:oc adm policy \
    remove-cluster-role-from-group self-provisioner \
    system:authenticated:oauth$oc adm policy\remove-cluster-role-from-group self-provisioner\system:authenticated:oauthCopy to ClipboardCopied!Toggle word wrapToggle overflow

If theself-provisionerscluster role binding binds theself-provisionerrole to more users, groups, or service accounts than thesystem:authenticated:oauthgroup, run the following command:

```
oc adm policy \
    remove-cluster-role-from-group self-provisioner \
    system:authenticated:oauth
```

```
$ oc adm policy \
    remove-cluster-role-from-group self-provisioner \
    system:authenticated:oauth
```

- Edit theself-provisionerscluster role binding to prevent automatic updates to the role. Automatic updates reset the cluster roles to the default state.To update the role binding using the CLI:Run the following command:oc edit clusterrolebinding.rbac self-provisioners$oc edit clusterrolebinding.rbac self-provisionersCopy to ClipboardCopied!Toggle word wrapToggle overflowIn the displayed role binding, set therbac.authorization.kubernetes.io/autoupdateparameter value tofalse, as shown in the following example:apiVersion: authorization.openshift.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "false"
# ...apiVersion:authorization.openshift.io/v1kind:ClusterRoleBindingmetadata:annotations:rbac.authorization.kubernetes.io/autoupdate:"false"# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowTo update the role binding by using a single command:oc patch clusterrolebinding.rbac self-provisioners -p '{ "metadata": { "annotations": { "rbac.authorization.kubernetes.io/autoupdate": "false" } } }'$oc patch clusterrolebinding.rbac self-provisioners-p'{ "metadata": { "annotations": { "rbac.authorization.kubernetes.io/autoupdate": "false" } } }'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theself-provisionerscluster role binding to prevent automatic updates to the role. Automatic updates reset the cluster roles to the default state.

- To update the role binding using the CLI:Run the following command:oc edit clusterrolebinding.rbac self-provisioners$oc edit clusterrolebinding.rbac self-provisionersCopy to ClipboardCopied!Toggle word wrapToggle overflowIn the displayed role binding, set therbac.authorization.kubernetes.io/autoupdateparameter value tofalse, as shown in the following example:apiVersion: authorization.openshift.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "false"
# ...apiVersion:authorization.openshift.io/v1kind:ClusterRoleBindingmetadata:annotations:rbac.authorization.kubernetes.io/autoupdate:"false"# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

To update the role binding using the CLI:

- Run the following command:oc edit clusterrolebinding.rbac self-provisioners$oc edit clusterrolebinding.rbac self-provisionersCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command:

- In the displayed role binding, set therbac.authorization.kubernetes.io/autoupdateparameter value tofalse, as shown in the following example:apiVersion: authorization.openshift.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "false"
# ...apiVersion:authorization.openshift.io/v1kind:ClusterRoleBindingmetadata:annotations:rbac.authorization.kubernetes.io/autoupdate:"false"# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

In the displayed role binding, set therbac.authorization.kubernetes.io/autoupdateparameter value tofalse, as shown in the following example:

```
apiVersion: authorization.openshift.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "false"
# ...
```

```
apiVersion: authorization.openshift.io/v1
kind: ClusterRoleBinding
metadata:
  annotations:
    rbac.authorization.kubernetes.io/autoupdate: "false"
# ...
```

- To update the role binding by using a single command:oc patch clusterrolebinding.rbac self-provisioners -p '{ "metadata": { "annotations": { "rbac.authorization.kubernetes.io/autoupdate": "false" } } }'$oc patch clusterrolebinding.rbac self-provisioners-p'{ "metadata": { "annotations": { "rbac.authorization.kubernetes.io/autoupdate": "false" } } }'Copy to ClipboardCopied!Toggle word wrapToggle overflow

To update the role binding by using a single command:

- Log in as an authenticated user and verify that it can no longer self-provision a project:oc new-project test$oc new-projecttestCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputError from server (Forbidden): You may not request a new project via this API.Error from server (Forbidden): You may not request a new project via this API.Copy to ClipboardCopied!Toggle word wrapToggle overflowConsider customizing this project request message to provide more helpful instructions specific to your organization.

Log in as an authenticated user and verify that it can no longer self-provision a project:

Example output

Consider customizing this project request message to provide more helpful instructions specific to your organization.

### 2.3.4. Customizing the project request messageCopy linkLink copied to clipboard!

When a developer or a service account that is unable to self-provision projects makes a project creation request using the web console or CLI, the following error message is returned by default:

Cluster administrators can customize this message. Consider updating it to provide further instructions on how to request a new project specific to your organization. For example:

- To request a project, contact your system administrator [REDACTED_EMAIL].
- To request a new project, fill out the project request form located athttps://internal.example.com/openshift-project-request.

To customize the project request message:

Procedure

- Edit the project configuration resource using the web console or CLI.Using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.Using the CLI:Log in as a user withcluster-adminprivileges.Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit the project configuration resource using the web console or CLI.

- Using the web console:Navigate to theAdministrationCluster Settingspage.ClickConfigurationto view all configuration resources.Find the entry forProjectand clickEdit YAML.

Using the web console:

- Navigate to theAdministrationCluster Settingspage.
- ClickConfigurationto view all configuration resources.
- Find the entry forProjectand clickEdit YAML.
- Using the CLI:Log in as a user withcluster-adminprivileges.Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Using the CLI:

- Log in as a user withcluster-adminprivileges.
- Edit theproject.config.openshift.io/clusterresource:oc edit project.config.openshift.io/cluster$oc edit project.config.openshift.io/clusterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theproject.config.openshift.io/clusterresource:

- Update thespecsection to include theprojectRequestMessageparameter and set the value to your custom message:Project configuration resource with custom project request messageapiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: <message_string>
# ...apiVersion:config.openshift.io/v1kind:Projectmetadata:# ...spec:projectRequestMessage:<message_string># ...Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example:apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: To request a project, contact your system administrator at [REDACTED_EMAIL].
# ...apiVersion:config.openshift.io/v1kind:Projectmetadata:# ...spec:projectRequestMessage:To request a project,contact your system administrator at [REDACTED_EMAIL].# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Update thespecsection to include theprojectRequestMessageparameter and set the value to your custom message:

Project configuration resource with custom project request message

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: <message_string>
# ...
```

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: <message_string>
# ...
```

For example:

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: To request a project, contact your system administrator at [REDACTED_EMAIL].
# ...
```

```
apiVersion: config.openshift.io/v1
kind: Project
metadata:
# ...
spec:
  projectRequestMessage: To request a project, contact your system administrator at [REDACTED_EMAIL].
# ...
```

- After you save your changes, attempt to create a new project as a developer or service account that is unable to self-provision projects to verify that your changes were successfully applied.
