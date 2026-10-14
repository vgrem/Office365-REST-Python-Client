from __future__ import annotations

from typing import Optional

from office365.sharepoint.entity import Entity


class FieldLink(Entity):
    """Specifies a reference to a field or field definition for a content type."""

    @property
    def id(self) -> Optional[str]:
        """Gets a value that specifies the GUID of the FieldLink."""
        return self.properties.get("Id", None)

    @property
    def field_internal_name(self) -> Optional[str]:
        """Gets a value that specifies the linked field's internal name.

        Note:
            SharePoint's REST API returns the internal name in ``Name`` and
            leaves ``FieldInternalName`` (a creation-time property) empty, so this
            falls back to :attr:`name` for a value read back from the server.
        """
        return self.properties.get("FieldInternalName", None) or self.name

    @property
    def read_only(self) -> Optional[bool]:
        """ """
        return self.properties.get("ReadOnly", None)

    @property
    def hidden(self) -> Optional[bool]:
        """Gets a value that specifies whether the field is displayed in forms that can be edited."""
        return self.properties.get("Hidden", None)

    @property
    def required(self) -> Optional[bool]:
        """Gets a value that specifies whether the field (2) requires a value."""
        return self.properties.get("Required", None)

    @property
    def show_in_display_form(self) -> Optional[bool]:
        """A Boolean value that indicates whether this field is shown in the display form."""
        return self.properties.get("ShowInDisplayForm", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the DisplayName property"""
        return self.properties.get("DisplayName", None)

    @property
    def name(self) -> Optional[str]:
        """Gets the Name property"""
        return self.properties.get("Name", None)
