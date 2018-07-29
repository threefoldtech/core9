

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


Z_pushd(){
    echo "pushd to: $1" >> $ZLogFile
    pushd "$1" >> $ZLogFile 2>&1 || die "could not pushd to $1" || return 1
}

Z_popd(){
    popd > /dev/null || die "could not popd" || return 1
}

Z_mkdir(){
    echo "mkdir: $1" >> $ZLogFile
    mkdir -p "$1" >> $ZLogFile 2>&1 || die "could not mkdir $1" || return 1
}

Z_mkdir_pushd(){
    Z_mkdir "$1" || return 1
    Z_pushd "$1" || return 1
}

Z_brew_install(){
    echo "brew install: $@" >> $ZLogFile
    brew install  $@ >> $ZLogFile 2>&1 || die "could not brew install $@" || return 1
}

Z_apt_install(){
  echo "apt-get install: $@" >> $ZLogFile
  sudo apt-get -y install $@ >> $ZLogFile 2>&1 || die "could not install package $@" || return 1
}

Z_exists_dir(){
    if [ ! -d "$1" ]; then
        die "dir $1 not found" || return 1
    fi
}

Z_exists_file(){
    if [ ! -f "$1" ]; then
        die "file $1 not found" || return 1
    fi
}



ZCodeGetJSUsage() {
   cat <<EOF
Usage: ZCodeGet [-r reponame] [-g giturl] [-a account] [-b branch]
   -r reponame: name or repo which is being downloaded
   -b branchname: defaults to development
   -h: help

check's out jumpscale repo to $ZCODEDIR/github/threefoldtech/$reponame
branchname can optionally be specified.

if specified but repo exists then a pull will be done & branch will be ignored !!!

if reponame not specified then will checkout
- lib9
- core9
- prefab

EOF
}

ZCodeGetJS() {
    echo FUNCTION: ${FUNCNAME[0]} >> $ZLogFile

    local OPTIND
    local account='threefoldtech'
    local reponame=''
    local branch=${JS9BRANCH:-development}
    while getopts "r:b:h" opt; do
        case $opt in
           r )  reponame=$OPTARG ;;
           b )  branch=$OPTARG ;;
           h )  ZCodeGetJSUsage ; return 0 ;;
           \? )  ZCodeGetJSUsage ; return 1 ;;
        esac
    done

    if [ -z "$reponame" ]; then
        ZCodeGetJS -r jumpscale_core9  -b $branch || return 1
        ZCodeGetJS -r jumpscale_lib9 -b $branch || return 1
        ZCodeGetJS -r jumpscale_prefab9 -b $branch || return 1
        return 0
    fi

    # local giturl="git@github.com:Jumpscale/$reponame.git"
    local githttpsurl="https://github.com/threefoldtech/$reponame.git"

    # check if specificed branch or $JS9BRANCH exist, if not then fallback to development
    JS9BRANCHExists ${githttpsurl} ${branch} || branch=development

    # ZCodeGet -r $reponame -a $account -u $giturl -b $branch  || ZCodeGet -r $reponame -a $account -u $githttpsurl -b $branch || return 1
    ZCodeGet -r $reponame -a $account -u $githttpsurl -b $branch || return 1

}

ZCodeGetUsage() {
   cat <<EOF
Usage: ZCodeGet [-r reponame] [-g giturl] [-a account] [-b branch]
   -t type: default is github but could be e.g. gitlab, ...
   -a account: will default to 'varia', but can be account name
   -r reponame: name or repo which is being downloaded
   -u giturl: e.g. git@github.com:mathieuancelin/duplicates.git
   -b branchname: defaults to development
   -k sshkey: path to sshkey to use for authorization when connecting to the repository.
   -h: help

check's out any git repo repo to $ZCODEDIR/$type/$account/$reponame
branchname can optionally be specified.

if specified but repo exists then a pull will be done & branch will be ignored !!!

EOF
}
#to return to original dir do Z_pushd
ZCodeGet() {
    echo FUNCTION: ${FUNCNAME[0]} > $ZLogFile
    local OPTIND
    local type='github'
    local account='varia'
    local reponame=''
    local giturl=''
    local branch=${JS9BRANCH:-development}
    local sshkey=''
    while getopts "a:r:u:b:t:k:h" opt; do
        case $opt in
           a )  account=$OPTARG ;;
           t )  type=$OPTARG ;;
           r )  reponame=$OPTARG ;;
           u )  giturl=$OPTARG ;;
           b )  branch=$OPTARG ;;
           k )  sshkey=$OPTARG ;;
           h )  ZCodeGetUsage ; return 0 ;;
           \? )  ZCodeGetUsage ; return 1 ;;
        esac
    done
    if [ -z "$giturl" ]; then
        ZCodeGetUsage
        return 0
    fi

    if [ -z "$reponame" ]; then
        ZCodeGetUsage
        return 0
    fi

    echo "[+] get code $giturl ($branch)"

    Z_mkdir_pushd $ZCODEDIR/$type/$account || return 1

    # check if docs.greenitglobe.com (gogs) in the url
    if grep -q docs.greenitglobe.com <<< $giturl; then
        ssh-keyscan -t rsa docs.greenitglobe.com >> ~/.ssh/known_hosts 2>&1 >> $ZLogFile || die "ssh keyscan" || return 1
    fi

    if ! grep -q ^github.com ~/.ssh/known_hosts 2> /dev/null; then
        ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts 2>&1 >> $ZLogFile || die "ssh keyscan" || return 1
    fi

    if [ ! -e $ZCODEDIR/$type/$account/$reponame ]; then
        echo " [+] clone"
        git clone -b ${branch} $giturl $reponame 2>&1 >> $ZLogFile || die "git clone" || return 1
    else
        Z_pushd $ZCODEDIR/$type/$account/$reponame || return 1
        echo " [+] pull"
        echo 'git pull' >> $ZLogFile
        git pull  2>&1 >> $ZLogFile || die "could not git pull" || return 1
        Z_popd || return 1
    fi
    Z_popd || return 1
}

JS9BRANCHExists() {
    local giturl="$1"
    local branch=${2:-${JS9BRANCH}}

    # remove the trailing .git from the giturl if exist
    giturl=${giturl%.git}

    echo "[+] Checking if ${giturl}/tree/${branch} exists"
    httpcode=$(curl -o /dev/null -I -s --write-out '%{http_code}\n' $giturl/tree/${branch})

    if [ "$httpcode" = "200" ]; then
        return 0
    else
      echo "[+] Error: ${giturl}/tree/${branch} does not exist"
        return 1
    fi
}

ZInstall_host_js9() {

    # if ZDoneCheck "ZInstall_host_js9" ; then
    #     echo "[+] Host jumpscale installation already done."
    #    return 0
    # fi

    mkdir -p $HOME/js9host

    echo "[+] clean previous js9 install"
    rm -rf /usr/local/lib/python3.6/site-packages/JumpScale9*
    rm -rf /usr/local/lib/python3.6/site-packages/js9*

    echo "[+] install js9"
    pushd $ZCODEDIR/github/threefoldtech/jumpscale_core9
    pip3 install -e . > ${ZLogFile} 2>&1 || die "Could not install core9 of js9" || return 1
    popd
    # pip3 install -e $ZCODEDIR/github/threefoldtech/jumpscale_core9 || die "could not install core9 of js9" || return 1

    echo "[+] load env"
    python3 -c 'from JumpScale9 import j;j.tools.executorLocal.initEnv()' > ${ZLogFile} 2>&1 || die "Could not install core9 of js9, initenv" || return 1
    python3 -c 'from JumpScale9 import j;j.tools.jsloader.generate()'  > ${ZLogFile} 2>&1  || die "Could not install core9 of js9, jsloader" || return 1

    echo "[+] installing jumpscale lib9"
    pushd $ZCODEDIR/github/threefoldtech/jumpscale_lib9
    # pip3 install docker
    pip3 install --no-deps -e .  > ${ZLogFile} 2>&1 || die "Coud not install lib9 of js9" || return 1
    popd


    echo "[+] installing jumpscale prefab9"
    pushd $ZCODEDIR/github/threefoldtech/jumpscale_prefab9
    pip3 install -e .  > ${ZLogFile} 2>&1 || die "Coud not install prefab9" || return 1
    popd
    # pip3 install -e $ZCODEDIR/github/threefoldtech/jumpscale_prefab9 || die "could not install prefab9" || return 1

    # echo "[+] installing binaries files"
    # find  $ZCODEDIR/github/threefoldtech/jumpscale_core9/cmds -exec ln -s {} "/usr/local/bin/" \; || die || return 1
    #
    # rm -rf /usr/local/bin/cmds
    # rm -rf /usr/local/bin/cmds_guest

    echo "[+] initializing jumpscale"
    python3 -c 'from JumpScale9 import j;j.tools.jsloader.generate()' > ${ZLogFile} 2>&1  || die "Could not install core9 of js9, jsloader" || return 1

    pip3 install Cython --upgrade  || die || return 1
    # pip3 install asyncssh
    pip3 install numpy --upgrade  || die || return 1
    # pip3 install tarantool
    pip3 install PyNaCl --upgrade || die || return 1


    echo "[+] js9 installed (OK)"

    # ZDoneSet "ZInstall_host_js9"

}


ZInstall_host_base(){

    # if ZDoneCheck "ZInstall_host_base" ; then
    #     echo "[+] ZInstall_host_base already installed"
    #    return 0
    # fi

    if [ "$(uname)" == "Darwin" ]; then

        if [ -n "$JSFULL" ] ; then
            echo "[+] check to install xcode (am in jsfull development mode)"
            which xcode-select 2>&1 >> /dev/null
            if [ $? -ne 0 ]; then
                xcode-select --install
            fi
        fi

        which brew 2>&1 >> /dev/null
        if [ $? -ne 0 ]; then
            /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
        fi

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

        if [ -n "$JSFULL" ] ; then
            echo "[+] installing development tools: build essential & pythondev"
            Z_apt_install  build-essential python3-dev
        fi

    elif [ "$(expr substr $(uname -s) 1 5)" == "Linux" ]; then
        dist=''
        dist=`grep DISTRIB_ID /etc/*-release | awk -F '=' '{print $2}'`
        if [ "$dist" == "Ubuntu" ]; then
            echo "[+] updating packages"
            sudo apt-get update >> ${ZLogFile} 2>&1 || die "could not update packages" || return 1

            echo "[+] installing git, python, mc, tmux, curl"
            Z_apt_install mc wget python3 git unzip rsync tmux curl || return 1

            if [ -n "$JSFULL" ] ; then
                echo "[+] installing development tools: build essential & pythondev"
                Z_apt_install  build-essential python3-dev
            fi

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

    # ZDoneSet "ZInstall_host_base"
}





#########################################################
#########################################################

#remove old stuff
rm -rf /usr/local/bin/js9_*
rm -f ~/jsenv.sh
rm -f ~/jsinit.sh
sed -i.bak '/jsenv.sh/d' $HOMEDIR/.profile
sed -i.bak '/export SSHKEYNAME/d' $HOMEDIR/.bashrc
sed -i.bak '/jsenv.sh/d' $HOMEDIR/.bashrc
sed -i.bak '/jsenv.sh/d' $HOMEDIR/.bash_profile
sed -i.bak '/.*zlibs.sh/d' $HOMEDIR/.bashrc
sed -i.bak '/.*zlibs.sh/d' $HOMEDIR/.bash_profile
rm ~/js9host/cfg/me.toml > /dev/null 2>&1
rm ~/js9host/cfg/jumpscale9.toml > /dev/null 2>&1
sudo rm -rf $TMPDIR/zutils_done > /dev/null 2>&1
sudo rm -rf /tmp/zutils_done > /dev/null 2>&1

#check if branch given, if not set do development
export JS9BRANCH=${JS9BRANCH:-development}
# export JS9FULL=1 #if set will install in developer mode

export ZLogFile='/tmp/zutils.log'
echo "init" > $ZLogFile

if [ -e /opt/code ] && [ "$(uname)" != "Darwin" ] ; then
    export ZCODEDIR=${ZCODEDIR:-/opt/code}
else
    export ZCODEDIR=${ZCODEDIR:-~/code}
fi

if [ -z "$HOMEDIR" ] ; then
    export HOMEDIR="$HOME"
fi

if [ -z "$LC_ALL" ] ; then
    export LC_ALL="C.UTF-8"
fi

if [ -z "$HOMEDIR" ] || [ ! -d "$HOMEDIR" ]; then
    echo "[-] ERROR, could not find homedir $HOMEDIR"
    return 1
fi

cd /tmp

echo "INSTALL Jumpscale9 on branch $JS9BRANCH"

ZInstall_host_base || die "Could not prepare the base system" || exit 1
ZCodeGetJS || die "Could not download js9 code" || exit 1
ZInstall_host_js9 || die "Could not install core9 of js9" || exit 1


