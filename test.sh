#!/bin/bash
set -e
set -x

export JumpscaleMODE=TESTING
pytest -v /opt/code/github/threefoldtech/jumpscale_core/tests/unittests/
unset JumpscaleMODE

# run integration tests
# we need to generate an ssh key
ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa

# init config manager
python3 tests/basic.py

pytest -v tests/integration_tests
