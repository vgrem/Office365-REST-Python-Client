from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity


class SharePointDirectoryProvider(BaseEntity):

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("SP.Directory.Provider.SharePointDirectoryProvider")
        super(SharePointDirectoryProvider, self).__init__(context, resource_path)

    @property
    def entity_type_name(self):
        return "SP.Directory.Provider.SharePointDirectoryProvider"
