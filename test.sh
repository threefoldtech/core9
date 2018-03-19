#!/bin/bash
set -e
set -x

export JS9MODE=TESTING
pytest -v /opt/code/github/jumpscale/core9/tests/unittests/
unset JS9MODE

# run integration tests
# init config manager
python3 tests/basic.py

pytest -v tests/integration_tests
