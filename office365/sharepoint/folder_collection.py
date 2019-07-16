from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.folder import Folder


class FolderCollection(ClientObjectCollection):
    """Represents a collection of Folder resources."""
    def __init__(self, context, resource_path=None):
        super(FolderCollection, self).__init__(context, Folder, resource_path)

    def add(self, folder_url):
        folder = Folder(self.context)
        folder.set_property("ServerRelativeUrl", folder_url)
        qry = ClientQuery(self.url, ActionType.CreateEntry, folder.convert_to_payload())
        self.context.add_query(qry, folder)
        return folder

    def get_by_url(self, url):
        """Retrieve Folder resource by url"""
        return Folder(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "GetByUrl", [url]))
