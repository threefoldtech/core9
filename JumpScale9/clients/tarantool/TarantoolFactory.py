from js9 import j
from .TarantoolDB import TarantoolDB
from .TarantoolClient import TarantoolClient
import tarantool

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

    def client_get(self, ipaddr="localhost", port=3301, login="root", password="admin007", fromcache=True):
        key = "%s_%s" % (ipaddr, port)
        if key not in self._tarantool or fromcache is False:
            client=        tarantool.connect(
                ipaddr, user=login, port=port, password=password)
            self._tarantool[key]=TarantoolClient(client=client)
        return self._tarantool[key]

    def server_get(self, name="test", path="$DATADIR/tarantool/$NAME", adminsecret="admin007", port=3301):
        return TarantoolDB(name=name, path=path, adminsecret=adminsecret, port=port)

    def server_start(self, name="test", path="$DATADIR/tarantool/$NAME", adminsecret="admin007", port=3301, configTemplatePath=None):
        db = self.server_get(name=name, path=path,
                            adminsecret=adminsecret, port=port)
        db.configTemplatePath = configTemplatePath
        db.start()

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
        

        tt.scripts_execute()

        from IPython import embed
        embed(colors='Linux')
