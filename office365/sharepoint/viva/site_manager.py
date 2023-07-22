from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class VivaSiteManager(BaseEntity):
    """"""
    def __init__(self, content, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("Microsoft.SharePoint.Portal.VivaSiteManager")
        super().__init__(content, resource_path)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.VivaSiteManager"
