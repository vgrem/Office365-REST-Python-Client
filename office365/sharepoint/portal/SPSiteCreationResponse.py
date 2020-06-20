from office365.runtime.clientValue import ClientValue


class SPSiteCreationResponse(ClientValue):

    def __init__(self):
        super(SPSiteCreationResponse, self).__init__()
        self.SiteId = None
        self.SiteStatus = None
        self.SiteUrl = None
