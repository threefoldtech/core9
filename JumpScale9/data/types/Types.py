

'''Definition of several primitive type properties (integer, string,...)'''

from .CustomTypes import *
from .CollectionTypes import *
from .PrimitiveTypes import *

JSBASE = j.application.jsbase_get_class()
class Types(JSBASE):

    def __init__(self):
        self.__jslocation__ = "j.data.types"
        JSBASE.__init__(self)
        self.dict = Dictionary()
        self.list = List()
        self.guid = Guid()
        self.path = Path()
        self.bool = Boolean()
        self.int = Integer()
        self.float = Float()
        self.string = String()
        self.bytes = Bytes()
        self.multiline = StringMultiLine()
        self.set = Set()
        self.ipaddr = IPAddress()
        self.iprange = IPRange()
        self.ipport = IPPort()
        self.duration = Duration()
        self.tel = Tel()
        self.yaml = YAML()
        self.json = JSON()
        self.email = Email()
        self.date = Date()
        self.types_list=[self.bool,self.dict,self.list,self.bytes,self.guid,self.float,self.int,self.multiline,self.string]

    def type_detect(self,val):
        """
        check for most common types
        """
        for ttype in self.types_list:
            if ttype.check(val):
                return ttype
        raise RuntimeError("did not detect val for :%s"%val)


    def getTypeClass(self, ttype):
        """
        type is one of following
        - str, string
        - int, integer
        - float
        - bool,boolean
        - tel, mobile
        - ipaddr, ipaddress
        - ipport, tcpport
        - iprange
        - email
        - multiline
        - list
        - dict
        - yaml
        - set
        - guid
        - duration e.g. 1w, 1d, 1h, 1m, 1
        """
        ttype = ttype.lower().strip()
        if ttype in ["str", "string"]:
            return self.string
        elif ttype in ["int", "integer"]:
            return self.int
        elif ttype == "float":
            return self.float
        elif ttype in ["tel", "mobile"]:
            return self.tel
        elif ttype in ["ipaddr", "ipaddress"]:
            return self.ipaddr
        elif ttype in ["iprange", "ipaddressrange"]:
            return self.iprange
        elif ttype in ["ipport", "ipport"]:
            return self.ipport
        elif ttype in ["bool", "boolean"]:
            return self.bool
        elif ttype == "email":
            return self.email
        elif ttype == "multiline":
            return self.multiline
        elif ttype == "list":
            return self.list
        elif ttype == "dict":
            return self.dict
        elif ttype == "yaml":
            return self.yaml
        elif ttype == "json":
            return self.json
        elif ttype == "set":
            return self.set
        elif ttype == "guid":
            return self.guid
        elif ttype == "duration":
            return self.duration
        elif ttype == "date":
            return self.date

        raise j.exceptions.RuntimeError("did not find type:'%s'" % ttype)

    def get(self, ttype, val):
        """
        type is one of following
        - str, string
        - int, integer
        - float
        - tel, mobile
        - ipaddr, ipaddress
        - ipport, tcpport
        - iprange
        - email
        - multiline
        - list
        - dict
        - set
        - guid
        - duration e.g. 1w, 1d, 1h, 1m, 1
        """
        cl = self.getTypeClass(ttype)
        return cl.get(val)
