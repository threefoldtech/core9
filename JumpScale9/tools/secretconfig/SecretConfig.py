from js9 import j
import os

TEMPLATE = """
fullname = ""
email = ""
login_name = ""
ssh_key_name = ""
"""

FormBuilderBase = j.tools.formbuilder.baseclass_get()


class JSBaseClassSecret():

    def __init__(self):
        self.__jslocation__ = None
        self.instance = None
        self._TEMPLATE = TEMPLATE

    @property
    def _location(self):
        # make sure __jslocation__ always exists and raise if not
        # cause we can set a default value
        if not hasattr(self, '__jslocation__') or \
                self.__jslocation__ is None or self.__jslocation__ == '':
            raise RuntimeError("__jslocation__ attribute doesn't exist or is not set.")
        return self.__jslocation__

    @property
    def _instance(self):
        # make sure self.instance always exists and set a default value
        if not hasattr(self, 'instance') or self.instance is None or self.instance == '':
            self.instance = 'main'
        return self.instance

    @property
    def _configure_class(self):
        return j.tools.formbuilder.baseclass_get()

    @property
    def _configure_template(self):
        if not hasattr(self, '_TEMPLATE') or \
                self._TEMPLATE is None or self._TEMPLATE == '':
            raise RuntimeError("self._TEMPLATE attribute doesn't exist or is not set")
        return self._TEMPLATE

    @property
    def config(self):
        return j.tools.secretconfig.get(location=self._location, instance=self._instance)

    @config.setter
    def config(self, val):
        if j.data.types.dict.check(val) is False:
            raise TypeError("need to be dict")
        return j.tools.secretconfig.config_update(location=self._location, instance=self._instance, updatedict=val)


class MyConfig(FormBuilderBase):
    """
    This class let the user tune the form displayed during configuration.
    By default configure only show the inputs from the template,
    this class allow to enhance the form with custom inputs.
    """

    def __init__(self):
        super().__init__()
        # makes sure that this property is not auto populated, not needed when in form_add_items_pre
        self.auto_disable.append("ssh_key_name")

    def form_add_items_post(self):
        # SSHKEYS
        sshpath = "%s/.ssh" % (j.dirs.HOMEDIR)
        keynames = [j.sal.fs.getBaseName(item)[:-4] for item in j.sal.fs.listFilesInDir(sshpath, filter="*.pub")]
        if len(keynames) == 0:
            raise RuntimeError("No ssh key found in ssh-agent. Make sure ssh-agent is running and at least one key is loaded")
        self.widget_add_multichoice("ssh_key_name", keynames)


class SecretConfigFactory(JSBaseClassSecret):

    def __init__(self):
        super().__init__()
        self.__jslocation__ = "j.tools.secretconfig"
        self._path = ""
        self._TEMPLATE = TEMPLATE

    @property
    def _configure_class(self):
        return MyConfig

    @property
    def path_configrepo(self):
        if self._path == "":
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
    def base_class_secret(self):
        return JSBaseClassSecret

    def configure(self, location="myconfig", instance="main"):
        """
        Will display a npyscreen form to edit the configuration
        """
        if location == "myconfig":
            jsclient_object = self
        else:
            jsclient_object = eval(location)

        sc = SecretConfig(instance=instance, jsclient_object=jsclient_object)
        sc.configure()
        sc.save()
        return sc

    def config_update(self, location="myconfig", instance="main", updatedict={}):
        """
        update the configuration by giving a dictionnary. The configuration will
        be updated with the value of updatedict
        """
        if location == "myconfig":
            jsclient_object = self
        else:
            jsclient_object = eval(location)

        sc = SecretConfig(instance=instance, jsclient_object=jsclient_object)
        sc.data = updatedict
        sc.save()
        return sc

    def get(self, location="myconfig", instance="main"):
        """
        return a secret config
        """
        if location == "myconfig":
            jsclient_object = self
        else:
            jsclient_object = eval(location)

        sc = SecretConfig(instance=instance, jsclient_object=jsclient_object)
        return sc

    def set(self, location, instance, config=None):
        """
        create a new config

        @param location: location of the client
        @param instance: instance name
        @param config: optional configuration to set.
        @type config: dict
        """
        # create the config directory and file, so we don't trigger the form
        # when creating a SercretConfig object
        path = j.sal.fs.joinPaths(j.tools.secretconfig.path_configrepo, location, instance + '.toml')
        j.sal.fs.createDir(j.sal.fs.getParent(path))
        j.sal.fs.writeFile(path, "")

        jsclient_object = eval(location)

        sc = SecretConfig(instance=instance, jsclient_object=jsclient_object)
        if config is not None:
            sc.data = config
        sc.save()
        return sc

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

    def delete(self, location, instance):
        path = j.sal.fs.joinPaths(j.tools.secretconfig.path_configrepo, self.__jslocation__, instance + '.toml')
        if not j.sal.fs.exists(path):
            return

        j.sal.fs.remove(path)

    def init(self):
        curdir = j.sal.fs.getcwd()
        gitdir = "%s/.git" % curdir
        if not j.sal.fs.exists(gitdir) or not j.sal.fs.isDir(gitdir):
            raise RuntimeError("am not in root of git dir")
        self._path = curdir
        j.sal.fs.touch(".jsconfig")
        self.configure()


class SecretConfig():

    def __init__(self, instance="main", jsclient_object=None, location=None):
        """
        jsclient_object is e.g. j.clients.packet.net
        """
        if location is None:
            self.location = jsclient_object.__jslocation__
        else:
            self.location = location
        self.instance = instance
        self._template = {}
        self.jsclient_object = jsclient_object

        dirpath = j.tools.secretconfig.path_configrepo + "/%s" % self.location

        j.sal.fs.createDir(dirpath)

        self.path = j.sal.fs.joinPaths(dirpath, instance + '.toml')

        if not j.sal.fs.exists(self.path):
            self._data = {}
            self.configure()
            self.save()
        else:
            content = j.sal.fs.fileGetContents(self.path)
            config = j.data.serializer.toml.loads(content)
            # merge found config into template
            self._data, error = j.data.serializer.toml.merge(self.template, config, listunique=True)

    def configure(self):
        myconfig = self.jsclient_object._configure_class(name=self.path, config=self.data, template=self.template)
        myconfig.run()
        self.data = myconfig.config

    def save(self):
        # at this point we have the config & can write (self._data has the encrypted pieces)
        j.sal.fs.writeFile(self.path, j.data.serializer.toml.fancydumps(self._data))

    @property
    def template(self):
        if self._template == {}:
            self._template = j.data.serializer.toml.loads(self.jsclient_object._configure_template)
        return self._template

    @property
    def data(self):
        res = {}
        for key, item in self._data.items():
            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_") and ttype.BASETYPE == "string":
                # FIXME: this is buggy in the case the key ends with _ but is not a string, the value is lost
                if item != '':
                    res[key] = j.data.nacl.default.decryptSymmetric(item, hex=True).decode()
                else:
                    res[key] = ''
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
            if key.endswith("_") and ttype.BASETYPE == "string":
                # FIXME: this is buggy in the case the key ends with _ but is not a string, the value is lost
                if item != '':
                    item = j.data.nacl.default.encryptSymmetric(item, hex=True, salt=item)
            self._data[key] = item

    @property
    def yaml(self):
        return j.data.serializer.toml.fancydumps(self._data)

    def __str__(self):
        out = "config:%s:%s\n\n" % (self.location, self.instance)
        out += self.yaml
        out += "===========================\n"
        return out

    __repr__ = __str__
