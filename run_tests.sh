#!/bin/bash
eval $(ssh-agent)
ssh-add

# Start js9 container
sudo -HE bash -c "source /opt/code/github/jumpscale/bash/zlibs.sh; ZDockerActive -b jumpscale/js9_full -i js9_full"

# Run tests
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /opt/code/github/jumpscale/core9; /bin/bash test.sh\""
