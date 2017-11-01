import pytest
from js9 import j

from .AsyncSSHClient import AsyncSSHClient
from .SSHClient import SSHClient


@pytest.fixture(autouse=True)
def no_ssh_transport(monkeypatch):
    """
    mocking SSHClient.transport property
    """
    class Transport:
        def is_active():
            return True
    monkeypatch.setattr(SSHClient, "transport", Transport)


@pytest.fixture(autouse=True)
def no_ssh_close(monkeypatch):
    """
    mocking SSHClient.close method
    """
    def close(dull):
        pass
    monkeypatch.setattr(SSHClient, "close", close)



@pytest.mark.ssh_factory
def test_get_ssh_client_default():
    """
    Checks if j.client.ssh.get() returns SSHClient instance
    with default values
    """
    ssh_client = j.clients.ssh.get()
    assert isinstance(ssh_client, SSHClient)
    assert ssh_client.addr == "localhost"
    assert ssh_client.port == 22
    assert ssh_client.login == "root"
    assert ssh_client.timeout == 5
    assert ssh_client.stdout
    assert ssh_client.forward_agent
    assert ssh_client.allow_agent
    assert ssh_client.look_for_keys
    assert not ssh_client.passwd
    assert not ssh_client.key_filename
    assert not ssh_client.passphrase


@pytest.mark.ssh_factory
def test_get_ssh_client_cache():
    """
    Checks if j.client.ssh.get() caching works properly
    """
    ssh_instance_id_first = id(j.clients.ssh.get())
    ssh_instance_id_second = id(j.clients.ssh.get())
    assert ssh_instance_id_first == ssh_instance_id_second


@pytest.mark.ssh_factory
def test_get_ssh_client_not_cache():
    """
    Checks if j.client.ssh.get() disabling caching works properly
    """
    ssh_instance_id_first = id(j.clients.ssh.get(usecache=False))
    ssh_instance_id_second = id(j.clients.ssh.get(usecache=False))
    assert not ssh_instance_id_first == ssh_instance_id_second


@pytest.mark.ssh_factory
def test_get_async_ssh_default():
    """
    Checks if j.client.ssh.get_async() returns AsyncSSHClient instance
    with default values
    """
    ssh_client = j.clients.ssh.get_async()
    assert isinstance(ssh_client, AsyncSSHClient)
    assert ssh_client.addr == "localhost"
    assert ssh_client.port == 22
    assert ssh_client.login == "root"
    assert ssh_client.timeout == 5
    assert ssh_client.forward_agent
    assert ssh_client.allow_agent
    assert ssh_client.look_for_keys
    assert not ssh_client.password
    assert not ssh_client.key_filename
    assert not ssh_client.passphrase


@pytest.mark.ssh_factory
def test_get_async_ssh_client_cache():
    """
    Checks if j.client.ssh.get_async() caching works properly
    """
    ssh_instance_id_first = id(j.clients.ssh.get_async())
    ssh_instance_id_second = id(j.clients.ssh.get_async())
    assert ssh_instance_id_first == ssh_instance_id_second


@pytest.mark.ssh_factory
def test_get_async_ssh_client_not_cache():
    """
    Checks if j.client.ssh.get_async() disabling caching works properly
    """
    ssh_instance_id_first = id(j.clients.ssh.get_async(usecache=False))
    ssh_instance_id_second = id(j.clients.ssh.get_async(usecache=False))
    assert not ssh_instance_id_first == ssh_instance_id_second


@pytest.mark.ssh_factory
def test_reset_cache():
    """
    Checks if cache is clear after calling reset
    """
    j.clients.ssh.get()
    j.clients.ssh.reset()
    assert j.clients.ssh.cache == {}
