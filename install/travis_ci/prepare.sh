#!/bin/bash
set -e

sudo ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa
export SSHKEYNAME=id_rsa

export ZUTILSBRANCH=${ZUTILSBRANCH:-development}

curl https://raw.githubusercontent.com/threefoldtech/jumpscale_core/bash/$ZUTILSBRANCH/install.sh?$RANDOM > /tmp/install.sh;sudo -E bash /tmp/install.sh

sudo -HE bash -c "source /opt/code/github/threefoldtech/jumpscale_bash/zlibs.sh; ZKeysLoad; ZCodeGetJS"
sudo -HE bash -c "source /opt/code/github/threefoldtech/jumpscale_bash/zlibs.sh; ZKeysLoad; ZDockerInstallLocal"
sudo -HE bash -c "source /opt/code/github/threefoldtech/jumpscale_bash/zlibs.sh; ZKeysLoad; ZInstall_js_full"
