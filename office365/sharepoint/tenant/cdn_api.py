from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class TenantCdnApi(BaseEntity):

    def __init__(self, context):
        super(TenantCdnApi, self).__init__(context, ResourcePath("Microsoft.SharePoint.TenantCdn.TenantCdnApi"))

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.TenantCdn.TenantCdnApi"
