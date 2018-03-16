# To use (mount) host configuration in your container

you should run the container using `ZDockerActive ` tool
it will mount the those dirs from host to docker
```
|============================================================|
|host                        |             docker            |
|============================================================|
|/root/js9host               |             /host             |
|------------------------------------------------------------|
|/root/js9host/cfg           |             /hostcfg          |
|------------------------------------------------------------|
|/opt/code                   |             /opt/code         |
|------------------------------------------------------------|
|/root/js9host/.cache/pip    |            /root/.cache/pip   |
|============================================================|

```

# If you are using container
```python

BASEDIR              : /opt
BASEDIRJS            : /opt/jumpscale9
BINDIR               : /opt/bin
BUILDDIR             : /host/var/build
CFGDIR               : /hostcfg
CODEDIR              : /opt/code
DATADIR              : /host/var/data
HOMEDIR              : /root
HOSTCFGDIR           : /hostcfg
HOSTDIR              : /host
JSAPPSDIR            : /opt/jumpscale9/apps/
LIBDIR               : /opt/lib/
LOGDIR               : /host/var/log
TEMPLATEDIR          : /host/var/templates/
TMPDIR               : /tmp
VARDIR               : /host/var
```

# If you are using host based installation

```python
BASEDIR              : /opt
BASEDIRJS            : /opt/jumpscale9
BINDIR               : /opt/bin
BUILDDIR             : /opt/var/build
CFGDIR               : /opt/cfg
CODEDIR              : /opt/code
DATADIR              : /opt/var/data
HOMEDIR              : /root
HOSTCFGDIR           : /root/js9host/cfg/
HOSTDIR              : /root/js9host/
JSAPPSDIR            : /opt/jumpscale9/apps/
LIBDIR               : /opt/lib/
LOGDIR               : /opt/var/log
TEMPLATEDIR          : /opt/var/templates/
TMPDIR               : /tmp
VARDIR               : /opt/var
```