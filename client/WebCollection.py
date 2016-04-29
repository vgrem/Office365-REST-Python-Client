from ClientQuery import ClientQuery
import Web
from ClientObjectCollection import ClientObjectCollection

class WebCollection(ClientObjectCollection):
    """Web collection"""


    def add(self,webCreationInformation):
        self.ResourceUrl = "/_api/web/webs/add"
        qry = ClientQuery.createWebQuery(self,webCreationInformation)
        self.Context.addQuery(qry)
        #add child web
        from Web import Web
        web = Web(self.Context)
        self.addChild(web)
        return web 
        