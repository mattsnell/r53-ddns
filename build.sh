#!/bin/sh

# docker image output, if changed here, also update run.sh to match
IMAGE="r53-ddns"

# build the container
docker build \
--tag ${IMAGE} \
.