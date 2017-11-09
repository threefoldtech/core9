from js9 import j
import os
import capnp

ModelBaseCollection = j.data.capnp.getModelBaseClassCollection()
ModelBase = j.data.capnp.getModelBaseClass()
from JumpScale9.clients.tarantool.KVSInterface import KVSTarantool


class $NameModel(ModelBase):
    '''
    '''
    pass


class $NameCollection(ModelBaseCollection):
    '''
    This class represent a collection of $Names
    It's used to list/find/create new Instance of $Name Model object
    '''

    def __init__(self):
        self.logger = j.logger.get('model.$name')
        category = '$name'
        namespace = ""

        # instanciate the KVS interface on top of tarantool
        cl = j.clients.tarantool.client_get()  # will get the tarantool from the config file, the main connection
        db = KVSTarantool(cl, category)

        mpath = j.sal.fs.getDirName(os.path.abspath(__file__)) + "/model.capnp"
        SchemaCapnp = j.data.capnp.getSchemaFromPath(mpath, name='$Name')

        super().__init__(SchemaCapnp, category=category, namespace=namespace, modelBaseClass=$NameModel, db=db, indexDb=db)

    def new(self):
        return $NameModel(collection=self, new=True)

    def get(self, key):
        return $NameModel(key=key, collection=self, new=False)

    # BELOW IS ALL EXAMPLE CODE WHICH NEEDS TO BE REPLACED

    def list(self):
        """
        list all key in this collection
        """
        return self._db.list()

    def find(self):
        raise NotImplementedError()

    def delete(self, key):
        self._db.delete(key=key)
