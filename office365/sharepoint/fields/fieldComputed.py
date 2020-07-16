from office365.sharepoint.fields.field import Field


class FieldComputed(Field):

    @property
    def enableLookup(self):
        """
        Specifies whether a lookup field can reference the field (2).

        :rtype: bool or None
        """
        return self.properties.get("EnableLookup", None)
