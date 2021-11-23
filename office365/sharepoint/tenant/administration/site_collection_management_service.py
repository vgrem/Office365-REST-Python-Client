from office365.runtime.client_object import ClientObject
from office365.runtime.paths.resource_path import ResourcePath


class SiteCollectionManagementService(ClientObject):

    def __init__(self, context):
        fqn = "Microsoft.Online.SharePoint.TenantAdministration.SiteCollectionManagementService"
        super(SiteCollectionManagementService, self).__init__(context, ResourcePath(fqn))
