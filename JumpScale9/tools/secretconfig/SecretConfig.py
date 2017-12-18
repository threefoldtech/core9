from js9 import j

class SecretConfigFactory:

    def __init__(self):
        self.__jslocation__ = "j.tools.secretconfig"

    def start(self, secret,url):
        """
        e.g. ssh://git@docs.grid.tf:7022/myusername/myconfig.git
        will checkout your configuration which is encrypted
        
        the public key is not encrypted

        """
        sc= SecretConfig(secret,url)
        sc.start()


class SecretConfig:

    def __init__(self, secret, url):
        self.url = url
        self.secret = 

    def start(self):
        try:
            from jose import jwt
            from nacl.public import PrivateKey, SealedBox, PublicKey
        except:
            print("jose not installed will try now")
            j.sal.process.execute("pip3 install python-jose")
            j.sal.process.execute("pip3 install PyNaCl")
        from jose import jwt
        from nacl.public import PrivateKey, SealedBox, PublicKey            
        self.init()



    def init(self):
        self.path=j.clients.git.pullGitRepo(url=self.url)

        self.keyname="key"
        self.path_privatekey = "%s/%s.priv"%(self.path,self.keyname)
        self.path_pubkey = "%s/%s.pub"%(self.path,self.keyname)
        if not j.sal.fs.exists(self.path_privatekey) or not j.sal.fs.exists(self.path_pubkey):
            j.data.nacl.privatekey_generate(self.keyname,self.path)
            



        
