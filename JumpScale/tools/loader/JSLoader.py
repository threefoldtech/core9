from JumpScale import j
# import os
import sys

corepackages = """
j.core.platformtype
j.core.state
j.sal.fs
j.sal.process
j.sal.fswalker
j.tools.executorLocal
j.tools.jsloader
j.tools.tmux
j.data.serializer
j.data.text
j.data.tags
j.data.idgenerator
j.data.time
j.data.types
j.clients.redis
j.clients.git
j.clients.email
j.core.dirs
j.core.application
j.logger
j.errorconditionhandler
"""

GEN_START = """
from JumpScale.core.JSBase import JSBase

"""

GEN = """
{{#location}}
from {{importlocation}} import {{classname}}
{{/location}}

{{#locationerr}}
{{classname}}=JSBase
{{/locationerr}}

class {{jname}}:
    {{#location}}
    {{name}} = {{classname}}()
    {{/location}}

"""

GEN_END = """

class Jumpscale9():

    def __init__(self):
        {{#locations}}
            self.{{name}}={{name}}()
        {{/locations}}

j = Jumpscale9()
j.logger=j.core.logger
j.application=j.core.application

"""

import pystache


class JSLoader():

    def __init__(self):
        self.logger = j.logger.get("jsloader")
        self.autopip = j.application.config["system"].get("autopip") == True
        self.__jslocation__ = "j.tools.jsloader"

    def _installDevelopmentEnv(self):

        cmd = "apk add gcc"
        # apt-get install python3-dev
        from IPython import embed
        print("DEBUG NOW _installDevelopmentEnv")
        embed()
        raise RuntimeError("stop debug here")

    def _pip(self, item):
        rc, out, err = j.sal.process.execute("pip3 install %s" % item, die=False)
        if rc > 0:
            if "command 'gcc' failed" in out:
                if self.coreOnly:
                    # will not install dependencies which rely on development env
                    return 1
                self._installDevelopmentEnv()
                rc, out, err = j.sal.process.execute("pip3 install %s" % item, die=False)
        if rc > 0:
            print("WARNING: COULD NOT PIP INSTALL:%s\n\n" % item)
        return rc

    def generate(self, path="", out=""):
        basedir = j.sal.fs.getParent(j.sal.fs.getDirName(j.sal.fs.getPathOfRunningFunction(j.application.__init__)))
        if out == "":
            out = basedir + "/init.py"

        content = GEN_START

        jlocations = {}
        jlocations["locations"] = []

        res = self.findModules(path=path)
        for jlocation, items in res.items():
            if jlocation.strip() in ["", "j"]:
                continue
            res2 = {}
            res2["location"] = []
            res2["locationerr"] = []
            jname = jlocation.split(".")[1]
            res2["jname"] = jname
            toadd = {"name": jname}
            if toadd not in jlocations["locations"]:
                jlocations["locations"].append(toadd)
            res2["jlocation"] = jlocation

            for classfile, classname, item, importItems in items:
                res3 = {}
                res3["classname"] = classname
                res3["name"] = item
                importlocation = "JumpScale." + j.sal.fs.pathRemoveDirPart(classfile, basedir).replace("/", ".")[: -3]
                res3["importlocation"] = importlocation

                try:
                    exec("from %s import %s" % (importlocation, classname))
                    res2["location"].append(res3)
                except Exception as e:
                    print("import error:\n%s\n" % e)
                    if not self.autopip:
                        continue
                    if importItems == []:
                        print("\n\nCOULD NOT IMPORT:%s\n" % importlocation)
                        # print("ERROR:\n%s\n" % e)
                        # sys.exit(1)
                        exec("from %s import %s" % (importlocation, classname))
                        # imports ok so can add
                        res2["location"].append(res3)
                    else:
                        for item in importItems:
                            if j.application.config["system"]["debug"]:
                                rc, out, err = j.sal.process.execute("pip3 show %s" % item, die=False)
                                if out != "":
                                    exec("from %s import %s" % (importlocation, classname))
                                else:
                                    rc = self._pip(item)
                                    if rc > 0:
                                        if res3 not in res2["locationerr"]:
                                            res2["locationerr"].append(res3)
                                    else:
                                        print("pip install ok")
                                        if res3 not in res2["location"]:
                                            res2["location"].append(res3)
                            else:
                                if res3 not in res2["locationerr"]:
                                    res2["locationerr"].append(res3)

            content += pystache.render(GEN, **res2)

        content += pystache.render(GEN_END, **jlocations)
        j.sal.fs.writeFile(filename=out, contents=content)

    def findJumpscaleLocationsInFile(self, path):
        res = {}
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
                    if classname not in res:
                        res[classname] = {}
                    res[classname]["location"] = location
            if line.find("self.__imports__") != -1:
                if classname is None:
                    raise RuntimeError(
                        "Could not find class in %s while loading jumpscale lib." % path)
                importItems = line.split("=", 1)[1].replace("\"", "").replace("'", "").strip()
                importItems = [item.strip() for item in importItems.split(",") if item.strip() != ""]
                if classname not in res:
                    res[classname] = {}
                res[classname]["import"] = importItems
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

        for classfile in j.sal.fs.listFilesInDir(path, True, "*.py"):
            # print(classfile)
            basename = j.do.getBaseName(classfile)
            if basename.startswith("_"):
                continue
            # look for files starting with Capital
            if str(basename[0]) != str(basename[0].upper()):
                continue

            for classname, item in self.findJumpscaleLocationsInFile(classfile).items():
                if "location" in item:
                    location = item["location"]
                    if "import" in item:
                        importItems = item["import"]
                    else:
                        importItems = []

                    loc = ".".join(location.split(".")[:-1])
                    item = location.split(".")[-1]
                    if loc not in result:
                        result[loc] = []
                    result[loc].append((classfile, classname, item, importItems))

        return result
