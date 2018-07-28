#!/bin/bash
set -e
set -x

export SSHKEYNAME=id_rsa

# Start js9 container
sudo -HE bash -c "source /opt/code/github/threefoldtech/jumpscale_bash/zlibs.sh; ZKeysLoad; ZDockerActive -b jumpscale/js9_full -i js9_full"

# Install pytest
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"pip install -U pytest\""

# Run tests
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /opt/code/github/threefoldtech/jumpscale_core9; /bin/bash test.sh\""
