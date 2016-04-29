from ClientRequest import ClientRequest
from ClientQuery import ClientQuery
from Web import Web
from Site import Site

class ClientContext(object):
    """SharePoint client context"""
    def __init__(self,url,authContext):
        self.__url = url
        self.__authContext = authContext
        self.__web = None
        self.__site = None
        self.__pendingRequest = None
        self.__queries = []
        

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
        qry = ClientQuery(clientObject)
        self.addQuery(qry)


    def executeQuery(self):
        "Submit pending request to the server"
        for qry in self.__queries:
            data = self.PendingRequest.executeQuery(requestUrl=qry.Url,headers=qry.Headers,data=qry.Payload)
            if any(data):
                qry.ResultObject.Properties = data['d']


    def addQuery(self,query):
        self.__queries.append(query)
        



