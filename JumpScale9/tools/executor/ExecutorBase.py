from JumpScale9 import j
try:
    import ujson as json
except ImportError:
    import json

import pytoml

class ExecutorBase:

    def __init__(self, debug=False, checkok=True):

        self.debug=debug
        self.checkok = checkok

        self.type = None
        self._id = None
        self.readonly = False
        self.CURDIR = ""
        self.reset()
        self._logger = None
        self._iscontainer=None
        self.state=None
        self.config=None

    def init(self):
        if not self.type == "local":
            from JumpScale9.core.State import State
            self.state = State(self)
            self.config=self.state.config

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("unknown")
        return self._logger

    @property
    def id(self):
        if self._id is None:
            raise j.exceptions.Input(message="self._id cannot be None", level=1, source="", tags="", msgpub="")
        return self._id

    # @property
    # def config(self):
    #     """
    #     is dict which is stored on node itself in json format in /tmp/jsself.json
    #     """
            
    #     if "CFGDIR" not in self.env:
    #         T=j.do.getDirPathConfig(self)
    #         T=T.replace("//", "/")
    #         DIRPATHS = pytoml.loads(T)

    #         config=""
    #         for key,val in DIRPATHS.items():
    #             config+="export %s=%s\n"%(key,val)

    #     print (22222222)
    #     from IPython import embed;embed(colors='Linux')

    #     if "DEBUG" in env and str(env["DEBUG"]).lower() in ["true", "1", "yes"]:
    #         env["DEBUG"] = "1"
    #     else:
    #         env["DEBUG"] = "0"

    #     if "READONLY" in env and str(env["READONLY"]).lower() in ["true", "1", "yes"]:
    #         env["READONLY"] = "1"
    #         self.readonly = True
    #     else:
    #         env["READONLY"] = "0"
    #         self.readonly = False
            

    #     if self._config is None:
    #         if self.exists("$VARDIR/jsself.json") == False:
    #             self._config = {}
    #         else:
    #             data = self.prefab.core.file_read("$VARDIR/jsself.json")
    #             self._config = json.loads(data)

    #     return self._config



    @property
    def env(self):
        if self._env is None:
            res = {}
            print("DEBUG: EXECUTOR GET ENV")
            _, out, _ = self.execute("printenv", showout=False)
            for line in out.splitlines():
                if '=' in line:
                    name, val = line.split("=", 1)
                    name = name.strip()
                    val = val.strip().strip("'").strip("\"")
                    res[name] = val
            self._env = res
        return self._env

    def docheckok(self, cmd, out):
        out = out.rstrip("\n")
        lastline = out.split("\n")[-1]
        if lastline.find("**OK**") == -1:
            raise j.exceptions.RuntimeError("Error in:\n%s\n***\n%s" % (cmd, out))
        out = "\n".join(out.split("\n")[:-1]).rstrip() + "\n"
        return out

    def _transformCmds(self, cmds, die=True, checkok=None, env={}):
        # print ("TRANSF:%s"%cmds)
        if cmds.find("\n") == -1:
            separator = ";"
        else:
            separator = "\n"

        pre = ""

        if checkok is None:
            checkok = self.checkok

        if die:
            if self.debug:
                pre += "set -ex\n"
            else:
                pre += "set -e\n"

        if self.CURDIR != "":
            pre += "cd %s\n" % (self.CURDIR)

        cmds = "%s\n%s" % (pre, cmds)

        if checkok:
            cmds += "\necho '**OK**'"

        cmds = cmds.replace("\n", separator).replace(";;", ";").strip(";")

        return cmds

    #LETS TRY THAT WE SHOULD NOT HAVE TO DO THIS, ITS SAFER, PEOPLE NEED TO GET THEIR PREFAB INSTANCE WHICH WILL THEN SET THE EXECUTOR
    # @property
    # def prefab(self):
    #     if self._prefab is None:
    #         from js9 import j
    #         self._prefab = j.tools.prefab.get(self)
    #         self._prefab.executor = self
    #         try:
    #             self._prefab.sshclient = self.sshclient
    #         except BaseException:
    #             pass
    #     return self._prefab

    def exists(self, path):
        rc,out,err=self.execute('test -e %s'%path,die=False,showout=False)
        if rc>0:
            return False
        else:
            return True

    # interface to implement by child classes
    def execute(self, cmds, die=True, checkok=None, showout=True, timeout=0, env={}):
        raise NotImplementedError()

    def executeRaw(self, cmd, die=True, showout=False):
        raise NotImplementedError()

    def reset(self):
        self._env=None

    @property
    def isDebug(self):
        return self.config["system"]["debug"]=="1" or  self.config["system"]["debug"]==1 or  self.config["system"]["debug"]==True or self.config["system"]["debug"]=="true"

    @property
    def isContainer(self):
        """
        means we don't work with ssh-agent ...
        """
        if self._iscontainer==None:
            self._iscontainer= self.exists("/root/.iscontainer")
        return self._iscontainer

    def enableDebug(self):
        self.config["system"]["debug"] = value
        self.state.configSave()

    def _getDirPathConfig(self):

        islinux=self.platformtype.isUnix
        hostdirexists= self.exists("/host")

        if self.isContainer and not hostdirexists:
            raise RuntimeError("if container the hostdir needs to exists (/host)")

        if self.isContainer:
            T = '''
            BASEDIR = "/opt"        
            CODEDIR = "/opt/code"
            HOSTDIR = "/host"
            HOSTCFGDIR = "/hostcfg"
            VARDIR = "{{HOSTDIR}}/var"
            '''
        elif islinux:
            T = '''
            BASEDIR = "/opt"        
            CODEDIR = "/opt/code"
            HOSTDIR = ""
            HOSTCFGDIR = ""
            VARDIR = "{{BASEDIR}}/var"     
            '''
        else:
            T = '''
            BASEDIR = "{{HOMEDIR}}/opt"        
            CODEDIR = "{{HOMEDIR}}/code"
            HOSTDIR = ""
            HOSTCFGDIR = ""
            VARDIR = "{{BASEDIR}}/var"     
            '''

        BASE='''           
        HOMEDIR = "~"
        TMPDIR = "/tmp"
        BASEDIRJS = "{{BASEDIR}}/jumpscale9"
        DATADIR = "{{VARDIR}}/data"
        BUILDDIR = "{{VARDIR}}/build"
        LIBDIR = "{{BASEDIR}}/lib/"
        LOGDIR = "{{VARDIR}}/log"
        BINDIR="{{BASEDIR}}/bin"
        CFGDIR = "{{BASEDIR}}/cfg"
        '''
        
        TXT=j.data.text.strip(BASE)+"\n"+j.data.text.strip(T)

        return self._replaceInToml(TXT)
        
    def _replaceInToml(self,T):
        T=T.replace("~", os.environ["HOME"])        
        # will replace  variables in itself
        counter = 0
        while "{{" in T and counter < 10:
            TT = pytoml.loads(T)
            T = pystache.render(T, **TT)
            counter += 1
        TT = pytoml.loads(T)

        if counter > 9:
            raise RuntimeError(
                "cannot convert default configfile, template arguments still in")
        
        return T

    def initEnv(self):
        """
        init the environment of an executor
        """

        T=self._getDirPathConfig()
        T=T.replace("//", "/")
        DIRPATHS = pytoml.loads(T)

        # get env dir arguments & overrule them in jumpscale config
        for key, val in self.env.items():
            if "DIR" in key and key in DIRPATHS:
                DIRPATHS[key] = val

        TME = '''
        [email]
        from = "info@incubaid.com"
        smtp_port = 443
        smtp_server = ""

        [me]
        fullname = "This is my full name, needs to be replace"
        loginname = "someid"

        [ssh]
        SSHKEYNAME = "somename"

        '''

        TME=j.data.text.strip(TME)

        # if DIRPATHS["HOSTCFGDIR"]!="":
        #     path=self.joinPaths(DIRPATHS["HOSTCFGDIR"],"me.toml")
        #     if not self.exists(path):
        #         self.writeFile(path,j.data.text.strip(TME))
        #     else:
        #         #config file exists lets load it
        #         TME=self.readFile(path)

        TSYSTEM= '''

        [system]
        debug = true
        autopip = false
        readonly = false
        container = false

        [grid]
        gid = 0
        nid = 0

        [redis]
        enabled = false
        port = 6379
        addr = "localhost"

        '''

        TSYSTEM=j.data.text.strip(TSYSTEM)

        T = TSYSTEM + "\n" + TME + "\n"

        TT = pytoml.loads(T)
        TT["dirs"]=DIRPATHS
             
        TT["system"]["container"] = self.exists("/root/.iscontainer")

        if "plugins" not in TT.keys():
            TT["plugins"]={"core9":"%s/github/jumpscale/core9/" % DIRPATHS["CODEDIR"]}

        if not self.exists(TT["plugins"]["core9"]):
            raise RuntimeError("cannot find codedir for jumpscale9: %s"%(TT["plugins"]["core9"]))

        if TT["system"]["container"] == True:
            self.state.configUpdate(TT, True)  # will overwrite
        else:
            self.state.configUpdate(TT, False)  # will not overwrite

        
        if not self.exists(j.core.state.config["dirs"]["CODEDIR"]):
            raise RuntimeError("cannot find codedir: %s"%j.core.state.config["dirs"]["CODEDIR"])

        for key, val in DIRPATHS.items():
            if not self.exists(val):
                self.execute("mkdir -p %s"%val)

        # if DIRPATHS["HOSTCFGDIR"]!="":
        #     path=self.joinPaths(DIRPATHS["HOSTCFGDIR"],"me.toml")
        #     if not self.exists(path):
        #         self.writeFile(path,j.data.text.strip(TME))  #needs to use the args I already know & then put in separate file

        if self.type == "local":
            src = "%s/github/jumpscale/core9/cmds/" % j.core.state.config["dirs"]["CODEDIR"]
            j.do.symlinkFilesInDir(src, "/usr/local/bin", delete=True, includeDirs=False, makeExecutable=True)

        # self.writeEnvArgsBash()

        self.state.configSave()

        import pudb; pudb.set_trace()
    
    @property
    def dir_paths(self):
        return self.config["dirs"]


    @property
    def platformtype(self):  
        return j.core.platformtype.get(self)

    def file_read(self,path):
        rc, out, err=self.execute("cat %s"%path,showout=False)
        return out
        # source=j.sal.fs.getTmpFilePath()
        # self.download(path,source)
        # content=j.sal.fs.readFile(source)
        # j.sal.fs.remove(source)    
        # return content

    def file_write(self,path,content):
        source=j.sal.fs.getTmpFilePath()
        j.sal.fs.writeFile(source,content)
        self.upload(source, path)
        j.sal.fs.remove(source)    