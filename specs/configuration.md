
# configuration/state info of jumpscale9

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

- jumpscale can work without any configuration information, only some preset ENV variables are required (see below and they are by default)
- installtools.py works with these basics & is all which is required

## where are things stored

- the default set of config arguments is

```bash
export HOMEDIR=~
export VARDIR=$HOMEDIR/js9/
export SSHKEYNAME=id_rsa
export DATADIR=$HOMEDIR/data
export CODEDIR=$HOMEDIR/code
export REDISHOST=localhost
export REDISPORT=6379
```

### order of loading info

- redis will be checked on ```$TMPDIR/redis.sock``` or on ```$REDISHOST/PORT```, if found that redis will be used
- if no redis and cache/configration/state is required will be stored in ```$VARDIR/cache``` or ```$VARDIR/cfg``` or ```$VARDIR/state```
    - formats are toml for state & cfg, cache is different

## data formats

### redis

- js9:cfg:config = toml file
- js9:state:$stateName = toml file
- js9:cache:$cacheName:$key = any format, std expiration 1h

### filesystem

- ```$VARDIR/cfg/config.toml```
- ```$VARDIR/state/$name.toml```
- ```$VARDIR/cache/$cachename/$key``` #binary data as a file (first 4 bytes = expiration in epoch, 4 bytes metadata, rest is the binary )
