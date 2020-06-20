from office365.sharepoint.fields.field import Field


class FieldLookup(Field):

    def __init__(self, context):
        """Specifies a lookup field."""
        super().__init__(context)

    @property
    def lookup_web_id(self):
        """Gets the ID of the Web site that contains the list that is the source of this field's value."""
        return self.properties.get('LookupWebId', None)

    @lookup_web_id.setter
    def lookup_web_id(self, val):
        """Sets the ID of the Web site that contains the list that is the source of this field's value."""
        self.set_property("LookupWebId", val, True)

    @property
    def lookup_list(self):
        """Gets value that specifies the list identifier of the list that contains the field to use as the lookup
        values."""
        return self.properties.get('LookupList', None)

    @lookup_list.setter
    def lookup_list(self, val):
        """Sets a value that specifies the list identifier of the list that contains the field to use as
        the lookup values."""
        self.set_property("LookupList", val, True)
