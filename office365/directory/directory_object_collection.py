from office365.directory.directory_object import DirectoryObject
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class DirectoryObjectCollection(EntityCollection):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super(DirectoryObjectCollection, self).__init__(context, DirectoryObject, resource_path)

    def get(self):
        """
        :rtype: DirectoryObjectCollection
        """
        return super(DirectoryObjectCollection, self).get()

    def __getitem__(self, key):
        """
        :type key: int or str
        :rtype: DirectoryObject
        """
        return super(DirectoryObjectCollection, self).__getitem__(key)

    def get_by_ids(self, ids):
        """Returns the directory objects specified in a list of IDs."""
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "getByIds", None, None, None, result)
        self.context.add_query(qry)
        return result

    def add(self, user_id):
        """Add a user to the group."""
        payload = {
            "@odata.id": "https://graph.microsoft.com/v1.0/users/{0}".format(user_id)
        }
        qry = ServiceOperationQuery(self, "$ref", None, payload)
        self.context.add_query(qry)
        return self

    def get_available_extension_properties(self, is_synced_from_on_premises=None):
        """
        Return all or a filtered list of the directory extension properties that have been registered in a directory.
        The following entities support extension properties: user, group, organization, device, application,
        and servicePrincipal.
        """
        from office365.directory.extensions.extension_property import ExtensionProperty
        return_type = EntityCollection(self.context, ExtensionProperty, self.context.directory_objects.resource_path)
        payload = {
            "isSyncedFromOnPremises": is_synced_from_on_premises
        }
        qry = ServiceOperationQuery(self, "getAvailableExtensionProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove(self, user_id):
        """Remove a user from the group."""

        qry = ServiceOperationQuery(self, "{0}/$ref".format(user_id))
        self.context.add_query(qry)

        def _construct_remove_user_request(request):
            """
            :type request: RequestOptions
            """
            request.method = HttpMethod.Delete
        self.context.before_execute(_construct_remove_user_request)
        return self
