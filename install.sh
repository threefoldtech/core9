#for development mode
mkdir -p /root/.ssh
ssh-keyscan github.com >> /root/.ssh/known_hosts
pip3 install -e .
