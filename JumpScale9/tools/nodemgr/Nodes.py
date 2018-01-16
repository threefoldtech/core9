from js9 import j

from .Node import Node


JSConfigBase = j.tools.configmanager.base_class_configs


class Nodes(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.tools.nodemgr"
        JSConfigBase.__init__(self, Node)
        self._tree = None
        res = self.getall()
        for item in res:
            self._add2tree(item)

    @property
    def tree(self):
        if self._tree is None:
            self._tree = j.data.treemanager.get()
        return self._tree

    def set(self, name, addr, port=22, cat="", description="", selected=False, active=True, clienttype="", secretconfig="", pubconfig=""):

        secretconfig = j.data.serializer.json.dumps(secretconfig)
        pubconfig = j.data.serializer.json.dumps(pubconfig)

        data = {}
        data["addr"] = addr
        data["name"] = name
        data["port"] = port
        data["active"] = active
        data["selected"] = selected
        data["clienttype"] = clienttype
        data["secretconfig_"] = secretconfig
        data["pubconfig"] = pubconfig
        data["category"] = cat
        data["description"] = description
        n = self.get(instance=name, data=data, create=True)
        n.config.save()

        print("nodeset:%s" % n)

        if self.exists(name):
            treeitem = self.tree.findByName(name, die=False)
            if treeitem != None:
                tpath = treeitem.path
                self.tree.items.pop(tpath)

        self._add2tree(n)

    def _add2tree(self, n):

        if n.category == "":
            path = "all.%s" % n.name
        else:
            path = "%s.%s" % (n.category, n.name)

        self.tree.set(path=path, data="%s|%s|%s" % (n.name, n.addr, n.port),
                      description=n.description, cat=n.category, selected=n.selected)

    def test(self):
        """
        js9 'j.tools.nodemgr.test()'
        """

        self.delete(prefix="myhost")

        startnr = len(self.getall())
        assert self.count() == startnr

        assert self.exists("myhost1") is False

        for i in range(10):
            self.set("myhost%s" % i, "127.0.0.%s" % i, 22, cat="testcat")

        assert self.exists("myhost1") == True

        assert len(self.getall()) == 10 + startnr

        for i in range(5):
            self.set("myhostcat2_%s" % i, "127.0.0.%s" % i, 22, cat="cat2")

        n = self.get("myhost9")
        d2 = {'active': True,
              'addr': '127.0.0.9',
              'category': 'testcat',
              'clienttype': '',
              'description': '',
              'name': 'myhost9',
              'port': 22,
              'secretconfig_': '',
              'selected': False}

        assert n.config.data == d2
        j.data.serializer.toml.fancydumps(
            n.config.data) == j.data.serializer.toml.fancydumps(d2)

        print(self)

        n.selected = True
        assert n.selected == n.config.data["selected"]
        n.selected = False
        n.config.data["selected"] = False
        assert n.selected == n.config.data["selected"]
        assert n.selected == False
        assert n.config.data["selected"] == False
        n.selected = True
        assert n.config.data["selected"] == True

        # TODO: *3 need more tests

        assert len(self.list(prefix="myhost")) == 15 + startnr

        # cleanup
        self.delete(prefix="myhost")

        assert len(self.getall()) == startnr

        print("TEST for nodes ok")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # return ("%s"%self.tree)
        out = ""
        for item in self.getall():
            out += str(item) + "\n"
        return out
