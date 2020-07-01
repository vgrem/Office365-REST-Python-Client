from office365.sharepoint.base_entity import BaseEntity


class RoleDefinition(BaseEntity):
    """Defines a single role definition, including a name, description, and set of rights."""

    @property
    def name(self):
        """Gets a value that specifies the role definition name."""
        return self.properties.get('Name', None)

    @name.setter
    def name(self, value):
        """Sets a value that specifies the role definition name."""
        self.set_property('Name', value)

    @property
    def description(self):
        """Gets or sets a value that specifies the description of the role definition."""
        return self.properties.get('Description', None)

    @description.setter
    def description(self, value):
        """Gets or sets a value that specifies the description of the role definition."""
        self.set_property('Description', value)
