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

cd /tmp

echo "INSTALL BASHTOOLS"
curl https://raw.githubusercontent.com/Jumpscale/bash/master/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh

echo "load zlibs"
source ~/code/github/jumpscale/bash/zlibs.sh > /dev/null 2>&1 
source /opt/code/github/jumpscale/bash/zlibs.sh > /dev/null 2>&1 
ZDoneReset

rm ~/js9host/cfg/me.toml > /dev/null 2>&1
rm ~/js9host/cfg/jumpscale9.toml > /dev/null 2>&1

echo "install js9"
export JS9BRANCH="9.3.0"
ZInstall_host_js9 || die "Could not install core9 of js9" || exit 1

pip3 install Cython
pip3 install asyncssh
pip3 install numpy
pip3 install tarantool

