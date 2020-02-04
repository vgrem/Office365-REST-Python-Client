from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.client_result import ClientResult
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.utilities.http_method import HttpMethod
from office365.directory.user import User


class DirectoryObjectCollection(ClientObjectCollection):
    """User's collection"""

    def __getitem__(self, key):
        return User(self.context,
                    ResourcePathEntity(self.context, self.resourcePath, key))

    def getByIds(self, ids):
        """Returns the directory objects specified in a list of IDs."""
        qry = ServiceOperationQuery(self,
                                    HttpMethod.Post,
                                    "getByIds",
                                    None
                                    )
        result = ClientResult(None)
        self.context.add_query(qry, result)
        return result
