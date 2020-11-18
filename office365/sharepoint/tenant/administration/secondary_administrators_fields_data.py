from office365.runtime.client_value import ClientValue


class SecondaryAdministratorsFieldsData(ClientValue):
    def __init__(self, emails, names, site_id):
        """
        :type emails: List[str] or None
        :type names: List[str] or None
        :type site_id: str or None
        """
        super().__init__()
        self.secondaryAdministratorEmails = emails
        self.secondaryAdministratorLoginNames = names
        self.siteId = site_id

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData"




