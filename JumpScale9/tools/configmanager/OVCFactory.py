from js9 import j

from .OVCClient import OVCClient
from pprint import pprint as print

JSConfigBaseFactory = j.tools.configmanager.base_class_configs

class OVCClientFactory(JSConfigBaseFactory):

    def __init__(self):
        self.__jslocation__ = "j.clients.openvcloud"
        self._logger = None
        self.__imports__ = "ovc"
        JSConfigBaseFactory.__init__(self)
        self._CHILDCLASS = OVCClient
        self.logger = j.logger.get("OVC Client Factory")


    #TODO:*1 change ays to use the config mgmt, in any class where you need e.g. the client just do j.clients.openvcloud.get(instance=...) 
    #       the instance name is only thing which needs to be in the relevan AYS

    # def getFromAYSService(self, service):
    #     """
    #     Returns an OpenvCloud Client object for a given AYS service object.
    #     """
    #     data = {'baseurl': service.model.data.url,
    #             'login': service.model.data.login,
    #             'password_': service.model.data.password,
    #             'JWT_': service.model.data.jwt,
    #             'port': service.model.data.port}
    #     toml = j.data.serializer.toml.dumps(service)
    #     return self.get(data=toml)

    def get_for_operator(self,instance="main",data={}):
        """
        this will return a client always created for the operator even if the appkey has been filled in
        """
        i=self.get(instance,data)
        i.operator = True 
        return i

    def get_for_enduser(self,instance="main",data={}):
        """
        this will return a client always created for the enduser
        """
        i=self.get(instance,data)
        i.operator = False
        return i


    def test(self):

        def mytest_as_operator():
            cl=self.get_for_operator()
            print(cl.config)

            print("locations")
            print(cl.locations)

            print ("images")
            print (cl.get_available_images())

        def mytest_as_enduser():
            cl=self.get_for_enduser()
            print (cl.get_available_images())

        mytest_as_operator()
        mytest_as_enduser()


