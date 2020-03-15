from office365.runtime.client_value_object import ClientValueObject


class SPSiteCreationResponse(ClientValueObject):

    def __init__(self):
        super(SPSiteCreationResponse, self).__init__()
        self.SiteId = None
        self.SiteStatus = None
        self.SiteUrl = None
