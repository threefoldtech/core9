import threading
import time
from io import StringIO

import paramiko
from js9 import j
from pssh.ssh2_client import SSHClient as PSSHClient


class SSHClient:

    def __init__(self, addr='', port=22, login="root", passwd=None, usesproxy=False, stdout=True,
                 forward_agent=True, allow_agent=True, look_for_keys=True, key_filename=None, passphrase=None, timeout=5.0):
        self._lock = threading.Lock()
        self.port = port
        self.addr = addr
        self.login = login
        self.passwd = passwd
        self.stdout = stdout
        self.timeout = timeout
        self.allow_agent = allow_agent
        self.usesproxy = usesproxy
        if passwd:
            self.forward_agent = False
            self.look_for_keys = False
            self.key_filename = None
            self.passphrase = None
        else:
            self.forward_agent = forward_agent
            self.look_for_keys = look_for_keys
            self.key_filename = key_filename
            self.passphrase = passphrase

        self.logger = j.logger.get("ssh client: %s(%s):" % (self.addr, self.port))
        self._prefab = None

        self.pkey = None
        if self.key_filename is not None and self.key_filename != '':
            self.pkey = paramiko.RSAKey.from_private_key_file(
                self.key_filename, password=self.passphrase)

        if self.key_filename:
            self.allow_agent = True
            self.look_for_keys = True
            if j.clients.ssh.SSHKeyGetPathFromAgent(self.key_filename, die=False) is not None and not self.passphrase:
                j.clients.ssh.ssh_keys_load(self.key_filename)

    def connect(self):

        self._client = PSSHClient(self.addr,
                                  user=self.login,
                                  password=self.passwd,
                                  port=self.port,
                                  pkey=self.key_filename,
                                  num_retries=self.timeout / 6,
                                  retry_delay=1,
                                  allow_agent=self.allow_agent,
                                  timeout=5)

    # def connectViaProxy(self, host, username, port, identityfile, proxycommand=None):
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

    def getSFTP(self):
        self.logger.info("open sftp")
        return self._client._make_sftp()

    def execute(self, cmd, showout=True, die=True):
        channel, _, stdout, stderr, _ = self._client.run_command(cmd)
        self._client.wait_finished(channel)
        
        def _consume_stream(stream, printer):
            buffer = StringIO()
            for line in stream:
                buffer.write(line+'\n')
                if showout:
                    printer(line)
            return buffer

        out = _consume_stream(stdout, self.logger.info)
        err = _consume_stream(stderr, self.logger.error)

        rc = channel.get_exit_status()

        if rc and die:
            raise j.exceptions.RuntimeError("Cannot execute (ssh):\n%s\noutput:\n%serrors:\n%s" % (cmd, out.getvalue(), err.getvalue()))

        return rc, out.getvalue(), err.getvalue()

    def close(self):
        # TODO: make sure we don't need to clean anything
        pass

    def rsync_up(self, source, dest, recursive=True):
        if dest[0] != "/":
            raise j.exceptions.RuntimeError(
                "dest path should be absolute, need / in beginning of dest path")

        dest = "%s@%s:%s" % (self.login, self.addr, dest)
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
            sshport=self.port,
            recursive=recursive)

    def rsync_down(self, source, dest, source_prefix="", recursive=True):
        if source[0] != "/":
            raise j.exceptions.RuntimeError(
                "source path should be absolute, need / in beginning of source path")
        source = "%s@%s:%s" % (self.login, self.addr, source)
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
            sshport=self.port,
            recursive=recursive)

    @property
    def prefab(self):
        if not self.usesproxy and self._prefab is None:
            executor = j.tools.executor.getSSHBased(
                addr=self.addr, port=self.port, timeout=self.timeout)
            self._prefab = executor.prefab
        if self.usesproxy:
            ex = j.tools.executor.getSSHViaProxy(self.addr)
            self._prefab = j.tools.prefab.get(self)
        return self._prefab

    def ssh_authorize(self, user, key):
        self.prefab.system.ssh.authorize(user, key)

    def portforwardToLocal(self, remoteport, localport):
        self.portforwardKill(localport)
        C = "ssh -L %s:localhost:%s root@%s -p %s" % (
            remoteport, localport, self.addr, self.port)
        print(C)
        pm = j.tools.prefab.local.system.processmanager.get()
        pm.ensure(cmd=C, name="ssh_%s" % localport, wait=0.5)
        print("Test tcp port to:%s" % localport)
        if not j.sal.nettools.waitConnectionTest("127.0.0.1", localport, 10):
            raise RuntimeError("Cannot open ssh forward:%s_%s_%s" %
                               (self, remoteport, localport))
        print("Connection ok")

    def portforwardKill(self, localport):
        print("kill portforward %s" % localport)
        pm = j.tools.prefab.local.system.processmanager.get()
        pm.processmanager.stop('ssh_%s' % localport)

    def SSHAuthorizeKey(
            self,
            keyname=None, keydata=None):
        """
        @keyname name of the key as loaded in ssh-agent if set keydata will be ignored(this requires ssh-agent to be loaded)
        @keydata actual data of private key if set keyname will be ignored
        """
        if keydata:
            key_des = StringIO(keydata)
            p = paramiko.RSAKey.from_private_key(key_des)
            key = '%s ' % p.get_name() + p.get_base64()
        elif not keyname:
            raise j.exceptions.Input("keyname and keydata can't be both empty")
        else:
            key = j.clients.ssh.SSHKeyGetFromAgentPub(keyname)

        rc, _, _ = self.execute("echo '%s' | sudo -S bash -c 'test -e /root/.ssh'" % self.passwd, die=False)
        mkdir_cmd = ''
        if rc > 0:
            mkdir_cmd = 'mkdir -p /root/.ssh;'

        cmd = '''echo '%s' | sudo -S bash -c "%s echo '\n%s' >> /root/.ssh/authorized_keys; chmod 644 /root/.ssh/authorized_keys;chown root:root /root/.ssh/authorized_keys"''' % (
            self.passwd, mkdir_cmd, key)
        self.execute(cmd, showout=False)

        j.clients.ssh.remove_item_from_known_hosts(self.addr)
