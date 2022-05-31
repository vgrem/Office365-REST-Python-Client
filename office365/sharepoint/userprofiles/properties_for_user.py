from office365.runtime.client_object import ClientObject
from office365.runtime.paths.service_operation import ServiceOperationPath


class UserProfilePropertiesForUser(ClientObject):
    """The UserProfilePropertiesForUser class represents a set of user profile properties for a user."""

    def __init__(self, context, account_name, property_names):
        params = {
            "accountName": account_name,
            "propertyNames": property_names
        }
        path = ServiceOperationPath("SP.UserProfiles.UserProfilePropertiesForUser", params)
        super(UserProfilePropertiesForUser, self).__init__(context, path)
