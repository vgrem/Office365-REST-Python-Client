from ClientObject import ClientObject


class Web(ClientObject):
    """Web client object"""

    def buildQuery(self):
        self.setQuery(url ="/_api/web/")


