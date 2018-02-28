import io

from js9 import j
from pssh.ssh2_client import SSHClient as PSSHClient

from .SSHClientBase import SSHClientBase


class SSHClient(SSHClientBase):

    def __init__(self, instance, data={}, parent=None, interactive=False):
        SSHClientBase.__init__(self, instance=instance,
                               data=data, parent=parent, interactive=interactive)
        self._logger = j.logger.get("ssh client: %s:%s(%s)" % (self.addr, self.port, self.login))
        self._client = None
        self._prefab = None

    @property
    def client(self):
        pkey = self.sshkey.path or None
        passwd = self.passwd
        if pkey:
            passwd = self.sshkey.passphrase
        self._client = PSSHClient(self.addr,
                                  user=self.login,
                                  password=passwd,
                                  port=self.port,
                                  pkey=pkey,
                                  num_retries=0,
                                  retry_delay=0,
                                  allow_agent=self.allow_agent,
                                  timeout=self.timeout)

        return self._client

    def execute(self, cmd, showout=True, die=True):
        channel, _, stdout, stderr, _ = self.client.run_command(cmd)

        def _consume_stream(stream, printer):
            buffer = io.StringIO()
            for line in stream:
                buffer.write(line + '\n')
                if showout:
                    printer(line)
            return buffer

        out = _consume_stream(stdout, self.logger.info)
        err = _consume_stream(stderr, self.logger.error)

        # TODO: not sure both of these are required
        channel.wait_eof()
        channel.close()

        rc = channel.get_exit_status()
        if rc and die:
            raise j.exceptions.RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, out.getvalue(), err.getvalue()))

        return rc, out.getvalue(), err.getvalue()

    def connect(self):
        pkey = self.sshkey.path or None
        passwd = self.passwd
        if pkey:
            passwd = self.sshkey.passphrase
        self._client = PSSHClient(self.addr,
                                  user=self.login,
                                  password=passwd,
                                  port=self.port,
                                  pkey=pkey,
                                  num_retries=self.timeout / 6,
                                  retry_delay=1,
                                  allow_agent=self.allow_agent,
                                  timeout=5)
        self._client.session.sftp_init() # seems to go further when I add this - TODO: look into it

    # def connectViaProxy(self, host, username, port, identityfile, proxycommand=None):
    #     # TODO: Fix this
    #     self.usesproxy = True
    #     client = paramiko.SSHClient()
    #     client._policy = paramiko.WarningPolicy()
    #     client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    #     import os.path
    #     self.host = host
    #     cfg = {'hostname': host, 'username': username, "port": port}
    #     self.addr = host
    #     self.user = username

    #     if identityfile is not None:
    #         cfg['key_filename'] = identityfile
    #         self.key_filename = cfg['key_filename']

    #     if proxycommand is not None:
    #         cfg['sock'] = paramiko.ProxyCommand(proxycommand)
    #     cfg['timeout'] = 5
    #     cfg['allow_agent'] = True
    #     cfg['banner_timeout'] = 5
    #     self.cfg = cfg
    #     self.forward_agent = True
    #     self._client = client
    #     self._client.connect(**cfg)

    #     return self._client

    def reset(self):
        with self._lock:
            if self._client is not None:
                self._client = None

    @property
    def sftp(self):
        return self.client._make_sftp()

    def close(self):
        # TODO: make sure we don't need to clean anything
        pass

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError("dest path should be absolute")

        dest = "%s@%s:%s" % (self.config.data['login'], self.addr_variable, dest)
        j.sal.fs.copyDirTree(
            source,
            dest,
            keepsymlinks=True,
            deletefirst=False,
            overwriteFiles=True,
            ignoredir=[
                ".egg-info",
                ".dist-info",
                "__pycache__"],
            ignorefiles=[".egg-info"],
            rsync=True,
            ssh=True,
            sshport=self.port_variable,
            recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise j.exceptions.RuntimeError("source path should be absolute")
        source = "%s@%s:%s" % (self.config.data['login'], self.addr_variable, source)
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
            sshport=self.port_variable,
            recursive=recursive)

    @property
    def prefab(self):
        # FIXME: THIS is very spaghetti` !!!

        if not self.config.data['proxy']:
            executor = j.tools.executor.ssh_get(self.instance)
            if self.config.data["login"] != "root":
                # print("NONROOT PREFAB")
                executor.state_disabled = True
            prefab = executor.prefab

        elif self.config.data['proxy']:
            ex = j.tools.executor.getSSHViaProxy(self.addr_variable)
            prefab = j.tools.prefab.get(self)

        return prefab

    def ssh_authorize(self, user, key):
        sshkey = j.clients.sshkey.get(key)
        pubkey = sshkey.pubkey
        self.prefab.system.ssh.authorize(user=user, key=pubkey)
    # def portforwardToLocal(self, remoteport, localport):
    #     self.portforwardKill(localport)
    #     C = "ssh -L %s:localhost:%s root@%s -p %s" % (
    #         remoteport, localport, self.addr, self.port)
    #     print(C)
    #     pm = j.tools.prefab.local.system.processmanager.get()
    #     pm.ensure(cmd=C, name="ssh_%s" % localport, wait=0.5)
    #     print("Test tcp port to:%s" % localport)
    #     if not j.sal.nettools.waitConnectionTest("127.0.0.1", localport, 10):
    #         raise RuntimeError("Cannot open ssh forward:%s_%s_%s" %
    #                            (self, remoteport, localport))
    #     print("Connection ok")

    # def portforwardKill(self, localport):
    #     print("kill portforward %s" % localport)
    #     pm = j.tools.prefab.local.system.processmanager.get()
    #     pm.processmanager.stop('ssh_%s' % localport)
