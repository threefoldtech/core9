#!/bin/bash
export JS9MODE=TESTING
pytest -v /opt/code/github/jumpscale/core9/JumpScale9/
unset JS9MODE
