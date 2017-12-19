
import pytoml
# import toml

from .SerializerBase import SerializerBase


class SerializerTOML(SerializerBase):

    def dumps(self, obj):
        return pytoml.dumps(obj, sort_keys=True)

    def loads(self, s):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        return pytoml.loads(s)

    def set_value(self,tomltemplate,key,val,overwrite=False):
        """
        start from a toml template
        only works for dicts in root for now

        will check the type & corresponding the type fill in

        """
        newtoml=tomltemplate
        print ("process toml:%s:%s"%(key,val))
        if j.data.types.list.check(newtoml[key]):
            if j.data.types.list.check(val):
                for val0 in val:
                    if val0 not in newtoml[key]:
                        newtoml[key].append(val0)
            else:
                val=str(val).replace("'","")
                if val not in newtoml[key]:
                    newtoml[key].append(val)
        elif j.data.types.bool.check(newtoml[key]):
            if str(val).lower() in ['true',"1","y","yes"]:
                val=True
            else:
                val=False
            newtoml[key]=val
        elif j.data.types.int.check(newtoml[key]):
            newtoml[key]=int(val)
        elif j.data.types.float.check(newtoml[key]):
            newtoml[key]=int(val)
        else:
            newtoml[key]=str(val)

        return newtoml
