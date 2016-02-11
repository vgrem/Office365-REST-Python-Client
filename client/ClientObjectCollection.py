from ClientObject import ClientObject
class ClientObjectCollection(ClientObject):
    """Client object collection"""


    def __init__(self,context):
        super(ClientObjectCollection, self).__init__(context)
        self.__data = []

    def addChild(self,clientObject):
        self.__data.append(clientObject)





