from office365.directory.directoryObject import DirectoryObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath


class DirectoryObjectCollection(ClientObjectCollection):
    """User's collection"""

    def __getitem__(self, key):
        if type(key) == int:
            return self._data[key]
        return DirectoryObject(self.context,
                               ResourcePath(key, self.resourcePath))

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

    def remove(self, user_id):
        """Remove a user from the group."""
        qry = ServiceOperationQuery(self, "{0}/$ref".format(user_id))
        self.context.add_query(qry)
        self.context.get_pending_request().beforeExecute += self._construct_remove_user_request

    def _construct_remove_user_request(self, request):
        request.method = HttpMethod.Delete
        self.context.get_pending_request().beforeExecute -= self._construct_remove_user_request
