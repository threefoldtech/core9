#!/bin/bash

# generate ssh keys
# ssh-keygen -t rsa -N "" -f ~/.ssh/main
# export SSHKEYNAME=main

# export GIGSAFE=1
# export GIGDEVELOPERBRANCH=master

# curl https://raw.githubusercontent.com/Jumpscale/developer/$GIGDEVELOPERBRANCH/jsinit.sh?$RANDOM > /tmp/jsinit.sh; bash /tmp/jsinit.sh

# build image
# source ~/.jsenv.sh
# js9_build

export ZUTILSBRANCH=${ZUTILSBRANCH:-fixes}

curl https://raw.githubusercontent.com/Jumpscale/bash/$ZUTILSBRANCH/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh
