from js9 import j

from .Node import Node


JSConfigBase = j.tools.configmanager.base_class_configs


class Nodes(JSConfigBase):

    def __init__(self):
        self.__jslocation__ = "j.tools.nodemgr"
        JSConfigBase.__init__(self, Node)
        self._tree = None

    @property
    def tree(self):
        if self._tree==None:
            self._tree = j.data.treemanager.get()
        return self._tree

    def nodesGet(self):
        res = []
        print("nodes get")
        from IPython import embed;embed(colors='Linux')
        return res

    def nodeGet(self, name, die=True):
        res = self.nodesGet()
        res = [item for item in res if item.name == name]
        if len(res) == 0:
            if die is False:
                return None
            raise j.exceptions.Input("did not find node: %s" % (name))
        if len(res) > 1:
            raise j.exceptions.Input("found more than 1 node: %s" % (name))
        return res[0]

    def nodeExists(self, name):
        res = self.nodesGet()
        res = [item for item in res if item.name == name]
        if len(res) == 0:
            return False
        if len(res) > 1:
            raise j.exceptions.Input("found more than 1 node: %s" % (name))
        return True

    def nodeSet(self, name, addr, port=22, cat="", description="", selected=False,active=True):

        print("nodeset")
        data={}
        data["addr"]=addr
        data["name"]=name
        data["port"]=port
        data["active"]=active
        data["selected"]=selected
        data["category"]=cat
        data["description"]=description
        n=j.tools.nodemgr.get(instance=name,data=data)
        n.config.save()
        
        if self.nodeExists(name):
            tpath = self.tree.findByName(name).path
            self.tree.items.pop(tpath)

        if cat == "":
            path = "all.%s" % name
        else:
            path = "%s.%s" % (cat, name)
        self.tree.set(path=path, data="%s|%s" % (addr, port),
                      description=description, cat=cat, selected=selected)


        node = self.nodeGet(name)

        return node

    def save(self):
        j.sal.fs.writeFile(self.configpath, str(self))

    def test(self):

        for i in range(10):
            self.nodeSet("myhost%s"%i,"127.0.0.%s"%i,22,cat="testcat")
        
        assert self.nodeExists("myhost1") == True

        assert len(self.nodesGet())==10

        for i in range(5):
            self.nodeSet("myhostcat2_%s"%i,"127.0.0.%s"%i,22,cat="cat2")

        from IPython import embed;embed(colors='Linux')


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # return ("%s"%self.tree)
        out = ""
        for item in self.nodesGet():
            out += str(item) + "\n"
        return out