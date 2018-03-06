

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
        self.integer = self.int
        self.float = Float()
        self.string = String()
        self.str = self.string
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
        self.numeric = Numeric()

        self._dict = Dictionary
        self._list = List
        self._guid = Guid
        self._path = Path
        self._bool = Boolean
        self._int = Integer
        self._float = Float
        self._string = String
        self._bytes = Bytes
        self._multiline = StringMultiLine
        self._set = Set
        self._ipaddr = IPAddress
        self._iprange = IPRange
        self._ipport = IPPort
        self._duration = Duration
        self._tel = Tel
        self._yaml = YAML
        self._json = JSON
        self._email = Email
        self._date = Date
        self._duration = Duration
        self._numeric = Numeric

        self.types_list = [self.bool, self.dict, self.list, self.bytes,
                           self.guid, self.float, self.int, self.multiline, self.string, self.date, self.numeric]

    def type_detect(self, val):
        """
        check for most common types
        """
        for ttype in self.types_list:
            if ttype.check(val):
                return ttype
        raise RuntimeError("did not detect val for :%s" % val)

    def get(self, ttype, return_class=False):
        """
        type is one of following
        - s, str, string
        - i, int, integer
        - f, float
        - b, bool,boolean
        - tel, mobile
        - d, date
        - n, numeric
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
        - dur, duration e.g. 1w, 1d, 1h, 1m, 1
        """
        ttype = ttype.lower().strip()
        if ttype in ["s", "str", "string"]:
            res = self._string
        elif ttype in ["i","int", "integer"]:
            res = self._int
        elif ttype in ["f","float"]:
            res = self._float
        elif ttype in ["tel", "mobile"]:
            res = self._tel
        elif ttype in ["ipaddr", "ipaddress"]:
            res = self._ipaddr
        elif ttype in ["iprange", "ipaddressrange"]:
            res = self._iprange
        elif ttype in ["ipport", "ipport"]:
            res = self._ipport
        elif ttype in ["b","bool", "boolean"]:
            res = self._bool
        elif ttype == "email":
            res = self._email
        elif ttype == "multiline":
            res = self._multiline
        elif ttype in ["d", "date"]:
            res = self._date
        elif ttype in ["n", "num","numeric"]:
            res = self._numeric
        elif ttype.startswith("l"):
            res = self._list
            if len(ttype)==2:
                if return_class:
                    raise RuntimeError("cannot return class if subtype specified")
                tt = self.list
                ttsub = self.get(ttype[1],return_class=True)
                tt.SUBTYPE = ttsub()
                return tt
        elif ttype == "dict":
            res = self._dict
        elif ttype == "yaml":
            res = self._yaml
        elif ttype == "json":
            res = self._json
        elif ttype == "set":
            res = self._set
        elif ttype == "guid":
            res = self._guid
        elif ttype in ["dur","duration"]:
            res = self._duration
        else:
            raise j.exceptions.RuntimeError("did not find type:'%s'" % ttype)

        if return_class:
            return res
        else:
            return res()



