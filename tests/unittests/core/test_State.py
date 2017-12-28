import pytest
from unittest.mock import MagicMock
from js9 import j

from  .. import base


STATE_ON_SYSTEM = {'bashprofile': '',
 'cfg_js9': {'dirs': {'BASEDIR': '/opt',
   'BASEDIRJS': '/opt/jumpscale9',
   'BINDIR': '/opt/bin',
   'BUILDDIR': '/host/var/build',
   'CFGDIR': '/hostcfg',
   'CODEDIR': '/opt/code',
   'DATADIR': '/host/var/data',
   'HOMEDIR': '/root',
   'HOSTCFGDIR': '/hostcfg',
   'HOSTDIR': '/host',
   'JSAPPSDIR': '/opt/jumpscale9/apps',
   'LIBDIR': '/opt/lib/',
   'LOGDIR': '/host/var/log',
   'TEMPLATEDIR': '/host/var/templates',
   'TMPDIR': '/tmp',
   'VARDIR': '/host/var'},
  'plugins': {'JumpScale9': '/opt/code/github/jumpscale/core9/JumpScale9/',
   'JumpScale9AYS': '/opt/code/github/jumpscale/ays9/JumpScale9AYS',
   'JumpScale9Lib': '/opt/code/github/jumpscale/lib9/JumpScale9Lib',
   'JumpScale9Prefab': '/opt/code/github/jumpscale/prefab9/JumpScale9Prefab'},
  'redis': {'addr': 'localhost', 'enabled': False, 'port': 6379},
  'system': {'autopip': False,
   'container': True,
   'debug': True,
   'readonly': False}},
 'cfg_me': {'email': {'server': ''},
  'me': {'email': '', 'fullname': '', 'loginname': ''},
  'ssh': {'sshkeyname': 'idonotexist'}},
 'cfg_state': {},
 'env': {'SHELL': '/bin/bash', 'PYTHONUNBUFFERED': '1', 'DATADIR': '/host/var/data', 'BUILDDIR': '/host/var/build', '_': '/usr/local/bin/js9', 'HOSTNAME': 'ays9', 'LOGNAME': 'root', 'PWD': '/opt/code/github/jumpscale/ays9', 'HOSTCFGDIR': '/hostcfg', 'VARDIR': '/host/var', 'HOMEDIR': '/root', 'SHLVL': '5', 'BASEDIR': '/opt', 'TERM': 'screen', 'USER': 'root', 'LC_CTYPE': 'en_US.UTF-8', 'SSH_CLIENT': '172.17.0.1 44878 22', 'CODEDIR': '/opt/code', 'DEBIAN_FRONTEND': 'teletype', 'LOGDIR': '/host/var/log', 'LIBDIR': '/opt/lib/', 'HOME': '/root', 'BINDIR': '/opt/bin', 'LANG': 'en_US.UTF-8', 'HOSTDIR': '/host', 'CFGDIR': '/hostcfg', 'SSH_TTY': '/dev/pts/0', 'LC_ALL': 'en_US.UTF-8', 'SSH_CONNECTION': '172.17.0.1 44882 172.17.0.2 22', 'INITRD': 'no', 'TMUX_PANE': '%2', 'LANGUAGE': 'en_US:en', 'JSAPPSDIR': '/opt/jumpscale9/apps', 'MAIL': '/var/mail/root', 'TMUX': '/tmp/tmux-0/default,457,0', 'TEMPLATEDIR': '/host/var/templates', 'BASEDIRJS': '/opt/jumpscale9', 'TMPDIR': '/tmp', 'PATH': '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'},
 'hostname': 'ays9',
 'iscontainer': True,
 'os_type': 'ubuntu',
 'path_jscfg': '/root/js9host/cfg',
 'uname': 'Linux ays9 3.13.0-86-generic x86_64 x86_64'}

class TestStateClientConfig(base.BaseTestCase):

    def setUp(self):
        """
        Test setup
        """
        super(base.BaseTestCase, self).setUp()
        from JumpScale9.core import State
        executor = MagicMock()
        executor.stateOnSystem = STATE_ON_SYSTEM
        State.j.core.state = State.State(executor)
        j.core.state = State.j.core.state


    def test_clientConfigSetGet(self):
        category = 'test'
        instance = 'foo'
        data = {'hello': 'world'}
        j.core.state.clientConfigSet(category, instance, data)
        cfg = j.core.state.clientConfigGet('test', 'foo')
        assert cfg.data == data
        assert cfg.category == category
        assert cfg.instance == instance
        assert cfg.key == "client_%s_%s" % (category, instance)

        # when getting from non existing instance, return an empty ClientConfig
        instance = 'nonexists'
        cfg = j.core.state.clientConfigGet(category, instance)
        assert cfg.data == {}
        assert cfg.category == category
        assert cfg.instance == instance
        assert cfg.key == "client_%s_%s" % (category, instance)

    def test_clientConfigSetGet_wrong_data_type(self):
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', "string")
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', 1)
        with pytest.raises(ValueError):
            j.core.state.clientConfigSet('test', 'foo', ['hello', 'world'])

    def test_clientConfigList(self):
        # set some config
        category = 'test'
        instance = 'foo'
        data = {'hello': 'world'}
        j.core.state.clientConfigSet(category, instance + "1", data)
        j.core.state.clientConfigSet(category, instance + "2", data)

        cfgs = j.core.state.clientConfigList(category)
        assert len(cfgs) == 2

        cfgs = j.core.state.clientConfigList('nonexists')
        assert len(cfgs) == 0
