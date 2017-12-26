
# how to create a configuration object


## How to enable a jumpscale module to have a secret config management

- Make you module inherits from the secret config base class, available at `j.tools.configmanager.base_class_config`.
- Make sure to call the constructor of the base class. (`super().__ini__()`)
- Define the template of your configuration. This template is a multi string representing a dictionary.  
You need to specified a default value for each key. The type of the value will be automatically deducted. The type per key will be remember and checked when updating the config. If you tried to set a value with a wrong type, an exception will be raised.  
If the key last end with an '_' then the value will always be encrypted.

- set the TEMPLATE attribute to the template you've defined

- before accessing the `self.config` attribute, set `self.instance`.

Example code:

```python


CONFIG_TEMPLATE = """
host = ""
port = 0
secret_ = ""
"""

JSConfigBase = j.tools.configmanager.base_class_config

class MyModuleFactory(JSConfigBase):

    def __init__(self):
        # you need to call the constructor
        # of the base class to boostrap the config
        super().__init__()
        # define the jslocation like any other js module
        self.__jslocation__ = "j.client.mymodule"
        # set self.TEMPLATE to your defined TEMPLATE
        # self.TEMPLATE is given by JSConfigBase
        self._TEMPLATE = CONFIG_TEMPLATE
    
    def get(self, instance='main'):
        """
        get an instance of your module
        """
        # self.instance is give by JSConfigBase
        # you need to set it for self.config to return the proper values
        self.instance = instance
        host = self.config.data['host']
        port = self.config.data['port']
        # the secret will get decrypted on the fly
        secret = self.config.data['secret']
        # create an instance
        i = Instance(host, port, secret)
        return i
    
```
