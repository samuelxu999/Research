#!/bin/bash

OPERATION=$1
IMAGE_NAME=$2

# Check image name
if [[ "" == $2 ]]; then
	IMAGE_NAME="python36_base"
	#echo "Use default image $IMAGE_NAME ...!"
fi

# Liat all image
if [[ "list" == $OPERATION ]]; then
	echo "List image $IMAGE_NAME ...!"
	docker image ls $IMAGE_NAME
	#docker image ls

# Make image
elif [[ "make" == $OPERATION ]]; then
	echo "Start make $IMAGE_NAME ...!"
	docker build -t $IMAGE_NAME -f Dockerfile.base .

# Clean image given IMAGE_NAME
elif [[ "clean" == $OPERATION ]]; then
	echo "Remove $IMAGE_NAME ...!"
	docker image rm -f $IMAGE_NAME

else
	echo "Usage $0 cmd[list|make|clean|] image_name"
fi

