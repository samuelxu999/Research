
## Use python36_base image to build service application
FROM python36_base

## Setting up working directory
ENV HOME /home/docker

## ============================ app work directory setup =============================
RUN mkdir ${HOME}/app

## --------- app code and files ---------
COPY ./app/ ${HOME}/app/

## change owner to docker
RUN chown -R docker:docker ${HOME}/app

## ----------- Install requirements ------------
COPY ./requirements.txt ${HOME}/app/
RUN apt-get update -y
RUN python3 -m pip install -r ${HOME}/app/requirements.txt

## Minimize image size 
RUN apt-get autoremove -y && apt-get autoclean -y

WORKDIR ${HOME}/app

## open-access port
EXPOSE 31180 8180

## Default command
#CMD ["python3", "ENFChain_server.py --blockepoch 3 --pauseepoch 3 --phasedelay 2 -p 8180 --rp 31180 --refresh_neighbors 15"]