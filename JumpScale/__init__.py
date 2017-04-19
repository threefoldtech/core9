class JumpScale:

    def __init__(self):
        self.tools = None
        self.sal = None
        self.data = None
        self.clients = None
        self.core = None
        self.logger = None
        self.dirs = None
        self.errorhandler = None
        self.application = None
        # self.do = None


j = JumpScale()

# core
from JumpScale.core.PlatformTypes import PlatformTypes
from JumpScale.core.State import State

# # sal
from JumpScale.fs.SystemFS import SystemFS
from JumpScale.tools.process.SystemProcess import SystemProcess
from JumpScale.fs.SystemFSWalker import SystemFSWalker
#
# tools
from JumpScale.tools.executor.ExecutorLocal import ExecutorLocal
from JumpScale.tools.loader.JSLoader import JSLoader
from JumpScale.tools.tmux.Tmux import Tmux
#
# # data
from JumpScale.data.serializers.SerializersFactory import SerializersFactory
from JumpScale.data.text.Text import Text
from JumpScale.data.types.Types import Types
from JumpScale.data.cache.Cache import Cache
from JumpScale.data.idgenerator.IDGenerator import IDGenerator
from JumpScale.data.time.Time import Time_

# # clients
from JumpScale.clients.redis.RedisFactory import RedisFactory
#
# # base
from JumpScale.core.Dirs import Dirs
from JumpScale.core.Application import Application
from JumpScale.logging.LoggerFactory import LoggerFactory
from JumpScale.errorhandling.ErrorConditionHandler import ErrorConditionHandler
# from JumpScale.core.InstallTools import InstallTools

class Core:

    def __init__(self):
        self.__platformtype = None
        self.__state = None

    @property
    def platformtype(self) -> PlatformTypes:
        if self.__platformtype is None:
            self.__platformtype = PlatformTypes()
        return self.__platformtype

    @property
    def state(self) -> State:
        if self.__state is None:
            self.__state = State()
        return self.__state


class Sal:

    def __init__(self):
        self.__fs = None
        self.__process = None
        self.__fswalker = None

    @property
    def fs(self) -> SystemFS:
        if self.__fs is None:
            self.__fs = SystemFS()
        return self.__fs

    @property
    def process(self) -> SystemProcess:
        if self.__process is None:
            self.__process = SystemProcess()
        return self.__process

    @property
    def fswalker(self) -> SystemFSWalker:
        if self.__fswalker is None:
            self.__fswalker = SystemFSWalker
        return self.__fswalker


class Tools:

    def __init__(self):
        self.__executorLocal = None
        self.__jsloader = None
        self.__tmux = None

    @property
    def executorLocal(self) -> ExecutorLocal:
        if self.__executorLocal is None:
            self.__executorLocal = ExecutorLocal()  # needed in platformtypes
        return self.__executorLocal

    @property
    def jsloader(self) -> JSLoader:
        if self.__jsloader is None:
            self.__jsloader = JSLoader()
        return self.__jsloader

    @property
    def tmux(self) -> Tmux:
        if self.__tmux is None:
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
    def serializer(self) -> SerializersFactory:
        if self.__serializer is None:
            self.__serializer = SerializersFactory()
        return self.__serializer

    @property
    def text(self) -> Text:
        if self.__text is None:
            self.__text = Text()
        return self.__text

    @property
    def types(self) -> Types:
        if self.__types is None:
            self.__types = Types()
        return self.__types

    @property
    def cache(self) -> Cache:
        if self.__cache is None:
            self.__cache = Cache()
        return self.__cache

    @property
    def idgenerator(self) -> IDGenerator:
        if self.__idgenerator is None:
            self.__idgenerator = IDGenerator()
        return self.__idgenerator

    @property
    def time(self) -> Time_:
        if self.__time is None:
            self.__time = Time_()
        return self.__time


class Clients:

    def __init__(self):
        self.__redis = None

    @property
    def redis(self) -> RedisFactory:
        if self.__redis is None:
            self.__redis = RedisFactory()
        return self.__redis


class JumpScale:

    def __init__(self):
        self.core = Core()
        self.data = Data()
        self.sal = Sal()
        self.tools = Tools()
        self.clients = Clients()

        self.__logger = None
        self.__dirs = None
        self.__errorhandler = None
        self.__application = None
        self.__do = None

    @property
    def dirs(self) -> Dirs:
        if self.__dirs is None:
            self.__dirs = Dirs()
        return self.__dirs

    @property
    def application(self) -> Application:
        if self.__application is None:
            self.__application = Application()
        return self.__application

    @property
    def logger(self) -> LoggerFactory:
        if self.__logger is None:
            self.__logger = LoggerFactory()
        return self.__logger

    @property
    def errorhandler(self) -> ErrorConditionHandler:
        if self.__errorhandler is None:
            self.__errorhandler = ErrorConditionHandler()
        return self.__errorhandler

    # @property
    # def do(self) -> InstallTools:
    #     if self.__do is None:
    #         self.__do = InstallTools()
    #     return self.__do


j = JumpScale()


if "dirs" not in j.core.state.config:
    j.do.initEnv()

j.logger.enableConsoleHandler()
j.logger.set_mode("DEV")
j.logger.init()


logger = j.logger.get("init")
logger.debug("Init Done")
