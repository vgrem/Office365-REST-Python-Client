from functools import partial
from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import UpdateEntityQuery, DeleteEntityQuery, CreateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.file_creation_information import FileCreationInformation
from office365.sharepoint.listitem import ListItem


def _copy_files(new_folder_relative_url, overwrite, folder):
    """Copies files

    :type new_folder_relative_url: str
    :type overwrite: bool
    :type folder: Folder
    """
    for file in folder.files:
        new_file_url = "/".join([new_folder_relative_url, file.properties['Name']])
        file.copyto(new_file_url, overwrite)


def _move_folder_with_files(new_folder_relative_url, flag, folder):
    """Moves folder with files

    :type new_folder_relative_url: str
    :type flag: int
    :type folder: Folder
    """
    for file in folder.files:
        new_file_url = "/".join([new_folder_relative_url, file.properties['Name']])
        file.moveto(new_file_url, flag)


def _add_sub_folder(new_folder_name, target_folder, parent_folder):
    """Creates sub folder by name

    :type new_folder_name: str
    :type parent_folder: Folder
    """
    new_folder_url = "/".join([parent_folder.properties['ServerRelativeUrl'], new_folder_name])
    target_folder.set_property("ServerRelativeUrl", new_folder_url)
    qry = CreateEntityQuery(parent_folder.folders, target_folder, target_folder)
    parent_folder.context.add_query(qry)


class Folder(ClientObject):
    """Represents a folder in a SharePoint Web site."""

    def add(self, name):
        """Adds the folder that is located under a current folder

        :type name: str
        """
        new_folder = Folder(self.context)
        self.ensure_property("ServerRelativeUrl", partial(_add_sub_folder, name, new_folder))
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

    def update(self):
        qry = UpdateEntityQuery(self)
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
        self.ensure_property("Files", partial(_copy_files, new_relative_url, overwrite))

    def moveto(self, new_relative_url, flags):
        """Moves the folder with files to the destination URL.

        :type new_relative_url: str
        :type flags: int
        """
        if flags:
            pass
        self.ensure_property("Files", partial(_move_folder_with_files, new_relative_url, flags))

    @property
    def list_item_all_fields(self):
        """Specifies the list item field (2) values for the list item corresponding to the folder."""
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
            from office365.sharepoint.file_collection import FileCollection
            return FileCollection(self.context, ResourcePath("Files", self.resource_path))

    @property
    def folders(self):
        """Get a folder collection"""
        if self.is_property_available('Folders'):
            return self.properties["Folders"]
        else:
            from office365.sharepoint.folder_collection import FolderCollection
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
