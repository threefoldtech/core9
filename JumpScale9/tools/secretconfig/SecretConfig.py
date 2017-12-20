from js9 import j

class ConfigObjectBase():

    def __str__(self):
        
        for key,item in self.__dict__.items():

            


class ConfigObject():

    def __init__(self):
        self.ssh_keyname=""
        self.fullname=""
        self.email=""
        self.login_name=""



class SecretConfigFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"

    def start(self, secret,sshkeyname="",giturl=""):
        """
        e.g. the url is e.g. ssh://git@docs.grid.tf:7022/myusername/myconfig.git
        is also stored in the config file in [myconfig] section as giturl & sshkeyname
        
        will checkout your configuration which is encrypted
        
        """

        sc= SecretConfig(secret,sshkeyname=sshkeyname,giturl=giturl)
        sc.start()

    def config_object_baseclass_get(self):
        """
        returns base class for creating a config object with
        """
        return ConfigObjectBase


class SecretConfig:

    def __init__(self, secret, url):
        self.url = url
        self.secret = 

    def start(self):

        self.init()

    def init(self):
        self.path=j.clients.git.pullGitRepo(url=self.url)

            



        
