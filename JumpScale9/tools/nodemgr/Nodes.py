from js9 import j

from .Node import Node


TEMPLATE = """
addr = ""
port = 22
clienttype = ""
active = false
selected = false
category = ""
description = ""
secretconfig_ = ""
"""

FormBuilderBaseClass=j.tools.formbuilder.baseclass_get()
SecretConfigBase = j.tools.secretconfig.base_class_secret_config

class MyConfigUI(FormBuilderBaseClass):

    def init(self):
        self.auto_disable.append("clienttype")  # makes sure that this property is not auto populated, not needed when in form_add_items_pre
        self.auto_disable.append("enabled")
        self.auto_disable.append("selected")

    def form_add_items_post(self):
        self.widget_add_multichoice("clienttype", ["ovh","packetnet","ovc","physical","docker","container","zos"])
        self.widget_add_boolean("enabled",default=False)
        self.widget_add_boolean("selected",default=True)


SecretConfigBase = j.tools.secretconfig.base_class_secret_configs
class Nodes(SecretConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.tools.nodemgr"    
        SecretConfigBase.__init__(self)  
        self._CHILDCLASS = Node
        self._tree=None
        self._config = j.tools.secretconfig._get_for_obj(self,instance="main",data={},template=TEMPLATE,ui=MyConfigUI)
        print("INIT NODES, SHOULD NOT HAPPEN OFTEN")


    # @property
    # def tree(self):
    #     if self._tree==None:
    #         self._tree = j.data.treemanager.get()
    #     return self._tree


