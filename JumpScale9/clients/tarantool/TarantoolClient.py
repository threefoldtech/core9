from js9 import j
import tarantool
import os
import sys

class Models():
    pass
class TarantoolClient():

    def __init__(self,client):
        self.db = client
        self.call = client.call
        self.models = Models()

    @property
    def _path(self):
        return j.sal.fs.getDirName(os.path.abspath(__file__))
        

    # def addSpace(self):
    #     C = "s = box.schema.space.create('tester',{if_not_exists = true})"

    def getQueue(self, name, ttl=0, delay=0):
        return TarantoolQueue(self, name, ttl=ttl, delay=delay)

    def eval(self, code):
        code = j.data.text.strip(code)
        self.db.eval(code)

    def userGrant(self, user="guest", operation=1, objtype="universe", objname=""):
        """
        @param objtype the type of object - "space" or "function" or "universe",
        @param objname the name of object only relevant for space or function
        @param opstype in integer the type of operation - "read" = 1, or "write" = 2, or "execute" = 4, or a combination such as "read,write,execute".
        """
        if objname == "":
            C = "box.schema.user.grant('%s',%s,'%s')" % (
                user, operation, objtype)
        else:
            C = "box.schema.user.grant('%s',%s,'%s','%s')" % (
                user, operation, objtype, objname)

        self.db.eval(C)

    def addFunction(self, code=""):
        """
        example:
            function echo3(name)
              return name
            end

        then use with self.call...
        """
        self.eval(code)

    def _pyModelFix(self,path,name,dbtype,login,passwd):
        lcontent=j.sal.fs.readFile(path)

        if lcontent.find("ModelBaseCollection")==-1:
            C="""
            from js9 import j
            import os
            import capnp

            ModelBaseCollection=j.data.capnp.getModelBaseClassCollection()
            ModelBase=j.data.capnp.getModelBaseClass()

            class $NameModel(ModelBase):
                '''
                '''

                def index(self):
                    #no need to put indexes because will be done by capnp
                    pass

                def save(self):
                    self.reSerialize()
                    self._pre_save()
                    buff = self.dbobj.to_bytes()                    
                    ddict=self.collection._db.call("model_$name_set",(buff)) #call the stored procedure which will put in db
                    print(ddict)

            class $NameCollection(ModelBaseCollection):
                '''
                This class represent a collection of $Names
                It's used to list/find/create new Instance of $Name Model object
                '''

                def __init__(self):
                    self.logger = j.logger.get('model.$name')
                    category = '$name'
                    namespace = ""
                    db =  j.clients.tarantool.client_get() #will get the tarantool from the config file, the main connection
                    mpath=j.sal.fs.getDirName(os.path.abspath(__file__))+"/model.capnp"
                    SchemaCapnp=j.data.capnp.getSchemaFromPath(mpath,name='$Name')
                    super().__init__(SchemaCapnp, category=category, namespace=namespace, modelBaseClass=$NameModel, db=db, indexDb=db)

                ##BELOW IS ALL EXAMPLE CODE WHICH NEEDS TO BE REPLACED

                def list(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999,tags=[], returnIndex=False):
                    self.db
                    return res

                def find(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, tags=[]):
                    res = []
                    for key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch, tags):
                        if self.get(key):
                            res.append(self.get(key))
                    return res


                def delete(self, actor="", service="", action="", state="", serviceKey="", fromEpoch=0, toEpoch=9999999999999, tags=[]):
                    '''
                    Delete a job
                    :param actor: actor name
                    :param service: service name
                    :param action: action name
                    :param state: state of the job to be deleted
                    :param serviceKey: key identifying the service
                    :param fromEpoch: runs in this period will be deleted
                    :param toEpoch: runs in this period will be deleted
                    :param tags: jobs with these tags will be deleted
                    '''
                    for index, key in self.list(actor, service, action, state, serviceKey, fromEpoch, toEpoch, tags, True):
                        self._index.index_remove(keys=index)
                        self._db.delete(key=key)

            """

            lcontent+=j.data.text.strip(C)

        lcontent=lcontent.replace("$dbtype",dbtype)
        lcontent=lcontent.replace("$name",name)
        nameUpper=name[0].upper()+name[1:]
        lcontent=lcontent.replace("$Name",nameUpper)
        lcontent=lcontent.replace("mymodelname",name)
        lcontent=lcontent.replace("$login",login)
        lcontent=lcontent.replace("$passwd",passwd)
        
        j.sal.fs.writeFile(path,lcontent)    

        # print(lcontent)


    def _luaModelFix(self,path,name,dbtype,login,passwd):
        lcontent=j.sal.fs.readFile(path)
        nameUpper=name[0].upper()+name[1:]

        funcname='model_%s_get'%name
        if lcontent.find("function %s"%funcname)==-1:
            C="""
            function $funcname(id)
                return box.space.$name:get(id)
            end

            box.schema.func.create('$funcname', {if_not_exists = true})
            box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

            """
            lcontent+=j.data.text.strip(C.replace("$funcname",funcname))

        funcname='model_%s_get_json'%name
        if lcontent.find("function %s"%funcname)==-1:
            C="""
            function $funcname(id)
                bdata= box.space.$name:get(id)
                return model_capnp_$name.$Name.parse(bdata)
            end

            box.schema.func.create('$funcname', {if_not_exists = true})
            box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

            """
            lcontent+=j.data.text.strip(C.replace("$funcname",funcname))

        funcname='model_%s_set'%name
        if lcontent.find("function %s"%funcname)==-1:
            C="""
            function $funcname(id,data)
                obj=model_capnp_$name.$Name.parse(data) --deserialze capnp
                if id==0 then
                    res = box.space.$name:auto_increment({data})
                    return res[1]
                else
                    box.space.$name:put{id,data}
                    return id
                end                
            end

            box.schema.func.create('$funcname', {if_not_exists = true})
            box.schema.user.grant('$login', 'execute', 'function','$funcname',{ if_not_exists= true})

            """            
            lcontent+=j.data.text.strip(C.replace("$funcname",funcname))

        funcname='model_%s_del'%name
        if lcontent.find("function %s"%funcname)==-1:
            C="""
            function $funcname(guid)
                return box.$name.user:delete(id)
            end
            box.schema.func.create('$funcname', {if_not_exists = true})
            box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

            """     
            lcontent+=j.data.text.strip(C.replace("$funcname",funcname))
        
        funcname='model_%s_find'%name
        if lcontent.find("function %s"%funcname)==-1:
            C="""
            function $funcname(query)
                --todo
                return True
            end
            box.schema.func.create('$funcname', {if_not_exists = true})
            box.schema.user.grant('$login', 'execute', 'function', '$funcname',{ if_not_exists= true})

            """     
            lcontent+=j.data.text.strip(C.replace("$funcname",funcname))

        lcontent=lcontent.replace("$dbtype",dbtype)
        lcontent=lcontent.replace("$name",name)
        lcontent=lcontent.replace("$Name",nameUpper)
        lcontent=lcontent.replace("mymodelname",name)
        lcontent=lcontent.replace("$login",login)
        lcontent=lcontent.replace("$passwd",passwd)
        
        j.sal.fs.writeFile(path,lcontent)    

        # print(lcontent)


    def addModels(self,path="",login="user",passwd="secret",dbtype="memtx"):
        """
        @PARAM path is the directory where the capnp, lua, ... can be found, each subdir has a model name
               if not specified will look for models underneith the capnp extension
        @PARAM dbtype vinyl or memtx

        will be available in tarantool as require("model_capnp_$name")  $name of the model which is the directory name
        and the lua model as "model_$name" which has the required stored procedures _set _get _delete _find
        """

        if path=="":
            path="%s/models"%self._path

        if path not in sys.path:
            sys.path.append(path)


        for name in j.sal.fs.listDirsInDir(path, False,True):
            nameUpper=name[0].upper()+name[1:]
            cpath=j.sal.fs.joinPaths(path,name,"model.capnp")
            lpath=j.sal.fs.joinPaths(path,name,"model.lua")
            ppath=j.sal.fs.joinPaths(path,name,"%sCollection.py"%nameUpper)
            j.sal.fs.touch(j.sal.fs.joinPaths(path,name,"__init__.py"))
            if j.sal.fs.exists(cpath):
                # j.sal.fs.readFile(cpath)
                res=j.data.capnp.schema_generate_lua(cpath)
                self.addScript(res,"model_capnp_%s"%name)
                j.sal.fs.remove(res)

            if not j.sal.fs.exists(lpath):
                C="""
                box.schema.space.create('mymodelname',{if_not_exists= true, engine="$dbtype"})

                box.space.mymodelname:create_index('primary',{ type = 'hash', parts = {1, 'unsigned'}, if_not_exists= true})
                -- box.space.mymodelname:create_index('secondary', {type = 'tree', parts = {2, 'string'}, if_not_exists= true})

                box.schema.user.create('$login', {password = '$passwd', if_not_exists= true})

                """
                j.sal.fs.writeFile(lpath,j.data.text.strip(C)) 

            if not j.sal.fs.exists(ppath):
                C="""                
                """
                j.sal.fs.writeFile(ppath,j.data.text.strip(C)) 

            self._luaModelFix(path=lpath,name=name,dbtype=dbtype,login=login,passwd=passwd)
            self._pyModelFix(path=ppath,name=name,dbtype=dbtype,login=login,passwd=passwd)

            self.addScript(lpath,"model_%s"%name)

            cmd="from $name import $NameCollection"
            cmd=cmd.replace("$name",name)
            cmd=cmd.replace("$Name",nameUpper)
            exec(cmd)
            exec("self.models.$NameCollection=$NameCollection.$NameCollection()".replace("$Name",nameUpper))
        

    # def bootstrap(self, code):
    #     code = """
    #         box.once("bootstrap", function()
    #             box.schema.space.create('$space')
    #             box.space.test:create_index('primary',
    #                 { type = 'TREE', parts = {1, 'NUM'}})
    #         end)
    #         box.schema.user.grant('$user', 'read,write,execute', 'universe')
    #         """
    #     code = code.replace("$space", space)
    #     self.eval(code)

    def addScripts(self,path=None,require=False):
        """
        load all lua scripts in path (sorted) & execute in the tarantool instance

        if @path empty then path = testscripts subdir of this extension
        """
        if path==None:
            path="%s/testscripts"%self._path
        for path0 in j.sal.fs.listFilesInDir(path, recursive=False, filter="*.lua"):
            self.addScript(path0,require=require)

    def addScript(self,path,name="",require=True):
        print("addscript %s %s"%(path,name))
        C=j.sal.fs.readFile(path)
        if name=="":
            name=j.sal.fs.getBaseName(path)[:-4]
        #write the lua script to the location on server
        self.db.call("add_lua_script",(name,C))
        if require:
            cmd="%s=require('%s')"%(name,name)
            print(cmd)
            self.eval(cmd)
            
    