from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity


class UserProfilePropertiesForUser(BaseEntity):
    """The UserProfilePropertiesForUser class represents a set of user profile properties for a user."""

    @property
    def account_name(self):
        """
        The AccountName property specifies the account name of the user.

        :rtype: str or None
        """
        return self.properties.get('AccountName', None)

    def __init__(self, context, account_name, property_names):
        params = {
            "accountName": account_name,
            "propertyNames": property_names
        }
        path = ServiceOperationPath("SP.UserProfiles.UserProfilePropertiesForUser", params)
        super(UserProfilePropertiesForUser, self).__init__(context, path)
