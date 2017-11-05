
from js9 import j
import os
import sys

sys.path.append(j.sal.fs.getDirName(os.path.abspath(__file__)) + "/schemaspy")
# print(sys.path)
from .ZeroTemplates import ZeroTemplates
from .ZeroDomains import ZeroDomains

try:
    from domain import *
    from job import *
    from service import *
    from template import *
    from zerorobot import *
except:
    print("WARNING: COULD NOT LOAD SCHEMAS FOR ZEROROBOT, REGENERATE !!!")


class Messages():
    pass


class ZeroRobot:

    def __init__(self):
        self.__jslocation__ = "j.tools.zerorobot"
        self._messages = None
        self.templates = ZeroTemplates()
        self.domains = ZeroDomains()

    @property
    def messages(self):
        if self._messages is None:
            self._messages = Messages()
            self._loadSchemas()
        return self._messages

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))

    def install(self):
        """
        will install protobuf & other requirements for zerorobot
        """
        j.tools.prefab.local.runtimes.celery.install()
        j.tools.prefab.local.lib.protobuf.install()

        self.generateSchemas()

    def generateSchemas(self):
        path = "%s/schemas" % self._path

        j.sal.fs.removeDirTree("%s/schemaspy" % self._path)
        cmd = "cd %s;mkdir -p %s;protoc -I=schemas --python3_out=schemaspy/ schemas/job.proto" % (
            self._path, "%s/schemaspy" % self._path)
        j.do.execute(cmd)

        j.sal.fs.touch("%s/schemaspy/__init__.py" % self._path)

    def _loadSchemas(self):

        self.messages.Domain = Domain
        self.messages.Job = Job
        self.messages.JobRequest = JobRequest
        self.messages.JobRecurring = JobRecurring
        self.messages.ServicePointer = ServicePointer
        self.messages.ServiceConsumption = ServiceConsumption
        self.messages.Template = Template
        self.messages.TemplateAction = TemplateAction
        self.messages.ZeroRobot = ZeroRobot
        self.messages.Location = Location
        self.messages.LocationPointer = LocationPointer
