from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


class DirectoryObject(Entity):
    """Represents an Azure Active Directory object. The directoryObject type is the base type for many other
    directory entity types. """

    def get_member_objects(self, security_enabled_only=True):
        """Returns all the groups and directory roles that a user, group, or directory object is a member of.
        This function is transitive.

        :type security_enabled_only: bool"""
        result = ClientResult(self.context, ClientValueCollection(str))
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

    def get_available_extension_properties(self, is_synced_from_on_premises=None):
        """
        Return all or a filtered list of the directory extension properties that have been registered in a directory.
        The following entities support extension properties: user, group, organization, device, application,
        and servicePrincipal.
        """
        from office365.directory.extensions.extension_property import ExtensionProperty
        return_type = EntityCollection(self.context, ExtensionProperty)
        payload = {
            "isSyncedFromOnPremises": is_synced_from_on_premises
        }
        qry = ServiceOperationQuery(self, "getAvailableExtensionProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def deleted_datetime(self):
        """ETag for the item."""
        return self.properties.get('deletedDateTime', None)

    def set_property(self, name, value, persist_changes=True):
        super(DirectoryObject, self).set_property(name, value, persist_changes)
