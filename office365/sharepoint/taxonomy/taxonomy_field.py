from office365.sharepoint.fields.field_lookup import FieldLookup


class TaxonomyField(FieldLookup):
    """Represents a taxonomy field."""

    @property
    def anchor_id(self):
        """Gets or sets the GUID of the anchor Term object for a TaxonomyField object."""
        return self.properties.get('AnchorId', None)

    @property
    def is_anchor_valid(self):
        """Gets a Boolean value that specifies whether the Term object identified by the AnchorId property is valid."""
        return self.properties.get('IsAnchorValid', None)

    @property
    def text_field(self):
        """Gets the GUID that identifies the hidden text field in an item."""
        return self.properties.get('TextField', None)

    @text_field.setter
    def text_field(self, value):
        """Sets the GUID that identifies the hidden text field in an item."""
        self.set_property("TextField", value)
