from office365.runtime.client_result import ClientResult
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.actions.create_file import CreateFileQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.files.file_creation_information import FileCreationInformation
from office365.sharepoint.listitems.listitem import ListItem


class Folder(BaseEntity):
    """Represents a folder in a SharePoint Web site."""

    def recycle(self):
        """Moves the folder to the Recycle Bin and returns the identifier of the new Recycle Bin item."""

        result = ClientResult(None)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        return result

    def recycle_with_parameters(self, parameters):
        """

        :type parameters: office365.sharepoint.folders.folder_delete_parameters.FolderDeleteParameters
        """
        result = ClientResult(None)
        qry = ServiceOperationQuery(self, "RecycleWithParameters", None, parameters, "parameters", result)
        self.context.add_query(qry)
        return result

    def get_changes(self, query=None):
        """Returns the collection of changes from the change log that have occurred within the folder,
           based on the specified query.

        :param office365.sharepoint.changeQuery.ChangeQuery query: Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(folder=True)
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

    def get_list_item_changes(self, query):
        """

        :param office365.sharepoint.changeQuery.ChangeQuery query: Specifies which changes to return
        """
        changes = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getListItemChanges", None, query, "query", changes)
        self.context.add_query(qry)
        return changes

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
        return self

    def delete_object(self):
        """Deletes the folder."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    def upload_file(self, file_name, content):
        """Uploads a file into folder

        :type file_name: str
        :type content: str
        :rtype: office365.sharepoint.files.file.File
        """
        info = FileCreationInformation(url=file_name, overwrite=True, content=content)
        qry = CreateFileQuery(self.files, info)
        self.context.add_query(qry)
        return qry.return_type

    def copy_to(self, new_relative_url, overwrite):
        """Copies the folder with files to the destination URL.

        :type new_relative_url: str
        :type overwrite: bool
        """

        def _copy_files():
            for file in self.files:
                new_file_url = "/".join([new_relative_url, file.properties['Name']])
                file.copyto(new_file_url, overwrite)

        self.ensure_property("Files", _copy_files)
        return self

    def move_to(self, new_relative_url, flags):
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
        return self

    @property
    def list_item_all_fields(self):
        """Specifies the list item fields (2) values for the list item corresponding to the folder."""
        return self.properties.get("ListItemAllFields",
                                   ListItem(self.context, ResourcePath("ListItemAllFields", self.resource_path)))

    @property
    def files(self):
        """Get a file collection"""
        if self.is_property_available('Files'):
            return self.properties["Files"]
        else:
            from office365.sharepoint.files.file_collection import FileCollection
            return FileCollection(self.context, ResourcePath("Files", self.resource_path))

    @property
    def folders(self):
        """Specifies the collection of list folders contained within the list folder.
        """
        from office365.sharepoint.folders.folder_collection import FolderCollection
        return self.properties.get("Folders",
                                   FolderCollection(self.context, ResourcePath("Folders", self.resource_path)))

    @property
    def parent_folder(self):
        """Specifies the list folder.
        """
        return self.properties.get("ParentFolder",
                                   Folder(self.context, ResourcePath("ParentFolder", self.resource_path)))

    @property
    def name(self):
        """Specifies the list folder name.
        :rtype: str or None
        """
        return self.properties.get("Name", None)

    @property
    def unique_id(self):
        """Gets the unique ID of the folder.
        :rtype: str or None
        """
        return self.properties.get("UniqueId", None)

    @property
    def exists(self):
        """Gets a Boolean value that indicates whether the folder exists.
        :rtype: bool or None
        """
        return self.properties.get("Exists", None)

    @property
    def welcome_page(self):
        """Specifies the server-relative URL for the list folder Welcome page.
        :rtype: str or None
        """
        return self.properties.get("WelcomePage", None)

    @property
    def unique_content_type_order(self):
        """Specifies the content type order for the list folder.

        :rtype: office365.sharepoint.contenttypes.content_type_id.ContentTypeId or None
        """
        return self.properties.get("UniqueContentTypeOrder", None)

    @property
    def content_type_order(self):
        """Specifies the content type order for the list folder.

        :rtype: office365.sharepoint.contenttypes.content_type_id.ContentTypeId or None
        """
        return self.properties.get("ContentTypeOrder", ContentTypeId())

    @property
    def time_last_modified(self):
        """Gets the last time this folder or a direct child was modified in UTC.

        :rtype: str or None
        """
        return self.properties.get("TimeLastModified", None)

    @property
    def serverRelativeUrl(self):
        """Gets the server-relative URL of the list folder.
        :rtype: str or None
        """
        return self.properties.get("ServerRelativeUrl", None)

    def get_property(self, name):
        property_mapping = {
            "ListItemAllFields": self.list_item_all_fields,
            "ParentFolder": self.parent_folder
        }
        if name in property_mapping:
            return property_mapping[name]
        else:
            return super(Folder, self).get_property(name)

    def set_property(self, name, value, persist_changes=True):
        super(Folder, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "ServerRelativeUrl":
            self._resource_path = ResourcePathServiceOperation("getFolderByServerRelativeUrl", [value],
                                                               ResourcePath("Web"))
        elif name == "UniqueId":
            self._resource_path = ResourcePathServiceOperation("getFolderById", [value], ResourcePath("Web"))
        return self
