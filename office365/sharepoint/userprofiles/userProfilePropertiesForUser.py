from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class UserProfilePropertiesForUser(ClientObject):

    def __init__(self, context, account_name, property_names):
        params = {
            "accountName": account_name,
            "propertyNames": property_names
        }

        super(UserProfilePropertiesForUser, self).__init__(context, ResourcePathServiceOperation("SP.UserProfiles.UserProfilePropertiesForUser", params))
