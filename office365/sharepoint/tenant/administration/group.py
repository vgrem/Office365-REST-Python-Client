from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity


class SPOGroup(Entity):
    """ """

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath(
                "Microsoft.Online.SharePoint.TenantAdministration.SPOGroup"
            )
        super(SPOGroup, self).__init__(context, resource_path)

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantAdministration.SPOGroup"
