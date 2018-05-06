import pytest
import unittest
import sys
from unittest.mock import MagicMock
from unittest.mock import patch
from js9 import j

from ... import base


class TestSSHClientFactory(base.BaseTestCase):

    # @pytest.mark.ssh_factory
    # def test_get_ssh_client_default(self):
    #     """
    #     Checks if SSHClient instance is created with default values
    #     """
    #     ssh_client = j.clients.ssh.get()
    #     assert isinstance(ssh_client, MagicMock)
    #
    #     from JumpScale9.clients.ssh import SSHClientFactory
    #     ssh_client_factory = SSHClientFactory.SSHClientFactory()
    #     ssh_client_factory.reset()
    #     ssh_client = ssh_client_factory.get()
    #
    #     assert ssh_client.port == 22
    #     assert ssh_client.timeout == 5
    #     assert ssh_client.stdout
    #     assert ssh_client.forward_agent
    #     assert ssh_client.allow_agent
    #     assert ssh_client.look_for_keys
    #     assert not ssh_client.passwd
    #     assert not ssh_client.key_filename
    #     assert not ssh_client.passphrase
    #
    #     # assert the expected calls to j namespace are executed
    #     assert j.data.hash.md5_string.called

    @pytest.mark.ssh_factory
    def test_get_ssh_client_cache(self):
        """
        Checks if j.client.ssh.get() caching works properly
        """
        with patch('JumpScale9.clients.ssh.SSHClient.SSHClient') as SSHClient:
            from JumpScale9.clients.ssh import SSHClientFactory
            ssh_client_factory = SSHClientFactory.SSHClientFactory()
            ssh_client_factory.reset()
            ssh_instance_id_first = id(ssh_client_factory.get())
            ssh_instance_id_second = id(ssh_client_factory.get())
            assert ssh_instance_id_first == ssh_instance_id_second

    # @pytest.mark.ssh_factory
    # def test_get_ssh_client_not_cache(self):
    #     """
    #     Checks if j.client.ssh.get() disabling caching works properly
    #     """
    #     from JumpScale9.clients.ssh import SSHClientFactory
    #     ssh_client_factory = SSHClientFactory.SSHClientFactory()
    #     ssh_client_factory.reset()
    #     ssh_instance_id_first = id(ssh_client_factory.get(usecache=False))
    #     ssh_instance_id_second = id(ssh_client_factory.get(usecache=False))
    #     assert not ssh_instance_id_first == ssh_instance_id_second

    # @pytest.mark.ssh_factory
    # def test_reset_cache(self):
    #     """
    #     Checks if cache is clear after calling reset
    #     """
    #     from JumpScale9.clients.ssh import SSHClientFactory
    #     ssh_client_factory = SSHClientFactory.SSHClientFactory()
    #     ssh_client_factory.reset()
    #     assert ssh_client_factory.cache == {}
