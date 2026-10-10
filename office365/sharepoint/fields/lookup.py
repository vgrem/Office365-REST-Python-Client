from __future__ import annotations

from typing import Optional

from office365.runtime.types.collections import StringCollection
from office365.sharepoint.fields.field import Field


class FieldLookup(Field):
    """Specifies a lookup field."""

    @property
    def allow_multiple_values(self) -> Optional[bool]:
        """Gets a value that specifies whether the lookup field allows multiple values."""
        return self.properties.get("AllowMultipleValues", None)

    @allow_multiple_values.setter
    def allow_multiple_values(self, value: bool) -> None:
        """Sets a value that specifies whether the lookup field allows multiple values."""
        self.set_property("AllowMultipleValues", value)

    @property
    def lookup_web_id(self) -> Optional[str]:
        """Gets the ID of the Web site that contains the list that is the source of this field's value."""
        return self.properties.get("LookupWebId", None)

    @lookup_web_id.setter
    def lookup_web_id(self, val: str) -> None:
        """Sets the ID of the Web site that contains the list that is the source of this field's value."""
        self.set_property("LookupWebId", val, True)

    @property
    def lookup_list(self) -> Optional[str]:
        """Gets value that specifies the list identifier of the list that contains the field to use as the lookup
        values."""
        return self.properties.get("LookupList", None)

    @lookup_list.setter
    def lookup_list(self, val: str) -> None:
        """Sets a value that specifies the list identifier of the list that contains the field to use as
        the lookup values."""
        self.set_property("LookupList", val, True)

    @property
    def primary_field_id(self) -> Optional[str]:
        """Specifies the primary lookup field identifier if this is a dependent lookup field.
        Otherwise, it is an empty string."""
        return self.properties.get("PrimaryFieldId", None)

    @property
    def relationship_delete_behavior(self) -> Optional[int]:
        """Gets a value that specifies the relationship delete behavior of the lookup field."""
        return self.properties.get("RelationshipDeleteBehavior", None)

    @property
    def unlimited_length_in_document_library(self) -> Optional[bool]:
        """Gets or sets a Boolean value that specifies whether to allow values with unlimited text
        in the lookup field."""
        return self.properties.get("UnlimitedLengthInDocumentLibrary", None)

    @property
    def dependent_lookup_internal_names(self) -> StringCollection:
        """Gets the DependentLookupInternalNames property"""
        return self.properties.get("DependentLookupInternalNames", StringCollection())

    @property
    def is_dependent_lookup(self) -> Optional[bool]:
        """Gets the IsDependentLookup property"""
        return self.properties.get("IsDependentLookup", None)

    @property
    def is_relationship(self) -> Optional[bool]:
        """Gets the IsRelationship property"""
        return self.properties.get("IsRelationship", None)

    @property
    def lookup_field(self) -> Optional[str]:
        """Gets the LookupField property"""
        return self.properties.get("LookupField", None)
