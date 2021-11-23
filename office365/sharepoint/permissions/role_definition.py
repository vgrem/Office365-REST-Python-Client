from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity


class RoleDefinition(BaseEntity):
    """Defines a single role definition, including a name, description, and set of rights."""

    @property
    def id(self):
        """Specifies the identifier of the role definition.
        Its value MUST be equal to or greater than 1073741824."""
        return self.properties.get('Id', None)

    @property
    def role_type_kind(self):
        """Specifies the type of the role definition.
        Its value MUST be equal to or greater than 0. Its value MUST be equal to or less than 5."""
        return self.properties.get('RoleTypeKind', None)

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

    def set_property(self, name, value, persist_changes=True):
        if self.resource_path is None:
            if name == "Id":
                self._resource_path = ServiceOperationPath(
                    "GetById", [value], self._parent_collection.resource_path)
        return super(RoleDefinition, self).set_property(name, value, persist_changes)
