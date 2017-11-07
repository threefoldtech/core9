from js9 import j
import tarantool
import os


class TarantoolClient():

    def __init__(self,client):
        self.db = client
        self.call = client.call

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))
        

    # def addSpace(self):
    #     C = "s = box.schema.space.create('tester',{if_not_exists = true})"

    def getQueue(self, name, ttl=0, delay=0):
        return TarantoolQueue(self, name, ttl=ttl, delay=delay)

    def eval(self, code):
        code = j.data.text.strip(code)
        self.db.eval(code)

    def userGrant(self, user="guest", operation=1, objtype="universe", objname=""):
        """
        @param objtype the type of object - "space" or "function" or "universe",
        @param objname the name of object only relevant for space or function
        @param opstype in integer the type of operation - "read" = 1, or "write" = 2, or "execute" = 4, or a combination such as "read,write,execute".
        """
        if objname == "":
            C = "box.schema.user.grant('%s',%s,'%s')" % (
                user, operation, objtype)
        else:
            C = "box.schema.user.grant('%s',%s,'%s','%s')" % (
                user, operation, objtype, objname)

        self.db.eval(C)

    def addFunction(self, code=""):
        """
        example:
            function echo3(name)
              return name
            end

        then use with self.call...
        """
        self.eval(code)


    def addModels(self,path="",login="user",passwd="secret",dbtype="memtx"):
        """
        @PARAM path is the directory where the capnp, lua, ... can be found, each subdir has a model name
               if not specified will look for models underneith the capnp extension
        @PARAM dbtype vinyl or memtx
        """

        FGRANT = """
        box.schema.func.create('write', {if_not_exists = true})
        box.schema.user.grant('$login', '$fname', 'function', 'write',{ if_not_exists= true})
        """
        C=C.replace("$login",login)
        C=C.replace("$fname",fname)
        C=C.replace("$mymodelname",mname)

        C=C.replace("$login",login)
        C=C.replace("$passwd",passwd)
        

    # def bootstrap(self, code):
    #     code = """
    #         box.once("bootstrap", function()
    #             box.schema.space.create('$space')
    #             box.space.test:create_index('primary',
    #                 { type = 'TREE', parts = {1, 'NUM'}})
    #         end)
    #         box.schema.user.grant('$user', 'read,write,execute', 'universe')
    #         """
    #     code = code.replace("$space", space)
    #     self.eval(code)

    def addScripts(self,path=None):
        """
        load all lua scripts in path (sorted) & execute in the tarantool instance

        if @path empty then path = testscripts subdir of this extension
        """
        if path==None:
            path="%s/testscripts"%self._path
        for path0 in j.sal.fs.listFilesInDir(path, recursive=False, filter="*.lua"):
            self.addScript(path0)

    def addScript(self,path):
        C=j.sal.fs.readFile(path0)
        bname=j.sal.fs.getBaseName(path0)[:-4]
        #write the lua script to the location on server
        self.db.call("add_lua_script",(bname,C))
        self.eval("require('%s')"%(bname))
    