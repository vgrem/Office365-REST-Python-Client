from ClientObject import ClientObject
from Web import Web

class Site(ClientObject):
    """Site client object"""


    @property
    def RootWeb(self):
        "Get root web"
        if 'RootWeb' in self.Properties:
            return self.Properties['RootWeb']
        else:
            return Web(self.Context) 
