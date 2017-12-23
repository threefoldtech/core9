from js9 import j
import os
import copy

class JSBaseClassSecretConfig():

    def __init__(self):
        self._config = None
        self._single_item = True

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

class JSBaseClassSecretConfigs():
    """
    collection class to deal with multiple instances
    """

    def __init__(self):
        self.items = {}
        self._single_item = False

    def get(self,instance="main",data={}):
        if not instance in self.items:
            config=j.tools.secretconfig.get(factoryclassobj=self, instance=instance,data={})
            self.items[instance]=self._CHILDCLASS(config=config)
            self.items[instance]._TEMPLATE=self._TEMPLATE
            self.items[instance]._instance=instance
            self.items[instance]._FORMBUILDER_UI=self._FORMBUILDER_UI
        return self.items[instance]

    def delete(self,instance):
        raise RuntimeError("#TODO:*1 implement")

    def list(self):
        return j.tools.secretconfig.list(location=self.__jslocation__)

    def getall(self):
        res=[]
        for name in  j.tools.secretconfig.list(location=self.__jslocation__):
            res.append(self.config_get(name))
        return res

class SecretConfig():

    def __init__(self, instance="main",location=None,template={},ui=None,data={}):
        """
        jsclient_object is e.g. j.clients.packet.net
        """
        self.location = location
        self.instance = instance
        self._template = template
        self._data = data
        self.ui = ui
        if self.instance==None:
            raise RuntimeError("cannot be None")
        self.load()

    def instance_set(self,instance):
        """
        will change instance name & delete data
        """
        self.instance=instance
        self._data={}

        self.load()

    def load(self):

        dirpath = j.tools.secretconfig.path_configrepo + "/%s" % self.location

        j.sal.fs.createDir(dirpath)

        self.path = j.sal.fs.joinPaths(dirpath, self.instance + '.toml')

        if not j.sal.fs.exists(self.path):
            self._data, error = j.data.serializer.toml.merge(tomlsource=self.template, tomlupdate=self._data, listunique=True)
            self.save()
        else:
            content = j.sal.fs.fileGetContents(self.path)
            data = j.data.serializer.toml.loads(content)
            # merge found data into template
            self._data, error = j.data.serializer.toml.merge(tomlsource=self.template, tomlupdate=data, listunique=True)

    def configure(self):
        if self.ui==None:
            raise RuntimeError("cannot call configure UI because not defined yet, is None")
        myconfig = self.ui(name=self.path, config=self.data, template=self.template)
        myconfig.run()
        self.data = myconfig.config
        self.save()

    def save(self):
        # at this point we have the config & can write (self._data has the encrypted pieces)
        j.sal.fs.writeFile(self.path, j.data.serializer.toml.fancydumps(self._data))

    @property
    def template(self):
        if self._template is None or self._template == '':
            raise RuntimeError("self._template has to be set")
        if j.data.types.string.check(self._template):
            self._template=j.data.serializer.toml.loads(self._template)
        return self._template

    @property
    def data(self):
        res = {}
        if self._data=={}:
            self.load()
        for key, item in self._data.items():
            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_"):
                if ttype.BASETYPE == "string":
                    if item != '':
                        res[key] = j.data.nacl.default.decryptSymmetric(item, hex=True).decode()
                    else:
                        res[key] = ''
                else:
                    res[key] = item
            else:
                res[key] = item
        return res

    @data.setter
    def data(self, value):
        if j.data.types.dict.check(value) is False:
            raise TypeError("value needs to be dict")

        for key, item in value.items():
            if key not in self.template:
                raise RuntimeError("Cannot find key:%s in template for %s" % (key, self))

            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_"):
                if ttype.BASETYPE == "string":
                    if item != '':
                        item = j.data.nacl.default.encryptSymmetric(item, hex=True, salt=item)
                    
            self._data[key] = item

    @property
    def yaml(self):
        return j.data.serializer.toml.fancydumps(self._data)

    def __str__(self):
        out = "config:%s:%s\n\n" % (self.location, self.instance)
        out += j.data.text.indent(self.yaml)
        return out

    __repr__ = __str__

class SecretConfigFactory():

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"
        self._path = ""
        self._cache={}   

    def reset(self):
        self._cache={}             

    @property
    def path_configrepo(self):        
        if self._path == "":

            #first check if there is no .jsconfig in parent dirs
            curdir= j.sal.fs.getcwd()
            while curdir.strip()=="" or not j.sal.fs.exists("%s/.jsconfig"%curdir):
                #look for parent
                curdir=j.sal.fs.getParent(curdir)
            if curdir.strip()!="":
                #means we found dir
                self._path=curdir
                return self._path

            res = j.clients.git.getGitReposListLocal()
            for key, path in res.items():
                checkpath = "%s/.jsconfig" % path
                if key.startswith("config_"):
                    if j.sal.fs.exists(checkpath):
                        self._path = path
                        return self._path
            raise RuntimeError("Cannot find path for configuration repo, please checkout right git repo & run 'js9_secret init' in that repo ")
        return self._path

    @property
    def base_class_secret_config(self):
        return JSBaseClassSecretConfig

    @property
    def base_class_secret_configs(self):
        return JSBaseClassSecretConfigs

    def configure(self, location="", instance="main"):
        """
        Will display a npyscreen form to edit the configuration
        """
        sc = self.get_for_location(location=location,instance=instance)
        sc.configure()
        sc.save()
        return sc

    def update(self, location, instance="main", updatedict={}):
        """
        update the configuration by giving a dictionnary. The configuration will
        be updated with the value of updatedict
        """
        sc = self.get(location=location,instance=instance)
        sc.data = updatedict
        sc.save()
        return sc

    def _get_for_obj(self, factoryclassobj,template,ui=None, instance="main",data={}):
        """
        return a secret config
        """
        if not hasattr(factoryclassobj, '__jslocation__') or factoryclassobj.__jslocation__ is None or factoryclassobj.__jslocation__ is "":
            raise RuntimeError("__jslocation__ has not been set on class %s"%self.__class__)
        location=factoryclassobj.__jslocation__        
        key="%s_%s"%(location,instance)

        if ui==None:
            ui=j.tools.formbuilder.baseclass_get()

        if key not in self._cache:            
            sc = SecretConfig(instance=instance, location=location, template=template ,ui=ui,data=data)
            self._cache[key]=sc

        return self._cache[key]

    def get_for_location(self,location="",instance="main",data={}):
        if location=="" or  location==None:
            if j.sal.fs.getcwd().startswith(self.path_configrepo):
                #means we are in subdir of current config  repo, so we can be in location
                location = j.sal.fs.getBaseName(j.sal.fs.getcwd())
                if not location.startswith("j."):
                    raise RuntimeError("Cannot find location, are you in right directory? now in:%s"%j.sal.fs.getcwd())

        obj = eval(location)
        if obj._single_item:
            return obj.config
        else:
            print("multiple objects")
            from IPython import embed;embed(colors='Linux')


    def get(self, location, template={},instance="main", data = {},ui=None):
        """
        return a secret config
        """
        if location=="":
            raise RuntimeError("location cannot be empty")
        if instance=="" or instance==None:
            raise RuntimeError("instance cannot be empty")            
        key="%s_%s"%(location,instance)
        if key not in self._cache:
            sc = SecretConfig(instance=instance, location=location, template=template ,ui=ui,data=data)
            self._cache[key]=sc
        return self._cache[key]    

    #should use config_update
    # def set(self, location, instance, config=None):
    #     """
    #     create a new config

    #     @param location: location of the client
    #     @param instance: instance name
    #     @param config: optional configuration to set.
    #     @type config: dict
    #     """
    #     # create the config directory and file, so we don't trigger the form
    #     # when creating a SercretConfig object
    #     path = j.sal.fs.joinPaths(j.tools.secretconfig.path_configrepo, location, instance + '.toml')
    #     j.sal.fs.createDir(j.sal.fs.getParent(path))
    #     j.sal.fs.writeFile(path, "")

    #     jsclient_object = eval(location)

    #     sc = SecretConfig(instance=instance, jsclient_object=jsclient_object)
    #     if config is not None:
    #         sc.data = config
    #     sc.save()
    #     return sc

    def list(self, location):
        """
        list all the existing instance name for a location

        @return: list of instance name
        """
        instances = []

        root = j.sal.fs.joinPaths(self.path_configrepo, location)
        if not j.sal.fs.exists(root):
            return instances

        jsclient_object = eval(location)

        for cfg_path in j.sal.fs.listFilesInDir(root):
            cfg_name = j.sal.fs.getBaseName(cfg_path)
            if cfg_name in ('.git', '.jsconfig'):
                continue
            # trim the extension
            instance_name = cfg_name.split(os.path.extsep)[0]
            instances.append(instance_name)
        return instances

    def delete(self, location, instance="*"):
        if instance != "*":
            path = j.sal.fs.joinPaths(j.tools.secretconfig.path_configrepo, location, instance + '.toml')
            j.sal.fs.remove(path)
        else:
            path = j.sal.fs.joinPaths(j.tools.secretconfig.path_configrepo, location)
            for item in j.sal.fs.listFilesInDir(path):
                j.sal.fs.remove(item)

    def init(self,path="",data={}):
        if path=="":
            path = j.sal.fs.getcwd()

        #first check if there is no .jsconfig in parent dirs
        curdir= copy.copy(path)
        while curdir.strip()=="" or not j.sal.fs.exists("%s/.jsconfig"%curdir):
            #look for parent
            curdir=j.sal.fs.getParent(curdir)
        if curdir.strip()!="":
            return curdir

        gitdir = "%s/.git" % path
        if not j.sal.fs.exists(gitdir) or not j.sal.fs.isDir(gitdir):
            raise RuntimeError("am not in root of git dir")
        self._path = path
        if data == None:
            j.tools.myconfig.configure()
        else:
            j.tools.myconfig.config.data=data
            j.tools.myconfig.config.save()
        j.sal.fs.touch(".jsconfig")

        return path

    def test(self):

        tdir = "/tmp/tests/secretconfig"
        j.sal.fs.createDir(tdir)
        j.sal.process.execute("cd %s && git init"%tdir)
        
        # self._test_myconfig_singleitem()
        self._test_myconfig_multiitem()


    def _test_myconfig_singleitem(self):

        tdir = "/tmp/tests/secretconfig"

        MYCONFIG = """
        fullname = "kristof@something"
        email = "kkk@kk.com"
        login_name = "dddd"
        ssh_key_name = "something"
        """
        data=j.data.serializer.toml.loads(MYCONFIG)

        self.init(path=tdir,data=data)

        j.tools.myconfig.config.data=data
        j.tools.myconfig.config.save()
        

        tdir = "/tmp/tests/secretconfig/j.tools.myconfig"
        assert len(j.sal.fs.listFilesInDir(tdir))==1 #there should be 1 file

        #check that the saved data is ok
        assert j.data.serializer.toml.fancydumps(j.tools.myconfig.config.data) == j.data.serializer.toml.fancydumps(data)

        self.delete("j.tools.myconfig") #should remove all        
        assert len(j.sal.fs.listFilesInDir(tdir))==0

        j.tools.secretconfig.reset()
        j.tools.myconfig.reset() #will remove data from mem
        assert j.tools.myconfig.config._data=={'email': '', 'fullname': '', 'login_name': '', 'ssh_key_name': ''}
        assert j.tools.myconfig.config.data=={'email': '', 'fullname': '', 'login_name': '', 'ssh_key_name': ''}

        j.tools.myconfig.config.load()
        assert j.tools.myconfig.config.data=={'email': '', 'fullname': '', 'login_name': '', 'ssh_key_name': ''}
        j.tools.myconfig.config.data=data
        j.tools.myconfig.config.save()
        assert len(j.sal.fs.listFilesInDir(tdir))==1

        #clean the env
        j.tools.secretconfig.reset()
        j.tools.myconfig.reset()
        j.tools.myconfig.config._data={}
        assert j.data.serializer.toml.fancydumps(j.tools.myconfig.config.data) == j.data.serializer.toml.fancydumps(data)

        #clean the env
        j.tools.secretconfig.reset()
        j.tools.myconfig.config.load()
        j.tools.myconfig.config.data={"email":"someting@ree.com"}
        j.tools.myconfig.config.save()
        j.tools.secretconfig.reset()

        assert j.tools.myconfig.config.data["email"]=="someting@ree.com"

        #delete
        self.delete("j.tools.myconfig","main")
        assert len(j.sal.fs.listFilesInDir(tdir))==0

    def _test_myconfig_multiitem(self):
        j.tools.nodemgr
        from IPython import embed;embed(colors='Linux')