from office365.sharepoint.fields.lookup_value import FieldLookupValue


class FieldUserValue(FieldLookupValue):

    def __init__(self, user_id):
        """Represents the value of a user fields for a list item."""
        super(FieldUserValue, self).__init__(user_id)

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
            value.LookupValue = user.login_name
        user.ensure_properties(["Id", "LoginName"], _init_from_user)
        return value
