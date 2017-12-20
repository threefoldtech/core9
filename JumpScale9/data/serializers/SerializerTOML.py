
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

    def merge(self,tomlsource, tomlupdate,keys_replace={},add_non_exist=False,die=True,errors=[]):
        """
        the values of the tomlupdate will be applied on tomlsource (are strings)

        @param add_non_exist, if False then will die if there is a value in the dictupdate which is not in the dictsource
        @param keys_replace, key = key to replace with value in the dictsource (which will be the result)
        @param if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource

        @return dictsource,errors
        
        """
        try:
            dictsource = self.load(tomlsource)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
        try:
            dictupdate = self.load(tomlupdate)
        except Exception:
            raise RuntimeError("toml file source is not properly formatted.")
        return j.data.serializer.dict(dictsource, dictupdate,keys_replace=keys_replace,add_non_exist=add_non_exist,die=die,errors=errors)
        
