from inspect import isclass

from js9 import j


class JSBaseClassConfigs():
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
            raise TypeError("child_class need to be a class not %s" % type(child_class))

        self.items = {}
        self._single_item = single_item
        self._child_class = child_class

    def get(self, instance="main", data={}):
        """
        Get an instance of the child_class set in the constructor

        @param instance: instance name to get. If an instance is already loaded in memory, return it
        @data data: dictionary of data use to configure the instance
        """
        if not instance in self.items:
            self.items[instance] = self._child_class(instance=instance, data=data, parent=self)

        return self.items[instance]

    def reset(self):
        self.items = {}
        j.tools.configmanager.delete(location=self.__jslocation__, instance="*")

    def delete(self, instance):
        if instance in self.items:
            del self.items[instance]
        j.tools.configmanager.delete(location=self.__jslocation__, instance=instance)

    def list(self):
        return j.tools.configmanager.list(location=self.__jslocation__)

    def getall(self):
        res = []
        for name in j.tools.configmanager.list(location=self.__jslocation__):
            res.append(self.get(name).config)
        return res
