from office365.sharepoint.entity import Entity


class FeatureDefinition(Entity):
    """Contains the base definition of a feature, including its name, ID, scope, and version."""

    @property
    def display_name(self):
        """
        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)
