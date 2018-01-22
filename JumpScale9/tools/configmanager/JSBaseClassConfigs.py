from inspect import isclass

from js9 import j


class JSBaseClassConfigs:
    """
    collection class to deal with multiple instances
    """

    def __init__(self, child_class, single_item=False):
        """
        @param child_class: The class that this factory will create
        @param single_item: In the case this factory will only ever return the same instance
                            set single_item to True
        """
        if not isclass(child_class):
            raise TypeError("child_class need to be a class not %s" %
                            type(child_class))

        self.items = {}
        self._single_item = single_item
        self._child_class = child_class

        # self.getall()

    def get(self, instance="main", data={}, create=True, die=True):
        """
        Get an instance of the child_class set in the constructor

        @param instance: instance name to get. If an instance is already loaded in memory, return it
        @data data: dictionary of data use to configure the instance
        """
        if instance in self.items:
            # print("CONFIG:GET:INSTANCEEXISTS")
            if data != {}:
                self.items[instance].config.data = data
                self.items[instance].config.save()
                # print("SAVE")
        else:
            if create:
                # print("CONFIG:GET:CREATE")
                self.items[instance] = self._child_class(
                    instance=instance, data=data, parent=self)
            else:
                if die:
                    raise RuntimeError(
                        "could not find instance:%s" % (instance))
                else:
                    return None
        return self.items[instance]

    def exists(self, instance):
        return instance in self.list()

    def new(self, instance, data={}):
        return self.get(instance=instance, data=data, create=True)

    def reset(self):
        self.items = {}
        j.tools.configmanager.delete(
            location=self.__jslocation__, instance="*")
        self.items = {}
        self.getall()

    def delete(self, instance="", prefix=""):
        if prefix != "":
            for item in self.list(prefix=prefix):
                self.delete(instance=item)
            return
        # if instance in self.items:
        #     del self.items[instance]
        j.tools.configmanager.delete(
            location=self.__jslocation__, instance=instance)
        self.items = {}

    def count(self):
        return len(self.list())

    def list(self, prefix=""):
        self.items = {}  # make sure anything in mem is gone
        res = []
        for item in j.tools.configmanager.list(location=self.__jslocation__):
            if prefix != "":
                if item.startswith(prefix):
                    res.append(item)
            else:
                res.append(item)
        return res

    def getall(self):
        res = []
        for name in j.tools.configmanager.list(location=self.__jslocation__):
            res.append(self.get(name, create=True))
        return res
