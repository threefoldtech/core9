#for development mode

export ZLogFile='/tmp/zutils.log'

die() {
    set +x
    rm -f /tmp/sdwfa #to remove temp passwd for restic, just to be sure
    echo
    echo "**** ERRORLOG ****"
    cat $ZLogFile
    echo
    echo "[-] something went wrong: $1"
    echo
    echo
    # set -x
    exit 1
}

ZUtilsGetCode() {
    mkdir -p $ZUTILSDIR
    #giturl like: git@github.com:mathieuancelin/duplicates.git
    # local giturl=git@github.com:Jumpscale/bash.git
    local giturl=https://github.com/Jumpscale/bash.git
    local branch=${ZUTILSBRANCH:-development}
    echo "[+] get code $giturl ($branch)"
    pushd $ZUTILSDIR 2>&1 >> $ZLogFile

    if ! grep -q ^github.com ~/.ssh/known_hosts 2> /dev/null; then
        mkdir -p ~/.ssh
        ssh-keyscan github.com >> ~/.ssh/known_hosts 2>&1 >> $ZLogFile || die || return 1
    fi

    if [ ! -e $ZUTILSDIR/bash ]; then
        echo " [+] clone zutils"
        git clone -b ${branch} $giturl bash 2>&1 >> $ZLogFile || die || return 1
    else
        pushd $ZUTILSDIR/bash
        echo " [+] pull"
        git pull  2>&1 >> $ZLogFile || die || return 1
        popd > /dev/null 2>&1
    fi
    popd > /dev/null 2>&1
}

cd /tmp

export ZUTILSBRANCH=${ZUTILSBRANCH:-development}

echo "INSTALL Jumpscale9"
#!/bin/bash

set -e

sudo rm -rf $TMPDIR/zutils_done > /dev/null 2>&1
sudo rm -rf /tmp/zutils_done > /dev/null 2>&1

if [ -z "$HOMEDIR" ] ; then
    export HOMEDIR="$HOME"
fi

if [ -z "$HOMEDIR" ] ; then
    echo "[-] ERROR, could not specify homedir"
    exit 1
fi

if [ "$(uname)" == "Darwin" ]; then
    set +e
    which xcode-select 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        xcode-select --install
    fi
    which brew 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
    curl -V 2>&1 >> /dev/null
    if [ $? -ne 0 ]; then
        brew install curl
    fi
    export ZUTILSDIR=${ZUTILSDIR:-~/code/github/threefoldtech/jumpscale_core9}
    set -e

elif [ -f /etc/redhat-release ]; then
    dnf update
    dnf install curl git wget -y
    export ZUTILSDIR=${ZUTILSDIR:-/opt/code/github/threefoldtech/jumpscale_core9}
elif [ -f /etc/arch-release ]; then
    pacman -S --noconfirm curl git wget
    export ZUTILSDIR=${ZUTILSDIR:-/opt/code/github/threefoldtech/jumpscale_core9}
else
    #TODO: *2 need to support windows as well
    sudo apt-get update
    sudo apt-get install curl -y
    sudo apt-get install git wget -y
    export ZUTILSDIR=${ZUTILSDIR:-/opt/code/github/threefoldtech/jumpscale_core9}
fi

#if not exist then do in /opt/code...


export ZLogFile='/tmp/zutils.log'


if [ ! -f $HOMEDIR/.bashrc ]; then
   touch $HOMEDIR/.bashrc
fi

if [ ! -f $HOMEDIR/.bashrc ]; then
   sed -i.bak '/jsenv.sh/d' $HOMEDIR/.profile
fi

rm -f ~/jsenv.sh
rm -f ~/jsinit.sh

sed -i.bak '/export SSHKEYNAME/d' $HOMEDIR/.bashrc
sed -i.bak '/jsenv.sh/d' $HOMEDIR/.bashrc
sed -i.bak '/.*zlibs.sh/d' $HOMEDIR/.bashrc
echo ". ${ZUTILSDIR}/bash/zlibs.sh" >> $HOMEDIR/.bashrc

if [ ! -e ~/.iscontainer ] ; then
    ZUtilsGetCode
    . ${ZUTILSDIR}/bash/zlibs.sh
else
    . ${ZUTILSDIR}/bash/zlibs.sh
fi

echo "[+] Install OK"

echo "load zlibs"
if [ -f ~/code/github/threefoldtech/jumpscale_core9/bash/zlibs.sh ]; then
    source ~/code/github/threefoldtech/jumpscale_core9/bash/zlibs.sh 2>&1 > /dev/null
elif [ -f /opt/code/github/threefoldtech/jumpscale_core9/bash/zlibs.sh ]; then
    source /opt/code/github/threefoldtech/jumpscale_core9/bash/zlibs.sh 2>&1 > /dev/null
else
    die "Cannot find zlibs"
fi


ZDoneReset

rm ~/js9host/cfg/me.toml > /dev/null 2>&1
rm ~/js9host/cfg/jumpscale9.toml > /dev/null 2>&1

echo "install js9"
ZInstall_host_js9 || die "Could not install core9 of js9" || exit 1

pip3 install Cython
# pip3 install asyncssh
pip3 install numpy
# pip3 install tarantool
pip3 install PyNaCl --upgrade

