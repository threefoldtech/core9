from js9 import j

import os
import threading
from .SSHClient import SSHClient
from .AsyncSSHClient import AsyncSSHClient


class SSHClientFactory:

    _lock = threading.Lock()
    cache = {}

    logger = j.logger.get("j.clients.ssh")

    def __init__(self):
        self.__jslocation__ = "j.clients.ssh"
        self.__imports__ = "paramiko,asyncssh"
        self.loadSSHAgent = self._loadSSHAgent

    def reset(self):
        with self._lock:
            for key, client in self.cache.items():
                client.close()
            self.cache = {}

    def get(self, addr='', port=22, login="root", passwd=None, stdout=True, forward_agent=True, allow_agent=True,
            look_for_keys=True, timeout=5, key_filename=None, passphrase=None, die=True, usecache=True):
        """
        gets an ssh client.
        @param addr: the server to connect to
        @param port: port to connect to
        @param login: the username to authenticate as
        @param passwd: leave empty if logging in with sshkey
        @param stdout: show output
        @param foward_agent: fowrward all keys to new connection
        @param allow_agent: set to False to disable connecting to the SSH agent
        @param look_for_keys: set to False to disable searching for discoverable private key files in ~/.ssh/
        @param timeout: an optional timeout (in seconds) for the TCP connect
        @param key_filename: the filename to try for authentication
        @param passphrase: a password to use for unlocking a private key
        @param die: die on error
        @param usecache: use cached client. False to get a new connection

        If password is passed, sshclient will try to authenticated with login/passwd.
        If key_filename is passed, it will override look_for_keys and allow_agent and try to connect with this key.
        """
        with self._lock:
            key = "%s_%s_%s_%s_sync" % (
                addr, port, login, j.data.hash.md5_string(str(passwd)))

            if key in self.cache and usecache:
                try:
                    if not self.cache[key].transport.is_active():
                        usecache = False
                except Exception:
                    usecache = False
            if key not in self.cache or usecache is False:
                self.cache[key] = SSHClient(
                    addr,
                    port,
                    login,
                    passwd,
                    stdout=stdout,
                    forward_agent=forward_agent,
                    allow_agent=allow_agent,
                    look_for_keys=look_for_keys,
                    key_filename=key_filename,
                    passphrase=passphrase,
                    timeout=timeout)

            return self.cache[key]

    def getAsync(self, addr='', port=22, login="root", passwd=None, stdout=True, forward_agent=True, allow_agent=True,
                 look_for_keys=True, timeout=5, key_filename=(), passphrase=None, die=True, usecache=True):

        key = "%s_%s_%s_%s_async" % (
            addr, port, login, j.data.hash.md5_string(str(passwd)))

        if key not in self.cache or usecache is False:
            self.cache[key] = AsyncSSHClient(
                addr=addr,
                port=port,
                login=login,
                passwd=passwd,
                forward_agent=forward_agent,
                allow_agent=allow_agent,
                look_for_keys=look_for_keys,
                key_filename=key_filename,
                passphrase=passphrase,
                timeout=timeout)

        return self.cache[key]

    def removeFromCache(self, client):
        with self._lock:
            key = "%s_%s_%s_%s" % (
                client.addr, client.port, client.login, j.data.hash.md5_string(str(client.passwd)))
            if key in self.cache:
                self.cache.pop(key)

    def close(self):
        with self._lock:
            for key, client in self.cache.items():
                client.close()

    def _addSSHAgentToBashProfile(self, path=None):

        bashprofile_path = os.path.expanduser("~/.bash_profile")
        if not j.sal.fs.exists(bashprofile_path):
            j.do.execute('touch %s' % bashprofile_path)

        content = j.sal.fs.readFile(bashprofile_path)
        out = ""
        for line in content.split("\n"):
            if line.find("#JSSSHAGENT") != -1:
                continue
            if line.find("SSH_AUTH_SOCK") != -1:
                continue

            out += "%s\n" % line

        if "SSH_AUTH_SOCK" in os.environ:
            self.logger.info("NO NEED TO ADD SSH_AUTH_SOCK to env")
            j.sal.fs.writeFile(bashprofile_path, out)
            return

        out += "export SSH_AUTH_SOCK=%s" % self._getSSHSocketpath()
        out = out.replace("\n\n\n", "\n\n")
        out = out.replace("\n\n\n", "\n\n")
        j.sal.fs.writeFile(bashprofile_path, out)

    def _initSSH_ENV(self, force=False):
        if force or "SSH_AUTH_SOCK" not in os.environ:
            os.putenv("SSH_AUTH_SOCK", self._getSSHSocketpath())
            os.environ["SSH_AUTH_SOCK"] = self._getSSHSocketpath()

    def _getSSHSocketpath(self):

        if "SSH_AUTH_SOCK" in os.environ:
            return(os.environ["SSH_AUTH_SOCK"])

        socketpath = "%s/sshagent_socket" % os.environ.get("HOME", '/root')
        os.environ['SSH_AUTH_SOCK'] = socketpath
        return socketpath

    def SSHAgentCheck(self):
        if "SSH_AUTH_SOCK" not in os.environ:
            self._initSSH_ENV(True)
            self._addSSHAgentToBashProfile()
        if not self.SSHAgentAvailable():
            self._loadSSHAgent()

    def SSHKeyLoad(self, path, duration=3600 * 24):
        """
        @param path is name or full path
        """
        self.SSHAgentCheck()
        if self.SSHAgentCheckKeyIsLoaded(path):
            return
        self.logger.info("load ssh key:%s" % path)
        j.do.chmod(path, 0o600)
        cmd = "ssh-add -t %s %s " % (duration, path)
        j.do.executeInteractive(cmd)

    def SSHAgentCheckKeyIsLoaded(self, keyNamePath):
        keysloaded = [j.sal.fs.getBaseName(item)
                      for item in self.SSHKeysListFromAgent()]
        if j.sal.fs.getBaseName(keyNamePath) in keysloaded:
            self.logger.info("ssh key:%s loaded" % keyNamePath)
            return True
        else:
            self.logger.info("ssh key:%s NOT loaded" % keyNamePath)
            return False

    def SSHKeysLoad(self, path=None, duration=3600 * 24, die=False):
        """
        will see if ssh-agent has been started
        will check keys in home dir
        will ask which keys to load
        will adjust .profile file to make sure that env param is set to allow ssh-agent to find the keys
        """
        self.SSHAgentCheck()

        if path is None:
            path = os.path.expanduser("~/.ssh")
        j.do.createDir(path)

        if "SSH_AUTH_SOCK" not in os.environ:
            self._initSSH_ENV(True)

        self._loadSSHAgent()

        keysloaded = [j.sal.fs.getBaseName(item)
                      for item in self.SSHKeysListFromAgent()]

        if j.do.isDir(path):
            keysinfs = [j.sal.fs.getBaseName(item).replace(".pub", "") for item in self.listFilesInDir(
                path, filter="*.pub") if j.sal.fs.exists(item.replace(".pub", ""))]
            keysinfs = [item for item in keysinfs if item not in keysloaded]

            res = self.askItemsFromList(
                keysinfs,
                "select ssh keys to load, use comma separated list e.g. 1,4,3 and press enter.")
        else:
            res = [j.sal.fs.getBaseName(path).replace(".pub", "")]
            path = j.do.getParent(path)

        for item in res:
            pathkey = "%s/%s" % (path, item)
            # timeout after 24 h
            self.logger.info("load sshkey: %s" % pathkey)
            cmd = "ssh-add -t %s %s " % (duration, pathkey)
            j.do.executeInteractive(cmd)

    def SSHKeyGetPathFromAgent(self, keyname, die=True):
        for item in j.clients.ssh.SSHKeysListFromAgent():
            if item.endswith(keyname):
                return item
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)

    def SSHKeyGetFromAgentPub(self, keyname, die=True):
        for item in j.clients.ssh.SSHKeysListFromAgent():
            if item.endswith(keyname):
                return j.sal.fs.readFile(item + ".pub")
        if die:
            raise RuntimeError(
                "Did not find key with name:%s, check its loaded in ssh-agent with ssh-add -l" %
                keyname)

    def SSHKeysListFromAgent(self, keyIncluded=False):
        """
        returns list of paths
        """
        if "SSH_AUTH_SOCK" not in os.environ:
            self._initSSH_ENV(True)
        self._loadSSHAgent()
        cmd = "ssh-add -L"
        rc, out, err = j.do.execute(cmd, False, False, die=False)
        if rc:
            if rc == 1 and out.find("The agent has no identities") != -1:
                return []
            raise RuntimeError("error during listing of keys :%s" % err)
        keys = [line.split()
                for line in out.splitlines() if len(line.split()) == 3]
        if keyIncluded:
            return list(map(lambda key: key[2:0:-1], keys))
        else:
            return list(map(lambda key: key[2], keys))

    # def SSHEnsureKeyname(self, keyname="", username="root"):
    #     if not j.sal.fs.exists(keyname):
    #         rootpath = "/root/.ssh/" if username == "root" else "/home/%s/.ssh/"
    #         fullpath = j.do.joinPaths(rootpath, keyname)
    #         if j.sal.fs.exists(fullpath):
    #             return fullpath
    #     return keyname

    def SSHKnownHostsRemoveItem(self, item):
        """
        item is ip addr or hostname of the file we need to remove
        """
        path = "%s/.ssh/known_hosts" % j.dirs.HOMEDIR
        out = ""
        for line in j.sal.fs.readFile(path).split("\n"):
            if line.find(item) is not -1:
                continue
            out += "%s\n" % line
        j.sal.fs.writeFile(path, out)

    def _loadSSHAgent(self, path=None, createkeys=False, killfirst=False):
        """
        check if ssh-agent is available & there is key loaded

        @param path: is path to private ssh key

        the primary key is 'id_rsa' and will be used as default e.g. if authorizing another node then this key will be used

        """
        # check if more than 1 agent
        socketpath = self._getSSHSocketpath()
        res = [
            item for item in j.do.execute(
                "ps aux|grep ssh-agent",
                False,
                False)[1].split("\n") if item.find("grep ssh-agent") == -
            1]
        res = [item for item in res if item.strip() != ""]
        res = [item for item in res if item[-2:] != "-l"]

        if len(res) > 1:
            self.logger.info("more than 1 ssh-agent, will kill all")
            killfirst = True
        if len(res) == 0 and j.sal.fs.exists(socketpath):
            j.do.delete(socketpath)

        if killfirst:
            cmd = "killall ssh-agent"
            # self.logger.info(cmd)
            j.do.execute(cmd, showout=False, outputStderr=False, die=False)
            # remove previous socketpath
            j.do.delete(socketpath)
            j.do.delete(j.do.joinPaths('/tmp', "ssh-agent-pid"))

        if not j.sal.fs.exists(socketpath):
            j.do.createDir(j.do.getParent(socketpath))
            # ssh-agent not loaded
            self.logger.info("load ssh agent")
            rc, result, err = j.do.execute(
                "ssh-agent -a %s" %
                socketpath, die=False, showout=False, outputStderr=False)

            if rc > 0:
                # could not start ssh-agent
                raise RuntimeError(
                    "Could not start ssh-agent, something went wrong,\nstdout:%s\nstderr:%s\n" %
                    (result, err))
            else:
                # get pid from result of ssh-agent being started
                if not j.sal.fs.exists(socketpath):
                    raise RuntimeError(
                        "Serious bug, ssh-agent not started while there was no error, should never get here")
                piditems = [item for item in result.split(
                    "\n") if item.find("pid") != -1]
                # print(piditems)
                if len(piditems) < 1:
                    print("results was:")
                    print(result)
                    print("END")
                    raise RuntimeError("Cannot find items in ssh-add -l")
                self._initSSH_ENV(True)
                pid = int(piditems[-1].split(" ")[-1].strip("; "))
                j.sal.fs.writeFile(
                    j.do.joinPaths(
                        '/tmp',
                        "ssh-agent-pid"),
                    str(pid))
                self._addSSHAgentToBashProfile()

            # ssh agent should be loaded because ssh-agent socket has been
            # found
            if os.environ.get("SSH_AUTH_SOCK") != socketpath:
                self._initSSH_ENV(True)
            rc, result, err = j.do.execute(
                "ssh-add -l", die=False, showout=False, outputStderr=False)
            if rc == 2:
                # no ssh-agent found
                print(result)
                raise RuntimeError(
                    "Could not connect to ssh-agent, this is bug, ssh-agent should be loaded by now")
            elif rc == 1:
                # no keys but agent loaded
                result = ""
            elif rc > 0:
                raise RuntimeError(
                    "Could not start ssh-agent, something went wrong,\nstdout:%s\nstderr:%s\n" %
                    (result, err))

    def SSHAgentAvailable(self):
        if not j.sal.fs.exists(self._getSSHSocketpath()):
            return False
        if "SSH_AUTH_SOCK" not in os.environ:
            self._initSSH_ENV(True)
        rc, out, err = j.do.execute(
            "ssh-add -l", showout=False, outputStderr=False, die=False)
        if 'The agent has no identities.' in out:
            return True
        if rc != 0:
            return False
        else:
            return True
