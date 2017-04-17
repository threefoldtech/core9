

class Sal():
    def __init__(self):
        pass


class Tools():
    def __init__(self):
        pass


class Data():
    def __init__(self):
        pass


class Clients():
    def __init__(self):
        pass


class Core():
    def __init__(self):
        pass


class Jumpscale9():

    def __init__(self):
        self.tools = Tools()
        self.sal = Sal()
        self.data = Data()
        self.clients = Clients()
        self.core = Core()


j = Jumpscale9()

from .data.text.Text import Text
j.data.text = Text()

from .data.types.Types import Types
j.data.types = Types()

from .logging.LoggerFactory import LoggerFactory
j.logger = LoggerFactory()
j.logger.enableConsoleHandler()

from .fs.SystemFS import SystemFS
j.sal.fs = SystemFS()

from .tools.process.SystemProcess import SystemProcess
j.sal.process = SystemProcess()

from .tools.executor.ExecutorLocal import ExecutorLocal
j.tools.executorLocal = ExecutorLocal()  # needed in platformtypes

from .core.PlatformTypes import PlatformTypes
j.core.platformtype = PlatformTypes()

from .data.cache.Cache import Cache
j.data.cache = Cache()

from .clients.redis.RedisFactory import RedisFactory
j.clients.redis = RedisFactory()

from .core.State import State
j.core.state = State()

from .core.InstallTools import InstallTools
j.do = InstallTools()

from .core.Dirs import Dirs
j.dirs = Dirs()

from .data.idgenerator.IDGenerator import IDGenerator
j.data.idgenerator = IDGenerator()

from .data.time.Time import Time_
j.data.time = Time_()

from .errorhandling.ErrorConditionHandler import ErrorConditionHandler
j.errorhandler = ErrorConditionHandler()


from .core.Application import Application
j.application = Application()

j.logger.set_mode("DEV")

from .fs.SystemFSWalker import SystemFSWalker
j.sal.fswalker = SystemFSWalker

from .tools.loader.JSLoader import JSLoader
j.tools.jsloader = JSLoader()

j.logger.init()


if "dirs" not in j.core.state.config:
    j.do.initEnv()

# logger = j.logger.get("init")
# logger.debug("Init Done")
