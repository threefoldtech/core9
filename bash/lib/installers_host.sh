


ZInstall_host_code_jumpscale() {
    if ZDoneCheck "ZInstall_host_code_jumpscale" ; then
        echo "[+] update jumpscale code was already done."
       return 0
    fi

    local branch='development'
    if [ ! -z $1 ]
    then
        branch=$1
    elif [ ! -z ${JS9BRANCH} ]
    then
        branch=${JS9BRANCH}
    fi
    echo "[+] loading or updating jumpscale source code (branch:$branch)"
    ZCodeGetJS -r core9 -b $branch || return 1
    ZCodeGetJS -r lib9 -b $branch  || return 1
    ZCodeGetJS -r prefab9 -b $branch || return 1
    echo "[+] update jumpscale code done"
    ZDoneSet "ZInstall_host_code_jumpscale"
}


ZInstall_host_js9() {

    if ZDoneCheck "ZInstall_host_js9" ; then
        echo "[+] Host jumpscale installation already done."
       return 0
    fi

    ZCodeConfig

    ZInstall_host_base || die "Could not ZInstall_host_base" || return 1

    ZInstall_host_code_jumpscale || die "Could not ZInstall_host_code_jumpscale" || return 1

    ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts > ${ZLogFile} 2>&1

    mkdir -p $HOME/js9host

    echo "[+] clean previous js9 install"
    rm -rf /usr/local/lib/python3.6/site-packages/JumpScale9*
    rm -rf /usr/local/lib/python3.6/site-packages/js9*

    echo "[+] install js9"
    pushd $ZCODEDIR/github/threefoldtech/core9
    cp /$ZCODEDIR/github/threefoldtech/core9/mascot $HOMEDIR/.mascot.txt || die "Could not copy mascot" || return 1
    pip3 install -e . > ${ZLogFile} 2>&1 || die "Could not install core9 of js9" || return 1
    popd
    # pip3 install -e $ZCODEDIR/github/threefoldtech/core9 || die "could not install core9 of js9" || return 1

    echo "[+] load env"
    python3 -c 'from JumpScale9 import j;j.tools.executorLocal.initEnv()' > ${ZLogFile} 2>&1 || die "Could not install core9 of js9, initenv" || return 1
    python3 -c 'from JumpScale9 import j;j.tools.jsloader.generate()'  > ${ZLogFile} 2>&1  || die "Could not install core9 of js9, jsloader" || return 1

    echo "[+] installing jumpscale lib9"
    pushd $ZCODEDIR/github/threefoldtech/lib9
    pip3 install docker
    pip3 install --no-deps -e .  > ${ZLogFile} 2>&1 || die "Coud not install lib9 of js9" || return 1
    popd


    echo "[+] installing jumpscale prefab9"
    pushd $ZCODEDIR/github/threefoldtech/prefab9
    pip3 install -e .  > ${ZLogFile} 2>&1 || die "Coud not install prefab9" || return 1
    popd
    # pip3 install -e $ZCODEDIR/github/threefoldtech/prefab9 || die "could not install prefab9" || return 1

    # echo "[+] installing binaries files"
    # find  $ZCODEDIR/github/threefoldtech/core9/cmds -exec ln -s {} "/usr/local/bin/" \; || die || return 1
    #
    # rm -rf /usr/local/bin/cmds
    # rm -rf /usr/local/bin/cmds_guest

    echo "[+] initializing jumpscale"
    python3 -c 'from JumpScale9 import j;j.tools.jsloader.generate()' > ${ZLogFile} 2>&1  || die "Could not install core9 of js9, jsloader" || return 1

    echo "[+] js9 installed (OK)"

    ZDoneSet "ZInstall_host_js9"

}


ZInstall_host_base(){

    if ZDoneCheck "ZInstall_host_base" ; then
        echo "[+] ZInstall_host_base already installed"
       return 0
    fi

    if [ "$(uname)" == "Darwin" ]; then
        # echo "[+] upgrade brew"
        # brew upgrade  >> ${ZLogFile} 2>&1 || die "could not upgrade all brew installed components" || return 1

        echo "[+] installing git, python3, mc, tmux, curl"
        Z_brew_install mc wget python3 git unzip rsync tmux curl || return 1

        echo "[+] set system config params"
        echo kern.maxfiles=65536 | sudo tee -a /etc/sysctl.conf >> ${ZLogFile} 2>&1 || die || return 1
        echo kern.maxfilesperproc=65536 | sudo tee -a /etc/sysctl.conf >> ${ZLogFile} 2>&1 || die || return 1
        sudo sysctl -w kern.maxfiles=65536 >> ${ZLogFile} 2>&1 || die || return 1
        sudo sysctl -w kern.maxfilesperproc=65536 >> ${ZLogFile} 2>&1 || die || return 1
        ulimit -n 65536 >> ${ZLogFile} 2>&1 || die || return 1


    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        dist=''
        dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
        if [ "$dist" == "Ubuntu" ]; then
            echo "[+] updating packages"
            sudo apt-get update >> ${ZLogFile} 2>&1 || die "could not update packages" || return 1

            echo "[+] installing git, python, mc, tmux, curl"
            Z_apt_install mc wget python3 git unzip rsync tmux curl build-essential python3-dev || return 1

        fi
    else
        die "platform not supported"
    fi

    if [ "$(uname)" == "Darwin" ]; then
        echo "no need to install pip, should be installed already"
    else
        curl -sk https://bootstrap.pypa.io/get-pip.py > /tmp/get-pip.py || die "could not download pip" || return 1
        python3 /tmp/get-pip.py  >> ${ZLogFile} 2>&1 || die "pip install" || return 1
        rm -f /tmp/get-pip.py
    fi

    echo "[+] upgrade pip"
    pip3 install --upgrade pip >> ${ZLogFile} 2>&1 || die "pip upgrade" || return 1

    ZDoneSet "ZInstall_host_base"
}



# ZInstall_host_ipfs() {
#     if ZDoneCheck "ZInstall_host_ipfs" ; then
#         echo "[+] ZInstall_host_ipfs already installed"
#        return 0
#     fi
#
#     # container "cd tmp; mkdir -p ipfs; cd ipfs; wget --inet4-only https://dist.ipfs.io/go-ipfs/v0.4.10/go-ipfs_v0.4.10_linux-amd64.tar.gz"
#     if [ "$(uname)" == "Darwin" ]; then
#         rm -rf /tmp/ipfs
#         mkdir -p /tmp/ipfs
#         Z_pushd /tmp/ipfs
#         wget --inet4-only https://dist.ipfs.io/go-ipfs/v0.4.10/go-ipfs_v0.4.10_darwin-amd64.tar.gz
#         ipfs daemon --init &
#         Z_popd || return 1
#
#     elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
#         dist=''
#         dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
#         if [ "$dist" == "Ubuntu" ]; then
#             rm -rf /tmp/ipfs
#             mkdir -p /tmp/ipfs
#             Z_pushd /tmp/ipfs
#             wget https://dist.ipfs.io/go-ipfs/v0.4.10/go-ipfs_v0.4.10_linux-amd64.tar.gz --output-document go-ipfs.tar.gz
#             tar xvfz go-ipfs.tar.gz
#             mv go-ipfs/ipfs /usr/local/bin/ipfs
#             ipfs daemon --init &
#
#             Z_popd || return 1
#
#         fi
#     else
#         die "platform not supported"
#     fi
#
#     ZDoneSet "ZInstall_host_ipfs"
#
# }


# ZCodePluginInstall(){
#     Z_mkdir ~/.code_data_dir || return 1
#     code --install-extension $1 --user-data-dir=~/.code_data_dir >> ${ZLogFile} 2>&1 || die  "could not code install extension $1" || return 1
# }


# this will install a full js9 with all required system dependencies
ZInstall_host_js9_full() {

    if ZDoneCheck "ZInstall_host_js9_full" ; then
        echo "[+] Host jumpsacle full isntallation already done."
       return 0
    fi

    ZCodeConfig

    ZInstall_host_base

    ZInstall_host_code_jumpscale

    ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

    echo "[+] install js9"
    pushd $ZCODEDIR/github/threefoldtech/core9
    /bin/bash install.sh || die "Could not install core9 of js9" || return 1
    popd
    # pip3 install -e $ZCODEDIR/github/threefoldtech/core9 || die "could not install core9 of js9" || return 1

    echo "[+] installing jumpscale lib9"
    pushd $ZCODEDIR/github/threefoldtech/lib9
    /bin/bash install.sh || die "Coud not install lib9 of js9" || return 1
    popd
    # pip3 install --no-deps -e $ZCODEDIR/github/threefoldtech/lib9 || die "could not install lib9 of js9" || return 1

    echo "[+] installing jumpscale prefab9"
    pushd $ZCODEDIR/github/threefoldtech/prefab9
    /bin/bash install.sh || die "Coud not install prefab9" || return 1
    popd

    echo "[+] initializing jumpscale"
    python3 -c 'from JumpScale9 import j;j.tools.jsloader.generate()' || die "js9 generate" || return 1

    echo "[+] js9 installed (OK)"

    ZDoneSet "ZInstall_host_js9_full"

}

