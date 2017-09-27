#for development mode

echo "INSTALL BASHTOOLS"
curl https://raw.githubusercontent.com/Jumpscale/bash/master/install.sh?$RANDOM > /tmp/install.sh;bash /tmp/install.sh

ZInstall_host_js9

pip3 install Cython
pip3 install asyncssh
pip3 install numpy
pip3 install tarantool

