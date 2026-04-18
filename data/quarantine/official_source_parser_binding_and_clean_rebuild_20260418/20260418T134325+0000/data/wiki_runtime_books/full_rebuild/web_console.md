# 웹 콘솔

## Web Console Overview

The {product-title} web console provides a graphical user interface to visualize your project data and perform administrative, management, and troubleshooting tasks. The web console runs as pods on the control plane nodes in the openshift-console project. It is managed by a `console-operator` pod.

You can create quick start tutorials for {product-title} that provide guided steps within the web console with user tasks. They are helpful for getting oriented with an application, Operator, or other product offering.

Additional resources

* Learn more about Cluster Administrator
* Viewing the applications in your project, verifying their deployment status, and interacting with them in the *Topology* view
* Viewing cluster information
* Configuring the web console
* Customizing the web console
* About the web console
* Using the web terminal
* Creating quick start tutorials
* Disabling the web console

## Accessing the web console

The {product-title} web console is a user interface accessible from a web browser. You can use the web console to visualize, browse, and manage the contents of projects.

#### Prerequisites

* You must use one of the following supported web browsers: Edge, Chrome, Safari, or Mozilla Firefox. IE 11 and earlier is not supported.
* Review the [OpenShift ContainerPlatform 4.x Tested Integrations](https://access.redhat.com/articles/4128421) page before you create the supporting infrastructure for your cluster.

Additional resources
* Enabling feature sets using the web console

## Using the {product-title} dashboard to get cluster information

The {product-title} web console captures high-level information about the cluster.

## Adding user preferences

You can change the default preferences for your profile to meet your requirements. You can set your default project, topology view (graph or list), editing medium (form or YAML), language preferences, and resource type.

The changes made to the user preferences are automatically saved.

## Configuring the web console in {product-title}

You can modify the {product-title} web console to set a logout redirect URL
or disable the quick start tutorials.

#### Prerequisites

* Deploy an {product-title} cluster.

## Customizing the web console in {product-title}

You can customize the
web console to set
a custom logo, product name, links, notifications, and command-line downloads.
a custom logo and product name.
This is especially helpful if you need to tailor the web console to meet specific corporate or government requirements.

## Overview of dynamic plugins

#### About dynamic plugins

Dynamic plugins are loaded and interpreted from remote sources at runtime. One way to deliver and expose dynamic plugins to the console is through OLM Operators. The Operator creates a deployment on the platform with an HTTP server to host the plugin and exposes it using a Kubernetes service.

Dynamic plugins allow you to add custom pages and other extensions to your console user interface at runtime. The `ConsolePlugin` custom resource registers plugins with the console, and a cluster administrator enables plugins in the console Operator configuration.

#### Key features

A dynamic plugin allows you to make the following customizations to the {product-title} experience:

* Add custom pages.
* Add perspectives beyond administrator and developer.
* Add navigation items.
* Add tabs and actions to resource pages.

#### General guidelines

When creating your plugin, follow these general guidelines:

* [`Node.js`](https://nodejs.org/en/) and [`yarn`](https://yarnpkg.com/) are required to build and run your plugin.
* Prefix your CSS class names with your plugin name to avoid collisions. For example, `my-plugin_\_heading` and `my-plugin_\_icon`.
* Maintain a consistent look, feel, and behavior with other console pages.
* Follow [react-i18next](https://www.i18next.com/) localization guidelines when creating your plugin. You can use the `useTranslation` hook like the one in the following example:
```tsx
conster Header: React.FC ++= () => {++
  ++const { t } = useTranslation('plugin__console-demo-plugin');++
  ++return <h1>{t('Hello, World!')}</h1>;++
++};++
```

* Avoid selectors that could affect markup outside of your plugins components, such as element selectors. These are not APIs and are subject to change. Using them might break your plugin. Avoid selectors like element selectors that could affect markup outside of your plugins components.
* Provide valid JavaScript Multipurpose Internet Mail Extension (MIME) type using the `Content-Type` response header for all assets served by your plugin web server. Each plugin deployment should include a web server that hosts the generated assets of the given plugin.
* You must build your plugin with Webpack using Webpack version 5 and later.
* You should prefix CSS class names with your plugin name to avoid collisions. For example, `my-plugin_\_heading` and `my-plugin_\_icon`.
* You should maintain a consistent look, feel, and behavior with other console pages.
* You should avoid selectors that could affect markup outside of your plugin components, such as element selectors. These are not APIs and are subject to change.
* You must provide a valid JavaScript Multipurpose Internet Mail Extension (MIME) type using the `Content-Type` response header for all assets served by your plugin web server. Each plugin deployment should include a web server that hosts the generated assets of the given plugin.

#### PatternFly guidelines

When creating your plugin, follow these guidelines for using PatternFly:

* Use [PatternFly](https://www.patternfly.org/components/all-components/) components and PatternFly CSS variables. Core PatternFly components are available through the SDK. Using PatternFly components and variables help your plugin look consistent in future console versions.
** Use PatternFly 4.x if you are using {product-title} versions 4.14 and earlier.
** Use PatternFly 5.x if you are using {product-title} versions 4.15 through 4.18.
** Use PatternFly 6.x if you are using {product-title} versions 4.19 and later.

** Use Patternfly 5.x.
* Make your plugin accessible by following [PatternFly's accessibility fundamentals](https://www.patternfly.org/accessibility/accessibility-fundamentals/).
* Avoid using other CSS libraries such as Bootstrap or Tailwind. They might conflict with PatternFly and not match the rest of the console. Plugins should only include styles that are specific to their user interfaces to be evaluated on top of base PatternFly styles. Do not import styles directly from `@patternfly/react-styles/**/*.css` or `@patternfly/patternfly`. Instead, use components and CSS variables provided by the console SDK.
* The console application is responsible for loading base styles for all supported PatternFly versions.

## Getting started with dynamic plugins

To get started using the dynamic plugin, you must set up your environment to write a new {product-title} dynamic plugin. For an example of how to write a new plugin, see Adding a tab to the pods page.

## Deploy your plugin on a cluster

You can deploy the plugin to
an {product-title}
a {product-title}
cluster.

Additional resources

* Service CA certificates
* Securing service traffic using service serving certificate secrets
* Dynamic plugin API

#### Additional resources

* Understanding Helm

## Content Security Policy (CSP)

You can specify Content Security Policy (CSP) directives for your dynamic plugin using the `contentSecurityPolicy` field in the `ConsolePluginSpec` file. This field helps mitigate potential security risks by specifying which sources are allowed for fetching content like scripts, styles, images, and fonts. For dynamic plugins that require loading resources from external sources, defining custom CSP rules ensures secure integration into the {product-title} console.

> The console currently uses the `Content-Security-Policy-Report-Only` response header, so the browser will only warn about CSP violations in the web console and enforcement of CSP policies will be limited. CSP violations will be logged in the browser console, but the associated CSP directives will not be enforced. This feature is behind a `feature-gate`, so you will need to manually enable it.

> For more information, see Enabling feature sets using the web console.

#### Additional resources

* [Content Security Policy (CSP)](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)

## Dynamic plugin example

Before working through the example, verify that the plugin is working by following the steps in Dynamic plugin development

## Dynamic plugin reference

You can add extensions that allow you to customize your plugin. Those extensions are then loaded to the console at run-time.

Additional resources
* Understanding service serving certificates

## Installing the web terminal

You can install the web terminal by using the {web-terminal-op} listed in the {product-title} software catalog. When you install the {web-terminal-op}, the custom resource definitions (CRDs) that are required for the command line configuration, such as the `DevWorkspace` CRD, are automatically installed. The web console creates the required resources when you open the web terminal.

#### Prerequisites

* You are logged into the {product-title} web console.
* You have cluster administrator permissions.

#### Procedure

 In the *Administrator* perspective of the web console, navigate to *Ecosystem* -> *Software Catalog*.
 Use the *Filter by keyword* box to search for the {web-terminal-op} in the catalog, and then click the *Web Terminal* tile.
 Read the brief description about the Operator on the *Web Terminal*  page, and then click *Install*.
 On the *Install Operator* page, retain the default values for all fields.

** The *fast* option in the *Update Channel* menu enables installation of the latest release of the {web-terminal-op}.
** The *All namespaces on the cluster* option in the *Installation Mode* menu  enables the Operator to watch and be available to all namespaces in the cluster.
** The *openshift-operators* option in the *Installed Namespace* menu installs the Operator in the default `openshift-operators` namespace.
** The *Automatic* option in the *Approval Strategy* menu ensures that the future upgrades to the Operator are handled automatically by the Operator Lifecycle Manager.

 Click *Install*.
 In the *Installed Operators* page, click the *View Operator* to verify that the Operator is listed on the *Installed Operators* page.
> The {web-terminal-op} installs the DevWorkspace Operator as a dependency.

 After the Operator is installed, refresh your page to see the command-line terminal icon (image:odc-wto-icon.png[title="web terminal icon"]) in the masthead of the console.

> If you install the {web-terminal-op} manually by creating a `Subscription` resource, you must name the `Subscription` `web-terminal`. If you do not name it `web-terminal`, the terminal icon does not appear in the console masthead.

## Configuring the web terminal

You can configure timeout and image settings for the web terminal, either for your current session or for all user sessions if you are a cluster administrator.

## Using the web terminal

You can launch an embedded command-line terminal instance in the web console. This terminal instance is preinstalled with common CLI tools for interacting with the cluster, such as `oc`, `kubectl`,`odo`, `kn`, `tkn`, `helm`, and `subctl`. It also has the context of the project you are working on and automatically logs you in using your credentials.

## Troubleshooting the web terminal

#### Web terminal and network policies

The web terminal might fail to start if the cluster has network policies configured. To start a web terminal instance, the {web-terminal-op} must communicate with the web terminal's pod to verify it is running, and the {product-title} web console needs to send information to automatically log in to the cluster within the terminal. If either step fails, the web terminal fails to start and the terminal panel is in a loading state until a `context deadline exceeded error` occurs.

To avoid this issue, ensure that the network policies for namespaces that are used for terminals allow ingress from the `openshift-console` and `openshift-operators` namespaces.

The following samples show `NetworkPolicy` objects for allowing ingress from the `openshift-console` and `openshift-operators` namespaces.

Allowing ingress from the `openshift-console` namespace
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-openshift-console
spec:
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: openshift-console
  podSelector: {}
  policyTypes:
  - Ingress
```

Allowing ingress from the `openshift-operators` namespace
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-openshift-operators
spec:
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: openshift-operators
  podSelector: {}
  policyTypes:
  - Ingress
```

## Uninstalling the web terminal

Uninstalling the {web-terminal-op} does not remove any of the custom resource definitions (CRDs) or managed resources that are created when the Operator is installed. For security purposes, you must manually uninstall these components. By removing these components, you save cluster resources because terminals do not idle when the Operator is uninstalled.

Uninstalling the web terminal is a two-step process:

 Uninstall the {web-terminal-op} and related custom resources (CRs) that were added when you installed the Operator.
 Uninstall the DevWorkspace Operator and its related custom resources that were added as a dependency of the {web-terminal-op}.

## Disabling the web console in {product-title}

You can disable the {product-title} web console.

#### Prerequisites

* Deploy
an {product-title}
a {rosa-short}
a {rosa-classic-short}
cluster.

## Creating quick start tutorials in the web console

### About quick start tutorials

If you are creating quick start tutorials for the {product-title} web console, follow these guidelines to maintain a consistent user experience across all quick starts.

#### Additional resources

* [Best practices for writing quick starts](https://www.uxd-hub.com/entries/resource/best-practices-for-writing-quick-starts)
* [PatternFly's brand voice and tone guidelines](https://www.patternfly.org/ux-writing/brand-voice-and-tone)
* [PatternFly's UX writing style guide](https://www.patternfly.org/ux-writing/about)

## Optional capabilities and products in the web console

You can further customize the {product-title} web console by adding additional capabilities to your existing workflows and integrations through products.

Additional resources
* Understanding the software catalog
* Installing the web terminal
* [{ols} overview](https://docs.redhat.com/en/documentation/red_hat_openshift_lightspeed/1.0tp1/html/about/ols-about-openshift-lightspeed#ols-openshift-lightspeed-overview)
* [Installing {ols}](https://docs.redhat.com/en/documentation/red_hat_openshift_lightspeed/1.0tp1/html/install/ols-installing-lightspeed)
* [Working with {pipelines-title} in the web console](https://docs.openshift.com/pipelines/1.14/create/working-with-pipelines-web-console.html)
* [Pipeline execution statistics in the web console](https://docs.openshift.com/pipelines/1.14/create/working-with-pipelines-web-console.html#op-console-statistics_working-with-pipelines-web-console)
* [Installing the {ServerlessProductName} Operator from the web console](https://access.redhat.com/documentation/en-us/red_hat_openshift_serverless/1.31/html/installing_serverless/install-serverless-operator#serverless-install-web-console_install-serverless-operator)
* [Product Documentation for {rh-dev-hub}](https://access.redhat.com/documentation/en-us/red_hat_developer_hub/1.0)
