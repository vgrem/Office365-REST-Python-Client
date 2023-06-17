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
        return_type = FieldUserValue(-1)

        def _user_loaded():
            return_type.LookupId = user.id
            return_type.LookupValue = user.login_name
        user.ensure_properties(["Id", "LoginName"], _user_loaded)
        return return_type
