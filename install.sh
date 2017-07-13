#for development mode

# 'Cython>=0.25.2',
# 'asyncssh>=1.9.0',
# 'numpy>=1.12.1',
# 'tarantool>=0.5.4',
#TODO: *1 force right min versions

pip3 install Cython
pip3 install asyncssh
pip3 install numpy
pip3 install tarantool

mkdir -p /root/.ssh
ssh-keyscan github.com >> /root/.ssh/known_hosts
apt-get install build-essential python3-dev libssl-dev -y
pip3 install -e .
