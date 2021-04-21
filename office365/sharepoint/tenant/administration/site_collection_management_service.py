from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path import ResourcePath


class SiteCollectionManagementService(ClientObject):

    def __init__(self, context):
        fqn = "Microsoft.Online.SharePoint.TenantAdministration.SiteCollectionManagementService"
        super().__init__(context, ResourcePath(fqn))
