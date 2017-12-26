from js9 import j
# import os
# import copy


class Config():

    def __init__(self, instance="main",location=None,template={},ui=None,data={}):
        """
        jsclient_object is e.g. j.clients.packet.net
        """
        self.location = location
        self.instance = instance
        self._template = template
        self._data = {}
        self.data=data
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

        dirpath = j.tools.configmanager.path_configrepo + "/%s" % self.location

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
            # print("set data:%s %s"%(ttype,key))
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
