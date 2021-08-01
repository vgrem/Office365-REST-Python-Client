import os

from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.folders.folder import Folder


class FolderCollection(BaseEntityCollection):
    """Represents a collection of Folder resources."""
    def __init__(self, context, resource_path=None, parent=None):
        super(FolderCollection, self).__init__(context, Folder, resource_path, parent)

    def get(self):
        """
        :rtype: FolderCollection
        """
        return super(FolderCollection, self).get()

    def add_using_path(self, decoded_url, overwrite):
        """
        :type decoded_url: str
        :type overwrite:  bool
        """
        parameters = {
            "DecodedUrl": decoded_url,
            "Overwrite": overwrite
        }
        target_folder = Folder(self.context)
        qry = ServiceOperationQuery(self, "AddUsingPath", parameters, None, None, target_folder)
        self.context.add_query(qry)
        return target_folder

    def get_by_path(self, decoded_url):
        """

        :type decoded_url: str
        """
        from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
        target_folder = Folder(self.context)
        qry = ServiceOperationQuery(self, "GetByPath", SPResPath(decoded_url), None, "parameters", target_folder)
        self.context.add_query(qry)
        return target_folder

    def ensure_folder_path(self, path):
        """
        Ensures a nested folder hierarchy exist

        :param str path: relative server URL (path) to a folder
        """

        url_component = os.path.normpath(path).split(os.path.sep)
        url_component = [part for part in url_component if part]
        if not url_component:
            raise NotADirectoryError("Wrong relative URL provided")
        child_folder = self
        for url_part in url_component:
            child_folder = child_folder.add(url_part)
        return child_folder

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
