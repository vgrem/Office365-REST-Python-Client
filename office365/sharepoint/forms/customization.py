from office365.sharepoint.entity import Entity


class FormsCustomization(Entity):
    @property
    def entity_type_name(self):
        return "SP.Internal.FormsCustomization"
