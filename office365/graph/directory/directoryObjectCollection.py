from office365.graph.directory.directoryObject import DirectoryObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.resource_path import ResourcePath
from office365.runtime.serviceOperationQuery import ServiceOperationQuery


class DirectoryObjectCollection(ClientObjectCollection):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super(DirectoryObjectCollection, self).__init__(context, DirectoryObject, resource_path)

    def __getitem__(self, key):
        """

        :param key: key is used to address a DirectoryObject resource by either an index in collection
        or by resource id
        :type key: int or str
        """
        if type(key) == int:
            return super(DirectoryObjectCollection, self).__getitem__(key)
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

    def remove(self, user_id):
        """Remove a user from the group."""
        qry = ServiceOperationQuery(self, "{0}/$ref".format(user_id))
        self.context.add_query(qry)
        self.context.get_pending_request().beforeExecute += self._construct_remove_user_request

    def _construct_remove_user_request(self, request):
        """

        :type request: RequestOptions
        """
        request.method = HttpMethod.Delete
        self.context.get_pending_request().beforeExecute -= self._construct_remove_user_request
