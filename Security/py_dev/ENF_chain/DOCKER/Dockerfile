
## Use an python3.6 official image as base image
FROM python:3.6-slim

## Developer information
MAINTAINER Samuel Xu <samuelxu999@gmail.com>

## ------------- Dependencies and tools installation ----------------
## Install system tools and dependencies
RUN apt-get update && \
	apt-get install -y \
    build-essential libssl-dev libffi-dev \
	libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev \
	python3 python-dev python3-dev \
	python-pip \
    cmake \
    git \
    wget \
    unzip \
    nano \
    sqlite3 \
    libsqlite3-dev

## Install pip tools and configurations
RUN python3 -m pip install --upgrade pip

## =========================== Setup docker user account ==================================
## Add user so that container does not run as root 
RUN useradd -m docker 
RUN echo "docker:samuelxu999" | chpasswd 
RUN usermod -s /bin/bash docker 
RUN usermod -aG sudo docker

## Setting up working directory
ENV HOME /home/docker

## ============================ app work directory setup =============================
RUN mkdir ${HOME}/app

## --------- app code and files ---------
COPY ./app/ ${HOME}/app/

## change owner to docker
RUN chown -R docker:docker ${HOME}/app

## ----------- Install app requirements ------------
COPY ./requirements.txt ${HOME}/app/
RUN apt-get update -y
RUN python3 -m pip install -r ${HOME}/app/requirements.txt

## Minimize image size 
RUN apt-get autoremove -y && apt-get autoclean -y

WORKDIR ${HOME}/app
