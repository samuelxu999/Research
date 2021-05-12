# ecoledger_node x86
This docker image built on Python3.6 image.

The overview of contents of project are:

## Dockerfile
The Dockerfile defines all denpendencies, libs and app code inside the container.


## build.sh
$./build.sh make

The docker image 'ecoledger_node' will be built on your local environment.

Execute './build.sh clean' will remove built image. Similiar to using 'docker image rm -f @id'.

### To push image on docker hub docker hub.

1) Log in with your Docker ID

$docker login

2) Tag the image: 

$ docker tag imagename username/repository:tag

For example:

$ docker tag ecoledger_node samuelxu999/ecoledger_node:x86

3) Push the imagename by uploading your tagged image to the repository:

$ docker push username/repository:tag

For example:

$ docker push samuelxu999/ecoledger_node:x86

## run_node.sh

$./run_node.sh --container_name

This is used to startup container. For example, './run_node.sh ecoledger-node1'. After container startup, execue 'docker attach ecoledger-node1' to attach container with sh CLI.

## run_bash.sh

$./run_bash.sh --container_name

This is used to test in development. For example, './run_bash.sh ecoledger-node1'. After container startup, automatically attach to container with sh CLI.

To detach current container, pressing 'Ctrl+p' and 'Ctrl+q' to exit.

## docker_exec.sh

Run 'docker exec command' to interact with tools and scripts in container.

## service_run.sh

$./service_run.sh --operation --container_name --image_type --rpc_port --port --bootstrapnode

Startup container and run services in container. 

1) For bootstrapnode on x86 platform like desktop, execute './service_run.sh start ecoledger-node x86 31180 8180'

2) For ENF_node on arm platform like Respberry Pi, execute './service_run.sh start ecoledger-node1 arm 31181 8181 0.0.0.0:31180'

Execute './service_run.sh stop --container_name' can stop running container

Execute './service_run.sh show --container_name' can list all running container. Similiar to 'docker ps'.
