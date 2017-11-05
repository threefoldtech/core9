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

    def bootstrap(self, code):
        code = """
            box.once("bootstrap", function()
                box.schema.space.create('$space')
                box.space.test:create_index('primary',
                    { type = 'TREE', parts = {1, 'NUM'}})
            end)
            box.schema.user.grant('$user', 'read,write,execute', 'universe')
            """
        code = code.replace("$space", space)
        self.eval(code)

    def scripts_execute(self,path=None):
        """
        load all lua scripts in path (sorted) & execute in the tarantool instance

        if @path empty then path = testscripts subdir of this extension
        """
        if path==None:
            path="%s/testscripts"%self._path
        from IPython import embed;embed(colors='Linux')
