from js9 import j

from .ExecutorSSH import *
from .ExecutorLocal import *
from .ExecutorAsyncSSH import ExecutorAsyncSSH
import threading


class ExecutorFactory:
    _lock = threading.Lock()
    _executors = {}
    _executors_async = {}

    def __init__(self):
        self.__jslocation__ = "j.tools.executor"

    def get(self, executor="localhost"):
        """
        @param executor is localhost or $hostname:$port or $ipaddr:$port or $hostname or $ipaddr

        for ssh only root access is allowed !

        """
        #  test if it's in cache
        with self._lock:
            if executor in self._executors:
                return self._executors[executor]

            if executor in ["localhost", "", None, "127.0.0.1"]:
                if 'localhost' not in self._executors:
                    local = self.getLocal()
                    self._executors['localhost'] = local
                return self._executors['localhost']

        if j.data.types.string.check(executor):
            if executor.find(":") > 0:
                nbr = executor.count(':')
                if nbr == 1:
                    # ssh with port
                    addr, port = executor.split(":")
                if nbr == 2:
                    raise RuntimeError("no longer supported, only root access")
                return self.getSSHBased(addr=addr.strip(), port=int(port))
            else:
                return self.getSSHBased(addr=executor.strip())
        else:
            return executor

    def getLocal(self, jumpscale=False, debug=False, checkok=False):
        return ExecutorLocal(debug=debug, checkok=debug)

    def getSSHBased(self, addr="localhost", port=22, timeout=5, usecache=True):
        """
        returns an ssh-based executor, the ssh key needs to be loaded in ssh-agent
        usecache: gets cached executor if available. False to get a new one.
        """
        with self._lock:
            key = '%s:%s' % (addr, port)
            if key not in self._executors or usecache is False or (key in self._executors and self._executors[key].sshclient.transport is None):
                sshclient = j.clients.ssh.get(
                    addr=addr, port=port, timeout=timeout, usecache=usecache)
                self._executors[key] = ExecutorSSH(sshclient=sshclient)
            return self._executors[key]

    def getFromSSHClient(self, sshclient, usecache=True):
        """
        get sshclient from j.clients.ssh
        """
        with self._lock:
            key = '%s:%s' % (sshclient.addr, sshclient.port)
            if key not in self._executors or usecache is False or (key in self._executors and self._executors[key].sshclient.transport is None):
                self._executors[key] = ExecutorSSH(sshclient=sshclient)
            return self._executors[key]

    def getAsyncSSHBased(self, addr="localhost", port=22, timeout=5, usecache=True):
        """
        returns an asyncssh-based executor where:
        allow_agent: uses the ssh-agent to connect
        look_for_keys: will iterate over keys loaded on the ssh-agent and try to use them to authenticate
        pushkey: authorizes itself on remote
        pubkey: uses this particular key (path) to connect
        usecache: gets cached executor if available. False to get a new one.
        """
        #@TODO: *1 needs to be fixed
        raise RuntimeError("not implemented")
        with self._lock:
            key = '%s:%s:%s' % (addr, port, login)
            if key not in self._executors_async or usecache is False:
                self._executors_async[key] = ExecutorAsyncSSH(addr=addr,
                                                              port=port,
                                                              login=login,
                                                              passwd=passwd,
                                                              debug=debug,
                                                              allow_agent=allow_agent,
                                                              look_for_keys=look_for_keys,
                                                              timeout=timeout,
                                                              key_filename=key_filename,
                                                              passphrase=passphrase)

            return self._executors_async[key]

    def reset(self, executor):
        """
        reset remove the executor passed in argument from the cache.
        """
        if j.data.types.string.check(executor):
            key = executor
        elif executor.type == 'ssh':
            key = '%s:%s' % (executor.addr, executor.port)
        else:
            raise j.exceptions.Input(message='executor type not recognize.')
        with self._lock:
            if key in self._executors:
                exe = self._executors[key]
                j.tools.prefab.reset(exe.prefab)
                del self._executors[key]
