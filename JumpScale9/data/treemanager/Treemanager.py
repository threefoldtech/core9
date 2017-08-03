from js9 import j


class TreeItem():

    def __init__(self):
        self.id = ""
        self.description = ""
        self.path = ""
        self.item = None
        self.changed = False
        self.tree = None
        self.cat = None

    @property
    def parent(self):
        if "." in self.path:
            pathParent = ".".join(self.path.split(".")[:-1])
            return self.tree.items[pathParent]

    @property
    def name(self):
        return self.path.split(".")[-1]

    @property
    def children(self):
        r = []
        depth = self.path.count(".")
        for key, val in self.tree.items.items():
            if key.startswith(self.path):
                depth2 = val.path.count(".")
                if depth2 == depth + 1:
                    r.append(val)
        return r

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return ("treeitem %s:%s" % (self.path, self.cat))


class Tree():

    def __init__(self):
        self.items = {}
        self.changed = False
        self.set("")  # will set the root

    @property
    def children(self):
        return self.items[""].children

    def _pathNormalize(self, path):
        path = path.lower()
        path = path.strip()
        return path

    def exists(self, path):
        path = self._pathNormalize(path)
        return path in self.items

    def set(self, path, id=None, cat=None, description=None, item=None):

        path = self._pathNormalize(path)
        if path not in self.items:
            self.items[path] = TreeItem()

        ti = self.items[path]

        if path == "":
            self.root = ti

        if id is not None and ti.id != id:
            ti.id = id
            ti.changed = True
        if description is not None and ti.description != description:
            ti.description = description
            ti.changed = True
        if item is not None and ti.item != item:
            ti.item = item
            ti.changed = True
        if cat is not None and ti.cat != cat:
            ti.cat = cat
            ti.changed = True

        ti.path = path
        ti.tree = self

        if ti.changed:
            self.changed = True

    def dumps(self):
        r = []
        for key, val in self.items.items():
            cat = val.cat or ""
            id = val.id or ""
            description = val.description or ""
            line = "%s : %s : %s : %s" % (val.path, cat, id, description)
            r.append(line)
        r.sort()

        out = ""
        for line in r:
            out += "%s\n" % line

        return out

    def loads(self, data):
        lines = [line for line in data.split("\n") if line.strip() is not "" and not line.strip().startswith("#")]
        lines.sort()
        self.items = {}
        for line in lines:
            path, cat, id, descr = line.split(":")
            path = path.strip()

            id = id.strip()
            if id == "":
                id = None

            cat = cat.strip()
            if cat == "":
                cat = None

            descr = descr.strip()
            if descr == "":
                descr = None
            if cat == "":
                cat = None
            self.set(path=path, id=id, cat=cat, description=descr, item=None)

    def find(self, partOfPath, maxAmount=200, getItems=False):
        """
        @param if getItems True then will return the items in the treeobj
        """
        r = []
        for key in self.items.keys():
            if key.find(partOfPath) != -1:
                r.append(self.items[key])

        if len(r) == 0:
            raise j.exceptions.Input("could not find %s in %s" % (partOfPath, self))

        if len(r) > maxAmount:
            raise j.exceptions.Input("found more than %s %s in %s" % (maxAmount, partOfPath, self))

        if getItems:
            r = [item.item for item in r if item.item is not None]

        return r

    def findOne(self, partOfPath, getItems=False):
        return self.find(partOfPath, maxAmount=1, getItems=getItems)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return (self.dumps())


class TreemanagerFactory:

    def __init__(self):
        self.__jslocation__ = "j.data.treemanager"

    def get(self):
        return Tree()
