from js9 import j

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
ssh_key_name = ""
"""

BaseConfig=j.tools.formbuilder.baseclass_get()

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
        self.widget_add_singlechoice("ssh_key_name",keynames)



class SecretConfigFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"
        self.path=""


    def configrepo_find(self):
        if self.path=="":
            res=j.clients.git.getGitReposListLocal()
            for key,path in res.items():
                checkpath="%s/.jsconfig"%path
                if key.startswith("config_"):
                    if j.sal.fs.exists(checkpath):
                        self.path=path
                        return self.path
            raise RuntimeError("Cannot find path for configuration repo, please checkout right git repo & run 'js9_secret init' in that repo ")
        return self.path

    @property
    def _configure_class(self):
        return MyConfig

    @property
    def _configure_template(self):
        return TEMPLATE

    def _js_location_get(self,location):
        return eval(location)

    def configure(self, location="myconfig", instance="main",configure=False,updatedict={},write=True):
        self.configrepo_find()
        if location.startswith("j."):
            category=location[2:]
        else:
            category=location
        category=category.replace(".","_")
        category=category.lower().strip()
        cdir=self.path+"/%s"%category
        j.sal.fs.createDir(cdir)
        cfile="%s/%s.toml"%(cdir,instance)
        location=location.strip(".")
        if category=="myconfig":
            location="self"

        l=self._js_location_get(location)

        if not j.sal.fs.exists(cfile):
            config = {}
            configure=True
            write=True
        else:
            content=j.sal.fs.fileGetContents(cfile)
            config=j.data.serializer.toml.loads(content,secure=True)
        
        #merge found config into template
        config,error=j.data.serializer.toml.merge(l._configure_template,config,listunique=True)
        if updatedict!={}:
            config,error=j.data.serializer.toml.merge(config,updatedict,listunique=True)
        
        if configure:
            myconfig=l._configure_class(name=cfile, config=config,template=l._configure_template)
            myconfig.run()
            config=myconfig.config

        if write:
            #at this point we have the config & can write
            j.sal.fs.writeFile(cfile,j.data.serializer.toml.fancydumps(config,secure=True))

        return config

    def init(self):
        curdir=j.sal.fs.getcwd()
        gitdir="%s/.git"%curdir
        if not j.sal.fs.exists(gitdir):
            raise RuntimeError("am not in root of git dir")
        self.path=curdir
        j.sal.fs.touch(".jsconfig")
        self.run(configure=True)

    def get(self,location,instance="main"):
        config = self.configure(location=location, instance=instance,configure=False,updatedict={},write=False)

        configtoml=j.data.serializer.toml.fancydumps(config,secure=True)
        configtoml2=j.data.serializer.toml.loads(configtoml,secure=True)

        return configtoml2


        



