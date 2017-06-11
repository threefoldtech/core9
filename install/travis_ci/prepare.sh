#!/bin/bash

# generate ssh keys
ssh-keygen -t rsa -N "" -f ~/.ssh/main
export SSHKEYNAME=main

export GIGBRANCH=$(git branch | grep \* | cut -d ' ' -f2-)
echo $GIGBRANCH
curl https://raw.githubusercontent.com/Jumpscale/developer/master/jsinit.sh?$RANDOM > /tmp/jsinit.sh; bash /tmp/jsinit.sh

# build image
source ~/.jsenv.sh
js9_build
