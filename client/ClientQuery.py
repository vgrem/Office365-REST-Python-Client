class ClientQuery(object):
    """Client query"""

    def __init__(self,clientObject):
        self.Url = clientObject.ResourceUrl
        self.Payload = {}
        self.Headers = {}
        self.__resultObject = clientObject
      
    @staticmethod     
    def createUpdateQuery(clientObject,entityTypeName,propertiesToUpdate):
        qry = ClientQuery(clientObject)
        qry.Headers = {"X-HTTP-Method": "MERGE"}
        qry.Payload = { '__metadata': { 'type': entityTypeName }}
        for key in propertiesToUpdate:
            qry.Payload[key] = propertiesToUpdate[key]
        return qry

    @staticmethod
    def createDeleteQuery(clientObject):
        qry = ClientQuery(clientObject)
        qry.Headers = {"X-HTTP-Method": "DELETE"}
        return qry

    @staticmethod
    def createWebQuery(clientObject,webCreationInformation):
        qry = ClientQuery(clientObject)
        qry.Payload = { 'parameters' : { '__metadata': { 'type': 'SP.WebCreationInformation' }}}
        for key in webCreationInformation:
            qry.Payload['parameters'][key] = webCreationInformation[key]
        return qry
  

    @property 
    def ResultObject(self):
        return self.__resultObject

   


    

    


