#!/bin/bash
eval $(ssh-agent)
ssh-add

# Run tests
sudo -HE bash -c "ssh -tA  root@localhost -p 2222 \"cd /opt/code/github/jumpscale/core9; /bin/bash test.sh\""
