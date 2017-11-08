from js9 import j
from .TarantoolDB import TarantoolDB
from .TarantoolClient import TarantoolClient
import tarantool
import os
# import itertools


# import sys
# sys.path.append(".")
# from tarantool_queue import *



class TarantoolFactory:

    """
    #server_start
    js9 'j.clients.tarantool.server_start()'

    #start test
    js9 'j.clients.tarantool.test()'

    """

    def __init__(self):
        self.__jslocation__ = "j.clients.tarantool"
        self.__imports__ = "tarantool"
        if j.core.platformtype.myplatform.isMac:
            self.cfgdir = "/usr/local/etc/tarantool/instances.enabled"
        else:
            self.cfgdir = "/etc/tarantool/instances.enabled"
        self._tarantool = {}
        self._tarantoolq = {}

    def install(self, start=True):
        j.tools.prefab.local.db.tarantool.install()
        if start:
            self.start()

    def client_configure(self,name="main",ipaddr="localhost", port=3301, login="root", password="admin007"):
        cfg=j.core.state.clientConfigGet("tarantool",name)
        cfg.data["ipaddr"]=ipaddr
        cfg.data["port"]=port
        cfg.data["login"]=login
        cfg.data["password"]=password
        cfg.save()

    def client_get(self, name="main", fromcache=True):
        cfg=j.core.state.clientConfigGet("tarantool",name=name)
        if "ipaddr" not in cfg.data.keys():
            self.client_configure()
            cfg=j.core.state.clientConfigGet("tarantool",name=name)
        cfg=cfg.data
        key = "%s_%s" % (cfg["ipaddr"], cfg["port"])
        if key not in self._tarantool or fromcache is False:
            client= tarantool.connect(
                cfg["ipaddr"], user=cfg["login"], port=cfg["port"], password=cfg["password"])
            self._tarantool[key]=TarantoolClient(client=client)
        return self._tarantool[key]

    def server_get(self, name="main", path="$DATADIR/tarantool/$NAME", adminsecret="admin007", port=3301):
        return TarantoolDB(name=name, path=path, adminsecret=adminsecret, port=port)

    def server_start(self, name="main", path="$DATADIR/tarantool/$NAME", adminsecret="admin007", port=3301, configTemplatePath=None):
        db = self.server_get(name=name, path=path,
                            adminsecret=adminsecret, port=port)
        db.configTemplatePath = configTemplatePath
        db.start()



    def testmodels(self):

        #remove the generated code
        todel=j.sal.fs.getDirName(os.path.abspath(__file__))+"models/user/"
        j.sal.fs.remove(todel+"/model.lua")
        j.sal.fs.remove(todel+"/UserCollection.py")

        tt = self.client_get()
        tt.addScripts() #will add the system scripts
        tt.addModels()

        for i in range(1):
            d=tt.models.UserCollection.new()
            d.dbobj.name="name_%s"%i
            d.dbobj.description="this is some description %s"%i
            d.dbobj.region=10
            d.dbobj.epoch=j.data.time.getTimeEpoch()
            d.save()

        # print("list of users")
        # print(tt.models.UserCollection.list())

        # from IPython import embed;embed(colors='Linux')

    def test(self):
        C = """
        function echo3(name)
          return name
        end
        """
        tt = self.client_get()
        tt.eval(C)
        print("return:%s" % tt.call("echo3", "testecho"))


        capnpSchema="""
        @0x9a7562d859cc7ffa;

        struct User {
        id @0 :UInt32;
        name @1 :Text;
        }

        """
        lpath=j.dirs.TMPDIR+"/test.capnp"
        j.sal.fs.writeFile(lpath,capnpSchema)

        res=j.data.capnp.schema_generate_lua(lpath)



        # tt.scripts_execute()
        print(test)
        from IPython import embed
        embed(colors='Linux')
