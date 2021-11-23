from office365.runtime.client_object import ClientObject
from office365.runtime.paths.service_operation import ServiceOperationPath


class UserProfilePropertiesForUser(ClientObject):

    def __init__(self, context, account_name, property_names):
        params = {
            "accountName": account_name,
            "propertyNames": property_names
        }

        super(UserProfilePropertiesForUser, self).__init__(context, ServiceOperationPath("SP.UserProfiles.UserProfilePropertiesForUser", params))
