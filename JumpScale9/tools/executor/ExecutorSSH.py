from js9 import j
from .ExecutorBase import *
import os


class ExecutorSSH(ExecutorBase):

    def __init__(self, sshclient, debug=False, checkok=True):

        ExecutorBase.__init__(self, debug=debug, checkok=checkok)

        self.sshclient = sshclient
        self.type = "ssh"

        self.cache = j.data.cache.get(id="executor:%s" % self.id)
        self.cache.reset()

        self._id = None

        self._logger = j.logger.get("executorssh%s" % self.sshclient.addr)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = j.logger.get("executor.%s" % self.sshclient.addr)
        return self._logger

    # def pushkey(self, user='root'):
    #     self.logger.debug("pushkey from agent with name:%s" % self.key_filename)
    #     key = self.pubkey or j.clients.ssh.SSHKeyGetFromAgentPub(self.key_filename)
    #     self.sshclient.ssh_authorize(user=self.login, key=key)
    #     # pass

    # def getMacAddr(self):
    #     print("Get maccaddr")
    #     rc, out, err = self.execute("ifconfig", showout=False)

    #     def checkOK(nic):
    #         excl = ["dummy", "docker", "lxc", "mie", "veth",
    #                 "vir", "vnet", "zt", "vms", "weave", "ovs"]
    #         check = True
    #         for item in excl:
    #             if nic.startswith(item):
    #                 check = False
    #         return check

    #     if out.find("HWaddr") != -1:
    #         # e.g. Ubuntu 16.04
    #         out = "\n".join([item for item in out.split("\n")
    #                          if item.find("HWaddr") != -1])

    #         res = {}
    #         for line in out.split("\n"):
    #             line = line.strip()

    #             if line == "":
    #                 continue

    #             addr = line.split("HWaddr")[-1].strip()
    #             name = line.split(" ")[0]

    #             if checkOK(line):
    #                 res[name] = addr

    #         if "eth0" in res:
    #             self.macaddr = res["eth0"]
    #         else:
    #             keys = [item for item in res.keys()]
    #             keys.sort()
    #             self.macaddr = res[keys[0]]
    #     else:
    #         lastnic = ""
    #         for line in out.split("\n"):
    #             print(line)
    #             if len(out) == 0:
    #                 continue
    #             if lastnic == "" and out[0] != " ":
    #                 if checkOK(line):
    #                     lastnic = line.split(":")[0]
    #                     print("lastnic:%s" % lastnic)
    #             if lastnic != "" and line.find("Ethernet") != -1:
    #                 self.macaddr = line.split(
    #                     "ether")[1].strip().split(" ")[0].strip()
    #                 break

    #     if self.macaddr == "":
    #         raise j.exceptions.Input(
    #             message="could not find macaddr", level=1, source="", tags="", msgpub="")

    #     return self.macaddr

    @property
    def id(self):
        if self._id is None:
            self._id = '%s:%s' % (self.sshclient.addr, self.sshclient.port)
        return self._id

    def executeRaw(self, cmd, die=True, showout=False):
        return self.sshclient.execute(cmd, die=die, showout=showout)

    def execute(self, cmds, die=True, checkok=False, showout=True, timeout=0, env={}, asScript=False, hide=False):
        """
        return (rc,out,err)
        """
        # if cmds.find("cat /root/.bash_profile") != -1:
        #     raise RuntimeError("JJ")
        # if cmds.find("test -e /root/.bash_profile") != -1:
        #     raise RuntimeError("JJ")

        if hide:
            showout=False

        cmds2 = self._transformCmds(cmds, die, checkok=checkok, env=env)

        if cmds.find("\n") != -1 and asScript:
            if showout:
                self.logger.info("EXECUTESCRIPT} %s:%s:\n%s" %
                                 (self.sshclient.addr, self.sshclient.port, cmds))
            # sshkey = self.sshclient.key_filename or ""
            return self._execute_script(content=cmds2, showout=showout, die=die, checkok=checkok, hide=hide)

        # online command, we use prefab
        if showout:
            self.logger.info("EXECUTE %s:%s: %s" %
                             (self.sshclient.addr, self.sshclient.port, cmds))
        else:
            if not hide:
                self.logger.debug("EXECUTE %s:%s: %s" %
                                  (self.sshclient.addr, self.sshclient.port, cmds))

        rc, out, err = self.sshclient.execute(
            cmds2, die=die, showout=showout)

        if hide is False:
            self.logger.debug("EXECUTE OK")

        if checkok and die:
            out = self.docheckok(cmds, out)

        return rc, out, err

    def _execute_script(self, content="", die=True, showout=True, checkok=None, hide=False):
        """
        @param remote can be ip addr or hostname of remote, if given will execute cmds there
        """

        if showout:
            self.logger.info("EXECUTESCRIPT %s:%s: %s" %
                             (self.sshclient.addr, self.sshclient.port, content))
        else:
            if not hide:
                self.logger.debug("EXECUTESCRIPT %s:%s: %s" %
                                  (self.sshclient.addr, self.sshclient.port, content))

        if content[-1] != "\n":
            content += "\n"

        if die:
            content = "set -ex\n%s" % content

        path = "/tmp/prefab_%s.sh" % j.data.idgenerator.generateRandomInt(
            1, 100000)
        j.sal.fs.writeFile(path, content)
        sftp = self.sshclient.getSFTP()
        sftp.put(path, path)  # is now always on tmp

        cmd = "bash {}".format(path)
        rc, out, err = self.sshclient.execute(cmd, die=die, showout=showout)

        if checkok and die:
            out = self.docheckok(content, out)

        j.sal.fs.remove(path)
        sftp.remove(path)

        return rc, out, err

    def upload(self, source, dest, dest_prefix="", recursive=True, createdir=True,
               rsyncdelete=True, ignoredir=['.egg-info', '.dist-info', '__pycache__', ".git"], keepsymlinks=False):

        if dest_prefix != "":
            dest = j.sal.fs.joinPaths(dest_prefix, dest)
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("need / in beginning of dest path")
        dest = "root@%s:%s" % (self.sshclient.addr, dest)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=keepsymlinks,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=ignoredir,
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.sshclient.port,
            recursive=recursive,
            createdir=createdir,
            rsyncdelete=rsyncdelete)
        self.cache.reset()

    def download(self, source, dest, source_prefix="", recursive=True):
        if source_prefix != "":
            source = j.sal.fs.joinPaths(source_prefix, source)
        if source[0] != "/":
            raise j.exceptions.RuntimeError(
                "need / in beginning of source path")
        source = "root@%s:%s" % (self.sshclient.addr, source)
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
            ssh=True,
            sshport=self.sshclient.port,
            recursive=recursive)

    def __repr__(self):
        return ("Executor ssh: %s (%s)" % (self.sshclient.addr, self.sshclient.port))

    __str__ = __repr__
