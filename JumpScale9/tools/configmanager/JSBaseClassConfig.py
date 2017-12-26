from js9 import j
# import os
# import copy

class JSBaseClassConfig():

    def __init__(self,instance="main",data={},parent=None):
        self._single_item = True
        self._config=None
        X=self.__jslocation__
        if parent!=None:
            X=parent.__jslocation__
        #self._config = j.tools.configmanager._get_for_obj(self,instance=instance,data=data,template=TEMPLATE,ui=MyConfigUI)


    def reload(self):
        self._config.load()

    def reset(self):
        self._config.instance_set(self.instance)

    @property
    def config(self):
        if self._config==None:
            raise RuntimeError("could not find config obj on secret base class, make sure has been properly initialized check MyConfig.py in core for example.")
        return self._config

    @config.setter
    def config(self,val):
        self._config=val

    @property
    def instance(self):
        return self.config.instance

    @property
    def config_template(self):
        return self.config.template

    def configure(self):
        """
        call the form build to represent this object
        """
        return self.config.configure()

    def __str__(self):
        out = "js9_object:"
        out += str(self.config)
        return out

    __repr__ = __str__
