from office365.sharepoint.base_entity import BaseEntity


class StructuralNavigationCacheWrapper(BaseEntity):
    @property
    def entity_type_name(self):
        return "SP.Publishing.Navigation.StructuralNavigationCacheWrapper"
