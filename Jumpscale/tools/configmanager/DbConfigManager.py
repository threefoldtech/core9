from .IConfigManager import IConfigManager


from jumpscale import j
import sys
import re
import os
import copy
from .JSBaseClassConfig import JSBaseClassConfig
from .JSBaseClassConfigs import JSBaseClassConfigs
from .DbConfig import DbConfig, mk_hsetname, hdel, iselect_all, get_key_info


installmessage = """

**ERROR**: there is no config directory created

create a git repository on github or any other git system.
checkout this repository by doing

'js_code get --url='...your ssh git url ...'

the go to this directory (to to that path & do)

js_config init
"""


"cfg_reponame:myconfig_instance:main"


class DbConfigManager(IConfigManager):

    def __init__(self):
        super().__init__()

        self._path = ""
        self.interactive = True  # std needs to be on True
        self.sandbox = True
        self._keyname = ""  # if set will overrule from the main js config file
        self._keypath = ""
        self._init = False
        self._zdbsimplecl = None
        self._namespace = j.core.state.configGetFromDict("myconfig", "namespace", "default")
        self.set_namespace(self._namespace)

    @property
    def namespace(self):
        if not self._namespace:
            raise RuntimeError("configmanager isn't configured for a namespace you need to set the namespace using j.tools.configmanager.set_namespace")
        return self._namespace

    def init(self, data={}, silent=False, configpath="", keypath=""):
        privkeypath = keypath
        pubkeypath = keypath + ".pub"
        self._keypath = keypath

        self.configure_keys_from_paths(privkeypath, pubkeypath)

    def configure_keys(self, keypriv, keypub, seed="NULL", keyprivencoded="NULL"):
        self._zdbsimplecl.namespace.set(keypriv, "key.priv")
        self._zdbsimplecl.namespace.set(keypub, "key.pub")
        self._zdbsimplecl.namespace.set(seed, "key.seed")
        self._zdbsimplecl.namespace.set(keyprivencoded, "key.priv.encoded")
        self.prepare_mgmt_repo()

    def configure_keys_from_paths(self, keypriv_path, keypub_path, seed_path=None, priv_key_encoded_path=None):
        seed_data = "NULL"
        if seed_path:
            seed_data = j.sal.fs.readFile(seed_path)

        priv_key_encoded_data = "NULL"
        if priv_key_encoded_path:
            priv_key_encoded_data = j.sal.fs.readFile(priv_key_encoded_path)
        self._keypath = keypriv_path
        return self.configure_keys(j.sal.fs.readFile(keypriv_path), j.sal.fs.readFile(keypub_path), seed_data, priv_key_encoded_data)

    @property
    def keypath(self):
        return self._keypath

    def configure_from_sandbox(self, sandbox_path, keyisdirname=True):
        keyname = "key"
        if keyisdirname:
            keyname = j.sal.fs.getBaseName(sandbox_path)

        keysdir = j.sal.fs.joinPaths(sandbox_path, "keys")
        privkeypath = j.sal.fs.joinPaths(keysdir, keyname)
        pubkeypath = j.sal.fs.joinPaths(keysdir, keyname+".pub")

        seed = j.sal.fs.joinPaths(sandbox_path, "key.seed")
        privkey_encoded = j.sal.fs.joinPaths(sandbox_path, "key.priv")

        self.configure_keys_from_paths(privkeypath, pubkeypath, seed, privkey_encoded)

    def get_keys(self):
        return self._zdbsimplecl.namespace.get("key.priv"), self._zdbsimplecl.namespace.get("key.pub"), self._zdbsimplecl.namespace.get("key.seed"), self._zdbsimplecl.namespace.get("key.priv.encoded")

    def set_namespace(self, namespace):
        self._zdbsimplecl = None
        if namespace == "default":
            self.logger.warning("using default namespace.")
        else:
            self.logger.info("using namespace {}".format(namespace))
        self._namespace = namespace
        if j.core.state.configGetFromDict("myconfig", "backend", "file") == "db":
            backend_addr = j.core.state.configGetFromDict("myconfig", "backend_addr", "localhost:9900")
            adminsecret = j.core.state.configGetFromDict("myconfig", "adminsecret", "")
            secrets = j.core.state.configGetFromDict("myconfig", "secrets", "")

            if ":" in backend_addr:
                host, port = backend_addr.split(":")
                if port.isdigit():
                    port = int(port)
                else:
                    raise RuntimeError("port is expected to be a number, but got {}".format(port))
                self._zdbsimplecl = j.clients.zdbsimple.get(host, port, adminsecret, secrets, namespace)
                # TODO: understand better secret/secrets/adminsecrets role..
                self._zdbsimplecl.namespace_new(namespace, die=False)
            else:
                raise ValueError("Can't instantiate configmanager with db backend without specifying that in jumpscale state.")
        # try to populate sandbox if namespace has the keys
        if self._zdbsimplecl.namespace.exists('key.priv') and self._zdbsimplecl.namespace.exists('key.pub'):
            self.configure_keys(self._zdbsimplecl.namespace.get('key.priv'), self._zdbsimplecl.namespace.get('key.pub'),
                                self._zdbsimplecl.namespace.get('key.seed'), self._zdbsimplecl.namespace.get('key.seed'))

        self._keypath = j.sal.fs.joinPaths(self.path, "keys", "key")

    def reset(self, location=None, instance=None, force=False):
        """
        Reset configurations

        @param force: If no location is given and force is set to true then all locations will be reset
        """
        if location is None:
            location = '.+'
        if instance is None:
            instance = '.+'

        hsetname = mk_hsetname(configrepo='.+', instance=instance, clientpath=location)

        configs_keys = iselect_all(self._zdbsimplecl, hsetname)
        if force or j.tools.console.askYesNo("No location specified, Are you sure you want to delete all configs?", default=True):
            for k in configs_keys:
                hdel(self._zdbsimplecl, k)

    @property
    def path(self):
        # rootconfig
        home = j.dirs.HOMEDIR
        if not self.namespace:
            raise RuntimeError("you need to configure namespace using set_namespace")

        mgmtpath = j.sal.fs.joinPaths(home, "configmgrsandboxes", self.namespace)
        if not j.sal.fs.exists(mgmtpath):
            try:
                os.makedirs(mgmtpath)
            except Exception as e:
                raise RuntimeError("Couldn't prepare dbconfig repo path")
        return mgmtpath

    def prepare_mgmt_repo(self):
        priv, pub, seed, encoded_key = self.get_keys()
        mgmtpath = self.path

        self.sandbox = True
        j.sal.fs.createDir(mgmtpath)
        keyspath = j.sal.fs.joinPaths(mgmtpath, "keys")
        secureconfigpath = j.sal.fs.joinPaths(mgmtpath, "secureconfig")

        os.makedirs(keyspath, exist_ok=True)
        os.makedirs(secureconfigpath, exist_ok=True)

        self._keypath = j.sal.fs.joinPaths(keyspath, "key")
        j.sal.fs.writeFile(j.sal.fs.joinPaths(keyspath, "key"), priv)
        j.sal.fs.writeFile(j.sal.fs.joinPaths(keyspath, "key.pub"), pub)
        if seed.decode() != "NULL":
            j.sal.fs.writeFile(j.sal.fs.joinPaths(mgmtpath, "key.seed"), seed)
        else:
            # TODO: check behavior with secret and sshkeyname..
            nacl = j.data.nacl.get("key")
            # put the seed in the db
            self._zdbsimplecl.namespace.set(j.sal.fs.readFile(j.sal.fs.joinPaths(mgmtpath, "key.seed")), "key.seed")
            self._zdbsimplecl.namespace.set(j.sal.fs.readFile(j.sal.fs.joinPaths(mgmtpath, "key.priv")), "key.priv.encoded")

    def _findConfigRepo(self, die=False):
        """
        if path is not set, it will look under CODEDIRS for any pre-configured js_config repo
        if there are more than one, will try to use one in root of cwd. If not in one, will raise a RuntimeError

        return configpath,remoteGitUrl
        """
        # self.sandbox_check()

        # return self._zdbsimplecl.get(CONFIG_REPO_PATH), self._zdbsimplecl.get(CONFIG_REPO_REMOTE_URL)
        # SHOULD USE CONFIG REPO ON THE FS...
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
        sc = DbConfig(instance=instance, location=location, template=template, data=data)
        return sc

    # FIXME: not sure how it works..

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

    def sandbox_check(self):
        return True

    def sandbox_init(self, path="", passphrase="", reset=False, sshkeyname="key"):
        """
        Will use specified dir as sandbox for config management (will not use system config dir)
        looks for $path/secureconfig & $path/sshkeys (if systemssh == False)
        if not found will create
        Keyword Arguments:
            systemssh {Bool} -- if True will use the configured sshkey on system (default: {False})
            reset {Bool} -- will replace current config (default: {False})
            sshkeyname -- if empty will be dirname of current path
        Returns:
            SSHKey
        """

        if path:
            j.sal.fs.changeDir(path)

        # just to make sure all stays relative (we don't want to store full paths)
        path = ""

        cpath = "secureconfig"
        j.sal.fs.createDir(cpath)

        kpath_full = "keys/%s" % sshkeyname
        kpath_full0 = j.sal.fs.pathNormalize(kpath_full)
        j.tools.configmanager._keyname = sshkeyname

        j.tools.configmanager._path = j.sal.fs.pathNormalize(cpath)

        data = {}
        data["path"] = kpath_full
        data["passphrase_"] = passphrase

        sshkeyobj = j.clients.sshkey.get(instance=sshkeyname, data=data, interactive=False)

        self.sandbox = True
        # WE SHOULD NOT CONFIGURE THE HOST CONFIGMMANAGER ALL SHOULD BE ALREADY DONE
        #j.tools.configmanager.init(configpath=cpath, keypath=kpath_full, silent=False)

        return sshkeyobj

    def get(self, location, instance="main"):
        """
        return a secret config, it needs to exist, otherwise it will die
        """
        self.sandbox_check()
        if location == "":
            raise RuntimeError("location cannot be empty")
        if instance == "" or instance == None:
            raise RuntimeError("instance cannot be empty")

        return DbConfig(instance=instance, location=location)

    def list(self, location=""):
        """
        list all the existing instance name for a location

        if empty then will list (($location,$name),)

        @return: list of instance name
        """
        # self.sandbox_check()
        if not location:
            location = ".*"

        pattern = mk_hsetname(configrepo=".*", instance=".*", clientpath=location)
        # extract instance names here..
        instances = []
        for k in iselect_all(self._zdbsimplecl, pattern):
            kinfo = get_key_info(k)
            instances.append(kinfo['instance'])

        return instances

    def delete(self, location, instance="*"):
        pattern = mk_hsetname(configrepo=".*", instance=instance, clientpath=location)
        for k in iselect_all(self._zdbsimplecl, pattern):
            hdel(self._zdbsimplecl, k)

    def __str__(self):
        self.sandbox_check()
        sshagent = j.clients.sshkey.sshagent_available()
        keyloaded = self.keyname in j.clients.sshkey.listnames()
        C = """

        configmanager:
        - backend: db
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
