import urllib
from client.client_object_collection import ClientObjectCollection
from client.runtime.client_action_type import ClientActionType
from client.runtime.client_query import ClientQuery


class FolderCollection(ClientObjectCollection):
    """Represents a collection of Folder resources."""

    def add(self, folder_url):
        from client.folder import Folder
        folder = Folder(self.context)
        folder.properties["ServerRelativeUrl"] = folder_url
        qry = ClientQuery(self.url, ClientActionType.Create, folder.metadata)
        self.context.add_query(qry, folder)
        return folder

