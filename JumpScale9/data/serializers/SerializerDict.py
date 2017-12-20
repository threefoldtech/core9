
# import blosc


class SerializerDict:


    def set_value(self,dictsource,key,val,add_non_exist=False,die=True,errors=[]):
        """
        start from a dict template (we only go 1 level deep)

        will check the type & corresponding the type fill in

        @return dict,errors=[]

        in errors there will be key's which are not found in dictsource

        """
        print ("add to ddict:%s:%s"%(key,val))

        if key not in dictsource.keys():
            if add_non_exist:
                dictsource[key]=val   
                return dictsource,errors             
            else:
                if die:
                    raise j.exceptions.Input("dictsource does not have key:%s, can insert value"%key)
                else:
                    errors.append(key)


        if j.data.types.list.check(dictsource[key]):
            if j.data.types.list.check(val):
                #avoid duplicates in list
                for val0 in val:
                    if val0 not in dictsource[key]:
                        dictsource[key].append(val0)
            else:
                val=str(val).replace("'","")
                if val not in dictsource[key]:
                    dictsource[key].append(val)
        elif j.data.types.bool.check(dictsource[key]):
            if str(val).lower() in ['true',"1","y","yes"]:
                val=True
            else:
                val=False
            dictsource[key]=val
        elif j.data.types.int.check(dictsource[key]):
            dictsource[key]=int(val)
        elif j.data.types.float.check(dictsource[key]):
            dictsource[key]=int(val)
        else:
            dictsource[key]=str(val)

        return dictsource,errors

    def merge(self,dictsource, dictupdate,keys_replace={},add_non_exist=False,die=True,errors=[]):
        """
        the values of the dictupdate will be applied on dictsource

        @param add_non_exist, if False then will die if there is a value in the dictupdate which is not in the dictsource
        @param keys_replace, key = key to replace with value in the dictsource (which will be the result)
        @param if die=False then will return errors, the list has the keys which were in dictupdate but not in dictsource

        @return dictsource,errors

        """
        if not j.data.types.dict.check(dictsource) or not j.data.types.dict.check(dictupdate):
            raise j.exceptions.Input("dictsource and dictupdate need to be dicts")

        for key, val in dictupdate.items():                
            if key in keys_replace.keys():                    
                key=keys_replace[key]
            dictsource,errors = self.set_value(dictsource, key, val,add_non_exist=add_non_exist,die=die,errors=errors)
        return dictsource,errors
    