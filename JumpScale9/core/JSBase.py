from JumpScale9 import j


class JSBase:

    def __init__(self):
        # self.__j = None
        self.__logger = None

    @property
    def j(self):
        if self.__logger == None:
            self.__logger = j.logger.get()
        return self.__logger

    # @property
    # def j(self):
    #     if self.__j==None:
    #         from JumpScale9 import jumpScale2
    #         self.__j= JumpScale2()
    #     return self.__j
