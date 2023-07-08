from office365.runtime.paths.key import KeyPath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


class FolderCollection(BaseEntityCollection):
    """Represents a collection of Folder resources."""
    def __init__(self, context, resource_path=None, parent=None):
        super(FolderCollection, self).__init__(context, Folder, resource_path, parent)

    def add_using_path(self, decoded_url, overwrite):
        """
        Adds the folder located at the specified path to the collection.

        :param str decoded_url: Specifies the path for the folder.
        :param bool overwrite:  bool
        """
        parameters = {
            "DecodedUrl": decoded_url,
            "Overwrite": overwrite
        }
        target_folder = Folder(self.context)
        qry = ServiceOperationQuery(self, "AddUsingPath", parameters, None, None, target_folder)
        self.context.add_query(qry)
        return target_folder

    def ensure_path(self, path):
        """
        Ensures a folder exist

        :param str path: server or site relative url to a folder
        """
        names = [name for name in path.split("/") if name]
        if not names:
            raise ValueError("Invalid server or site relative url")

        name, child_names = names[0], names[1:]
        folder = self.add(name)
        for name in child_names:
            folder = folder.add(name)
        return folder

    def add(self, name):
        """Adds the folder that is located at the specified URL to the collection.

        :param str name: Specifies the Name of the folder.
        """
        return_type = Folder(self.context, KeyPath(name, self.resource_path))
        self.add_child(return_type)
        qry = ServiceOperationQuery(self, "Add", [name], None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_by_url(self, url):
        """Retrieve Folder resource by url

        :param str url: Specifies the URL of the list folder. The URL MUST be an absolute URL, a server-relative URL,
            a site-relative URL relative to the site (2) containing the collection of list folders, or relative to the
            list folder that directly contains this collection of list folders.
        """
        return Folder(self.context, ServiceOperationPath("GetByUrl", [url], self.resource_path))

    def get_by_path(self, decoded_url):
        """
        Get folder at the specified path.

        :param str decoded_url: Specifies the path for the folder.
        """
        return Folder(self.context, ServiceOperationPath("GetByPath", SPResPath(decoded_url), self.resource_path))
