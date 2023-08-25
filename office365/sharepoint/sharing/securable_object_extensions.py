from office365.sharepoint.base_entity import BaseEntity


class SecurableObjectExtensions(BaseEntity):
    """Contains extension methods of securable object."""

    @property
    def entity_type_name(self):
        return "SP.Sharing.SecurableObjectExtensions"
