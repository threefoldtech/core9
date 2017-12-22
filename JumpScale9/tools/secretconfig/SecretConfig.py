from js9 import j

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
ssh_key_name = ""
"""

BaseConfig=j.tools.formbuilder.baseclass_get()

class JSBaseClassSecret():

    @property
    def _configure_class(self):
        return j.tools.formbuilder.baseclass_get()

    @property
    def _configure_template(self):
        return self._TEMPLATE     

    @property
    def config(self):
        return j.tools.secretconfig.get(location=self.__jslocation__,instance=self.instance)

    @config.setter
    def config(self,val):
        if j.data.types.dict.check(val)==False:
            raise RuntimeError("need to be dict")
        return j.tools.secretconfig.configure(location=self.__jslocation__,instance=self.instance,updatedict=val,configure=False)
    
    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__)).rstrip("/")    

class MyConfig(BaseConfig):

    def init(self):
        self.auto_disable.append("ssh_key_name") #makes sure that this property is not auto populated, not needed when in form_add_items_pre

    def form_add_items_post(self):
        #SSHKEYS
        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        # keynames = [j.sal.fs.getBaseName(item) for item in j.clients.ssh.ssh_keys_list_from_agent()] #load all ssh keys loaded in mem
        keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        if len(keynames)==0:
            raise RuntimeError("load ssh-agent")
        self.widget_add_multichoice("ssh_key_name",keynames)



class SecretConfigFactory(JSBaseClassSecret):

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"
        self._path=""
        self._TEMPLATE = TEMPLATE

    @property
    def _configure_class(self):
        return MyConfig

    @property
    def path_configrepo(self):
        if self._path=="":
            res=j.clients.git.getGitReposListLocal()
            for key,path in res.items():
                checkpath="%s/.jsconfig"%path
                if key.startswith("config_"):
                    if j.sal.fs.exists(checkpath):
                        self._path=path
                        return self._path
            raise RuntimeError("Cannot find path for configuration repo, please checkout right git repo & run 'js9_secret init' in that repo ")
        return self._path

    @property
    def base_class_secret(self):
        return JSBaseClassSecret

    def configure(self, location="myconfig", instance="main"):
        """
        call the configurator, which will allow arguments to be filled in
        """
        if location=="myconfig":
            jsclient_object=self
        else:
            jsclient_object=eval(location)

        sc=SecretConfig(instance=instance,jsclient_object=jsclient_object)
        sc.configure()
        sc.save()
        return sc

    def config_update(self, location="myconfig", instance="main",updatedict={}):
        """
        call the configurator, which will allow arguments to be filled in
        """
        if location=="myconfig":
            jsclient_object=self
        else:
            jsclient_object=eval(location)

        sc=SecretConfig(instance=instance,jsclient_object=jsclient_object)
        sc.data = updatedict
        sc.save()
        return sc

    def get(self, location="myconfig", instance="main"):
        """
        """
        if location=="myconfig":
            jsclient_object=self
        else:
            jsclient_object=eval(location)

        sc=SecretConfig(instance=instance,jsclient_object=jsclient_object)
        return sc    

    def init(self):
        curdir=j.sal.fs.getcwd()
        gitdir="%s/.git"%curdir
        if not j.sal.fs.exists(gitdir):
            raise RuntimeError("am not in root of git dir")
        self.path=curdir
        j.sal.fs.touch(".jsconfig")
        self.configure()

        

class SecretConfig():

    def __init__(self,instance="main",jsclient_object=None,location=None):
        """
        jsclient_object is e.g. j.clients.packet.net
        """
        if location==None:
            self.location = jsclient_object.__jslocation__ 
        else:
            self.location = location
        self.instance=instance
        # self._category = ""
        self._template = {}
        self.jsclient_object = jsclient_object

        dirpath = j.tools.secretconfig.path_configrepo+"/%s"%self.location

        j.sal.fs.createDir(dirpath)
        
        self.path="%s/%s.toml"%(dirpath,instance)
            
        if not j.sal.fs.exists(self.path):
            self._data={}
            self.configure()
            self.save()
        else:
            content=j.sal.fs.fileGetContents(self.path)
            config=j.data.serializer.toml.loads(content)
            #merge found config into template
            self._data,error=j.data.serializer.toml.merge(self.template,config,listunique=True)
        
    def configure(self):
        myconfig=self.jsclient_object._configure_class(name=self.path, config=self.data,template=self.template)
        myconfig.run()
        self.data=myconfig.config

    def save(self):
        #at this point we have the config & can write (self._data has the encrypted pieces)
        j.sal.fs.writeFile(self.path,j.data.serializer.toml.fancydumps(self._data))


    # @property
    # def category(self):
    #     if self._category=="":
    #         location=self.location.strip(".")        
    #         if location.startswith("j."):
    #             category = location[2:]
    #         else:
    #             category = location
    #         category = category.replace(".","_")
    #         self._category = category.lower().strip()
    #     return self._category

    @property
    def template(self):
        if self._template=={}:            
            self._template=j.data.serializer.toml.loads(self.jsclient_object._configure_template)
        return self._template

    @property
    def data(self):
        res={}
        for key,item in self._data.items():            
            if key.endswith("_"):
                ttype= j.data.types.type_detect(self.template[key])
                if ttype.BASETYPE == "string":
                    res[key]=j.data.nacl.default.decryptSymmetric(item,hex=True).decode()
            else:
                res[key]=item                
        return res

    @property
    def yaml(self):    
        return j.data.serializer.toml.fancydumps(self._data)

    @data.setter
    def data(self,val):
        if j.data.types.dict.check(val)==False:
            raise RuntimeError("need to be dict")
        for key,item in val.items():
            if key not in self.template:
                raise RuntimeError("Cannot find key:%s in template for %s"%(key,self))
            ttype= j.data.types.type_detect(self.template[key])
            if key.endswith("_") and ttype.BASETYPE == "string":
                item = j.data.nacl.default.encryptSymmetric(item,hex=True,salt=item)
            self._data[key] = item
                    
    def __str__(self):
        out = "config:%s:%s\n\n"%(self.location, self.instance)    
        out += self.yaml
        out += "===========================\n"
        return out

    __repr__=__str__


