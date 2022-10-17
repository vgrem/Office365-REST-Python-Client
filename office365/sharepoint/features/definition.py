from office365.sharepoint.base_entity import BaseEntity


class FeatureDefinition(BaseEntity):
    """Contains the base definition of a feature, including its name, ID, scope, and version."""

    @property
    def display_name(self):
        """
        :rtype: str or None
        """
        return self.properties.get("DisplayName", None)
