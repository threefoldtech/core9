import pytoml
from JumpScale9 import j
import os
import sys

# ONLY DEVELOPED NOW FOR CONFIG, REST NEEDS TO BE DONE


class State():

    def __init__(self):
        self.readonly = False
        self._db = None
        self.config = None
        self._configPath=None
        self.configLoad()

    @property
    def configPath(self):
        if self._configPath==None:
            if j.sal.fs.exists("/etc/", followlinks=True):
                self._configPath= "/etc/jumpscale9.toml"
            else:
                self._configPath= "%s/jumpscale9.toml"%os.environ["HOME"]
        return self._configPath

    @property
    def versions(self):
        versions = {}
        for name, path in self.config.get('plugins', {}).items():
            repo = j.clients.git.get(path)
            _, versions[name] = repo.getBranchOrTag()
        return versions

    @property
    def db(self):
        return None
        if self._db is None and j.clients is not None:
            self._db = j.clients.redis.get4core()
        return self._db

    @property
    def _vardir(self):
        if str(sys.platform).startswith("linux"):
            return "/optvar"
        else:
            return "%s/opt/var"%os.environ["HOME"]
        

    def configLoad(self):
        if j.sal.fs.exists(self.configPath):
            table_open_object = open(self.configPath, 'r')
            self.config = pytoml.load(table_open_object)
        else:
            self.config={}

    def configGet(self, key, defval=None, set=False):
        """
        """
        if key in self.config:
            return self.config[key]
        else:
            if defval is not None:
                if set:
                    self.configSet(key, defval)
                return defval
            else:
                raise j.exceptions.Input(
                    message="could not find config key:%s in executor:%s" %
                    (key, self), level=1, source="", tags="", msgpub="")

    def configSet(self, key, val, save=True):
        """
        @return True if changed
        """
        if key in self.config:
            val2 = self.config[key]
        else:
            val2 = None
        if val != val2:
            self.config[key] = val
            print("config set %s:%s" % (key, val))
            # print("config changed")
            self._config_changed = True
            if save:
                self.configSave()
            return True
        else:
            if save:
                self.configSave()
            return False

    def configSetInDict(self, key, dkey, dval):
        """
        will check that the val is a dict, if not set it and put key & val in
        """
        if key in self.config:
            val2 = self.config[key]
        else:
            self.configSet(key, {}, save=True)
            val2 = {}
        if dkey in val2:
            if val2[dkey] != dval:
                self._config_changed = True
        else:
            self._config_changed = True

        val2[dkey] = dval

        self.config[key] = val2
        print("config set dict %s:%s:%s" % (key, dkey, dval))
        self.configSave()

    def configGetFromDict(self, key, dkey, default=None):
        """
        get val from subdict
        """
        if key not in self.config:
            self.configSet(key, val={}, save=True)

        if dkey not in self.config[key]:
            if default is not None:
                return default
            raise RuntimeError("Cannot find dkey:%s in state config for dict '%s'" % (dkey, key))

        return self.config[key][dkey]

    def configUpdate(self, ddict, overwrite=True):
        """
        will walk over  2 levels deep of dict & update
        """
        for key0, val0 in ddict.items():
            if key0 not in self.config:
                self.configSet(key0, val0, save=False)
            else:
                if not j.data.types.dict.check(val0):
                    raise RuntimeError(
                        "first level in config needs to be a dict ")
                for key1, val1 in val0.items():
                    if key1 not in self.config[key0]:
                        self.config[key0][key1] = val1
                        self._config_changed = True
                    else:
                        if overwrite:
                            self.config[key0][key1] = val1
                            self._config_changed = True
        self.configSave()

    def configSave(self):
        if self.readonly:
            raise j.exceptions.Input(
                message="cannot write config to '%s', because is readonly" %
                self, level=1, source="", tags="", msgpub="")
        path=self.configPath
        try:
            table_open_object = open(path, 'w')
        except FileNotFoundError:
            try:
                os.makedirs(os.path.dirname(path))
            except OSError:
                pass
            table_open_object = open(path, 'x')
        try:
            data = pytoml.dump(self.config,table_open_object, sort_keys=True)
        except:
            print("[-] ERROR COULD NOT SAVE CONFIG FOR JUMPSCALE")
            print(self.config)
            raise RuntimeError("ERROR COULD NOT SAVE CONFIG FOR JUMPSCALE")

    def resetConfig(self):
        self.config = {}
        self.configSave()

    def resetState(self):
        from IPython import embed
        print("DEBUG NOW resetState")
        embed()
        raise RuntimeError("stop debug here")

    def resetCache(self):
        from IPython import embed
        print("DEBUG NOW reset cache")
        embed()
        raise RuntimeError("stop debug here")

    def resetAll(self):
        self.resetState()
        self.resetCache()
        self.resetConfig()

    def _getpath(self, cat="cfg", key=None):
        if cat == "cache":
            path = "%s/cache/%s" % (self._vardir, key)
        elif cat == "state":
            path = "%s/state/%s" % (self._vardir, key)
        else:
            raise RuntimeError("only supported categories: cache,state")
        return path

    def _set(self, cat="cfg", data="", key=None):
        if self.db is not None:
            from IPython import embed
            print("DEBUG NOW sdat")
            embed()
            raise RuntimeError("stop debug here")
        else:
            path = self._getpath(cat=cat, key=key)
            j.sal.fs.createDir(j.sal.fs.getDirName(path))
            j.sal.fs.writeFile(filename=path, contents=data, append=False)

    def _exists(self, cat="cfg", data="", key=None):
        if self.db is not None:
            from IPython import embed
            print("DEBUG NOW wewe")
            embed()
            raise RuntimeError("stop debug here")
        else:
            path = self._getpath(cat=cat, key=key)
            return os.path.exists(path)

    def _get(self, cat="cfg", data="", key=None):
        if self.db is not None:
            from IPython import embed
            print("DEBUG NOW 2323")
            embed()
            raise RuntimeError("stop debug here")
        else:
            path = self._getpath(cat=cat, key=key)
            with open(path, 'r') as f:
                return f.read()
