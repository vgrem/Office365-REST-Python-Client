from ClientObject import ClientObject

class Site(ClientObject):
    """Site client object"""

    def buildQuery(self):
        self.setQuery(url ="/_api/site/")


