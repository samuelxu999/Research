#!/bin/bash

##------------------------------ Used for test ----------------------------------------------------
# -i sets up an interactive session; -t allocates a pseudo tty; --rm makes this container ephemeral
# -u specify the process should be run by root. This step is important (v.i.)!
# -v @volume:@docker path. use volume to save data
# -v /etc/localtime:/etc/localtime:ro make sure docker's time syncs with that of the host
# --name=@ specify the name of the container (here rdev); 
# the image you want to run the container from (here ubuntu-r); 
# the process you want to run in the container (here bash). 
# (The last step of specifying a process is only necessary if you have not set a default CMD or ENTRYPOINT for your image.)

IMAGE_NAME="ecoledger_node"

CONTAINER_NAME=$1

## Check container name
if [[ "" == $1 ]]; then
	CONTAINER_NAME="ecoledger-node"
	echo "Use default container name: $CONTAINER_NAME"
fi

# execute docker run command
docker run -i -t --rm --network=host \
	--privileged=true \
	-v /etc/localtime:/etc/localtime:ro \
	-v $CONTAINER_NAME:/home/docker/app \
	--name=$CONTAINER_NAME $IMAGE_NAME /bin/bash
