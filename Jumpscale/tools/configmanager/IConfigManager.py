from jumpscale import j
import sys


JSBASE = j.application.jsbase_get_class()


class IConfigManager(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)

    def reset(self, location, instance=None, force=False):
        pass

    def reset_all(self):
        pass

    def set_namespace(self, namespace):
        pass

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

    # let's keep it as a repo with key, seed only.
    def _findConfigRepo(self, die=False):
        pass

    def configure(self, location="", instance="main", data={}, interactive=True):
        pass

    def update(self, location, instance="main", updatedict={}):
        pass

    def _get_for_obj(self, jsobj, template, ui=None, instance="main", data={}):
        pass

    def js_obj_get(self, location="", instance="main", data={}):
        pass

    def get(self, location, instance="main"):
        pass

    def list(self, location="j.tools.myconfig"):
        pass

    def delete(self, location, instance="*"):
        pass

    def sandbox_init(self, path="", systemssh=False, passphrase="", reset=False, sshkeyname=""):
        """
        Will use specified dir as sandbox for config management (will not use system config dir)
        looks for $path/secureconfig & $path/sshkeys (if systemssh is False)
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
        if not sshkeyname:
            sshkeyname = j.sal.fs.getBaseName(j.sal.fs.getcwd())

        cpath = "secureconfig"
        j.sal.fs.createDir(cpath)

        if not systemssh:
            kpath_full = "keys/%s" % sshkeyname
            kpath_full0 = j.sal.fs.pathNormalize(kpath_full)
            if not j.sal.fs.exists("keys"):
                j.sal.fs.createDir("keys")
                j.clients.sshkey.key_generate(path=kpath_full0, passphrase=passphrase, load=True, returnObj=False)
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

    def sandbox_check(self, path="", die=False):
        if self._init and path == "" and die is False:
            return self.sandbox
        if not path:
            path = j.sal.fs.getcwd()

        cpath = j.sal.fs.pathNormalize(path + "/secureconfig")
        kpath = j.sal.fs.pathNormalize(path + "/keys")

        if j.sal.fs.exists(cpath):
            self.logger.debug("found sandbox config:%s" % cpath)
            j.tools.configmanager._path = cpath
            self.sandbox = True
        if j.sal.fs.exists(kpath):
            self.logger.debug("found sandbox sshkeys:%s" % kpath)
            items = j.sal.fs.listFilesInDir(kpath, filter="*.pub")
            if len(items) != 1:
                raise RuntimeError("should only find 1 key, found:%s" % items)
            sshkeyname = j.sal.fs.getBaseName(items[0][:-4])
            kpath_full = j.sal.fs.pathNormalize(path + "/keys/%s" % sshkeyname)
            j.tools.configmanager._keyname = sshkeyname
            self._init = True
            self.sandbox = True
            return j.clients.sshkey.key_load(path=kpath_full, duration=None)

        if die:
            raise RuntimeError("did not find sandbox on this path:%s" % path)
        self._init = True
        return self.sandbox

    def init(self, data={}, silent=False, configpath="", keypath=""):
        """
        @param data is data for myconfig
        @param configpath is the path towards the config directory can be git based or local
        @param keypath is the path towards the ssh key which will be used to use the config manager
        """
        def msg(msg):
            self.logger.info("Jumpscale init: %s" % msg)

        def die(msg):
            self.logger.error("ERROR: CANNOT INIT jumpscale")
            self.logger.error("ERROR: %s" % msg)
            self.logger.error(
                "make sure you did the upgrade procedure: 'cd  ~/code/github/threefoldtech/jumpscale_core/;python3 upgrade.py'")
            sys.exit(1)

        def ssh_init(ssh_silent=False):
            self.logger.debug("ssh init (no keypath specified)")

            keys = j.clients.sshkey.list()  # LOADS FROM AGENT NOT FROM CONFIG
            keys0 = [j.sal.fs.getBaseName(item) for item in keys]

            if not keys:
                # if no keys try to load a key from home directory/.ssh and re-run the method again
                self.logger.info("found 0 keys from ssh-agent")
                keys = j.sal.fs.listFilesInDir("%s/.ssh" % j.dirs.HOMEDIR,
                                               exclude=["*.pub", "*authorized_keys*", "*known_hosts*"])
                if not keys:
                    raise RuntimeError("Cannot find keys, please load right ssh keys in agent, now 0")
                elif len(keys) > 1:
                    if silent:
                        raise RuntimeError("cannot run silent if more than 1 sshkey exists in your ~/.ssh directory, "
                                           "please either load your key into your ssh-agent or "
                                           "make sure you have only one key in ~/.ssh")
                    msg("found ssh keys in your ~/.ssh directory, do you want to load one is ssh-agent?")
                    key_chosen = j.tools.console.askChoice(keys)
                    j.clients.sshkey.key_load(path=key_chosen, duration=None)
                else:
                    j.clients.sshkey.key_load(path=keys[0], duration=None)
                return ssh_init()

            elif len(keys) > 1:
                # if loaded keys are more than one, ask user to select one or raise error if in silent mode
                if ssh_silent:
                    raise RuntimeError("cannot run silent if more than 1 sshkey loaded")
                # more than 1 key
                msg("Found more than 1 ssh key loaded in ssh-agent, "
                    "please specify which one you want to use to store your secure config.")
                key_chosen = j.tools.console.askChoice(keys0)
                j.core.state.configSetInDict("myconfig", "sshkeyname", key_chosen)

            else:
                # 1 key found
                msg("ssh key found in agent is:'%s'" % keys[0])
                if not silent:
                    msg("Is it ok to use this one:'%s'?" % keys[0])
                    if not j.tools.console.askYesNo():
                        die("cannot continue, please load other sshkey in your agent you want to use")
                j.core.state.configSetInDict("myconfig", "sshkeyname", keys0[0])

        if self.sandbox_check():
            return

        if data != {}:
            self.logger.debug("init: silent:%s path:%s withdata:\n" % (silent, configpath))
        else:
            self.logger.debug("init: silent:%s path:%s nodata\n" % (silent, configpath))

        if silent:
            self.interactive = False

        if configpath and not self.sandbox:
            self._path = configpath
            j.sal.fs.createDir(configpath)
            j.sal.fs.touch("%s/.jsconfig" % configpath)
            j.core.state.configSetInDict("myconfig", "path", configpath)

        cpath = configpath

        if keypath:
            self._keyname = j.sal.fs.getBaseName(keypath)
            j.core.state.configSetInDict("myconfig", "sshkeyname", self.keyname)
            j.clients.sshkey.key_get(keypath, load=True)
        else:
            ssh_init(ssh_silent=silent)

        cfg = j.core.state.config_js
        if "myconfig" not in cfg:
            die("could not find myconfig in the main configuration file, prob need to upgrade")

        if not cpath and not cfg["myconfig"].get("path", None):
            # means config directory not configured
            cpath, giturl = self._findConfigRepo(die=False)

            if silent:
                if not cpath:
                    msg("did not find config dir in code dirs, will create one in js_shell cfg dir")
                    cpath = '%s/myconfig/' % j.dirs.CFGDIR
                    j.sal.fs.createDir(cpath)
                    msg("Config dir in: '%s'" % cpath)
                j.core.state.configSetInDict("myconfig", "path", cpath)
                if not giturl:
                    j.core.state.configSetInDict("myconfig", "giturl", giturl)
            else:

                if cpath:
                    msg("Found a config repo on: '%s', do you want to use this one?" % cpath)
                    if not j.tools.console.askYesNo():
                        giturl = None
                        cpath = ""
                    else:
                        if giturl:
                            j.clients.git.pullGitRepo(url=giturl, interactive=True, ssh=True)

                if not cpath:
                    msg("Do you want to use a git based CONFIG dir, y/n?")
                    if j.tools.console.askYesNo():
                        msg("Specify a url like: 'ssh://git@docs.grid.tf:7022/despiegk/config_despiegk.git'")
                        giturl = j.tools.console.askString("url")
                        cpath = j.clients.git.pullGitRepo(url=giturl, interactive=True, ssh=True)

                if not cpath:
                    msg(
                        "will create config dir in '%s/myconfig/', your config will not be centralised! Is this ok?" % j.dirs.CFGDIR)
                    if j.tools.console.askYesNo():
                        cpath = '%s/myconfig/' % j.dirs.CFGDIR
                        j.sal.fs.createDir(cpath)

                if cpath:
                    j.core.state.configSetInDict("myconfig", "path", cpath)
                else:
                    die("ERROR: please restart config procedure, use git based config or need to store locally.")
                if giturl:
                    j.core.state.configSetInDict("myconfig", "giturl", giturl)

                j.core.state.configSave()

        data = data or {}
        if data:
            from Jumpscale.tools.myconfig.MyConfig import MyConfig as MyConfig
            j.tools._myconfig = MyConfig(data=data)

        if j.tools.myconfig.config.data["email"] == "":
            if not silent:
                j.tools.myconfig.configure()
                j.tools.myconfig.config.save()

    def __str__(self):
        return "IConfigManager..."

    __repr__ = __str__
