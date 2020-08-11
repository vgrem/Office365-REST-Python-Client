from office365.runtime.client_value import ClientValue


class SiteCreationProperties(ClientValue):

    def __init__(self, url, owner):
        """Sets the initial properties for a new site when it is created.
        :type owner: str
        :type url: str
        """
        super().__init__()
        self.Url = url
        self.Owner = owner
        self.Title = None
        self.Template = None

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SiteCreationProperties"
