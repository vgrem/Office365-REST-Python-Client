from office365.sharepoint.base_entity import BaseEntity


class FormsCustomization(BaseEntity):

    @property
    def entity_type_name(self):
        return "SP.Internal.FormsCustomization"
