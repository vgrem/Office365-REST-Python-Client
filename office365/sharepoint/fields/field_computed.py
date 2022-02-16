from office365.sharepoint.fields.field import Field


class FieldComputed(Field):
    """Specifies a computed field. To set the properties of this class, call the Update method
    (section 3.2.5.42.2.1.5)."""

    @property
    def enable_lookup(self):
        """
        Specifies whether a lookup field can reference the field (2).

        :rtype: bool or None
        """
        return self.properties.get("EnableLookup", None)
