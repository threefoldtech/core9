from js9 import j


class Node:

    def __init__(self, addr="localhost", port=22,cat="all",description="",name="",selected=False):
        self.addr = addr
        self.port = port
        self.connected = None
        self.cat=cat
        self.name=name
        self.description=description

        if selected in [1,True,"1"]:
            self.selected=True
        else:
            self.selected=False
        

    def test(self):
        if self.connected is None:
            # lets test tcp on 22 if not then 9022 which are our defaults
            test = j.sal.nettools.tcpPortConnectionTest(self.addr, self.port, 3)
            if test is False:
                print("could not connect to %s:%s, will try port 9022" % (self.addr, self.port))
                if self.port == 22:
                    test = j.sal.nettools.tcpPortConnectionTest(self.addr, 9022, 1)
                    if test:
                        self.port = 9022
            if test is False:
                raise j.exceptions.RuntimeError("Cannot connect to %s:%s" % (self.addr, self.port))

            self._sshclient = None
            self._ftpclient = None

            self.connected = True

    @property
    def ftpclient(self):
        self.test()
        if self._ftpclient is None:
            print("ftpclient")
            self._ftpclient = self.executor.sshclient.getSFTP()
        return self._ftpclient


    @property
    def executor(self):
        return j.tools.executor.get("%s:%s"%(self.addr,self.port))

    @property
    def prefab(self):
        return j.tools.prefab.get(executor=self.executor)

    def clean(self):
        cmd="""
        rm -f ~/.profile_js
        rm -f ~/env.sh
        rm -f rm /etc/jumpscale9.toml     
        """
        self.executor.execute(cmd)
    
    def test_executor(self):
        self.executor.test()

    def sync(self):
        ddirs=j.tools.develop.codedirs.getActiveCodeDirs()
        for ddir in ddirs:
            source=ddir.path
            dest="%s/%s/%s/%s"%(self.prefab.executor.dir_paths["CODEDIR"],ddir.type,ddir.account,ddir.name)
            self.prefab.executor.upload(source, dest, dest_prefix='', recursive=True, createdir=True)

    def __str__(self):
        if self.selected == True:
            return "%-14s %-25s:%-4s [%s] *"%(self.name,self.addr,self.port,self.cat)
        else:
            return "%-14s %-25s:%-4s [%s]"%(self.name,self.addr,self.port,self.cat)        

    __repr__ = __str__
