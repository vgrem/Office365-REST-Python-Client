from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.directory.allowed_value import AllowedValue


class CustomSecurityAttributeDefinition(Entity):
    """Represents the schema of a custom security attribute (key-value pair).
    For example, the custom security attribute name, description, data type, and allowed values.
    """

    @property
    def attribute_set(self) -> Optional[str]:
        """Gets the attributeSet property"""
        return self.properties.get("attributeSet", None)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def is_collection(self) -> Optional[bool]:
        """Gets the isCollection property"""
        return self.properties.get("isCollection", None)

    @property
    def is_searchable(self) -> Optional[bool]:
        """Gets the isSearchable property"""
        return self.properties.get("isSearchable", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the name property"""
        return self.properties.get("name", None)

    @property
    def status(self) -> Optional[str]:
        """Gets the status property"""
        return self.properties.get("status", None)

    @property
    def type(self) -> Optional[str]:
        """Gets the type property"""
        return self.properties.get("type", None)

    @property
    def use_pre_defined_values_only(self) -> Optional[bool]:
        """Gets the usePreDefinedValuesOnly property"""
        return self.properties.get("usePreDefinedValuesOnly", None)

    @property
    def allowed_values(self) -> EntityCollection[AllowedValue]:
        """Gets the allowedValues property"""
        from office365.directory.allowed_value import AllowedValue

        return self.properties.get(
            "allowedValues",
            EntityCollection[AllowedValue](
                self.context, AllowedValue, ResourcePath("allowedValues", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CustomSecurityAttributeDefinition"
