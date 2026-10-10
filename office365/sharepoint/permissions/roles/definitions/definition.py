from __future__ import annotations

from typing import Optional

from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.types.odata_property import odata
from office365.sharepoint.entity import Entity
from office365.sharepoint.permissions.base_permissions import BasePermissions


class RoleDefinition(Entity):
    """Defines a single role definition, including a name, description, and set of rights."""

    def __repr__(self):
        return self.name or self.entity_type_name

    @odata(name="BasePermissions")
    @property
    def base_permissions(self) -> BasePermissions:
        """
        Specifies the base permissions for the role definition.
        When assigning values to the property, use bitwise AND, OR, and XOR operators with values from
        the BasePermissions uint.
        """
        return self.properties.get("BasePermissions", BasePermissions())

    @property
    def id(self) -> Optional[int]:
        """Specifies the identifier of the role definition.
        Its value MUST be equal to or greater than 1073741824."""
        return self.properties.get("Id", None)

    @property
    def role_type_kind(self) -> Optional[int]:
        """Specifies the type of the role definition.
        Its value MUST be equal to or greater than 0. Its value MUST be equal to or less than 5.
        """
        return self.properties.get("RoleTypeKind", None)

    @property
    def name(self) -> Optional[str]:
        """Gets a value that specifies the role definition name."""
        return self.properties.get("Name", None)

    @name.setter
    def name(self, value):
        """Sets a value that specifies the role definition name."""
        self.set_property("Name", value)

    @property
    def description(self) -> Optional[str]:
        """Gets or sets a value that specifies the description of the role definition."""
        return self.properties.get("Description", None)

    @description.setter
    def description(self, value):
        """Gets or sets a value that specifies the description of the role definition."""
        self.set_property("Description", value)

    def set_property(self, name, value, persist_changes=True):
        if self.resource_path is None:
            if name == "Id" and self.parent_collection is not None:
                self._resource_path = ServiceOperationPath("GetById", [value], self.parent_collection.resource_path)
        return super().set_property(name, value, persist_changes)

    @property
    def hidden(self) -> Optional[bool]:
        """Gets the Hidden property"""
        return self.properties.get("Hidden", None)

    @property
    def order(self) -> Optional[int]:
        """Gets the Order property"""
        return self.properties.get("Order", None)
