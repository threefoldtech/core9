from js9 import j
# import os
# import copy


class JSBaseClassConfigs():
    """
    collection class to deal with multiple instances
    """

    def __init__(self):
        self.items = {}
        self._single_item = False
        self._CHILDCLASS = None

    def get(self,instance="main",data={}):
        if self._CHILDCLASS == None:
            raise RuntimeError("self_CHILDCLASS was not populated on factory class")

        if not instance in self.items:
            # config=j.tools.configmanager._get_for_obj(factoryclassobj=self, template=,ui=,instance=instance,data={})
            self.items[instance]=self._CHILDCLASS(instance=instance,data=data,parent=self)            

        return self.items[instance]


    def reset(self):
        j.tools.configmanager.delete(location=self.__jslocation__, instance="*")

    def list(self):
        return j.tools.configmanager.list(location=self.__jslocation__)

    def getall(self):
        res=[]
        for name in  j.tools.configmanager.list(location=self.__jslocation__):
            res.append(self.config_get(name))
        return res

