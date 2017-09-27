from js9 import j

from .CodeDirs import CodeDirs
from .Nodes import Nodes
from .MyFileSystemEventHandler import MyFileSystemEventHandler
from watchdog.observers import Observer

import time
import pytoml

class DevelopToolsFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.develop"
        self.__imports__ = "watchdog"
        self._nodes = None
        self._codedirs = None

    def run(self):
        from .DevelopConfig import ConfigUI
        # self.dockerconfig()
        app = ConfigUI()
        app.run()

    @property
    def iscontainer(self):
        return j.sal.fs.exists("%s/.iscontainer"%j.dirs.HOMEDIR)


    # def dockerconfig(self):
    #     if self.iscontainer:
    #         if not j.sal.fs.exists("/hostcfg/me.toml"):
    #             j.tools.executorLocal.initEnv()
    #         cfg=pytoml.loads(j.sal.fs.readFile("/hostcfg/me.toml"))
    #         j.core.state.configSet("me",cfg["me"])
    #         j.core.state.configSet("email",cfg["email"])    
    #     else:
    #         cpath=j.dirs.HOMEDIR+"/.cfg/me.toml"
    #         if  j.sal.fs.exists(j.dirs.HOMEDIR+"/.cfg"):
    #             if not j.sal.fs.exists(cpath):  
    #                 cfgnew={}
    #                 cfgnew["email"]=j.core.state.config["email"]
    #                 cfgnew["me"]=j.core.state.config["me"]
    #                 txt=pytoml.dumps(cfgnew,True)                    
    #                 j.sal.fs.writeFile(cpath,txt)
    #             keyname=j.core.state.config["ssh"]["sshkeyname"]
    #             spath=j.dirs.HOMEDIR+"/.ssh/%s.pub"%keyname
    #             dpath=j.dirs.HOMEDIR+"/.cfg/ssh_%s.pub"%keyname.lower()
    #             if j.sal.fs.exists(spath):
    #                 j.sal.fs.copyFile(spath,dpath)

    @property
    def codedirs(self):
        if self._codedirs is None:
            self._codedirs = CodeDirs()
        return self._codedirs

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = Nodes()
        return self._nodes


    def help(self):

        H = """
        j.tools.develop.run()
        """
        print(H)




    # def resetState(self):
    #     j.actions.setRunId("developtools")
    #     j.actions.reset()
    #     self.init()

    def sync(self):
        """
        sync all code to the remote destinations, uses config as set in jumpscale.toml


        """
        if  self.nodes.nodesGet()==[]:
            print ("NOTHING TO DO, THERE ARE NO NODES DEFINED PLEASE USE  j.tools.develop.run()")
            return
        did=False
        for node in self.nodes.nodesGet():
            if node.selected:
                node.sync()
                did=True
        if did==False:
            print("nodes are defined but not selected, please use j.tools.develop.run()")

    def monitor(self):
        """
        look for changes in directories which are being pushed & if found push to remote nodes
        """

        self.sync()
        
        event_handler = MyFileSystemEventHandler()
        observer = Observer()
        codepaths=j.tools.develop.codedirs.getActiveCodeDirs()
        for source in codepaths:
            print("monitor:%s" % source)
            observer.schedule(event_handler, source.path, recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass



    def test_executor(self):
        for node in self.nodes.nodesGet():
            if node.selected:
                node.test_executor()

    def clean(self):
        for node in self.nodes.nodesGet():
            if node.selected:
                node.clean()
                

    def test_js9_quick(self):
        j.data.kvs.test()
        j.data.cache.test()

    
        