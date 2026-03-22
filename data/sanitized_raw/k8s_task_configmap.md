<!-- source: k8s_task_configmap.md -->

# Tasks - Configuration

---
Source: https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
---

# Configure a Pod to Use a ConfigMap

Many applications rely on configuration which is used during either application initialization or runtime.
Most times, there is a requirement to adjust values assigned to configuration parameters.
ConfigMaps are a Kubernetes mechanism that let you inject configuration data into applicationpods.

The ConfigMap concept allow you to decouple configuration artifacts from image content to
keep containerized applications portable. For example, you can download and run the samecontainer imageto spin up containers for
the purposes of local development, system test, or running a live end-user workload.

This page provides a series of usage examples demonstrating how to create ConfigMaps and
configure Pods using data stored in ConfigMaps.

## Before you begin

You need to have a Kubernetes cluster, and the kubectl command-line tool must
be configured to communicate with your cluster. It is recommended to run this tutorial on a cluster with at least two nodes that are not acting as control plane hosts. If you do not already have a
cluster, you can create one by usingminikubeor you can use one of these Kubernetes playgrounds:

- iximiuz Labs
- Killercoda
- KodeKloud

You need to have thewgettool installed. If you have a different tool
such ascurl, and you do not havewget, you will need to adapt the
step that downloads example data.

## Create a ConfigMap

You can use eitherkubectl create configmapor a ConfigMap generator inkustomization.yamlto create a ConfigMap.

### Create a ConfigMap usingkubectl create configmap

Use thekubectl create configmapcommand to create ConfigMaps fromdirectories,files,
orliteral values:

```
kubectl create configmap <map-name> <data-source>
```

where <map-name> is the name you want to assign to the ConfigMap and <data-source> is the
directory, file, or literal value to draw the data from.
The name of a ConfigMap object must be a validDNS subdomain name.

When you are creating a ConfigMap based on a file, the key in the <data-source> defaults to
the basename of the file, and the value defaults to the file content.

You can usekubectl describeorkubectl getto retrieve information
about a ConfigMap.

#### Create a ConfigMap from a directory

You can usekubectl create configmapto create a ConfigMap from multiple files in the same
directory. When you are creating a ConfigMap based on a directory, kubectl identifies files
whose filename is a valid key in the directory and packages each of those files into the new
ConfigMap. Any directory entries except regular files are ignored (for example: subdirectories,
symlinks, devices, pipes, and more).

#### Note:

Each filename being used for ConfigMap creation must consist of only acceptable characters,
which are: letters (AtoZandatoz), digits (0to9), '-', '_', or '.'.
If you usekubectl create configmapwith a directory where any of the file names contains
an unacceptable character, thekubectlcommand may fail.

Thekubectlcommand does not print an error when it encounters an invalid filename.

Create the local directory:

```
mkdir -p configure-pod-container/configmap/
```

Now, download the sample configuration and create the ConfigMap:

```
# Download the sample files into `configure-pod-container/configmap/` directory
wget https://kubernetes.io/examples/configmap/game.properties -O configure-pod-container/configmap/game.properties
wget https://kubernetes.io/examples/configmap/ui.properties -O configure-pod-container/configmap/ui.properties

# Create the ConfigMap
kubectl create configmap game-config --from-file=configure-pod-container/configmap/
```

The above command packages each file, in this case,game.propertiesandui.propertiesin theconfigure-pod-container/configmap/directory into the game-config ConfigMap. You can
display details of the ConfigMap using the following command:

```
kubectl describe configmaps game-config
```

The output is similar to this:

```
Name:         game-config
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
game.properties:
----
enemies=aliens
lives=3
enemies.cheat=true
enemies.cheat.level=noGoodRotten
secret.code.passphrase=UUDDLRLRBABAS
secret.code.allowed=true
secret.code.lives=30
ui.properties:
----
color.good=purple
color.bad=yellow
allow.textmode=true
how.nice.to.look=fairlyNice
```

Thegame.propertiesandui.propertiesfiles in theconfigure-pod-container/configmap/directory are represented in thedatasection of the ConfigMap.

```
kubectl get configmaps game-config -o yaml
```

The output is similar to this:

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2022-02-18T18:52:05Z
  name: game-config
  namespace: default
  resourceVersion: "516"
  uid: b4952dc3-d670-11e5-8cd0-68f728db1985
data:
  game.properties: |
    enemies=aliens
    lives=3
    enemies.cheat=true
    enemies.cheat.level=noGoodRotten
    secret.code.passphrase=UUDDLRLRBABAS
    secret.code.allowed=true
    secret.code.lives=30    
  ui.properties: |
    color.good=purple
    color.bad=yellow
    allow.textmode=true
    how.nice.to.look=fairlyNice
```

#### Create ConfigMaps from files

You can usekubectl create configmapto create a ConfigMap from an individual file, or from
multiple files.

For example,

```
kubectl create configmap game-config-2 --from-file=configure-pod-container/configmap/game.properties
```

would produce the following ConfigMap:

```
kubectl describe configmaps game-config-2
```

where the output is similar to this:

```
Name:         game-config-2
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
game.properties:
----
enemies=aliens
lives=3
enemies.cheat=true
enemies.cheat.level=noGoodRotten
secret.code.passphrase=UUDDLRLRBABAS
secret.code.allowed=true
secret.code.lives=30
```

You can pass in the--from-fileargument multiple times to create a ConfigMap from multiple
data sources.

```
kubectl create configmap game-config-2 --from-file=configure-pod-container/configmap/game.properties --from-file=configure-pod-container/configmap/ui.properties
```

You can display details of thegame-config-2ConfigMap using the following command:

```
kubectl describe configmaps game-config-2
```

The output is similar to this:

```
Name:         game-config-2
Namespace:    default
Labels:       <none>
Annotations:  <none>

Data
====
game.properties:
----
enemies=aliens
lives=3
enemies.cheat=true
enemies.cheat.level=noGoodRotten
secret.code.passphrase=UUDDLRLRBABAS
secret.code.allowed=true
secret.code.lives=30
ui.properties:
----
color.good=purple
color.bad=yellow
allow.textmode=true
how.nice.to.look=fairlyNice
```

Use the option--from-env-fileto create a ConfigMap from an env-file, for example:

```
# Env-files contain a list of environment variables.
# These syntax rules apply:
#   Each line in an env file has to be in VAR=VAL format.
#   Lines beginning with # (i.e. comments) are ignored.
#   Blank lines are ignored.
#   There is no special handling of quotation marks (i.e. they will be part of the ConfigMap value)).

# Download the sample files into `configure-pod-container/configmap/` directory
wget https://kubernetes.io/examples/configmap/game-env-file.properties -O configure-pod-container/configmap/game-env-file.properties
wget https://kubernetes.io/examples/configmap/ui-env-file.properties -O configure-pod-container/configmap/ui-env-file.properties

# The env-file `game-env-file.properties` looks like below
cat configure-pod-container/configmap/game-env-file.properties
enemies=aliens
lives=3
allowed="true"

# This comment and the empty line above it are ignored
```

```
kubectl create configmap game-config-env-file \
       --from-env-file=configure-pod-container/configmap/game-env-file.properties
```

would produce a ConfigMap. View the ConfigMap:

```
kubectl get configmap game-config-env-file -o yaml
```

the output is similar to:

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2019-12-27T18:36:28Z
  name: game-config-env-file
  namespace: default
  resourceVersion: "809965"
  uid: d9d1ca5b-eb34-11e7-887b-42010a8002b8
data:
  allowed: '"true"'
  enemies: aliens
  lives: "3"
```

Starting with Kubernetes v1.23,kubectlsupports the--from-env-fileargument to be
specified multiple times to create a ConfigMap from multiple data sources.

```
kubectl create configmap config-multi-env-files \
        --from-env-file=configure-pod-container/configmap/game-env-file.properties \
        --from-env-file=configure-pod-container/configmap/ui-env-file.properties
```

would produce the following ConfigMap:

```
kubectl get configmap config-multi-env-files -o yaml
```

where the output is similar to this:

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2019-12-27T18:38:34Z
  name: config-multi-env-files
  namespace: default
  resourceVersion: "810136"
  uid: 252c4572-eb35-11e7-887b-42010a8002b8
data:
  allowed: '"true"'
  color: purple
  enemies: aliens
  how: fairlyNice
  lives: "3"
  textmode: "true"
```

#### Define the key to use when creating a ConfigMap from a file

You can define a key other than the file name to use in thedatasection of your ConfigMap
when using the--from-fileargument:

```
kubectl create configmap game-config-3 --from-file=<my-key-name>=<path-to-file>
```

where<my-key-name>is the key you want to use in the ConfigMap and<path-to-file>is the
location of the data source file you want the key to represent.

For example:

```
kubectl create configmap game-config-3 --from-file=game-special-key=configure-pod-container/configmap/game.properties
```

would produce the following ConfigMap:

```
kubectl get configmaps game-config-3 -o yaml
```

where the output is similar to this:

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2022-02-18T18:54:22Z
  name: game-config-3
  namespace: default
  resourceVersion: "530"
  uid: 05f8da22-d671-11e5-8cd0-68f728db1985
data:
  game-special-key: |
    enemies=aliens
    lives=3
    enemies.cheat=true
    enemies.cheat.level=noGoodRotten
    secret.code.passphrase=UUDDLRLRBABAS
    secret.code.allowed=true
    secret.code.lives=30
```

#### Create ConfigMaps from literal values

You can usekubectl create configmapwith the--from-literalargument to define a literal
value from the command line:

```
kubectl create configmap special-config --from-literal=special.how=very --from-literal=special.type=charm
```

You can pass in multiple key-value pairs. Each pair provided on the command line is represented
as a separate entry in thedatasection of the ConfigMap.

```
kubectl get configmaps special-config -o yaml
```

The output is similar to this:

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2022-02-18T19:14:38Z
  name: special-config
  namespace: default
  resourceVersion: "651"
  uid: dadce046-d673-11e5-8cd0-68f728db1985
data:
  special.how: very
  special.type: charm
```

### Create a ConfigMap from generator

You can also create a ConfigMap from generators and then apply it to create the object
in the cluster's API server.
You should specify the generators in akustomization.yamlfile within a directory.

#### Generate ConfigMaps from files

For example, to generate a ConfigMap from filesconfigure-pod-container/configmap/game.properties

```
# Create a kustomization.yaml file with ConfigMapGenerator
cat <<EOF >./kustomization.yaml
configMapGenerator:
- name: game-config-4
  options:
    labels:
      game-config: config-4
  files:
  - configure-pod-container/configmap/game.properties
EOF
```

Apply the kustomization directory to create the ConfigMap object:

```
kubectl apply -k .
```

```
configmap/game-config-4-m9dm2f92bt created
```

You can check that the ConfigMap was created like this:

```
kubectl get configmap
```

```
NAME                       DATA   AGE
game-config-4-m9dm2f92bt   1      37s
```

and also:

```
kubectl describe configmaps/game-config-4-m9dm2f92bt
```

```
Name:         game-config-4-m9dm2f92bt
Namespace:    default
Labels:       game-config=config-4
Annotations:  kubectl.kubernetes.io/last-applied-configuration:
                {"apiVersion":"v1","data":{"game.properties":"enemies=aliens\nlives=3\nenemies.cheat=true\nenemies.cheat.level=noGoodRotten\nsecret.code.p...

Data
====
game.properties:
----
enemies=aliens
lives=3
enemies.cheat=true
enemies.cheat.level=noGoodRotten
secret.code.passphrase=UUDDLRLRBABAS
secret.code.allowed=true
secret.code.lives=30
Events:  <none>
```

Notice that the generated ConfigMap name has a suffix appended by hashing the contents. This
ensures that a new ConfigMap is generated each time the content is modified.

#### Define the key to use when generating a ConfigMap from a file

You can define a key other than the file name to use in the ConfigMap generator.
For example, to generate a ConfigMap from filesconfigure-pod-container/configmap/game.propertieswith the keygame-special-key

```
# Create a kustomization.yaml file with ConfigMapGenerator
cat <<EOF >./kustomization.yaml
configMapGenerator:
- name: game-config-5
  options:
    labels:
      game-config: config-5
  files:
  - game-special-key=configure-pod-container/configmap/game.properties
EOF
```

Apply the kustomization directory to create the ConfigMap object.

```
kubectl apply -k .
```

```
configmap/game-config-5-m67dt67794 created
```

#### Generate ConfigMaps from literals

This example shows you how to create aConfigMapfrom two literal key/value pairs:special.type=charmandspecial.how=very, using Kustomize and kubectl. To achieve
this, you can specify theConfigMapgenerator. Create (or replace)kustomization.yamlso that it has the following contents:

```
---
# kustomization.yaml contents for creating a ConfigMap from literals
configMapGenerator:
- name: special-config-2
  literals:
  - special.how=very
  - special.type=charm
```

Apply the kustomization directory to create the ConfigMap object:

```
kubectl apply -k .
```

```
configmap/special-config-2-c92b5mmcf2 created
```

## Interim cleanup

Before proceeding, clean up some of the ConfigMaps you made:

```
kubectl delete configmap special-config
kubectl delete configmap env-config
kubectl delete configmap -l 'game-config in (config-4,config-5)'
```

Now that you have learned to define ConfigMaps, you can move on to the next
section, and learn how to use these objects with Pods.

## Define container environment variables using ConfigMap data

### Define a container environment variable with data from a single ConfigMap

- Define an environment variable as a key-value pair in a ConfigMap:kubectl create configmap special-config --from-literal=special.how=very

Define an environment variable as a key-value pair in a ConfigMap:

```
kubectl create configmap special-config --from-literal=special.how=very
```

- Assign thespecial.howvalue defined in the ConfigMap to theSPECIAL_LEVEL_KEYenvironment variable in the Pod specification.pods/pod-single-configmap-env-variable.yamlapiVersion:v1kind:Podmetadata:name:dapi-test-podspec:containers:-name:test-containerimage:registry.k8s.io/busybox:1.27.2command:["/bin/sh","-c","env"]env:# Define the environment variable-name:SPECIAL_LEVEL_KEYvalueFrom:configMapKeyRef:# The ConfigMap containing the value you want to assign to SPECIAL_LEVEL_KEYname:special-config# Specify the key associated with the valuekey:special.howrestartPolicy:NeverCreate the Pod:kubectl create -f https://kubernetes.io/examples/pods/pod-single-configmap-env-variable.yamlNow, the Pod's output includes environment variableSPECIAL_LEVEL_KEY=very.

Assign thespecial.howvalue defined in the ConfigMap to theSPECIAL_LEVEL_KEYenvironment variable in the Pod specification.

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/sh", "-c", "env" ]
      env:
        # Define the environment variable
        - name: SPECIAL_LEVEL_KEY
          valueFrom:
            configMapKeyRef:
              # The ConfigMap containing the value you want to assign to SPECIAL_LEVEL_KEY
              name: special-config
              # Specify the key associated with the value
              key: special.how
  restartPolicy: Never
```

Create the Pod:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-single-configmap-env-variable.yaml
```

Now, the Pod's output includes environment variableSPECIAL_LEVEL_KEY=very.

### Define container environment variables with data from multiple ConfigMaps

As with the previous example, create the ConfigMaps first.
Here is the manifest you will use:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: special-config
  namespace: default
data:
  special.how: very
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: env-config
  namespace: default
data:
  log_level: INFO
```

- Create the ConfigMap:kubectl create -f https://kubernetes.io/examples/configmap/configmaps.yaml

Create the ConfigMap:

```
kubectl create -f https://kubernetes.io/examples/configmap/configmaps.yaml
```

- Define the environment variables in the Pod specification.pods/pod-multiple-configmap-env-variable.yamlapiVersion:v1kind:Podmetadata:name:dapi-test-podspec:containers:-name:test-containerimage:registry.k8s.io/busybox:1.27.2command:["/bin/sh","-c","env"]env:-name:SPECIAL_LEVEL_KEYvalueFrom:configMapKeyRef:name:special-configkey:special.how-name:LOG_LEVELvalueFrom:configMapKeyRef:name:env-configkey:log_levelrestartPolicy:NeverCreate the Pod:kubectl create -f https://kubernetes.io/examples/pods/pod-multiple-configmap-env-variable.yamlNow, the Pod's output includes environment variablesSPECIAL_LEVEL_KEY=veryandLOG_LEVEL=INFO.Once you're happy to move on, delete that Pod and ConfigMap:kubectl delete pod dapi-test-pod --nowkubectl delete configmap special-configkubectl delete configmap env-config

Define the environment variables in the Pod specification.

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/sh", "-c", "env" ]
      env:
        - name: SPECIAL_LEVEL_KEY
          valueFrom:
            configMapKeyRef:
              name: special-config
              key: special.how
        - name: LOG_LEVEL
          valueFrom:
            configMapKeyRef:
              name: env-config
              key: log_level
  restartPolicy: Never
```

Create the Pod:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-multiple-configmap-env-variable.yaml
```

Now, the Pod's output includes environment variablesSPECIAL_LEVEL_KEY=veryandLOG_LEVEL=INFO.

Once you're happy to move on, delete that Pod and ConfigMap:

```
kubectl delete pod dapi-test-pod --now
kubectl delete configmap special-config
kubectl delete configmap env-config
```

## Configure all key-value pairs in a ConfigMap as container environment variables

- Create a ConfigMap containing multiple key-value pairs.configmap/configmap-multikeys.yamlapiVersion:v1kind:ConfigMapmetadata:name:special-confignamespace:defaultdata:SPECIAL_LEVEL:verySPECIAL_TYPE:charmCreate the ConfigMap:kubectl create -f https://kubernetes.io/examples/configmap/configmap-multikeys.yaml

Create a ConfigMap containing multiple key-value pairs.

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: special-config
  namespace: default
data:
  SPECIAL_LEVEL: very
  SPECIAL_TYPE: charm
```

Create the ConfigMap:

```
kubectl create -f https://kubernetes.io/examples/configmap/configmap-multikeys.yaml
```

- UseenvFromto define all of the ConfigMap's data as container environment variables. The
key from the ConfigMap becomes the environment variable name in the Pod.pods/pod-configmap-envFrom.yamlapiVersion:v1kind:Podmetadata:name:dapi-test-podspec:containers:-name:test-containerimage:registry.k8s.io/busybox:1.27.2command:["/bin/sh","-c","env"]envFrom:-configMapRef:name:special-configrestartPolicy:NeverCreate the Pod:kubectl create -f https://kubernetes.io/examples/pods/pod-configmap-envFrom.yamlNow, the Pod's output includes environment variablesSPECIAL_LEVEL=veryandSPECIAL_TYPE=charm.Once you're happy to move on, delete that Pod:kubectl delete pod dapi-test-pod --now

UseenvFromto define all of the ConfigMap's data as container environment variables. The
key from the ConfigMap becomes the environment variable name in the Pod.

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/sh", "-c", "env" ]
      envFrom:
      - configMapRef:
          name: special-config
  restartPolicy: Never
```

Create the Pod:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-configmap-envFrom.yaml
```

Now, the Pod's output includes environment variablesSPECIAL_LEVEL=veryandSPECIAL_TYPE=charm.

Once you're happy to move on, delete that Pod:

```
kubectl delete pod dapi-test-pod --now
```

## Use ConfigMap-defined environment variables in Pod commands

You can use ConfigMap-defined environment variables in thecommandandargsof a container
using the$(VAR_NAME)Kubernetes substitution syntax.

For example, the following Pod manifest:

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/echo", "$(SPECIAL_LEVEL_KEY) $(SPECIAL_TYPE_KEY)" ]
      env:
        - name: SPECIAL_LEVEL_KEY
          valueFrom:
            configMapKeyRef:
              name: special-config
              key: SPECIAL_LEVEL
        - name: SPECIAL_TYPE_KEY
          valueFrom:
            configMapKeyRef:
              name: special-config
              key: SPECIAL_TYPE
  restartPolicy: Never
```

Create that Pod, by running:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-configmap-env-var-valueFrom.yaml
```

That pod produces the following output from thetest-containercontainer:

```
kubectl logs dapi-test-pod
```

```
very charm
```

Once you're happy to move on, delete that Pod:

```
kubectl delete pod dapi-test-pod --now
```

## Add ConfigMap data to a Volume

As explained inCreate ConfigMaps from files, when you create
a ConfigMap using--from-file, the filename becomes a key stored in thedatasection of
the ConfigMap. The file contents become the key's value.

The examples in this section refer to a ConfigMap namedspecial-config:

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: special-config
  namespace: default
data:
  SPECIAL_LEVEL: very
  SPECIAL_TYPE: charm
```

Create the ConfigMap:

```
kubectl create -f https://kubernetes.io/examples/configmap/configmap-multikeys.yaml
```

### Populate a Volume with data stored in a ConfigMap

Add the ConfigMap name under thevolumessection of the Pod specification.
This adds the ConfigMap data to the directory specified asvolumeMounts.mountPath(in this
case,/etc/config). Thecommandsection lists directory files with names that match the
keys in ConfigMap.

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/sh", "-c", "ls /etc/config/" ]
      volumeMounts:
      - name: config-volume
        mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        # Provide the name of the ConfigMap containing the files you want
        # to add to the container
        name: special-config
  restartPolicy: Never
```

Create the Pod:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-configmap-volume.yaml
```

When the pod runs, the commandls /etc/config/produces the output below:

```
SPECIAL_LEVEL
SPECIAL_TYPE
```

Text data is exposed as files using the UTF-8 character encoding. To use some other
character encoding, usebinaryData(seeConfigMap objectfor more details).

#### Note:

Once you're happy to move on, delete that Pod:

```
kubectl delete pod dapi-test-pod --now
```

### Add ConfigMap data to a specific path in the Volume

Use thepathfield to specify the desired file path for specific ConfigMap items.
In this case, theSPECIAL_LEVELitem will be mounted in theconfig-volumevolume at/etc/config/keys.

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: registry.k8s.io/busybox:1.27.2
      command: [ "/bin/sh","-c","cat /etc/config/keys" ]
      volumeMounts:
      - name: config-volume
        mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: special-config
        items:
        - key: SPECIAL_LEVEL
          path: keys
  restartPolicy: Never
```

Create the Pod:

```
kubectl create -f https://kubernetes.io/examples/pods/pod-configmap-volume-specific-key.yaml
```

When the pod runs, the commandcat /etc/config/keysproduces the output below:

```
very
```

#### Caution:

Delete that Pod:

```
kubectl delete pod dapi-test-pod --now
```

### Project keys to specific paths and file permissions

You can project keys to specific paths. Refer to the corresponding section in theSecretsguide for the syntax.You can set POSIX permissions for keys. Refer to the corresponding section in theSecretsguide for the syntax.

### Optional references

A ConfigMap reference may be markedoptional. If the ConfigMap is non-existent, the mounted
volume will be empty. If the ConfigMap exists, but the referenced key is non-existent, the path
will be absent beneath the mount point. SeeOptional ConfigMapsfor more
details.

### Mounted ConfigMaps are updated automatically

When a mounted ConfigMap is updated, the projected content is eventually updated too.
This applies in the case where an optionally referenced ConfigMap comes into
existence after a pod has started.

Kubelet checks whether the mounted ConfigMap is fresh on every periodic sync. However,
it uses its local TTL-based cache for getting the current value of the ConfigMap. As a
result, the total delay from the moment when the ConfigMap is updated to the moment
when new keys are projected to the pod can be as long as kubelet sync period (1
minute by default) + TTL of ConfigMaps cache (1 minute by default) in kubelet. You
can trigger an immediate refresh by updating one of the pod's annotations.

#### Note:

## Understanding ConfigMaps and Pods

The ConfigMap API resource stores configuration data as key-value pairs. The data can be consumed
in pods or provide the configurations for system components such as controllers. ConfigMap is
similar toSecrets, but provides a means of working
with strings that don't contain sensitive information. Users and system components alike can
store configuration data in ConfigMap.

#### Note:

The ConfigMap'sdatafield contains the configuration data. As shown in the example below,
this can be simple (like individual properties defined using--from-literal) or complex
(like configuration files or JSON blobs defined using--from-file).

```
apiVersion: v1
kind: ConfigMap
metadata:
  creationTimestamp: 2016-02-18T19:14:38Z
  name: example-config
  namespace: default
data:
  # example of a simple property defined using --from-literal
  example.property.1: hello
  example.property.2: world
  # example of a complex property defined using --from-file
  example.property.file: |-
    property.1=value-1
    property.2=value-2
    property.3=value-3
```

Whenkubectlcreates a ConfigMap from inputs that are not ASCII or UTF-8, the tool puts
these into thebinaryDatafield of the ConfigMap, and not indata. Both text and binary
data sources can be combined in one ConfigMap.

If you want to view thebinaryDatakeys (and their values) in a ConfigMap, you can runkubectl get configmap -o jsonpath='{.binaryData}' <name>.

Pods can load data from a ConfigMap that uses eitherdataorbinaryData.

## Optional ConfigMaps

You can mark a reference to a ConfigMap asoptionalin a Pod specification.
If the ConfigMap doesn't exist, the configuration for which it provides data in the Pod
(for example: environment variable, mounted volume) will be empty.
If the ConfigMap exists, but the referenced key is non-existent the data is also empty.

For example, the following Pod specification marks an environment variable from a ConfigMap
as optional:

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: gcr.io/google_containers/busybox
      command: ["/bin/sh", "-c", "env"]
      env:
        - name: SPECIAL_LEVEL_KEY
          valueFrom:
            configMapKeyRef:
              name: a-config
              key: akey
              optional: true # mark the variable as optional
  restartPolicy: Never
```

If you run this pod, and there is no ConfigMap nameda-config, the output is empty.
If you run this pod, and there is a ConfigMap nameda-configbut that ConfigMap doesn't have
a key namedakey, the output is also empty. If you do set a value forakeyin thea-configConfigMap, this pod prints that value and then terminates.

You can also mark the volumes and files provided by a ConfigMap as optional. Kubernetes always
creates the mount paths for the volume, even if the referenced ConfigMap or key doesn't exist. For
example, the following Pod specification marks a volume that references a ConfigMap as optional:

```
apiVersion: v1
kind: Pod
metadata:
  name: dapi-test-pod
spec:
  containers:
    - name: test-container
      image: gcr.io/google_containers/busybox
      command: ["/bin/sh", "-c", "ls /etc/config"]
      volumeMounts:
      - name: config-volume
        mountPath: /etc/config
  volumes:
    - name: config-volume
      configMap:
        name: no-config
        optional: true # mark the source ConfigMap as optional
  restartPolicy: Never
```

## Restrictions

- You must create theConfigMapobject before you reference it in a Pod
specification. Alternatively, mark the ConfigMap reference asoptionalin the Pod spec (seeOptional ConfigMaps). If you reference a ConfigMap that doesn't exist
and you don't mark the reference asoptional, the Pod won't start. Similarly, references
to keys that don't exist in the ConfigMap will also prevent the Pod from starting, unless
you mark the key references asoptional.

You must create theConfigMapobject before you reference it in a Pod
specification. Alternatively, mark the ConfigMap reference asoptionalin the Pod spec (seeOptional ConfigMaps). If you reference a ConfigMap that doesn't exist
and you don't mark the reference asoptional, the Pod won't start. Similarly, references
to keys that don't exist in the ConfigMap will also prevent the Pod from starting, unless
you mark the key references asoptional.

- If you useenvFromto define environment variables from ConfigMaps, keys that are considered
invalid will be skipped. The pod will be allowed to start, but the invalid names will be
recorded in the event log (InvalidVariableNames). The log message lists each skipped
key. For example:kubectl get eventsThe output is similar to this:LASTSEEN FIRSTSEEN COUNT NAME          KIND  SUBOBJECT  TYPE      REASON                            SOURCE                MESSAGE
0s       0s        1     dapi-test-pod Pod              Warning   InvalidEnvironmentVariableNames   {kubelet, [REDACTED_PRIVATE_IP]}  Keys [1badkey, 2alsobad] from the EnvFrom configMap default/myconfig were skipped since they are considered invalid environment variable names.

If you useenvFromto define environment variables from ConfigMaps, keys that are considered
invalid will be skipped. The pod will be allowed to start, but the invalid names will be
recorded in the event log (InvalidVariableNames). The log message lists each skipped
key. For example:

```
kubectl get events
```

The output is similar to this:

```
LASTSEEN FIRSTSEEN COUNT NAME          KIND  SUBOBJECT  TYPE      REASON                            SOURCE                MESSAGE
0s       0s        1     dapi-test-pod Pod              Warning   InvalidEnvironmentVariableNames   {kubelet, [REDACTED_PRIVATE_IP]}  Keys [1badkey, 2alsobad] from the EnvFrom configMap default/myconfig were skipped since they are considered invalid environment variable names.
```

- ConfigMaps reside in a specificNamespace.
Pods can only refer to ConfigMaps that are in the same namespace as the Pod.

ConfigMaps reside in a specificNamespace.
Pods can only refer to ConfigMaps that are in the same namespace as the Pod.

- You can't use ConfigMaps forstatic pods, because the
kubelet does not support this.

You can't use ConfigMaps forstatic pods, because the
kubelet does not support this.

## Cleaning up

Delete the ConfigMaps and Pods that you made:

```
kubectl delete configmaps/game-config configmaps/game-config-2 configmaps/game-config-3 \
               configmaps/game-config-env-file
kubectl delete pod dapi-test-pod --now

# You might already have removed the next set
kubectl delete configmaps/special-config configmaps/env-config
kubectl delete configmap -l 'game-config in (config-4,config-5)'
```

Remove thekustomization.yamlfile that you used to generate the ConfigMap:

```
rm kustomization.yaml
```

If you created a directoryconfigure-pod-containerand no longer need it, you should remove that too,
or move it into the trash can / deleted files location.

```
rm -r configure-pod-container
```

## What's next

- Follow a real world example ofConfiguring Redis using a ConfigMap.
- Follow an example ofUpdating configuration via a ConfigMap.

## Feedback

Was this page helpful?

Thanks for the feedback. If you have a specific, answerable question about how to use Kubernetes, ask it onStack Overflow.
Open an issue in theGitHub Repositoryif you want toreport a problemorsuggest an improvement.
