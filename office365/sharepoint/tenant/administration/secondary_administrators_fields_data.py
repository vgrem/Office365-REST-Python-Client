from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class SecondaryAdministratorsFieldsData(ClientValue):

    def __init__(self, site_id, emails=None, names=None):
        """
        :type emails: List[str] or None
        :type names: List[str] or None
        :type site_id: str or None
        """
        super(SecondaryAdministratorsFieldsData, self).__init__()
        self.secondaryAdministratorEmails = ClientValueCollection(str, emails)
        self.secondaryAdministratorLoginNames = ClientValueCollection(str, names)
        self.siteId = site_id

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData"
