from ClientQuery import ClientQuery

class ClientObject(object):
    """Base client object"""
    def __init__(self,context):
        self.__context = context
        #self.__query = None
        self.__properties = {}
        self.__parentCollection = None
        self.__entityTypeName = None


    def removeFromParentCollection(self):
        if (self.__parentCollection is None):
            return
        self.__parentCollection.remove(self)

    @property 
    def Context(self):
        return self.__context

    @property 
    def EntityTypeName(self):
        return self.__entityTypeName

  
    #@property 
    #def Query(self):
    #    if not self.__query:
    #        self.__query = ClientQuery(self) 
    #    return self.__query

    @property 
    def Properties(self):
        return self.__properties

    @Properties.setter
    def Properties(self, value):
        self.__properties = value

    