from office365.sharepoint.base_entity import BaseEntity


class StorageEntity(BaseEntity):
    """Storage entities which are available across app catalog scopes."""

    @property
    def value(self):
        """The value inside the storage entity."""
        return self.properties.get("Value", None)
