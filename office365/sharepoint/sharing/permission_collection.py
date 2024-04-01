from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.sharing.link_info import LinkInfo
from office365.sharepoint.utilities.principal_info import PrincipalInfo


class PermissionCollection(ClientValue):
    """
    This class is returned when Microsoft.SharePoint.Client.Sharing.SecurableObjectExtensions.GetSharingInformation
    is called with the optional expand on permissionsInformation property. It contains a collection of LinkInfo and
    PrincipalInfo objects of users/groups that have access to the list item and also the site administrators who have
    implicit access.
    """

    def __init__(
        self, hasInheritedLinks=None, links=None, principals=None, siteAdmins=None
    ):
        """
        :param bool hasInheritedLinks:
        :param list[LinkInfo] links: The List of tokenized sharing links with their LinkInfo objects.
        :param list[PrincipalInfo] principals: The List of Principals with their roles on this list item.
        :param list[PrincipalInfo] siteAdmins: The List of Principals who are Site Admins. This property is returned
            only if the caller is an Auditor.
        """
        self.hasInheritedLinks = hasInheritedLinks
        self.links = ClientValueCollection(LinkInfo, links)
        self.principals = ClientValueCollection(PrincipalInfo, principals)
        self.siteAdmins = ClientValueCollection(PrincipalInfo, siteAdmins)

    @property
    def entity_type_name(self):
        return "SP.Sharing.PermissionCollection"
