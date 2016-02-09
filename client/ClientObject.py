from ClientQuery import ClientQuery

class ClientObject(object):
    """Base client object"""
    def __init__(self,context):
        self.__context = context
        self.__query = None
        self.__properties = {}

    @property 
    def Context(self):
        return self.__context

    def buildQuery(self):
        "Build OData query"

    @property 
    def Query(self):
        return self.__query

    @property 
    def Properties(self):
        return self.__properties

    @Properties.setter
    def Properties(self, value):
        self.__properties = value

    def setQuery(self,url,headers={},payload={}):
        self.__query = ClientQuery(url,headers,payload)