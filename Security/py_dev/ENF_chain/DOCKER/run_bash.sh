#!/bin/bash

# -i sets up an interactive session; -t allocates a pseudo tty; --rm makes this container ephemeral
# -u specify the process should be run by root. This step is important (v.i.)!
# -v @volume:@docker path. use volume to save data
# -v /etc/localtime:/etc/localtime:ro make sure docker's time syncs with that of the host
# --name=@ specify the name of the container (here rdev); the image you want to run the container from (here ubuntu-r); the process you want to run in the container (here bash). (The last step of specifying a process is only necessary if you have not set a default CMD or ENTRYPOINT for your image.)

IMAGE_NAME="ecoledger_node"
CONTAINER_NAME="ecoledger-node"
#VOLUME_ACCOUNT="gethAccount"

RPC_PORT=$1
PORT=$2

# arguments validation
if [[ 2 -ne $# ]]; then
	echo "Usage $0 -rpcport -port!"
	exit 0
fi

if ! [[ $RPC_PORT =~ ^[0-9]+$ ]]; then
	echo "Error: rpcport should be integer!"
	exit 0
fi

if ! [[ $PORT =~ ^[0-9]+$ ]]; then
	echo "Error: port should be integer!"
	exit 0
fi

# execute docker run command
docker run -i -t --rm \
	-p $RPC_PORT:31180 \
	-p $PORT:8180 \
	--privileged=true \
	--name=$CONTAINER_NAME $IMAGE_NAME /bin/bash
