from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class SPOWebAppServicePrincipal(BaseEntity):

    def __init__(self, context):
        stat_path = ResourcePath("Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal")
        super(SPOWebAppServicePrincipal, self).__init__(context, stat_path)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.Internal.SPOWebAppServicePrincipal"
