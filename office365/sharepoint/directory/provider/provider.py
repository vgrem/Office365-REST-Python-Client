from office365.sharepoint.base_entity import BaseEntity


class SharePointDirectoryProvider(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Directory.Provider.SharePointDirectoryProvider"
