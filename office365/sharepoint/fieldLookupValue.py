from office365.runtime.client_value_object import ClientValueObject


class FieldLookupValue(ClientValueObject):

    def __init__(self, lookup_id=None, lookup_value=None):
        """Specifies the value of a lookup for a field within a list item.

        :param int or None lookup_id: Gets or sets the identifier (ID) of the list item that this instance of the lookup
        field is referring to.
        :param str or None lookup_value: Gets a summary of the list item that this instance
        of the lookup field is referring to.

        """
        super().__init__()
        self.LookupId = lookup_id
        self.LookupValue = lookup_value
