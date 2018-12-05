from unittest import TestCase
from jumpscale import j

class TestBackend(TestCase):

    @classmethod
    def setUpClass(self):
        print(type(j.tools.configmanager._impl))

    def setUp(self):
        self.name = 'test'
        self.token = 'token'
        j.clients.zerotier.new(self.name, data={'token_': self.token})

    def tearDown(self):
        j.clients.zerotier.delete(self.name)

    def test_client_exists(self):
        assert j.clients.zerotier.exists(self.name) == True

    def test_client_get(self):
        client = j.clients.zerotier.get(self.name)
        data =  {'networkid': '', 'nodeids': '', 'token_': self.token}
        assert client.config.data == data

    def test_client_list(self):
        assert self.name in j.clients.zerotier.list()

    def test_client_delete(self):
        j.clients.zerotier.delete(self.name)
        assert self.name not in j.clients.zerotier.list()

    def test_change_data(self):
        client = j.clients.zerotier.get(self.name, data={'token_': 'newtoken'})
        assert client.config.data['token_'] == 'newtoken'

    def test_create_with_get(self):
        j.clients.zerotier.get('new', data={'token_': 'newtoken'})
        assert j.clients.zerotier.exists('new') == True
        j.clients.zerotier.delete('new')
        assert j.clients.zerotier.exists('new') == False
