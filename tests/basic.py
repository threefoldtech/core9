#!/usr/bin/python3
import os
import time
import subprocess
from jumpscale import j

STANDARD_CONFIG_DIR = '/opt/code/local/stdorg/config'

j.sal.fs.createDir(STANDARD_CONFIG_DIR)
path = STANDARD_CONFIG_DIR
if not j.sal.fs.exists("%s/.git" % STANDARD_CONFIG_DIR):
    j.tools.prefab.local.core.run("cd %s && git init ." % STANDARD_CONFIG_DIR)

j.tools.prefab.local.core.run("js_config init -s -k /root/.ssh/id_rsa -p %s" % path)
