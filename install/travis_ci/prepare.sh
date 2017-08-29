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


# install python3.5
sudo add-apt-repository -y ppa:fkrull/deadsnakes
sudo apt-get update
sudo apt-get install -y python3.5 python3.5-dev
sudo rm -f /usr/bin/python3
sudo ln -s /usr/bin/python3.5 /usr/bin/python3

export ZUTILSBRANCH=${ZUTILSBRANCH:-fixes}

curl https://raw.githubusercontent.com/Jumpscale/bash/$ZUTILSBRANCH/install.sh?$RANDOM > /tmp/install.sh;sudo -E bash /tmp/install.sh
