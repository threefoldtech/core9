#!/bin/bash

export GIGBRANCH=$(git rev-parse --abbrev-ref HEAD)
curl https://raw.githubusercontent.com/Jumpscale/developer/${GIGBRANCH}/jsinit.sh?$RANDOM > /tmp/jsinit.sh; bash /tmp/jsinit.sh

# build image
js9_build
