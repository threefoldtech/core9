from jumpscale import j
import os

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
"""

FormBuilderBaseClass = j.tools.formbuilder.baseclass_get()

JSConfigBase = j.tools.configmanager.base_class_config


class MyConfig(JSConfigBase):
    """
    """

    def __init__(self, data={}):
        if not hasattr(self, '__jslocation__'):
            self.__jslocation__ = "j.tools.myconfig"
        JSConfigBase.__init__(self, instance="main", data=data, template=TEMPLATE, interactive=True)
