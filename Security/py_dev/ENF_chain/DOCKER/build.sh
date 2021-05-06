#!/bin/bash

OPERATION=$1
IMAGE_NAME=$2

## new folders for local test
if [ ! -d "app" ]
then
	mkdir app
fi
## copy server and client code to localtest folder
cp ../ENFChain_server.py app/
cp ../Test_client.py app/

## copy libs to localtest folder
cp -r ../cryptolib app/
cp -r ../network app/
cp -r ../consensus app/
cp -r ../randomness app/
cp -r ../utils app/
cp -r ../kademlia app/
cp -r ../rpcudp app/

## copy swarm_server.json 
cp ../swarm_server.json app/

## copy data
cp -r ../data app/

## copy requirements.txt 
cp ../requirements.txt ./

## Check image name
if [[ "" == $2 ]]; then
	IMAGE_NAME="ecoledger_node"
	#echo "Use default image $IMAGE_NAME ...!"
fi

## Liat all image
if [[ "list" == $OPERATION ]]; then
	echo "List image $IMAGE_NAME ...!"
	docker image ls $IMAGE_NAME
	#docker image ls

## Make image
elif [[ "make" == $OPERATION ]]; then
	echo "Start make $IMAGE_NAME ...!"
	docker build -t $IMAGE_NAME .

## Clean image given IMAGE_NAME
elif [[ "clean" == $OPERATION ]]; then
	echo "Remove $IMAGE_NAME ...!"
	docker image rm -f $IMAGE_NAME

else
	echo "Usage $0 cmd[list|make|clean|] image_name"
fi

