from js9 import j

from .CodeDirs import CodeDirs
from .Nodes import Nodes
from .MyFileSystemEventHandler import MyFileSystemEventHandler
from watchdog.observers import Observer

import time

class DevelopToolsFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.develop"
        self.__imports__ = "watchdog"
        self._nodes = None
        self._codedirs = None

    def run(self):
        from .DevelopConfig import ConfigUI
        app = ConfigUI()
        app.run()

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
        for node in self.nodes.nodesGet():
            if node.selected:
                node.sync()

    def monitor(self):
        """
        look for changes in directories which are being pushed & if found push to remote nodes
        """
        # self.sync()
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
        