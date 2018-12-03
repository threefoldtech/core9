
from jumpscale import j
from pprint import pprint as print

from .ZDBClient import ZDBClient

JSBASE = j.application.jsbase_get_class()


class ZDBFactory(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.clients.zdbsimple"
        # super(ZDBSimpleFactory, self).__init__(JSBASE)

    def get(self, addr="localhost", port=9900, adminsecret="", secrets="", mode="user"):
        """
        :param secrets: $ns:$secret,... or $secret which will be defaulf for all namespaces
        :param addr:
        :param port:
        :param adminsecret: the main secret
        :param mode: seq or user
        :return:
        """
        return ZDBClient(addr, port, adminsecret, secrets, mode)
