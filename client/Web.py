from ClientObject import ClientObject
from ClientQuery import ClientQuery
from WebCollection import WebCollection


class Web(ClientObject):
    """Web client object. Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self,context):
        super(Web, self).__init__(context)
        self.ResourceUrl = "/_api/web"

  
    def update(self):
        "Update web"
        webProperties = self.Properties
        qry = ClientQuery.createUpdateQuery(self,'SP.Web',webProperties)
        self.Context.addQuery(qry)
        
        
    def deleteObject(self):
        "Delete web"
        qry = ClientQuery.createDeleteQuery(self)
        self.Context.addQuery(qry)
        self.removeFromParentCollection()

    @property
    def Webs(self):
        "Get child webs"
        if 'Webs' in self.Properties:
            return self.Properties['Webs']
        else:
            return WebCollection(self.Context) 


    def removeFromParentCollection(self):
        "todo"


