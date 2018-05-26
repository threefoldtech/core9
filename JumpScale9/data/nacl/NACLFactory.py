from js9 import j

from .NACL import NACL

import nacl.secret
import nacl.utils
import base64

from nacl.public import PrivateKey, SealedBox

JSBASE = j.application.jsbase_get_class()

class NACLFactory(JSBASE):

    def __init__(self):
        JSBASE.__init__(self)        
        self.__jslocation__ = "j.data.nacl"
        self._default = None

    def get(self, name="key", secret="", sshkeyname=""):
        """
        if more than 1 will match ourid (generated from sshagent)
        if path not specified then is ~/.secrets
        """
        return NACL(name, secret, sshkeyname=j.tools.configmanager.keyname)

    @property
    def default(self):
        if self._default is None:
            self._default = self.get()
        return self._default

    @property
    def words(self):
        """
        default words which are securely stored on your filesystem
        js9 'print(j.data.nacl.default.words)'
        """
        return j.data.nacl.default.words

    
    def encrypt(self,secret="",message="",words="",interactive=True):
        """
        secret is any size key
        words are bip39 words e.g. see https://iancoleman.io/bip39/#english

        if words not given then will take from the default nacl local config

        result is base64

        its a combination of nacl symmetric encryption using secret and asymetric encryption using the words
        
        the result is a super strong encryption

        to use

        js9 'j.data.nacl.encrypt()'

        """

        if interactive:
            if not secret:
                secret = j.tools.console.askPassword("your secret")
            if not message:
                message = j.tools.console.askMultiline("your message to encrypt")
                message = message.strip()
            if not words:
                yn=j.tools.console.askYesNo("do you wan to specify secret key as bip39 words?")
                if yn:
                    words= j.tools.console.askString("your bip39 words")

        if words == "":
            words = j.data.nacl.default.words

        #first encrypt symmetric
        secret1 = j.data.hash.md5_string(secret)
        secret1 = bytes(secret1, 'utf-8')
        box = nacl.secret.SecretBox(secret1)
        if j.data.types.str.check(message):
            message = bytes(message, 'utf-8')
        res = box.encrypt(message)

        #now encrypt asymetric using the words
        privkeybytes = j.data.encryption.mnemonic.to_entropy(words)

        pk = PrivateKey(privkeybytes)
        sb = SealedBox(pk.public_key)

        res = sb.encrypt(res)

        res = base64.encodestring(res)

        #LETS VERIFY

        msg = self.decrypt(secret=secret,message=res.decode('utf8'),words=words)
# self.decrypt(secret=secret,message=res,words=words)
        if j.data.types.bytes.check(message):
            message = message.decode('utf8')   

        assert msg.strip() == message.strip()         
        
        if interactive:
            print("encrypted text:\n*************\n")
            print(res.decode('utf8'))


        return res

    def decrypt(self,secret,message,words=""):
        """
        use output from encrypt
        """
        secret = j.data.hash.md5_string(secret)
        secret = bytes(secret, 'utf-8')

        if not j.data.types.bytes.check(message):
            message = bytes(message,'utf8')
            
        message = base64.decodestring(message)

        if words == "":
            words = j.data.nacl.default.words

        privkeybytes = j.data.encryption.mnemonic.to_entropy(words)

        pk = PrivateKey(privkeybytes)
        sb = SealedBox(pk)

        message = sb.decrypt(message)

        #now decrypt symmetric
        box = nacl.secret.SecretBox(secret)
        message =  box.decrypt(message)        
        message = message.decode(encoding='utf-8', errors='strict')
        return message


    def test(self):
        """
        js9 'j.data.nacl.test()'
        """

        res = self.encrypt("1111","something")
        res2 = self.decrypt("1111",res)
        assert "something"==res2

        words = 'oxygen fun inner bachelor cherry pistol knife quarter grass act ceiling wrap another input style profit middle cake slight glance silk rookie caught parade'
        res3 = self.encrypt("1111","something",words=words)
        assert res != res3

        try:
            res4 = self.decrypt("1111",res3)
        except Exception as e:
            assert str(e).find("error occurred")!=-1

        res4 = self.decrypt("1111",res3,words=words)
        assert "something"==res4

        cl = self.default  # get's the default location & generate's keys

        data = b"something"
        r = cl.sign(data)

        assert cl.verify(data,r) == True
        assert cl.verify(b"a",r) == False

        pubsignkey32 = cl.signingkey_pub.encode()

        assert cl.verify(data,r,pubsignkey32) == True

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

        self.logger.info("TEST OK")

    def test_perf(self):
        """
        js9 'j.data.nacl.test_perf()'
        """

        cl = self.default  # get's the default location & generate's keys
        data = b"something"

        nr=10000
        j.tools.timer.start("signing")
        for i in range(nr):  
            p = str(i).encode()      
            r = cl.sign(data+p)
        j.tools.timer.stop(i)
        
        nr=10000
        j.tools.timer.start("encode and verify")
        for i in range(nr):  
            p = str(i).encode()
            r = cl.sign(data+p)      
            assert cl.verify(data+p,r) == True
        j.tools.timer.stop(i)        

        nr=10000
        data2=data*20
        j.tools.timer.start("encryption/decryption assymetric")
        for i in range(nr):  
            a = cl.encrypt(data2)
            b = cl.decrypt(a)
            assert data2==b
        j.tools.timer.stop(i)  


        nr=40000
        secret = b"something111"
        data2=data*20
        j.tools.timer.start("encryption/decryption symmetric")
        for i in range(nr):  
            a = cl.encryptSymmetric(data2,secret=secret)
            b = cl.decryptSymmetric(a,secret=secret)
            assert data2==b
        j.tools.timer.stop(i)  

