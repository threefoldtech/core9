# JumpScale 9


[![Join the chat at https://gitter.im/Jumpscale/jumpscale_core9](https://badges.gitter.im/Jumpscale/jumpscale_core9.svg)](https://gitter.im/Jumpscale/jumpscale_core9?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


JumpScale is a cloud automation product and a branch from what used to be Pylabs. About 7 years ago Pylabs was the basis of a cloud automation product which was acquired by SUN Microsystems from a company called Q-Layer. In the mean time we are 4 versions further and we have rebranded it to JumpScale.


## install in development env (RECOMMENDED)

- this means will be installed in a local docker
- see https://github.com/Jumpscale/developer

## how to install from master on own system (not in docker development mode)
Should be executed under root.

```
cd $TMPDIR
rm -f install.sh
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core9/master/install/install.sh?$RANDOM > install.sh
bash install.sh
```

## how to install from a branch.
Should be executed under root.

```
cd $TMPDIR
rm -f install.sh
export JSBRANCH="???"
curl -k https://raw.githubusercontent.com/Jumpscale/jumpscale_core9/$JSBRANCH/install/install.sh?$RANDOM > install.sh
bash install.sh
```
