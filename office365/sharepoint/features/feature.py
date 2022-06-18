from office365.sharepoint.base_entity import BaseEntity


class Feature(BaseEntity):
    """Represents an activated feature."""

    @property
    def definition_id(self):
        """
        Gets the GUID that identifies this feature.

        :rtype: str or None
        """
        return self.properties.get("DefinitionId", None)

    @property
    def display_name(self):
        """
        Gets the GUID that identifies this feature.

        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)
