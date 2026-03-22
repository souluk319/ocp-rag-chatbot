<!-- source: ocp_builds.md -->

# Builds

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/builds_using_buildconfig/understanding-image-builds
---

# Chapter 1. Understanding image builds

## 1.1. BuildsCopy linkLink copied to clipboard!

A build is the process of transforming input parameters into a resulting object. Most often, the process is used to transform input parameters or source code into a runnable image. ABuildConfigobject is the definition of the entire build process.

OpenShift Container Platform uses Kubernetes by creating containers from build images and pushing them to a container image registry.

Build objects share common characteristics including inputs for a build, the requirement to complete a build process, logging the build process, publishing resources from successful builds, and publishing the final status of the build. Builds take advantage of resource restrictions, specifying limitations on resources such as CPU usage, memory usage, and build or pod execution time.

The OpenShift Container Platform build system provides extensible support for build strategies that are based on selectable types specified in the build API. There are three primary build strategies available:

- Docker build
- Source-to-image (S2I) build
- Custom build

By default, docker builds and S2I builds are supported.

The resulting object of a build depends on the builder used to create it. For docker and S2I builds, the resulting objects are runnable images. For custom builds, the resulting objects are whatever the builder image author has specified.

Additionally, the pipeline build strategy can be used to implement sophisticated workflows:

- Continuous integration
- Continuous deployment

### 1.1.1. Docker buildCopy linkLink copied to clipboard!

OpenShift Container Platform uses Buildah to build a container image from a Dockerfile. For more information on building container images with Dockerfiles, seethe Dockerfile reference documentation.

If you set Docker build arguments by using thebuildArgsarray, seeUnderstand how ARG and FROM interactin the Dockerfile reference documentation.

### 1.1.2. Source-to-image buildCopy linkLink copied to clipboard!

Source-to-image (S2I) is a tool for building reproducible container images. It produces ready-to-run images by injecting application source into a container image and assembling a new image. The new image incorporates the base image, the builder, and built source and is ready to use with thebuildah runcommand. S2I supports incremental builds, which re-use previously downloaded dependencies, previously built artifacts, and so on.

### 1.1.3. Custom buildCopy linkLink copied to clipboard!

The custom build strategy allows developers to define a specific builder image responsible for the entire build process. Using your own builder image allows you to customize your build process.

A custom builder image is a plain container image embedded with build process logic, for example for building RPMs or base images.

Custom builds run with a high level of privilege and are not available to users by default. Only users who can be trusted with cluster administration permissions should be granted access to run custom builds.

### 1.1.4. Pipeline buildCopy linkLink copied to clipboard!

The Pipeline build strategy is deprecated in OpenShift Container Platform 4. Equivalent and improved functionality is present in the OpenShift Container Platform Pipelines based on Tekton.

Jenkins images on OpenShift Container Platform are fully supported and users should follow Jenkins user documentation for defining theirjenkinsfilein a job or store it in a Source Control Management system.

The Pipeline build strategy allows developers to define a Jenkins pipeline for use by the Jenkins pipeline plugin. The build can be started, monitored, and managed by OpenShift Container Platform in the same way as any other build type.

Pipeline workflows are defined in ajenkinsfile, either embedded directly in the build configuration, or supplied in a Git repository and referenced by the build configuration.
