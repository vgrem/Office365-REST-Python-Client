from ClientRequest import ClientRequest
from Web import Web
from Site import Site

class ClientContext(object):
    """SharePoint CSOM Client Context"""
    def __init__(self,url,authContext):
        self.__url = url
        self.__authContext = authContext
        self.__web = None
        self.__site = None
        self.__pendingRequest = None
        self.__resultObject = None

    @property
    def Web(self):
        "Get Web client object"
        if not self.__web:
            self.__web = Web(self) 
        return self.__web

    @property
    def Site(self):
        "Get Site client object"
        if not self.__site:
            self.__site = Site(self) 
        return self.__site
    
    @property
    def PendingRequest(self):
        if not self.__pendingRequest:
            self.__pendingRequest = ClientRequest(self.__url,self.__authContext) 
        return self.__pendingRequest


    def load(self,clientObject,retrievals=None):
        "Load client object"
        clientObject.buildQuery()
        self.__resultObject = clientObject


    def executeQuery(self):
        "Submit pending request to the server"
        query = self.__resultObject.Query
        data = self.PendingRequest.executeQuery(requestUrl=query.Url,headers=query.Headers,data=query.Payload)
        self.__resultObject.Properties = data['d']
        



