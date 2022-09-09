from office365.runtime.client_result import ClientResult
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity


class UserProfilePropertiesForUser(BaseEntity):
    """The UserProfilePropertiesForUser class represents a set of user profile properties for a user."""

    def get_property_names(self):
        """
        The GetPropertyNames method gets an array of strings that specify the user profile property names.
        """
        return_type = ClientResult(self.context, StringCollection())
        qry = ServiceOperationQuery(self, "GetPropertyNames", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def account_name(self):
        """
        The AccountName property specifies the account name of the user.

        :rtype: str or None
        """
        return self.properties.get('AccountName', None)

    @property
    def property_names(self):
        return self.properties.get('PropertyNames', None)

    @property
    def resource_path(self):
        if self._resource_path is None:
            params = {
                "accountName": self.account_name,
                "propertyNames": self.property_names
            }
            self._resource_path = ServiceOperationPath("SP.UserProfiles.UserProfilePropertiesForUser", params)
        return self._resource_path

