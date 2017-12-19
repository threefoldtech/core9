from JumpScale9 import j
from .ExecutorBase import ExecutorBase
import subprocess
import os
import pytoml

class ExecutorLocal(ExecutorBase):

    def __init__(self, debug=False, checkok=False):
        ExecutorBase.__init__(self, debug=debug, checkok=debug)

        self.type = "local"
        self._id = 'localhost'
        self._logger = None
        self.__jslocation__ = "j.tools.executorLocal"

        self.cache = j.data.cache.get(id="executor:%s" % self.id)

        # self.init()

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("executor.localhost")
        return self._logger

    def exists(self, path):
        return j.sal.fs.exists(path)

    @property
    def stateOnSystem(self):
        """
        is dict of all relevant param's on system
        """
        if self._stateOnSystem is None:            
            if "HOMEDIR" in os.environ.keys():
                homedir=os.environ["HOMEDIR"]
            else:
                homedir=os.environ["HOME"]
            cfgdir="%s/js9host/cfg"%homedir
            res={}
            
            def load(name):
                path="%s/%s.toml"%(cfgdir,name)
                if os.path.exists(path):
                    return pytoml.loads(j.sal.fs.fileGetContents(path))
                else:
                    return {}

            res["cfg_js9"]=load("jumpscale9")
            res["cfg_state"]=load("state")
            res["cfg_me"]=load("me")
            res["env"] = os.environ

            res["uname"]= subprocess.Popen("uname -mnprs", stdout=subprocess.PIPE, shell=True).stdout.read().decode().strip()
            res["hostname"]= subprocess.Popen("hostname", stdout=subprocess.PIPE, shell=True).stdout.read().decode().strip()

            if "darwin" in res["uname"].lower():
                res["os_type"] = "darwin"
            elif "linux" in res["uname"].lower():
                res["os_type"] = "ubuntu"  #dirty hack, will need to do something better, but keep fast
            else:
                print("need to fix for other types (check executorlocal")
                from IPython import embed;embed(colors='Linux')


            path=path="%s/.profile_js"%(homedir)
            if os.path.exists(path):
                res["bashprofile"]=j.sal.fs.fileGetContents(path)
            else:
                res["bashprofile"]=""

            res["path_jscfg"]=cfgdir

            if os.path.exists("/root/.iscontainer"):
                res["iscontainer"]=True
            else:
                res["iscontainer"]=False

            self._stateOnSystem=res

        return self._stateOnSystem
        

    def executeRaw(self, cmd, die=True, showout=False):
        return self.execute(cmd, die=die, showout=showout)

    def execute(self, cmds, die=True, checkok=None, showout=False, outputStderr=False, timeout=1000, env={}, hide=False):
        if env:
            self.env.update(env)
        # if self.debug:
        #     print("EXECUTOR:%s" % cmds)

        if outputStderr is None:
            outputStderr = showout

        if checkok is None:
            checkok = self.checkok

        cmds2 = self._transformCmds(cmds, die=die, checkok=checkok, env=env)

        rc, out, err = j.sal.process.execute(cmds2, die=die, showout=showout,
                                             outputStderr=outputStderr, timeout=timeout)

        if checkok:
            out = self.docheckok(cmds, out)

        return rc, out, err

    def executeInteractive(self, cmds, die=True, checkok=None):
        cmds = self._transformCmds(cmds, die, checkok=checkok)
        return j.sal.process.executeWithoutPipe(cmds)

    def upload(self, source, dest, dest_prefix="", recursive=True):
        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if j.sal.fs.isDir(source):
            j.sal.fs.copyDirTree(
                source,
                dest,
                keepsymlinks=True,
                deletefirst=False,
                overwriteFiles=True,
                ignoredir=[
                    ".egg-info",
                    ".dist-info"],
                ignorefiles=[".egg-info"],
                rsync=True,
                ssh=False,
                recursive=recursive)
        else:
            j.sal.fs.copyFile(source, dest, overwriteFile=True)
        self.cache.reset()

    def download(self, source, dest, source_prefix=""):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=False)

    def file_read(self, path):
        return j.sal.fs.readFile(path)
