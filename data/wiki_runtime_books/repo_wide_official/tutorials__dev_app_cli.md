# Deploying an application by using the CLI

[FIGURE src="/playbooks/wiki-assets/repo_wide_official/tutorials__dev_app_cli/getting-started-map-national-parks.png" alt="Map of the national parks across the world" kind="figure" diagram_type="image_figure"]
Map of the national parks across the world
[/FIGURE]

_Source: `getting-started-cli-view.adoc` · asset `getting-started-map-national-parks.png`_


To learn how to stand up an application on OpenShift Container Platform by using the {oc-first}, follow the provided tutorial. In this tutorial, you will deploy the services that are required for an application that displays a map of national parks across the world.

To complete this tutorial, you will perform the following steps:

 Create a project for the application.
This step allows your application to be isolated from other cluster user's workloads.

 Grant view permissions.
This step grants `view` permissions to interact with the OpenShift API to help discover services and other resources running within the project.

 Deploy the front-end application.
This step deploys the `parksmap` front-end application, exposes it externally, and scales it up to two instances.

 Deploy the back-end application.
This step deploys the `nationalparks` back-end application and exposes it externally.

 Deploy the database application.
This step deploys the `mongodb-nationalparks` MongoDB database, loads data into the database, and sets up the necessary credentials to access the database.

After you complete these steps, you can view the national parks application in a web browser.

### Prerequisites

Before you start this tutorial, ensure that you have the following required prerequisites:

* You have installed the {oc-first}.
* You have access to a test OpenShift Container Platform cluster.
If your organization does not have a cluster to test on, you can request access to the [Developer Sandbox](https://developers.redhat.com/developer-sandbox) to get a trial of OpenShift Container Platform.

* You have the appropriate permissions, such as the `cluster-admin` cluster role, to create a project and applications within it.
If you do not have the required permissions, contact your cluster administrator. You need the `self-provisioner` role to create a project and the `admin` role on the project to modify resources in that project.
If you are using Developer Sandbox, a project is created for you with the required permissions.

* You have logged in to your cluster by using the {oc-first}.

Additional resources
* oc new-project

Additional resources
* RBAC overview
* oc adm policy add-role-to-user

Additional resources
* oc new-app

Additional resources
* oc create route edge
* oc get

Additional resources
* oc describe
* oc get
* Viewing pods
* Viewing pod logs

Additional resources
* oc scale

Additional resources
* oc label

Additional resources
* Understanding secrets
* oc create secret generic
* oc set env
* oc rollout status

Additional resources
* oc exec

### Optional: Continuing to explore

Now that your application is successfully running, you can continue exploring the following aspects:

* Viewing pod details for your deployments
* Scaling up your deployments

Additional resources
* oc describe
* oc get
* Viewing pods
* Viewing pod logs

Additional resources
* oc scale
