from js9 import j

from .Node import Node




JSConfigBase = j.tools.configmanager.base_class_configs
class Nodes(JSConfigBase):
    def __init__(self):
        self.__jslocation__ = "j.tools.nodemgr"    
        JSConfigBase.__init__(self)
        self._CHILDCLASS=Node
        self._tree=None


    # @property
    # def tree(self):
    #     if self._tree==None:
    #         self._tree = j.data.treemanager.get()
    #     return self._tree


