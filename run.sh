#!/bin/bash

# path to config file
CONFIG_FILE="script/r53-ddns.conf"

# docker image to run
IMAGE="r53-ddns"

# docker log driver (none, syslog, etc)
# https://docs.docker.com/config/containers/logging/configure/
LOG_DRIVER=none

# read config file
source ${CONFIG_FILE}

# run container
docker run \
--interactive \
--rm \
--log-driver ${LOG_DRIVER} \
--env DNS_NAME=${DNS_NAME} \
--env HOSTED_ZONE_ID=${HOSTED_ZONE_ID} \
--env AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID} \
--env AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY} \
${IMAGE}