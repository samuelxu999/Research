#!/bin/bash

##---------------- Used for constainer startup and run background---------------------------------------
# -d 				run container in background and print container ID
# -i 				sets up an interactive session; -t allocates a pseudo tty; 
# --rm 				makes this container ephemeral
# --network=host 	network_mode uses the host network
# -v /etc/localtime:/etc/localtime:ro 	make sure docker's time syncs with that of the host
# -v @volume:@docker_path				use volume mapping to docker folder to save data
# --name=@container_name specify the name of the container; the image you want to run the container from ecoledger_node;
# using /bin/bash as default CMD.

## Using 'docker attach $CONTAINER_NAME' to attach /bin/bash in container. 
## you can detach from a container and leave it running using the 'CTRL-p CTRL-q key' sequence.

IMAGE_NAME="ecoledger_node"

OPERATION=$1
CONTAINER_NAME=$2

# List container
if  [ "list" == "$OPERATION" ] ; then
	echo "List all containers!"
	docker container ls

# Start container
elif [ "start" == "$OPERATION" ] ; then
	## Check container name
	if [[ "" == $2 ]]; then
		CONTAINER_NAME="ecoledger-node"
		echo "Use default container name: $CONTAINER_NAME"
	fi

	docker run -d -it --rm --network=host \
		--privileged=true \
		-v /etc/localtime:/etc/localtime:ro \
		-v $CONTAINER_NAME:/home/docker/app \
		--name=$CONTAINER_NAME $IMAGE_NAME /bin/bash

# Stop container		
elif [ "stop" == "$OPERATION" ] ; then
	docker container stop $CONTAINER_NAME
else
	echo "Usage $0 list|start|stop| -container_name!"
fi
