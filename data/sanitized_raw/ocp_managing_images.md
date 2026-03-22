<!-- source: ocp_managing_images.md -->

# Troubleshooting - Images

---
Source: https://docs.redhat.com/en/documentation/openshift_container_platform/4.17/html/images/managing-images
---

# Chapter 5. Managing images

## 5.1. Managing images overviewCopy linkLink copied to clipboard!

Image streams in OpenShift Container Platform provide a layer of abstraction over container images, enabling automation for your CI/CD pipelines. You can configure builds and deployments to watch image streams and automatically trigger new builds or deployments when images are updated.

The main advantage of using image streams is the automation they enable for your continuous integration and continuous delivery (CI/CD) pipelines. For example:

- Image streams allow OpenShift Container Platform resources like Builds and Deployments to "watch" them.
- When a new image is added to the stream, or when an existing tag is modified to point to a new image, the watching resources receive notifications.
- When notifications are received, the watching resources can automatically react by performing a new build or a new deployment.

## 5.2. Tagging imagesCopy linkLink copied to clipboard!

Image tags identify specific versions of container images in image streams. You can use image tags to organize images and control which versions your builds and deployments use.

### 5.2.1. Understanding image tags in image streamsCopy linkLink copied to clipboard!

Image tags in OpenShift Container Platform help you organize, identify, and reference specific versions of container images in image streams. Tags are human-readable labels that act as pointers to particular image layers and digests.

Tags function as mutable pointers within an image stream. When a new image is imported or tagged into the stream, the tag is updated to point to the new image’s immutable SHA digest. A single image digest can have multiple tags simultaneously assigned to it. For example, the:v3.11.59-2and:latesttags are assigned to the same image digest.

Tags offer two main benefits:

- Tags serve as the primary mechanism for builds and deployments to request a specific version of an image from an image stream.
- Tags help maintain clarity and allow for easy promotion of images between environments. For example, you can promote an image from the:testtag to the:prodtag.

While image tags are primarily used for referencing images in configurations, OpenShift Container Platform provides theoc tagcommand for managing tags directly within image streams. This command is similar to thepodman tagordocker tagcommands, but it operates on image streams instead of directly on local images. It is used to create a new tag pointer or update an existing tag pointer within an image stream to point to a new image.

Image tags are appended to the image name or image stream name by using a colon (:) as a separator.

| Context | Syntax Format | Example |
| --- | --- | --- |
| External Registry | <registry_path>:<tag> | registry.access.redhat.com/openshift3/jenkins-2-rhel7:v3.11.59-2 |
| Local Image Stream | <image_stream_name>:<tag> | jenkins:latest |

External Registry

<registry_path>:<tag>

registry.access.redhat.com/openshift3/jenkins-2-rhel7:v3.11.59-2

Local Image Stream

<image_stream_name>:<tag>

jenkins:latest

### 5.2.2. Image tag conventionsCopy linkLink copied to clipboard!

Image tag naming conventions in OpenShift Container Platform provide guidelines for creating tags that enable effective image pruning and maintain manageable image streams. Use consistent naming patterns to avoid tags that point to single revisions and never update.

Tags that are too specific effectively pin the tag to a single image revision that is never updated. For example, if you create a tag namedv2.0.1-may-2019, the tag points to just one revision of an image and is never updated. If you use default image pruning options, such an image is never removed.

In very large clusters, the schema of creating new tags for every revised image could eventually fill up the etcd datastore with excess tag metadata for images that are long outdated. If the tag is namedv2.0, image revisions are more likely. This results in longer tag history and, therefore, the image pruner is more likely to remove old and unused images.

To ensure proper garbage collection, use broader, more generic tags that are designed to be updated when a new image revision is built. The following table provides some recommended tagging conventions using the format<image_name>:<image_tag>.

| Description | Example |
| --- | --- |
| Major/Minor Version(Ideal for mutable pointers) | myimage:v2.0 |
| Full Revision(Often used for tracking, but requires manual pruning) | myimage:v2.0.1 |
| Architecture | myimage:v2.0-x86_64 |
| Base image | myimage:v1.2-centos7 |
| Latest | myimage:latest |
| Latest stable | myimage:stable |

Major/Minor Version(Ideal for mutable pointers)

myimage:v2.0

Full Revision(Often used for tracking, but requires manual pruning)

myimage:v2.0.1

Architecture

myimage:v2.0-x86_64

Base image

myimage:v1.2-centos7

Latest

myimage:latest

Latest stable

myimage:stable

If your team requires the use of unique, date-specific, or highly revisioned tags likev2.0.1-may-2019, you must periodically inspect old and unsupported images andistagsand remove them. Otherwise, you can experience increasing resource usage caused by retaining old images.

### 5.2.3. Adding tags to image streamsCopy linkLink copied to clipboard!

To organize images and create aliases for specific versions or automatically track changes to source tags in OpenShift Container Platform, you can add tags to image streams with theoc tagcommand.

There are two types of tags available in OpenShift Container Platform:

- Permanent tags: A permanent tag points to a specific image in time. If the permanent tag is in use and the source changes, the tag does not change for the destination.
- Tracking tags: A tracking tag means that the destination tag’s metadata is updated during the import of the source tag.

The default behavior creates a permanent tag that is pinned to an image ID.

Procedure

- Optional: Add a tag to an image stream by entering the following command. The default behavior creates a permanent tag that is pinned to an image ID:oc tag <source_reference> <destination_image_stream>:<destination_tag>$oc tag<source_reference><destination_image_stream>:<destination_tag>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, to configure therubyimage streamstatic-2.0tag to always refer to the specific image that theruby:2.0tag points to now, enter the following command:oc tag ruby:2.0 ruby:static-2.0$oc tag ruby:2.0 ruby:static-2.0Copy to ClipboardCopied!Toggle word wrapToggle overflowThis creates a new image stream tag namedstatic-2.0in therubyimage stream. The new tag directly references the image ID that theruby:2.0image stream tag pointed to at the timeoc tagwas run, and the image it points to never changes.

Optional: Add a tag to an image stream by entering the following command. The default behavior creates a permanent tag that is pinned to an image ID:

For example, to configure therubyimage streamstatic-2.0tag to always refer to the specific image that theruby:2.0tag points to now, enter the following command:

This creates a new image stream tag namedstatic-2.0in therubyimage stream. The new tag directly references the image ID that theruby:2.0image stream tag pointed to at the timeoc tagwas run, and the image it points to never changes.

- Optional: Use the--alias=trueflag to create a tracking tag. This ensures the destination tag automatically updates (tracks) when the source tag changes to point to a new image. For example, to ensure that theruby:latesttag always reflects whatever image is currently tagged asruby:2.0, enter the following command:oc tag --alias=true ruby:2.0 ruby:latest$oc tag--alias=true ruby:2.0 ruby:latestCopy to ClipboardCopied!Toggle word wrapToggle overflowA Tracking Tag created with--alias=trueautomatically updates its image ID whenever the source tag changes. Use thelatestorstabletracking tags for creating common, long-lived aliases. This tracking behavior only works correctly within a single image stream. Trying to create a cross-image stream alias produces an error.

Optional: Use the--alias=trueflag to create a tracking tag. This ensures the destination tag automatically updates (tracks) when the source tag changes to point to a new image. For example, to ensure that theruby:latesttag always reflects whatever image is currently tagged asruby:2.0, enter the following command:

A Tracking Tag created with--alias=trueautomatically updates its image ID whenever the source tag changes. Use thelatestorstabletracking tags for creating common, long-lived aliases. This tracking behavior only works correctly within a single image stream. Trying to create a cross-image stream alias produces an error.

- Optional: Use the--scheduled=trueflag to have the destination tag be refreshed, or re-imported, periodically. The period is configured globally at the system level. For example:oc tag <source_reference> <destination_image_stream>:<destination_tag> --scheduled=true$oc tag<source_reference><destination_image_stream>:<destination_tag>--scheduled=trueCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Use the--scheduled=trueflag to have the destination tag be refreshed, or re-imported, periodically. The period is configured globally at the system level. For example:

- Optional: Use the--referenceflag to create an image stream tag that is not imported. The tag permanently points to the source location, regardless of changes to the source image. For example:oc tag <source_reference> <destination_image_stream>:<destination_tag> --reference$oc tag<source_reference><destination_image_stream>:<destination_tag>--referenceCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Use the--referenceflag to create an image stream tag that is not imported. The tag permanently points to the source location, regardless of changes to the source image. For example:

- Optional. Use the--insecureflag if the source registry is not secured with a valid HTTPS certificate. This flag tells the image stream to skip certificate verification during the import progress. For example:oc tag <source_reference> <destination_image_stream>:<destination_tag> --insecure$oc tag<source_reference><destination_image_stream>:<destination_tag>--insecureCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional. Use the--insecureflag if the source registry is not secured with a valid HTTPS certificate. This flag tells the image stream to skip certificate verification during the import progress. For example:

- Optional: Use the--reference-policy=localflag to instruct OpenShift Container Platform to always fetch the tagged image from the integrated registry. The registry uses the pull-through feature to serve the image to the client. By default, the image blobs are mirrored locally by the registry. As a result, they can be pulled more quickly the next time they are needed. The--reference-policy=localflag also allows for pulling from insecure registries without a need to supply the--insecureflag to the container runtime provided that the image stream has an insecure annotation or the tag has an insecure import policy. For example:oc tag <source_reference> <destination_image_stream>:<destination_tag> --reference-policy=local$oc tag<source_reference><destination_image_stream>:<destination_tag>--reference-policy=localCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Use the--reference-policy=localflag to instruct OpenShift Container Platform to always fetch the tagged image from the integrated registry. The registry uses the pull-through feature to serve the image to the client. By default, the image blobs are mirrored locally by the registry. As a result, they can be pulled more quickly the next time they are needed. The--reference-policy=localflag also allows for pulling from insecure registries without a need to supply the--insecureflag to the container runtime provided that the image stream has an insecure annotation or the tag has an insecure import policy. For example:

### 5.2.4. Removing tags from image streamsCopy linkLink copied to clipboard!

To keep your image streams clean and maintain organized image references in OpenShift Container Platform, you can remove unused or outdated image stream tags. Remove tags by using theoc delete istagoroc tag -dcommands.

Procedure

- Remove a tag from an image stream by entering the following command:oc delete istag/<name>:<tag>$oc delete istag/<name>:<tag>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, to remove theruby:latesttag from therubyimage stream, enter the following command:oc delete istag/ruby:latest$oc delete istag/ruby:latestCopy to ClipboardCopied!Toggle word wrapToggle overflow

Remove a tag from an image stream by entering the following command:

For example, to remove theruby:latesttag from therubyimage stream, enter the following command:

- Alternatively, you can remove a tag using theoc tag -dcommand:oc tag -d <name>:<tag>$oc tag-d<name>:<tag>Copy to ClipboardCopied!Toggle word wrapToggle overflowFor example, to remove theruby:latesttag from therubyimage stream, enter the following command:oc tag -d ruby:latest$oc tag-druby:latestCopy to ClipboardCopied!Toggle word wrapToggle overflow

Alternatively, you can remove a tag using theoc tag -dcommand:

For example, to remove theruby:latesttag from therubyimage stream, enter the following command:

### 5.2.5. Using image stream reference syntaxCopy linkLink copied to clipboard!

To ensure that your builds and deployments use the intended image version in OpenShift Container Platform, you must use the correct reference syntax format.

Procedure

- To reference an image by a mutable tag (ImageStreamTag) from an image stream within your cluster, use the<image_stream_name>:<tag>format in your build or deployment. For example:# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>:<tag># ...spec:containers:-name:my-appimage:<image_stream_name>:<tag>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.containers.imageSpecifies the image to use from the image stream. For example,ruby:2.0.

To reference an image by a mutable tag (ImageStreamTag) from an image stream within your cluster, use the<image_stream_name>:<tag>format in your build or deployment. For example:

```
# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>:<tag>
```

```
# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>:<tag>
```

where:

**spec.containers.image**
  Specifies the image to use from the image stream. For example,ruby:2.0.
- To reference a specific, immutable image ID, or digest, within an image stream, use the<image_stream_name>@<image_id>format in your build or deployment. For example:# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>@<image_id># ...spec:containers:-name:my-appimage:<image_stream_name>@<image_id>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.containers.imageSpecifies the image to use from the image stream. For example,ruby@sha256:3a335d7d8a452970c5b4054ad7118ff134b3a6b50a2bb6d0c07c746e8986b28e.Using the image ID with the@idsyntax ensures your configuration always uses the exact same image, even if the tag is later updated to point to a different image.

To reference a specific, immutable image ID, or digest, within an image stream, use the<image_stream_name>@<image_id>format in your build or deployment. For example:

```
# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>@<image_id>
```

```
# ...
spec:
  containers:
    - name: my-app
      image: <image_stream_name>@<image_id>
```

where:

**spec.containers.image**
  Specifies the image to use from the image stream. For example,ruby@sha256:3a335d7d8a452970c5b4054ad7118ff134b3a6b50a2bb6d0c07c746e8986b28e.

Using the image ID with the@idsyntax ensures your configuration always uses the exact same image, even if the tag is later updated to point to a different image.

- To reference an image from an external registry by using the DockerImage format, use the standard Docker pull specification:<registry>/<namespace>/<image_name>:<tag>. For example:# ...
spec:
  source:
    type: Dockerfile
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: DockerImage
        name: <registry>/<namespace>/<image_name>:<tag># ...spec:source:type:Dockerfilestrategy:type:DockerdockerStrategy:from:kind:DockerImagename:<registry>/<namespace>/<image_name>:<tag>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:spec.strategy.dockerStrategy.from.nameSpecifies the image to use from the external registry. For example,registry.redhat.io/rhel7:latest.When no tag is specified in aDockerImagereference, thelatesttag is assumed.

To reference an image from an external registry by using the DockerImage format, use the standard Docker pull specification:<registry>/<namespace>/<image_name>:<tag>. For example:

```
# ...
spec:
  source:
    type: Dockerfile
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: DockerImage
        name: <registry>/<namespace>/<image_name>:<tag>
```

```
# ...
spec:
  source:
    type: Dockerfile
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: DockerImage
        name: <registry>/<namespace>/<image_name>:<tag>
```

where:

**spec.strategy.dockerStrategy.from.name**
  Specifies the image to use from the external registry. For example,registry.redhat.io/rhel7:latest.

When no tag is specified in aDockerImagereference, thelatesttag is assumed.

### 5.2.6. Understanding image stream reference typesCopy linkLink copied to clipboard!

By using image streams in OpenShift Container Platform, you can reference container images by using different reference types. These reference types define which specific image version your builds and deployments use.

ImageStreamImageobjects are automatically created in OpenShift Container Platform when you import or tag an image into the image stream. You never have to explicitly define anImageStreamImageobject in any image stream definition that you use to create image streams.

Example image stream definitions often contain definitions ofImageStreamTagand references toDockerImage, but never contain definitions ofImageStreamImage.

| Reference Type | Description | Syntax Examples |
| --- | --- | --- |
| ImageStreamTag | References or retrieves an image for a given image stream and human-readable tag. | image_stream_name:tag |
| ImageStreamImage | References or retrieves an image for a given image stream and immutable SHA ID (digest). | image_stream_name@id |
| DockerImage | References or retrieves an image from an external registry. Uses the standarddocker pullspecificatio | openshift/ruby-20-centos7:2.0,registry.redhat.io/rhel7:latest,centos/ruby-22-centos7@sha256:3a335d7d |

ImageStreamTag

References or retrieves an image for a given image stream and human-readable tag.

image_stream_name:tag

ImageStreamImage

References or retrieves an image for a given image stream and immutable SHA ID (digest).

image_stream_name@id

DockerImage

References or retrieves an image from an external registry. Uses the standarddocker pullspecification.

openshift/ruby-20-centos7:2.0,registry.redhat.io/rhel7:latest,centos/ruby-22-centos7@sha256:3a335d7d…​

## 5.3. Image pull policyCopy linkLink copied to clipboard!

To manage image updates and optimize pod startup performance in OpenShift Container Platform, you can configure theimagePullPolicyparameter in your container specifications. This setting controls when container images are pulled from registries.

### 5.3.1. About the imagePullPolicy parameterCopy linkLink copied to clipboard!

To control when OpenShift Container Platform pulls container images from registries or uses locally cached copies when starting containers, you can configure theimagePullPolicyparameter. This policy helps you manage image updates and optimize pod startup performance.

The following table lists the possible values for theimagePullPolicyparameter:

| Value | Description |
| --- | --- |
| Always | Always pull the image. |
| IfNotPresent | Only pull the image if it does not already exist on the node. |
| Never | Never pull the image. |

Always

Always pull the image.

IfNotPresent

Only pull the image if it does not already exist on the node.

Never

Never pull the image.

The following example sets theimagePullPolicyparameter toIfNotPresentfor the image taggedv1.2.3:

ExampleimagePullPolicyconfiguration

```
apiVersion: apps/v1
kind: Deployment
# ...
spec:
  # ...
  template:
    spec:
      containers:
      - name: my-app-container
        image: registry.example.com/myapp:v1.2.3
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
```

```
apiVersion: apps/v1
kind: Deployment
# ...
spec:
  # ...
  template:
    spec:
      containers:
      - name: my-app-container
        image: registry.example.com/myapp:v1.2.3
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8080
```

where:

**spec.template.spec.containers.image**
  Specifies is the image to use. In this example, the image tag is explicitly set tov1.2.3.

**spec.template.spec.containers.imagePullPolicy**
  Specifies the policy to use. In this example, the policy is set toIfNotPresentbecause the image tag is notlatest.

#### 5.3.1.1. Omitting the imagePullPolicy parameterCopy linkLink copied to clipboard!

When you omit theimagePullPolicyparameter, OpenShift Container Platform automatically determines the policy based on the image tag. This default behavior ensures that thelatesttag always pulls the newest image, while specific version tags use locally cached images when available to improve efficiency.

| Image tag | imagePullPolicysetting | Behavior |
| --- | --- | --- |
| latest | Always | Always pulls the image. This policy helps ensure that the container always uses the latest version o |
| Any other tag (for example,v1.2.3,stable,production) | IfNotPresent | Pull only if necessary. This policy uses the locally cached version of the image if it exists on the |

latest

Always

Always pulls the image. This policy helps ensure that the container always uses the latest version of the image.

Any other tag (for example,v1.2.3,stable,production)

IfNotPresent

Pull only if necessary. This policy uses the locally cached version of the image if it exists on the node, avoiding unnecessary pulls from the registry.

## 5.4. Using image pull secretsCopy linkLink copied to clipboard!

To authenticate with container registries and pull images across OpenShift Container Platform projects or from secured registries, you can configure and use image pull secrets.

You first obtain the registry authentication credentials, which are typically found in the~/.docker/config.jsonfile for Docker or the~/.config/containers/auth.jsonfile for Podman, created by thepull secret from Red Hat OpenShift Cluster Managerprocess. This content is then used to create or update the globalpullSecretobject within your cluster, allowing access to images fromquay.ioandregistry.redhat.io.

If you are using the OpenShift image registry and are pulling from image streams located in the same project, then your pod service account should already have the correct permissions. No additional action should be required.

### 5.4.1. Allowing pods to reference images across projectsCopy linkLink copied to clipboard!

To allow pods in one OpenShift Container Platform project to reference images from another project, you can bind a service account to thesystem:image-pullerrole in the target project. Use theoc policy add-role-to-useroroc policy add-role-to-groupcommand to grant cross-project image access.

When you create a pod service account or a namespace, wait until the service account is provisioned with a Docker pull secret. If you create a pod before its service account is fully provisioned, the pod fails to access the OpenShift image registry.

Procedure

- Allow pods inproject-ato reference images inproject-bby entering the following command. In this example, the service accountdefaultinproject-ais bound to thesystem:image-pullerrole inproject-b:oc policy add-role-to-user \
    system:image-puller system:serviceaccount:project-a:default \
    --namespace=project-b$oc policy add-role-to-user\system:image-puller system:serviceaccount:project-a:default\--namespace=project-bCopy to ClipboardCopied!Toggle word wrapToggle overflow

Allow pods inproject-ato reference images inproject-bby entering the following command. In this example, the service accountdefaultinproject-ais bound to thesystem:image-pullerrole inproject-b:

```
oc policy add-role-to-user \
    system:image-puller system:serviceaccount:project-a:default \
    --namespace=project-b
```

```
$ oc policy add-role-to-user \
    system:image-puller system:serviceaccount:project-a:default \
    --namespace=project-b
```

- Optional: Allow access for any service account inproject-aby using theadd-role-to-groupflag. For example:oc policy add-role-to-group \
    system:image-puller system:serviceaccounts:project-a \
    --namespace=project-b$oc policy add-role-to-group\system:image-puller system:serviceaccounts:project-a\--namespace=project-bCopy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Allow access for any service account inproject-aby using theadd-role-to-groupflag. For example:

```
oc policy add-role-to-group \
    system:image-puller system:serviceaccounts:project-a \
    --namespace=project-b
```

```
$ oc policy add-role-to-group \
    system:image-puller system:serviceaccounts:project-a \
    --namespace=project-b
```

### 5.4.2. Allowing pods to reference images from other secured registriesCopy linkLink copied to clipboard!

Pull secrets enable pods in OpenShift Container Platform to authenticate with secured registries and pull container images. Docker and Podman store authentication credentials in configuration files that you can use to create pull secrets for your service accounts.

The following files store your authentication information if you have previously logged in to a secured or insecure registry:

- Docker: By default, Docker uses$HOME/.docker/config.json.
- Podman: By default, Podman uses$HOME/.config/containers/auth.json.

Both Docker and Podman credential files and the associated pull secret can contain multiple references to the same registry if they have unique paths, for example,quay.ioandquay.io/<example_repository>. However, neither Docker nor Podman support multiple entries for the exact same registry path.

Exampleconfig.jsonfile

```
{
   "auths":{
      "cloud.openshift.com":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      },
      "quay.io":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      },
      "quay.io/repository-main":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      }
   }
}
```

```
{
   "auths":{
      "cloud.openshift.com":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      },
      "quay.io":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      },
      "quay.io/repository-main":{
         "auth":"b3Blb=",
         "email":"[REDACTED_EMAIL]"
      }
   }
}
```

Example pull secret

```
apiVersion: v1
data:
  .dockerconfigjson: ewogICAiYXV0aHMiOnsKICAgICAgIm0iOnsKICAgICAgIsKICAgICAgICAgImF1dGgiOiJiM0JsYj0iLAogICAgICAgICAiZW1haWwiOiJ5b3VAZXhhbXBsZS5jb20iCiAgICAgIH0KICAgfQp9Cg==
kind: Secret
metadata:
  creationTimestamp: "2021-09-09T19:10:11Z"
  name: pull-secret
  namespace: default
  resourceVersion: "37676"
  uid: e2851531-01bc-48ba-878c-de96cfe31020
type: Opaque
```

```
apiVersion: v1
data:
  .dockerconfigjson: ewogICAiYXV0aHMiOnsKICAgICAgIm0iOnsKICAgICAgIsKICAgICAgICAgImF1dGgiOiJiM0JsYj0iLAogICAgICAgICAiZW1haWwiOiJ5b3VAZXhhbXBsZS5jb20iCiAgICAgIH0KICAgfQp9Cg==
kind: Secret
metadata:
  creationTimestamp: "2021-09-09T19:10:11Z"
  name: pull-secret
  namespace: default
  resourceVersion: "37676"
  uid: e2851531-01bc-48ba-878c-de96cfe31020
type: Opaque
```

#### 5.4.2.1. Creating a pull secretCopy linkLink copied to clipboard!

To authenticate with container registries in OpenShift Container Platform, you can create pull secrets from existing Docker or Podman authentication files. You can also create secrets by providing registry credentials directly by using theoc create secret docker-registrycommand.

Procedure

- Create a secret from an existing authentication file:For Docker clients using.docker/config.json, enter the following command:oc create secret generic <pull_secret_name> \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson$oc create secret generic<pull_secret_name>\--from-file=.dockerconfigjson=<path/to/.docker/config.json>\--type=kubernetes.io/dockerconfigjsonCopy to ClipboardCopied!Toggle word wrapToggle overflowFor Podman clients using.config/containers/auth.json, enter the following command:oc create secret generic <pull_secret_name> \
     --from-file=<path/to/.config/containers/auth.json> \
     --type=kubernetes.io/podmanconfigjson$oc create secret generic<pull_secret_name>\--from-file=<path/to/.config/containers/auth.json>\--type=kubernetes.io/podmanconfigjsonCopy to ClipboardCopied!Toggle word wrapToggle overflow

Create a secret from an existing authentication file:

- For Docker clients using.docker/config.json, enter the following command:oc create secret generic <pull_secret_name> \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson$oc create secret generic<pull_secret_name>\--from-file=.dockerconfigjson=<path/to/.docker/config.json>\--type=kubernetes.io/dockerconfigjsonCopy to ClipboardCopied!Toggle word wrapToggle overflow

For Docker clients using.docker/config.json, enter the following command:

```
oc create secret generic <pull_secret_name> \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson
```

```
$ oc create secret generic <pull_secret_name> \
    --from-file=.dockerconfigjson=<path/to/.docker/config.json> \
    --type=kubernetes.io/dockerconfigjson
```

- For Podman clients using.config/containers/auth.json, enter the following command:oc create secret generic <pull_secret_name> \
     --from-file=<path/to/.config/containers/auth.json> \
     --type=kubernetes.io/podmanconfigjson$oc create secret generic<pull_secret_name>\--from-file=<path/to/.config/containers/auth.json>\--type=kubernetes.io/podmanconfigjsonCopy to ClipboardCopied!Toggle word wrapToggle overflow

For Podman clients using.config/containers/auth.json, enter the following command:

```
oc create secret generic <pull_secret_name> \
     --from-file=<path/to/.config/containers/auth.json> \
     --type=kubernetes.io/podmanconfigjson
```

```
$ oc create secret generic <pull_secret_name> \
     --from-file=<path/to/.config/containers/auth.json> \
     --type=kubernetes.io/podmanconfigjson
```

- Optional: If you do not already have a Docker credentials file for the secured registry, you can create a secret by running the following command:oc create secret docker-registry <pull_secret_name> \
    --docker-server=<registry_server> \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] create secret docker-registry<pull_secret_name>\--docker-server=<registry_server>\--docker-username=[REDACTED_ACCOUNT] to ClipboardCopied!Toggle word wrapToggle overflow

Optional: If you do not already have a Docker credentials file for the secured registry, you can create a secret by running the following command:

```
oc create secret docker-registry <pull_secret_name> \
    --docker-server=<registry_server> \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT]
```

```
$ oc create secret docker-registry <pull_secret_name> \
    --docker-server=<registry_server> \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT]
```

#### 5.4.2.2. Using a pull secret in a workloadCopy linkLink copied to clipboard!

To allow workloads to pull images from private registries in OpenShift Container Platform, you can link the pull secret to a service account by entering theoc secrets linkcommand or by defining it directly in your workload configuration YAML file.

Procedure

- Link the pull secret to a service account by entering the following command. Note that the name of the service account should match the name of the service account that pod uses. The default service account isdefault.oc secrets link default <pull_secret_name> --for=pull$oc secretslinkdefault<pull_secret_name>--for=pullCopy to ClipboardCopied!Toggle word wrapToggle overflow

Link the pull secret to a service account by entering the following command. Note that the name of the service account should match the name of the service account that pod uses. The default service account isdefault.

- Verify the change by entering the following command:oc get serviceaccount default -o yaml$oc get serviceaccount default-oyamlCopy to ClipboardCopied!Toggle word wrapToggle overflowExample outputapiVersion: v1
imagePullSecrets:
- name: default-dockercfg-123456
- name: <pull_secret_name>
kind: ServiceAccount
metadata:
  annotations:
    openshift.io/internal-registry-pull-secret-ref: <internal_registry_pull_secret>
  creationTimestamp: "2025-03-03T20:07:52Z"
  name: default
  namespace: default
  resourceVersion: "13914"
  uid: 9f62dd88-110d-4879-9e27-1ffe269poe3
secrets:
- name: <pull_secret_name>apiVersion:v1imagePullSecrets:-name:default-dockercfg-123456-name:<pull_secret_name>kind:ServiceAccountmetadata:annotations:openshift.io/internal-registry-pull-secret-ref:<internal_registry_pull_secret>creationTimestamp:"2025-03-03T20:07:52Z"name:defaultnamespace:defaultresourceVersion:"13914"uid:9f62dd88-110d-4879-9e27-1ffe269poe3secrets:-name:<pull_secret_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Verify the change by entering the following command:

Example output

```
apiVersion: v1
imagePullSecrets:
- name: default-dockercfg-123456
- name: <pull_secret_name>
kind: ServiceAccount
metadata:
  annotations:
    openshift.io/internal-registry-pull-secret-ref: <internal_registry_pull_secret>
  creationTimestamp: "2025-03-03T20:07:52Z"
  name: default
  namespace: default
  resourceVersion: "13914"
  uid: 9f62dd88-110d-4879-9e27-1ffe269poe3
secrets:
- name: <pull_secret_name>
```

```
apiVersion: v1
imagePullSecrets:
- name: default-dockercfg-123456
- name: <pull_secret_name>
kind: ServiceAccount
metadata:
  annotations:
    openshift.io/internal-registry-pull-secret-ref: <internal_registry_pull_secret>
  creationTimestamp: "2025-03-03T20:07:52Z"
  name: default
  namespace: default
  resourceVersion: "13914"
  uid: 9f62dd88-110d-4879-9e27-1ffe269poe3
secrets:
- name: <pull_secret_name>
```

- Optional: Instead of linking the secret to a service account, you can alternatively reference it directly in your pod or workload definition. This is useful for GitOps workflows such as ArgoCD. For example:Example pod specificationapiVersion: v1
kind: Pod
metadata:
  name: <secure_pod_name>
spec:
  containers:
  - name: <container_name>
    image: quay.io/my-private-image
  imagePullSecrets:
  - name: <pull_secret_name>apiVersion:v1kind:Podmetadata:name:<secure_pod_name>spec:containers:-name:<container_name>image:quay.io/my-private-imageimagePullSecrets:-name:<pull_secret_name>Copy to ClipboardCopied!Toggle word wrapToggle overflowExample ArgoCD workflowapiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: <example_workflow>
spec:
  entrypoint: <main_task>
  imagePullSecrets:
  - name: <pull_secret_name>apiVersion:argoproj.io/v1alpha1kind:Workflowmetadata:generateName:<example_workflow>spec:entrypoint:<main_task>imagePullSecrets:-name:<pull_secret_name>Copy to ClipboardCopied!Toggle word wrapToggle overflow

Optional: Instead of linking the secret to a service account, you can alternatively reference it directly in your pod or workload definition. This is useful for GitOps workflows such as ArgoCD. For example:

Example pod specification

```
apiVersion: v1
kind: Pod
metadata:
  name: <secure_pod_name>
spec:
  containers:
  - name: <container_name>
    image: quay.io/my-private-image
  imagePullSecrets:
  - name: <pull_secret_name>
```

```
apiVersion: v1
kind: Pod
metadata:
  name: <secure_pod_name>
spec:
  containers:
  - name: <container_name>
    image: quay.io/my-private-image
  imagePullSecrets:
  - name: <pull_secret_name>
```

Example ArgoCD workflow

```
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: <example_workflow>
spec:
  entrypoint: <main_task>
  imagePullSecrets:
  - name: <pull_secret_name>
```

```
apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: <example_workflow>
spec:
  entrypoint: <main_task>
  imagePullSecrets:
  - name: <pull_secret_name>
```

#### 5.4.2.3. Pulling from private registries with delegated authenticationCopy linkLink copied to clipboard!

To pull images from private registries that delegate authentication to a separate service in OpenShift Container Platform, you can create pull secrets for both the authentication server and the registry endpoint. Use theoc create secret docker-registrycommand to create separate secrets for each service.

Procedure

- Create a secret for the delegated authentication server by entering the following command:oc create secret docker-registry \
    --docker-server=sso.redhat.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    redhat-connect-sso$oc create secret docker-registry\--docker-server=sso.redhat.com\--docker-username=[REDACTED_ACCOUNT] to ClipboardCopied!Toggle word wrapToggle overflow

Create a secret for the delegated authentication server by entering the following command:

```
oc create secret docker-registry \
    --docker-server=sso.redhat.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    redhat-connect-sso
```

```
$ oc create secret docker-registry \
    --docker-server=sso.redhat.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    redhat-connect-sso
```

- Create a secret for the private registry by entering the following command:oc create secret docker-registry \
    --docker-server=privateregistry.example.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    private-registry$oc create secret docker-registry\--docker-server=privateregistry.example.com\--docker-username=[REDACTED_ACCOUNT] to ClipboardCopied!Toggle word wrapToggle overflow

Create a secret for the private registry by entering the following command:

```
oc create secret docker-registry \
    --docker-server=privateregistry.example.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    private-registry
```

```
$ oc create secret docker-registry \
    --docker-server=privateregistry.example.com \
    --docker-username=[REDACTED_ACCOUNT] \
    --docker-password=[REDACTED_SECRET] \
    --docker-email=[REDACTED_ACCOUNT] \
    private-registry
```

### 5.4.3. Updating the global cluster pull secretCopy linkLink copied to clipboard!

To add new registries or change authentication for your OpenShift Container Platform cluster, you can update the global pull secret by replacing it or appending new credentials. Use theoc set data secret/pull-secretcommand to apply the updated pull secret to all nodes in your cluster.

To transfer your cluster to another owner, you must initiate the transfer inOpenShift Cluster Managerand then update the pull secret on the cluster. Updating a cluster’s pull secret without initiating the transfer in OpenShift Cluster Manager causes the cluster to stop reporting Telemetry metrics in OpenShift Cluster Manager.

For more information, see "Transferring cluster ownership" in the Red Hat OpenShift Cluster Manager documentation.

Prerequisites

- You have access to the cluster as a user with thecluster-adminrole.

Procedure

- Optional: To append a new pull secret to the existing pull secret:[REDACTED_SECRET] the pull secret by entering the following command:oc get secret/pull-secret -n openshift-config --template='{{index .data ".dockerconfigjson" | base64decode}}' > <pull_secret_location>$oc get secret/pull-secret-nopenshift-config--template='{{index .data ".dockerconfigjson" | base64decode}}'><pull_secret_location>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<pull_secret_location>Specifies the path to the pull secret file.Add the new pull secret by entering the following command:oc registry login --registry="<registry>" \
--auth-basic="<username>:<password>" \
--to=<pull_secret_location>$oc registry login--registry="<registry>"\--auth-basic="<username>:<password>"\--to=<pull_secret_location>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<registry>Specifies the new registry. You can include many repositories within the same registry, for example:--registry="<registry/my-namespace/my-repository>.<username>:<password>Specifies the credentials of the new registry.<pull_secret_location>Specifies the path to the pull secret file.

Optional: To append a new pull secret to the existing pull secret:

[REDACTED_SECRET] Download the pull secret by entering the following command:oc get secret/pull-secret -n openshift-config --template='{{index .data ".dockerconfigjson" | base64decode}}' > <pull_secret_location>$oc get secret/pull-secret-nopenshift-config--template='{{index .data ".dockerconfigjson" | base64decode}}'><pull_secret_location>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<pull_secret_location>Specifies the path to the pull secret file.

Download the pull secret by entering the following command:

where:

**<pull_secret_location>**
  Specifies the path to the pull secret file.
- Add the new pull secret by entering the following command:oc registry login --registry="<registry>" \
--auth-basic="<username>:<password>" \
--to=<pull_secret_location>$oc registry login--registry="<registry>"\--auth-basic="<username>:<password>"\--to=<pull_secret_location>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<registry>Specifies the new registry. You can include many repositories within the same registry, for example:--registry="<registry/my-namespace/my-repository>.<username>:<password>Specifies the credentials of the new registry.<pull_secret_location>Specifies the path to the pull secret file.

Add the new pull secret by entering the following command:

```
oc registry login --registry="<registry>" \
--auth-basic="<username>:<password>" \
--to=<pull_secret_location>
```

```
$ oc registry login --registry="<registry>" \
--auth-basic="<username>:<password>" \
--to=<pull_secret_location>
```

where:

**<registry>**
  Specifies the new registry. You can include many repositories within the same registry, for example:--registry="<registry/my-namespace/my-repository>.

**<username>:<password>**
  Specifies the credentials of the new registry.

**<pull_secret_location>**
  Specifies the path to the pull secret file.
- Update the global pull secret for your cluster by entering the following command. Note that this update rolls out to all nodes, which can take some time depending on the size of your cluster.oc set data secret/pull-secret -n openshift-config \
  --from-file=.dockerconfigjson=<pull_secret_location>$ocsetdata secret/pull-secret-nopenshift-config\--from-file=.dockerconfigjson=<pull_secret_location>Copy to ClipboardCopied!Toggle word wrapToggle overflowwhere:<pull_secret_location>Specifies the path to the new pull secret file.

Update the global pull secret for your cluster by entering the following command. Note that this update rolls out to all nodes, which can take some time depending on the size of your cluster.

```
oc set data secret/pull-secret -n openshift-config \
  --from-file=.dockerconfigjson=<pull_secret_location>
```

```
$ oc set data secret/pull-secret -n openshift-config \
  --from-file=.dockerconfigjson=<pull_secret_location>
```

where:

**<pull_secret_location>**
  Specifies the path to the new pull secret file.
