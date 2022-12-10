from office365.sharepoint.base_entity import BaseEntity


class MetadataNavigationSettings(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.MetadataNavigation.MetadataNavigationSettings"
