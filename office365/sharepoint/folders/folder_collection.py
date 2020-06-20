from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.folders.folder import Folder


class FolderCollection(ClientObjectCollection):
    """Represents a collection of Folder resources."""
    def __init__(self, context, resource_path=None):
        super(FolderCollection, self).__init__(context, Folder, resource_path)

    def add(self, server_relative_url):
        """Adds the folder that is located at the specified URL to the collection.
        :type server_relative_url: str
        """
        folder = Folder(self.context)
        self.add_child(folder)
        folder.set_property("ServerRelativeUrl", server_relative_url)
        qry = CreateEntityQuery(self, folder, folder)
        self.context.add_query(qry)
        return folder

    def get_by_url(self, url):
        """Retrieve Folder resource by url
        :type url: str
        """
        return Folder(self.context, ResourcePathServiceOperation("GetByUrl", [url], self.resource_path))
