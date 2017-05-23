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

```toml
[dirs]
HOMEDIR = "~"
TMPDIR = "/tmp"
VARDIR = "/optvar/var"
BASEDIR = "/opt/jumpscale9"
CFGDIR = "{{VARDIR}}/cfg"
DATADIR = "{{VARDIR}}/data"
CODEDIR = "/opt/code"
BUILDDIR = "{{VARDIR}}/build"
LIBDIR = "{{BASEDIR}}/lib/"
TEMPLATEDIR = "{{BASEDIR}}/templates"
```

else:

```toml
[dirs]
HOMEDIR = "~"
TMPDIR = "/tmp"
VARDIR = "{{GIGDIR}}/var"
BASEDIR = "{{GIGDIR}}/gig"
CFGDIR = "{{VARDIR}}/cfg"
DATADIR = "{{VARDIR}}/data"
CODEDIR = "{{GIGDIR}}/code"
BUILDDIR = "{{VARDIR}}/build"
LIBDIR = "{{BASEDIR}}/lib/"
TEMPLATEDIR = "{{BASEDIR}}/templates"

```

following info comes after it

```toml

[email]
from = "info@incubaid.com"
smtp_port = 443
smtp_server = ""

[git.ays]
branch = "master"
url = "https://github.com/Jumpscale/ays9.git"

[git.js]
branch = "master"
url = "https://github.com/Jumpscale/core9.git"


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
