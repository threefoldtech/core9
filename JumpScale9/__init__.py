

class Sal:

    def __init__(self):
        self.__fs = None
        self.__process = None
        self.__fswalker = None

    @property
    def fs(self):
        from JumpScale9.fs.SystemFS import SystemFS
        if self.__fs is None:
            self.__fs = SystemFS()
        return self.__fs

    @property
    def process(self):
        from JumpScale9.tools.process.SystemProcess import SystemProcess
        if self.__process is None:
            self.__process = SystemProcess()
        return self.__process

    @property
    def fswalker(self):
        from JumpScale9.fs.SystemFSWalker import SystemFSWalker
        if self.__fswalker is None:
            self.__fswalker = SystemFSWalker
        return self.__fswalker


class Tools:

    def __init__(self):
        self.__executorLocal = None
        self.__jsloader = None
        self.__tmux = None

    @property
    def executorLocal(self):
        if self.__executorLocal is None:
            from JumpScale9.tools.executor.ExecutorLocal import ExecutorLocal
            self.__executorLocal = ExecutorLocal()  # needed in platformtypes
        return self.__executorLocal

    @property
    def jsloader(self):
        if self.__jsloader is None:
            from JumpScale9.tools.loader.JSLoader import JSLoader
            self.__jsloader = JSLoader()
        return self.__jsloader

    @property
    def tmux(self):
        if self.__tmux is None:
            from JumpScale9.tools.tmux.Tmux import Tmux
            self.__tmux = Tmux()
        return self.__tmux


class Data:

    def __init__(self):
        self.__serializer = None
        self.__text = None
        self.__types = None
        self.__cache = None
        self.__idgenerator = None
        self.__time = None

    @property
    def serializer(self):
        if self.__serializer is None:
            from JumpScale9.data.serializers.SerializersFactory import SerializersFactory
            self.__serializer = SerializersFactory()
        return self.__serializer

    @property
    def text(self):
        if self.__text is None:
            from JumpScale9.data.text.Text import Text
            self.__text = Text()
        return self.__text

    @property
    def types(self):
        if self.__types is None:
            from JumpScale9.data.types.Types import Types
            self.__types = Types()
        return self.__types

    @property
    def cache(self):
        if self.__cache is None:
            from JumpScale9.data.cache.Cache import Cache
            self.__cache = Cache()
        return self.__cache

    @property
    def idgenerator(self):
        if self.__idgenerator is None:
            from JumpScale9.data.idgenerator.IDGenerator import IDGenerator
            self.__idgenerator = IDGenerator()
        return self.__idgenerator

    @property
    def time(self):
        if self.__time is None:
            from JumpScale9.data.time.Time import Time
            self.__time = Time()
        return self.__time


class Clients:

    def __init__(self):
        self.__redis = None

    @property
    def redis(self):
        if self.__redis is None:
            from JumpScale9.clients.redis.RedisFactory import RedisFactory
            self.__redis = RedisFactory()
        return self.__redis


class Core:

    def __init__(self):
        self.__platformtype = None
        self.__state = None

    @property
    def platformtype(self):
        if self.__platformtype is None:
            from JumpScale9.core.PlatformTypes import PlatformTypes
            self.__platformtype = PlatformTypes()
        return self.__platformtype

    @property
    def state(self):
        if self.__state is None:
            from JumpScale9.core.State import State
            self.__state = State()
        return self.__state


# from JumpScale9.core.InstallTools import InstallTools
class Jumpscale9:

    def __init__(self):
        self.tools = Tools()
        self.sal = Sal()
        self.data = Data()
        self.clients = Clients()
        self.core = Core()

        self.__logger = None
        self.__dirs = None
        self.__errorhandler = None
        self.__application = None
        # self.do = InstallTools()

    @property
    def dirs(self):
        if self.__dirs is None:
            from JumpScale9.core.Dirs import Dirs
            self.__dirs = Dirs()
        return self.__dirs

    @property
    def application(self):
        if self.__application is None:
            from JumpScale9.core.Application import Application
            self.__application = Application()
        return self.__application

    @property
    def logger(self):
        if self.__logger is None:
            from JumpScale9.logging.LoggerFactory import LoggerFactory
            self.__logger = LoggerFactory()
        return self.__logger

    @property
    def errorhandler(self):
        if self.errorhandler is None:
            from JumpScale9.errorhandling.ErrorConditionHandler import ErrorConditionHandler
            self.errorhandler = ErrorConditionHandler()
        return self.errorhandler


j = Jumpscale9()

if "dirs" not in j.core.state.config:
    j.do.initEnv()

j.logger.enableConsoleHandler()
j.logger.set_mode("DEV")
j.logger.init()


logger = j.logger.get("init")
logger.debug("Init Done")
