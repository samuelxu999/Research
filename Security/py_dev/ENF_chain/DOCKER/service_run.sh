#!/bin/bash


##-------------- Run constainer as background service given args -------------------------------------

OPERATION=$1
CONTAINER_NAME=$2
RPC_PORT=$3
PORT=$4

## Check container name
if [[ "" == $2 ]]; then
	CONTAINER_NAME="ecoledger-node"
	echo "Use default container name: $CONTAINER_NAME"
fi

# Start container
if  [ "start" == "$OPERATION" ] ; then
	echo "Startup service!"

	if ! [[ $RPC_PORT =~ ^[0-9]+$ ]]; then
		echo "Error: rpcport should be integer!"
		exit 0
	fi

	if ! [[ $PORT =~ ^[0-9]+$ ]]; then
		echo "Error: port should be integer!"
		exit 0
	fi

	# bootup container node
	./run_node.sh start $CONTAINER_NAME

	# run geth as node
	./docker_exec.sh $CONTAINER_NAME docker "python3 /home/docker/app/ENFChain_server.py --blockepoch 3 --pauseepoch 3 --phasedelay 2 -p $PORT --rp $RPC_PORT --refresh_neighbors 15" &>/dev/null &

# Stop container
elif [ "stop" == "$OPERATION" ] ; then
	echo "Stop running service!"
	./run_node.sh stop $CONTAINER_NAME
# List container
else
	echo "Show running service!"
	./run_node.sh list
fi
