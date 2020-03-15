from office365.runtime.client_value_object import ClientValueObject


class GroupSiteInfo(ClientValueObject):

    def __init__(self):
        super(GroupSiteInfo, self).__init__()
        self.SiteStatus = None
        self.SiteUrl = None
        self.DocumentsUrl = None
        self.ErrorMessage = None
        self.GroupId = None

