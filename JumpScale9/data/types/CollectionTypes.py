'''Definition of several collection types (list, dict, set,...)'''

from .PrimitiveTypes import *


JSBASE = j.application.jsbase_get_class()


class YAML(JSBASE):
    '''Generic dictionary type'''

    def __init__(self):
        JSBASE.__init__(self)
        self.NAME = 'yaml'
        self.BASETYPE = 'dictionary'

    def check(self, value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def get_default(self):
        return dict()

    def fromString(self, s):
        """
        return string from a dict
        """
        if j.data.types.dict.check(s):
            return s
        else:
            # s = s.replace("''", '"')
            j.data.serializer.yaml.loads(s)
            return s

    def toString(self, v):
        return j.data.serializer.yaml.dumps(v)


class JSON(JSBASE):
    def __init__(self):
        JSBASE.__init__(self)
        self.NAME = 'json'
        self.BASETYPE = 'dictionary'


class Dictionary(JSBASE):
    '''Generic dictionary type'''

    def __init__(self):
        JSBASE.__init__(self)
        self.NAME = 'dictionary'
        self.BASETYPE = 'dictionary'

    def check(self, value):
        '''Check whether provided value is a dict'''
        return isinstance(value, dict)

    def get_default(self):
        return dict()
        # if self._default is NO_DEFAULT:
        #     return dict()
        # return dict(self._default)

    def fromString(self, s):
        """
        return string from a dict
        """
        if j.data.types.dict.check(s):
            return s
        else:
            s = s.replace("''", '"')
            j.data.serializer.json.loads(s)
            return s

    def toString(self, v):
        return j.data.serializer.json.dumps(v, True, True)


class List(JSBASE):
    '''Generic list type'''

    def __init__(self):
        JSBASE.__init__(self)
        self.NAME = 'list'
        self.BASETYPE = 'list'

    def check(self, value):
        '''Check whether provided value is a list'''
        return isinstance(value, (list, tuple))

    def get_default(self):
        return list()

    def list_check_1type(self, llist, die=True):
        if len(llist) == 0:
            return True
        ttype = j.data.types.type_detect(llist[0])
        for item in llist:
            res = ttype.check(item)
            if res == False:
                if die:
                    raise RuntimeError("List is not of 1 type.")
                else:
                    return False
        return True

    def fromString(self, v, ttype=None):
        if v == None:
            v = ""
        v = j.data.text.getList(v, ttype)
        v = self.clean(v)
        if self.check(v):
            return v
        else:
            raise ValueError("List not properly formatted.")

    def clean(self, val, toml=False, sort=False, ttype=None):
        if len(val) == 0:
            return val
        if ttype == None:
            ttype = j.data.types.type_detect(val[0])
        res = []
        for item in val:
            if not toml:
                item = ttype.clean(item)
            else:
                item = ttype.toml_string_get(item)
            if item not in res:
                res.append(item)
        res.sort()
        return res

    def toString(self, val, clean=True, sort=False):
        """
        will translate to what we need in toml
        """
        if clean:
            val = self.clean(val, toml=False, sort=sort)
        if len(str(val)) > 30:
            # multiline
            out = ""
            for item in val:
                out += "%s,\n" % item
            out += "\n"
        else:
            out = ""
            for item in val:
                out += " %s," % item
            out = out.strip().strip(",").strip()
        return out

    def toml_string_get(self, val, key="", clean=True, sort=True):
        """
        will translate to what we need in toml
        """
        if clean:
            val = self.clean(val, toml=True, sort=sort)
        if key == "":
            raise NotImplemented()
        else:
            out = ""
            if len(str(val)) > 30:
                # multiline
                out += "%s = [\n" % key
                for item in val:
                    out += "    %s,\n" % item
                out += "]\n\n"
            else:
                out += "%s = [" % key
                for item in val:
                    out += " %s," % item
                out = out.rstrip(",")
                out += " ]\n"
        return out

    def toml_value_get(self, val, key=""):
        """
        will from toml string to value
        """
        if key == "":
            raise NotImplemented()
        else:
            return j.data.serializer.toml.loads(val)


class Set(JSBASE):
    '''Generic set type'''

    def __init__(self):
        JSBASE.__init__(self)
        self.NAME = 'set'
        self.BASETYPE = 'set'

    def check(self, value):
        '''Check whether provided value is a set'''
        return isinstance(value, set)

    def get_default(self):
        return list()
