# Jumpscale Config Files


## types

- configuration info
    - mail config
    - name/email
    - sshkey
    - ...
- state info
    - e.g. done installs
- cache info
    - in redis only

## principles

- jumpscale can work without any configuration information
- configuration is in redis or in 1 file on the filesystem

### order of loading info

- redis will be checked on ```$TMPDIR/redis.sock``` or on ```$REDISHOST/PORT```, if found that redis will be used
- if no redis and cache/configration/state is required will be stored in ```$VARDIR/cache``` or ```$VARDIR/cfg``` or ```$VARDIR/state```
    - formats are toml for state & cfg, cache is different

## data formats

### redis

- js9:cfg:config = toml file
- js9:state:$stateName:$key = binary
- js9:cache:$cacheName:$key = binary, std expiration 1h

### filesystem

- ```$VARDIR/cfg/config.toml```
- ```$VARDIR/state/$name.toml```
- ```$VARDIR/cache/$cachename/$key``` #binary data as a file (first 4 bytes = expiration in epoch, 4 bytes metadata, rest is the binary )

## default configuration

if container:

when container starts /host is mapped to ~/container (on host)

```toml
[dirs]
HOMEDIR = "~"
TMPDIR = "/tmp"
VARDIR = "/optvar"
BASEDIR = "/opt/jumpscale9"
CFGDIR = "{{VARDIR}}/cfg"
DATADIR = "/host/data"
CODEDIR = "/opt/code"
BUILDDIR = "/host/build"
LIBDIR = "{{BASEDIR}}/lib/"
TEMPLATEDIR = "{{BASEDIR}}/templates"
LOGDIR = "/host/log"
JSAPPSDIR = "{{BASEDIR}}/apps"
BINDIR="{{BASEDIR}}/bin"
```

else:

```toml
[dirs]
HOMEDIR = "~"
TMPDIR = "/tmp"
VARDIR = "{{HOMEDIR}}/opt/var"
BASEDIR = "{{HOMEDIR}}/opt/jumpscale9"
CFGDIR = "{{VARDIR}}/cfg"
DATADIR = "{{VARDIR}}/data"
CODEDIR = "{{HOMEDIR}}/code"
BUILDDIR = "{{VARDIR}}/build"
LIBDIR = "{{BASEDIR}}/lib/"
TEMPLATEDIR = "{{BASEDIR}}/templates"
LOGDIR = "{{VARDIR}}/log"
JSAPPSDIR = "{{BASEDIR}}/apps"
BINDIR="{{BASEDIR}}/bin"

```

following info comes after it

```toml

[email]
from = "info@incubaid.com"
smtp_port = 443
smtp_server = ""

[git.ays]
branch = "master"
url = "https://github.com/threefoldtech/jumpscale_/ays9.git"

[git.js]
branch = "master"
url = "https://github.com/threefoldtech/jumpscale_core9.git"


[system]
debug = true
autopip = false
readonly = false
container = false

[grid]
gid = 0
nid = 0

[redis]
port = 6379
addr = "localhost"

[me]
fullname = "Kristof De Spiegeleer"

[ssh]
SSHKEYNAME = "id_rsa"

```


```
!!!
title = "Jumpscaleconfigfiles"
date = "2017-04-08"
tags = []
```
