from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class SiteCollectionManagementService(BaseEntity):

    def __init__(self, context):
        fqn = "Microsoft.Online.SharePoint.TenantAdministration.SiteCollectionManagementService"
        super().__init__(context, ResourcePath(fqn))
