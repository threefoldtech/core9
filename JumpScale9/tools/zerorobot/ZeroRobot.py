
from js9 import j
import os


class ZeroRobot:

    def __init__(self):
        self.__jslocation__ = "j.tools.zerorobot"
        self._models=None
        self._tarantool=None
        self._templates=None

    @property
    def templates(self):
        if self._templates==None:
            from .ZeroTemplates import ZeroTemplates
            self._templates=ZeroTemplates()
        return self._templates

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))

    @property
    def tarantool(self):
        if self._tarantool==None:
            self._tarantool = j.clients.tarantool.client_get()
        return self._tarantool

    @property
    def models(self):
        if self._models==None:
            self.tarantool.addModels(self._path+"models") 
            self._models= self.tarantool.models
        return self._models

    def test(self):
        self.templates.load() #will load all templates it can find
        from IPython import embed;embed(colors='Linux')
        

