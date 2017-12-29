from js9 import j
# import os
# import copy


class JSBaseClassConfig():

    def __init__(self, instance="main", data={}, parent=None,template=None,ui=None):
        self._single_item = True
        s = self
        if parent is not None:
            s.__jslocation__ = parent.__jslocation__
        self.logger = j.logger.get(self.__jslocation__)        
        if ui==None:
            self.ui = j.tools.formbuilder.baseclass_get() #is the default class
        else:
            self.ui=ui
        if template==None:
            raise RuntimeError("template needs to be specified, needs to be yaml or dict")
        self._config = j.tools.configmanager._get_for_obj(self,instance=instance,data=data,template=template,ui=self.ui)

        if self._config.load()>0:
            self.interactive()
        elif self.config_check() not in [None,"",0]:
            self.interactive()



    def reset(self):
        self.config.instance_set(self.instance)

    @property
    def config(self):
        if self._config is None:
            raise RuntimeError("could not find config obj on secret base class, make sure has been properly initialized check MyConfig.py in core for example.")
        return self._config

    @config.setter
    def config(self, val):
        self.config.data = val

    @property
    def instance(self):
        return self.config.instance

    @property
    def config_template(self):
        return self.config.template

    def interactive(self):
        if j.tools.configmanager.interactive:
            print("Did not find config file:%s, will ask for initial configuration information."%self.config.location)
            self.config.instance=j.tools.console.askString("specify name for instance", defaultparam=self.config.instance)
            self.configure()
        else:
            raise RuntimeError("configuration not found for :%s, please run 'js9_config configure -l %s "%(self.__jslocation__,self.__jslocation__))
   
    def configure(self):
        """
        call the form build to represent this object
        """

        if self.ui is None:
            raise RuntimeError("cannot call configure UI because not defined yet, is None")
        myui = self.ui(name=self.config.path, config=self.config.data, template=self.config.template)

        while True:
            myui.run()
            self.config.data =  myui.config #config in the ui is a std dict
            msg=self.config_check()
            if msg!=None and msg!="":
                print(msg)
                j.tools.console.askString("please correct the information in next configuraton screen, press enter")
            else:
                break
        
        self.config.save()

        return self.config

    def config_check(self):
        return 0

    def __str__(self):
        out = "js9_object:"
        out += str(self.config)
        return out

    __repr__ = __str__
