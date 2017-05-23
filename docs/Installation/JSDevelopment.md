# Installation

## Supported platforms

- Ubuntu 14+
- Mac OSX Yosemite
- Windows 10: to be completed

## Requirements

- install docker !
- on mac osx you need brew

## Installation

### init of your host os

First execute `jsinit.sh` in order to prepare the installation:

```bash
curl https://raw.githubusercontent.com/Jumpscale/developer/master/jsinit.sh?$RANDOM > $TMPDIR/jsinit.sh; sh $TMPDIR/jsinit.sh
```

### download/start jumpscale docker

```bash
js9_start
```

this will take a while, because this is a development docker and is +1.5GB

To see interactive output do the following in a separate console:
```bash
tail -f /tmp/lastcommandoutput.txt
```

## build jumpscale

If you rather build the system from scratch

```bash
#remove previous dockers, so you build from scratch
js9_destroy
#-l installs extra libs
#-p installs portal
js9_build -l
```

To see all options do ```js9_build -h```

To see interactive output do the following in a separate console:
```bash
tail -f /tmp/lastcommandoutput.txt
```

```
!!!
title = "JSDevelopment"
date = "2017-04-08"
tags = []
```
