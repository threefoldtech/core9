from .IConfigManager import IConfigManager

from jumpscale import j
import os
import copy
from .JSBaseClassConfig import JSBaseClassConfig
from .JSBaseClassConfigs import JSBaseClassConfigs
from .FileConfig import FileConfig
import sys


installmessage = """

**ERROR**: there is no config directory created

create a git repository on github or any other git system.
checkout this repository by doing

'js_code get --url='...your ssh git url ...'

the go to this directory (to to that path & do)

js_config init


"""


class FileConfigManager(IConfigManager):

    def __init__(self):
        IConfigManager.__init__(self)
        self._path = ""
        self.interactive = True  # std needs to be on True
        self.sandbox = False
        self._keyname = ""  # if set will overrule from the main js config file
        self._init = False

    def reset(self, location=None, instance=None, force=False):
        """
        Reset configurations

        @param force: If no location is given and force is set to true then all locations will be reset
        """

        path = self._path
        if location:
            path = j.sal.fs.joinPaths(path, location)
        if instance:
            path = j.sal.fs.joinPaths(path, '%s.toml' % instance)
        if not location:
            if force or j.tools.console.askYesNo("No location specified, Are you sure you want to delete all configs?", default=True):
                configs = j.sal.fs.listDirsInDir(path) if path else []
                for config in configs:
                    if not j.sal.fs.getBaseName(config).startswith('.'):
                        j.sal.fs.removeDirTree(config)
        else:
            j.sal.fs.remove(path)

    @property
    def path(self):
        if not self._path:
            self._path = j.core.state.configGetFromDict("myconfig", "path")
            if not self._path:
                self.init()
        return self._path

    @property
    def keyname(self):
        if not self._keyname:
            self._keyname = j.core.state.configGetFromDict("myconfig", "sshkeyname")
        return self._keyname

    @property
    def keypath(self):
        return j.sal.fs.joinPaths(j.dirs.HOMEDIR, ".ssh", self.keyname)

    def _findConfigRepo(self, die=False):
        """
        if path is not set, it will look under CODEDIRS for any pre-configured js_config repo
        if there are more than one, will try to use one in root of cwd. If not in one, will raise a RuntimeError

        return configpath,remoteGitUrl
        """
        # self.sandbox_check()
        path = j.sal.fs.getParentWithDirname(dirname=".jsconfig", die=die)
        if path != None:
            return path, None
        paths = []
        for key, path in j.clients.git.getGitReposListLocal().items():
            if j.sal.fs.exists(j.sal.fs.joinPaths(path, ".jsconfig")):
                paths.append(path)
        if len(paths) == 0:
            if die:
                raise RuntimeError("could not find config paths")
            else:
                return None, None
        if len(paths) > 1:
            if die:
                raise RuntimeError(
                    "multipule configuration repos were found in {} but not currently in root of one".format(paths))
            else:
                return None, None
        cpath = paths[0]
        g = j.clients.git.get(cpath)
        self.logger.info("found jsconfig dir in: %s" % cpath)
        self.logger.info("remote url: %s" % g.remoteUrl)

        return cpath, g.remoteUrl

    @property
    def base_class_config(self):
        return JSBaseClassConfig

    @property
    def base_class_configs(self):
        return JSBaseClassConfigs

    def _get_for_obj(self, jsobj, template, ui=None, instance="main", data={}):
        """
        return a secret config
        """
        self.sandbox_check()
        if not hasattr(jsobj, '__jslocation__') or jsobj.__jslocation__ is None or jsobj.__jslocation__ is "":
            raise RuntimeError("__jslocation__ has not been set on class %s" % jsobj.__class__)
        location = jsobj.__jslocation__
        key = "%s_%s" % (location, instance)

        if ui is not None:
            jsobj.ui = ui
        sc = FileConfig(instance=instance, location=location, template=template, data=data)

        return sc

    def js_obj_get(self, location="", instance="main", data={}):
        """
        will look for jumpscale module on defined location & return this object
        and generate the object which has a .config on the object
        """
        self.sandbox_check()
        if not location:
            if j.sal.fs.getcwd().startswith(self.path):
                # means we are in subdir of current config  repo, so we can be
                # in location
                location = j.sal.fs.getBaseName(j.sal.fs.getcwd())
                if not location.startswith("j."):
                    raise RuntimeError(
                        "Cannot find location, are you in right directory? now in:%s" % j.sal.fs.getcwd())
            else:
                raise RuntimeError(
                    "location has not been specified, looks like we are not in config directory:'%s'" % self.path)

        obj = eval(location)
        # If the client is a single item one (i.e itsyouonline), we will always use the default `main` instance
        if obj._single_item:
            instance = "main"
        if not hasattr(obj, 'get'):
            return obj
        obj = obj.get(instance=instance, data=data)
        return obj

    def get(self, location, instance="main"):
        """
        return a secret config, it needs to exist, otherwise it will die
        """
        self.sandbox_check()
        if location == "":
            raise RuntimeError("location cannot be empty")
        if instance == "" or instance is None:
            raise RuntimeError("instance cannot be empty")
        key = "%s_%s" % (location, instance)

        return FileConfig(instance=instance, location=location)

    def list(self, location="j.tools.myconfig"):
        """
        list all the existing instance name for a location

        if empty then will list (($location,$name),)

        @return: list of instance name
        """
        self.sandbox_check()
        instances = []

        if not location:
            res = []
            for location in j.sal.fs.listDirsInDir(self.path, recursive=False, dirNameOnly=True):
                if ".git" in location:
                    continue
                for instance in self.list(location):
                    res.append((location, instance))
            return res

        root = j.sal.fs.joinPaths(self.path, location)
        if not j.sal.fs.exists(root):
            return instances

        # jsclient_object = eval(location)

        for cfg_path in j.sal.fs.listFilesInDir(root):
            cfg_name = j.sal.fs.getBaseName(cfg_path)
            if cfg_name in ('.git', '.jsconfig'):
                continue
            # trim the extension
            instance_name, _ = os.path.splitext(cfg_name)
            instances.append(instance_name)

        return instances

    def delete(self, location, instance="*"):
        self.sandbox_check()
        if instance != "*":
            path = j.sal.fs.joinPaths(j.tools.configmanager.path, location, instance + '.toml')
            if j.sal.fs.exists(path):
                j.sal.fs.remove(path)
        else:
            path = j.sal.fs.joinPaths(j.tools.configmanager.path, location)
            if j.sal.fs.exists(path):
                for item in j.sal.fs.listFilesInDir(path):
                    j.sal.fs.remove(item)

    def __str__(self):
        self.sandbox_check()
        sshagent = j.clients.sshkey.sshagent_available()
        keyloaded = self.keyname in j.clients.sshkey.listnames()
        C = """
        
        configmanager:
        - backend: file
        - path: {path}
        - keyname: {keyname}
        - is sandbox: {sandbox}
        - sshagent loaded: {sshagent}
        - key in sshagent: {keyloaded}

        """.format(**{"path": self.path,
                      "sshagent": sshagent,
                      "keyloaded": keyloaded,
                      "keyname": self.keyname,
                      "sandbox": self.sandbox_check()})
        C = j.data.text.strip(C)

        return C

    __repr__ = __str__

    def test(self):
        """
        js_shell 'j.tools.configmanager.test()'
        """

        def testinit():

            tdir = "/tmp/tests/secretconfig"
            # j.sal.process.execute("cd %s && git init" % tdir)

            MYCONFIG = """
            fullname = "kristof@something"
            email = "kkk@kk.com"
            login_name = "dddd"
            """
            data = j.data.serializer.toml.loads(MYCONFIG)

            self.init(path=tdir, data=data, silent=True)

            assert j.tools.myconfig.config.data == data

            return data

        data = testinit()
        self._test_myconfig_singleitem(data)
        testinit()
        self._test_myconfig_multiitem()

        # j.sal.fs.remove(tdir)

    def _test_myconfig_singleitem(self, data):

        tdir = "/tmp/tests/secretconfig/j.tools.myconfig"
        # there should be 1 file
        assert len(j.sal.fs.listFilesInDir(tdir)) == 1

        # check that the saved data is ok
        assert j.data.serializer.toml.fancydumps(
            j.tools.myconfig.config.data) == j.data.serializer.toml.fancydumps(data)

        self.delete("j.tools.myconfig")  # should remove all
        assert len(j.sal.fs.listFilesInDir(tdir)) == 0

        # j.tools.configmanager.reset()
        j.tools.myconfig.reset()  # will remove data from mem
        assert j.tools.myconfig.config._data == {
            'email': '', 'fullname': '', 'login_name': ''}
        assert j.tools.myconfig.config.data == {
            'email': '', 'fullname': '', 'login_name': ''}

        j.tools.myconfig.config.load()
        assert j.tools.myconfig.config.data == {
            'email': '', 'fullname': '', 'login_name': ''}
        j.tools.myconfig.config.data = data
        j.tools.myconfig.config.save()
        assert len(j.sal.fs.listFilesInDir(tdir)) == 1

        # clean the env
        # j.tools.configmanager.reset()
        j.tools.myconfig.reset()
        j.tools.myconfig.config._data = {}
        assert j.data.serializer.toml.fancydumps(
            j.tools.myconfig.config.data) == j.data.serializer.toml.fancydumps(data)

        # clean the env
        # j.tools.configmanager.reset()
        j.tools.myconfig.config.load()
        j.tools.myconfig.config.data = {"email": "someting@ree.com"}
        j.tools.myconfig.config.save()
        # j.tools.configmanager.reset()

        assert j.tools.myconfig.config.data["email"] == "someting@ree.com"

        # delete
        self.delete("j.tools.myconfig", "main")
        assert len(j.sal.fs.listFilesInDir(tdir)) == 0

    def _test_myconfig_multiitem(self):

        MYCONFIG = """
        name = ""
        addr = "192.168.1.1"
        port = 22
        clienttype = "ovh"
        active = true
        selected = true
        category = "me"
        description = "some descr"
        secretconfig_ = "my secret config"
        """
        data = j.data.serializer.toml.loads(MYCONFIG)

        for i in range(10):
            data["addr"] = "192.168.1.%s" % i
            data["name"] = "test%s" % i
            obj = j.tools.nodemgr.get("test%s" % i, data=data)

        # empty mem
        # j.tools.configmanager.reset()
        j.tools.nodemgr.items = {}

        obj = j.tools.nodemgr.get("test5")
        assert obj.config._data["addr"] == "192.168.1.5"
        assert obj.config.data["addr"] == "192.168.1.5"
        # needs to be encrypted
        assert obj.config._data["secretconfig_"] != "my secret config"
        assert obj.config.data["secretconfig_"] == "my secret config"

        tdir = "/tmp/tests/secretconfig/j.tools.nodemgr"
        assert len(j.sal.fs.listFilesInDir(tdir)) == 10

        obj.config.data = {"secretconfig_": "test1"}
        assert obj.config.data["secretconfig_"] == "test1"

        i = j.tools.nodemgr.get("test1")
        assert i.name == "test1"

        # j.tools.nodemgr.reset()
        # assert len(j.sal.fs.listFilesInDir(tdir)) == 0
