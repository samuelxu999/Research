#!/bin/bash


##-------------- Run constainer as background service given args -------------------------------------

OPERATION=$1
CONTAINER_NAME=$2
IMAGE_TYPE=$3
RPC_PORT=$4
PORT=$5
BOOT_STRAP=$6

## Check container name
if [[ "" == $2 ]]; then
	CONTAINER_NAME="ecoledger-node"
	echo "Use default container name: $CONTAINER_NAME"
fi

## Start container
if  [ "start" == "$OPERATION" ]; then
	echo "Startup service!"

	if ! [[ $RPC_PORT =~ ^[0-9]+$ ]]; then
		echo "Error: rpcport should be integer!"
		exit 0
	fi

	if ! [[ $PORT =~ ^[0-9]+$ ]]; then
		echo "Error: port should be integer!"
		exit 0
	fi

	## Check image type name
	if [ "x86" == $IMAGE_TYPE ]; then
		echo "Use x86 version"
		IMAGE_FILE="samuelxu999/ecoledger_node:x86"
	elif [ "arm" == $IMAGE_TYPE ]; then
		echo "Use armv7l version"
		IMAGE_FILE="samuelxu999/ecoledger_node:armv7l"
	else
		echo "Not support image version."
		exit 0
	fi
	## prepare docker image
	docker pull "$IMAGE_FILE"
	docker tag "$IMAGE_FILE" ecoledger_node

	# bootup container node
	./run_node.sh start $CONTAINER_NAME

	if [ "" == "$BOOT_STRAP" ]; then
		echo "Run as boot strap node: 0.0.0.0:$RPC_PORT"
		CMD_Line="python3 /home/docker/app/ENFChain_server.py --blockepoch 3 --pauseepoch 3 --phasedelay 2 -p $PORT --rp $RPC_PORT --firstnode --save_state 60"
	else
		echo "Run as ENF node to contact: $BOOT_STRAP"
		CMD_Line="python3 /home/docker/app/ENFChain_server.py --blockepoch 3 --pauseepoch 3 --phasedelay 2 -p $PORT --rp $RPC_PORT --refresh_neighbors 15 --bootstrapnode $BOOT_STRAP"
	fi
	## run ENF service app
	./docker_exec.sh $CONTAINER_NAME docker "$CMD_Line" &>/dev/null &
	

## Stop container
elif [ "stop" == "$OPERATION" ]; then
	echo "Stop running service!"
	./run_node.sh stop $CONTAINER_NAME
## List container
elif [ "show" == "$OPERATION" ]; then
	echo "Show running service!"
	docker container ls
## show usage
else
	echo "Usage $0 list|start|show| -image_type(x86|armv7l) -container_name rpc_port port bootstrapnode_ip:port"
fi
