<!-- source: ocp_troubleshooting_os.md -->

---
category: Troubleshooting
source_url: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/support/troubleshooting#troubleshooting-operating-system-issues
---

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/support/troubleshooting#troubleshooting-operating-system-issues
---

# Chapter 7. Troubleshooting

## 7.1. Troubleshooting installationsCopy linkLink copied to clipboard!

### 7.1.1. Determining where installation issues occurCopy linkLink copied to clipboard!

When troubleshooting OpenShift Container Platform installation issues, you can monitor installation logs to determine at which stage issues occur. Then, retrieve diagnostic data relevant to that stage.

OpenShift Container Platform installation proceeds through the following stages:

- Ignition configuration files are created.
- The bootstrap machine boots and starts hosting the remote resources required for the control plane machines to boot.
- The control plane machines fetch the remote resources from the bootstrap machine and finish booting.
- The control plane machines use the bootstrap machine to form an etcd cluster.
- The bootstrap machine starts a temporary Kubernetes control plane using the new etcd cluster.
- The temporary control plane schedules the production control plane to the control plane machines.
- The temporary control plane shuts down and passes control to the production control plane.
- The bootstrap machine adds OpenShift Container Platform components into the production control plane.
- The installation program shuts down the bootstrap machine.
- The control plane sets up the worker nodes.
- The control plane installs additional services in the form of a set of Operators.
- The cluster downloads and configures remaining components needed for the day-to-day operation, including the creation of worker machines in supported environments.

### 7.1.2. User-provisioned infrastructure installation considerationsCopy linkLink copied to clipboard!

The default installation method uses installer-provisioned infrastructure. With installer-provisioned infrastructure clusters, OpenShift Container Platform manages all aspects of the cluster, including the operating system itself. If possible, use this feature to avoid having to provision and maintain the cluster infrastructure.

You can alternatively install OpenShift Container Platform 4.17 on infrastructure that you provide. If you use this installation method, follow user-provisioned infrastructure installation documentation carefully. Additionally, review the following considerations before the installation:

- Check theRed Hat Enterprise Linux (RHEL) Ecosystemto determine the level of Red Hat Enterprise Linux CoreOS (RHCOS) support provided for your chosen server hardware or virtualization technology.
- Many virtualization and cloud environments require agents to be installed on guest operating systems. Ensure that these agents are installed as a containerized workload deployed through a daemon set.
- Install cloud provider integration if you want to enable features such as dynamic storage, on-demand service routing, node hostname to Kubernetes hostname resolution, and cluster autoscaling.It is not possible to enable cloud provider integration in OpenShift Container Platform environments that mix resources from different cloud providers, or that span multiple physical or virtual platforms. The node life cycle controller will not allow nodes that are external to the existing provider to be added to a cluster, and it is not possible to specify more than one cloud provider integration.

Install cloud provider integration if you want to enable features such as dynamic storage, on-demand service routing, node hostname to Kubernetes hostname resolution, and cluster autoscaling.

It is not possible to enable cloud provider integration in OpenShift Container Platform environments that mix resources from different cloud providers, or that span multiple physical or virtual platforms. The node life cycle controller will not allow nodes that are external to the existing provider to be added to a cluster, and it is not possible to specify more than one cloud provider integration.

- A provider-specific Machine API implementation is required if you want to use machine sets or autoscaling to automatically provision OpenShift Container Platform cluster nodes.
- Check whether your chosen cloud provider offers a method to inject Ignition configuration files into hosts as part of their initial deployment. If they do not, you will need to host Ignition configuration files by using an HTTP server. The steps taken to troubleshoot Ignition configuration file issues will differ depending on which of these two methods is deployed.
- Storage needs to be manually provisioned if you want to leverage optional framework components such as the embedded container registry, Elasticsearch, or Prometheus. Default storage classes are not defined in user-provisioned infrastructure installations unless explicitly configured.
- A load balancer is required to distribute API requests across all control plane nodes in highly available OpenShift Container Platform environments. You can use any TCP-based load balancing solution that meets OpenShift Container Platform DNS routing and port requirements.

### 7.1.3. Checking a load balancer configuration before OpenShift Container Platform installationCopy linkLink copied to clipboard!

Check your load balancer configuration prior to starting an OpenShift Container Platform installation.

Prerequisites

- You have configured an external load balancer of your choosing, in preparation for an OpenShift Container Platform installation. The following example is based on a Red Hat Enterprise Linux (RHEL) host using HAProxy to provide load balancing services to a cluster.
- You have configured DNS in preparation for an OpenShift Container Platform installation.
- You have SSH access to your load balancer.

Procedure

- Check that thehaproxysystemd service is active:ssh <user_name>@<load_balancer> systemctl status haproxy$ssh<user_name>@<load_balancer>systemctl status haproxyCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check that thehaproxysystemd service is active:

- Verify that the load balancer is listening on the required ports. The following example references ports80,443,6443, and22623.For HAProxy instances running on Red Hat Enterprise Linux (RHEL) 6, verify port status by using thenetstatcommand:ssh <user_name>@<load_balancer> netstat -nltupe | grep -E ':80|:443|:6443|:22623'$ssh<user_name>@<load_balancer>netstat-nltupe|grep-E':80|:443|:6443|:22623'Copy to ClipboardCopied!Toggle word wrapToggle overflowFor HAProxy instances running on Red Hat Enterprise Linux (RHEL) 7 or 8, verify port status by using thesscommand:ssh <user_name>@<load_balancer> ss -nltupe | grep -E ':80|:443|:6443|:22623'$ssh<user_name>@<load_balancer>ss-nltupe|grep-E':80|:443|:6443|:22623'Copy to ClipboardCopied!Toggle word wrapToggle overflowRed Hat recommends thesscommand instead ofnetstatin Red Hat Enterprise Linux (RHEL) 7 or later.ssis provided by the iproute package. For more information on thesscommand, see theRed Hat Enterprise Linux (RHEL) 7 Performance Tuning Guide.

Verify that the load balancer is listening on the required ports. The following example references ports80,443,6443, and22623.

- For HAProxy instances running on Red Hat Enterprise Linux (RHEL) 6, verify port status by using thenetstatcommand:ssh <user_name>@<load_balancer> netstat -nltupe | grep -E ':80|:443|:6443|:22623'$ssh<user_name>@<load_balancer>netstat-nltupe|grep-E':80|:443|:6443|:22623'Copy to ClipboardCopied!Toggle word wrapToggle overflow

For HAProxy instances running on Red Hat Enterprise Linux (RHEL) 6, verify port status by using thenetstatcommand:

- For HAProxy instances running on Red Hat Enterprise Linux (RHEL) 7 or 8, verify port status by using thesscommand:ssh <user_name>@<load_balancer> ss -nltupe | grep -E ':80|:443|:6443|:22623'$ssh<user_name>@<load_balancer>ss-nltupe|grep-E':80|:443|:6443|:22623'Copy to ClipboardCopied!Toggle word wrapToggle overflowRed Hat recommends thesscommand instead ofnetstatin Red Hat Enterprise Linux (RHEL) 7 or later.ssis provided by the iproute package. For more information on thesscommand, see theRed Hat Enterprise Linux (RHEL) 7 Performance Tuning Guide.

For HAProxy instances running on Red Hat Enterprise Linux (RHEL) 7 or 8, verify port status by using thesscommand:

Red Hat recommends thesscommand instead ofnetstatin Red Hat Enterprise Linux (RHEL) 7 or later.ssis provided by the iproute package. For more information on thesscommand, see theRed Hat Enterprise Linux (RHEL) 7 Performance Tuning Guide.

- Check that the wildcard DNS record resolves to the load balancer:dig <wildcard_fqdn> @<dns_server>$dig<wildcard_fqdn>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check that the wildcard DNS record resolves to the load balancer:

### 7.1.4. Specifying OpenShift Container Platform installer log levelsCopy linkLink copied to clipboard!

By default, the OpenShift Container Platform installer log level is set toinfo. If more detailed logging is required when diagnosing a failed OpenShift Container Platform installation, you can increase theopenshift-installlog level todebugwhen starting the installation again.

Prerequisites

- You have access to the installation host.

Procedure

- Set the installation log level todebugwhen initiating the installation:./openshift-install --dir <installation_directory> wait-for bootstrap-complete --log-level debug$./openshift-install--dir<installation_directory>wait-for bootstrap-complete --log-level debug1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Possible log levels includeinfo,warn,error,anddebug.

Set the installation log level todebugwhen initiating the installation:

**1**
  Possible log levels includeinfo,warn,error,anddebug.

### 7.1.5. Troubleshooting openshift-install command issuesCopy linkLink copied to clipboard!

If you experience issues running theopenshift-installcommand, check the following:

- The installation has been initiated within 24 hours of Ignition configuration file creation. The Ignition files are created when the following command is run:./openshift-install create ignition-configs --dir=./install_dir$./openshift-install create ignition-configs--dir=./install_dirCopy to ClipboardCopied!Toggle word wrapToggle overflow

The installation has been initiated within 24 hours of Ignition configuration file creation. The Ignition files are created when the following command is run:

- Theinstall-config.yamlfile is in the same directory as the installer. If an alternative installation path is declared by using the./openshift-install --diroption, verify that theinstall-config.yamlfile exists within that directory.

### 7.1.6. Monitoring installation progressCopy linkLink copied to clipboard!

You can monitor high-level installation, bootstrap, and control plane logs as an OpenShift Container Platform installation progresses. This provides greater visibility into how an installation progresses and helps identify the stage at which an installation failure occurs.

Prerequisites

- You have access to the cluster as a user with thecluster-admincluster role.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have the fully qualified domain names of the bootstrap and control plane nodes.The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

You have the fully qualified domain names of the bootstrap and control plane nodes.

The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

Procedure

- Watch the installation log as the installation progresses:tail -f ~/<installation_directory>/.openshift_install.log$tail-f~/<installation_directory>/.openshift_install.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Watch the installation log as the installation progresses:

- Monitor thebootkube.servicejournald unit log on the bootstrap node, after it has booted. This provides visibility into the bootstrapping of the first control plane. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> journalctl -b -f -u bootkube.service$sshcore@<bootstrap_fqdn>journalctl-b-f-ubootkube.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowThebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

Monitor thebootkube.servicejournald unit log on the bootstrap node, after it has booted. This provides visibility into the bootstrapping of the first control plane. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

Thebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

- Monitorkubelet.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node agent activity.Monitor the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Monitorkubelet.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node agent activity.

- Monitor the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Monitor the logs usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:

- Monitorcrio.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node CRI-O container runtime activity.Monitor the logs usingoc:oc adm node-logs --role=master -u crio$oc adm node-logs--role=master-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@master-N.cluster_name.sub_domain.domain journalctl -b -f -u crio.service$sshcore@master-N.cluster_name.sub_domain.domain journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Monitorcrio.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node CRI-O container runtime activity.

- Monitor the logs usingoc:oc adm node-logs --role=master -u crio$oc adm node-logs--role=master-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Monitor the logs usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@master-N.cluster_name.sub_domain.domain journalctl -b -f -u crio.service$sshcore@master-N.cluster_name.sub_domain.domain journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:

### 7.1.7. Gathering bootstrap node diagnostic dataCopy linkLink copied to clipboard!

When experiencing bootstrap-related issues, you can gatherbootkube.servicejournaldunit logs and container logs from the bootstrap node.

Prerequisites

- You have SSH access to your bootstrap node.
- You have the fully qualified domain name of the bootstrap node.
- If you are hosting Ignition configuration files by using an HTTP server, you must have the HTTP server’s fully qualified domain name and the port number. You must also have SSH access to the HTTP host.

Procedure

- If you have access to the bootstrap node’s console, monitor the console until the node reaches the login prompt.
- Verify the Ignition file configuration.If you are hosting Ignition configuration files by using an HTTP server.Verify the bootstrap node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/bootstrap.ign$curl-Ihttp://<http_server_fqdn>:<port>/bootstrap.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the bootstrap node, query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files, enter the following command:grep -is 'bootstrap.ign' /var/log/httpd/access_log$grep-is'bootstrap.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the bootstrap Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that the Ignition files exist and that they have the appropriate file and web server permissions on the serving host directly.If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the bootstrap node’s console to determine if the mechanism is injecting the bootstrap node Ignition file correctly.

Verify the Ignition file configuration.

- If you are hosting Ignition configuration files by using an HTTP server.Verify the bootstrap node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/bootstrap.ign$curl-Ihttp://<http_server_fqdn>:<port>/bootstrap.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the bootstrap node, query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files, enter the following command:grep -is 'bootstrap.ign' /var/log/httpd/access_log$grep-is'bootstrap.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the bootstrap Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that the Ignition files exist and that they have the appropriate file and web server permissions on the serving host directly.

If you are hosting Ignition configuration files by using an HTTP server.

- Verify the bootstrap node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/bootstrap.ign$curl-Ihttp://<http_server_fqdn>:<port>/bootstrap.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.

Verify the bootstrap node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:

**1**
  The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.
- To verify that the Ignition file was received by the bootstrap node, query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files, enter the following command:grep -is 'bootstrap.ign' /var/log/httpd/access_log$grep-is'bootstrap.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the bootstrap Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

To verify that the Ignition file was received by the bootstrap node, query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files, enter the following command:

If the bootstrap Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

- If the Ignition file was not received, check that the Ignition files exist and that they have the appropriate file and web server permissions on the serving host directly.
- If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the bootstrap node’s console to determine if the mechanism is injecting the bootstrap node Ignition file correctly.

If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.

- Review the bootstrap node’s console to determine if the mechanism is injecting the bootstrap node Ignition file correctly.
- Verify the availability of the bootstrap node’s assigned storage device.
- Verify that the bootstrap node has been assigned an IP address from the DHCP server.
- Collectbootkube.servicejournald unit logs from the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> journalctl -b -f -u bootkube.service$sshcore@<bootstrap_fqdn>journalctl-b-f-ubootkube.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowThebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

Collectbootkube.servicejournald unit logs from the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

Thebootkube.servicelog on the bootstrap node outputs etcdconnection refusederrors, indicating that the bootstrap server is unable to connect to etcd on control plane nodes. After etcd has started on each control plane node and the nodes have joined the cluster, the errors should stop.

- Collect logs from the bootstrap node containers.Collect the logs usingpodmanon the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> 'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'$sshcore@<bootstrap_fqdn>'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Collect logs from the bootstrap node containers.

- Collect the logs usingpodmanon the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> 'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'$sshcore@<bootstrap_fqdn>'for pod in $(sudo podman ps -a -q); do sudo podman logs $pod; done'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Collect the logs usingpodmanon the bootstrap node. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

- If the bootstrap process fails, verify the following.You can resolveapi.<cluster_name>.<base_domain>from the installation host.The load balancer proxies port 6443 connections to bootstrap and control plane nodes. Ensure that the proxy configuration meets OpenShift Container Platform installation requirements.

If the bootstrap process fails, verify the following.

- You can resolveapi.<cluster_name>.<base_domain>from the installation host.
- The load balancer proxies port 6443 connections to bootstrap and control plane nodes. Ensure that the proxy configuration meets OpenShift Container Platform installation requirements.

### 7.1.8. Investigating control plane node installation issuesCopy linkLink copied to clipboard!

If you experience control plane node installation issues, determine the control plane node OpenShift Container Platform software defined network (SDN), and network Operator status. Collectkubelet.service,crio.servicejournald unit logs, and control plane node container logs for visibility into control plane node agent, CRI-O container runtime, and pod activity.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have the fully qualified domain names of the bootstrap and control plane nodes.
- If you are hosting Ignition configuration files by using an HTTP server, you must have the HTTP server’s fully qualified domain name and the port number. You must also have SSH access to the HTTP host.The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

If you are hosting Ignition configuration files by using an HTTP server, you must have the HTTP server’s fully qualified domain name and the port number. You must also have SSH access to the HTTP host.

The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

Procedure

- If you have access to the console for the control plane node, monitor the console until the node reaches the login prompt. During the installation, Ignition log messages are output to the console.
- Verify Ignition file configuration.If you are hosting Ignition configuration files by using an HTTP server.Verify the control plane node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/master.ign$curl-Ihttp://<http_server_fqdn>:<port>/master.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the control plane node query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'master.ign' /var/log/httpd/access_log$grep-is'master.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the master Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the console for the control plane node to determine if the mechanism is injecting the control plane node Ignition file correctly.

Verify Ignition file configuration.

- If you are hosting Ignition configuration files by using an HTTP server.Verify the control plane node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/master.ign$curl-Ihttp://<http_server_fqdn>:<port>/master.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the control plane node query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'master.ign' /var/log/httpd/access_log$grep-is'master.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the master Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.

If you are hosting Ignition configuration files by using an HTTP server.

- Verify the control plane node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/master.ign$curl-Ihttp://<http_server_fqdn>:<port>/master.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.

Verify the control plane node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:

**1**
  The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.
- To verify that the Ignition file was received by the control plane node query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'master.ign' /var/log/httpd/access_log$grep-is'master.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the master Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

To verify that the Ignition file was received by the control plane node query the HTTP server logs on the serving host. For example, if you are using an Apache web server to serve Ignition files:

If the master Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

- If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.
- If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the console for the control plane node to determine if the mechanism is injecting the control plane node Ignition file correctly.

If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.

- Review the console for the control plane node to determine if the mechanism is injecting the control plane node Ignition file correctly.
- Check the availability of the storage device assigned to the control plane node.
- Verify that the control plane node has been assigned an IP address from the DHCP server.
- Determine control plane node status.Query control plane node status:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowIf one of the control plane nodes does not reach aReadystatus, retrieve a detailed node description:oc describe node <master_node>$oc describenode<master_node>Copy to ClipboardCopied!Toggle word wrapToggle overflowIt is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node:

Determine control plane node status.

- Query control plane node status:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Query control plane node status:

- If one of the control plane nodes does not reach aReadystatus, retrieve a detailed node description:oc describe node <master_node>$oc describenode<master_node>Copy to ClipboardCopied!Toggle word wrapToggle overflowIt is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node:

If one of the control plane nodes does not reach aReadystatus, retrieve a detailed node description:

It is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node:

- Determine OVN-Kubernetes status.Reviewovnkube-nodedaemon set status, in theopenshift-ovn-kubernetesnamespace:oc get daemonsets -n openshift-ovn-kubernetes$oc get daemonsets-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflowIf those resources are listed asNot found, review pods in theopenshift-ovn-kubernetesnamespace:oc get pods -n openshift-ovn-kubernetes$oc get pods-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflowReview logs relating to failed OpenShift Container Platform OVN-Kubernetes pods in theopenshift-ovn-kubernetesnamespace:oc logs <ovn-k_pod> -n openshift-ovn-kubernetes$oc logs<ovn-k_pod>-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Determine OVN-Kubernetes status.

- Reviewovnkube-nodedaemon set status, in theopenshift-ovn-kubernetesnamespace:oc get daemonsets -n openshift-ovn-kubernetes$oc get daemonsets-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Reviewovnkube-nodedaemon set status, in theopenshift-ovn-kubernetesnamespace:

- If those resources are listed asNot found, review pods in theopenshift-ovn-kubernetesnamespace:oc get pods -n openshift-ovn-kubernetes$oc get pods-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflow

If those resources are listed asNot found, review pods in theopenshift-ovn-kubernetesnamespace:

- Review logs relating to failed OpenShift Container Platform OVN-Kubernetes pods in theopenshift-ovn-kubernetesnamespace:oc logs <ovn-k_pod> -n openshift-ovn-kubernetes$oc logs<ovn-k_pod>-nopenshift-ovn-kubernetesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review logs relating to failed OpenShift Container Platform OVN-Kubernetes pods in theopenshift-ovn-kubernetesnamespace:

- Determine cluster network configuration status.Review whether the cluster’s network configuration exists:oc get network.config.openshift.io cluster -o yaml$oc get network.config.openshift.io cluster-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the installer failed to create the network configuration, generate the Kubernetes manifests again and review message output:./openshift-install create manifests$./openshift-install create manifestsCopy to ClipboardCopied!Toggle word wrapToggle overflowReview the pod status in theopenshift-network-operatornamespace to determine whether the Cluster Network Operator (CNO) is running:oc get pods -n openshift-network-operator$oc get pods-nopenshift-network-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflowGather network Operator pod logs from theopenshift-network-operatornamespace:oc logs pod/<network_operator_pod_name> -n openshift-network-operator$oc logs pod/<network_operator_pod_name>-nopenshift-network-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Determine cluster network configuration status.

- Review whether the cluster’s network configuration exists:oc get network.config.openshift.io cluster -o yaml$oc get network.config.openshift.io cluster-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review whether the cluster’s network configuration exists:

- If the installer failed to create the network configuration, generate the Kubernetes manifests again and review message output:./openshift-install create manifests$./openshift-install create manifestsCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the installer failed to create the network configuration, generate the Kubernetes manifests again and review message output:

- Review the pod status in theopenshift-network-operatornamespace to determine whether the Cluster Network Operator (CNO) is running:oc get pods -n openshift-network-operator$oc get pods-nopenshift-network-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review the pod status in theopenshift-network-operatornamespace to determine whether the Cluster Network Operator (CNO) is running:

- Gather network Operator pod logs from theopenshift-network-operatornamespace:oc logs pod/<network_operator_pod_name> -n openshift-network-operator$oc logs pod/<network_operator_pod_name>-nopenshift-network-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Gather network Operator pod logs from theopenshift-network-operatornamespace:

- Monitorkubelet.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node agent activity.Retrieve the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Monitorkubelet.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node agent activity.

- Retrieve the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the logs usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

- Retrievecrio.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node CRI-O container runtime activity.Retrieve the logs usingoc:oc adm node-logs --role=master -u crio$oc adm node-logs--role=master-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u crio.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrievecrio.servicejournald unit logs on control plane nodes, after they have booted. This provides visibility into control plane node CRI-O container runtime activity.

- Retrieve the logs usingoc:oc adm node-logs --role=master -u crio$oc adm node-logs--role=master-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the logs usingoc:

- If the API is not functional, review the logs using SSH instead:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u crio.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs using SSH instead:

- Collect logs from specific subdirectories under/var/log/on control plane nodes.Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflowInspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Collect logs from specific subdirectories under/var/log/on control plane nodes.

- Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:

- Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:

- If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:

- Review control plane node container logs using SSH.List the containers:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps -a$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps-aCopy to ClipboardCopied!Toggle word wrapToggle overflowRetrieve a container’s logs usingcrictl:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review control plane node container logs using SSH.

- List the containers:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps -a$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps-aCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the containers:

- Retrieve a container’s logs usingcrictl:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a container’s logs usingcrictl:

- If you experience control plane node configuration issues, verify that the MCO, MCO endpoint, and DNS record are functioning. The Machine Config Operator (MCO) manages operating system configuration during the installation procedure. Also verify system clock accuracy and certificate validity.Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:curl https://api-int.<cluster_name>:22623/config/master$curlhttps://api-int.<cluster_name>:22623/config/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the endpoint is unresponsive, verify load balancer configuration. Ensure that the endpoint is configured to run on port 22623.Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowRun a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowVerify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> curl https://api-int.<cluster_name>:22623/config/master$sshcore@<bootstrap_fqdn>curlhttps://api-int.<cluster_name>:22623/config/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowSystem clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:ssh core@<node>.<cluster_name>.<base_domain> chronyc tracking$sshcore@<node>.<cluster_name>.<base_domain>chronyc trackingCopy to ClipboardCopied!Toggle word wrapToggle overflowReview certificate validity:openssl s_client -connect api-int.<cluster_name>:22623 | openssl x509 -noout -text$openssl s_client-connectapi-int.<cluster_name>:22623|openssl x509-noout-textCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you experience control plane node configuration issues, verify that the MCO, MCO endpoint, and DNS record are functioning. The Machine Config Operator (MCO) manages operating system configuration during the installation procedure. Also verify system clock accuracy and certificate validity.

- Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:curl https://api-int.<cluster_name>:22623/config/master$curlhttps://api-int.<cluster_name>:22623/config/masterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:

- If the endpoint is unresponsive, verify load balancer configuration. Ensure that the endpoint is configured to run on port 22623.
- Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowRun a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.

- Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run a DNS lookup for the defined MCO endpoint name:

- Run a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run a reverse lookup to the assigned MCO IP address on the load balancer:

- Verify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> curl https://api-int.<cluster_name>:22623/config/master$sshcore@<bootstrap_fqdn>curlhttps://api-int.<cluster_name>:22623/config/masterCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

- System clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:ssh core@<node>.<cluster_name>.<base_domain> chronyc tracking$sshcore@<node>.<cluster_name>.<base_domain>chronyc trackingCopy to ClipboardCopied!Toggle word wrapToggle overflow

System clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:

- Review certificate validity:openssl s_client -connect api-int.<cluster_name>:22623 | openssl x509 -noout -text$openssl s_client-connectapi-int.<cluster_name>:22623|openssl x509-noout-textCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review certificate validity:

### 7.1.9. Investigating etcd installation issuesCopy linkLink copied to clipboard!

If you experience etcd issues during installation, you can check etcd pod status and collect etcd pod logs. You can also verify etcd DNS records and check DNS availability on control plane nodes.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have the fully qualified domain names of the control plane nodes.

Procedure

- Check the status of etcd pods.Review the status of pods in theopenshift-etcdnamespace:oc get pods -n openshift-etcd$oc get pods-nopenshift-etcdCopy to ClipboardCopied!Toggle word wrapToggle overflowReview the status of pods in theopenshift-etcd-operatornamespace:oc get pods -n openshift-etcd-operator$oc get pods-nopenshift-etcd-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check the status of etcd pods.

- Review the status of pods in theopenshift-etcdnamespace:oc get pods -n openshift-etcd$oc get pods-nopenshift-etcdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review the status of pods in theopenshift-etcdnamespace:

- Review the status of pods in theopenshift-etcd-operatornamespace:oc get pods -n openshift-etcd-operator$oc get pods-nopenshift-etcd-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review the status of pods in theopenshift-etcd-operatornamespace:

- If any of the pods listed by the previous commands are not showing aRunningor aCompletedstatus, gather diagnostic information for the pod.Review events for the pod:oc describe pod/<pod_name> -n <namespace>$oc describe pod/<pod_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflowInspect the pod’s logs:oc logs pod/<pod_name> -n <namespace>$oc logs pod/<pod_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the pod has more than one container, the preceding command will create an error, and the container names will be provided in the error message. Inspect logs for each container:oc logs pod/<pod_name> -c <container_name> -n <namespace>$oc logs pod/<pod_name>-c<container_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

If any of the pods listed by the previous commands are not showing aRunningor aCompletedstatus, gather diagnostic information for the pod.

- Review events for the pod:oc describe pod/<pod_name> -n <namespace>$oc describe pod/<pod_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review events for the pod:

- Inspect the pod’s logs:oc logs pod/<pod_name> -n <namespace>$oc logs pod/<pod_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect the pod’s logs:

- If the pod has more than one container, the preceding command will create an error, and the container names will be provided in the error message. Inspect logs for each container:oc logs pod/<pod_name> -c <container_name> -n <namespace>$oc logs pod/<pod_name>-c<container_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

If the pod has more than one container, the preceding command will create an error, and the container names will be provided in the error message. Inspect logs for each container:

- If the API is not functional, review etcd pod and container logs on each control plane node by using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values.List etcd pods on each control plane node:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl pods --name=etcd-$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl pods--name=etcd-Copy to ClipboardCopied!Toggle word wrapToggle overflowFor any pods not showingReadystatus, inspect pod status in detail. Replace<pod_id>with the pod’s ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspectp <pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspectp<pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowList containers related to a pod:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps | grep '<pod_id>'$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps|grep'<pod_id>'Copy to ClipboardCopied!Toggle word wrapToggle overflowFor any containers not showingReadystatus, inspect container status in detail. Replace<container_id>with container IDs listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspect <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspect<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowReview the logs for any containers not showing aReadystatus. Replace<container_id>with the container IDs listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review etcd pod and container logs on each control plane node by using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values.

- List etcd pods on each control plane node:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl pods --name=etcd-$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl pods--name=etcd-Copy to ClipboardCopied!Toggle word wrapToggle overflow

List etcd pods on each control plane node:

- For any pods not showingReadystatus, inspect pod status in detail. Replace<pod_id>with the pod’s ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspectp <pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspectp<pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

For any pods not showingReadystatus, inspect pod status in detail. Replace<pod_id>with the pod’s ID listed in the output of the preceding command:

- List containers related to a pod:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps | grep '<pod_id>'$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps|grep'<pod_id>'Copy to ClipboardCopied!Toggle word wrapToggle overflow

List containers related to a pod:

- For any containers not showingReadystatus, inspect container status in detail. Replace<container_id>with container IDs listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspect <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspect<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

For any containers not showingReadystatus, inspect container status in detail. Replace<container_id>with container IDs listed in the output of the preceding command:

- Review the logs for any containers not showing aReadystatus. Replace<container_id>with the container IDs listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Review the logs for any containers not showing aReadystatus. Replace<container_id>with the container IDs listed in the output of the preceding command:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

- Validate primary and secondary DNS server connectivity from control plane nodes.

### 7.1.10. Investigating control plane node kubelet and API server issuesCopy linkLink copied to clipboard!

To investigate control plane node kubelet and API server issues during installation, check DNS, DHCP, and load balancer functionality. Also, verify that certificates have not expired.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have the fully qualified domain names of the control plane nodes.

Procedure

- Verify that the API server’s DNS record directs the kubelet on control plane nodes tohttps://api-int.<cluster_name>.<base_domain>:6443. Ensure that the record references the load balancer.
- Ensure that the load balancer’s port 6443 definition references each control plane node.
- Check that unique control plane node hostnames have been provided by DHCP.
- Inspect thekubelet.servicejournald unit logs on each control plane node.Retrieve the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Inspect thekubelet.servicejournald unit logs on each control plane node.

- Retrieve the logs usingoc:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the logs usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

- Check for certificate expiration messages in the control plane node kubelet logs.Retrieve the log usingoc:oc adm node-logs --role=master -u kubelet | grep -is 'x509: certificate has expired'$oc adm node-logs--role=master-ukubelet|grep-is'x509: certificate has expired'Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service  | grep -is 'x509: certificate has expired'$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.service|grep-is'x509: certificate has expired'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check for certificate expiration messages in the control plane node kubelet logs.

- Retrieve the log usingoc:oc adm node-logs --role=master -u kubelet | grep -is 'x509: certificate has expired'$oc adm node-logs--role=master-ukubelet|grep-is'x509: certificate has expired'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the log usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<master-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service  | grep -is 'x509: certificate has expired'$sshcore@<master-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.service|grep-is'x509: certificate has expired'Copy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values:

### 7.1.11. Investigating worker node installation issuesCopy linkLink copied to clipboard!

If you experience worker node installation issues, you can review the worker node status. Collectkubelet.service,crio.servicejournald unit logs and the worker node container logs for visibility into the worker node agent, CRI-O container runtime and pod activity. Additionally, you can check the Ignition file and Machine API Operator functionality. If worker node postinstallation configuration fails, check Machine Config Operator (MCO) and DNS functionality. You can also verify system clock synchronization between the bootstrap, master, and worker nodes, and validate certificates.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have SSH access to your hosts.
- You have the fully qualified domain names of the bootstrap and worker nodes.
- If you are hosting Ignition configuration files by using an HTTP server, you must have the HTTP server’s fully qualified domain name and the port number. You must also have SSH access to the HTTP host.The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

If you are hosting Ignition configuration files by using an HTTP server, you must have the HTTP server’s fully qualified domain name and the port number. You must also have SSH access to the HTTP host.

The initialkubeadminpassword can be found in<install_directory>/auth/kubeadmin-passwordon the installation host.

Procedure

- If you have access to the worker node’s console, monitor the console until the node reaches the login prompt. During the installation, Ignition log messages are output to the console.
- Verify Ignition file configuration.If you are hosting Ignition configuration files by using an HTTP server.Verify the worker node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/worker.ign$curl-Ihttp://<http_server_fqdn>:<port>/worker.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the worker node, query the HTTP server logs on the HTTP host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'worker.ign' /var/log/httpd/access_log$grep-is'worker.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the worker Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the worker node’s console to determine if the mechanism is injecting the worker node Ignition file correctly.

Verify Ignition file configuration.

- If you are hosting Ignition configuration files by using an HTTP server.Verify the worker node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/worker.ign$curl-Ihttp://<http_server_fqdn>:<port>/worker.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.To verify that the Ignition file was received by the worker node, query the HTTP server logs on the HTTP host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'worker.ign' /var/log/httpd/access_log$grep-is'worker.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the worker Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.

If you are hosting Ignition configuration files by using an HTTP server.

- Verify the worker node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:curl -I http://<http_server_fqdn>:<port>/worker.ign$curl-Ihttp://<http_server_fqdn>:<port>/worker.ign1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.

Verify the worker node Ignition file URL. Replace<http_server_fqdn>with HTTP server’s fully qualified domain name:

**1**
  The-Ioption returns the header only. If the Ignition file is available on the specified URL, the command returns200 OKstatus. If it is not available, the command returns404 file not found.
- To verify that the Ignition file was received by the worker node, query the HTTP server logs on the HTTP host. For example, if you are using an Apache web server to serve Ignition files:grep -is 'worker.ign' /var/log/httpd/access_log$grep-is'worker.ign'/var/log/httpd/access_logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the worker Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

To verify that the Ignition file was received by the worker node, query the HTTP server logs on the HTTP host. For example, if you are using an Apache web server to serve Ignition files:

If the worker Ignition file is received, the associatedHTTP GETlog message will include a200 OKsuccess status, indicating that the request succeeded.

- If the Ignition file was not received, check that it exists on the serving host directly. Ensure that the appropriate file and web server permissions are in place.
- If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.Review the worker node’s console to determine if the mechanism is injecting the worker node Ignition file correctly.

If you are using a cloud provider mechanism to inject Ignition configuration files into hosts as part of their initial deployment.

- Review the worker node’s console to determine if the mechanism is injecting the worker node Ignition file correctly.
- Check the availability of the worker node’s assigned storage device.
- Verify that the worker node has been assigned an IP address from the DHCP server.
- Determine worker node status.Query node status:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowRetrieve a detailed node description for any worker nodes not showing aReadystatus:oc describe node <worker_node>$oc describenode<worker_node>Copy to ClipboardCopied!Toggle word wrapToggle overflowIt is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node.

Determine worker node status.

- Query node status:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Query node status:

- Retrieve a detailed node description for any worker nodes not showing aReadystatus:oc describe node <worker_node>$oc describenode<worker_node>Copy to ClipboardCopied!Toggle word wrapToggle overflowIt is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node.

Retrieve a detailed node description for any worker nodes not showing aReadystatus:

It is not possible to runoccommands if an installation issue prevents the OpenShift Container Platform API from running or if the kubelet is not running yet on each node.

- Unlike control plane nodes, worker nodes are deployed and scaled using the Machine API Operator. Check the status of the Machine API Operator.Review Machine API Operator pod status:oc get pods -n openshift-machine-api$oc get pods-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the Machine API Operator pod does not have aReadystatus, detail the pod’s events:oc describe pod/<machine_api_operator_pod_name> -n openshift-machine-api$oc describe pod/<machine_api_operator_pod_name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflowInspectmachine-api-operatorcontainer logs. The container runs within themachine-api-operatorpod:oc logs pod/<machine_api_operator_pod_name> -n openshift-machine-api -c machine-api-operator$oc logs pod/<machine_api_operator_pod_name>-nopenshift-machine-api-cmachine-api-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflowAlso inspectkube-rbac-proxycontainer logs. The container also runs within themachine-api-operatorpod:oc logs pod/<machine_api_operator_pod_name> -n openshift-machine-api -c kube-rbac-proxy$oc logs pod/<machine_api_operator_pod_name>-nopenshift-machine-api-ckube-rbac-proxyCopy to ClipboardCopied!Toggle word wrapToggle overflow

Unlike control plane nodes, worker nodes are deployed and scaled using the Machine API Operator. Check the status of the Machine API Operator.

- Review Machine API Operator pod status:oc get pods -n openshift-machine-api$oc get pods-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review Machine API Operator pod status:

- If the Machine API Operator pod does not have aReadystatus, detail the pod’s events:oc describe pod/<machine_api_operator_pod_name> -n openshift-machine-api$oc describe pod/<machine_api_operator_pod_name>-nopenshift-machine-apiCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the Machine API Operator pod does not have aReadystatus, detail the pod’s events:

- Inspectmachine-api-operatorcontainer logs. The container runs within themachine-api-operatorpod:oc logs pod/<machine_api_operator_pod_name> -n openshift-machine-api -c machine-api-operator$oc logs pod/<machine_api_operator_pod_name>-nopenshift-machine-api-cmachine-api-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspectmachine-api-operatorcontainer logs. The container runs within themachine-api-operatorpod:

- Also inspectkube-rbac-proxycontainer logs. The container also runs within themachine-api-operatorpod:oc logs pod/<machine_api_operator_pod_name> -n openshift-machine-api -c kube-rbac-proxy$oc logs pod/<machine_api_operator_pod_name>-nopenshift-machine-api-ckube-rbac-proxyCopy to ClipboardCopied!Toggle word wrapToggle overflow

Also inspectkube-rbac-proxycontainer logs. The container also runs within themachine-api-operatorpod:

- Monitorkubelet.servicejournald unit logs on worker nodes, after they have booted. This provides visibility into worker node agent activity.Retrieve the logs usingoc:oc adm node-logs --role=worker -u kubelet$oc adm node-logs--role=worker-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead. Replace<worker-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<worker-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<worker-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Monitorkubelet.servicejournald unit logs on worker nodes, after they have booted. This provides visibility into worker node agent activity.

- Retrieve the logs usingoc:oc adm node-logs --role=worker -u kubelet$oc adm node-logs--role=worker-ukubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the logs usingoc:

- If the API is not functional, review the logs using SSH instead. Replace<worker-node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<worker-node>.<cluster_name>.<base_domain> journalctl -b -f -u kubelet.service$sshcore@<worker-node>.<cluster_name>.<base_domain>journalctl-b-f-ukubelet.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs using SSH instead. Replace<worker-node>.<cluster_name>.<base_domain>with appropriate values:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

- Retrievecrio.servicejournald unit logs on worker nodes, after they have booted. This provides visibility into worker node CRI-O container runtime activity.Retrieve the logs usingoc:oc adm node-logs --role=worker -u crio$oc adm node-logs--role=worker-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs using SSH instead:ssh core@<worker-node>.<cluster_name>.<base_domain> journalctl -b -f -u crio.service$sshcore@<worker-node>.<cluster_name>.<base_domain>journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrievecrio.servicejournald unit logs on worker nodes, after they have booted. This provides visibility into worker node CRI-O container runtime activity.

- Retrieve the logs usingoc:oc adm node-logs --role=worker -u crio$oc adm node-logs--role=worker-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve the logs usingoc:

- If the API is not functional, review the logs using SSH instead:ssh core@<worker-node>.<cluster_name>.<base_domain> journalctl -b -f -u crio.service$sshcore@<worker-node>.<cluster_name>.<base_domain>journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs using SSH instead:

- Collect logs from specific subdirectories under/var/log/on worker nodes.Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/sssd/on all worker nodes:oc adm node-logs --role=worker --path=sssd$oc adm node-logs--role=worker--path=sssdCopy to ClipboardCopied!Toggle word wrapToggle overflowInspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/sssd/sssd.logcontents from all worker nodes:oc adm node-logs --role=worker --path=sssd/sssd.log$oc adm node-logs--role=worker--path=sssd/sssd.logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/sssd/sssd.log:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/sssd/sssd.log$sshcore@<worker-node>.<cluster_name>.<base_domain>sudotail-f/var/log/sssd/sssd.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Collect logs from specific subdirectories under/var/log/on worker nodes.

- Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/sssd/on all worker nodes:oc adm node-logs --role=worker --path=sssd$oc adm node-logs--role=worker--path=sssdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/sssd/on all worker nodes:

- Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/sssd/sssd.logcontents from all worker nodes:oc adm node-logs --role=worker --path=sssd/sssd.log$oc adm node-logs--role=worker--path=sssd/sssd.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/sssd/sssd.logcontents from all worker nodes:

- If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/sssd/sssd.log:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/sssd/sssd.log$sshcore@<worker-node>.<cluster_name>.<base_domain>sudotail-f/var/log/sssd/sssd.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/sssd/sssd.log:

- Review worker node container logs using SSH.List the containers:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo crictl ps -a$sshcore@<worker-node>.<cluster_name>.<base_domain>sudocrictlps-aCopy to ClipboardCopied!Toggle word wrapToggle overflowRetrieve a container’s logs usingcrictl:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<worker-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review worker node container logs using SSH.

- List the containers:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo crictl ps -a$sshcore@<worker-node>.<cluster_name>.<base_domain>sudocrictlps-aCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the containers:

- Retrieve a container’s logs usingcrictl:ssh core@<worker-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<worker-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a container’s logs usingcrictl:

- If you experience worker node configuration issues, verify that the MCO, MCO endpoint, and DNS record are functioning. The Machine Config Operator (MCO) manages operating system configuration during the installation procedure. Also verify system clock accuracy and certificate validity.Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:curl https://api-int.<cluster_name>:22623/config/worker$curlhttps://api-int.<cluster_name>:22623/config/workerCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the endpoint is unresponsive, verify load balancer configuration. Ensure that the endpoint is configured to run on port 22623.Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowRun a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowVerify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> curl https://api-int.<cluster_name>:22623/config/worker$sshcore@<bootstrap_fqdn>curlhttps://api-int.<cluster_name>:22623/config/workerCopy to ClipboardCopied!Toggle word wrapToggle overflowSystem clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:ssh core@<node>.<cluster_name>.<base_domain> chronyc tracking$sshcore@<node>.<cluster_name>.<base_domain>chronyc trackingCopy to ClipboardCopied!Toggle word wrapToggle overflowReview certificate validity:openssl s_client -connect api-int.<cluster_name>:22623 | openssl x509 -noout -text$openssl s_client-connectapi-int.<cluster_name>:22623|openssl x509-noout-textCopy to ClipboardCopied!Toggle word wrapToggle overflow

If you experience worker node configuration issues, verify that the MCO, MCO endpoint, and DNS record are functioning. The Machine Config Operator (MCO) manages operating system configuration during the installation procedure. Also verify system clock accuracy and certificate validity.

- Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:curl https://api-int.<cluster_name>:22623/config/worker$curlhttps://api-int.<cluster_name>:22623/config/workerCopy to ClipboardCopied!Toggle word wrapToggle overflow

Test whether the MCO endpoint is available. Replace<cluster_name>with appropriate values:

- If the endpoint is unresponsive, verify load balancer configuration. Ensure that the endpoint is configured to run on port 22623.
- Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflowRun a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the MCO endpoint’s DNS record is configured and resolves to the load balancer.

- Run a DNS lookup for the defined MCO endpoint name:dig api-int.<cluster_name> @<dns_server>$digapi-int.<cluster_name>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run a DNS lookup for the defined MCO endpoint name:

- Run a reverse lookup to the assigned MCO IP address on the load balancer:dig -x <load_balancer_mco_ip_address> @<dns_server>$dig-x<load_balancer_mco_ip_address>@<dns_server>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run a reverse lookup to the assigned MCO IP address on the load balancer:

- Verify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:ssh core@<bootstrap_fqdn> curl https://api-int.<cluster_name>:22623/config/worker$sshcore@<bootstrap_fqdn>curlhttps://api-int.<cluster_name>:22623/config/workerCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that the MCO is functioning from the bootstrap node directly. Replace<bootstrap_fqdn>with the bootstrap node’s fully qualified domain name:

- System clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:ssh core@<node>.<cluster_name>.<base_domain> chronyc tracking$sshcore@<node>.<cluster_name>.<base_domain>chronyc trackingCopy to ClipboardCopied!Toggle word wrapToggle overflow

System clock time must be synchronized between bootstrap, master, and worker nodes. Check each node’s system clock reference time and time synchronization statistics:

- Review certificate validity:openssl s_client -connect api-int.<cluster_name>:22623 | openssl x509 -noout -text$openssl s_client-connectapi-int.<cluster_name>:22623|openssl x509-noout-textCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review certificate validity:

### 7.1.12. Querying Operator status after installationCopy linkLink copied to clipboard!

You can check Operator status at the end of an installation. Retrieve diagnostic data for Operators that do not become available. Review logs for any Operator pods that are listed asPendingor have an error status. Validate base images used by problematic pods.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Check that cluster Operators are all available at the end of an installation.oc get clusteroperators$oc get clusteroperatorsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check that cluster Operators are all available at the end of an installation.

- Verify that all of the required certificate signing requests (CSRs) are approved. Some nodes might not move to aReadystatus and some cluster Operators might not become available if there are pending CSRs.Check the status of the CSRs and ensure that you see a client and server request with thePendingorApprovedstatus for each machine that you added to the cluster:oc get csr$oc get csrCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending 
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending 
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending1csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending2csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...Copy to ClipboardCopied!Toggle word wrapToggle overflow1A client request CSR.2A server request CSR.In this example, two machines are joining the cluster. You might see more approved CSRs in the list.If the CSRs were not approved, after all of the pending CSRs for the machines you added are inPendingstatus, approve the CSRs for your cluster machines:Because the CSRs rotate automatically, approve your CSRs within an hour of adding the machines to the cluster. If you do not approve them within an hour, the certificates will rotate, and more than two certificates will be present for each node. You must approve all of these certificates. After you approve the initial CSRs, the subsequent node client CSRs are automatically approved by the clusterkube-controller-manager.For clusters running on platforms that are not machine API enabled, such as bare metal and other user-provisioned infrastructure, you must implement a method of automatically approving the kubelet serving certificate requests (CSRs). If a request is not approved, then theoc exec,oc rsh, andoc logscommands cannot succeed, because a serving certificate is required when the API server connects to the kubelet. Any operation that contacts the Kubelet endpoint requires this certificate approval to be in place. The method must watch for new CSRs, confirm that the CSR was submitted by thenode-bootstrapperservice account in thesystem:nodeorsystem:admingroups, and confirm the identity of the node.To approve them individually, run the following command for each valid CSR:oc adm certificate approve <csr_name>$oc adm certificate approve<csr_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1<csr_name>is the name of a CSR from the list of current CSRs.To approve all pending CSRs, run the following command:oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve$oc get csr-ogo-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}'|xargsoc adm certificate approveCopy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that all of the required certificate signing requests (CSRs) are approved. Some nodes might not move to aReadystatus and some cluster Operators might not become available if there are pending CSRs.

- Check the status of the CSRs and ensure that you see a client and server request with thePendingorApprovedstatus for each machine that you added to the cluster:oc get csr$oc get csrCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending 
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending 
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending1csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending2csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...Copy to ClipboardCopied!Toggle word wrapToggle overflow1A client request CSR.2A server request CSR.In this example, two machines are joining the cluster. You might see more approved CSRs in the list.

Check the status of the CSRs and ensure that you see a client and server request with thePendingorApprovedstatus for each machine that you added to the cluster:

Example output

```
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending 
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending 
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...
```

```
NAME        AGE     REQUESTOR                                                                   CONDITION
csr-8b2br   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
```

```
csr-8vnps   15m     system:serviceaccount:openshift-machine-config-operator:node-bootstrapper   Pending
csr-bfd72   5m26s   system:node:ip-10-0-50-126.us-east-2.compute.internal                       Pending
```

```
csr-c57lv   5m26s   system:node:ip-10-0-95-157.us-east-2.compute.internal                       Pending
...
```

**1**
  A client request CSR.

**2**
  A server request CSR.

In this example, two machines are joining the cluster. You might see more approved CSRs in the list.

- If the CSRs were not approved, after all of the pending CSRs for the machines you added are inPendingstatus, approve the CSRs for your cluster machines:Because the CSRs rotate automatically, approve your CSRs within an hour of adding the machines to the cluster. If you do not approve them within an hour, the certificates will rotate, and more than two certificates will be present for each node. You must approve all of these certificates. After you approve the initial CSRs, the subsequent node client CSRs are automatically approved by the clusterkube-controller-manager.For clusters running on platforms that are not machine API enabled, such as bare metal and other user-provisioned infrastructure, you must implement a method of automatically approving the kubelet serving certificate requests (CSRs). If a request is not approved, then theoc exec,oc rsh, andoc logscommands cannot succeed, because a serving certificate is required when the API server connects to the kubelet. Any operation that contacts the Kubelet endpoint requires this certificate approval to be in place. The method must watch for new CSRs, confirm that the CSR was submitted by thenode-bootstrapperservice account in thesystem:nodeorsystem:admingroups, and confirm the identity of the node.To approve them individually, run the following command for each valid CSR:oc adm certificate approve <csr_name>$oc adm certificate approve<csr_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1<csr_name>is the name of a CSR from the list of current CSRs.To approve all pending CSRs, run the following command:oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve$oc get csr-ogo-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}'|xargsoc adm certificate approveCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the CSRs were not approved, after all of the pending CSRs for the machines you added are inPendingstatus, approve the CSRs for your cluster machines:

Because the CSRs rotate automatically, approve your CSRs within an hour of adding the machines to the cluster. If you do not approve them within an hour, the certificates will rotate, and more than two certificates will be present for each node. You must approve all of these certificates. After you approve the initial CSRs, the subsequent node client CSRs are automatically approved by the clusterkube-controller-manager.

For clusters running on platforms that are not machine API enabled, such as bare metal and other user-provisioned infrastructure, you must implement a method of automatically approving the kubelet serving certificate requests (CSRs). If a request is not approved, then theoc exec,oc rsh, andoc logscommands cannot succeed, because a serving certificate is required when the API server connects to the kubelet. Any operation that contacts the Kubelet endpoint requires this certificate approval to be in place. The method must watch for new CSRs, confirm that the CSR was submitted by thenode-bootstrapperservice account in thesystem:nodeorsystem:admingroups, and confirm the identity of the node.

- To approve them individually, run the following command for each valid CSR:oc adm certificate approve <csr_name>$oc adm certificate approve<csr_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1<csr_name>is the name of a CSR from the list of current CSRs.

To approve them individually, run the following command for each valid CSR:

**1**
  <csr_name>is the name of a CSR from the list of current CSRs.
- To approve all pending CSRs, run the following command:oc get csr -o go-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}' | xargs oc adm certificate approve$oc get csr-ogo-template='{{range .items}}{{if not .status}}{{.metadata.name}}{{"\n"}}{{end}}{{end}}'|xargsoc adm certificate approveCopy to ClipboardCopied!Toggle word wrapToggle overflow

To approve all pending CSRs, run the following command:

- View Operator events:oc describe clusteroperator <operator_name>$oc describe clusteroperator<operator_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

View Operator events:

- Review Operator pod status within the Operator’s namespace:oc get pods -n <operator_namespace>$oc get pods-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review Operator pod status within the Operator’s namespace:

- Obtain a detailed description for pods that do not haveRunningstatus:oc describe pod/<operator_pod_name> -n <operator_namespace>$oc describe pod/<operator_pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a detailed description for pods that do not haveRunningstatus:

- Inspect pod logs:oc logs pod/<operator_pod_name> -n <operator_namespace>$oc logs pod/<operator_pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect pod logs:

- When experiencing pod base image related issues, review base image status.Obtain details of the base image used by a problematic pod:oc get pod -o "jsonpath={range .status.containerStatuses[*]}{.name}{'\t'}{.state}{'\t'}{.image}{'\n'}{end}" <operator_pod_name> -n <operator_namespace>$oc get pod-o"jsonpath={range .status.containerStatuses[*]}{.name}{'\t'}{.state}{'\t'}{.image}{'\n'}{end}"<operator_pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflowList base image release information:oc adm release info <image_path>:<tag> --commits$oc adm release info<image_path>:<tag>--commitsCopy to ClipboardCopied!Toggle word wrapToggle overflow

When experiencing pod base image related issues, review base image status.

- Obtain details of the base image used by a problematic pod:oc get pod -o "jsonpath={range .status.containerStatuses[*]}{.name}{'\t'}{.state}{'\t'}{.image}{'\n'}{end}" <operator_pod_name> -n <operator_namespace>$oc get pod-o"jsonpath={range .status.containerStatuses[*]}{.name}{'\t'}{.state}{'\t'}{.image}{'\n'}{end}"<operator_pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain details of the base image used by a problematic pod:

- List base image release information:oc adm release info <image_path>:<tag> --commits$oc adm release info<image_path>:<tag>--commitsCopy to ClipboardCopied!Toggle word wrapToggle overflow

List base image release information:

### 7.1.13. Gathering logs from a failed installationCopy linkLink copied to clipboard!

If you gave an SSH key to your installation program, you can gather data about your failed installation.

You use a different command to gather logs about an unsuccessful installation than to gather logs from a running cluster. If you must gather logs from a running cluster, use theoc adm must-gathercommand.

Prerequisites

- Your OpenShift Container Platform installation failed before the bootstrap process finished. The bootstrap node is running and accessible through SSH.
- Thessh-agentprocess is active on your computer, and you provided the same SSH key to both thessh-agentprocess and the installation program.
- If you tried to install a cluster on infrastructure that you provisioned, you must have the fully qualified domain names of the bootstrap and control plane nodes.

Procedure

- Generate the commands that are required to obtain the installation logs from the bootstrap and control plane machines:If you used installer-provisioned infrastructure, change to the directory that contains the installation program and run the following command:./openshift-install gather bootstrap --dir <installation_directory>$./openshift-install gather bootstrap--dir<installation_directory>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1installation_directoryis the directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.For installer-provisioned infrastructure, the installation program stores information about the cluster, so you do not specify the hostnames or IP addresses.If you used infrastructure that you provisioned yourself, change to the directory that contains the installation program and run the following command:./openshift-install gather bootstrap --dir <installation_directory> \
    --bootstrap <bootstrap_address> \
    --master <master_1_address> \
    --master <master_2_address> \
    --master <master_3_address>$./openshift-install gather bootstrap--dir<installation_directory>\1--bootstrap <bootstrap_address> \2--master <master_1_address> \3--master <master_2_address> \4--master <master_3_address>5Copy to ClipboardCopied!Toggle word wrapToggle overflow1Forinstallation_directory, specify the same directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.2<bootstrap_address>is the fully qualified domain name or IP address of the cluster’s bootstrap machine.345For each control plane, or master, machine in your cluster, replace<master_*_address>with its fully qualified domain name or IP address.A default cluster contains three control plane machines. List all of your control plane machines as shown, no matter how many your cluster uses.Example outputINFO Pulling debug logs from the bootstrap machine
INFO Bootstrap gather logs captured here "<installation_directory>/log-bundle-<timestamp>.tar.gz"INFO Pulling debug logs from the bootstrap machine
INFO Bootstrap gather logs captured here "<installation_directory>/log-bundle-<timestamp>.tar.gz"Copy to ClipboardCopied!Toggle word wrapToggle overflowIf you open a Red Hat support case about your installation failure, include the compressed logs in the case.

Generate the commands that are required to obtain the installation logs from the bootstrap and control plane machines:

- If you used installer-provisioned infrastructure, change to the directory that contains the installation program and run the following command:./openshift-install gather bootstrap --dir <installation_directory>$./openshift-install gather bootstrap--dir<installation_directory>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1installation_directoryis the directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.For installer-provisioned infrastructure, the installation program stores information about the cluster, so you do not specify the hostnames or IP addresses.

If you used installer-provisioned infrastructure, change to the directory that contains the installation program and run the following command:

**1**
  installation_directoryis the directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.

For installer-provisioned infrastructure, the installation program stores information about the cluster, so you do not specify the hostnames or IP addresses.

- If you used infrastructure that you provisioned yourself, change to the directory that contains the installation program and run the following command:./openshift-install gather bootstrap --dir <installation_directory> \
    --bootstrap <bootstrap_address> \
    --master <master_1_address> \
    --master <master_2_address> \
    --master <master_3_address>$./openshift-install gather bootstrap--dir<installation_directory>\1--bootstrap <bootstrap_address> \2--master <master_1_address> \3--master <master_2_address> \4--master <master_3_address>5Copy to ClipboardCopied!Toggle word wrapToggle overflow1Forinstallation_directory, specify the same directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.2<bootstrap_address>is the fully qualified domain name or IP address of the cluster’s bootstrap machine.345For each control plane, or master, machine in your cluster, replace<master_*_address>with its fully qualified domain name or IP address.A default cluster contains three control plane machines. List all of your control plane machines as shown, no matter how many your cluster uses.

If you used infrastructure that you provisioned yourself, change to the directory that contains the installation program and run the following command:

```
./openshift-install gather bootstrap --dir <installation_directory> \
    --bootstrap <bootstrap_address> \
    --master <master_1_address> \
    --master <master_2_address> \
    --master <master_3_address>
```

```
--bootstrap <bootstrap_address> \
```

```
--master <master_1_address> \
```

```
--master <master_2_address> \
```

```
--master <master_3_address>
```

**1**
  Forinstallation_directory, specify the same directory you specified when you ran./openshift-install create cluster. This directory contains the OpenShift Container Platform definition files that the installation program creates.

**2**
  <bootstrap_address>is the fully qualified domain name or IP address of the cluster’s bootstrap machine.

**345**
  For each control plane, or master, machine in your cluster, replace<master_*_address>with its fully qualified domain name or IP address.

A default cluster contains three control plane machines. List all of your control plane machines as shown, no matter how many your cluster uses.

Example output

```
INFO Pulling debug logs from the bootstrap machine
INFO Bootstrap gather logs captured here "<installation_directory>/log-bundle-<timestamp>.tar.gz"
```

```
INFO Pulling debug logs from the bootstrap machine
INFO Bootstrap gather logs captured here "<installation_directory>/log-bundle-<timestamp>.tar.gz"
```

If you open a Red Hat support case about your installation failure, include the compressed logs in the case.

## 7.2. Verifying node healthCopy linkLink copied to clipboard!

### 7.2.1. Reviewing node status, resource usage, and configurationCopy linkLink copied to clipboard!

Review cluster node health status, resource consumption statistics, and node logs. Additionally, querykubeletstatus on individual nodes.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- List the name, status, and role for all nodes in the cluster:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the name, status, and role for all nodes in the cluster:

- Summarize CPU and memory usage for each node within the cluster:oc adm top nodes$oc admtopnodesCopy to ClipboardCopied!Toggle word wrapToggle overflow

Summarize CPU and memory usage for each node within the cluster:

- Summarize CPU and memory usage for a specific node:oc adm top node my-node$oc admtopnodemy-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Summarize CPU and memory usage for a specific node:

### 7.2.2. Querying the kubelet’s status on a nodeCopy linkLink copied to clipboard!

You can review cluster node health status, resource consumption statistics, and node logs. Additionally, you can querykubeletstatus on individual nodes.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- The kubelet is managed using a systemd service on each node. Review the kubelet’s status by querying thekubeletsystemd service within a debug pod.Start a debug pod for a node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you are runningoc debugon a control plane node, you can find administrativekubeconfigfiles in the/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigsdirectory.Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, orkubeletis not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.Check whether thekubeletsystemd service is active on the node:systemctl is-active kubelet#systemctl is-active kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflowOutput a more detailedkubelet.servicestatus summary:systemctl status kubelet#systemctl status kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

The kubelet is managed using a systemd service on each node. Review the kubelet’s status by querying thekubeletsystemd service within a debug pod.

- Start a debug pod for a node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowIf you are runningoc debugon a control plane node, you can find administrativekubeconfigfiles in the/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigsdirectory.

Start a debug pod for a node:

If you are runningoc debugon a control plane node, you can find administrativekubeconfigfiles in the/etc/kubernetes/static-pod-resources/kube-apiserver-certs/secrets/node-kubeconfigsdirectory.

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, orkubeletis not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, orkubeletis not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- Check whether thekubeletsystemd service is active on the node:systemctl is-active kubelet#systemctl is-active kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check whether thekubeletsystemd service is active on the node:

- Output a more detailedkubelet.servicestatus summary:systemctl status kubelet#systemctl status kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Output a more detailedkubelet.servicestatus summary:

### 7.2.3. Querying cluster node journal logsCopy linkLink copied to clipboard!

You can gatherjournaldunit logs and other logs within/var/logon individual cluster nodes.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- Your API service is still functional.
- You have SSH access to your hosts.

Procedure

- Querykubeletjournaldunit logs from OpenShift Container Platform cluster nodes. The following example queries control plane nodes only:oc adm node-logs --role=master -u kubelet$oc adm node-logs--role=master-ukubelet1Copy to ClipboardCopied!Toggle word wrapToggle overflowkubelet: Replace as appropriate to query other unit logs.

Querykubeletjournaldunit logs from OpenShift Container Platform cluster nodes. The following example queries control plane nodes only:

- kubelet: Replace as appropriate to query other unit logs.
- Collect logs from specific subdirectories under/var/log/on cluster nodes.Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflowInspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Collect logs from specific subdirectories under/var/log/on cluster nodes.

- Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver$oc adm node-logs--role=master--path=openshift-apiserverCopy to ClipboardCopied!Toggle word wrapToggle overflow

Retrieve a list of logs contained within a/var/log/subdirectory. The following example lists files in/var/log/openshift-apiserver/on all control plane nodes:

- Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:oc adm node-logs --role=master --path=openshift-apiserver/audit.log$oc adm node-logs--role=master--path=openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect a specific log within a/var/log/subdirectory. The following example outputs/var/log/openshift-apiserver/audit.logcontents from all control plane nodes:

- If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:ssh core@<master-node>.<cluster_name>.<base_domain> sudo tail -f /var/log/openshift-apiserver/audit.log$sshcore@<master-node>.<cluster_name>.<base_domain>sudotail-f/var/log/openshift-apiserver/audit.logCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs on each node using SSH instead. The following example tails/var/log/openshift-apiserver/audit.log:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

## 7.3. Troubleshooting CRI-O container runtime issuesCopy linkLink copied to clipboard!

### 7.3.1. About CRI-O container runtime engineCopy linkLink copied to clipboard!

CRI-O is a Kubernetes-native container engine implementation that integrates closely with the operating system to deliver an efficient and optimized Kubernetes experience. The CRI-O container engine runs as a systemd service on each OpenShift Container Platform cluster node.

When container runtime issues occur, verify the status of thecriosystemd service on each node. Gather CRI-O journald unit logs from nodes that have container runtime issues.

### 7.3.2. Verifying CRI-O runtime engine statusCopy linkLink copied to clipboard!

You can verify CRI-O container runtime engine status on each cluster node.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Review CRI-O status by querying thecriosystemd service on a node, within a debug pod.Start a debug pod for a node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowSet/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.Check whether thecriosystemd service is active on the node:systemctl is-active crio#systemctl is-active crioCopy to ClipboardCopied!Toggle word wrapToggle overflowOutput a more detailedcrio.servicestatus summary:systemctl status crio.service#systemctl status crio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review CRI-O status by querying thecriosystemd service on a node, within a debug pod.

- Start a debug pod for a node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod for a node:

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- Check whether thecriosystemd service is active on the node:systemctl is-active crio#systemctl is-active crioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check whether thecriosystemd service is active on the node:

- Output a more detailedcrio.servicestatus summary:systemctl status crio.service#systemctl status crio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Output a more detailedcrio.servicestatus summary:

### 7.3.3. Gathering CRI-O journald unit logsCopy linkLink copied to clipboard!

If you experience CRI-O issues, you can obtain CRI-O journald unit logs from a node.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).
- You have the fully qualified domain names of the control plane or control plane machines.

Procedure

- Gather CRI-O journald unit logs. The following example collects logs from all control plane nodes (within the cluster:oc adm node-logs --role=master -u crio$oc adm node-logs--role=master-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Gather CRI-O journald unit logs. The following example collects logs from all control plane nodes (within the cluster:

- Gather CRI-O journald unit logs from a specific node:oc adm node-logs <node_name> -u crio$oc adm node-logs<node_name>-ucrioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Gather CRI-O journald unit logs from a specific node:

- If the API is not functional, review the logs using SSH instead. Replace<node>.<cluster_name>.<base_domain>with appropriate values:ssh core@<node>.<cluster_name>.<base_domain> journalctl -b -f -u crio.service$sshcore@<node>.<cluster_name>.<base_domain>journalctl-b-f-ucrio.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review the logs using SSH instead. Replace<node>.<cluster_name>.<base_domain>with appropriate values:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

### 7.3.4. Cleaning CRI-O storageCopy linkLink copied to clipboard!

You can manually clear the CRI-O ephemeral storage if you experience the following issues:

- A node cannot run any pods and this error appears:Failed to create pod sandbox: rpc error: code = Unknown desc = failed to mount container XXX: error recreating the missing symlinks: error reading name of symlink for XXX: open /var/lib/containers/storage/overlay/XXX/link: no such file or directoryFailed to create pod sandbox: rpc error: code = Unknown desc = failed to mount container XXX: error recreating the missing symlinks: error reading name of symlink for XXX: open /var/lib/containers/storage/overlay/XXX/link: no such file or directoryCopy to ClipboardCopied!Toggle word wrapToggle overflow

A node cannot run any pods and this error appears:

- You cannot create a new container on a working node and the “can’t stat lower layer” error appears:can't stat lower layer ...  because it does not exist.  Going through storage to recreate the missing symlinks.can't stat lower layer ...  because it does not exist.  Going through storage to recreate the missing symlinks.Copy to ClipboardCopied!Toggle word wrapToggle overflow

You cannot create a new container on a working node and the “can’t stat lower layer” error appears:

- Your node is in theNotReadystate after a cluster upgrade or if you attempt to reboot it.
- The container runtime implementation (crio) is not working properly.
- You are unable to start a debug shell on the node usingoc debug node/<node_name>because the container runtime instance (crio) is not working.

Follow this process to completely wipe the CRI-O storage and resolve the errors.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Usecordonon the node. This is to avoid any workload getting scheduled if the node gets into theReadystatus. You will know that scheduling is disabled whenSchedulingDisabledis in your Status section:oc adm cordon <node_name>$oc adm cordon<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Usecordonon the node. This is to avoid any workload getting scheduled if the node gets into theReadystatus. You will know that scheduling is disabled whenSchedulingDisabledis in your Status section:

- Drain the node as the cluster-admin user:[REDACTED_ACCOUNT] adm drain <node_name> --ignore-daemonsets --delete-emptydir-data$oc adm drain<node_name>--ignore-daemonsets --delete-emptydir-dataCopy to ClipboardCopied!Toggle word wrapToggle overflowTheterminationGracePeriodSecondsattribute of a pod or pod template controls the graceful termination period. This attribute defaults at 30 seconds, but can be customized for each application as necessary. If set to more than 90 seconds, the pod might be marked asSIGKILLedand fail to terminate successfully.

Drain the node as the cluster-admin user:

[REDACTED_ACCOUNT] of a pod or pod template controls the graceful termination period. This attribute defaults at 30 seconds, but can be customized for each application as necessary. If set to more than 90 seconds, the pod might be marked asSIGKILLedand fail to terminate successfully.

- When the node returns, connect back to the node via SSH or Console. Then connect to the root user:[REDACTED_ACCOUNT] [REDACTED_EMAIL]
sudo -i$[REDACTED_EMAIL]$sudo-iCopy to ClipboardCopied!Toggle word wrapToggle overflow

When the node returns, connect back to the node via SSH or Console. Then connect to the root user:

[REDACTED_ACCOUNT]
ssh [REDACTED_EMAIL]
sudo -i
```

```
$ ssh [REDACTED_EMAIL]
$ sudo -i
```

- Manually stop the kubelet:systemctl stop kubelet#systemctl stop kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Manually stop the kubelet:

- Stop the containers and pods:Use the following command to stop the pods that are not in theHostNetwork. They must be removed first because their removal relies on the networking plugin pods, which are in theHostNetwork... for pod in $(crictl pods -q); do if [[ "$(crictl inspectp $pod | jq -r .status.linux.namespaces.options.network)" != "NODE" ]]; then crictl rmp -f $pod; fi; done.. for pod in $(crictl pods -q); do if [[ "$(crictl inspectp $pod | jq -r .status.linux.namespaces.options.network)" != "NODE" ]]; then crictl rmp -f $pod; fi; doneCopy to ClipboardCopied!Toggle word wrapToggle overflowStop all other pods:crictl rmp -fa#crictl rmp-faCopy to ClipboardCopied!Toggle word wrapToggle overflow

Stop the containers and pods:

- Use the following command to stop the pods that are not in theHostNetwork. They must be removed first because their removal relies on the networking plugin pods, which are in theHostNetwork... for pod in $(crictl pods -q); do if [[ "$(crictl inspectp $pod | jq -r .status.linux.namespaces.options.network)" != "NODE" ]]; then crictl rmp -f $pod; fi; done.. for pod in $(crictl pods -q); do if [[ "$(crictl inspectp $pod | jq -r .status.linux.namespaces.options.network)" != "NODE" ]]; then crictl rmp -f $pod; fi; doneCopy to ClipboardCopied!Toggle word wrapToggle overflow

Use the following command to stop the pods that are not in theHostNetwork. They must be removed first because their removal relies on the networking plugin pods, which are in theHostNetwork.

- Stop all other pods:crictl rmp -fa#crictl rmp-faCopy to ClipboardCopied!Toggle word wrapToggle overflow

Stop all other pods:

- Manually stop the crio services:systemctl stop crio#systemctl stop crioCopy to ClipboardCopied!Toggle word wrapToggle overflow

Manually stop the crio services:

- After you run those commands, you can completely wipe the ephemeral storage:crio wipe -f#crio wipe-fCopy to ClipboardCopied!Toggle word wrapToggle overflow

After you run those commands, you can completely wipe the ephemeral storage:

- Start the crio and kubelet service:systemctl start crio
systemctl start kubelet#systemctl start crio#systemctl start kubeletCopy to ClipboardCopied!Toggle word wrapToggle overflow

Start the crio and kubelet service:

```
systemctl start crio
systemctl start kubelet
```

```
# systemctl start crio
# systemctl start kubelet
```

- You will know if the clean up worked if the crio and kubelet services are started, and the node is in theReadystatus:oc get nodes$oc get nodesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME				    STATUS	                ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1  Ready, SchedulingDisabled   master	 133m   v1.30.3NAME				    STATUS	                ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1  Ready, SchedulingDisabled   master	 133m   v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflow

You will know if the clean up worked if the crio and kubelet services are started, and the node is in theReadystatus:

Example output

```
NAME				    STATUS	                ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1  Ready, SchedulingDisabled   master	 133m   v1.30.3
```

```
NAME				    STATUS	                ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1  Ready, SchedulingDisabled   master	 133m   v1.30.3
```

- Mark the node schedulable. You will know that the scheduling is enabled whenSchedulingDisabledis no longer in status:oc adm uncordon <node_name>$oc adm uncordon<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME				     STATUS	      ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1   Ready            master   133m   v1.30.3NAME				     STATUS	      ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1   Ready            master   133m   v1.30.3Copy to ClipboardCopied!Toggle word wrapToggle overflow

Mark the node schedulable. You will know that the scheduling is enabled whenSchedulingDisabledis no longer in status:

Example output

```
NAME				     STATUS	      ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1   Ready            master   133m   v1.30.3
```

```
NAME				     STATUS	      ROLES    AGE    VERSION
ci-ln-tkbxyft-f76d1-nvwhr-master-1   Ready            master   133m   v1.30.3
```

## 7.4. Troubleshooting operating system issuesCopy linkLink copied to clipboard!

OpenShift Container Platform runs on RHCOS. You can follow these procedures to troubleshoot problems related to the operating system.

### 7.4.1. Investigating kernel crashesCopy linkLink copied to clipboard!

Thekdumpservice, included in thekexec-toolspackage, provides a crash-dumping mechanism. You can use this service to save the contents of a system’s memory for later analysis.

Thex86_64architecture supports kdump in General Availability (GA) status, whereas other architectures support kdump in Technology Preview (TP) status.

The following table provides details about the support level of kdump for different architectures.

| Architecture | Support level |
| --- | --- |
| x86_64 | GA |
| aarch64 | TP |
| s390x | TP |
| ppc64le | TP |

x86_64

GA

aarch64

TP

s390x

TP

ppc64le

TP

Kdump support, for the preceding three architectures in the table, is a Technology Preview feature only. Technology Preview features are not supported with Red Hat production service level agreements (SLAs) and might not be functionally complete. Red Hat does not recommend using them in production. These features provide early access to upcoming product features, enabling customers to test functionality and provide feedback during the development process.

For more information about the support scope of Red Hat Technology Preview features, seeTechnology Preview Features Support Scope.

#### 7.4.1.1. Enabling kdumpCopy linkLink copied to clipboard!

RHCOS ships with thekexec-toolspackage, but manual configuration is required to enable thekdumpservice.

Procedure

Perform the following steps to enable kdump on RHCOS.

- To reserve memory for the crash kernel during the first kernel booting, provide kernel arguments by entering the following command:rpm-ostree kargs --append='crashkernel=256M'#rpm-ostree kargs--append='crashkernel=256M'Copy to ClipboardCopied!Toggle word wrapToggle overflowFor theppc64leplatform, the recommended value forcrashkerneliscrashkernel=2G-4G:384M,4G-16G:512M,16G-64G:1G,64G-128G:2G,128G-:4G.

To reserve memory for the crash kernel during the first kernel booting, provide kernel arguments by entering the following command:

For theppc64leplatform, the recommended value forcrashkerneliscrashkernel=2G-4G:384M,4G-16G:512M,16G-64G:1G,64G-128G:2G,128G-:4G.

- Optional: To write the crash dump over the network or to some other location, rather than to the default local/var/crashlocation, edit the/etc/kdump.confconfiguration file.If your node uses LUKS-encrypted devices, you must use network dumps as kdump does not support saving crash dumps to LUKS-encrypted devices.For details on configuring thekdumpservice, see the comments in/etc/sysconfig/kdump,/etc/kdump.conf, and thekdump.confmanual page. Also refer to theRHEL kdump documentationfor further information on configuring the dump target.If you have multipathing enabled on your primary disk, the dump target must be either an NFS or SSH server and you must exclude the multipath module from your/etc/kdump.confconfiguration file.

Optional: To write the crash dump over the network or to some other location, rather than to the default local/var/crashlocation, edit the/etc/kdump.confconfiguration file.

If your node uses LUKS-encrypted devices, you must use network dumps as kdump does not support saving crash dumps to LUKS-encrypted devices.

For details on configuring thekdumpservice, see the comments in/etc/sysconfig/kdump,/etc/kdump.conf, and thekdump.confmanual page. Also refer to theRHEL kdump documentationfor further information on configuring the dump target.

If you have multipathing enabled on your primary disk, the dump target must be either an NFS or SSH server and you must exclude the multipath module from your/etc/kdump.confconfiguration file.

- Enable thekdumpsystemd service.systemctl enable kdump.service#systemctlenablekdump.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Enable thekdumpsystemd service.

- Reboot your system.systemctl reboot#systemctlrebootCopy to ClipboardCopied!Toggle word wrapToggle overflow

Reboot your system.

- Ensure that kdump has loaded a crash kernel by checking that thekdump.servicesystemd service has started and exited successfully and that the command,cat /sys/kernel/kexec_crash_loaded, prints the value1.

#### 7.4.1.2. Enabling kdump on day-1Copy linkLink copied to clipboard!

Thekdumpservice is intended to be enabled per node to debug kernel problems. Because there are costs to having kdump enabled, and these costs accumulate with each additional kdump-enabled node, it is recommended that thekdumpservice only be enabled on each node as needed. Potential costs of enabling thekdumpservice on each node include:

- Less available RAM due to memory being reserved for the crash kernel.
- Node unavailability while the kernel is dumping the core.
- Additional storage space being used to store the crash dumps.

If you are aware of the downsides and trade-offs of having thekdumpservice enabled, it is possible to enable kdump in a cluster-wide fashion. Although machine-specific machine configs are not yet supported, you can use asystemdunit in aMachineConfigobject as a day-1 customization and have kdump enabled on all nodes in the cluster. You can create aMachineConfigobject and inject that object into the set of manifest files used by Ignition during cluster setup.

See "Customizing nodes" in theInstallingInstallation configurationsection for more information and examples on how to use Ignition configs.

Procedure

Create aMachineConfigobject for cluster-wide configuration:

- Create a Butane config file,99-worker-kdump.bu, that configures and enables kdump:TheButane versionyou specify in the config file should match the OpenShift Container Platform version and always ends in0. For example,4.17.0. See "Creating machine configs with Butane" for information about Butane.variant: openshift
version: 4.17.0
metadata:
  name: 99-worker-kdump 
  labels:
    machineconfiguration.openshift.io/role: worker 
openshift:
  kernel_arguments: 
    - crashkernel=256M
storage:
  files:
    - path: /etc/kdump.conf 
      mode: 0644
      overwrite: true
      contents:
        inline: |
          path /var/crash
          core_collector makedumpfile -l --message-level 7 -d 31

    - path: /etc/sysconfig/kdump 
      mode: 0644
      overwrite: true
      contents:
        inline: |
          KDUMP_COMMANDLINE_REMOVE="hugepages hugepagesz slub_debug quiet log_buf_len swiotlb"
          KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never nokaslr novmcoredd hest_disable" 
          KEXEC_ARGS="-s"
          KDUMP_IMG="vmlinuz"

systemd:
  units:
    - name: kdump.service
      enabled: truevariant:openshiftversion:4.17.0metadata:name:99-worker-kdump1labels:machineconfiguration.openshift.io/role:worker2openshift:kernel_arguments:3-crashkernel=256Mstorage:files:-path:/etc/kdump.conf4mode:0644overwrite:truecontents:inline:|path /var/crash
          core_collector makedumpfile -l --message-level 7 -d 31-path:/etc/sysconfig/kdump5mode:0644overwrite:truecontents:inline:|KDUMP_COMMANDLINE_REMOVE="hugepages hugepagesz slub_debug quiet log_buf_len swiotlb"
          KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never nokaslr novmcoredd hest_disable"6KEXEC_ARGS="-s"
          KDUMP_IMG="vmlinuz"systemd:units:-name:kdump.serviceenabled:trueCopy to ClipboardCopied!Toggle word wrapToggle overflow112Replaceworkerwithmasterin both locations when creating aMachineConfigobject for control plane nodes.3Provide kernel arguments to reserve memory for the crash kernel. You can add other kernel arguments if necessary. For theppc64leplatform, the recommended value forcrashkerneliscrashkernel=2G-4G:384M,4G-16G:512M,16G-64G:1G,64G-128G:2G,128G-:4G.4If you want to change the contents of/etc/kdump.conffrom the default, include this section and modify theinlinesubsection accordingly.5If you want to change the contents of/etc/sysconfig/kdumpfrom the default, include this section and modify theinlinesubsection accordingly.6For theppc64leplatform, replacenr_cpus=1withmaxcpus=1, which is not supported on this platform.

Create a Butane config file,99-worker-kdump.bu, that configures and enables kdump:

TheButane versionyou specify in the config file should match the OpenShift Container Platform version and always ends in0. For example,4.17.0. See "Creating machine configs with Butane" for information about Butane.

```
variant: openshift
version: 4.17.0
metadata:
  name: 99-worker-kdump 
  labels:
    machineconfiguration.openshift.io/role: worker 
openshift:
  kernel_arguments: 
    - crashkernel=256M
storage:
  files:
    - path: /etc/kdump.conf 
      mode: 0644
      overwrite: true
      contents:
        inline: |
          path /var/crash
          core_collector makedumpfile -l --message-level 7 -d 31

    - path: /etc/sysconfig/kdump 
      mode: 0644
      overwrite: true
      contents:
        inline: |
          KDUMP_COMMANDLINE_REMOVE="hugepages hugepagesz slub_debug quiet log_buf_len swiotlb"
          KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never nokaslr novmcoredd hest_disable" 
          KEXEC_ARGS="-s"
          KDUMP_IMG="vmlinuz"

systemd:
  units:
    - name: kdump.service
      enabled: true
```

```
variant: openshift
version: 4.17.0
metadata:
  name: 99-worker-kdump
```

```
labels:
    machineconfiguration.openshift.io/role: worker
```

```
openshift:
  kernel_arguments:
```

```
- crashkernel=256M
storage:
  files:
    - path: /etc/kdump.conf
```

```
mode: 0644
      overwrite: true
      contents:
        inline: |
          path /var/crash
          core_collector makedumpfile -l --message-level 7 -d 31

    - path: /etc/sysconfig/kdump
```

```
mode: 0644
      overwrite: true
      contents:
        inline: |
          KDUMP_COMMANDLINE_REMOVE="hugepages hugepagesz slub_debug quiet log_buf_len swiotlb"
          KDUMP_COMMANDLINE_APPEND="irqpoll nr_cpus=1 reset_devices cgroup_disable=memory mce=off numa=off udev.children-max=2 panic=10 rootflags=nofail acpi_no_memhotplug transparent_hugepage=never nokaslr novmcoredd hest_disable"
```

```
KEXEC_ARGS="-s"
          KDUMP_IMG="vmlinuz"

systemd:
  units:
    - name: kdump.service
      enabled: true
```

**112**
  Replaceworkerwithmasterin both locations when creating aMachineConfigobject for control plane nodes.

**3**
  Provide kernel arguments to reserve memory for the crash kernel. You can add other kernel arguments if necessary. For theppc64leplatform, the recommended value forcrashkerneliscrashkernel=2G-4G:384M,4G-16G:512M,16G-64G:1G,64G-128G:2G,128G-:4G.

**4**
  If you want to change the contents of/etc/kdump.conffrom the default, include this section and modify theinlinesubsection accordingly.

**5**
  If you want to change the contents of/etc/sysconfig/kdumpfrom the default, include this section and modify theinlinesubsection accordingly.

**6**
  For theppc64leplatform, replacenr_cpus=1withmaxcpus=1, which is not supported on this platform.

To export the dumps to NFS targets, some kernel modules must be explicitly added to the configuration file:

Example/etc/kdump.conffile

```
nfs server.example.com:/export/cores
core_collector makedumpfile -l --message-level 7 -d 31
extra_bins /sbin/mount.nfs
extra_modules nfs nfsv3 nfs_layout_nfsv41_files blocklayoutdriver nfs_layout_flexfiles nfs_layout_nfsv41_files
```

```
nfs server.example.com:/export/cores
core_collector makedumpfile -l --message-level 7 -d 31
extra_bins /sbin/mount.nfs
extra_modules nfs nfsv3 nfs_layout_nfsv41_files blocklayoutdriver nfs_layout_flexfiles nfs_layout_nfsv41_files
```

- Use Butane to generate a machine config YAML file,99-worker-kdump.yaml, containing the configuration to be delivered to the nodes:butane 99-worker-kdump.bu -o 99-worker-kdump.yaml$butane99-worker-kdump.bu-o99-worker-kdump.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Use Butane to generate a machine config YAML file,99-worker-kdump.yaml, containing the configuration to be delivered to the nodes:

- Put the YAML file into the<installation_directory>/manifests/directory during cluster setup. You can also create thisMachineConfigobject after cluster setup with the YAML file:oc create -f 99-worker-kdump.yaml$oc create-f99-worker-kdump.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Put the YAML file into the<installation_directory>/manifests/directory during cluster setup. You can also create thisMachineConfigobject after cluster setup with the YAML file:

#### 7.4.1.3. Testing the kdump configurationCopy linkLink copied to clipboard!

See theTesting the kdump configurationsection in the RHEL documentation for kdump.

#### 7.4.1.4. Analyzing a core dumpCopy linkLink copied to clipboard!

See theAnalyzing a core dumpsection in the RHEL documentation for kdump.

It is recommended to perform vmcore analysis on a separate RHEL system.

### 7.4.2. Debugging Ignition failuresCopy linkLink copied to clipboard!

If a machine cannot be provisioned, Ignition fails and RHCOS will boot into the emergency shell. Use the following procedure to get debugging information.

Procedure

- Run the following command to show which service units failed:systemctl --failed$systemctl--failedCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to show which service units failed:

- Optional: Run the following command on an individual service unit to find out more information:journalctl -u <unit>.service$journalctl-u<unit>.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Run the following command on an individual service unit to find out more information:

## 7.5. Troubleshooting network issuesCopy linkLink copied to clipboard!

### 7.5.1. How the network interface is selectedCopy linkLink copied to clipboard!

For installations on bare metal or with virtual machines that have more than one network interface controller (NIC), the NIC that OpenShift Container Platform uses for communication with the Kubernetes API server is determined by thenodeip-configuration.serviceservice unit that is run by systemd when the node boots. Thenodeip-configuration.serviceselects the IP from the interface associated with the default route.

After thenodeip-configuration.serviceservice determines the correct NIC, the service creates the/etc/systemd/system/kubelet.service.d/20-nodenet.conffile. The20-nodenet.conffile sets theKUBELET_NODE_IPenvironment variable to the IP address that the service selected.

When the kubelet service starts, it reads the value of the environment variable from the20-nodenet.conffile and sets the IP address as the value of the--node-ipkubelet command-line argument. As a result, the kubelet service uses the selected IP address as the node IP address.

If hardware or networking is reconfigured after installation, or if there is a networking layout where the node IP should not come from the default route interface, it is possible for thenodeip-configuration.serviceservice to select a different NIC after a reboot. In some cases, you might be able to detect that a different NIC is selected by reviewing theINTERNAL-IPcolumn in the output from theoc get nodes -o widecommand.

If network communication is disrupted or misconfigured because a different NIC is selected, you might receive the following error:EtcdCertSignerControllerDegraded. You can create a hint file that includes theNODEIP_HINTvariable to override the default IP selection logic. For more information, see Optional: Overriding the default node IP selection logic.

#### 7.5.1.1. Optional: Overriding the default node IP selection logicCopy linkLink copied to clipboard!

To override the default IP selection logic, you can create a hint file that includes theNODEIP_HINTvariable to override the default IP selection logic. Creating a hint file allows you to select a specific node IP address from the interface in the subnet of the IP address specified in theNODEIP_HINTvariable.

For example, if a node has two interfaces,eth0with an address of10.0.0.10/24, andeth1with an address of192.0.2.5/24, and the default route points toeth0([REDACTED_PRIVATE_IP]),the node IP address would normally use the10.0.0.10IP address.

Users can configure theNODEIP_HINTvariable to point at a known IP in the subnet, for example, a subnet gateway such as192.0.2.1so that the other subnet,192.0.2.0/24, is selected. As a result, the192.0.2.5IP address oneth1is used for the node.

The following procedure shows how to override the default node IP selection logic.

Procedure

- Add a hint file to your/etc/default/nodeip-configurationfile, for example:NODEIP_HINT=192.0.2.1NODEIP_HINT=192.0.2.1Copy to ClipboardCopied!Toggle word wrapToggle overflowDo not use the exact IP address of a node as a hint, for example,192.0.2.5. Using the exact IP address of a node causes the node using the hint IP address to fail to configure correctly.The IP address in the hint file is only used to determine the correct subnet. It will not receive traffic as a result of appearing in the hint file.

Add a hint file to your/etc/default/nodeip-configurationfile, for example:

- Do not use the exact IP address of a node as a hint, for example,192.0.2.5. Using the exact IP address of a node causes the node using the hint IP address to fail to configure correctly.
- The IP address in the hint file is only used to determine the correct subnet. It will not receive traffic as a result of appearing in the hint file.
- Generate thebase-64encoded content by running the following command:echo -n 'NODEIP_HINT=192.0.2.1' | base64 -w0$echo-n'NODEIP_HINT=192.0.2.1'|base64-w0Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputTk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==Tk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==Copy to ClipboardCopied!Toggle word wrapToggle overflow

Generate thebase-64encoded content by running the following command:

Example output

- Activate the hint by creating a machine config manifest for bothmasterandworkerroles before deploying the cluster:99-nodeip-hint-master.yamlapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 99-nodeip-hint-master
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,<encoded_content> 
        mode: 0644
        overwrite: true
        path: /etc/default/nodeip-configurationapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:mastername:99-nodeip-hint-masterspec:config:ignition:version:3.2.0storage:files:-contents:source:data:text/plain;charset=utf-8;base64,<encoded_content>1mode:0644overwrite:truepath:/etc/default/nodeip-configurationCopy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<encoded_contents>with the base64-encoded content of the/etc/default/nodeip-configurationfile, for example,Tk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==. Note that a space is not acceptable after the comma and before the encoded content.99-nodeip-hint-worker.yamlapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
 labels:
   machineconfiguration.openshift.io/role: worker
   name: 99-nodeip-hint-worker
spec:
 config:
   ignition:
     version: 3.2.0
   storage:
     files:
     - contents:
         source: data:text/plain;charset=utf-8;base64,<encoded_content> 
       mode: 0644
       overwrite: true
       path: /etc/default/nodeip-configurationapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:workername:99-nodeip-hint-workerspec:config:ignition:version:3.2.0storage:files:-contents:source:data:text/plain;charset=utf-8;base64,<encoded_content>1mode:0644overwrite:truepath:/etc/default/nodeip-configurationCopy to ClipboardCopied!Toggle word wrapToggle overflow1Replace<encoded_contents>with the base64-encoded content of the/etc/default/nodeip-configurationfile, for example,Tk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==. Note that a space is not acceptable after the comma and before the encoded content.

Activate the hint by creating a machine config manifest for bothmasterandworkerroles before deploying the cluster:

99-nodeip-hint-master.yaml

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 99-nodeip-hint-master
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,<encoded_content> 
        mode: 0644
        overwrite: true
        path: /etc/default/nodeip-configuration
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
  name: 99-nodeip-hint-master
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:text/plain;charset=utf-8;base64,<encoded_content>
```

```
mode: 0644
        overwrite: true
        path: /etc/default/nodeip-configuration
```

**1**
  Replace<encoded_contents>with the base64-encoded content of the/etc/default/nodeip-configurationfile, for example,Tk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==. Note that a space is not acceptable after the comma and before the encoded content.

99-nodeip-hint-worker.yaml

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
 labels:
   machineconfiguration.openshift.io/role: worker
   name: 99-nodeip-hint-worker
spec:
 config:
   ignition:
     version: 3.2.0
   storage:
     files:
     - contents:
         source: data:text/plain;charset=utf-8;base64,<encoded_content> 
       mode: 0644
       overwrite: true
       path: /etc/default/nodeip-configuration
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
 labels:
   machineconfiguration.openshift.io/role: worker
   name: 99-nodeip-hint-worker
spec:
 config:
   ignition:
     version: 3.2.0
   storage:
     files:
     - contents:
         source: data:text/plain;charset=utf-8;base64,<encoded_content>
```

```
mode: 0644
       overwrite: true
       path: /etc/default/nodeip-configuration
```

**1**
  Replace<encoded_contents>with the base64-encoded content of the/etc/default/nodeip-configurationfile, for example,Tk9ERUlQX0hJTlQ9MTkyLjAuMCxxxx==. Note that a space is not acceptable after the comma and before the encoded content.
- Save the manifest to the directory where you store your cluster configuration, for example,~/clusterconfigs.
- Deploy the cluster.

#### 7.5.1.2. Configuring OVN-Kubernetes to use a secondary OVS bridgeCopy linkLink copied to clipboard!

You can create an additional orsecondaryOpen vSwitch (OVS) bridge,br-ex1, that OVN-Kubernetes manages and the Multiple External Gateways (MEG) implementation uses for defining external gateways for an OpenShift Container Platform node. You can define a MEG in anAdminPolicyBasedExternalRoutecustom resource (CR). The MEG implementation provides a pod with access to multiple gateways, equal-cost multipath (ECMP) routes, and the Bidirectional Forwarding Detection (BFD) implementation.

Consider a use case for pods impacted by the Multiple External Gateways (MEG) feature and you want to egress traffic to a different interface, for examplebr-ex1, on a node. Egress traffic for pods not impacted by MEG get routed to the default OVSbr-exbridge.

Currently, MEG is unsupported for use with other egress features, such as egress IP, egress firewalls, or egress routers. Attempting to use MEG with egress features like egress IP can result in routing and traffic flow conflicts. This occurs because of how OVN-Kubernetes handles routing and source network address translation (SNAT). This results in inconsistent routing and might break connections in some environments where the return path must patch the incoming path.

You must define the additional bridge in an interface definition of a machine configuration manifest file. The Machine Config Operator uses the manifest to create a new file at/etc/ovnk/extra_bridgeon the host. The new file includes the name of the network interface that the additional OVS bridge configures for a node.

Do not use thenmstateAPI to make configuration changes to the secondary interface that is defined in the/etc/ovnk/extra_bridgedirectory path. Theconfigure-ovs.shconfiguration script creates and manages OVS bridge interfaces, so any interruptive changes to these interfaces by thenmstateAPI can lead to network configuration instability.

After you create and edit the manifest file, the Machine Config Operator completes tasks in the following order:

- Drains nodes in singular order based on the selected machine configuration pool.
- Injects Ignition configuration files into each node, so that each node receives the additionalbr-ex1bridge network configuration.
- Verify that thebr-exMAC address matches the MAC address for the interface thatbr-exuses for the network connection.
- Executes theconfigure-ovs.shshell script that references the new interface definition.
- Addsbr-exandbr-ex1to the host node.
- Uncordons the nodes.

After all the nodes return to theReadystate and the OVN-Kubernetes Operator detects and configuresbr-exandbr-ex1, the Operator applies thek8s.ovn.org/l3-gateway-configannotation to each node.

For more information about useful situations for the additionalbr-ex1bridge and a situation that always requires the defaultbr-exbridge, see "Configuration for a localnet topology".

Procedure

- Optional: Create an interface connection that your additional bridge,br-ex1, can use by completing the following steps. The example steps show the creation of a new bond and its dependent interfaces that are all defined in a machine configuration manifest file. The additional bridge uses theMachineConfigobject to form a additional bond interface.Do not use the Kubernetes NMState Operator or aNodeNetworkConfigurationPolicy(NNCP) manifest file to define the additional interface. Ensure that the additional interface or sub-interfaces when defining abondinterface are not used by an existingbr-exOVN Kubernetes network deployment.You cannot make configuration changes to thebr-exbridge or its underlying interfaces as a postinstallation task. As a workaround, use a secondary network interface connected to your host or switch.Create the following interface definition files. These files get added to a machine configuration manifest file so that host nodes can access the definition files.Example of the first interface definition file that is namedeno1.config[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of the second interface definition file that is namedeno2.config[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of the second bond interface definition file that is namedbond1.config[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=auto[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=autoCopy to ClipboardCopied!Toggle word wrapToggle overflowConvert the definition files to Base64 encoded strings by running the following command:base64 <directory_path>/en01.config$base64<directory_path>/en01.configCopy to ClipboardCopied!Toggle word wrapToggle overflowbase64 <directory_path>/eno2.config$base64<directory_path>/eno2.configCopy to ClipboardCopied!Toggle word wrapToggle overflowbase64 <directory_path>/bond1.config$base64<directory_path>/bond1.configCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Create an interface connection that your additional bridge,br-ex1, can use by completing the following steps. The example steps show the creation of a new bond and its dependent interfaces that are all defined in a machine configuration manifest file. The additional bridge uses theMachineConfigobject to form a additional bond interface.

Do not use the Kubernetes NMState Operator or aNodeNetworkConfigurationPolicy(NNCP) manifest file to define the additional interface. Ensure that the additional interface or sub-interfaces when defining abondinterface are not used by an existingbr-exOVN Kubernetes network deployment.

You cannot make configuration changes to thebr-exbridge or its underlying interfaces as a postinstallation task. As a workaround, use a secondary network interface connected to your host or switch.

- Create the following interface definition files. These files get added to a machine configuration manifest file so that host nodes can access the definition files.Example of the first interface definition file that is namedeno1.config[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of the second interface definition file that is namedeno2.config[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of the second bond interface definition file that is namedbond1.config[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=auto[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=autoCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create the following interface definition files. These files get added to a machine configuration manifest file so that host nodes can access the definition files.

Example of the first interface definition file that is namedeno1.config

```
[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20
```

```
[connection]
id=eno1
type=ethernet
interface-name=eno1
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20
```

Example of the second interface definition file that is namedeno2.config

```
[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20
```

```
[connection]
id=eno2
type=ethernet
interface-name=eno2
master=bond1
slave-type=bond
autoconnect=true
autoconnect-priority=20
```

Example of the second bond interface definition file that is namedbond1.config

```
[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=auto
```

```
[connection]
id=bond1
type=bond
interface-name=bond1
autoconnect=true
connection.autoconnect-slaves=1
autoconnect-priority=20

[bond]
mode=802.3ad
miimon=100
xmit_hash_policy="layer3+4"

[ipv4]
method=auto
```

- Convert the definition files to Base64 encoded strings by running the following command:base64 <directory_path>/en01.config$base64<directory_path>/en01.configCopy to ClipboardCopied!Toggle word wrapToggle overflowbase64 <directory_path>/eno2.config$base64<directory_path>/eno2.configCopy to ClipboardCopied!Toggle word wrapToggle overflowbase64 <directory_path>/bond1.config$base64<directory_path>/bond1.configCopy to ClipboardCopied!Toggle word wrapToggle overflow

Convert the definition files to Base64 encoded strings by running the following command:

- Prepare the environment variables. Replace<machine_role>with the node role, such asworker, and replace<interface_name>with the name of your additionalbr-exbridge name.export ROLE=<machine_role>$exportROLE=<machine_role>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Prepare the environment variables. Replace<machine_role>with the node role, such asworker, and replace<interface_name>with the name of your additionalbr-exbridge name.

- Define each interface definition in a machine configuration manifest file:Example of a machine configuration file with definitions added forbond1,eno1, anden02apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-${ROLE}-sec-bridge-cni
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-bond1.conf>
        path: /etc/NetworkManager/system-connections/bond1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno1.conf>
        path: /etc/NetworkManager/system-connections/eno1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno2.conf>
        path: /etc/NetworkManager/system-connections/eno2.nmconnection
        filesystem: root
        mode: 0600
# ...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:${worker}name:12-${ROLE}-sec-bridge-cnispec:config:ignition:version:3.2.0storage:files:-contents:source:data:;base64,<base-64-encoded-contents-for-bond1.conf>path:/etc/NetworkManager/system-connections/bond1.nmconnectionfilesystem:rootmode:0600-contents:source:data:;base64,<base-64-encoded-contents-for-eno1.conf>path:/etc/NetworkManager/system-connections/eno1.nmconnectionfilesystem:rootmode:0600-contents:source:data:;base64,<base-64-encoded-contents-for-eno2.conf>path:/etc/NetworkManager/system-connections/eno2.nmconnectionfilesystem:rootmode:0600# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Define each interface definition in a machine configuration manifest file:

Example of a machine configuration file with definitions added forbond1,eno1, anden02

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-${ROLE}-sec-bridge-cni
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-bond1.conf>
        path: /etc/NetworkManager/system-connections/bond1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno1.conf>
        path: /etc/NetworkManager/system-connections/eno1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno2.conf>
        path: /etc/NetworkManager/system-connections/eno2.nmconnection
        filesystem: root
        mode: 0600
# ...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-${ROLE}-sec-bridge-cni
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-bond1.conf>
        path: /etc/NetworkManager/system-connections/bond1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno1.conf>
        path: /etc/NetworkManager/system-connections/eno1.nmconnection
        filesystem: root
        mode: 0600
      - contents:
          source: data:;base64,<base-64-encoded-contents-for-eno2.conf>
        path: /etc/NetworkManager/system-connections/eno2.nmconnection
        filesystem: root
        mode: 0600
# ...
```

- Create a machine configuration manifest file for configuring the network plugin by entering the following command in your terminal:oc create -f <machine_config_file_name>$oc create-f<machine_config_file_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Create a machine configuration manifest file for configuring the network plugin by entering the following command in your terminal:

- Create an Open vSwitch (OVS) bridge,br-ex1, on nodes by using the OVN-Kubernetes network plugin to create anextra_bridgefile`. Ensure that you save the file in the/etc/ovnk/extra_bridgepath of the host. The file must state the interface name that supports the additional bridge and not the default interface that supportsbr-ex, which holds the primary IP address of the node.Example configuration for theextra_bridgefile,/etc/ovnk/extra_bridge, that references a additional interfacebond1bond1Copy to ClipboardCopied!Toggle word wrapToggle overflow

Create an Open vSwitch (OVS) bridge,br-ex1, on nodes by using the OVN-Kubernetes network plugin to create anextra_bridgefile`. Ensure that you save the file in the/etc/ovnk/extra_bridgepath of the host. The file must state the interface name that supports the additional bridge and not the default interface that supportsbr-ex, which holds the primary IP address of the node.

Example configuration for theextra_bridgefile,/etc/ovnk/extra_bridge, that references a additional interface

- Create a machine configuration manifest file that defines the existing static interface that hostsbr-ex1on any nodes restarted on your cluster:Example of a machine configuration file that definesbond1as the interface for hostingbr-ex1apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-extra-bridge
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/ovnk/extra_bridge
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond1
          filesystem: rootapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:${worker}name:12-worker-extra-bridgespec:config:ignition:version:3.2.0storage:files:-path:/etc/ovnk/extra_bridgemode:0420overwrite:truecontents:source:data:text/plain;charset=utf-8,bond1filesystem:rootCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a machine configuration manifest file that defines the existing static interface that hostsbr-ex1on any nodes restarted on your cluster:

Example of a machine configuration file that definesbond1as the interface for hostingbr-ex1

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-extra-bridge
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/ovnk/extra_bridge
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond1
          filesystem: root
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-extra-bridge
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /etc/ovnk/extra_bridge
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond1
          filesystem: root
```

- Apply the machine-configuration to your selected nodes:oc create -f <machine_config_file_name>$oc create-f<machine_config_file_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Apply the machine-configuration to your selected nodes:

- Optional: You can override thebr-exselection logic for nodes by creating a machine configuration file that in turn creates a/var/lib/ovnk/iface_default_hintresource.The resource lists the name of the interface thatbr-exselects for your cluster. By default,br-exselects the primary interface for a node based on boot order and the IP address subnet in the machine network. Certain machine network configurations might require thatbr-excontinues to select the default interfaces or bonds for a host node.Create a machine configuration file on the host node to override the default interface.Only create this machine configuration file for the purposes of changing thebr-exselection logic. Using this file to change the IP addresses of existing nodes in your cluster is not supported.Example of a machine configuration file that overrides the default interfaceapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-br-ex-override
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /var/lib/ovnk/iface_default_hint
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond0 
          filesystem: rootapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:${worker}name:12-worker-br-ex-overridespec:config:ignition:version:3.2.0storage:files:-path:/var/lib/ovnk/iface_default_hintmode:0420overwrite:truecontents:source:data:text/plain;charset=utf-8,bond01filesystem:rootCopy to ClipboardCopied!Toggle word wrapToggle overflow1Ensurebond0exists on the node before you apply the machine configuration file to the node.Before you apply the configuration to all new nodes in your cluster, reboot the host node to verify thatbr-exselects the intended interface and does not conflict with the new interfaces that you defined onbr-ex1.Apply the machine configuration file to all new nodes in your cluster:oc create -f <machine_config_file_name>$oc create-f<machine_config_file_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: You can override thebr-exselection logic for nodes by creating a machine configuration file that in turn creates a/var/lib/ovnk/iface_default_hintresource.

The resource lists the name of the interface thatbr-exselects for your cluster. By default,br-exselects the primary interface for a node based on boot order and the IP address subnet in the machine network. Certain machine network configurations might require thatbr-excontinues to select the default interfaces or bonds for a host node.

- Create a machine configuration file on the host node to override the default interface.Only create this machine configuration file for the purposes of changing thebr-exselection logic. Using this file to change the IP addresses of existing nodes in your cluster is not supported.Example of a machine configuration file that overrides the default interfaceapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-br-ex-override
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /var/lib/ovnk/iface_default_hint
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond0 
          filesystem: rootapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:${worker}name:12-worker-br-ex-overridespec:config:ignition:version:3.2.0storage:files:-path:/var/lib/ovnk/iface_default_hintmode:0420overwrite:truecontents:source:data:text/plain;charset=utf-8,bond01filesystem:rootCopy to ClipboardCopied!Toggle word wrapToggle overflow1Ensurebond0exists on the node before you apply the machine configuration file to the node.

Create a machine configuration file on the host node to override the default interface.

Only create this machine configuration file for the purposes of changing thebr-exselection logic. Using this file to change the IP addresses of existing nodes in your cluster is not supported.

Example of a machine configuration file that overrides the default interface

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-br-ex-override
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /var/lib/ovnk/iface_default_hint
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond0 
          filesystem: root
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: ${worker}
  name: 12-worker-br-ex-override
spec:
  config:
    ignition:
      version: 3.2.0
    storage:
      files:
        - path: /var/lib/ovnk/iface_default_hint
          mode: 0420
          overwrite: true
          contents:
            source: data:text/plain;charset=utf-8,bond0
```

```
filesystem: root
```

**1**
  Ensurebond0exists on the node before you apply the machine configuration file to the node.
- Before you apply the configuration to all new nodes in your cluster, reboot the host node to verify thatbr-exselects the intended interface and does not conflict with the new interfaces that you defined onbr-ex1.
- Apply the machine configuration file to all new nodes in your cluster:oc create -f <machine_config_file_name>$oc create-f<machine_config_file_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Apply the machine configuration file to all new nodes in your cluster:

Verification

- Identify the IP addresses of nodes with theexgw-ip-addresseslabel in your cluster to verify that the nodes use the additional bridge instead of the default bridge:oc get nodes -o json | grep --color exgw-ip-addresses$oc get nodes-ojson|grep--colorexgw-ip-addressesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample output"k8s.ovn.org/l3-gateway-config":
   \"exgw-ip-address\":\"172.xx.xx.yy/24\",\"next-hops\":[\"xx.xx.xx.xx\"],"k8s.ovn.org/l3-gateway-config":
   \"exgw-ip-address\":\"172.xx.xx.yy/24\",\"next-hops\":[\"xx.xx.xx.xx\"],Copy to ClipboardCopied!Toggle word wrapToggle overflow

Identify the IP addresses of nodes with theexgw-ip-addresseslabel in your cluster to verify that the nodes use the additional bridge instead of the default bridge:

Example output

```
"k8s.ovn.org/l3-gateway-config":
   \"exgw-ip-address\":\"172.xx.xx.yy/24\",\"next-hops\":[\"xx.xx.xx.xx\"],
```

```
"k8s.ovn.org/l3-gateway-config":
   \"exgw-ip-address\":\"172.xx.xx.yy/24\",\"next-hops\":[\"xx.xx.xx.xx\"],
```

- Observe that the additional bridge exists on target nodes by reviewing the network interface names on the host node:oc debug node/<node_name> -- chroot /host sh -c "ip a | grep mtu | grep br-ex"$oc debug node/<node_name>--chroot/hostsh-c"ip a | grep mtu | grep br-ex"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputStarting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
6: br-ex1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`#...5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
6: br-ex1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000Copy to ClipboardCopied!Toggle word wrapToggle overflow

Observe that the additional bridge exists on target nodes by reviewing the network interface names on the host node:

Example output

```
Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
6: br-ex1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
```

```
Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
6: br-ex1: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
```

- Optional: If you use/var/lib/ovnk/iface_default_hint, check that the MAC address ofbr-exmatches the MAC address of the primary selected interface:oc debug node/<node_name> -- chroot /host sh -c "ip a | grep -A1 -E 'br-ex|bond0'$oc debug node/<node_name>--chroot/hostsh-c"ip a | grep -A1 -E 'br-ex|bond0'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output that shows the primary interface forbr-exasbond0Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
sh-5.1# ip a | grep -A1 -E 'br-ex|bond0'
2: bond0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master ovs-system state UP group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
--
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
    inet 10.xx.xx.xx/21 brd 10.xx.xx.255 scope global dynamic noprefixroute br-exStarting pod/worker-1-debug ...
To use host binaries, run `chroot /host`#...sh-5.1# ip a | grep -A1 -E 'br-ex|bond0'
2: bond0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master ovs-system state UP group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
--
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
    inet 10.xx.xx.xx/21 brd 10.xx.xx.255 scope global dynamic noprefixroute br-exCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: If you use/var/lib/ovnk/iface_default_hint, check that the MAC address ofbr-exmatches the MAC address of the primary selected interface:

Example output that shows the primary interface forbr-exasbond0

```
Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
sh-5.1# ip a | grep -A1 -E 'br-ex|bond0'
2: bond0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master ovs-system state UP group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
--
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
    inet 10.xx.xx.xx/21 brd 10.xx.xx.255 scope global dynamic noprefixroute br-ex
```

```
Starting pod/worker-1-debug ...
To use host binaries, run `chroot /host`
# ...
sh-5.1# ip a | grep -A1 -E 'br-ex|bond0'
2: bond0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel master ovs-system state UP group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
--
5: br-ex: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UNKNOWN group default qlen 1000
    link/ether fa:16:3e:47:99:98 brd ff:ff:ff:ff:ff:ff
    inet 10.xx.xx.xx/21 brd 10.xx.xx.255 scope global dynamic noprefixroute br-ex
```

### 7.5.2. Troubleshooting Open vSwitch issuesCopy linkLink copied to clipboard!

To troubleshoot some Open vSwitch (OVS) issues, you might need to configure the log level to include more information.

If you modify the log level on a node temporarily, be aware that you can receive log messages from the machine config daemon on the node like the following example:

To avoid the log messages related to the mismatch, revert the log level change after you complete your troubleshooting.

#### 7.5.2.1. Configuring the Open vSwitch log level temporarilyCopy linkLink copied to clipboard!

For short-term troubleshooting, you can configure the Open vSwitch (OVS) log level temporarily. The following procedure does not require rebooting the node. In addition, the configuration change does not persist whenever you reboot the node.

After you perform this procedure to change the log level, you can receive log messages from the machine config daemon that indicate a content mismatch for theovs-vswitchd.service. To avoid the log messages, repeat this procedure and set the log level to the original value.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Start a debug pod for a node:oc debug node/<node_name>$oc debug node/<node_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod for a node:

- Set/hostas the root directory within the debug shell. The debug pod mounts the root file system from the host in/hostwithin the pod. By changing the root directory to/host, you can run binaries from the host file system:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflow

Set/hostas the root directory within the debug shell. The debug pod mounts the root file system from the host in/hostwithin the pod. By changing the root directory to/host, you can run binaries from the host file system:

- View the current syslog level for OVS modules:ovs-appctl vlog/list#ovs-appctl vlog/listCopy to ClipboardCopied!Toggle word wrapToggle overflowThe following example output shows the log level for syslog set toinfo.Example outputconsole    syslog    file
                 -------    ------    ------
backtrace          OFF       INFO       INFO
bfd                OFF       INFO       INFO
bond               OFF       INFO       INFO
bridge             OFF       INFO       INFO
bundle             OFF       INFO       INFO
bundles            OFF       INFO       INFO
cfm                OFF       INFO       INFO
collectors         OFF       INFO       INFO
command_line       OFF       INFO       INFO
connmgr            OFF       INFO       INFO
conntrack          OFF       INFO       INFO
conntrack_tp       OFF       INFO       INFO
coverage           OFF       INFO       INFO
ct_dpif            OFF       INFO       INFO
daemon             OFF       INFO       INFO
daemon_unix        OFF       INFO       INFO
dns_resolve        OFF       INFO       INFO
dpdk               OFF       INFO       INFO
...console    syslog    file
                 -------    ------    ------
backtrace          OFF       INFO       INFO
bfd                OFF       INFO       INFO
bond               OFF       INFO       INFO
bridge             OFF       INFO       INFO
bundle             OFF       INFO       INFO
bundles            OFF       INFO       INFO
cfm                OFF       INFO       INFO
collectors         OFF       INFO       INFO
command_line       OFF       INFO       INFO
connmgr            OFF       INFO       INFO
conntrack          OFF       INFO       INFO
conntrack_tp       OFF       INFO       INFO
coverage           OFF       INFO       INFO
ct_dpif            OFF       INFO       INFO
daemon             OFF       INFO       INFO
daemon_unix        OFF       INFO       INFO
dns_resolve        OFF       INFO       INFO
dpdk               OFF       INFO       INFO
...Copy to ClipboardCopied!Toggle word wrapToggle overflow

View the current syslog level for OVS modules:

The following example output shows the log level for syslog set toinfo.

Example output

```
console    syslog    file
                 -------    ------    ------
backtrace          OFF       INFO       INFO
bfd                OFF       INFO       INFO
bond               OFF       INFO       INFO
bridge             OFF       INFO       INFO
bundle             OFF       INFO       INFO
bundles            OFF       INFO       INFO
cfm                OFF       INFO       INFO
collectors         OFF       INFO       INFO
command_line       OFF       INFO       INFO
connmgr            OFF       INFO       INFO
conntrack          OFF       INFO       INFO
conntrack_tp       OFF       INFO       INFO
coverage           OFF       INFO       INFO
ct_dpif            OFF       INFO       INFO
daemon             OFF       INFO       INFO
daemon_unix        OFF       INFO       INFO
dns_resolve        OFF       INFO       INFO
dpdk               OFF       INFO       INFO
...
```

```
console    syslog    file
                 -------    ------    ------
backtrace          OFF       INFO       INFO
bfd                OFF       INFO       INFO
bond               OFF       INFO       INFO
bridge             OFF       INFO       INFO
bundle             OFF       INFO       INFO
bundles            OFF       INFO       INFO
cfm                OFF       INFO       INFO
collectors         OFF       INFO       INFO
command_line       OFF       INFO       INFO
connmgr            OFF       INFO       INFO
conntrack          OFF       INFO       INFO
conntrack_tp       OFF       INFO       INFO
coverage           OFF       INFO       INFO
ct_dpif            OFF       INFO       INFO
daemon             OFF       INFO       INFO
daemon_unix        OFF       INFO       INFO
dns_resolve        OFF       INFO       INFO
dpdk               OFF       INFO       INFO
...
```

- Specify the log level in the/etc/systemd/system/ovs-vswitchd.service.d/10-ovs-vswitchd-restart.conffile:Restart=always
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /var/lib/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /etc/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /run/openvswitch'
ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg
ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbgRestart=always
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /var/lib/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /etc/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /run/openvswitch'
ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg
ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbgCopy to ClipboardCopied!Toggle word wrapToggle overflowIn the preceding example, the log level is set todbg. Change the last two lines by settingsyslog:<log_level>tooff,emer,err,warn,info, ordbg. Theofflog level filters out all log messages.

Specify the log level in the/etc/systemd/system/ovs-vswitchd.service.d/10-ovs-vswitchd-restart.conffile:

```
Restart=always
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /var/lib/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /etc/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /run/openvswitch'
ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg
ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbg
```

```
Restart=always
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /var/lib/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /etc/openvswitch'
ExecStartPre=-/bin/sh -c '/usr/bin/chown -R :$${OVS_USER_ID##*:} /run/openvswitch'
ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg
ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbg
```

In the preceding example, the log level is set todbg. Change the last two lines by settingsyslog:<log_level>tooff,emer,err,warn,info, ordbg. Theofflog level filters out all log messages.

- Restart the service:systemctl daemon-reload#systemctl daemon-reloadCopy to ClipboardCopied!Toggle word wrapToggle overflowsystemctl restart ovs-vswitchd#systemctl restart ovs-vswitchdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Restart the service:

#### 7.5.2.2. Configuring the Open vSwitch log level permanentlyCopy linkLink copied to clipboard!

For long-term changes to the Open vSwitch (OVS) log level, you can change the log level permanently.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Create a file, such as99-change-ovs-loglevel.yaml, with aMachineConfigobject like the following example:apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master  
  name: 99-change-ovs-loglevel
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - dropins:
        - contents: |
            [Service]
              ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg  
              ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbg
          name: 20-ovs-vswitchd-restart.conf
        name: ovs-vswitchd.serviceapiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigmetadata:labels:machineconfiguration.openshift.io/role:master1name:99-change-ovs-loglevelspec:config:ignition:version:3.2.0systemd:units:-dropins:-contents:|[Service]
              ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg2ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbgname:20-ovs-vswitchd-restart.confname:ovs-vswitchd.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflow1After you perform this procedure to configure control plane nodes, repeat the procedure and set the role toworkerto configure worker nodes.2Set thesyslog:<log_level>value. Log levels areoff,emer,err,warn,info, ordbg. Setting the value toofffilters out all log messages.

Create a file, such as99-change-ovs-loglevel.yaml, with aMachineConfigobject like the following example:

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master  
  name: 99-change-ovs-loglevel
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - dropins:
        - contents: |
            [Service]
              ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg  
              ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbg
          name: 20-ovs-vswitchd-restart.conf
        name: ovs-vswitchd.service
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfig
metadata:
  labels:
    machineconfiguration.openshift.io/role: master
```

```
name: 99-change-ovs-loglevel
spec:
  config:
    ignition:
      version: 3.2.0
    systemd:
      units:
      - dropins:
        - contents: |
            [Service]
              ExecStartPost=-/usr/bin/ovs-appctl vlog/set syslog:dbg
```

```
ExecReload=-/usr/bin/ovs-appctl vlog/set syslog:dbg
          name: 20-ovs-vswitchd-restart.conf
        name: ovs-vswitchd.service
```

**1**
  After you perform this procedure to configure control plane nodes, repeat the procedure and set the role toworkerto configure worker nodes.

**2**
  Set thesyslog:<log_level>value. Log levels areoff,emer,err,warn,info, ordbg. Setting the value toofffilters out all log messages.
- Apply the machine config:oc apply -f 99-change-ovs-loglevel.yaml$oc apply-f99-change-ovs-loglevel.yamlCopy to ClipboardCopied!Toggle word wrapToggle overflow

Apply the machine config:

#### 7.5.2.3. Displaying Open vSwitch logsCopy linkLink copied to clipboard!

Use the following procedure to display Open vSwitch (OVS) logs.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- Run one of the following commands:Display the logs by using theoccommand from outside the cluster:oc adm node-logs <node_name> -u ovs-vswitchd$oc adm node-logs<node_name>-uovs-vswitchdCopy to ClipboardCopied!Toggle word wrapToggle overflowDisplay the logs after logging on to a node in the cluster:journalctl -b -f -u ovs-vswitchd.service#journalctl-b-f-uovs-vswitchd.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOne way to log on to a node is by using theoc debug node/<node_name>command.

Run one of the following commands:

- Display the logs by using theoccommand from outside the cluster:oc adm node-logs <node_name> -u ovs-vswitchd$oc adm node-logs<node_name>-uovs-vswitchdCopy to ClipboardCopied!Toggle word wrapToggle overflow

Display the logs by using theoccommand from outside the cluster:

- Display the logs after logging on to a node in the cluster:journalctl -b -f -u ovs-vswitchd.service#journalctl-b-f-uovs-vswitchd.serviceCopy to ClipboardCopied!Toggle word wrapToggle overflowOne way to log on to a node is by using theoc debug node/<node_name>command.

Display the logs after logging on to a node in the cluster:

One way to log on to a node is by using theoc debug node/<node_name>command.

## 7.6. Troubleshooting Operator issuesCopy linkLink copied to clipboard!

Operators are a method of packaging, deploying, and managing an OpenShift Container Platform application. They act like an extension of the software vendor’s engineering team, watching over an OpenShift Container Platform environment and using its current state to make decisions in real time. Operators are designed to handle upgrades seamlessly, react to failures automatically, and not take shortcuts, such as skipping a software backup process to save time.

OpenShift Container Platform 4.17 includes a default set of Operators that are required for proper functioning of the cluster. These default Operators are managed by the Cluster Version Operator (CVO).

As a cluster administrator, you can install application Operators from the OperatorHub using the OpenShift Container Platform web console or the CLI. You can then subscribe the Operator to one or more namespaces to make it available for developers on your cluster. Application Operators are managed by Operator Lifecycle Manager (OLM).

If you experience Operator issues, verify Operator subscription status. Check Operator pod health across the cluster and gather Operator logs for diagnosis.

### 7.6.1. Operator subscription condition typesCopy linkLink copied to clipboard!

Subscriptions can report the following condition types:

| Condition | Description |
| --- | --- |
| CatalogSourcesUnhealthy | Some or all of the catalog sources to be used in resolution are unhealthy. |
| InstallPlanMissing | An install plan for a subscription is missing. |
| InstallPlanPending | An install plan for a subscription is pending installation. |
| InstallPlanFailed | An install plan for a subscription has failed. |
| ResolutionFailed | The dependency resolution for a subscription has failed. |

CatalogSourcesUnhealthy

Some or all of the catalog sources to be used in resolution are unhealthy.

InstallPlanMissing

An install plan for a subscription is missing.

InstallPlanPending

An install plan for a subscription is pending installation.

InstallPlanFailed

An install plan for a subscription has failed.

ResolutionFailed

The dependency resolution for a subscription has failed.

Default OpenShift Container Platform cluster Operators are managed by the Cluster Version Operator (CVO) and they do not have aSubscriptionobject. Application Operators are managed by Operator Lifecycle Manager (OLM) and they have aSubscriptionobject.

### 7.6.2. Viewing Operator subscription status by using the CLICopy linkLink copied to clipboard!

You can view Operator subscription status by using the CLI.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- List Operator subscriptions:oc get subs -n <operator_namespace>$oc get subs-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

List Operator subscriptions:

- Use theoc describecommand to inspect aSubscriptionresource:oc describe sub <subscription_name> -n <operator_namespace>$oc describe sub<subscription_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Use theoc describecommand to inspect aSubscriptionresource:

- In the command output, find theConditionssection for the status of Operator subscription condition types. In the following example, theCatalogSourcesUnhealthycondition type has a status offalsebecause all available catalog sources are healthy:Example outputName:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
# ...
Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy
# ...Name:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription#...Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy#...Copy to ClipboardCopied!Toggle word wrapToggle overflow

In the command output, find theConditionssection for the status of Operator subscription condition types. In the following example, theCatalogSourcesUnhealthycondition type has a status offalsebecause all available catalog sources are healthy:

Example output

```
Name:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
# ...
Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy
# ...
```

```
Name:         cluster-logging
Namespace:    openshift-logging
Labels:       operators.coreos.com/cluster-logging.openshift-logging=
Annotations:  <none>
API Version:  operators.coreos.com/v1alpha1
Kind:         Subscription
# ...
Conditions:
   Last Transition Time:  2019-07-29T13:42:57Z
   Message:               all available catalogsources are healthy
   Reason:                AllCatalogSourcesHealthy
   Status:                False
   Type:                  CatalogSourcesUnhealthy
# ...
```

Default OpenShift Container Platform cluster Operators are managed by the Cluster Version Operator (CVO) and they do not have aSubscriptionobject. Application Operators are managed by Operator Lifecycle Manager (OLM) and they have aSubscriptionobject.

### 7.6.3. Viewing Operator catalog source status by using the CLICopy linkLink copied to clipboard!

You can view the status of an Operator catalog source by using the CLI.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- List the catalog sources in a namespace. For example, you can check theopenshift-marketplacenamespace, which is used for cluster-wide catalog sources:oc get catalogsources -n openshift-marketplace$oc get catalogsources-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-marketplace    Red Hat Marketplace   grpc   Red Hat     55m
redhat-operators      Red Hat Operators     grpc   Red Hat     55mNAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-marketplace    Red Hat Marketplace   grpc   Red Hat     55m
redhat-operators      Red Hat Operators     grpc   Red Hat     55mCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the catalog sources in a namespace. For example, you can check theopenshift-marketplacenamespace, which is used for cluster-wide catalog sources:

Example output

```
NAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-marketplace    Red Hat Marketplace   grpc   Red Hat     55m
redhat-operators      Red Hat Operators     grpc   Red Hat     55m
```

```
NAME                  DISPLAY               TYPE   PUBLISHER   AGE
certified-operators   Certified Operators   grpc   Red Hat     55m
community-operators   Community Operators   grpc   Red Hat     55m
example-catalog       Example Catalog       grpc   Example Org 2m25s
redhat-marketplace    Red Hat Marketplace   grpc   Red Hat     55m
redhat-operators      Red Hat Operators     grpc   Red Hat     55m
```

- Use theoc describecommand to get more details and status about a catalog source:oc describe catalogsource example-catalog -n openshift-marketplace$oc describe catalogsource example-catalog-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource
# ...
Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace
# ...Name:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource#...Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace#...Copy to ClipboardCopied!Toggle word wrapToggle overflowIn the preceding example output, the last observed state isTRANSIENT_FAILURE. This state indicates that there is a problem establishing a connection for the catalog source.

Use theoc describecommand to get more details and status about a catalog source:

Example output

```
Name:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource
# ...
Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace
# ...
```

```
Name:         example-catalog
Namespace:    openshift-marketplace
Labels:       <none>
Annotations:  operatorframework.io/managed-by: marketplace-operator
              target.workload.openshift.io/management: {"effect": "PreferredDuringScheduling"}
API Version:  operators.coreos.com/v1alpha1
Kind:         CatalogSource
# ...
Status:
  Connection State:
    Address:              example-catalog.openshift-marketplace.svc:50051
    Last Connect:         2021-09-09T17:07:35Z
    Last Observed State:  TRANSIENT_FAILURE
  Registry Service:
    Created At:         2021-09-09T17:05:45Z
    Port:               50051
    Protocol:           grpc
    Service Name:       example-catalog
    Service Namespace:  openshift-marketplace
# ...
```

In the preceding example output, the last observed state isTRANSIENT_FAILURE. This state indicates that there is a problem establishing a connection for the catalog source.

- List the pods in the namespace where your catalog source was created:oc get pods -n openshift-marketplace$oc get pods-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-marketplace-57p8c                1/1     Running            0          36m
redhat-operators-smxx8                  1/1     Running            0          36mNAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-marketplace-57p8c                1/1     Running            0          36m
redhat-operators-smxx8                  1/1     Running            0          36mCopy to ClipboardCopied!Toggle word wrapToggle overflowWhen a catalog source is created in a namespace, a pod for the catalog source is created in that namespace. In the preceding example output, the status for theexample-catalog-bwt8zpod isImagePullBackOff. This status indicates that there is an issue pulling the catalog source’s index image.

List the pods in the namespace where your catalog source was created:

Example output

```
NAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-marketplace-57p8c                1/1     Running            0          36m
redhat-operators-smxx8                  1/1     Running            0          36m
```

```
NAME                                    READY   STATUS             RESTARTS   AGE
certified-operators-cv9nn               1/1     Running            0          36m
community-operators-6v8lp               1/1     Running            0          36m
marketplace-operator-86bfc75f9b-jkgbc   1/1     Running            0          42m
example-catalog-bwt8z                   0/1     ImagePullBackOff   0          3m55s
redhat-marketplace-57p8c                1/1     Running            0          36m
redhat-operators-smxx8                  1/1     Running            0          36m
```

When a catalog source is created in a namespace, a pod for the catalog source is created in that namespace. In the preceding example output, the status for theexample-catalog-bwt8zpod isImagePullBackOff. This status indicates that there is an issue pulling the catalog source’s index image.

- Use theoc describecommand to inspect a pod for more detailed information:oc describe pod example-catalog-bwt8z -n openshift-marketplace$oc describe pod example-catalog-bwt8z-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputName:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/[REDACTED_PRIVATE_IP]
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [[REDACTED_PRIVATE_IP]/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePullName:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/[REDACTED_PRIVATE_IP]
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [[REDACTED_PRIVATE_IP]/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePullCopy to ClipboardCopied!Toggle word wrapToggle overflowIn the preceding example output, the error messages indicate that the catalog source’s index image is failing to pull successfully because of an authorization issue. For example, the index image might be stored in a registry that requires login credentials.

Use theoc describecommand to inspect a pod for more detailed information:

Example output

```
Name:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/[REDACTED_PRIVATE_IP]
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [[REDACTED_PRIVATE_IP]/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePull
```

```
Name:         example-catalog-bwt8z
Namespace:    openshift-marketplace
Priority:     0
Node:         ci-ln-jyryyg2-f76d1-ggdbq-worker-b-vsxjd/[REDACTED_PRIVATE_IP]
...
Events:
  Type     Reason          Age                From               Message
  ----     ------          ----               ----               -------
  Normal   Scheduled       48s                default-scheduler  Successfully assigned openshift-marketplace/example-catalog-bwt8z to ci-ln-jyryyf2-f76d1-fgdbq-worker-b-vsxjd
  Normal   AddedInterface  47s                multus             Add eth0 [[REDACTED_PRIVATE_IP]/23] from openshift-sdn
  Normal   BackOff         20s (x2 over 46s)  kubelet            Back-off pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          20s (x2 over 46s)  kubelet            Error: ImagePullBackOff
  Normal   Pulling         8s (x3 over 47s)   kubelet            Pulling image "quay.io/example-org/example-catalog:v1"
  Warning  Failed          8s (x3 over 47s)   kubelet            Failed to pull image "quay.io/example-org/example-catalog:v1": rpc error: code = Unknown desc = reading manifest v1 in quay.io/example-org/example-catalog: unauthorized: access to the requested resource is not authorized
  Warning  Failed          8s (x3 over 47s)   kubelet            Error: ErrImagePull
```

In the preceding example output, the error messages indicate that the catalog source’s index image is failing to pull successfully because of an authorization issue. For example, the index image might be stored in a registry that requires login credentials.

### 7.6.4. Querying Operator pod statusCopy linkLink copied to clipboard!

You can list Operator pods within a cluster and their status. You can also collect a detailed Operator pod summary.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- List Operators running in the cluster. The output includes Operator version, availability, and up-time information:oc get clusteroperators$oc get clusteroperatorsCopy to ClipboardCopied!Toggle word wrapToggle overflow

List Operators running in the cluster. The output includes Operator version, availability, and up-time information:

- List Operator pods running in the Operator’s namespace, plus pod status, restarts, and age:oc get pod -n <operator_namespace>$oc get pod-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

List Operator pods running in the Operator’s namespace, plus pod status, restarts, and age:

- Output a detailed Operator pod summary:oc describe pod <operator_pod_name> -n <operator_namespace>$oc describe pod<operator_pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Output a detailed Operator pod summary:

- If an Operator issue is node-specific, query Operator container status on that node.Start a debug pod for the node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowSet/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.List details about the node’s containers, including state and associated pod IDs:crictl ps#crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflowList information about a specific Operator container on the node. The following example lists information about thenetwork-operatorcontainer:crictl ps --name network-operator#crictlps--namenetwork-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflowExit from the debug shell.

If an Operator issue is node-specific, query Operator container status on that node.

- Start a debug pod for the node:oc debug node/my-node$oc debug node/my-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod for the node:

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- List details about the node’s containers, including state and associated pod IDs:crictl ps#crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflow

List details about the node’s containers, including state and associated pod IDs:

- List information about a specific Operator container on the node. The following example lists information about thenetwork-operatorcontainer:crictl ps --name network-operator#crictlps--namenetwork-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

List information about a specific Operator container on the node. The following example lists information about thenetwork-operatorcontainer:

- Exit from the debug shell.

### 7.6.5. Gathering Operator logsCopy linkLink copied to clipboard!

If you experience Operator issues, you can gather detailed diagnostic information from Operator pod logs.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).
- You have the fully qualified domain names of the control plane or control plane machines.

Procedure

- List the Operator pods that are running in the Operator’s namespace, plus the pod status, restarts, and age:oc get pods -n <operator_namespace>$oc get pods-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

List the Operator pods that are running in the Operator’s namespace, plus the pod status, restarts, and age:

- Review logs for an Operator pod:oc logs pod/<pod_name> -n <operator_namespace>$oc logs pod/<pod_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf an Operator pod has multiple containers, the preceding command will produce an error that includes the name of each container. Query logs from an individual container:oc logs pod/<operator_pod_name> -c <container_name> -n <operator_namespace>$oc logs pod/<operator_pod_name>-c<container_name>-n<operator_namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review logs for an Operator pod:

If an Operator pod has multiple containers, the preceding command will produce an error that includes the name of each container. Query logs from an individual container:

- If the API is not functional, review Operator pod and container logs on each control plane node by using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values.List pods on each control plane node:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl pods$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl podsCopy to ClipboardCopied!Toggle word wrapToggle overflowFor any Operator pods not showing aReadystatus, inspect the pod’s status in detail. Replace<operator_pod_id>with the Operator pod’s ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspectp <operator_pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspectp<operator_pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowList containers related to an Operator pod:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps --pod=<operator_pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps--pod=<operator_pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor any Operator container not showing aReadystatus, inspect the container’s status in detail. Replace<container_id>with a container ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspect <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspect<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowReview the logs for any Operator containers not showing aReadystatus. Replace<container_id>with a container ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

If the API is not functional, review Operator pod and container logs on each control plane node by using SSH instead. Replace<master-node>.<cluster_name>.<base_domain>with appropriate values.

- List pods on each control plane node:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl pods$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

List pods on each control plane node:

- For any Operator pods not showing aReadystatus, inspect the pod’s status in detail. Replace<operator_pod_id>with the Operator pod’s ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspectp <operator_pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspectp<operator_pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

For any Operator pods not showing aReadystatus, inspect the pod’s status in detail. Replace<operator_pod_id>with the Operator pod’s ID listed in the output of the preceding command:

- List containers related to an Operator pod:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl ps --pod=<operator_pod_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictlps--pod=<operator_pod_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

List containers related to an Operator pod:

- For any Operator container not showing aReadystatus, inspect the container’s status in detail. Replace<container_id>with a container ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl inspect <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl inspect<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflow

For any Operator container not showing aReadystatus, inspect the container’s status in detail. Replace<container_id>with a container ID listed in the output of the preceding command:

- Review the logs for any Operator containers not showing aReadystatus. Replace<container_id>with a container ID listed in the output of the preceding command:ssh core@<master-node>.<cluster_name>.<base_domain> sudo crictl logs -f <container_id>$sshcore@<master-node>.<cluster_name>.<base_domain>sudocrictl logs-f<container_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

Review the logs for any Operator containers not showing aReadystatus. Replace<container_id>with a container ID listed in the output of the preceding command:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. Before attempting to collect diagnostic data over SSH, review whether the data collected by runningoc adm must gatherand otheroccommands is sufficient instead. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>.

### 7.6.6. Disabling the Machine Config Operator from automatically rebootingCopy linkLink copied to clipboard!

When configuration changes are made by the Machine Config Operator (MCO), Red Hat Enterprise Linux CoreOS (RHCOS) must reboot for the changes to take effect. Whether the configuration change is automatic or manual, an RHCOS node reboots automatically unless it is paused.

- When the MCO detects any of the following changes, it applies the update without draining or rebooting the node:Changes to the SSH key in thespec.config.passwd.users.sshAuthorizedKeysparameter of a machine config.Changes to the global pull secret or pull secret in theopenshift-confignamespace.Automatic rotation of the/etc/kubernetes/kubelet-ca.crtcertificate authority (CA) by the Kubernetes API Server Operator.

When the MCO detects any of the following changes, it applies the update without draining or rebooting the node:

- Changes to the SSH key in thespec.config.passwd.users.sshAuthorizedKeysparameter of a machine config.
- Changes to the global pull secret or pull secret in theopenshift-confignamespace.
- Automatic rotation of the/etc/kubernetes/kubelet-ca.crtcertificate authority (CA) by the Kubernetes API Server Operator.
- When the MCO detects changes to the/etc/containers/registries.conffile, such as editing anImageDigestMirrorSet,ImageTagMirrorSet, orImageContentSourcePolicyobject, it drains the corresponding nodes, applies the changes, and uncordons the nodes. The node drain does not happen for the following changes:The addition of a registry with thepull-from-mirror = "digest-only"parameter set for each mirror.The addition of a mirror with thepull-from-mirror = "digest-only"parameter set in a registry.The addition of items to theunqualified-search-registrieslist.

When the MCO detects changes to the/etc/containers/registries.conffile, such as editing anImageDigestMirrorSet,ImageTagMirrorSet, orImageContentSourcePolicyobject, it drains the corresponding nodes, applies the changes, and uncordons the nodes. The node drain does not happen for the following changes:

- The addition of a registry with thepull-from-mirror = "digest-only"parameter set for each mirror.
- The addition of a mirror with thepull-from-mirror = "digest-only"parameter set in a registry.
- The addition of items to theunqualified-search-registrieslist.

To avoid unwanted disruptions, you can modify the machine config pool (MCP) to prevent automatic rebooting after the Operator makes changes to the machine config.

#### 7.6.6.1. Disabling the Machine Config Operator from automatically rebooting by using the consoleCopy linkLink copied to clipboard!

To avoid unwanted disruptions from changes made by the Machine Config Operator (MCO), you can use the OpenShift Container Platform web console to modify the machine config pool (MCP) to prevent the MCO from making any changes to nodes in that pool. This prevents any reboots that would normally be part of the MCO update process.

See secondNOTEinDisabling the Machine Config Operator from automatically rebooting.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.

Procedure

To pause or unpause automatic MCO update rebooting:

- Pause the autoreboot process:Log in to the OpenShift Container Platform web console as a user with thecluster-adminrole.ClickComputeMachineConfigPools.On theMachineConfigPoolspage, click eithermasterorworker, depending upon which nodes you want to pause rebooting for.On themasterorworkerpage, clickYAML.In the YAML, update thespec.pausedfield totrue.Sample MachineConfigPool objectapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: true 
# ...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPool# ...spec:# ...paused:true1# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Update thespec.pausedfield totrueto pause rebooting.To verify that the MCP is paused, return to theMachineConfigPoolspage.On theMachineConfigPoolspage, thePausedcolumn reportsTruefor the MCP you modified.If the MCP has pending changes while paused, theUpdatedcolumn isFalseandUpdatingisFalse. WhenUpdatedisTrueandUpdatingisFalse, there are no pending changes.If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

Pause the autoreboot process:

- Log in to the OpenShift Container Platform web console as a user with thecluster-adminrole.
- ClickComputeMachineConfigPools.
- On theMachineConfigPoolspage, click eithermasterorworker, depending upon which nodes you want to pause rebooting for.
- On themasterorworkerpage, clickYAML.
- In the YAML, update thespec.pausedfield totrue.Sample MachineConfigPool objectapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: true 
# ...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPool# ...spec:# ...paused:true1# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Update thespec.pausedfield totrueto pause rebooting.

In the YAML, update thespec.pausedfield totrue.

Sample MachineConfigPool object

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: true 
# ...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: true
```

```
# ...
```

**1**
  Update thespec.pausedfield totrueto pause rebooting.
- To verify that the MCP is paused, return to theMachineConfigPoolspage.On theMachineConfigPoolspage, thePausedcolumn reportsTruefor the MCP you modified.If the MCP has pending changes while paused, theUpdatedcolumn isFalseandUpdatingisFalse. WhenUpdatedisTrueandUpdatingisFalse, there are no pending changes.If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

To verify that the MCP is paused, return to theMachineConfigPoolspage.

On theMachineConfigPoolspage, thePausedcolumn reportsTruefor the MCP you modified.

If the MCP has pending changes while paused, theUpdatedcolumn isFalseandUpdatingisFalse. WhenUpdatedisTrueandUpdatingisFalse, there are no pending changes.

If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

- Unpause the autoreboot process:Log in to the OpenShift Container Platform web console as a user with thecluster-adminrole.ClickComputeMachineConfigPools.On theMachineConfigPoolspage, click eithermasterorworker, depending upon which nodes you want to pause rebooting for.On themasterorworkerpage, clickYAML.In the YAML, update thespec.pausedfield tofalse.Sample MachineConfigPool objectapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: false 
# ...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPool# ...spec:# ...paused:false1# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Update thespec.pausedfield tofalseto allow rebooting.By unpausing an MCP, the MCO applies all paused changes reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.To verify that the MCP is paused, return to theMachineConfigPoolspage.On theMachineConfigPoolspage, thePausedcolumn reportsFalsefor the MCP you modified.If the MCP is applying any pending changes, theUpdatedcolumn isFalseand theUpdatingcolumn isTrue. WhenUpdatedisTrueandUpdatingisFalse, there are no further changes being made.

Unpause the autoreboot process:

- Log in to the OpenShift Container Platform web console as a user with thecluster-adminrole.
- ClickComputeMachineConfigPools.
- On theMachineConfigPoolspage, click eithermasterorworker, depending upon which nodes you want to pause rebooting for.
- On themasterorworkerpage, clickYAML.
- In the YAML, update thespec.pausedfield tofalse.Sample MachineConfigPool objectapiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: false 
# ...apiVersion:machineconfiguration.openshift.io/v1kind:MachineConfigPool# ...spec:# ...paused:false1# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow1Update thespec.pausedfield tofalseto allow rebooting.By unpausing an MCP, the MCO applies all paused changes reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.

In the YAML, update thespec.pausedfield tofalse.

Sample MachineConfigPool object

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: false 
# ...
```

```
apiVersion: machineconfiguration.openshift.io/v1
kind: MachineConfigPool
# ...
spec:
# ...
  paused: false
```

```
# ...
```

**1**
  Update thespec.pausedfield tofalseto allow rebooting.

By unpausing an MCP, the MCO applies all paused changes reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.

- To verify that the MCP is paused, return to theMachineConfigPoolspage.On theMachineConfigPoolspage, thePausedcolumn reportsFalsefor the MCP you modified.If the MCP is applying any pending changes, theUpdatedcolumn isFalseand theUpdatingcolumn isTrue. WhenUpdatedisTrueandUpdatingisFalse, there are no further changes being made.

To verify that the MCP is paused, return to theMachineConfigPoolspage.

On theMachineConfigPoolspage, thePausedcolumn reportsFalsefor the MCP you modified.

If the MCP is applying any pending changes, theUpdatedcolumn isFalseand theUpdatingcolumn isTrue. WhenUpdatedisTrueandUpdatingisFalse, there are no further changes being made.

#### 7.6.6.2. Disabling the Machine Config Operator from automatically rebooting by using the CLICopy linkLink copied to clipboard!

To avoid unwanted disruptions from changes made by the Machine Config Operator (MCO), you can modify the machine config pool (MCP) using the OpenShift CLI (oc) to prevent the MCO from making any changes to nodes in that pool. This prevents any reboots that would normally be part of the MCO update process.

See secondNOTEinDisabling the Machine Config Operator from automatically rebooting.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

To pause or unpause automatic MCO update rebooting:

- Pause the autoreboot process:Update theMachineConfigPoolcustom resource to set thespec.pausedfield totrue.Control plane (master) nodesoc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/master$oc patch--type=merge--patch='{"spec":{"paused":true}}'machineconfigpool/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/worker$oc patch--type=merge--patch='{"spec":{"paused":true}}'machineconfigpool/workerCopy to ClipboardCopied!Toggle word wrapToggle overflowVerify that the MCP is paused:Control plane (master) nodesoc get machineconfigpool/master --template='{{.spec.paused}}'$oc get machineconfigpool/master--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc get machineconfigpool/worker --template='{{.spec.paused}}'$oc get machineconfigpool/worker--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputtruetrueCopy to ClipboardCopied!Toggle word wrapToggle overflowThespec.pausedfield istrueand the MCP is paused.Determine if the MCP has pending changes:oc get machineconfigpool#oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     FalseNAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     FalseCopy to ClipboardCopied!Toggle word wrapToggle overflowIf theUPDATEDcolumn isFalseandUPDATINGisFalse, there are pending changes. WhenUPDATEDisTrueandUPDATINGisFalse, there are no pending changes. In the previous example, the worker node has pending changes. The control plane node does not have any pending changes.If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

Pause the autoreboot process:

- Update theMachineConfigPoolcustom resource to set thespec.pausedfield totrue.Control plane (master) nodesoc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/master$oc patch--type=merge--patch='{"spec":{"paused":true}}'machineconfigpool/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc patch --type=merge --patch='{"spec":{"paused":true}}' machineconfigpool/worker$oc patch--type=merge--patch='{"spec":{"paused":true}}'machineconfigpool/workerCopy to ClipboardCopied!Toggle word wrapToggle overflow

Update theMachineConfigPoolcustom resource to set thespec.pausedfield totrue.

Control plane (master) nodes

Worker nodes

- Verify that the MCP is paused:Control plane (master) nodesoc get machineconfigpool/master --template='{{.spec.paused}}'$oc get machineconfigpool/master--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc get machineconfigpool/worker --template='{{.spec.paused}}'$oc get machineconfigpool/worker--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputtruetrueCopy to ClipboardCopied!Toggle word wrapToggle overflowThespec.pausedfield istrueand the MCP is paused.

Verify that the MCP is paused:

Control plane (master) nodes

Worker nodes

Example output

Thespec.pausedfield istrueand the MCP is paused.

- Determine if the MCP has pending changes:oc get machineconfigpool#oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     FalseNAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     FalseCopy to ClipboardCopied!Toggle word wrapToggle overflowIf theUPDATEDcolumn isFalseandUPDATINGisFalse, there are pending changes. WhenUPDATEDisTrueandUPDATINGisFalse, there are no pending changes. In the previous example, the worker node has pending changes. The control plane node does not have any pending changes.If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

Determine if the MCP has pending changes:

Example output

```
NAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     False
```

```
NAME     CONFIG                                             UPDATED   UPDATING
master   rendered-master-33cf0a1254318755d7b48002c597bf91   True      False
worker   rendered-worker-e405a5bdb0db1295acea08bcca33fa60   False     False
```

If theUPDATEDcolumn isFalseandUPDATINGisFalse, there are pending changes. WhenUPDATEDisTrueandUPDATINGisFalse, there are no pending changes. In the previous example, the worker node has pending changes. The control plane node does not have any pending changes.

If there are pending changes (where both theUpdatedandUpdatingcolumns areFalse), it is recommended to schedule a maintenance window for a reboot as early as possible. Use the following steps for unpausing the autoreboot process to apply the changes that were queued since the last reboot.

- Unpause the autoreboot process:Update theMachineConfigPoolcustom resource to set thespec.pausedfield tofalse.Control plane (master) nodesoc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/master$oc patch--type=merge--patch='{"spec":{"paused":false}}'machineconfigpool/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/worker$oc patch--type=merge--patch='{"spec":{"paused":false}}'machineconfigpool/workerCopy to ClipboardCopied!Toggle word wrapToggle overflowBy unpausing an MCP, the MCO applies all paused changes and reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.Verify that the MCP is unpaused:Control plane (master) nodesoc get machineconfigpool/master --template='{{.spec.paused}}'$oc get machineconfigpool/master--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc get machineconfigpool/worker --template='{{.spec.paused}}'$oc get machineconfigpool/worker--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputfalsefalseCopy to ClipboardCopied!Toggle word wrapToggle overflowThespec.pausedfield isfalseand the MCP is unpaused.Determine if the MCP has pending changes:oc get machineconfigpool$oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    TrueNAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    TrueCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the MCP is applying any pending changes, theUPDATEDcolumn isFalseand theUPDATINGcolumn isTrue. WhenUPDATEDisTrueandUPDATINGisFalse, there are no further changes being made. In the previous example, the MCO is updating the worker node.

Unpause the autoreboot process:

- Update theMachineConfigPoolcustom resource to set thespec.pausedfield tofalse.Control plane (master) nodesoc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/master$oc patch--type=merge--patch='{"spec":{"paused":false}}'machineconfigpool/masterCopy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc patch --type=merge --patch='{"spec":{"paused":false}}' machineconfigpool/worker$oc patch--type=merge--patch='{"spec":{"paused":false}}'machineconfigpool/workerCopy to ClipboardCopied!Toggle word wrapToggle overflowBy unpausing an MCP, the MCO applies all paused changes and reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.

Update theMachineConfigPoolcustom resource to set thespec.pausedfield tofalse.

Control plane (master) nodes

Worker nodes

By unpausing an MCP, the MCO applies all paused changes and reboots Red Hat Enterprise Linux CoreOS (RHCOS) as needed.

- Verify that the MCP is unpaused:Control plane (master) nodesoc get machineconfigpool/master --template='{{.spec.paused}}'$oc get machineconfigpool/master--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowWorker nodesoc get machineconfigpool/worker --template='{{.spec.paused}}'$oc get machineconfigpool/worker--template='{{.spec.paused}}'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputfalsefalseCopy to ClipboardCopied!Toggle word wrapToggle overflowThespec.pausedfield isfalseand the MCP is unpaused.

Verify that the MCP is unpaused:

Control plane (master) nodes

Worker nodes

Example output

Thespec.pausedfield isfalseand the MCP is unpaused.

- Determine if the MCP has pending changes:oc get machineconfigpool$oc get machineconfigpoolCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    TrueNAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    TrueCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the MCP is applying any pending changes, theUPDATEDcolumn isFalseand theUPDATINGcolumn isTrue. WhenUPDATEDisTrueandUPDATINGisFalse, there are no further changes being made. In the previous example, the MCO is updating the worker node.

Determine if the MCP has pending changes:

Example output

```
NAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    True
```

```
NAME     CONFIG                                   UPDATED  UPDATING
master   rendered-master-546383f80705bd5aeaba93   True     False
worker   rendered-worker-b4c51bb33ccaae6fc4a6a5   False    True
```

If the MCP is applying any pending changes, theUPDATEDcolumn isFalseand theUPDATINGcolumn isTrue. WhenUPDATEDisTrueandUPDATINGisFalse, there are no further changes being made. In the previous example, the MCO is updating the worker node.

### 7.6.7. Refreshing failing subscriptionsCopy linkLink copied to clipboard!

In Operator Lifecycle Manager (OLM), if you subscribe to an Operator that references images that are not accessible on your network, you can find jobs in theopenshift-marketplacenamespace that are failing with the following errors:

Example output

```
ImagePullBackOff for
Back-off pulling image "example.com/openshift4/ose-elasticsearch-operator-bundle@sha256:6d2587129c846ec28d384540322b40b05833e7e00b25cca584e004af9a1d292e"
```

```
ImagePullBackOff for
Back-off pulling image "example.com/openshift4/ose-elasticsearch-operator-bundle@sha256:6d2587129c846ec28d384540322b40b05833e7e00b25cca584e004af9a1d292e"
```

Example output

As a result, the subscription is stuck in this failing state and the Operator is unable to install or upgrade.

You can refresh a failing subscription by deleting the subscription, cluster service version (CSV), and other related objects. After recreating the subscription, OLM then reinstalls the correct version of the Operator.

Prerequisites

- You have a failing subscription that is unable to pull an inaccessible bundle image.
- You have confirmed that the correct bundle image is accessible.

Procedure

- Get the names of theSubscriptionandClusterServiceVersionobjects from the namespace where the Operator is installed:oc get sub,csv -n <namespace>$oc get sub,csv-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              SucceededNAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              SucceededCopy to ClipboardCopied!Toggle word wrapToggle overflow

Get the names of theSubscriptionandClusterServiceVersionobjects from the namespace where the Operator is installed:

Example output

```
NAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              Succeeded
```

```
NAME                                                       PACKAGE                  SOURCE             CHANNEL
subscription.operators.coreos.com/elasticsearch-operator   elasticsearch-operator   redhat-operators   5.0

NAME                                                                         DISPLAY                            VERSION    REPLACES   PHASE
clusterserviceversion.operators.coreos.com/elasticsearch-operator.5.0.0-65   OpenShift Elasticsearch Operator   5.0.0-65              Succeeded
```

- Delete the subscription:oc delete subscription <subscription_name> -n <namespace>$oc delete subscription<subscription_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Delete the subscription:

- Delete the cluster service version:oc delete csv <csv_name> -n <namespace>$oc delete csv<csv_name>-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Delete the cluster service version:

- Get the names of any failing jobs and related config maps in theopenshift-marketplacenamespace:oc get job,configmap -n openshift-marketplace$oc get job,configmap-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30sNAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30sCopy to ClipboardCopied!Toggle word wrapToggle overflow

Get the names of any failing jobs and related config maps in theopenshift-marketplacenamespace:

Example output

```
NAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30s
```

```
NAME                                                                        COMPLETIONS   DURATION   AGE
job.batch/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   1/1           26s        9m30s

NAME                                                                        DATA   AGE
configmap/1de9443b6324e629ddf31fed0a853a121275806170e34c926d69e53a7fcbccb   3      9m30s
```

- Delete the job:oc delete job <job_name> -n openshift-marketplace$oc delete job<job_name>-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflowThis ensures pods that try to pull the inaccessible image are not recreated.

Delete the job:

This ensures pods that try to pull the inaccessible image are not recreated.

- Delete the config map:oc delete configmap <configmap_name> -n openshift-marketplace$oc delete configmap<configmap_name>-nopenshift-marketplaceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Delete the config map:

- Reinstall the Operator using OperatorHub in the web console.

Verification

- Check that the Operator has been reinstalled successfully:oc get sub,csv,installplan -n <namespace>$oc get sub,csv,installplan-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check that the Operator has been reinstalled successfully:

### 7.6.8. Reinstalling Operators after failed uninstallationCopy linkLink copied to clipboard!

You must successfully and completely uninstall an Operator prior to attempting to reinstall the same Operator. Failure to fully uninstall the Operator properly can leave resources, such as a project or namespace, stuck in a "Terminating" state and cause "error resolving resource" messages. For example:

ExampleProjectresource description

```
...
    message: 'Failed to delete all resource types, 1 remaining: Internal error occurred:
      error resolving resource'
...
```

```
...
    message: 'Failed to delete all resource types, 1 remaining: Internal error occurred:
      error resolving resource'
...
```

These types of issues can prevent an Operator from being reinstalled successfully.

Forced deletion of a namespace is not likely to resolve "Terminating" state issues and can lead to unstable or unpredictable cluster behavior, so it is better to try to find related resources that might be preventing the namespace from being deleted. For more information, see theRed Hat Knowledgebase Solution #4165791, paying careful attention to the cautions and warnings.

The following procedure shows how to troubleshoot when an Operator cannot be reinstalled because an existing custom resource definition (CRD) from a previous installation of the Operator is preventing a related namespace from deleting successfully.

Procedure

- Check if there are any namespaces related to the Operator that are stuck in "Terminating" state:oc get namespaces$oc get namespacesCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputoperator-ns-1                                       Terminatingoperator-ns-1                                       TerminatingCopy to ClipboardCopied!Toggle word wrapToggle overflow

Check if there are any namespaces related to the Operator that are stuck in "Terminating" state:

Example output

- Check if there are any CRDs related to the Operator that are still present after the failed uninstallation:oc get crds$oc get crdsCopy to ClipboardCopied!Toggle word wrapToggle overflowCRDs are global cluster definitions; the actual custom resource (CR) instances related to the CRDs could be in other namespaces or be global cluster instances.

Check if there are any CRDs related to the Operator that are still present after the failed uninstallation:

CRDs are global cluster definitions; the actual custom resource (CR) instances related to the CRDs could be in other namespaces or be global cluster instances.

- If there are any CRDs that you know were provided or managed by the Operator and that should have been deleted after uninstallation, delete the CRD:oc delete crd <crd_name>$oc delete crd<crd_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

If there are any CRDs that you know were provided or managed by the Operator and that should have been deleted after uninstallation, delete the CRD:

- Check if there are any remaining CR instances related to the Operator that are still present after uninstallation, and if so, delete the CRs:The type of CRs to search for can be difficult to determine after uninstallation and can require knowing what CRDs the Operator manages. For example, if you are troubleshooting an uninstallation of the etcd Operator, which provides theEtcdClusterCRD, you can search for remainingEtcdClusterCRs in a namespace:oc get EtcdCluster -n <namespace_name>$oc get EtcdCluster-n<namespace_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can search across all namespaces:oc get EtcdCluster --all-namespaces$oc get EtcdCluster --all-namespacesCopy to ClipboardCopied!Toggle word wrapToggle overflowIf there are any remaining CRs that should be removed, delete the instances:oc delete <cr_name> <cr_instance_name> -n <namespace_name>$oc delete<cr_name><cr_instance_name>-n<namespace_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check if there are any remaining CR instances related to the Operator that are still present after uninstallation, and if so, delete the CRs:

- The type of CRs to search for can be difficult to determine after uninstallation and can require knowing what CRDs the Operator manages. For example, if you are troubleshooting an uninstallation of the etcd Operator, which provides theEtcdClusterCRD, you can search for remainingEtcdClusterCRs in a namespace:oc get EtcdCluster -n <namespace_name>$oc get EtcdCluster-n<namespace_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can search across all namespaces:oc get EtcdCluster --all-namespaces$oc get EtcdCluster --all-namespacesCopy to ClipboardCopied!Toggle word wrapToggle overflow

The type of CRs to search for can be difficult to determine after uninstallation and can require knowing what CRDs the Operator manages. For example, if you are troubleshooting an uninstallation of the etcd Operator, which provides theEtcdClusterCRD, you can search for remainingEtcdClusterCRs in a namespace:

Alternatively, you can search across all namespaces:

- If there are any remaining CRs that should be removed, delete the instances:oc delete <cr_name> <cr_instance_name> -n <namespace_name>$oc delete<cr_name><cr_instance_name>-n<namespace_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

If there are any remaining CRs that should be removed, delete the instances:

- Check that the namespace deletion has successfully resolved:oc get namespace <namespace_name>$oc get namespace<namespace_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the namespace or other Operator resources are still not uninstalled cleanly, contact Red Hat Support.

Check that the namespace deletion has successfully resolved:

If the namespace or other Operator resources are still not uninstalled cleanly, contact Red Hat Support.

- Reinstall the Operator using OperatorHub in the web console.

Verification

- Check that the Operator has been reinstalled successfully:oc get sub,csv,installplan -n <namespace>$oc get sub,csv,installplan-n<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Check that the Operator has been reinstalled successfully:

## 7.7. Investigating pod issuesCopy linkLink copied to clipboard!

OpenShift Container Platform leverages the Kubernetes concept of a pod, which is one or more containers deployed together on one host. A pod is the smallest compute unit that can be defined, deployed, and managed on OpenShift Container Platform 4.17.

After a pod is defined, it is assigned to run on a node until its containers exit, or until it is removed. Depending on policy and exit code, pods are either removed after exiting or retained so that their logs can be accessed.

The first thing to check when pod issues arise is the pod’s status. If an explicit pod failure has occurred, observe the pod’s error state to identify specific image, container, or pod network issues. Focus diagnostic data collection according to the error state. Review pod event messages, as well as pod and container log information. Diagnose issues dynamically by accessing running Pods on the command line, or start a debug pod with root access based on a problematic pod’s deployment configuration.

### 7.7.1. Understanding pod error statesCopy linkLink copied to clipboard!

Pod failures return explicit error states that can be observed in thestatusfield in the output ofoc get pods. Pod error states cover image, container, and container network related failures.

The following table provides a list of pod error states along with their descriptions.

| Pod error state | Description |
| --- | --- |
| ErrImagePull | Generic image retrieval error. |
| ErrImagePullBackOff | Image retrieval failed and is backed off. |
| ErrInvalidImageName | The specified image name was invalid. |
| ErrImageInspect | Image inspection did not succeed. |
| ErrImageNeverPull | PullPolicyis set toNeverPullImageand the target image is not present locally on the host. |
| ErrRegistryUnavailable | When attempting to retrieve an image from a registry, an HTTP error was encountered. |
| ErrContainerNotFound | The specified container is either not present or not managed by the kubelet, within the declared pod |
| ErrRunInitContainer | Container initialization failed. |
| ErrRunContainer | None of the pod’s containers started successfully. |
| ErrKillContainer | None of the pod’s containers were killed successfully. |
| ErrCrashLoopBackOff | A container has terminated. The kubelet will not attempt to restart it. |
| ErrVerifyNonRoot | A container or image attempted to run with root privileges. |
| ErrCreatePodSandbox | Pod sandbox creation did not succeed. |
| ErrConfigPodSandbox | Pod sandbox configuration was not obtained. |
| ErrKillPodSandbox | A pod sandbox did not stop successfully. |
| ErrSetupNetwork | Network initialization failed. |
| ErrTeardownNetwork | Network termination failed. |

ErrImagePull

Generic image retrieval error.

ErrImagePullBackOff

Image retrieval failed and is backed off.

ErrInvalidImageName

The specified image name was invalid.

ErrImageInspect

Image inspection did not succeed.

ErrImageNeverPull

PullPolicyis set toNeverPullImageand the target image is not present locally on the host.

ErrRegistryUnavailable

When attempting to retrieve an image from a registry, an HTTP error was encountered.

ErrContainerNotFound

The specified container is either not present or not managed by the kubelet, within the declared pod.

ErrRunInitContainer

Container initialization failed.

ErrRunContainer

None of the pod’s containers started successfully.

ErrKillContainer

None of the pod’s containers were killed successfully.

ErrCrashLoopBackOff

A container has terminated. The kubelet will not attempt to restart it.

ErrVerifyNonRoot

A container or image attempted to run with root privileges.

ErrCreatePodSandbox

Pod sandbox creation did not succeed.

ErrConfigPodSandbox

Pod sandbox configuration was not obtained.

ErrKillPodSandbox

A pod sandbox did not stop successfully.

ErrSetupNetwork

Network initialization failed.

ErrTeardownNetwork

Network termination failed.

### 7.7.2. Reviewing pod statusCopy linkLink copied to clipboard!

You can query pod status and error states. You can also query a pod’s associated deployment configuration and review base image availability.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- skopeois installed.

Procedure

- Switch into a project:oc project <project_name>$oc project<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Switch into a project:

- List pods running within the namespace, as well as pod status, error states, restarts, and age:oc get pods$oc get podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

List pods running within the namespace, as well as pod status, error states, restarts, and age:

- Determine whether the namespace is managed by a deployment configuration:oc status$oc statusCopy to ClipboardCopied!Toggle word wrapToggle overflowIf the namespace is managed by a deployment configuration, the output includes the deployment configuration name and a base image reference.

Determine whether the namespace is managed by a deployment configuration:

If the namespace is managed by a deployment configuration, the output includes the deployment configuration name and a base image reference.

- Inspect the base image referenced in the preceding command’s output:skopeo inspect docker://<image_reference>$skopeo inspect docker://<image_reference>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect the base image referenced in the preceding command’s output:

- If the base image reference is not correct, update the reference in the deployment configuration:oc edit deployment/my-deployment$oc edit deployment/my-deploymentCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the base image reference is not correct, update the reference in the deployment configuration:

- When deployment configuration changes on exit, the configuration will automatically redeploy. Watch pod status as the deployment progresses, to determine whether the issue has been resolved:oc get pods -w$oc get pods-wCopy to ClipboardCopied!Toggle word wrapToggle overflow

When deployment configuration changes on exit, the configuration will automatically redeploy. Watch pod status as the deployment progresses, to determine whether the issue has been resolved:

- Review events within the namespace for diagnostic information relating to pod failures:oc get events$oc get eventsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review events within the namespace for diagnostic information relating to pod failures:

### 7.7.3. Inspecting pod and container logsCopy linkLink copied to clipboard!

You can inspect pod and container logs for warnings and error messages related to explicit pod failures. Depending on policy and exit code, pod and container logs remain available after pods have been terminated.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- Query logs for a specific pod:oc logs <pod_name>$oc logs<pod_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Query logs for a specific pod:

- Query logs for a specific container within a pod:oc logs <pod_name> -c <container_name>$oc logs<pod_name>-c<container_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowLogs retrieved using the precedingoc logscommands are composed of messages sent to stdout within pods or containers.

Query logs for a specific container within a pod:

Logs retrieved using the precedingoc logscommands are composed of messages sent to stdout within pods or containers.

- Inspect logs contained in/var/log/within a pod.List log files and subdirectories contained in/var/logwithin a pod:oc exec <pod_name>  -- ls -alh /var/log$ocexec<pod_name>--ls-alh/var/logCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputtotal 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmptotal 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmpCopy to ClipboardCopied!Toggle word wrapToggle overflowQuery a specific log file contained in/var/logwithin a pod:oc exec <pod_name> cat /var/log/<path_to_log>$ocexec<pod_name>cat/var/log/<path_to_log>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFO2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFOCopy to ClipboardCopied!Toggle word wrapToggle overflowList log files and subdirectories contained in/var/logwithin a specific container:oc exec <pod_name> -c <container_name> ls /var/log$ocexec<pod_name>-c<container_name>ls/var/logCopy to ClipboardCopied!Toggle word wrapToggle overflowQuery a specific log file contained in/var/logwithin a specific container:oc exec <pod_name> -c <container_name> cat /var/log/<path_to_log>$ocexec<pod_name>-c<container_name>cat/var/log/<path_to_log>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect logs contained in/var/log/within a pod.

- List log files and subdirectories contained in/var/logwithin a pod:oc exec <pod_name>  -- ls -alh /var/log$ocexec<pod_name>--ls-alh/var/logCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputtotal 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmptotal 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmpCopy to ClipboardCopied!Toggle word wrapToggle overflow

List log files and subdirectories contained in/var/logwithin a pod:

Example output

```
total 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmp
```

```
total 124K
drwxr-xr-x. 1 root root   33 Aug 11 11:23 .
drwxr-xr-x. 1 root root   28 Sep  6  2022 ..
-rw-rw----. 1 root utmp    0 Jul 10 10:31 btmp
-rw-r--r--. 1 root root  33K Jul 17 10:07 dnf.librepo.log
-rw-r--r--. 1 root root  69K Jul 17 10:07 dnf.log
-rw-r--r--. 1 root root 8.8K Jul 17 10:07 dnf.rpm.log
-rw-r--r--. 1 root root  480 Jul 17 10:07 hawkey.log
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 lastlog
drwx------. 2 root root   23 Aug 11 11:14 openshift-apiserver
drwx------. 2 root root    6 Jul 10 10:31 private
drwxr-xr-x. 1 root root   22 Mar  9 08:05 rhsm
-rw-rw-r--. 1 root utmp    0 Jul 10 10:31 wtmp
```

- Query a specific log file contained in/var/logwithin a pod:oc exec <pod_name> cat /var/log/<path_to_log>$ocexec<pod_name>cat/var/log/<path_to_log>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFO2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFOCopy to ClipboardCopied!Toggle word wrapToggle overflow

Query a specific log file contained in/var/logwithin a pod:

Example output

```
2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFO
```

```
2023-07-10T10:29:38+0000 INFO --- logging initialized ---
2023-07-10T10:29:38+0000 DDEBUG timer: config: 13 ms
2023-07-10T10:29:38+0000 DEBUG Loaded plugins: builddep, changelog, config-manager, copr, debug, debuginfo-install, download, generate_completion_cache, groups-manager, needs-restarting, playground, product-id, repoclosure, repodiff, repograph, repomanage, reposync, subscription-manager, uploadprofile
2023-07-10T10:29:38+0000 INFO Updating Subscription Management repositories.
2023-07-10T10:29:38+0000 INFO Unable to read consumer identity
2023-07-10T10:29:38+0000 INFO Subscription Manager is operating in container mode.
2023-07-10T10:29:38+0000 INFO
```

- List log files and subdirectories contained in/var/logwithin a specific container:oc exec <pod_name> -c <container_name> ls /var/log$ocexec<pod_name>-c<container_name>ls/var/logCopy to ClipboardCopied!Toggle word wrapToggle overflow

List log files and subdirectories contained in/var/logwithin a specific container:

- Query a specific log file contained in/var/logwithin a specific container:oc exec <pod_name> -c <container_name> cat /var/log/<path_to_log>$ocexec<pod_name>-c<container_name>cat/var/log/<path_to_log>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Query a specific log file contained in/var/logwithin a specific container:

### 7.7.4. Accessing running podsCopy linkLink copied to clipboard!

You can review running pods dynamically by opening a shell inside a pod or by gaining network access through port forwarding.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- Switch into the project that contains the pod you would like to access. This is necessary because theoc rshcommand does not accept the-nnamespace option:oc project <namespace>$oc project<namespace>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Switch into the project that contains the pod you would like to access. This is necessary because theoc rshcommand does not accept the-nnamespace option:

- Start a remote shell into a pod:oc rsh <pod_name>$oc rsh<pod_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1If a pod has multiple containers,oc rshdefaults to the first container unless-c <container_name>is specified.

Start a remote shell into a pod:

**1**
  If a pod has multiple containers,oc rshdefaults to the first container unless-c <container_name>is specified.
- Start a remote shell into a specific container within a pod:oc rsh -c <container_name> pod/<pod_name>$oc rsh-c<container_name>pod/<pod_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a remote shell into a specific container within a pod:

- Create a port forwarding session to a port on a pod:oc port-forward <pod_name> <host_port>:<pod_port>$oc port-forward<pod_name><host_port>:<pod_port>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1EnterCtrl+Cto cancel the port forwarding session.

Create a port forwarding session to a port on a pod:

**1**
  EnterCtrl+Cto cancel the port forwarding session.

### 7.7.5. Starting debug pods with root accessCopy linkLink copied to clipboard!

You can start a debug pod with root access, based on a problematic pod’s deployment or deployment configuration. Pod users typically run with non-root privileges, but running troubleshooting pods with temporary root privileges can be useful during issue investigation.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- Start a debug pod with root access, based on a deployment.Obtain a project’s deployment name:oc get deployment -n <project_name>$oc get deployment-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowStart a debug pod with root privileges, based on the deployment:oc debug deployment/my-deployment --as-root -n <project_name>$oc debug deployment/my-deployment --as-root-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod with root access, based on a deployment.

- Obtain a project’s deployment name:oc get deployment -n <project_name>$oc get deployment-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a project’s deployment name:

- Start a debug pod with root privileges, based on the deployment:oc debug deployment/my-deployment --as-root -n <project_name>$oc debug deployment/my-deployment --as-root-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod with root privileges, based on the deployment:

- Start a debug pod with root access, based on a deployment configuration.Obtain a project’s deployment configuration name:oc get deploymentconfigs -n <project_name>$oc get deploymentconfigs-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowStart a debug pod with root privileges, based on the deployment configuration:oc debug deploymentconfig/my-deployment-configuration --as-root -n <project_name>$oc debug deploymentconfig/my-deployment-configuration --as-root-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod with root access, based on a deployment configuration.

- Obtain a project’s deployment configuration name:oc get deploymentconfigs -n <project_name>$oc get deploymentconfigs-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain a project’s deployment configuration name:

- Start a debug pod with root privileges, based on the deployment configuration:oc debug deploymentconfig/my-deployment-configuration --as-root -n <project_name>$oc debug deploymentconfig/my-deployment-configuration --as-root-n<project_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Start a debug pod with root privileges, based on the deployment configuration:

You can append-- <command>to the precedingoc debugcommands to run individual commands within a debug pod, instead of running an interactive shell.

### 7.7.6. Copying files to and from pods and containersCopy linkLink copied to clipboard!

You can copy files to and from a pod to test configuration changes or gather diagnostic information.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- Copy a file to a pod:oc cp <local_path> <pod_name>:/<path> -c <container_name>$occp<local_path><pod_name>:/<path>-c<container_name>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The first container in a pod is selected if the-coption is not specified.

Copy a file to a pod:

**1**
  The first container in a pod is selected if the-coption is not specified.
- Copy a file from a pod:oc cp <pod_name>:/<path>  -c <container_name> <local_path>$occp<pod_name>:/<path>-c<container_name><local_path>1Copy to ClipboardCopied!Toggle word wrapToggle overflow1The first container in a pod is selected if the-coption is not specified.Foroc cpto function, thetarbinary must be available within the container.

Copy a file from a pod:

**1**
  The first container in a pod is selected if the-coption is not specified.

Foroc cpto function, thetarbinary must be available within the container.

## 7.8. Troubleshooting the Source-to-Image processCopy linkLink copied to clipboard!

### 7.8.1. Strategies for Source-to-Image troubleshootingCopy linkLink copied to clipboard!

Use Source-to-Image (S2I) to build reproducible, Docker-formatted container images. You can create ready-to-run images by injecting application source code into a container image and assembling a new image. The new image incorporates the base image (the builder) and built source.

Procedure

- To determine where in the S2I process a failure occurs, you can observe the state of the pods relating to each of the following S2I stages:During the build configuration stage, a build pod is used to create an application container image from a base image and application source code.During the deployment configuration stage, a deployment pod is used to deploy application pods from the application container image that was built in the build configuration stage. The deployment pod also deploys other resources such as services and routes. The deployment configuration begins after the build configuration succeeds.After the deployment pod has started the application pods, application failures can occur within the running application pods. For instance, an application might not behave as expected even though the application pods are in aRunningstate. In this scenario, you can access running application pods to investigate application failures within a pod.

To determine where in the S2I process a failure occurs, you can observe the state of the pods relating to each of the following S2I stages:

- During the build configuration stage, a build pod is used to create an application container image from a base image and application source code.
- During the deployment configuration stage, a deployment pod is used to deploy application pods from the application container image that was built in the build configuration stage. The deployment pod also deploys other resources such as services and routes. The deployment configuration begins after the build configuration succeeds.
- After the deployment pod has started the application pods, application failures can occur within the running application pods. For instance, an application might not behave as expected even though the application pods are in aRunningstate. In this scenario, you can access running application pods to investigate application failures within a pod.
- When troubleshooting S2I issues, follow this strategy:Monitor build, deployment, and application pod status.Determine the stage of the S2I process where the problem occurred.Review logs corresponding to the failed stage.

When troubleshooting S2I issues, follow this strategy:

- Monitor build, deployment, and application pod status.
- Determine the stage of the S2I process where the problem occurred.
- Review logs corresponding to the failed stage.

### 7.8.2. Gathering Source-to-Image diagnostic dataCopy linkLink copied to clipboard!

The S2I tool runs a build pod and a deployment pod in sequence. The deployment pod is responsible for deploying the application pods based on the application container image created in the build stage. Watch build, deployment and application pod status to determine where in the S2I process a failure occurs. Then, focus diagnostic data collection accordingly.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- Your API service is still functional.
- You have installed the OpenShift CLI (oc).

Procedure

- Watch the pod status throughout the S2I process to determine at which stage a failure occurs:oc get pods -w$oc get pods-w1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Use-wto monitor pods for changes until you quit the command usingCtrl+C.

Watch the pod status throughout the S2I process to determine at which stage a failure occurs:

**1**
  Use-wto monitor pods for changes until you quit the command usingCtrl+C.
- Review a failed pod’s logs for errors.If the build pod fails, review the build pod’s logs:oc logs -f pod/<application_name>-<build_number>-build$oc logs-fpod/<application_name>-<build_number>-buildCopy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can review the build configuration’s logs usingoc logs -f bc/<application_name>. The build configuration’s logs include the logs from the build pod.If the deployment pod fails, review the deployment pod’s logs:oc logs -f pod/<application_name>-<build_number>-deploy$oc logs-fpod/<application_name>-<build_number>-deployCopy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can review the deployment configuration’s logs usingoc logs -f dc/<application_name>. This outputs logs from the deployment pod until the deployment pod completes successfully. The command outputs logs from the application pods if you run it after the deployment pod has completed. After a deployment pod completes, its logs can still be accessed by runningoc logs -f pod/<application_name>-<build_number>-deploy.If an application pod fails, or if an application is not behaving as expected within a running application pod, review the application pod’s logs:oc logs -f pod/<application_name>-<build_number>-<random_string>$oc logs-fpod/<application_name>-<build_number>-<random_string>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review a failed pod’s logs for errors.

- If the build pod fails, review the build pod’s logs:oc logs -f pod/<application_name>-<build_number>-build$oc logs-fpod/<application_name>-<build_number>-buildCopy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can review the build configuration’s logs usingoc logs -f bc/<application_name>. The build configuration’s logs include the logs from the build pod.

If the build pod fails, review the build pod’s logs:

Alternatively, you can review the build configuration’s logs usingoc logs -f bc/<application_name>. The build configuration’s logs include the logs from the build pod.

- If the deployment pod fails, review the deployment pod’s logs:oc logs -f pod/<application_name>-<build_number>-deploy$oc logs-fpod/<application_name>-<build_number>-deployCopy to ClipboardCopied!Toggle word wrapToggle overflowAlternatively, you can review the deployment configuration’s logs usingoc logs -f dc/<application_name>. This outputs logs from the deployment pod until the deployment pod completes successfully. The command outputs logs from the application pods if you run it after the deployment pod has completed. After a deployment pod completes, its logs can still be accessed by runningoc logs -f pod/<application_name>-<build_number>-deploy.

If the deployment pod fails, review the deployment pod’s logs:

Alternatively, you can review the deployment configuration’s logs usingoc logs -f dc/<application_name>. This outputs logs from the deployment pod until the deployment pod completes successfully. The command outputs logs from the application pods if you run it after the deployment pod has completed. After a deployment pod completes, its logs can still be accessed by runningoc logs -f pod/<application_name>-<build_number>-deploy.

- If an application pod fails, or if an application is not behaving as expected within a running application pod, review the application pod’s logs:oc logs -f pod/<application_name>-<build_number>-<random_string>$oc logs-fpod/<application_name>-<build_number>-<random_string>Copy to ClipboardCopied!Toggle word wrapToggle overflow

If an application pod fails, or if an application is not behaving as expected within a running application pod, review the application pod’s logs:

### 7.8.3. Gathering application diagnostic data to investigate application failuresCopy linkLink copied to clipboard!

Application failures can occur within running application pods. In these situations, you can retrieve diagnostic information with these strategies:

- Review events relating to the application pods.
- Review the logs from the application pods, including application-specific log files that are not collected by the OpenShift Logging framework.
- Test application functionality interactively and run diagnostic tools in an application container.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).

Procedure

- List events relating to a specific application pod. The following example retrieves events for an application pod namedmy-app-1-akdlg:oc describe pod/my-app-1-akdlg$oc describe pod/my-app-1-akdlgCopy to ClipboardCopied!Toggle word wrapToggle overflow

List events relating to a specific application pod. The following example retrieves events for an application pod namedmy-app-1-akdlg:

- Review logs from an application pod:oc logs -f pod/my-app-1-akdlg$oc logs-fpod/my-app-1-akdlgCopy to ClipboardCopied!Toggle word wrapToggle overflow

Review logs from an application pod:

- Query specific logs within a running application pod. Logs that are sent to stdout are collected by the OpenShift Logging framework and are included in the output of the preceding command. The following query is only required for logs that are not sent to stdout.If an application log can be accessed without root privileges within a pod, concatenate the log file as follows:oc exec my-app-1-akdlg -- cat /var/log/my-application.log$ocexecmy-app-1-akdlg --cat/var/log/my-application.logCopy to ClipboardCopied!Toggle word wrapToggle overflowIf root access is required to view an application log, you can start a debug container with root privileges and then view the log file from within the container. Start the debug container from the project’sDeploymentConfigobject. Pod users typically run with non-root privileges, but running troubleshooting pods with temporary root privileges can be useful during issue investigation:oc debug dc/my-deployment-configuration --as-root -- cat /var/log/my-application.log$oc debug dc/my-deployment-configuration --as-root --cat/var/log/my-application.logCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can access an interactive shell with root access within the debug pod if you runoc debug dc/<deployment_configuration> --as-rootwithout appending-- <command>.

Query specific logs within a running application pod. Logs that are sent to stdout are collected by the OpenShift Logging framework and are included in the output of the preceding command. The following query is only required for logs that are not sent to stdout.

- If an application log can be accessed without root privileges within a pod, concatenate the log file as follows:oc exec my-app-1-akdlg -- cat /var/log/my-application.log$ocexecmy-app-1-akdlg --cat/var/log/my-application.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

If an application log can be accessed without root privileges within a pod, concatenate the log file as follows:

- If root access is required to view an application log, you can start a debug container with root privileges and then view the log file from within the container. Start the debug container from the project’sDeploymentConfigobject. Pod users typically run with non-root privileges, but running troubleshooting pods with temporary root privileges can be useful during issue investigation:oc debug dc/my-deployment-configuration --as-root -- cat /var/log/my-application.log$oc debug dc/my-deployment-configuration --as-root --cat/var/log/my-application.logCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can access an interactive shell with root access within the debug pod if you runoc debug dc/<deployment_configuration> --as-rootwithout appending-- <command>.

If root access is required to view an application log, you can start a debug container with root privileges and then view the log file from within the container. Start the debug container from the project’sDeploymentConfigobject. Pod users typically run with non-root privileges, but running troubleshooting pods with temporary root privileges can be useful during issue investigation:

You can access an interactive shell with root access within the debug pod if you runoc debug dc/<deployment_configuration> --as-rootwithout appending-- <command>.

- Test application functionality interactively and run diagnostic tools, in an application container with an interactive shell.Start an interactive shell on the application container:oc exec -it my-app-1-akdlg /bin/bash$ocexec-itmy-app-1-akdlg /bin/bashCopy to ClipboardCopied!Toggle word wrapToggle overflowTest application functionality interactively from within the shell. For example, you can run the container’s entry point command and observe the results. Then, test changes from the command line directly, before updating the source code and rebuilding the application container through the S2I process.Run diagnostic binaries available within the container.Root privileges are required to run some diagnostic binaries. In these situations you can start a debug pod with root access, based on a problematic pod’sDeploymentConfigobject, by runningoc debug dc/<deployment_configuration> --as-root. Then, you can run diagnostic binaries as root from within the debug pod.

Test application functionality interactively and run diagnostic tools, in an application container with an interactive shell.

- Start an interactive shell on the application container:oc exec -it my-app-1-akdlg /bin/bash$ocexec-itmy-app-1-akdlg /bin/bashCopy to ClipboardCopied!Toggle word wrapToggle overflow

Start an interactive shell on the application container:

- Test application functionality interactively from within the shell. For example, you can run the container’s entry point command and observe the results. Then, test changes from the command line directly, before updating the source code and rebuilding the application container through the S2I process.
- Run diagnostic binaries available within the container.Root privileges are required to run some diagnostic binaries. In these situations you can start a debug pod with root access, based on a problematic pod’sDeploymentConfigobject, by runningoc debug dc/<deployment_configuration> --as-root. Then, you can run diagnostic binaries as root from within the debug pod.

Run diagnostic binaries available within the container.

Root privileges are required to run some diagnostic binaries. In these situations you can start a debug pod with root access, based on a problematic pod’sDeploymentConfigobject, by runningoc debug dc/<deployment_configuration> --as-root. Then, you can run diagnostic binaries as root from within the debug pod.

- If diagnostic binaries are not available within a container, you can run a host’s diagnostic binaries within a container’s namespace by usingnsenter. The following example runsip adwithin a container’s namespace, using the host`sipbinary.Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:oc debug node/my-cluster-node$oc debug node/my-cluster-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflowSet/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.Determine the target container ID:crictl ps#crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflowDetermine the container’s process ID. In this example, the target container ID isa7fe32346b120:crictl inspect a7fe32346b120 --output yaml | grep 'pid:' | awk '{print $2}'#crictl inspect a7fe32346b120--outputyaml|grep'pid:'|awk'{print $2}'Copy to ClipboardCopied!Toggle word wrapToggle overflowRunip adwithin the container’s namespace, using the host’sipbinary. This example uses31150as the container’s process ID. Thensentercommand enters the namespace of a target process and runs a command in its namespace. Because the target process in this example is a container’s process ID, theip adcommand is run in the container’s namespace from the host:nsenter -n -t 31150 -- ip ad#nsenter-n-t31150--ipadCopy to ClipboardCopied!Toggle word wrapToggle overflowRunning a host’s diagnostic binaries within a container’s namespace is only possible if you are using a privileged container such as a debug node.

If diagnostic binaries are not available within a container, you can run a host’s diagnostic binaries within a container’s namespace by usingnsenter. The following example runsip adwithin a container’s namespace, using the host`sipbinary.

- Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:oc debug node/my-cluster-node$oc debug node/my-cluster-nodeCopy to ClipboardCopied!Toggle word wrapToggle overflow

Enter into a debug session on the target node. This step instantiates a debug pod called<node_name>-debug:

- Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:chroot /host#chroot/hostCopy to ClipboardCopied!Toggle word wrapToggle overflowOpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

Set/hostas the root directory within the debug shell. The debug pod mounts the host’s root file system in/hostwithin the pod. By changing the root directory to/host, you can run binaries contained in the host’s executable paths:

OpenShift Container Platform 4.17 cluster nodes running Red Hat Enterprise Linux CoreOS (RHCOS) are immutable and rely on Operators to apply cluster changes. Accessing cluster nodes by using SSH is not recommended. However, if the OpenShift Container Platform API is not available, or the kubelet is not properly functioning on the target node,ocoperations will be impacted. In such situations, it is possible to access nodes usingssh core@<node>.<cluster_name>.<base_domain>instead.

- Determine the target container ID:crictl ps#crictlpsCopy to ClipboardCopied!Toggle word wrapToggle overflow

Determine the target container ID:

- Determine the container’s process ID. In this example, the target container ID isa7fe32346b120:crictl inspect a7fe32346b120 --output yaml | grep 'pid:' | awk '{print $2}'#crictl inspect a7fe32346b120--outputyaml|grep'pid:'|awk'{print $2}'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Determine the container’s process ID. In this example, the target container ID isa7fe32346b120:

- Runip adwithin the container’s namespace, using the host’sipbinary. This example uses31150as the container’s process ID. Thensentercommand enters the namespace of a target process and runs a command in its namespace. Because the target process in this example is a container’s process ID, theip adcommand is run in the container’s namespace from the host:nsenter -n -t 31150 -- ip ad#nsenter-n-t31150--ipadCopy to ClipboardCopied!Toggle word wrapToggle overflowRunning a host’s diagnostic binaries within a container’s namespace is only possible if you are using a privileged container such as a debug node.

Runip adwithin the container’s namespace, using the host’sipbinary. This example uses31150as the container’s process ID. Thensentercommand enters the namespace of a target process and runs a command in its namespace. Because the target process in this example is a container’s process ID, theip adcommand is run in the container’s namespace from the host:

Running a host’s diagnostic binaries within a container’s namespace is only possible if you are using a privileged container such as a debug node.

## 7.9. Troubleshooting storage issuesCopy linkLink copied to clipboard!

### 7.9.1. Resolving multi-attach errorsCopy linkLink copied to clipboard!

When a node crashes or shuts down abruptly, the attached ReadWriteOnce (RWO) volume is expected to be unmounted from the node so that it can be used by a pod scheduled on another node.

However, mounting on a new node is not possible because the failed node is unable to unmount the attached volume.

A multi-attach error is reported:

Example output

```
Unable to attach or mount volumes: unmounted volumes=[sso-mysql-pvol], unattached volumes=[sso-mysql-pvol default-token-x4rzc]: timed out waiting for the condition
Multi-Attach error for volume "pvc-8837384d-69d7-40b2-b2e6-5df86943eef9" Volume is already used by pod(s) sso-mysql-1-ns6b4
```

```
Unable to attach or mount volumes: unmounted volumes=[sso-mysql-pvol], unattached volumes=[sso-mysql-pvol default-token-x4rzc]: timed out waiting for the condition
Multi-Attach error for volume "pvc-8837384d-69d7-40b2-b2e6-5df86943eef9" Volume is already used by pod(s) sso-mysql-1-ns6b4
```

Procedure

To resolve the multi-attach issue, use one of the following solutions:

- Enable multiple attachments by using RWX volumes.For most storage solutions, you can use ReadWriteMany (RWX) volumes to prevent multi-attach errors.

Enable multiple attachments by using RWX volumes.

For most storage solutions, you can use ReadWriteMany (RWX) volumes to prevent multi-attach errors.

- Recover or delete the failed node when using an RWO volume.For storage that does not support RWX, such as VMware vSphere, RWO volumes must be used instead. However, RWO volumes cannot be mounted on multiple nodes.If you encounter a multi-attach error message with an RWO volume, force delete the pod on a shutdown or crashed node to avoid data loss in critical workloads, such as when dynamic persistent volumes are attached.oc delete pod <old_pod> --force=true --grace-period=0$oc delete pod<old_pod>--force=true --grace-period=0Copy to ClipboardCopied!Toggle word wrapToggle overflowThis command deletes the volumes stuck on shutdown or crashed nodes after six minutes.

Recover or delete the failed node when using an RWO volume.

For storage that does not support RWX, such as VMware vSphere, RWO volumes must be used instead. However, RWO volumes cannot be mounted on multiple nodes.

If you encounter a multi-attach error message with an RWO volume, force delete the pod on a shutdown or crashed node to avoid data loss in critical workloads, such as when dynamic persistent volumes are attached.

This command deletes the volumes stuck on shutdown or crashed nodes after six minutes.

## 7.10. Troubleshooting Windows container workload issuesCopy linkLink copied to clipboard!

### 7.10.1. Windows Machine Config Operator does not installCopy linkLink copied to clipboard!

If you have completed the process of installing the Windows Machine Config Operator (WMCO), but the Operator is stuck in theInstallWaitingphase, your issue is likely caused by a networking issue.

The WMCO requires your OpenShift Container Platform cluster to be configured with hybrid networking using OVN-Kubernetes; the WMCO cannot complete the installation process without hybrid networking available. This is necessary to manage nodes on multiple operating systems (OS) and OS variants. This must be completed during the installation of your cluster.

For more information, seeConfiguring hybrid networking.

### 7.10.2. Investigating why Windows Machine does not become compute nodeCopy linkLink copied to clipboard!

There are various reasons why a Windows Machine does not become a compute node. The best way to investigate this problem is to collect the Windows Machine Config Operator (WMCO) logs.

Prerequisites

- You installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.

Procedure

- Run the following command to collect the WMCO logs:oc logs -f deployment/windows-machine-config-operator -n openshift-windows-machine-config-operator$oc logs-fdeployment/windows-machine-config-operator-nopenshift-windows-machine-config-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to collect the WMCO logs:

### 7.10.3. Accessing a Windows nodeCopy linkLink copied to clipboard!

Windows nodes cannot be accessed using theoc debug nodecommand; the command requires running a privileged pod on the node, which is not yet supported for Windows. Instead, a Windows node can be accessed using a secure shell (SSH) or Remote Desktop Protocol (RDP). An SSH bastion is required for both methods.

#### 7.10.3.1. Accessing a Windows node using SSHCopy linkLink copied to clipboard!

You can access a Windows node by using a secure shell (SSH).

Prerequisites

- You have installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.
- You have added the key used in thecloud-private-keysecret and the key used when creating the cluster to the ssh-agent. For security reasons, remember to remove the keys from the ssh-agent after use.
- You have connected to the Windows nodeusing anssh-bastionpod.

Procedure

- Access the Windows node by running the following command:ssh -t -o StrictHostKeyChecking=no -o ProxyCommand='ssh -A -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=30 -W %h:%p core@$(oc get service --all-namespaces -l run=ssh-bastion \
    -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")' <username>@<windows_node_internal_ip>$ssh-t-oStrictHostKeyChecking=no-oProxyCommand='ssh -A -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=30 -W %h:%p core@$(oc get service --all-namespaces -l run=ssh-bastion \
    -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")'<username>@<windows_node_internal_ip>12Copy to ClipboardCopied!Toggle word wrapToggle overflow1Specify the cloud provider username, such asAdministratorfor Amazon Web Services (AWS) orcapifor Microsoft Azure.2Specify the internal IP address of the node, which can be discovered by running the following command:oc get nodes <node_name> -o jsonpath={.status.addresses[?\(@.type==\"InternalIP\"\)].address}$oc get nodes<node_name>-ojsonpath={.status.addresses[?\(@.type==\"InternalIP\"\)].address}Copy to ClipboardCopied!Toggle word wrapToggle overflow

Access the Windows node by running the following command:

```
ssh -t -o StrictHostKeyChecking=no -o ProxyCommand='ssh -A -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=30 -W %h:%p core@$(oc get service --all-namespaces -l run=ssh-bastion \
    -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")' <username>@<windows_node_internal_ip>
```

```
$ ssh -t -o StrictHostKeyChecking=no -o ProxyCommand='ssh -A -o StrictHostKeyChecking=no \
    -o ServerAliveInterval=30 -W %h:%p core@$(oc get service --all-namespaces -l run=ssh-bastion \
    -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")' <username>@<windows_node_internal_ip>
```

**1**
  Specify the cloud provider username, such asAdministratorfor Amazon Web Services (AWS) orcapifor Microsoft Azure.

**2**
  Specify the internal IP address of the node, which can be discovered by running the following command:

#### 7.10.3.2. Accessing a Windows node using RDPCopy linkLink copied to clipboard!

You can access a Windows node by using a Remote Desktop Protocol (RDP).

Prerequisites

- You installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.
- You have added the key used in thecloud-private-keysecret and the key used when creating the cluster to the ssh-agent. For security reasons, remember to remove the keys from the ssh-agent after use.
- You have connected to the Windows nodeusing anssh-bastionpod.

Procedure

- Run the following command to set up an SSH tunnel:ssh -L 2020:<windows_node_internal_ip>:3389 \
    core@$(oc get service --all-namespaces -l run=ssh-bastion -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")$ssh-L2020:<windows_node_internal_ip>:3389\1core@$(oc get service --all-namespaces -l run=ssh-bastion -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")Copy to ClipboardCopied!Toggle word wrapToggle overflow1Specify the internal IP address of the node, which can be discovered by running the following command:oc get nodes <node_name> -o jsonpath={.status.addresses[?\(@.type==\"InternalIP\"\)].address}$oc get nodes<node_name>-ojsonpath={.status.addresses[?\(@.type==\"InternalIP\"\)].address}Copy to ClipboardCopied!Toggle word wrapToggle overflow

Run the following command to set up an SSH tunnel:

```
ssh -L 2020:<windows_node_internal_ip>:3389 \
    core@$(oc get service --all-namespaces -l run=ssh-bastion -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")
```

```
core@$(oc get service --all-namespaces -l run=ssh-bastion -o go-template="{{ with (index (index .items 0).status.loadBalancer.ingress 0) }}{{ or .hostname .ip }}{{end}}")
```

**1**
  Specify the internal IP address of the node, which can be discovered by running the following command:
- From within the resulting shell, SSH into the Windows node and run the following command to create a password for the user:[REDACTED_ACCOUNT] user <username> *C:\> net user <username> *1Copy to ClipboardCopied!Toggle word wrapToggle overflow1Specify the cloud provider user name, such asAdministratorfor AWS orcapifor Azure.

From within the resulting shell, SSH into the Windows node and run the following command to create a password for the user:

[REDACTED_ACCOUNT]
  Specify the cloud provider user name, such asAdministratorfor AWS orcapifor Azure.

You can now remotely access the Windows node atlocalhost:2020using an RDP client.

### 7.10.4. Collecting Kubernetes node logs for Windows containersCopy linkLink copied to clipboard!

Windows container logging works differently from Linux container logging; the Kubernetes node logs for Windows workloads are streamed to theC:\var\logsdirectory by default. Therefore, you must gather the Windows node logs from that directory.

Prerequisites

- You installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.

Procedure

- To view the logs under all directories inC:\var\logs, run the following command:oc adm node-logs -l kubernetes.io/os=windows --path= \
    /ip-10-0-138-252.us-east-2.compute.internal containers \
    /ip-10-0-138-252.us-east-2.compute.internal hybrid-overlay \
    /ip-10-0-138-252.us-east-2.compute.internal kube-proxy \
    /ip-10-0-138-252.us-east-2.compute.internal kubelet \
    /ip-10-0-138-252.us-east-2.compute.internal pods$oc adm node-logs-lkubernetes.io/os=windows--path=\/ip-10-0-138-252.us-east-2.compute.internal containers\/ip-10-0-138-252.us-east-2.compute.internal hybrid-overlay\/ip-10-0-138-252.us-east-2.compute.internal kube-proxy\/ip-10-0-138-252.us-east-2.compute.internal kubelet\/ip-10-0-138-252.us-east-2.compute.internal podsCopy to ClipboardCopied!Toggle word wrapToggle overflow

To view the logs under all directories inC:\var\logs, run the following command:

```
oc adm node-logs -l kubernetes.io/os=windows --path= \
    /ip-10-0-138-252.us-east-2.compute.internal containers \
    /ip-10-0-138-252.us-east-2.compute.internal hybrid-overlay \
    /ip-10-0-138-252.us-east-2.compute.internal kube-proxy \
    /ip-10-0-138-252.us-east-2.compute.internal kubelet \
    /ip-10-0-138-252.us-east-2.compute.internal pods
```

```
$ oc adm node-logs -l kubernetes.io/os=windows --path= \
    /ip-10-0-138-252.us-east-2.compute.internal containers \
    /ip-10-0-138-252.us-east-2.compute.internal hybrid-overlay \
    /ip-10-0-138-252.us-east-2.compute.internal kube-proxy \
    /ip-10-0-138-252.us-east-2.compute.internal kubelet \
    /ip-10-0-138-252.us-east-2.compute.internal pods
```

- You can now list files in the directories using the same command and view the individual log files. For example, to view the kubelet logs, run the following command:oc adm node-logs -l kubernetes.io/os=windows --path=/kubelet/kubelet.log$oc adm node-logs-lkubernetes.io/os=windows--path=/kubelet/kubelet.logCopy to ClipboardCopied!Toggle word wrapToggle overflow

You can now list files in the directories using the same command and view the individual log files. For example, to view the kubelet logs, run the following command:

### 7.10.5. Collecting Windows application event logsCopy linkLink copied to clipboard!

TheGet-WinEventshim on the kubeletlogsendpoint can be used to collect application event logs from Windows machines.

Prerequisites

- You installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.

Procedure

- To view logs from all applications logging to the event logs on the Windows machine, run:oc adm node-logs -l kubernetes.io/os=windows --path=journal$oc adm node-logs-lkubernetes.io/os=windows--path=journalCopy to ClipboardCopied!Toggle word wrapToggle overflowThe same command is executed when collecting logs withoc adm must-gather.Other Windows application logs from the event log can also be collected by specifying the respective service with a-uflag. For example, you can run the following command to collect logs for the containerd container runtime service:oc adm node-logs -l kubernetes.io/os=windows --path=journal -u containerd$oc adm node-logs-lkubernetes.io/os=windows--path=journal-ucontainerdCopy to ClipboardCopied!Toggle word wrapToggle overflow

To view logs from all applications logging to the event logs on the Windows machine, run:

The same command is executed when collecting logs withoc adm must-gather.

Other Windows application logs from the event log can also be collected by specifying the respective service with a-uflag. For example, you can run the following command to collect logs for the containerd container runtime service:

### 7.10.6. Collecting containerd logs for Windows containersCopy linkLink copied to clipboard!

The Windows containerd container service does not stream log data to stdout, but instead, it stream log data to the Windows event log. You can view the containerd event logs to investigate issues you think might be caused by the Windows containerd container service.

Prerequisites

- You installed the Windows Machine Config Operator (WMCO) using Operator Lifecycle Manager (OLM).
- You have created a Windows compute machine set.

Procedure

- View the containerd logs by running the following command:oc adm node-logs -l kubernetes.io/os=windows --path=containerd$oc adm node-logs-lkubernetes.io/os=windows--path=containerdCopy to ClipboardCopied!Toggle word wrapToggle overflow

View the containerd logs by running the following command:

## 7.11. Investigating monitoring issuesCopy linkLink copied to clipboard!

OpenShift Container Platform includes a preconfigured, preinstalled, and self-updating monitoring stack that provides monitoring for core platform components. In OpenShift Container Platform 4.17, cluster administrators can optionally enable monitoring for user-defined projects.

Use these procedures if the following issues occur:

- Your own metrics are unavailable.
- Prometheus is consuming a lot of disk space.
- TheKubePersistentVolumeFillingUpalert is firing for Prometheus.

### 7.11.1. Investigating why user-defined project metrics are unavailableCopy linkLink copied to clipboard!

ServiceMonitorresources enable you to determine how to use the metrics exposed by a service in user-defined projects. Follow the steps outlined in this procedure if you have created aServiceMonitorresource but cannot see any corresponding metrics in the Metrics UI.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.
- You have installed the OpenShift CLI (oc).
- You have enabled and configured monitoring for user-defined projects.
- You have created aServiceMonitorresource.

Procedure

- Ensure that your project and resources are not excluded from user workload monitoring. The following examples use thens1project.Verify that the projectdoes nothave theopenshift.io/user-monitoring=falselabel attached:oc get namespace ns1 --show-labels | grep 'openshift.io/user-monitoring=false'$oc get namespace ns1 --show-labels|grep'openshift.io/user-monitoring=false'Copy to ClipboardCopied!Toggle word wrapToggle overflowThe default label set for user workload projects isopenshift.io/user-monitoring=true. However, the label is not visible unless you manually apply it.Verify that theServiceMonitorandPodMonitorresourcesdo nothave theopenshift.io/user-monitoring=falselabel attached. The following example checks theprometheus-example-monitorservice monitor.oc -n ns1 get servicemonitor prometheus-example-monitor --show-labels | grep 'openshift.io/user-monitoring=false'$oc-nns1 get servicemonitor prometheus-example-monitor --show-labels|grep'openshift.io/user-monitoring=false'Copy to ClipboardCopied!Toggle word wrapToggle overflowIf the label is attached, remove the label:Example of removing the label from the projectoc label namespace ns1 'openshift.io/user-monitoring-'$oc label namespace ns1'openshift.io/user-monitoring-'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of removing the label from the resourceoc -n ns1 label servicemonitor prometheus-example-monitor 'openshift.io/user-monitoring-'$oc-nns1 label servicemonitor prometheus-example-monitor'openshift.io/user-monitoring-'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputnamespace/ns1 unlabelednamespace/ns1 unlabeledCopy to ClipboardCopied!Toggle word wrapToggle overflow

Ensure that your project and resources are not excluded from user workload monitoring. The following examples use thens1project.

- Verify that the projectdoes nothave theopenshift.io/user-monitoring=falselabel attached:oc get namespace ns1 --show-labels | grep 'openshift.io/user-monitoring=false'$oc get namespace ns1 --show-labels|grep'openshift.io/user-monitoring=false'Copy to ClipboardCopied!Toggle word wrapToggle overflowThe default label set for user workload projects isopenshift.io/user-monitoring=true. However, the label is not visible unless you manually apply it.

Verify that the projectdoes nothave theopenshift.io/user-monitoring=falselabel attached:

The default label set for user workload projects isopenshift.io/user-monitoring=true. However, the label is not visible unless you manually apply it.

- Verify that theServiceMonitorandPodMonitorresourcesdo nothave theopenshift.io/user-monitoring=falselabel attached. The following example checks theprometheus-example-monitorservice monitor.oc -n ns1 get servicemonitor prometheus-example-monitor --show-labels | grep 'openshift.io/user-monitoring=false'$oc-nns1 get servicemonitor prometheus-example-monitor --show-labels|grep'openshift.io/user-monitoring=false'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify that theServiceMonitorandPodMonitorresourcesdo nothave theopenshift.io/user-monitoring=falselabel attached. The following example checks theprometheus-example-monitorservice monitor.

- If the label is attached, remove the label:Example of removing the label from the projectoc label namespace ns1 'openshift.io/user-monitoring-'$oc label namespace ns1'openshift.io/user-monitoring-'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample of removing the label from the resourceoc -n ns1 label servicemonitor prometheus-example-monitor 'openshift.io/user-monitoring-'$oc-nns1 label servicemonitor prometheus-example-monitor'openshift.io/user-monitoring-'Copy to ClipboardCopied!Toggle word wrapToggle overflowExample outputnamespace/ns1 unlabelednamespace/ns1 unlabeledCopy to ClipboardCopied!Toggle word wrapToggle overflow

If the label is attached, remove the label:

Example of removing the label from the project

Example of removing the label from the resource

Example output

- Check that the corresponding labels match in the service andServiceMonitorresource configurations. The following examples use theprometheus-example-appservice, theprometheus-example-monitorservice monitor, and thens1project.Obtain the label defined in the service.oc -n ns1 get service prometheus-example-app -o yaml$oc-nns1 getserviceprometheus-example-app-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputlabels:
    app: prometheus-example-applabels:
    app: prometheus-example-appCopy to ClipboardCopied!Toggle word wrapToggle overflowCheck that thematchLabelsdefinition in theServiceMonitorresource configuration matches the label output in the previous step.oc -n ns1 get servicemonitor prometheus-example-monitor -o yaml$oc-nns1 get servicemonitor prometheus-example-monitor-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: v1
kind: ServiceMonitor
metadata:
  name: prometheus-example-monitor
  namespace: ns1
spec:
  endpoints:
  - interval: 30s
    port: web
    scheme: http
  selector:
    matchLabels:
      app: prometheus-example-appapiVersion:v1kind:ServiceMonitormetadata:name:prometheus-example-monitornamespace:ns1spec:endpoints:-interval:30sport:webscheme:httpselector:matchLabels:app:prometheus-example-appCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can check service andServiceMonitorresource labels as a developer with view permissions for the project.

Check that the corresponding labels match in the service andServiceMonitorresource configurations. The following examples use theprometheus-example-appservice, theprometheus-example-monitorservice monitor, and thens1project.

- Obtain the label defined in the service.oc -n ns1 get service prometheus-example-app -o yaml$oc-nns1 getserviceprometheus-example-app-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputlabels:
    app: prometheus-example-applabels:
    app: prometheus-example-appCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain the label defined in the service.

Example output

```
labels:
    app: prometheus-example-app
```

```
labels:
    app: prometheus-example-app
```

- Check that thematchLabelsdefinition in theServiceMonitorresource configuration matches the label output in the previous step.oc -n ns1 get servicemonitor prometheus-example-monitor -o yaml$oc-nns1 get servicemonitor prometheus-example-monitor-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: v1
kind: ServiceMonitor
metadata:
  name: prometheus-example-monitor
  namespace: ns1
spec:
  endpoints:
  - interval: 30s
    port: web
    scheme: http
  selector:
    matchLabels:
      app: prometheus-example-appapiVersion:v1kind:ServiceMonitormetadata:name:prometheus-example-monitornamespace:ns1spec:endpoints:-interval:30sport:webscheme:httpselector:matchLabels:app:prometheus-example-appCopy to ClipboardCopied!Toggle word wrapToggle overflowYou can check service andServiceMonitorresource labels as a developer with view permissions for the project.

Check that thematchLabelsdefinition in theServiceMonitorresource configuration matches the label output in the previous step.

Example output

```
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: prometheus-example-monitor
  namespace: ns1
spec:
  endpoints:
  - interval: 30s
    port: web
    scheme: http
  selector:
    matchLabels:
      app: prometheus-example-app
```

```
apiVersion: v1
kind: ServiceMonitor
metadata:
  name: prometheus-example-monitor
  namespace: ns1
spec:
  endpoints:
  - interval: 30s
    port: web
    scheme: http
  selector:
    matchLabels:
      app: prometheus-example-app
```

You can check service andServiceMonitorresource labels as a developer with view permissions for the project.

- Inspect the logs for the Prometheus Operator in theopenshift-user-workload-monitoringproject.List the pods in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring get pods$oc-nopenshift-user-workload-monitoring get podsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132mNAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132mCopy to ClipboardCopied!Toggle word wrapToggle overflowObtain the logs from theprometheus-operatorcontainer in theprometheus-operatorpod. In the following example, the pod is calledprometheus-operator-776fcbbd56-2nbfm:oc -n openshift-user-workload-monitoring logs prometheus-operator-776fcbbd56-2nbfm -c prometheus-operator$oc-nopenshift-user-workload-monitoring logs prometheus-operator-776fcbbd56-2nbfm-cprometheus-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflowIf there is a issue with the service monitor, the logs might include an error similar to this example:level=warn ts=2020-08-10T11:48:20.906739623Z caller=operator.go:1829 component=prometheusoperator msg="skipping servicemonitor" error="it accesses file system via bearer token file which Prometheus specification prohibits" servicemonitor=eagle/eagle namespace=openshift-user-workload-monitoring prometheus=user-workloadlevel=warn ts=2020-08-10T11:48:20.906739623Z caller=operator.go:1829 component=prometheusoperator msg="skipping servicemonitor" error="it accesses file system via bearer token file which Prometheus specification prohibits" servicemonitor=eagle/eagle namespace=openshift-user-workload-monitoring prometheus=user-workloadCopy to ClipboardCopied!Toggle word wrapToggle overflow

Inspect the logs for the Prometheus Operator in theopenshift-user-workload-monitoringproject.

- List the pods in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring get pods$oc-nopenshift-user-workload-monitoring get podsCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputNAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132mNAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132mCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the pods in theopenshift-user-workload-monitoringproject:

Example output

```
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132m
```

```
NAME                                   READY   STATUS    RESTARTS   AGE
prometheus-operator-776fcbbd56-2nbfm   2/2     Running   0          132m
prometheus-user-workload-0             5/5     Running   1          132m
prometheus-user-workload-1             5/5     Running   1          132m
thanos-ruler-user-workload-0           3/3     Running   0          132m
thanos-ruler-user-workload-1           3/3     Running   0          132m
```

- Obtain the logs from theprometheus-operatorcontainer in theprometheus-operatorpod. In the following example, the pod is calledprometheus-operator-776fcbbd56-2nbfm:oc -n openshift-user-workload-monitoring logs prometheus-operator-776fcbbd56-2nbfm -c prometheus-operator$oc-nopenshift-user-workload-monitoring logs prometheus-operator-776fcbbd56-2nbfm-cprometheus-operatorCopy to ClipboardCopied!Toggle word wrapToggle overflowIf there is a issue with the service monitor, the logs might include an error similar to this example:level=warn ts=2020-08-10T11:48:20.906739623Z caller=operator.go:1829 component=prometheusoperator msg="skipping servicemonitor" error="it accesses file system via bearer token file which Prometheus specification prohibits" servicemonitor=eagle/eagle namespace=openshift-user-workload-monitoring prometheus=user-workloadlevel=warn ts=2020-08-10T11:48:20.906739623Z caller=operator.go:1829 component=prometheusoperator msg="skipping servicemonitor" error="it accesses file system via bearer token file which Prometheus specification prohibits" servicemonitor=eagle/eagle namespace=openshift-user-workload-monitoring prometheus=user-workloadCopy to ClipboardCopied!Toggle word wrapToggle overflow

Obtain the logs from theprometheus-operatorcontainer in theprometheus-operatorpod. In the following example, the pod is calledprometheus-operator-776fcbbd56-2nbfm:

If there is a issue with the service monitor, the logs might include an error similar to this example:

- Review the target status for your endpoint on theMetrics targetspage in the OpenShift Container Platform web console UI.Log in to the OpenShift Container Platform web console and navigate toObserveTargetsin theAdministratorperspective.Locate the metrics endpoint in the list, and review the status of the target in theStatuscolumn.If theStatusisDown, click the URL for the endpoint to view more information on theTarget Detailspage for that metrics target.

Review the target status for your endpoint on theMetrics targetspage in the OpenShift Container Platform web console UI.

- Log in to the OpenShift Container Platform web console and navigate toObserveTargetsin theAdministratorperspective.
- Locate the metrics endpoint in the list, and review the status of the target in theStatuscolumn.
- If theStatusisDown, click the URL for the endpoint to view more information on theTarget Detailspage for that metrics target.
- Configure debug level logging for the Prometheus Operator in theopenshift-user-workload-monitoringproject.Edit theuser-workload-monitoring-configConfigMapobject in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring edit configmap user-workload-monitoring-config$oc-nopenshift-user-workload-monitoring edit configmap user-workload-monitoring-configCopy to ClipboardCopied!Toggle word wrapToggle overflowAddlogLevel: debugforprometheusOperatorunderdata/config.yamlto set the log level todebug:apiVersion: v1
kind: ConfigMap
metadata:
  name: user-workload-monitoring-config
  namespace: openshift-user-workload-monitoring
data:
  config.yaml: |
    prometheusOperator:
      logLevel: debug
# ...apiVersion:v1kind:ConfigMapmetadata:name:user-workload-monitoring-confignamespace:openshift-user-workload-monitoringdata:config.yaml:|prometheusOperator:
      logLevel: debug# ...Copy to ClipboardCopied!Toggle word wrapToggle overflowSave the file to apply the changes. The affectedprometheus-operatorpod is automatically redeployed.Confirm that thedebuglog-level has been applied to theprometheus-operatordeployment in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring get deploy prometheus-operator -o yaml |  grep "log-level"$oc-nopenshift-user-workload-monitoring get deploy prometheus-operator-oyaml|grep"log-level"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output- --log-level=debug- --log-level=debugCopy to ClipboardCopied!Toggle word wrapToggle overflowDebug level logging will show all calls made by the Prometheus Operator.Check that theprometheus-operatorpod is running:oc -n openshift-user-workload-monitoring get pods$oc-nopenshift-user-workload-monitoring get podsCopy to ClipboardCopied!Toggle word wrapToggle overflowIf an unrecognized Prometheus Operatorloglevelvalue is included in the config map, theprometheus-operatorpod might not restart successfully.Review the debug logs to see if the Prometheus Operator is using theServiceMonitorresource. Review the logs for other related errors.

Configure debug level logging for the Prometheus Operator in theopenshift-user-workload-monitoringproject.

- Edit theuser-workload-monitoring-configConfigMapobject in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring edit configmap user-workload-monitoring-config$oc-nopenshift-user-workload-monitoring edit configmap user-workload-monitoring-configCopy to ClipboardCopied!Toggle word wrapToggle overflow

Edit theuser-workload-monitoring-configConfigMapobject in theopenshift-user-workload-monitoringproject:

- AddlogLevel: debugforprometheusOperatorunderdata/config.yamlto set the log level todebug:apiVersion: v1
kind: ConfigMap
metadata:
  name: user-workload-monitoring-config
  namespace: openshift-user-workload-monitoring
data:
  config.yaml: |
    prometheusOperator:
      logLevel: debug
# ...apiVersion:v1kind:ConfigMapmetadata:name:user-workload-monitoring-confignamespace:openshift-user-workload-monitoringdata:config.yaml:|prometheusOperator:
      logLevel: debug# ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

AddlogLevel: debugforprometheusOperatorunderdata/config.yamlto set the log level todebug:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-workload-monitoring-config
  namespace: openshift-user-workload-monitoring
data:
  config.yaml: |
    prometheusOperator:
      logLevel: debug
# ...
```

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: user-workload-monitoring-config
  namespace: openshift-user-workload-monitoring
data:
  config.yaml: |
    prometheusOperator:
      logLevel: debug
# ...
```

- Save the file to apply the changes. The affectedprometheus-operatorpod is automatically redeployed.
- Confirm that thedebuglog-level has been applied to theprometheus-operatordeployment in theopenshift-user-workload-monitoringproject:oc -n openshift-user-workload-monitoring get deploy prometheus-operator -o yaml |  grep "log-level"$oc-nopenshift-user-workload-monitoring get deploy prometheus-operator-oyaml|grep"log-level"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output- --log-level=debug- --log-level=debugCopy to ClipboardCopied!Toggle word wrapToggle overflowDebug level logging will show all calls made by the Prometheus Operator.

Confirm that thedebuglog-level has been applied to theprometheus-operatordeployment in theopenshift-user-workload-monitoringproject:

Example output

Debug level logging will show all calls made by the Prometheus Operator.

- Check that theprometheus-operatorpod is running:oc -n openshift-user-workload-monitoring get pods$oc-nopenshift-user-workload-monitoring get podsCopy to ClipboardCopied!Toggle word wrapToggle overflowIf an unrecognized Prometheus Operatorloglevelvalue is included in the config map, theprometheus-operatorpod might not restart successfully.

Check that theprometheus-operatorpod is running:

If an unrecognized Prometheus Operatorloglevelvalue is included in the config map, theprometheus-operatorpod might not restart successfully.

- Review the debug logs to see if the Prometheus Operator is using theServiceMonitorresource. Review the logs for other related errors.

### 7.11.2. Determining why Prometheus is consuming a lot of disk spaceCopy linkLink copied to clipboard!

Developers can create labels to define attributes for metrics in the form of key-value pairs. The number of potential key-value pairs corresponds to the number of possible values for an attribute. An attribute that has an unlimited number of potential values is called an unbound attribute. For example, acustomer_idattribute is unbound because it has an infinite number of possible values.

Every assigned key-value pair has a unique time series. The use of many unbound attributes in labels can result in an exponential increase in the number of time series created. This can impact Prometheus performance and can consume a lot of disk space.

You can use the following measures when Prometheus consumes a lot of disk:

- Check the time series database (TSDB) status using the Prometheus HTTP APIfor more information about which labels are creating the most time series data. Doing so requires cluster administrator privileges.
- Check the number of scrape samplesthat are being collected.
- Reduce the number of unique time series that are createdby reducing the number of unbound attributes that are assigned to user-defined metrics.Using attributes that are bound to a limited set of possible values reduces the number of potential key-value pair combinations.

Reduce the number of unique time series that are createdby reducing the number of unbound attributes that are assigned to user-defined metrics.

Using attributes that are bound to a limited set of possible values reduces the number of potential key-value pair combinations.

- Enforce limits on the number of samples that can be scrapedacross user-defined projects. This requires cluster administrator privileges.

Prerequisites

- You have access to the cluster as a user with thecluster-admincluster role.
- You have installed the OpenShift CLI (oc).

Procedure

- In theAdministratorperspective, navigate toObserveMetrics.
- Enter a Prometheus Query Language (PromQL) query in theExpressionfield. The following example queries help to identify high cardinality metrics that might result in high disk space consumption:By running the following query, you can identify the ten jobs that have the highest number of scrape samples:topk(10, max by(namespace, job) (topk by(namespace, job) (1, scrape_samples_post_metric_relabeling)))topk(10, max by(namespace, job) (topk by(namespace, job) (1, scrape_samples_post_metric_relabeling)))Copy to ClipboardCopied!Toggle word wrapToggle overflowBy running the following query, you can pinpoint time series churn by identifying the ten jobs that have created the most time series data in the last hour:topk(10, sum by(namespace, job) (sum_over_time(scrape_series_added[1h])))topk(10, sum by(namespace, job) (sum_over_time(scrape_series_added[1h])))Copy to ClipboardCopied!Toggle word wrapToggle overflow

Enter a Prometheus Query Language (PromQL) query in theExpressionfield. The following example queries help to identify high cardinality metrics that might result in high disk space consumption:

- By running the following query, you can identify the ten jobs that have the highest number of scrape samples:topk(10, max by(namespace, job) (topk by(namespace, job) (1, scrape_samples_post_metric_relabeling)))topk(10, max by(namespace, job) (topk by(namespace, job) (1, scrape_samples_post_metric_relabeling)))Copy to ClipboardCopied!Toggle word wrapToggle overflow

By running the following query, you can identify the ten jobs that have the highest number of scrape samples:

- By running the following query, you can pinpoint time series churn by identifying the ten jobs that have created the most time series data in the last hour:topk(10, sum by(namespace, job) (sum_over_time(scrape_series_added[1h])))topk(10, sum by(namespace, job) (sum_over_time(scrape_series_added[1h])))Copy to ClipboardCopied!Toggle word wrapToggle overflow

By running the following query, you can pinpoint time series churn by identifying the ten jobs that have created the most time series data in the last hour:

- Investigate the number of unbound label values assigned to metrics with higher than expected scrape sample counts:If the metrics relate to a user-defined project, review the metrics key-value pairs assigned to your workload. These are implemented through Prometheus client libraries at the application level. Try to limit the number of unbound attributes referenced in your labels.If the metrics relate to a core OpenShift Container Platform project, create a Red Hat support case on theRed Hat Customer Portal.

Investigate the number of unbound label values assigned to metrics with higher than expected scrape sample counts:

- If the metrics relate to a user-defined project, review the metrics key-value pairs assigned to your workload. These are implemented through Prometheus client libraries at the application level. Try to limit the number of unbound attributes referenced in your labels.
- If the metrics relate to a core OpenShift Container Platform project, create a Red Hat support case on theRed Hat Customer Portal.
- Review the TSDB status using the Prometheus HTTP API by following these steps when logged in as a cluster administrator:Get the Prometheus API route URL by running the following command:HOST=$(oc -n openshift-monitoring get route prometheus-k8s -ojsonpath='{.status.ingress[].host}')$HOST=$(oc-nopenshift-monitoring get route prometheus-k8s-ojsonpath='{.status.ingress[].host}')Copy to ClipboardCopied!Toggle word wrapToggle overflowExtract an authentication token by running the following command:TOKEN=[REDACTED_SECRET] whoami -t)$TOKEN=[REDACTED_SECRET] to ClipboardCopied!Toggle word wrapToggle overflowQuery the TSDB status for Prometheus by running the following command:curl -H "Authorization: Bearer $TOKEN" -k "https://$HOST/api/v1/status/tsdb"$curl-H"Authorization: Bearer$TOKEN"-k"https://$HOST/api/v1/status/tsdb"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output"status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
..."status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Review the TSDB status using the Prometheus HTTP API by following these steps when logged in as a cluster administrator:

- Get the Prometheus API route URL by running the following command:HOST=$(oc -n openshift-monitoring get route prometheus-k8s -ojsonpath='{.status.ingress[].host}')$HOST=$(oc-nopenshift-monitoring get route prometheus-k8s-ojsonpath='{.status.ingress[].host}')Copy to ClipboardCopied!Toggle word wrapToggle overflow

Get the Prometheus API route URL by running the following command:

- Extract an authentication token by running the following command:TOKEN=[REDACTED_SECRET] whoami -t)$TOKEN=[REDACTED_SECRET] to ClipboardCopied!Toggle word wrapToggle overflow

Extract an authentication token by running the following command:

- Query the TSDB status for Prometheus by running the following command:curl -H "Authorization: Bearer $TOKEN" -k "https://$HOST/api/v1/status/tsdb"$curl-H"Authorization: Bearer$TOKEN"-k"https://$HOST/api/v1/status/tsdb"Copy to ClipboardCopied!Toggle word wrapToggle overflowExample output"status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
..."status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Query the TSDB status for Prometheus by running the following command:

Example output

```
"status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
...
```

```
"status": "success","data":{"headStats":{"numSeries":507473,
"numLabelPairs":19832,"chunkCount":946298,"minTime":1712253600010,
"maxTime":1712257935346},"seriesCountByMetricName":
[{"name":"etcd_request_duration_seconds_bucket","value":51840},
{"name":"apiserver_request_sli_duration_seconds_bucket","value":47718},
...
```

### 7.11.3. Resolving the KubePersistentVolumeFillingUp alert firing for PrometheusCopy linkLink copied to clipboard!

As a cluster administrator, you can resolve theKubePersistentVolumeFillingUpalert being triggered for Prometheus.

The critical alert fires when a persistent volume (PV) claimed by aprometheus-k8s-*pod in theopenshift-monitoringproject has less than 3% total space remaining. This can cause Prometheus to function abnormally.

There are twoKubePersistentVolumeFillingUpalerts:

- Critical alert: The alert with theseverity="critical"label is triggered when the mounted PV has less than 3% total space remaining.
- Warning alert: The alert with theseverity="warning"label is triggered when the mounted PV has less than 15% total space remaining and is expected to fill up within four days.

To address this issue, you can remove Prometheus time-series database (TSDB) blocks to create more space for the PV.

Prerequisites

- You have access to the cluster as a user with thecluster-admincluster role.
- You have installed the OpenShift CLI (oc).

Procedure

- List the size of all TSDB blocks, sorted from oldest to newest, by running the following command:oc debug <prometheus_k8s_pod_name> -n openshift-monitoring \
-c prometheus --image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'cd /prometheus/;du -hs $(ls -dtr */ | grep -Eo "[0-9|A-Z]{26}")'$oc debug<prometheus_k8s_pod_name>-nopenshift-monitoring\1-c prometheus --image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \2-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'cd /prometheus/;du -hs $(ls -dtr */ | grep -Eo "[0-9|A-Z]{26}")'Copy to ClipboardCopied!Toggle word wrapToggle overflow12Replace<prometheus_k8s_pod_name>with the pod mentioned in theKubePersistentVolumeFillingUpalert description.Example output308M    01HVKMPKQWZYWS8WVDAYQHNMW6
52M     01HVK64DTDA81799TBR9QDECEZ
102M    01HVK64DS7TRZRWF2756KHST5X
140M    01HVJS59K11FBVAPVY57K88Z11
90M     01HVH2A5Z58SKT810EM6B9AT50
152M    01HV8ZDVQMX41MKCN84S32RRZ1
354M    01HV6Q2N26BK63G4RYTST71FBF
156M    01HV664H9J9Z1FTZD73RD1563E
216M    01HTHXB60A7F239HN7S2TENPNS
104M    01HTHMGRXGS0WXA3WATRXHR36B308M    01HVKMPKQWZYWS8WVDAYQHNMW6
52M     01HVK64DTDA81799TBR9QDECEZ
102M    01HVK64DS7TRZRWF2756KHST5X
140M    01HVJS59K11FBVAPVY57K88Z11
90M     01HVH2A5Z58SKT810EM6B9AT50
152M    01HV8ZDVQMX41MKCN84S32RRZ1
354M    01HV6Q2N26BK63G4RYTST71FBF
156M    01HV664H9J9Z1FTZD73RD1563E
216M    01HTHXB60A7F239HN7S2TENPNS
104M    01HTHMGRXGS0WXA3WATRXHR36BCopy to ClipboardCopied!Toggle word wrapToggle overflow

List the size of all TSDB blocks, sorted from oldest to newest, by running the following command:

```
oc debug <prometheus_k8s_pod_name> -n openshift-monitoring \
-c prometheus --image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'cd /prometheus/;du -hs $(ls -dtr */ | grep -Eo "[0-9|A-Z]{26}")'
```

```
-c prometheus --image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
```

```
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'cd /prometheus/;du -hs $(ls -dtr */ | grep -Eo "[0-9|A-Z]{26}")'
```

**12**
  Replace<prometheus_k8s_pod_name>with the pod mentioned in theKubePersistentVolumeFillingUpalert description.

Example output

```
308M    01HVKMPKQWZYWS8WVDAYQHNMW6
52M     01HVK64DTDA81799TBR9QDECEZ
102M    01HVK64DS7TRZRWF2756KHST5X
140M    01HVJS59K11FBVAPVY57K88Z11
90M     01HVH2A5Z58SKT810EM6B9AT50
152M    01HV8ZDVQMX41MKCN84S32RRZ1
354M    01HV6Q2N26BK63G4RYTST71FBF
156M    01HV664H9J9Z1FTZD73RD1563E
216M    01HTHXB60A7F239HN7S2TENPNS
104M    01HTHMGRXGS0WXA3WATRXHR36B
```

```
308M    01HVKMPKQWZYWS8WVDAYQHNMW6
52M     01HVK64DTDA81799TBR9QDECEZ
102M    01HVK64DS7TRZRWF2756KHST5X
140M    01HVJS59K11FBVAPVY57K88Z11
90M     01HVH2A5Z58SKT810EM6B9AT50
152M    01HV8ZDVQMX41MKCN84S32RRZ1
354M    01HV6Q2N26BK63G4RYTST71FBF
156M    01HV664H9J9Z1FTZD73RD1563E
216M    01HTHXB60A7F239HN7S2TENPNS
104M    01HTHMGRXGS0WXA3WATRXHR36B
```

- Identify which and how many blocks could be removed, then remove the blocks. The following example command removes the three oldest Prometheus TSDB blocks from theprometheus-k8s-0pod:oc debug prometheus-k8s-0 -n openshift-monitoring \
-c prometheus --image=$(oc get po -n openshift-monitoring prometheus-k8s-0 \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'ls -latr /prometheus/ | egrep -o "[0-9|A-Z]{26}" | head -3 | \
while read BLOCK; do rm -r /prometheus/$BLOCK; done'$oc debug prometheus-k8s-0-nopenshift-monitoring\-cprometheus--image=$(oc get po-nopenshift-monitoring prometheus-k8s-0\-ojsonpath='{.spec.containers[?(@.name=="prometheus")].image}')\--sh-c'ls -latr /prometheus/ | egrep -o "[0-9|A-Z]{26}" | head -3 | \
while read BLOCK; do rm -r /prometheus/$BLOCK; done'Copy to ClipboardCopied!Toggle word wrapToggle overflow

Identify which and how many blocks could be removed, then remove the blocks. The following example command removes the three oldest Prometheus TSDB blocks from theprometheus-k8s-0pod:

```
oc debug prometheus-k8s-0 -n openshift-monitoring \
-c prometheus --image=$(oc get po -n openshift-monitoring prometheus-k8s-0 \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'ls -latr /prometheus/ | egrep -o "[0-9|A-Z]{26}" | head -3 | \
while read BLOCK; do rm -r /prometheus/$BLOCK; done'
```

```
$ oc debug prometheus-k8s-0 -n openshift-monitoring \
-c prometheus --image=$(oc get po -n openshift-monitoring prometheus-k8s-0 \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') \
-- sh -c 'ls -latr /prometheus/ | egrep -o "[0-9|A-Z]{26}" | head -3 | \
while read BLOCK; do rm -r /prometheus/$BLOCK; done'
```

- Verify the usage of the mounted PV and ensure there is enough space available by running the following command:oc debug <prometheus_k8s_pod_name> -n openshift-monitoring \
--image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') -- df -h /prometheus/$oc debug<prometheus_k8s_pod_name>-nopenshift-monitoring\1--image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \2-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') -- df -h /prometheus/Copy to ClipboardCopied!Toggle word wrapToggle overflow12Replace<prometheus_k8s_pod_name>with the pod mentioned in theKubePersistentVolumeFillingUpalert description.The following example output shows the mounted PV claimed by theprometheus-k8s-0pod that has 63% of space remaining:Example outputStarting pod/prometheus-k8s-0-debug-j82w4 ...
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p4  40G   15G  40G  37% /prometheus

Removing debug pod ...Starting pod/prometheus-k8s-0-debug-j82w4 ...
Filesystem      Size  Used Avail Use% Mounted on/dev/nvme0n1p4  40G   15G  40G  37%/prometheusRemoving debug pod ...Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify the usage of the mounted PV and ensure there is enough space available by running the following command:

```
oc debug <prometheus_k8s_pod_name> -n openshift-monitoring \
--image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') -- df -h /prometheus/
```

```
--image=$(oc get po -n openshift-monitoring <prometheus_k8s_pod_name> \
```

```
-o jsonpath='{.spec.containers[?(@.name=="prometheus")].image}') -- df -h /prometheus/
```

**12**
  Replace<prometheus_k8s_pod_name>with the pod mentioned in theKubePersistentVolumeFillingUpalert description.

The following example output shows the mounted PV claimed by theprometheus-k8s-0pod that has 63% of space remaining:

Example output

```
Starting pod/prometheus-k8s-0-debug-j82w4 ...
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p4  40G   15G  40G  37% /prometheus

Removing debug pod ...
```

```
Starting pod/prometheus-k8s-0-debug-j82w4 ...
Filesystem      Size  Used Avail Use% Mounted on
/dev/nvme0n1p4  40G   15G  40G  37% /prometheus

Removing debug pod ...
```

## 7.12. Diagnosing OpenShift CLI (oc) issuesCopy linkLink copied to clipboard!

### 7.12.1. Understanding OpenShift CLI (oc) log levelsCopy linkLink copied to clipboard!

With the OpenShift CLI (oc), you can create applications and manage OpenShift Container Platform projects from a terminal.

Ifoccommand-specific issues arise, increase theoclog level to output API request, API response, andcurlrequest details generated by the command. This provides a granular view of a particularoccommand’s underlying operation, which in turn might provide insight into the nature of a failure.

oclog levels range from 1 to 10. The following table provides a list ofoclog levels, along with their descriptions.

| Log level | Description |
| --- | --- |
| 1 to 5 | No additional logging to stderr. |
| 6 | Log API requests to stderr. |
| 7 | Log API requests and headers to stderr. |
| 8 | Log API requests, headers, and body, plus API response headers and body to stderr. |
| 9 | Log API requests, headers, and body, API response headers and body, pluscurlrequests to stderr. |
| 10 | Log API requests, headers, and body, API response headers and body, pluscurlrequests to stderr, in v |

1 to 5

No additional logging to stderr.

6

Log API requests to stderr.

7

Log API requests and headers to stderr.

8

Log API requests, headers, and body, plus API response headers and body to stderr.

9

Log API requests, headers, and body, API response headers and body, pluscurlrequests to stderr.

10

Log API requests, headers, and body, API response headers and body, pluscurlrequests to stderr, in verbose detail.

### 7.12.2. Specifying OpenShift CLI (oc) log levelsCopy linkLink copied to clipboard!

You can investigate OpenShift CLI (oc) issues by increasing the command’s log level.

The OpenShift Container Platform user’s current session token is typically included in loggedcurlrequests where required. You can also obtain the current user’s session token manually, for use when testing aspects of anoccommand’s underlying process step-by-step.

Prerequisites

- Install the OpenShift CLI (oc).

Procedure

- Specify theoclog level when running anoccommand:oc <command> --loglevel <log_level>$oc<command>--loglevel<log_level>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<command>Specifies the command you are running.<log_level>Specifies the log level to apply to the command.

Specify theoclog level when running anoccommand:

where:

**<command>**
  Specifies the command you are running.

**<log_level>**
  Specifies the log level to apply to the command.
- To obtain the current user’s session token, run the following command:oc whoami -t$ocwhoami-tCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputsha256~RCV3Qcn7H-OEfqCGVI0CvnZ6...sha256~RCV3Qcn7H-OEfqCGVI0CvnZ6...Copy to ClipboardCopied!Toggle word wrapToggle overflow

To obtain the current user’s session token, run the following command:

Example output
