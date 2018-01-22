## Config Manager

JumpScale 9.3.0 introduces a secure configuration manager that makes sure that private configuration data is NACL encrypted on the filesystem.

### Getting started

to get started
 1. create a git repo under j.dirs.CODEDIR
 2. run `js9_config init`. This will mark this repo as your configuration repo
 3. Start creating your configuration instances

### Configuring

to configure a client from the cmdline
```
js9_config configure -l j.clients.openvcloud -i test -s /root/.ssh/id_rsa
```

where 
 - `-l` denotes the jslocation of the client to be configured
 - `-i` the instance name of this configuration
 - `-s` the ssh key used in encryption/decryption
 
 
 ### internals
** TODO
