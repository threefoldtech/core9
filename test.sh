#!/bin/bash
set -e
set -x

export JS9MODE=TESTING
pytest -v /opt/code/github/jumpscale/core9/tests/unittests/
unset JS9MODE
