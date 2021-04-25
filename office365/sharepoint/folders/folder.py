from office365.runtime.client_result import ClientResult
from office365.runtime.queries.create_entity_query import CreateEntityQuery
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
from office365.sharepoint.storagemetrics.storage_metrics import StorageMetrics
from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil


class Folder(BaseEntity):
    """Represents a folder in a SharePoint Web site."""

    @staticmethod
    def from_url(abs_url):
        """
        Addresses a Folder by absolute url

        :type abs_url: str
        """
        from office365.sharepoint.client_context import ClientContext
        ctx = ClientContext.from_url(abs_url)
        relative_url = abs_url.replace(ctx.base_url, "")
        return ctx.web.get_folder_by_server_relative_url(relative_url)

    def recycle(self):
        """Moves the folder to the Recycle Bin and returns the identifier of the new Recycle Bin item."""

        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, result)
        self.context.add_query(qry)
        return result

    def recycle_with_parameters(self, parameters):
        """

        :type parameters: office365.sharepoint.folders.folder_delete_parameters.FolderDeleteParameters
        """
        result = ClientResult(self.context)
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

    def copy_to(self, new_relative_url, keep_both=False, reset_author_and_created=False):
        """Copies the folder with files to the destination URL.

        :type new_relative_url: str
        :type keep_both: bool
        :type reset_author_and_created: bool
        """

        def _build_full_url(rel_url):
            return self.context.base_url + rel_url

        def _copy_folder():
            opts = MoveCopyOptions(keep_both=keep_both, reset_author_and_created_on_copy=reset_author_and_created)
            MoveCopyUtil.copy_folder(self.context, _build_full_url(self.serverRelativeUrl),
                                     _build_full_url(new_relative_url), opts)

        self.ensure_property("ServerRelativeUrl", _copy_folder)
        return self.context.web.get_folder_by_server_relative_url(new_relative_url)

    def move_to(self, new_relative_url, retain_editor_and_modified=False):
        """Moves the folder with files to the destination URL.

        :type new_relative_url: str
        :type retain_editor_and_modified: bool
        """

        def _build_full_url(rel_url):
            return self.context.base_url + rel_url

        def _move_folder():
            MoveCopyUtil.move_folder(self.context, _build_full_url(self.serverRelativeUrl),
                                     _build_full_url(new_relative_url),
                                     MoveCopyOptions(retain_editor_and_modified_on_move=retain_editor_and_modified))

        self.ensure_property("ServerRelativeUrl", _move_folder)
        return self.context.web.get_folder_by_server_relative_url(new_relative_url)

    @property
    def storage_metrics(self):
        return self.properties.get("StorageMetrics",
                                   StorageMetrics(self.context, ResourcePath("StorageMetrics", self.resource_path)))

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
