from office365.directory.directoryObject import DirectoryObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path import ResourcePath


class DirectoryObjectCollection(ClientObjectCollection):
    """User's collection"""

    def __getitem__(self, key):
        return DirectoryObject(self.context,
                               ResourcePath(key, self.resourcePath))

    def getByIds(self, ids):
        """Returns the directory objects specified in a list of IDs."""
        result = ClientResult(None)
        qry = ServiceOperationQuery(self, "getByIds", None, None, None, result)
        self.context.add_query(qry)
        return result
