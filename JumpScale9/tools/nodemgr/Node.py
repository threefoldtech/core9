from js9 import j

TEMPLATE = """
addr = ""
name = ""
port = 22
clienttype = ""
active = false
selected = false
category = ""
description = ""
secretconfig_ = ""
pubconfig = ""
"""

FormBuilderBaseClass = j.tools.formbuilder.baseclass_get()


class MyConfigUI(FormBuilderBaseClass):

    def init(self):
        # makes sure that this property is not auto populated, not needed when in form_add_items_pre
        self.auto_disable.append("clienttype")
        self.auto_disable.append("active")
        self.auto_disable.append("selected")

    def form_add_items_post(self):
        self.widget_add_boolean("active", default=False)
        self.widget_add_boolean("selected", default=True)
        self.widget_add_multichoice("clienttype", [
                                    "ovh", "packetnet", "ovc", "physical", "docker", "container", "zos"])


JSConfigBase = j.tools.configmanager.base_class_config


class Node(JSConfigBase):

    def __init__(self, instance, data={}, parent=None):
        self._connected = None
        JSConfigBase.__init__(self, instance=instance, data=data,
                              parent=parent, template=TEMPLATE, ui=MyConfigUI)

    @property
    def addr(self):
        return self.config.data["addr"]

    @addr.setter
    def addr(self, val):
        self.config._data["addr"] = val

    @property
    def port(self):
        return self.config.data["port"]

    @port.setter
    def port(self, val):
        self.config._data["port"] = val

    @property
    def active(self):
        return self.config.data["active"]

    @active.setter
    def active(self, val):
        self.config._data["active"] = val

    @property
    def clienttype(self):
        return self.config.data["clienttype"]

    @clienttype.setter
    def clienttype(self, val):
        self.config._data["clienttype"] = val

    @property
    def category(self):
        return self.config.data["category"]

    @category.setter
    def category(self, val):
        self.config._data["category"] = val

    @property
    def name(self):
        return self.config.data["name"]

    @name.setter
    def name(self, val):
        self.config._data["name"] = val

    @property
    def description(self):
        return self.config.data["description"]

    @description.setter
    def description(self, val):
        self.config._data["description"] = val

    @property
    def selected(self):
        return self.config.data["selected"]

    @selected.setter
    def selected(self, val):
        self.config._data["selected"] = val

    @property
    def secretconfig(self):
        data = self.config.data["secretconfig_"]
        data = j.data.serializer.json.loads(data)
        return data

    @secretconfig.setter
    def secretconfig(self, data):
        data = j.data.serializer.json.dumps(data)
        self.config._data["secretconfig_"] = data

    @property
    def pubconfig(self):
        data = self.config.data["pubconfig"]
        data = j.data.serializer.json.loads(data)
        return data

    @pubconfig.setter
    def pubconfig(self, data):
        data = j.data.serializer.json.dumps(data)
        self.config._data["pubconfig"] = data

    @property
    def isconnected(self):
        if self._connected is None:
            # lets test tcp on 22 if not then 9022 which are our defaults
            test = j.sal.nettools.tcpPortConnectionTest(
                self.addr, self.port, 3)
            if test is False:
                print("could not connect to %s:%s, will try port 9022" %
                      (self.addr, self.port))
                if self.port == 22:
                    test = j.sal.nettools.tcpPortConnectionTest(
                        self.addr, 9022, 1)
                    if test:
                        self.port = 9022
            if test is False:
                self._connected = False
            else:
                self._connected = True
                self.active = True
            self._sshclient = None
            self._ftpclient = None
        return self._connected

    @property
    def ftpclient(self):
        if self.isconnected:
            if self._ftpclient is None:
                print("ftpclient")
                self._ftpclient = self.executor.sshclient.getSFTP()
            return self._ftpclient
        else:
            raise RuntimeError("node %s cannot be reached, cannot get ftpclient." % self.instance)

    @property
    def executor(self):
        if self.isconnected:
            return j.tools.executor.get("%s:%s" % (self.addr, self.port))
        else:
            raise RuntimeError("node %s cannot be reached, cannot get executor." % self.instance)

    @property
    def prefab(self):
        if self.isconnected:
            return j.tools.prefab.get(executor=self.executor)
        else:
            raise RuntimeError("node %s cannot be reached, cannot get prefab." % self.instance)

    def clean(self):
        cmd = """
        rm -f ~/.profile_js
        rm -f ~/env.sh
        rm -f rm /etc/jumpscale9.toml     
        """
        self.executor.execute(cmd)

    def test_executor(self):
        self.executor.test()

    def sync(self):
        ddirs = j.tools.develop.codedirs.getActiveCodeDirs()
        for ddir in ddirs:
            source = ddir.path
            dest = "%s/%s/%s" % (
                self.prefab.executor.dir_paths["CODEDIR"], ddir.type, ddir.account)
            self.prefab.executor.upload(
                source, dest, dest_prefix='', recursive=True, createdir=True)

    def saveToHostfile(self):
        j.tools.prefab.local.system.ns.hostfile_set(self.name, self.addr)

    def save(self):
        self.config.save()

    def ssh(self):
        cmd = "ssh root@%s -p %s" % (self.addr, self.port)
        j.sal.process.executeInteractive(cmd)

    def __str__(self):
        if self.selected is True:
            return "%-14s %-25s:%-4s [%s] *" % (self.name, self.addr, self.port, self.category)
        else:
            return "%-14s %-25s:%-4s [%s]" % (self.name, self.addr, self.port, self.category)

    __repr__ = __str__
