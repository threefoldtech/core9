from js9 import j

from .NACLClient import NACLClient


class NACLClientFactory:

    def __init__(self):
        self.__jslocation__ = "j.data.nacl"
        self._default = None

    def get(self, name="key", secret="", sshkeyname=""):
        """
        if more than 1 will match ourid (generated from sshagent)
        if path not specified then is ~/.secrets
        """
        return NACLClient(name, secret, sshkeyname=j.tools.configmanager.keyname)

    @property
    def default(self):
        if self._default is None:
            self._default = self.get()
        return self._default

    def test(self):
        """
        js9 'j.data.nacl.test()'
        """

        cl = self.default  # get's the default location & generate's keys

        a = cl.encryptSymmetric("something")
        b = cl.decryptSymmetric(a)

        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric("something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        a = cl.encryptSymmetric(b"something", "qwerty")
        b = cl.decryptSymmetric(a, b"qwerty")
        assert b == b"something"

        # now with hex
        a = cl.encryptSymmetric(b"something", "qwerty", hex=True)
        b = cl.decryptSymmetric(a, b"qwerty", hex=True)
        assert b == b"something"

        a = cl.encrypt(b"something")
        b = cl.decrypt(a)

        assert b == b"something"

        a = cl.encrypt("something")  # non binary start
        b = cl.decrypt(a)

        # now with hex
        a = cl.encrypt("something", hex=True)  # non binary start
        b = cl.decrypt(a, hex=True)
        assert b == b"something"
