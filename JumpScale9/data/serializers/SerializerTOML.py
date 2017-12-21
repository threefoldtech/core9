from JumpScale9 import j
import pytoml
# import toml

from .SerializerBase import SerializerBase

testtemplate="""
name = ''

multiline = ''

nr = 0
nr2 = 0
nr3 = 0
nr4 = 0.0
nr5 = 0.0

bbool = true
bbool2 = true
bbool3 = true

list1 = [ ]
list2 = [ ]
list3 = [ ]
list4 = [ ]
list5 = [ ]

"""

testtoml="""
name = 'something'

multiline = '''
    these are multiple lines
    next line
    '''

nr = 87
nr2 = ""
nr3 = "1"
nr4 = "34.4"
nr5 = 34.4

bbool = 1
bbool2 = true
bbool3 = 0

list1 = "4,1,2,3"
list2 = [ 3, 1, 2, 3 ]
list3 = [ "a", " b ", "   c  " ]
list4 = [ "ab" ]
list5 = "d,a,a,b,c"

"""



class SerializerTOML(SerializerBase):

    def fancydumps(self,obj,secure=False):
        """
        if secure then will look for key's ending with _ and will use your secret key to encrypt (see nacl client)
        """

        if not j.data.types.dict.check(obj):
            raise j.exceptions.Input("need to be dict")

        keys=[item for item in obj.keys()]
        keys.sort()

        out=""
        prefix=""
        lastprefix=""
        for key in keys:

            val=obj[key]

            #get some vertical spaces between groups which are not equal
            if "." in key:
                prefix,key.split(".",1)
            elif "_" in key:
                prefix,key.split("_",1)
            else:
                prefix=key[0:2]
            if prefix!=lastprefix:
                out+="\n"
                lastprefix=prefix

            ttype=j.data.types.type_detect(val)
            if secure and key.endswith("_") and ttype.BASETYPE == "string":
                val = j.data.nacl.default.encryptSymmetric(val,hex=True,salt=val)

            out+="%s\n"%(ttype.toml_string_get(val,key=key))

            # else:
            #     raise RuntimeError("error in fancydumps for %s in %s"%(key,obj))

        return j.data.text.strip(out)


    def dumps(self, obj):
        return pytoml.dumps(obj, sort_keys=True)

    def loads(self, s,secure=False):
        if isinstance(s, bytes):
            s = s.decode('utf-8')
        val = pytoml.loads(s)
        if secure and j.data.types.dict.check(val):
            res={}
            for key,item in val.items():
                if key.endswith("_"):
                    res[key]=j.data.nacl.default.decryptSymmetric(item,hex=True).decode()
            val=res
        return val


    def merge(self,tomlsource, tomlupdate,keys_replace={},add_non_exist=False,die=True,errors=[],listunique=False,listsort=True,liststrip=True):
        """
        the values of the tomlupdate will be applied on tomlsource (are strings or dicts)

        @param add_non_exist, if False then will die if there is a value in the dictupdate which is not in the dictsource
        @param keys_replace, key = key to replace with value in the dictsource (which will be the result)
        @param if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource

        listsort means that items in list will be sorted (list at level 1 under dict)

        @return dict,errors
        
        """
        if j.data.types.string.check(tomlsource):
            try:
                dictsource = self.loads(tomlsource)
            except Exception:
                raise RuntimeError("toml file source is not properly formatted.")
        else:
            dictsource = tomlsource
        if j.data.types.string.check(tomlupdate):
            try:
                dictupdate = self.loads(tomlupdate)
            except Exception:
                raise RuntimeError("toml file source is not properly formatted.")
        else:
            dictupdate = tomlupdate
        
        return j.data.serializer.dict.merge(dictsource, dictupdate,keys_replace=keys_replace,add_non_exist=add_non_exist,die=die,\
                errors=errors,listunique=listunique,listsort=listsort,liststrip=liststrip)
        

    def test(self):

        ddict=self.loads(testtoml)
        template=self.loads(testtemplate)

        ddictout,errors=self.merge(template,ddict,listunique=True)

        ddicttest={'name': 'something', 'multiline': 'these are multiple lines\nnext line\n', 'nr': 87, 'nr2': 0, 'nr3': 1, 'nr4': 34.4, 'nr5': 34.4, 'bbool': True, 'bbool2': True, 'bbool3': False, 'list1': ['1', '2', '3', '4'], 'list2': [1, 2, 3], 'list3': ['a', 'b', 'c'], 'list4': ['ab'], 'list5': ['a', 'b', 'c', 'd']}

        print(ddictout)

        assert ddictout==ddicttest

        ddictmerge={'nr': 88}

        #start from previous one, update
        ddictout,errors=self.merge(ddicttest,ddictmerge,listunique=True)

        ddicttest={'name': 'something', 'multiline': 'these are multiple lines\nnext line\n', 'nr': 88, 'nr2': 0, 'nr3': 1, 'nr4': 34.4, 'nr5': 34.4, 'bbool': True, 'bbool2': True, 'bbool3': False, 'list1': ['1', '2', '3', '4'], 'list2': [1, 2, 3], 'list3': ['a', 'b', 'c'], 'list4': ['ab'], 'list5': ['a', 'b', 'c', 'd']}

        assert ddictout==ddicttest

        ddictmerge={'nr_nonexist': 88}

        #needs to throw error
        try:
            error=0
            ddictout,errors=self.merge(ddicttest,ddictmerge,listunique=True)
        except:
            error=1
        assert 1

        ddictmerge={}
        ddictmerge["list1"]=[]
        for i in range(20):
            ddictmerge["list1"].append("this is a test %s"%i)
        ddictout,errors=self.merge(ddicttest,ddictmerge,listunique=True)


        yyaml=self.fancydumps(ddictout)
        print (yyaml)

        compare={'bbool': True,
            'bbool2': True,
            'bbool3': False,
            'list1': ['this is a test 0',
            'this is a test 1',
            'this is a test 10',
            'this is a test 11',
            'this is a test 12',
            'this is a test 13',
            'this is a test 14',
            'this is a test 15',
            'this is a test 16',
            'this is a test 17',
            'this is a test 18',
            'this is a test 19',
            'this is a test 2',
            'this is a test 3',
            'this is a test 4',
            'this is a test 5',
            'this is a test 6',
            'this is a test 7',
            'this is a test 8',
            'this is a test 9'],
            'list2': [1, 2, 3],
            'list3': ['a', 'b', 'c'],
            'list4': ['ab'],
            'list5': ['a', 'b', 'c', 'd'],
            'multiline': '    these are multiple lines\n    next line\n    ',
            'name': 'something',
            'nr': 88,
            'nr2': 0,
            'nr3': 1,
            'nr4': 34.4,
            'nr5': 34.4}

        res=self.loads(yyaml)

        assert res==compare


