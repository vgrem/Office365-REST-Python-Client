from office365.runtime.client_result import ClientResult
from office365.runtime.queries.serviceOperationQuery import ServiceOperationQuery
from office365.sharepoint.permissions.basePermissions import BasePermissions
from office365.sharepoint.base_entity import BaseEntity


class SecurableObject(BaseEntity):
    """An object that can be assigned security permissions."""

    def get_user_effective_permissions(self, user_name):
        """

        :type user_name: str
        """
        result = ClientResult(BasePermissions())
        qry = ServiceOperationQuery(self, "getUserEffectivePermissions", [user_name], None, None, result)
        self.context.add_query(qry)
        return result
