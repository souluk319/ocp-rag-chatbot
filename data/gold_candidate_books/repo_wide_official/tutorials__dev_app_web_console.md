# Deploying an application by using the web console

[FIGURE src="/playbooks/wiki-assets/repo_wide_official/tutorials__dev_app_web_console/getting-started-examine-pod.png" alt="Topology view of parksmap deployment" kind="diagram" diagram_type="semantic_diagram"]
Topology view of parksmap deployment
[/FIGURE]

_Source: `getting-started-web-console-examining-pod.adoc` · asset `getting-started-examine-pod.png`_


[FIGURE src="/playbooks/wiki-assets/repo_wide_official/tutorials__dev_app_web_console/getting-started-scaling-pod.png" alt="Scaling pod to two instances" kind="figure" diagram_type="image_figure"]
Scaling pod to two instances
[/FIGURE]

_Source: `getting-started-web-console-scaling-app.adoc` · asset `getting-started-scaling-pod.png`_


[FIGURE src="/playbooks/wiki-assets/repo_wide_official/tutorials__dev_app_web_console/getting-started-parksmap-url.png" alt="Opening the URL for the parksmap deployment" kind="figure" diagram_type="image_figure"]
Opening the URL for the parksmap deployment
[/FIGURE]

_Source: `getting-started-web-console-view.adoc` · asset `getting-started-parksmap-url.png`_


[FIGURE src="/playbooks/wiki-assets/repo_wide_official/tutorials__dev_app_web_console/getting-started-map-national-parks.png" alt="Map of the national parks across the world" kind="figure" diagram_type="image_figure"]
Map of the national parks across the world
[/FIGURE]

_Source: `getting-started-web-console-view.adoc` · asset `getting-started-map-national-parks.png`_


To learn how to stand up an application on OpenShift Container Platform by using the web console, follow the provided tutorial. In this tutorial, you will deploy the services that are required for an application that displays a map of national parks across the world.

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

* You have access to a test OpenShift Container Platform cluster.
If your organization does not have a cluster to test on, you can request access to the [Developer Sandbox](https://developers.redhat.com/developer-sandbox) to get a trial of OpenShift Container Platform.

* You have the appropriate permissions, such as the `cluster-admin` cluster role, to create a project and applications within it.
If you do not have the required permissions, contact your cluster administrator. You need the `self-provisioner` role to create a project and the `admin` role on the project to modify resources in that project.
If you are using Developer Sandbox, a project is created for you with the required permissions.

* You have logged in to the OpenShift Container Platform web console.

Additional resources
* Viewing a project by using the web console

Additional resources
* RBAC overview

Additional resources
* Viewing the topology of your application

Additional resources
* Interacting with applications and components
* Scaling application pods and checking builds and routes
* Labels and annotations used for the Topology view

Additional resources
* Recommended practices for scaling the cluster

Additional resources
* Adding services to your application
* Importing a codebase from Git to create an application

Additional resources
* Understanding secrets
