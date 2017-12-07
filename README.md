# JumpScale 9


[![Join the chat at https://gitter.im/Jumpscale/jumpscale_core9](https://badges.gitter.im/Jumpscale/jumpscale_core9.svg)](https://gitter.im/Jumpscale/jumpscale_core9?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) ![travis](https://travis-ci.org/Jumpscale/core9.svg?branch=master)


JumpScale is a cloud automation product and a branch from what used to be Pylabs. About 7 years ago Pylabs was the basis of a cloud automation product which was acquired by SUN Microsystems from a company called Q-Layer. In the mean time we are 4 versions further and we have rebranded it to JumpScale.


## install in development env (RECOMMENDED)

```bash
#to define branch:
#export JS9BRANCH="9.3.0"
curl https://raw.githubusercontent.com/Jumpscale/core9/master/install.sh?$RANDOM > /tmp/install_js9.sh;bash /tmp/install_js9.sh
```

tested on osx & ubuntu 16.04 (will upgrade brew as part of the process on OSX)

to follow the install

```bash
tail -f /tmp/zutils.log
```

#### to test that it worked:

```bash
js9
```

## shortcut to install using pip3 (not recommended)

```
pip3 install JumpScale9
```

## shortcut to install using pip3 directly from git

```
pip3 install git+https://github.com/Jumpscale/core9@master
```

will checkout in local directory & install
this will not be in development mode !



## how to use after install from python

```bash
 python3 -c 'from js9 import j;print(j.application.getMemoryUsage())'
```

the default mem usage < 23 MB and lazy loading of the modules.

## autocomplete

in  (ofcourse change yourusername)
```
/Users/yourusername/js9host/autocomplete
```

add this path to your editor

