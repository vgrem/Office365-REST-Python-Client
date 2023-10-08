from office365.sharepoint.entity import Entity


class Feature(Entity):
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
