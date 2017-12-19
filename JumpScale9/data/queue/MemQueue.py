
from JumpScale9 import j

import time


class MemQueueFactory:


    def get(self):
        """
        """
        return MemQueue()


class MemQueue():

    def __init__(self):
        self.data=[]
    
    def put(self,data):
        self.data.append(data)

    def __str__(self):
        return self.data

    __repr__ = __str__
