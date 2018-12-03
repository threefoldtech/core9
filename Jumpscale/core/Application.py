from Jumpscale import j
import os
# import sys
import atexit
import struct
from collections import namedtuple
import psutil
from .JSBase import JSBase


class Application:

    def __init__(self):

        self.logger = j.logger.get("application")

        self._calledexit = False

        self.state = "UNKNOWN"
        self.appname = 'UNKNOWN'

        self._debug = None

        self._systempid = None

        self.interactive = True
        self._location = "j.core.application"
        self.schemas = False  # to know if schema's can be used or not

    def jsbase_get_class(self):
        """

        JSBASE = j.application.jsbase_get_class()

        class myclass(JSBASE):

            def __init__(self):
                JSBASE.__init__(self)

        """
        return JSBase

    def reset(self):
        """
        empties the core.db
        """
        if j.core.db is not None:
            for key in j.core.db.keys():
                j.core.db.delete(key)
        self.reload()

    def reload(self):
        j.tools.jsloader.generate()

    @property
    def debug(self):
        if self._debug is None:
            self._debug = j.core.state.configGetFromDictBool("system", "debug", False)
        return self._debug

    @debug.setter
    def debug(self, value):
        self._debug = value

    def break_into_jshell(self, msg="DEBUG NOW"):
        if self.debug is True:
            self.logger.debug(msg)
            from IPython import embed
            embed()
        else:
            raise j.exceptions.RuntimeError(
                "Can't break into jsshell in production mode.")

    def init(self):
        pass

    @property
    def systempid(self):
        if self._systempid is None:
            self._systempid = os.getpid()
        return self._systempid

    def start(self, name=None):
        '''Start the application

        You can only stop the application with return code 0 by calling
        j.application.stop(). Don't call sys.exit yourself, don't try to run
        to end-of-script, I will find you anyway!
        '''
        if name:
            self.appname = name

        if "JSPROCNAME" in os.environ:
            self.appname = os.environ["JSPROCNAME"]

        if self.state == "RUNNING":
            raise j.exceptions.RuntimeError(
                "Application %s already started" % self.appname)

        # Register exit handler for sys.exit and for script termination
        atexit.register(self._exithandler)
        # Set state
        self.state = "RUNNING"

        self.logger.info("***Application started***: %s" % self.appname)

    def stop(self, exitcode=0, stop=True):
        '''Stop the application cleanly using a given exitcode

        @param exitcode: Exit code to use
        @type exitcode: number
        '''
        import sys

        # TODO: should we check the status (e.g. if application wasnt started,
        # we shouldnt call this method)
        if self.state == "UNKNOWN":
            # Consider this a normal exit
            self.state = "HALTED"
            sys.exit(exitcode)

        # Since we call os._exit, the exithandler of IPython is not called.
        # We need it to save command history, and to clean up temp files used by
        # IPython itself.
        # self.logger.debug("Stopping Application %s" % self.appname)
        try:
            __IPYTHON__.atexit_operations()
        except BaseException:
            pass

        self._calledexit = True
        # to remember that this is correct behavior we set this flag

        # tell gridmaster the process stopped

        # TODO: this SHOULD BE WORKING AGAIN, now processes are never removed

        if stop:
            sys.exit(exitcode)

    def _exithandler(self):
        # Abnormal exit
        # You can only come here if an application has been started, and if
        # an abnormal exit happened, i.e. somebody called sys.exit or the end of script was reached
        # Both are wrong! One should call j.application.stop(<exitcode>)
        # TODO: can we get the line of code which called sys.exit here?

        # j.logger.log("UNCLEAN EXIT OF APPLICATION, SHOULD HAVE USED j.application.stop()", 4)
        import sys
        if not self._calledexit:
            self.stop(stop=False)

    # def getCPUUsage(self):
    #     """
    #     try to get cpu usage, if it doesn't work will return 0
    #     By default 0 for windows
    #     """
    #     try:
    #         pid = os.getpid()
    #         if j.core.platformtype.myplatform.isWindows:
    #             return 0
    #         if j.core.platformtype.myplatform.isLinux:
    #             command = "ps -o pcpu %d | grep -E --regex=\"[0.9]\"" % pid
    #             self.logger.debug("getCPUusage on linux with: %s" % command)
    #             exitcode, output, err = j.sal.process.execute(
    #                 command, True, False)
    #             return output
    #         elif j.core.platformtype.myplatform.isSolaris():
    #             command = 'ps -efo pcpu,pid |grep %d' % pid
    #             self.logger.debug("getCPUusage on linux with: %s" % command)
    #             exitcode, output, err = j.sal.process.execute(
    #                 command, True, False)
    #             cpuUsage = output.split(' ')[1]
    #             return cpuUsage
    #     except Exception:
    #         pass
    #     return 0

    def getMemoryUsage(self):
        """
        for linux is the unique mem used for this process
        is in KB
        """
        p = psutil.Process()
        info = p.memory_full_info()
        return info.uss / 1024

    def appCheckActive(self, appname):
        return self.appNrInstances(appname) > 0

    def appNrInstances(self, appname):
        return len(self.appGetPids(appname))

    def appNrInstancesActive(self, appname):
        return len(self.appGetPidsActive(appname))

    # TODO: *2 is this still being used?
    def appGetPids(self, appname):
        if j.core.db is None:
            raise j.exceptions.RuntimeError(
                "Redis was not running when applications started, cannot get pid's")
        if not j.core.db.hexists("application", appname):
            return list()
        else:
            pids = j.data.serializer.json.loads(
                j.core.db.hget("application", appname))
            return pids

    def appsGetNames(self):
        if j.core.db is None:
            raise j.exceptions.RuntimeError(
                "Make sure redis is running for port 9999")
        return j.core.db.hkeys("application")

    def appsGet(self):

        defunctlist = j.sal.process.getDefunctProcesses()
        result = {}
        for item in self.appsGetNames():
            pids = self.appGetPidsActive(item)
            pids = [pid for pid in pids if pid not in defunctlist]

            if not pids:
                j.core.db.hdelete("application", item)
            else:
                result[item] = pids
        return result

    def appGetPidsActive(self, appname):
        pids = self.appGetPids(appname)
        todelete = []
        for pid in pids:
            if not self.isPidAlive(pid):
                todelete.append(pid)
            else:
                environ = self.getEnviron(pid)
                if environ.get('JSPROCNAME') != appname:
                    todelete.append(pid)
        for item in todelete:
            pids.remove(item)
        j.core.db.hset(
            "application",
            appname,
            j.data.serializer.json.dumps(pids))

        return pids

    def _setWriteExitcodeOnExit(self, value):
        if not j.data.types.bool.check(value):
            raise TypeError
        self._writeExitcodeOnExit = value

    def _getWriteExitcodeOnExit(self):
        if not hasattr(self, '_writeExitcodeOnExit'):
            return False
        return self._writeExitcodeOnExit

    writeExitcodeOnExit = property(
        fset=_setWriteExitcodeOnExit,
        fget=_getWriteExitcodeOnExit,
        doc="Gets / sets if the exitcode has to be persisted on disk")
