#!/bin/bash
set -e
set -x

export JS9MODE=TESTING
pytest -v /opt/code/github/jumpscale/core9/tests/unittests/
unset JS9MODE

# run integration tests
# we need to generate an ssh key
ssh-keygen -t rsa -N "" -f /root/.ssh/id_rsa

# init config manager
python3 tests/basic.py

pytest -v tests/integration_tests
