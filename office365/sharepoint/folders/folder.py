from office365.runtime.client_result import ClientResult
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.change_collection import ChangeCollection
from office365.sharepoint.changes.change_query import ChangeQuery
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.internal.paths.entity_resource import EntityResourcePath
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.storagemetrics.storage_metrics import StorageMetrics
from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.runtime.compat import urlparse


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
        Gets the collection of all changes from the change log that have occurred within the scope of the SharePoint
        folder based on the specified query.

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
        return self.folders.add(name)

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
        return self.files.upload(file_name, content)

    def copy_to(self, new_relative_url, keep_both=False, reset_author_and_created=False):
        """Copies the folder with files to the destination URL.

        :type new_relative_url: str
        :type keep_both: bool
        :type reset_author_and_created: bool
        """

        target_folder = Folder(self.context)
        target_folder.set_property("ServerRelativeUrl", new_relative_url)

        def _copy_folder():
            opts = MoveCopyOptions(keep_both=keep_both, reset_author_and_created_on_copy=reset_author_and_created)
            MoveCopyUtil.copy_folder(self.context, self._build_full_url(self.serverRelativeUrl),
                                     self._build_full_url(new_relative_url), opts)

        self.ensure_property("ServerRelativeUrl", _copy_folder)
        return target_folder

    def copy_to_by_path(self, new_relative_path, keep_both=False, reset_author_and_created=False):
        """Copies the folder with files to the destination Path.

        :type new_relative_path: str
        :type keep_both: bool
        :type reset_author_and_created: bool
        """

        target_folder = Folder(self.context)
        target_folder.set_property("ServerRelativePath", SPResPath(new_relative_path))

        def _copy_folder():
            opts = MoveCopyOptions(keep_both=keep_both, reset_author_and_created_on_copy=reset_author_and_created)
            MoveCopyUtil.copy_folder_by_path(self.context, self._build_full_url(self.server_relative_path.DecodedUrl),
                                             self._build_full_url(new_relative_path), opts)

        self.ensure_property("ServerRelativePath", _copy_folder)
        return target_folder

    def move_to(self, new_relative_url, retain_editor_and_modified=False):
        """Moves the folder with files to the destination URL.

        :type new_relative_url: str
        :type retain_editor_and_modified: bool
        """
        target_folder = Folder(self.context)
        target_folder.set_property("ServerRelativeUrl", new_relative_url)

        def _move_folder():
            MoveCopyUtil.move_folder(self.context, self._build_full_url(self.serverRelativeUrl),
                                     self._build_full_url(new_relative_url),
                                     MoveCopyOptions(retain_editor_and_modified_on_move=retain_editor_and_modified))

        self.ensure_property("ServerRelativeUrl", _move_folder)
        return target_folder

    def move_to_by_path(self, new_relative_path, retain_editor_and_modified=False):
        """Moves the folder with files to the destination Path.

        :type new_relative_path: str
        :type retain_editor_and_modified: bool
        """
        target_folder = Folder(self.context)
        target_folder.set_property("ServerRelativePath", SPResPath(new_relative_path))

        def _move_folder():
            MoveCopyUtil.move_folder_by_path(self.context, self._build_full_url(self.server_relative_path.DecodedUrl),
                                             self._build_full_url(new_relative_path),
                                             MoveCopyOptions(
                                                 retain_editor_and_modified_on_move=retain_editor_and_modified))

        self.ensure_property("ServerRelativePath", _move_folder)
        return target_folder

    @property
    def storage_metrics(self):
        """"""
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
        from office365.sharepoint.files.file_collection import FileCollection
        return self.properties.get("Files",
                                   FileCollection(self.context, ResourcePath("Files", self.resource_path)))

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
    def is_wopi_enabled(self):
        return self.properties.get("IsWOPIEnabled", None)

    @property
    def prog_id(self):
        """Gets the identifier (ID) of the application in which the folder was created."""
        return self.properties.get("ProgID", None)

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
        return self.properties.get("UniqueContentTypeOrder", ContentTypeId())

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

    @property
    def server_relative_path(self):
        """Gets the server-relative Path of the list folder.
        :rtype: SPResPath or None
        """
        return self.properties.get("ServerRelativePath", SPResPath(None))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "ContentTypeOrder": self.content_type_order,
                "UniqueContentTypeOrder": self.unique_content_type_order,
                "ListItemAllFields": self.list_item_all_fields,
                "ParentFolder": self.parent_folder,
                "ServerRelativePath": self.server_relative_path,
                "StorageMetrics": self.storage_metrics
            }
            default_value = property_mapping.get(name, None)
        return super(Folder, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        super(Folder, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if name == "ServerRelativeUrl":
            self._resource_path = ServiceOperationPath("getFolderByServerRelativeUrl", [value], ResourcePath("Web"))
        elif name == "ServerRelativePath":
            self._resource_path = ServiceOperationPath("getFolderByServerRelativePath", [value], ResourcePath("Web"))
        elif name == "UniqueId":
            self._resource_path = ServiceOperationPath("getFolderById", [value], ResourcePath("Web"))

    def _build_full_url(self, rel_url):
        """
        :type rel_url: str
        """
        site_path = urlparse(self.context.base_url).path
        return self.context.base_url.replace(site_path, "") + rel_url
