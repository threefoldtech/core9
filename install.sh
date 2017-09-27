#for development mode

cd /tmp

echo "INSTALL BASHTOOLS"
curl https://raw.githubusercontent.com/Jumpscale/bash/master/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh

echo "load zlibs"
source ~/code/github/jumpscale/bash/zlibs.sh 2>&1 > /dev/null
source /opt/code/github/jumpscale/bash/zlibs.sh 2>&1 > /dev/null

echo "install js9"
ZInstall_host_js9 || die "Could not install core9 of js9" || return 1

pip3 install Cython
pip3 install asyncssh
pip3 install numpy
pip3 install tarantool

