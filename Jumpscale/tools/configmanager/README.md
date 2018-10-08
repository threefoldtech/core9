# ConfigManager
Configuration management tool to manage secrets securely and cleanly manage deployments with credentials.






## how to create a configuration object


### How to enable a jumpscale module to have a secret config management
#### Setup the factory
- Make you factory module inherits from the config manager base class, available at `j.tools.configmanager.base_class_configs`.
- set the `__jslocation__` on your factory class
- Call the constructor of the base class with as first argument, the Class of object that the factory produces (`super().__init__(MyModule)`)

#### Setup the client class
- Define the template of your configuration. This template is a multi string representing a dictionary.  
You need to specified a default value for each key. The type of the value will be automatically deducted. The type per key will be remember and checked when updating the config. If you tried to set a value with a wrong type, an exception will be raised.  
If the key last end with an '_' then the value will always be encrypted.

- Make your child class inherits from the config manager base class, available at `j.tools.configmanager.base_class_config`
- Make your child class accept `instance, data={}, parent=None` as argument for its constructor
- call the constructor of the base class like this : `super().__init__(instance=instance, data=data, parent=parent,template=CONFIG_TEMPLATE)`


Example code:

```python
CONFIG_TEMPLATE = """
host = ""
port = 0
secret_ = ""
"""

JSConfigFactoryBase = j.tools.configmanager.base_class_configs
JSConfigClientBase = j.tools.configmanager.base_class_config

class MyModuleFactory(JSConfigFactoryBase):

    def __init__(self):
        # define the jslocation like any other js module
        self.__jslocation__ = "j.client.mymodule"
        
        # you need to call the constructor
        # of the base class to boostrap the config
        # by passing the Class this factory will instantiate
        super().__init__(MyModule)
    

class MyModule(JSConfigClientBase):

    def __init__(self, instance, data={}, parent=None):
        # configure the base class with the 
        # the instance name, the data of the config, 
        # the parent which is the factory class
        # and the template config
        super().__init__(instance=instance, data=data, parent=parent,template=CONFIG_TEMPLATE)
    
```



## Backends

### Filebackend

- sandbox: self contained configuration repository contains keys and the encoded configurations in `secureconfig` directory
- system-wide can be configured using `js_config`


### ZdbBackend
Uses 0-db backend to store the data 

#### representation on the filesystem
```
~> tree ~/configmgrsandboxes

/home/ahmed/configmgrsandboxes
├── robot1
│   ├── key.priv
│   ├── keys
│   │   ├── key.priv
│   │   └── key.pub
│   ├── key.seed
│   └── secureconfig
└── robot2
    ├── key.priv
    ├── keys
    │   ├── key.priv
    │   └── key.pub
    ├── key.seed
    └── secureconfig
```

- `keys` directory contains the private/pub key you configured for that namespace
- `seed` seed file
- `key.priv` the private encoded key

#### jumpscale.toml configuration

In myconfig section in `~/jumpscale/cfg/jumpscale.toml`
```
[myconfig]
..
backend = "db"
backend_addr = "localhost:9900"
adminsecret = ""
secrets = ""
```
- set the backend type to `db` to use 0-db backend (it's `file` by default.)
- You set the backend url (e.g localhost:9000)
- secrets/adminsecrets from 0-db terminology
- while using the 0-db backend you must call `j.tools.configmanager.set_namespace` first



## Examples

### ZDB Backend

```python
from jumpscale import j

j.tools.configmanager.set_namespace("robot1")
j.tools.configmanager.configure_keys_from_paths("/home/ahmed/.ssh/key1", "/home/ahmed/.ssh/key1.pub", None)
zcl = j.clients.zos_protocol.get("r1", data={'host':'127.0.2.5', 'port':5005, 'password_':'dmdm1'})
print(zcl.config.data)
```
1- in this example we set the working namespace to store the data to `robot1` (if you don't u will get runtime error `RuntimeError: configmanager isn't configured for a namespace you need to set the namespace using j.tools.configmanager.set_namespace`)
2- and configure the keys telling configmanager which keys we want to use using `configure_keys_from_paths` and pass the private key and the public key paths.
3- get a new instance of `zos_protocol` client using `j.clients.zos_protocol.get` and pass the secret data.

 

```python

j.tools.configmanager.set_namespace("robot2")
j.tools.configmanager.configure_keys_from_paths("/home/ahmed/.ssh/key2", "/home/ahmed/.ssh/key2.pub", None)

zcl = j.clients.zos_protocol.get("r2", data={'host': '192.0.2.10', 'port': 6000, 'password_': 'dmdm3'})
print(zcl.config.data)

```
Here we do the same using another namespace

```python

j.tools.configmanager.set_namespace("robot1")
zcl = j.clients.zos_protocol.get("r1")
print(zcl.config.data)

j.tools.configmanager.set_namespace("robot2")
zcl = j.clients.zos_protocol.get("r2")
print(zcl.config.data)

```
Here we show how to retreive the data from clients where data is isolated by zdb namespaces. 


