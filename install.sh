#for development mode
mkdir -p /root/.ssh
ssh-keyscan github.com >> /root/.ssh/known_hosts
apt-get install build-essential python3-dev libssl-dev -y
pip3 install -e .
