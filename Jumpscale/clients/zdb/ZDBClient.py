import os
import struct
from pprint import pprint as print

from jumpscale import j

from .ZDBClientNS import ZDBClientNS

JSBASE = j.application.jsbase_get_class()


class ZDBClient(JSBASE):

    def __init__(self, addr="127.0.0.1", port=9900, adminsecret="", secrets="", namespace="default", mode="user"):
        """
        is connection to ZDB

        - secret is also the name of the directory where zdb data is for this namespace/secret

        config params:
            secrets {str} -- format: $ns:$secret,... or $secret then will be same for all namespaces
            port {[int} -- (default: 9900)
            mode -- user,seq(uential) see https://github.com/rivine/0-db/blob/master/README.md
            adminsecret does not have to be set, but when you want to create namespaces it is a must

        """
        super().__init__()
        self.addr = addr
        self.port = port
        self._adminsecret = adminsecret
        self._secrets = secrets
        self.mode = mode
        self._namespace = namespace
        self.namespaces = {}
        # default namespace should always exist

    @property
    def secrets(self):
        res = {}
        if "," in self._secrets:
            items = self._secrets.split(",")
            for item in items:
                if item.strip() == "":
                    continue
                nsname, secret = item.split(":")
                res[nsname.lower().strip()] = secret.strip()
        else:
            res["default"] = self._secrets.strip()
        return res

    def namespace_exists(self, name):
        try:
            self.namespace_system.redis.execute_command("NSINFO", name)
            return True
        except Exception as e:
            if not "Namespace not found" in str(e):
                raise RuntimeError("could not check namespace:%s, error:%s" % (name, e))
            return False

    def namespace_get(self, name):
        if not name in self.namespaces:
            self.namespaces[name] = ZDBClientNS(self, name)
        return self.namespaces[name]

    @property
    def namespace(self):
        return self.namespace_get(self._namespace)

    def ping(self):
        """
        go to default namespace & ping
        :return:
        """
        d = self.namespace_get("default")
        return d.redis.ping()

    @property
    def namespace_system(self):
        return self.namespace_get("default")

    def namespace_new(self, name, secret="", maxsize=0, die=False):
        if self.namespace_exists(name):
            if die:
                raise RuntimeError("namespace already exists:%s" % name)
            return self.namespace_get(name)

        if secret is "" and "default" in self.secrets.keys():
            secret = self.secrets["default"]

        cl = self.namespace_system
        cl.redis.execute_command("NSNEW", name)
        if secret is not "":
            cl.redis.execute_command("NSSET", name, "password", secret)
            cl.redis.execute_command("NSSET", name, "public", "no")
        self.logger.debug("namespace:%s NEW" % name)

        if maxsize is not 0:
            cl.redis.execute_command("NSSET", name, "maxsize", maxsize)

        return self.namespace_get(name)

    def namespace_delete(self, name):
        if not self.namespace_exists(name):
            return

        return self.redis.execute_command("NSDEL", name)
