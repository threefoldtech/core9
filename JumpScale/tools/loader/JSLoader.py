from JumpScale import j
# import os


class JSLoader():

    def __init__(self):
        self.logger = j.logger.get("jsloader")

    def findJumpscaleLocationsInFile(self, path):
        res = []
        C = j.sal.fs.readFile(path)
        classname = None
        for line in C.split("\n"):
            if line.startswith("class "):
                classname = line.replace("class ", "").split(
                    ":")[0].split("(", 1)[0].strip()
            if line.find("self.__jslocation__") != -1:
                if classname is None:
                    raise RuntimeError(
                        "Could not find class in %s while loading jumpscale lib." % path)
                location = line.split("=", 1)[1].replace(
                    "\"", "").replace("'", "").strip()
                if location.find("self.__jslocation__") == -1:
                    res.append((classname, location))
        return res

    # import json

    def findModules(self, path=""):
        """
        walk over code files & find locations for jumpscale modules

        return as dict
        """
        if path == "":
            path = j.sal.fs.getParent(j.sal.fs.getDirName(j.sal.fs.getPathOfRunningFunction(j.application.__init__)))

        result = {}

        self.logger.info("findmodules in %s" % path)

        for classfile in j.sal.fs.listPyScriptsInDir(path):
            basename = j.do.getBaseName(classfile)
            if basename.startswith("_"):
                continue
            # look for files starting with Capital
            if str(basename[0]) != str(basename[0].upper()):
                continue

            for (classname, location) in self.findJumpscaleLocationsInFile(classfile):
                if classname is not None:
                    loc = ".".join(location.split(".")[:-1])
                    item = location.split(".")[-1]
                    if loc not in result:
                        result[loc] = []
                    result[loc].append((classfile, classname, item))
