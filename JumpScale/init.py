
from JumpScale.core.JSBase import JSBase


from JumpScale.fs.SystemFS import SystemFS
from JumpScale.fs.SystemFSWalker import SystemFSWalker
from JumpScale.tools.nettools.NetTools import NetTools
from JumpScale.tools.process.ProcessManagerFactory import ProcessManagerFactory
from JumpScale.tools.process.SystemProcess import SystemProcess
from JumpScale.tools.rsync.RsyncFactory import RsyncFactory


class sal:
    fs = SystemFS()
    fswalker = SystemFSWalker()
    nettools = NetTools()
    processmanager = ProcessManagerFactory()
    process = SystemProcess()
    rsync = RsyncFactory()


from JumpScale.clients.git.GitFactory import GitFactory
from JumpScale.clients.http.HttpClient import HttpClient
from JumpScale.clients.redis.RedisFactory import RedisFactory
from JumpScale.clients.tarantool.Tarantool import TarantoolFactory


class clients:
    git = GitFactory()
    http = HttpClient()
    redis = RedisFactory()
    tarantool = TarantoolFactory()


from JumpScale.data.idgenerator.IDGenerator import IDGenerator
from JumpScale.data.regex.RegexTools import RegexTools
from JumpScale.data.serializers.SerializersFactory import SerializersFactory
from JumpScale.data.tags.TagsFactory import TagsFactory
from JumpScale.data.text.Text import Text
from JumpScale.data.time.Time import Time_
from JumpScale.data.types.Types import Types


class data:
    idgenerator = IDGenerator()
    regex = RegexTools()
    serializer = SerializersFactory()
    tags = TagsFactory()
    text = Text()
    time = Time_()
    types = Types()


from JumpScale.data.email.Email import EmailTool
from JumpScale.data.tarfile.TarFile import TarFileFactory
from JumpScale.data.zip.ZipFile import ZipFileFactory
from JumpScale.tools.bash.BashFactory import BashFactory
from JumpScale.tools.executor.ExecutorFactory import ExecutorFactory
from JumpScale.tools.executor.ExecutorLocal import ExecutorLocal
from JumpScale.tools.performancetrace.PerformanceTrace import PerformanceTraceFactory
from JumpScale.tools.tmux.Tmux import Tmux


class tools:
    email = EmailTool()
    tarfile = TarFileFactory()
    zipfile = ZipFileFactory()
    bash = BashFactory()
    executor = ExecutorFactory()
    executorLocal = ExecutorLocal()
    performancetrace = PerformanceTraceFactory()
    tmux = Tmux()


from JumpScale.core.Application import Application
from JumpScale.core.PlatformTypes import PlatformTypes
from JumpScale.core.State import State
from JumpScale.logging.LoggerFactory import LoggerFactory


class core:
    application = Application()
    platformtype = PlatformTypes()
    state = State()
    logger = LoggerFactory()



class Jumpscale9():

    def __init__(self):
            self.sal=sal()
            self.clients=clients()
            self.data=data()
            self.tools=tools()
            self.core=core()
j = Jumpscale9()
j.logger=j.core.logger
j.application=j.core.application

