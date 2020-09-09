from office365.directory.directoryObject import DirectoryObject
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class DirectoryObjectCollection(EntityCollection):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, DirectoryObject, resource_path)

    def get(self):
        return super().get()

    def __getitem__(self, key):
        """

        :param key: key is used to address a DirectoryObject resource by either an index in collection
        or by resource id
        :type key: int or str
        :rtype: DirectoryObject
        """
        if type(key) == int:
            return super().__getitem__(key)
        return self._item_type(self.context,
                               ResourcePath(key, self.resource_path))

    def getByIds(self, ids):
        """Returns the directory objects specified in a list of IDs."""
        result = ClientResult(None)
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
