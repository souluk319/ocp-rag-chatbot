<!-- source: ocp_rhcos.md -->

# Architecture

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/architecture/architecture-rhcos
---

# Chapter 8. Red Hat Enterprise Linux CoreOS (RHCOS)

## 8.1. About RHCOSCopy linkLink copied to clipboard!

Red Hat Enterprise Linux CoreOS (RHCOS) represents the next generation of single-purpose container operating system technology by providing the quality standards of Red Hat Enterprise Linux (RHEL) with automated, remote upgrade features.

RHCOS is supported only as a component of OpenShift Container Platform 4.17 for all OpenShift Container Platform machines. RHCOS is the only supported operating system for OpenShift Container Platform control plane, or master, machines. While RHCOS is the default operating system for all cluster machines, you can create compute machines, which are also known as worker machines, that use RHEL as their operating system. There are two general ways RHCOS is deployed in OpenShift Container Platform 4.17:

- If you install your cluster on infrastructure that the installation program provisions, RHCOS images are downloaded to the target platform during installation. Suitable Ignition config files, which control the RHCOS configuration, are also downloaded and used to deploy the machines.
- If you install your cluster on infrastructure that you manage, you must follow the installation documentation to obtain the RHCOS images, generate Ignition config files, and use the Ignition config files to provision your machines.

### 8.1.1. Key RHCOS featuresCopy linkLink copied to clipboard!

The following list describes key features of the RHCOS operating system:

- Based on RHEL: The underlying operating system consists primarily of RHEL components. The same quality, security, and control measures that support RHEL also support RHCOS. For example, RHCOS software is in RPM packages, and each RHCOS system starts up with a RHEL kernel and a set of services that are managed by the systemd init system.
- Controlled immutability: Although it contains RHEL components, RHCOS is designed to be managed more tightly than a default RHEL installation. Management is performed remotely from the OpenShift Container Platform cluster. When you set up your RHCOS machines, you can modify only a few system settings. This controlled immutability allows OpenShift Container Platform to store the latest state of RHCOS systems in the cluster so it is always able to create additional machines and perform updates based on the latest RHCOS configurations.
- CRI-O container runtime: Although RHCOS contains features for running the OCI- and libcontainer-formatted containers that Docker requires, it incorporates the CRI-O container engine instead of the Docker container engine. By focusing on features needed by Kubernetes platforms, such as OpenShift Container Platform, CRI-O can offer specific compatibility with different Kubernetes versions. CRI-O also offers a smaller footprint and reduced attack surface than is possible with container engines that offer a larger feature set. At the moment, CRI-O is the only engine available within OpenShift Container Platform clusters.CRI-O can use either the runC or crun container runtime to start and manage containers. For information about how to enable crun, see the documentation for creating aContainerRuntimeConfigCR.

CRI-O container runtime: Although RHCOS contains features for running the OCI- and libcontainer-formatted containers that Docker requires, it incorporates the CRI-O container engine instead of the Docker container engine. By focusing on features needed by Kubernetes platforms, such as OpenShift Container Platform, CRI-O can offer specific compatibility with different Kubernetes versions. CRI-O also offers a smaller footprint and reduced attack surface than is possible with container engines that offer a larger feature set. At the moment, CRI-O is the only engine available within OpenShift Container Platform clusters.

CRI-O can use either the runC or crun container runtime to start and manage containers. For information about how to enable crun, see the documentation for creating aContainerRuntimeConfigCR.

- Set of container tools: For tasks such as building, copying, and otherwise managing containers, RHCOS replaces the Docker CLI tool with a compatible set of container tools. The podman CLI tool supports many container runtime features, such as running, starting, stopping, listing, and removing containers and container images. The skopeo CLI tool can copy, authenticate, and sign images. You can use thecrictlCLI tool to work with containers and pods from the CRI-O container engine. While direct use of these tools in RHCOS is discouraged, you can use them for debugging purposes.
- rpm-ostree upgrades: RHCOS features transactional upgrades using therpm-ostreesystem. Updates are delivered by means of container images and are part of the OpenShift Container Platform update process. When deployed, the container image is pulled, extracted, and written to disk, then the bootloader is modified to boot into the new version. The machine will reboot into the update in a rolling manner to ensure cluster capacity is minimally impacted.
- bootupd firmware and bootloader updater: Package managers and hybrid systems such asrpm-ostreedo not update the firmware or the bootloader. Withbootupd, RHCOS users have access to a cross-distribution, system-agnostic update tool that manages firmware and boot updates in UEFI and legacy BIOS boot modes that run on modern architectures, such as x86_64, ppc64le, and aarch64.For information about how to installbootupd, see the documentation forUpdating the bootloader using bootupd.

bootupd firmware and bootloader updater: Package managers and hybrid systems such asrpm-ostreedo not update the firmware or the bootloader. Withbootupd, RHCOS users have access to a cross-distribution, system-agnostic update tool that manages firmware and boot updates in UEFI and legacy BIOS boot modes that run on modern architectures, such as x86_64, ppc64le, and aarch64.

For information about how to installbootupd, see the documentation forUpdating the bootloader using bootupd.

- Updated through the Machine Config Operator: In OpenShift Container Platform, the Machine Config Operator handles operating system upgrades. Instead of upgrading individual packages, as is done withyumupgrades,rpm-ostreedelivers upgrades of the OS as an atomic unit. The new OS deployment is staged during upgrades and goes into effect on the next reboot. If something goes wrong with the upgrade, a single rollback and reboot returns the system to the previous state. RHCOS upgrades in OpenShift Container Platform are performed during cluster updates.

For RHCOS systems, the layout of therpm-ostreefile system has the following characteristics:

- /usris where the operating system binaries and libraries are stored and is read-only. We do not support altering this.
- /etc,/boot,/varare writable on the system but only intended to be altered by the Machine Config Operator.
- /var/lib/containersis the graph storage location for storing container images.

### 8.1.2. Choosing how to configure RHCOSCopy linkLink copied to clipboard!

RHCOS is designed to deploy on an OpenShift Container Platform cluster with a minimal amount of user configuration. In its most basic form, this consists of:

- Starting with a provisioned infrastructure, such as on AWS, or provisioning the infrastructure yourself.
- Supplying a few pieces of information, such as credentials and cluster name, in aninstall-config.yamlfile when runningopenshift-install.

Because RHCOS systems in OpenShift Container Platform are designed to be fully managed from the OpenShift Container Platform cluster after that, directly changing an RHCOS machine is discouraged. Although limited direct access to RHCOS machines cluster can be accomplished for debugging purposes, you should not directly configure RHCOS systems. Instead, if you need to add or change features on your OpenShift Container Platform nodes, consider making changes in the following ways:

- Kubernetes workload objects, such as DaemonSet and Deployment: If you need to add services or other user-level features to your cluster, consider adding them as Kubernetes workload objects. Keeping those features outside of specific node configurations is the best way to reduce the risk of breaking the cluster on subsequent upgrades.
- Day-2 customizations: If possible, bring up a cluster without making any customizations to cluster nodes and make necessary node changes after the cluster is up. Those changes are easier to track later and less likely to break updates. Creating machine configs or modifying Operator custom resources are ways of making these customizations.
- Day-1 customizations: For customizations that you must implement when the cluster first comes up, there are ways of modifying your cluster so changes are implemented on first boot. Day-1 customizations can be done through Ignition configs and manifest files duringopenshift-installor by adding boot options during ISO installs provisioned by the user.

Here are examples of customizations you could do on day 1:

- Kernel arguments: If particular kernel features or tuning is needed on nodes when the cluster first boots.
- Disk encryption: If your security needs require that the root file system on the nodes are encrypted, such as with FIPS support.
- Kernel modules: If a particular hardware device, such as a network card or video card, does not have a usable module available by default in the Linux kernel.
- Chronyd: If you want to provide specific clock settings to your nodes, such as the location of time servers.

To accomplish these tasks, you can augment theopenshift-installprocess to include additional objects such asMachineConfigobjects. Those procedures that result in creating machine configs can be passed to the Machine Config Operator after the cluster is up.

- The Ignition config files that the installation program generates contain certificates that expire after 24 hours, which are then renewed at that time. If the cluster is shut down before renewing the certificates and the cluster is later restarted after the 24 hours have elapsed, the cluster automatically recovers the expired certificates. The exception is that you must manually approve the pendingnode-bootstrappercertificate signing requests (CSRs) to recover kubelet certificates. See the documentation forRecovering from expired control plane certificatesfor more information.
- It is recommended that you use Ignition config files within 12 hours after they are generated because the 24-hour certificate rotates from 16 to 22 hours after the cluster is installed. By using the Ignition config files within 12 hours, you can avoid installation failure if the certificate update runs during installation.

### 8.1.3. Choosing how to deploy RHCOSCopy linkLink copied to clipboard!

Differences between RHCOS installations for OpenShift Container Platform are based on whether you are deploying on an infrastructure provisioned by the installer or by the user:

[REDACTED_ACCOUNT] Installer-provisioned: Some cloud environments offer preconfigured infrastructures that allow you to bring up an OpenShift Container Platform cluster with minimal configuration. For these types of installations, you can supply Ignition configs that place content on each node so it is there when the cluster first boots.
- User-provisioned: If you are provisioning your own infrastructure, you have more flexibility in how you add content to a RHCOS node. For example, you could add kernel arguments when you boot the RHCOS ISO installer to install each system. However, in most cases where configuration is required on the operating system itself, it is best to provide that configuration through an Ignition config.

The Ignition facility runs only when the RHCOS system is first set up. After that, Ignition configs can be supplied later using the machine config.

### 8.1.4. About IgnitionCopy linkLink copied to clipboard!

Ignition is the utility that is used by RHCOS to manipulate disks during initial configuration. It completes common disk tasks, including partitioning disks, formatting partitions, writing files, and configuring users. On first boot, Ignition reads its configuration from the installation media or the location that you specify and applies the configuration to the machines.

Whether you are installing your cluster or adding machines to it, Ignition always performs the initial configuration of the OpenShift Container Platform cluster machines. Most of the actual system setup happens on each machine itself. For each machine, Ignition takes the RHCOS image and boots the RHCOS kernel. Options on the kernel command line identify the type of deployment and the location of the Ignition-enabled initial RAM disk (initramfs).

#### 8.1.4.1. How Ignition worksCopy linkLink copied to clipboard!

To create machines by using Ignition, you need Ignition config files. The OpenShift Container Platform installation program creates the Ignition config files that you need to deploy your cluster. These files are based on the information that you provide to the installation program directly or through aninstall-config.yamlfile.

The way that Ignition configures machines is similar to how tools likecloud-initor Linux Anacondakickstartconfigure systems, but with some important differences:

- Ignition runs from an initial RAM disk that is separate from the system you are installing to. Because of that, Ignition can repartition disks, set up file systems, and perform other changes to the machine’s permanent file system. In contrast, cloud-init runs as part of a machine init system when the system boots, so making foundational changes to things like disk partitions cannot be done as easily. With cloud-init, it is also difficult to reconfigure the boot process while you are in the middle of the node boot process.
- Ignition is meant to initialize systems, not change existing systems. After a machine initializes and the kernel is running from the installed system, the Machine Config Operator from the OpenShift Container Platform cluster completes all future machine configuration.
- Instead of completing a defined set of actions, Ignition implements a declarative configuration. It checks that all partitions, files, services, and other items are in place before the new machine starts. It then makes the changes, like copying files to disk that are necessary for the new machine to meet the specified configuration.
- After Ignition finishes configuring a machine, the kernel keeps running but discards the initial RAM disk and pivots to the installed system on disk. All of the new system services and other features start without requiring a system reboot.
- Because Ignition confirms that all new machines meet the declared configuration, you cannot have a partially configured machine. If a machine setup fails, the initialization process does not finish, and Ignition does not start the new machine. Your cluster will never contain partially configured machines. If Ignition cannot complete, the machine is not added to the cluster. You must add a new machine instead. This behavior prevents the difficult case of debugging a machine when the results of a failed configuration task are not known until something that depended on it fails at a later date.
- If there is a problem with an Ignition config that causes the setup of a machine to fail, Ignition will not try to use the same config to set up another machine. For example, a failure could result from an Ignition config made up of a parent and child config that both want to create the same file. A failure in such a case would prevent that Ignition config from being used again to set up an other machines until the problem is resolved.
- If you have multiple Ignition config files, you get a union of that set of configs. Because Ignition is declarative, conflicts between the configs could cause Ignition to fail to set up the machine. The order of information in those files does not matter. Ignition will sort and implement each setting in ways that make the most sense. For example, if a file needs a directory several levels deep, if another file needs a directory along that path, the later file is created first. Ignition sorts and creates all files, directories, and links by depth.
- Because Ignition can start with a completely empty hard disk, it can do something cloud-init cannot do: set up systems on bare metal from scratch using features such as PXE boot. In the bare metal case, the Ignition config is injected into the boot partition so that Ignition can find it and configure the system correctly.

#### 8.1.4.2. The Ignition sequenceCopy linkLink copied to clipboard!

The Ignition process for an RHCOS machine in an OpenShift Container Platform cluster involves the following steps:

- The machine gets its Ignition config file. Control plane machines get their Ignition config files from the bootstrap machine, and worker machines get Ignition config files from a control plane machine.
- Ignition creates disk partitions, file systems, directories, and links on the machine. It supports RAID arrays but does not support LVM volumes.
- Ignition mounts the root of the permanent file system to the/sysrootdirectory in the initramfs and starts working in that/sysrootdirectory.
- Ignition configures all defined file systems and sets them up to mount appropriately at runtime.
- Ignition runssystemdtemporary files to populate required files in the/vardirectory.
- Ignition runs the Ignition config files to set up users, systemd unit files, and other configuration files.
- Ignition unmounts all components in the permanent system that were mounted in the initramfs.
- Ignition starts up the init process of the new machine, which in turn starts up all other services on the machine that run during system boot.

At the end of this process, the machine is ready to join the cluster and does not require a reboot.

## 8.2. Viewing Ignition configuration filesCopy linkLink copied to clipboard!

To see the Ignition config file used to deploy the bootstrap machine, run the following command:

After you answer a few questions, thebootstrap.ign,master.ign, andworker.ignfiles appear in the directory you entered.

To see the contents of thebootstrap.ignfile, pipe it through thejqfilter. Here’s a snippet from that file:

```
cat $HOME/testconfig/bootstrap.ign | jq
{
  "ignition": {
    "version": "3.2.0"
  },
  "passwd": {
    "users": [
      {
        "name": "core",
        "sshAuthorizedKeys": [
          "ssh-rsa AAAAB3NzaC1yc...."
        ]
      }
    ]
  },
  "storage": {
    "files": [
      {
        "overwrite": false,
        "path": "/etc/motd",
        "user": {
          "name": "root"
        },
        "append": [
          {
            "source": "data:text/plain;charset=utf-8;base64,VGhpcyBpcyB0aGUgYm9vdHN0cmFwIG5vZGU7IGl0IHdpbGwgYmUgZGVzdHJveWVkIHdoZW4gdGhlIG1hc3RlciBpcyBmdWxseSB1cC4KClRoZSBwcmltYXJ5IHNlcnZpY2VzIGFyZSByZWxlYXNlLWltYWdlLnNlcnZpY2UgZm9sbG93ZWQgYnkgYm9vdGt1YmUuc2VydmljZS4gVG8gd2F0Y2ggdGhlaXIgc3RhdHVzLCBydW4gZS5nLgoKICBqb3VybmFsY3RsIC1iIC1mIC11IHJlbGVhc2UtaW1hZ2Uuc2VydmljZSAtdSBib290a3ViZS5zZXJ2aWNlCg=="
          }
        ],
        "mode": 420
      },
...
```

```
$ cat $HOME/testconfig/bootstrap.ign | jq
{
  "ignition": {
    "version": "3.2.0"
  },
  "passwd": {
    "users": [
      {
        "name": "core",
        "sshAuthorizedKeys": [
          "ssh-rsa AAAAB3NzaC1yc...."
        ]
      }
    ]
  },
  "storage": {
    "files": [
      {
        "overwrite": false,
        "path": "/etc/motd",
        "user": {
          "name": "root"
        },
        "append": [
          {
            "source": "data:text/plain;charset=utf-8;base64,VGhpcyBpcyB0aGUgYm9vdHN0cmFwIG5vZGU7IGl0IHdpbGwgYmUgZGVzdHJveWVkIHdoZW4gdGhlIG1hc3RlciBpcyBmdWxseSB1cC4KClRoZSBwcmltYXJ5IHNlcnZpY2VzIGFyZSByZWxlYXNlLWltYWdlLnNlcnZpY2UgZm9sbG93ZWQgYnkgYm9vdGt1YmUuc2VydmljZS4gVG8gd2F0Y2ggdGhlaXIgc3RhdHVzLCBydW4gZS5nLgoKICBqb3VybmFsY3RsIC1iIC1mIC11IHJlbGVhc2UtaW1hZ2Uuc2VydmljZSAtdSBib290a3ViZS5zZXJ2aWNlCg=="
          }
        ],
        "mode": 420
      },
...
```

To decode the contents of a file listed in thebootstrap.ignfile, pipe the base64-encoded data string representing the contents of that file to thebase64 -dcommand. Here’s an example using the contents of the/etc/motdfile added to the bootstrap machine from the output shown above:

Example output

```
This is the bootstrap node; it will be destroyed when the master is fully up.

The primary services are release-image.service followed by bootkube.service. To watch their status, run e.g.

  journalctl -b -f -u release-image.service -u bootkube.service
```

```
This is the bootstrap node; it will be destroyed when the master is fully up.

The primary services are release-image.service followed by bootkube.service. To watch their status, run e.g.

  journalctl -b -f -u release-image.service -u bootkube.service
```

Repeat those commands on themaster.ignandworker.ignfiles to see the source of Ignition config files for each of those machine types.  You should see a line like the following for theworker.ign, identifying how it gets its Ignition config from the bootstrap machine:

Here are a few things you can learn from thebootstrap.ignfile:

- Format: The format of the file is defined in theIgnition config spec. Files of the same format are used later by the MCO to merge changes into a machine’s configuration.
- Contents: Because the bootstrap machine serves the Ignition configs for other machines, both master and worker machine Ignition config information is stored in thebootstrap.ign, along with the bootstrap machine’s configuration.
- Size: The file is more than 1300 lines long, with path to various types of resources.
- The content of each file that will be copied to the machine is actually encoded into data URLs, which tends to make the content a bit clumsy to read. (Use thejqandbase64commands shown previously to make the content more readable.)
- Configuration: The different sections of the Ignition config file are generally meant to contain files that are just dropped into a machine’s file system, rather than commands to modify existing files. For example, instead of having a section on NFS that configures that service, you would just add an NFS configuration file, which would then be started by the init process when the system comes up.
- users: A user namedcoreis created, with your SSH key assigned to that user. This allows you to log in to the cluster with that user name and your credentials.
- storage: The storage section identifies files that are added to each machine. A few notable files include/root/.docker/config.json(which provides credentials your cluster needs to pull from container image registries) and a bunch of manifest files in/opt/openshift/manifeststhat are used to configure your cluster.
- systemd: Thesystemdsection holds content used to createsystemdunit files. Those files are used to start up services at boot time, as well as manage those services on running systems.
- Primitives: Ignition also exposes low-level primitives that other tools can build on.

## 8.3. Changing Ignition configs after installationCopy linkLink copied to clipboard!

Machine config pools manage a cluster of nodes and their corresponding machine configs. Machine configs contain configuration information for a cluster. To list all machine config pools that are known:

Example output

```
NAME   CONFIG                                  UPDATED UPDATING DEGRADED
master master-1638c1aea398413bb918e76632f20799 False   False    False
worker worker-2feef4f8288936489a5a832ca8efe953 False   False    False
```

```
NAME   CONFIG                                  UPDATED UPDATING DEGRADED
master master-1638c1aea398413bb918e76632f20799 False   False    False
worker worker-2feef4f8288936489a5a832ca8efe953 False   False    False
```

To list all machine configs:

Example output

```
NAME                                      GENERATEDBYCONTROLLER   IGNITIONVERSION   CREATED   OSIMAGEURL

00-master                                 4.0.0-0.150.0.0-dirty   3.2.0             16m
00-master-ssh                             4.0.0-0.150.0.0-dirty                     16m
00-worker                                 4.0.0-0.150.0.0-dirty   3.2.0             16m
00-worker-ssh                             4.0.0-0.150.0.0-dirty                     16m
01-master-kubelet                         4.0.0-0.150.0.0-dirty   3.2.0             16m
01-worker-kubelet                         4.0.0-0.150.0.0-dirty   3.2.0             16m
master-1638c1aea398413bb918e76632f20799   4.0.0-0.150.0.0-dirty   3.2.0             16m
worker-2feef4f8288936489a5a832ca8efe953   4.0.0-0.150.0.0-dirty   3.2.0             16m
```

```
NAME                                      GENERATEDBYCONTROLLER   IGNITIONVERSION   CREATED   OSIMAGEURL

00-master                                 4.0.0-0.150.0.0-dirty   3.2.0             16m
00-master-ssh                             4.0.0-0.150.0.0-dirty                     16m
00-worker                                 4.0.0-0.150.0.0-dirty   3.2.0             16m
00-worker-ssh                             4.0.0-0.150.0.0-dirty                     16m
01-master-kubelet                         4.0.0-0.150.0.0-dirty   3.2.0             16m
01-worker-kubelet                         4.0.0-0.150.0.0-dirty   3.2.0             16m
master-1638c1aea398413bb918e76632f20799   4.0.0-0.150.0.0-dirty   3.2.0             16m
worker-2feef4f8288936489a5a832ca8efe953   4.0.0-0.150.0.0-dirty   3.2.0             16m
```

The Machine Config Operator acts somewhat differently than Ignition when it comes to applying these machine configs. The machine configs are read in order (from 00* to 99*). Labels inside the machine configs identify the type of node each is for (master or worker). If the same file appears in multiple machine config files, the last one wins. So, for example, any file that appears in a 99* file would replace the same file that appeared in a 00* file. The inputMachineConfigobjects are unioned into a "rendered"MachineConfigobject, which will be used as a target by the operator and is the value you can see in the machine config pool.

To see what files are being managed from a machine config, look for "Path:" inside a particularMachineConfigobject. For example:

Example output

```
Path:            /etc/containers/registries.conf
            Path:            /etc/containers/storage.conf
            Path:            /etc/crio/crio.conf
```

```
Path:            /etc/containers/registries.conf
            Path:            /etc/containers/storage.conf
            Path:            /etc/crio/crio.conf
```

Be sure to give the machine config file a later name (such as 10-worker-container-runtime). Keep in mind that the content of each file is in URL-style data. Then apply the new machine config to the cluster.
