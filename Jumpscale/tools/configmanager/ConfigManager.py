from jumpscale import j

import sys
import os
import copy
from .JSBaseClassConfig import JSBaseClassConfig
from .JSBaseClassConfigs import JSBaseClassConfigs

from .FileConfigManager import FileConfigManager
from .DbConfigManager import DbConfigManager


installmessage = """

**ERROR**: there is no config directory created

create a git repository on github or any other git system.
checkout this repository by doing

'js_code get --url='...your ssh git url ...'

the go to this directory (to to that path & do)

js_config init


"""

JSBASE = j.application.jsbase_get_class()


class ConfigFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.tools.configmanager"
        JSBASE.__init__(self)
    
        configbackend = j.core.state.configGetFromDict("myconfig", "backend", None) # file is the default
        if configbackend is None:
            j.core.state.configSetInDict("myconfig", "backend", "file")
            configbackend = "file"

        self._impl = None
        if configbackend == "file":
            self._impl = FileConfigManager()
        elif configbackend == "db":
            self._impl = DbConfigManager()

    def __dir__(self):
        return dir(self) + dir(self.impl)

    def __getattr__(self, attr):
        return getattr(self._impl, attr)

    