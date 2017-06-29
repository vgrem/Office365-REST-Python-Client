from office365.runtime.action_type import ActionType
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class FolderCollection(ClientObjectCollection):
    """Represents a collection of Folder resources."""

    def add(self, folder_url):
        from office365.sharepoint.folder import Folder
        folder = Folder(self.context)
        folder.set_property("ServerRelativeUrl", folder_url)
        qry = ClientQuery(self.url, ActionType.CreateEntry, folder.convert_to_payload())
        self.context.add_query(qry, folder)
        return folder

    def get_by_url(self, url):
        """Retrieve Folder resource by url"""
        from office365.sharepoint.folder import Folder
        return Folder(self.context, ResourcePathServiceOperation(self.context, self.resource_path, "GetByUrl", [url]))
