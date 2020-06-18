from office365.sharepoint.fieldLookupValue import FieldLookupValue


class FieldUserValue(FieldLookupValue):

    def __init__(self, user_id):
        """Represents the value of a user field for a list item."""
        super().__init__(user_id)

    @staticmethod
    def from_user(user):
        pass
