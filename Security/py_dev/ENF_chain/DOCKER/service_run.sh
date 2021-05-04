#!/bin/bash

OPERATION=$1

# Start container
if  [ "start" == "$OPERATION" ] ; then
	echo "Startup service!"
	# bootup container node
	./run_ssh.sh start 31181 8181

	# run geth as node
	./docker_exec.sh ecoledger-node docker 'python3 /home/docker/app/ENFChain_server.py --blockepoch 3 --pauseepoch 3 --phasedelay 2 -p 8180 --rp 31180 --refresh_neighbors 15' &>/dev/null &


# Stop container
elif [ "stop" == "$OPERATION" ] ; then
	echo "Stop running service!"
	./run_ssh.sh stop
# List container
else
	echo "Show running service!"
	./run_ssh.sh list
fi
