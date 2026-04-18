# 검증 및 문제 해결

## Validating an installation

You can check the status of an {product-title} cluster after an installation or validate boot artifacts before an installation by following the procedures in this document.

Additional resources

* See Querying Operator status after installation for more information about querying Operator status if your installation is still progressing.

* See Troubleshooting Operator issues for information about investigating issues with Operators.

* See Updating a cluster using the web console for more information on updating your cluster.

* See Understanding update channels and releases for an overview about update release channels.

Additional resources

* See Verifying node health for more details about reviewing node health and investigating node issues.

Additional resources

* See Using {red-hat-lightspeed} to identify issues with your cluster for more information about reviewing potential issues with your cluster.

Additional resources

* See [About {product-title} monitoring](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/about_monitoring/about-ocp-monitoring) for more information about the {product-title} monitoring stack.

Additional resources

* See [Managing alerts as an Administrator](https://docs.redhat.com/en/documentation/monitoring_stack_for_red_hat_openshift/4.20/html/managing_alerts/managing-alerts-as-an-administrator) for further details about alerting in {product-title}.

#### Next steps

* See Troubleshooting installations if you experience issues when installing your cluster.

* After installing {product-title}, you can further expand and customize your cluster.

## Troubleshooting installation issues

To assist in troubleshooting a failed {product-title} installation, you can gather logs from the bootstrap and control plane machines. You can also get debug information from the installation program. If you are unable to resolve the issue using the logs and debug information, see Determining where installation issues occur for component-specific troubleshooting.

> If your {product-title} installation fails and the debug output or logs contain network timeouts or other connectivity errors, review the guidelines for configuring your firewall. Gathering logs from your firewall and load balancer can help you diagnose network-related errors.

#### Prerequisites

* You attempted to install an {product-title} cluster and the installation failed.

Additional resources
* Installing an {product-title} cluster
