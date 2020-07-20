from office365.runtime.client_query import CreateEntityQuery, DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.files.file_creation_information import FileCreationInformation
from office365.sharepoint.listitems.listitem import ListItem


class Folder(BaseEntity):
    """Represents a folder in a SharePoint Web site."""

    def add(self, name):
        """Adds the folder that is located under a current folder

        :type name: str
        """
        new_folder = Folder(self.context)

        def _add_sub_folder():
            new_folder_url = "/".join([self.serverRelativeUrl, name])
            new_folder.set_property("ServerRelativeUrl", new_folder_url)
            qry = CreateEntityQuery(self.folders, new_folder, new_folder)
            self.context.add_query(qry)
        self.ensure_property("ServerRelativeUrl", _add_sub_folder)
        return new_folder

    def rename(self, name):
        """Rename a Folder resource

        :type name: str
        """
        item = self.list_item_all_fields
        item.set_property('Title', name)
        item.set_property('FileLeafRef', name)
        qry = UpdateEntityQuery(item)
        self.context.add_query(qry)

    def delete_object(self):
        """Deletes the folder."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()

    def upload_file(self, name, content):
        """Uploads a file into folder

        :type name: str
        :type content: str
        """
        info = FileCreationInformation()
        info.content = content
        info.url = name
        info.overwrite = True
        target_file = self.files.add(info)
        return target_file

    def copyto(self, new_relative_url, overwrite):
        """Copies the folder with files to the destination URL.

        :type new_relative_url: str
        :type overwrite: bool
        """

        def _copy_files():
            for file in self.files:
                new_file_url = "/".join([new_relative_url, file.properties['Name']])
                file.copyto(new_file_url, overwrite)

        self.ensure_property("Files", _copy_files)

    def moveto(self, new_relative_url, flags):
        """Moves the folder with files to the destination URL.

        :type new_relative_url: str
        :type flags: int
        """
        if flags:
            pass

        def _move_folder_with_files():
            """Moves folder with files"""
            for file in self.files:
                new_file_url = "/".join([new_relative_url, file.properties['Name']])
                file.moveto(new_file_url, flags)
        self.ensure_property("Files", _move_folder_with_files)

    @property
    def list_item_all_fields(self):
        """Specifies the list item fields (2) values for the list item corresponding to the folder."""
        if self.is_property_available('ListItemAllFields'):
            return self.properties["ListItemAllFields"]
        else:
            return ListItem(self.context, ResourcePath("ListItemAllFields", self.resource_path))

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            from office365.sharepoint.files.file_collection import FileCollection
            return FileCollection(self.context, ResourcePath("Files", self.resource_path))

    @property
    def serverRelativeUrl(self):
        """Gets the server-relative URL of the list folder.
        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            from office365.sharepoint.folders.folder_collection import FolderCollection
            return FolderCollection(self.context, ResourcePath("Folders", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(Folder, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = ResourcePathServiceOperation("getFolderByServerRelativeUrl", [value],
                                                                   ResourcePath("Web"))
            elif name == "UniqueId":
                self._resource_path = ResourcePathServiceOperation("getFolderById", [value], ResourcePath("Web"))
