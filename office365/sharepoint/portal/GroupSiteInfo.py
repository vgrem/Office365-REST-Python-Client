from office365.runtime.clientValue import ClientValue


class GroupSiteInfo(ClientValue):

    def __init__(self):
        super(GroupSiteInfo, self).__init__()
        self.SiteStatus = None
        self.SiteUrl = None
        self.DocumentsUrl = None
        self.ErrorMessage = None
        self.GroupId = None
