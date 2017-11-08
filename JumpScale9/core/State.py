import pytoml
from JumpScale9 import j
import sys
import os

class ClientConfig():
    def __init__(self, category,name):
        if category not in j.core.state.config.keys():
            j.core.state.config[category]={}
        if name not in j.core.state.config[category].keys():
            j.core.state.config[category][name]={}
        self.data=j.core.state.config[category][name]
        self.category=category
        self.name=name

    def save(self):
        j.core.state.config[self.category][self.name]=self.data
        j.core.state.configSave()


class State():
    """

    """

    def __init__(self, executor, configPath=""):
        self.readonly = False
        self.executor = executor
        self.load()

    def load(self, reset=False):
        if reset:
            self.executor.reset()
        self.configPath = self.executor.stateOnSystem["path_jscfg"] + \
            "/jumpscale9.toml"
        self.configMePath = self.executor.stateOnSystem["path_jscfg"] + "/me.toml"
        self.config = self.executor.stateOnSystem["cfg_js9"]
        self.configMe = self.executor.stateOnSystem["cfg_me"]

    @property
    def cfgPath(self):
        return self.executor.stateOnSystem["path_jscfg"]

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
            # print("config set %s:%s" % (key, val))
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
        # print("config set dict %s:%s:%s" % (key, dkey, dval))
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
            raise RuntimeError(
                "Cannot find dkey:%s in state config for dict '%s'" % (dkey, key))

        return self.config[key][dkey]

    def configGetFromDictBool(self, key, dkey, default=None):
        if key not in self.config:
            self.configSet(key, val={}, save=True)

        if dkey not in self.config[key]:
            if default is not None:
                return default
            raise RuntimeError(
                "Cannot find dkey:%s in state config for dict '%s'" % (dkey, key))

        val = self.config[key][dkey]
        if val in [1, True] or val.strip().lower() in ["true", "1", "yes", "y"]:
            return True
        else:
            return False

    def configSetInDictBool(self, key, dkey, dval):
        """
        will check that the val is a dict, if not set it and put key & val in
        """
        if dval in [1, True] or dval.strip().lower() in ["true", "1", "yes", "y"]:
            dval = "1"
        else:
            dval = "0"
        return configSetInDict(key, dkey, dval)

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
        """        
        if in container write: /hostcfg/me.toml
        if in host write: ~/js9host/cfg/me.toml
        """
        print("configsave")
        if self.readonly:
            raise j.exceptions.Input(
                message="cannot write config to '%s', because is readonly" %
                self, level=1, source="", tags="", msgpub="")
        # if self.executor == j.tools.executorLocal:
        #     # print("configsave state on %s" % self.configPath)
        #     path = self.configPath
        #     table_open_object = open(path, 'w')
        #     data = pytoml.dump(self.config, table_open_object, sort_keys=True)
        # else:
        # print("configsave state")
        data = pytoml.dumps(self.config)
        self.executor.file_write(self.configPath, data)
        data = pytoml.dumps(self.configMe)
        self.executor.file_write(self.configMePath, data)

        # if "me" in self.config:

        #     cdict = {}
        #     cdict["me"] = self.config["me"]
        #     cdict["email"] = self.config["email"]

        #     if self.executor == j.tools.executorLocal:
        #         # print("configsave state me on %s" % path)
        #         table_open_object = open(self.configMePath, 'w')
        #         data = pytoml.dump(cdict, table_open_object, sort_keys=True)
        #     else:
        #         # print("configsave state me")
        #         data = pytoml.dumps(cdict)
        #         self.executor.file_write(self.configMePath, data)

    def clientConfigGet(self,category,name):
        return ClientConfig(category,name)

    def reset(self):
        self.config = {}
        self.configSave()

    def __repr__(self):
        return str(self.config)

    def __str__(self):
        return str(self.config)
