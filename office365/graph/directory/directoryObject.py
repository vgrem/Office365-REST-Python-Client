from office365.graph.entity import Entity
from office365.runtime.client_query import DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DirectoryObject(Entity):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types. """

    def get_member_groups(self, security_enabled_only=True):
        """Return all the groups that the specified user, group, or directory object is a member of. This function is
        transitive.

        :type security_enabled_only: bool"""
        result = ClientResult(None)
        payload = {
            "securityEnabledOnly": security_enabled_only
        }
        qry = ServiceOperationQuery(self, "getMemberGroups", None, payload, None, result)
        self.context.add_query(qry)
        return result

    def update(self):
        """Updates the directory object."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the directory object."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    @property
    def deletedDateTime(self):
        """ETag for the item."""
        if self.is_property_available("deletedDateTime"):
            return self.properties['deletedDateTime']
        return None

    def set_property(self, name, value, persist_changes=True):
        super(DirectoryObject, self).set_property(name, value, persist_changes)
