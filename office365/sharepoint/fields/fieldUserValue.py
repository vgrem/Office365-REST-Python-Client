from office365.sharepoint.fields.fieldLookupValue import FieldLookupValue


class FieldUserValue(FieldLookupValue):

    def __init__(self, user_id):
        """Represents the value of a user fields for a list item."""
        super().__init__(user_id)

    @staticmethod
    def from_user(user):
        """
        Initialize field value from User

        :param office365.sharepoint.principal.user.User user: User entity
        :return: FieldUserValue
        """
        value = FieldUserValue(-1)

        def _init_from_user():
            value.LookupId = user.id
        user.ensure_property("Id", _init_from_user)
        return value
