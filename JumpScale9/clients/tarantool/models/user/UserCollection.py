from js9 import j
import os
import capnp

ModelBaseCollection=j.data.capnp.getModelBaseClassCollection()
ModelBase=j.data.capnp.getModelBaseClass()

class UserModel(ModelBase):
    '''
    '''

    def index(self):
        #no need to put indexes because will be done by capnp
        pass

    def save(self):
        self.reSerialize()
        self._pre_save()
        buff = self.dbobj.to_bytes()                    
        return self.collection._db.call("model_user_set",(buff))

    def delete(self,name="",id=0):                    
        return self.collection._db.call("model_user_del",(name,id))

class UserCollection(ModelBaseCollection):
    '''
    This class represent a collection of Users
    It's used to list/find/create new Instance of User Model object
    '''

    def __init__(self):
        self.logger = j.logger.get('model.user')
        category = 'user'
        namespace = ""
        db =  j.clients.tarantool.client_get() #will get the tarantool from the config file, the main connection
        mpath=j.sal.fs.getDirName(os.path.abspath(__file__))+"/model.capnp"
        SchemaCapnp=j.data.capnp.getSchemaFromPath(mpath,name='User')
        super().__init__(SchemaCapnp, category=category, namespace=namespace, modelBaseClass=UserModel, db=db, indexDb=db)

    def get(self,name="",id=0):                    
        buff=self._db.call("model_user_get",(name,id))
        print(456789)
        from IPython import embed;embed(colors='Linux')
        o
        print(ddict)  


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

