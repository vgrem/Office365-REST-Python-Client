from office365.runtime.clientValue import ClientValue


class SPSiteCreationResponse(ClientValue):

    def __init__(self):
        super().__init__()
        self.SiteId = None
        self.SiteStatus = None
        self.SiteUrl = None
