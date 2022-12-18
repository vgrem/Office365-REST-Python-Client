from office365.entity import Entity
from office365.runtime.types.collections import StringCollection


class PermissionGrantConditionSet(Entity):
    """
    A permission grant condition set is used to specify a matching rule in a permission grant policy to include
    or exclude a permission grant event.

    A permission grant condition set contains several conditions. For an event to match a permission grant condition
    set, all conditions must be met.
    """

    @property
    def client_application_ids(self):
        """
        A list of appId values for the client applications to match with, or a list with the single value all to
        match any client application. Default is the single value all.
        """
        return self.properties.get("clientApplicationIds", StringCollection())

    @property
    def permissions(self):
        """
        The list of id values for the specific permissions to match with, or a list with the single value all to
        match with any permission. The id of delegated permissions can be found in the oauth2PermissionScopes property
        of the API's servicePrincipal object. The id of application permissions can be found in the appRoles property
        of the API's servicePrincipal object. The id of resource-specific application permissions can be found in
        the resourceSpecificApplicationPermissions property of the API's servicePrincipal object.
        Default is the single value all.
        """
        return self.properties.get("permissions", StringCollection())
