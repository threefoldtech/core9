from jumpscale import j
import re
import json
from inspect import getmodule

JSBASE = j.application.jsbase_get_class()

HSET_NAME = "cfg::{configrepo}::{instance}::{clientpath}"

def get_key_info(k):
    m = re.match("cfg::(?P<configrepo>\w+)::(?P<instance>\w+)::(?P<clientpath>.+)", k)
    if m:
        return m.groupdict()
    return None


def mk_hsetname(configrepo="myconfig", instance="main", clientpath=""):
    return HSET_NAME.format(configrepo=configrepo, instance=instance, clientpath=clientpath)


def hset(client, hsetname, key, val):
    nsclient = client.namespace
    data_str = nsclient.get(hsetname)
    data = {}
    try:
        data = json.loads(data_str)
    except Exception as e:
        pass

    data[key] = val
    data_str = json.dumps(data)
    nsclient.set(data_str, hsetname)
    return True


def hsetmany(client, hsetname, **kwargs):
    nsclient = client.namespace
    data_str = nsclient.get(hsetname)
    data = {}
    try:
        data = json.loads(data_str)
    except Exception as e:
        pass
    for k, v in kwargs.items():
        data[k] = v
    data_str = json.dumps(data)
    nsclient.set(data_str, hsetname)
    return True

 

def hget(client, hsetname, key):
    try:
        return hget_all(client, hsetname)[key]
    except:
        return {}

def hget_all(client, hsetname):
    nsclient = client.namespace
    data_str = nsclient.get(hsetname)
    try:
        data = json.loads(data_str)
        return data
    except:
        return {} 

def hdel(client, hsetname):
    nsclient = client.namespace
    nsclient.delete(hsetname)

def hdel_key(client, hsetname, key):
    d = hget_all(client, hsetname)
    try:
        del d[key]
    except:
        return True
    else:
        hsetmany(client, hsetname, **d)


def iselect_all(client, pattern=None):
    nsclient = client.namespace
    
    result = []
    def do(arg, result):
        if pattern:
            try:
                arg = arg.decode()
            except Exception as e:
                print(e)
            else:
                if re.match(pattern, arg):
                    result.append(arg)
        else:
            result.append(arg)
        return result

    nsclient.iterate(do, key_start=None, direction="forward", nrrecords=100000,  _keyonly=True, result=result)

    return result



def find_configs(client):
    configs = []
    for el in iselect_all(client):
        if el.startswith("cfg::"): # USE re.match better
            configs.append(el)

    return configs

def template_from_object(obj):
    module = None
    if hasattr(obj,"_child_class"):
        obj._child_class
        try:
            module = getmodule(obj._child_class)
        except Exception as e:
            if "cannot import name" in str(e):
                raise RuntimeError("cannot find TEMPLATE in %s, please call the template: TEMPLATE"%obj._child_class.__module__)
            raise e          
    else:
        try:
            module = getmodule(obj)
        except Exception as e:
            if "cannot import name" in str(e):
                raise RuntimeError("cannot find TEMPLATE in %s, please call the template: TEMPLATE"%obj.__module__)
            raise e
    return module.TEMPLATE


class DbConfig(JSBASE):

    def __init__(self, instance="main", location=None, template=None, data={}):
        """
        jsclient_object is e.g. j.clients.packet.net
        """

        JSBASE.__init__(self)
        self._zdbsimplecl = None
        if j.core.state.configGetFromDict("myconfig", "backend", "file") == "db":
            backend_addr = j.core.state.configGetFromDict("myconfig", "backend_addr", "localhost:9900")
            adminsecret = j.core.state.configGetFromDict("myconfig", "adminsecret", "")
            secrets = j.core.state.configGetFromDict("myconfig", "secrets", "")
            namespace = j.tools.configmanager.namespace

            if ":" in backend_addr:
                host, port = backend_addr.split(":")
                if port.isdigit():
                    port = int(port)
                else:
                    raise RuntimeError("port is expected to be a number, but got {}".format(port))
                self._zdbsimplecl = j.clients.zdbsimple.get(host, port, adminsecret, secrets, namespace)
        else:
            raise RuntimeError("can't create DbConfig with file backend.")
        data = data or {}
        self.location = j.data.text.toStr(location)
        self.instance = j.data.text.toStr(instance)
        self.hsetname = mk_hsetname(configrepo="myconfig", instance=self.instance, clientpath=self.location)
        self._path = self.location
        self.error = False # if this is true then need to call the configure part
        self._template = template
        if not j.data.types.string.check(template):
            if template is not None:
                raise RuntimeError("template needs to be None or string:%s"%template)
        if self.instance is None:
            raise RuntimeError("instance cannot be None")

        self.reset()
        self.load()
        
        if not self._zdbsimplecl.namespace.get(self.hsetname):
            self.new = True

        # this is data on disk, because exists, should already apply to template
        # without decryption so needs to go to self._data
        dataOnFS = self.data  # now decrypt
        # make sure template has been applied !
        data2, error = j.data.serializer.toml.merge(tomlsource=self.template, tomlupdate=dataOnFS, listunique=True)
        if data != {}:
            # update with data given
            data, error = j.data.serializer.toml.merge(tomlsource=data2, tomlupdate=data, listunique=True)
            self.data = data
        else:
            # now put the data into the object (encryption)
            self.data = data2

        # do the fancydump to make sure we really look at differences
        if j.data.serializer.toml.fancydumps(self.data) != j.data.serializer.toml.fancydumps(dataOnFS):
            self.logger.debug("change of data in config, need to save")
            self.save()

    def reset(self):
        self._data = {}
        self.loaded = False
        self._path = None
        self._nacl = None
        self.new = False

    @property
    def path(self):
        self.logger.debug("init getpath:%s" % self._path)
        if not self._path:
            self._path = self.location #j.sal.fs.joinPaths(j.data.text.toStr(j.tools.configmanager.path), self.location, self.instance + '.toml')
            self.logger.debug("getpath:%s" % self._path)
        return self._path

    @property
    def nacl(self):
        if not self._nacl:
            if j.tools.configmanager.keyname:
                self._nacl = j.data.nacl.get(sshkeyname=j.tools.configmanager.keyname)
            else:
                self._nacl = j.data.nacl.get()
        return self._nacl

    def instance_set(self, instance):
        """
        will change instance name & delete data
        """
        self.instance = instance
        self.load(reset=True)

    def load(self, reset=False):
        """
        @RETURN if 1 means did not find the toml file so is new
        """
        # if not reset or self._data == {}:
            # TODO: assert the hset exists.
        bdata = hget_all(self._zdbsimplecl, self.hsetname)
        for k, v in bdata.items():
            if isinstance(k, bytes):
                k = k.decode()
            if isinstance(v, bytes):
                v = v.decode()
            self._data[k] = v

        for key, val in self.template.items():
            ttype = j.data.types.type_detect(self.template[key])
            if ttype.BASETYPE == "string":
                if key.encode() in self._data:
                    self._data[key.encode()] = self._data[key.encode()].strip()

    def save(self):
        hsetmany(self._zdbsimplecl, self.hsetname, **self._data)

    
    def delete(self):
        hdel(self._zdbsimplecl, self.hsetname)



    @property
    def template(self):
        if self._template is None or self._template == '':
            obj = eval(self.location)
            self._template = template_from_object(obj)
        if j.data.types.string.check(self._template):
            try:
                self._template = j.data.serializer.toml.loads(self._template)
            except Exception as e:
                if "deserialization failed" in str(e):
                    raise RuntimeError("config file:%s is not valid toml.\n%s"%(self.path,self._template))
                raise e          
        return self._template

    @property
    def data(self):
        res = {}
        if self._data == {}:
            self.load()
        for key, item in self._data.items():
            if isinstance(key, bytes):
                key = key.decode()
            if key not in self.template:
                self.logger.warning("could not find key:%s in template, while it was in instance:%s"%(key,self.path))
                self.logger.debug("template was:%s\n"%self.template)
                self.error=True
            else:
                ttype = j.data.types.type_detect(self.template[key])
                if key.endswith("_"):
                    if ttype.BASETYPE == "string":
                        if item != '' and item != '""':
                            res[key] = self.nacl.decryptSymmetric(item, hex=True).decode()
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

        changed = False
        for key, item in value.items():
            ch1 = self.data_set(key, item, save=False)
            changed = changed or ch1

        if changed:
            # raise RuntimeError()
            self.logger.debug("changed:\n%s" % self)
            self.save()

    def data_set(self, key, val, save=True):
        if key not in self.template:
            raise RuntimeError(
                "Cannot find key:%s in template for %s" % (key, self))

        if key not in self._data or self._data[key] != val:
            ttype = j.data.types.type_detect(self.template[key])
            if key.endswith("_"):
                if ttype.BASETYPE == "string":
                    if val != '' and val != '""':
                        val = self.nacl.encryptSymmetric(val, hex=True, salt=val)
                        if key in self._data and val == self._data[key]:
                            return False
            self._data[key] = val
            if save:
                self.save()
            return True
        else:
            return False

    @property
    def yaml(self):
        return j.data.serializer.toml.fancydumps(self._data)

    def __str__(self):
        out = "config:%s:%s\n\n" % (self.location, self.instance)
        out += j.data.text.indent(self.yaml)
        return out

    __repr__ = __str__
