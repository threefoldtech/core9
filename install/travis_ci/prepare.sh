#!/bin/bash

# generate ssh keys
ssh-keygen -t rsa -N "" -f ~/.ssh/main
export SSHKEYNAME=main

export GIGBRANCH=$(git rev-parse --abbrev-ref HEAD)
echo $GIGBRANCH
curl https://raw.githubusercontent.com/Jumpscale/developer/${GIGBRANCH}/jsinit.sh?$RANDOM > /tmp/jsinit.sh; bash /tmp/jsinit.sh

# build image
js9_build
