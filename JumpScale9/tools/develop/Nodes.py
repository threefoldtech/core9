from js9 import j

from .Node import Node


class Nodes():
    def __init__(self):
        self.load()

    @property
    def configpath(self):
        path = j.sal.fs.joinPaths(j.core.state.cfgPath, "nodes.cfg")
        if not j.sal.fs.exists(path):
            j.sal.fs.touch(path)
        return path

    def load(self, data=""):
        if data == "":
            data = j.sal.fs.readFile(self.configpath)
        self.tree = j.data.treemanager.get()
        self.loadFromText(data)

    def nodesGet(self):
        res = []
        for item in j.tools.develop.nodes.tree.find():
            if item.name == "":
                continue
            addr, port = item.data.split("|")
            addr = addr.strip()
            port = int(port.strip())
            node = Node(name=item.name, addr=addr, port=port,
                        description=item.description, cat=item.cat, selected=item.selected)
            res.append(node)
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

    def nodeSet(self, name, addr, port=22, cat="", description="", selected=None):
        if self.nodeExists(name):
            tpath = self.tree.findByName(name).path
            self.tree.items.pop(tpath)
        self._nodeSet(name=name, addr=addr, port=port, cat=cat,
                      description=description, selected=selected)
        node = self.nodeGet(name)
        self.save()
        return node

    def _nodeSet(self, name, addr, port=22, cat="", description="", selected=None):
        if cat == "":
            path = "all.%s" % name
        else:
            path = "%s.%s" % (cat, name)
        self.tree.set(path=path, data="%s|%s" % (addr, port),
                      description=description, cat=cat, selected=selected)

    def save(self):
        j.sal.fs.writeFile(self.configpath, str(self))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # return ("%s"%self.tree)
        out = ""
        for item in self.nodesGet():
            out += str(item) + "\n"
        return out

    def loadFromText(self, data):
        """
        format is:

            test localhost:22 [mycat]
            test2 localhost:24 [mycat2]
            test3 localhost [mycat]

            test4 localhost
            test5 localhost:8000
            test5 localhost:8001


        """
        for line in data.split("\n"):

            if line.strip() == "" or line.startswith("#"):
                continue

            line = line.strip()

            name, line = line.split(" ", 1)
            name = name.lower().strip()
            line = line.strip()

            selected = None
            if "*" in line:
                selected = True
                line = line.replace("*", "")

            if "#" in line:
                line, remark = line.split("#", 1)
                remark = remark.strip()
            else:
                remark = ""

            if "[" in line:
                line, remain = line.split("[", 1)
                cat = remain.split("]", 1)[0]
            else:
                cat = "all"

            if ":" in line:
                addr, port = line.split(":")
                addr = addr.strip()
                port = port.strip()
            else:
                addr = line.strip()
                port = "22"

            self._nodeSet(name, addr=addr, port=port,
                          cat=cat, selected=selected)

    def _test(self):
        text = """
        test localhost:22 [mycat ]
        test2 localhost:24 [mycat2]
        test3 localhost [mycat ] *

        test4 localhost
        test5 localhost:8000
        test5 localhost:8001

        """
        self.loadFromText(text)
        print(self)

        assert len(self.nodesGet()) == 5

        assert self.nodeGet("test2").name == "test2"

        data = self.tree.dumps()
        self.load(data)

        assert len(self.nodesGet()) == 5

        assert self.nodeGet("test2").name == "test2"
