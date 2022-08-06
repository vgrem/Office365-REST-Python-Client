from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection


class DirectoryObject(Entity):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types. """

    def get_member_objects(self, security_enabled_only=True):
        """Returns all the groups and directory roles that a user, group, or directory object is a member of.
        This function is transitive.

        :type security_enabled_only: bool"""
        result = ClientResult(self.context, StringCollection())
        payload = {
            "securityEnabledOnly": security_enabled_only
        }
        qry = ServiceOperationQuery(self, "getMemberObjects", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def get_member_groups(self, security_enabled_only=True):
        """Return all the groups that the specified user, group, or directory object is a member of. This function is
        transitive.

        :type security_enabled_only: bool"""
        result = ClientResult(self.context)
        payload = {
            "securityEnabledOnly": security_enabled_only
        }
        qry = ServiceOperationQuery(self, "getMemberGroups", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def restore(self):
        qry = ServiceOperationQuery(self, "restore")
        self.context.add_query(qry)
        return self

    @property
    def deleted_datetime(self):
        """ETag for the item."""
        return self.properties.get('deletedDateTime', None)
