from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.storagemetrics.storage_metrics import StorageMetrics
from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath


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

    def get_files(self, recursive=False):
        """
        Retrieves files

        :param bool recursive: Determines whether to enumerate folders recursively
        """
        from office365.sharepoint.files.collection import FileCollection
        return_type = FileCollection(self.context, self.files.resource_path)

        def _loaded(parent):
            """
            :type parent: Folder
            """
            [return_type.add_child(f) for f in parent.files]
            if recursive:
                for folder in parent.folders:
                    folder.ensure_properties(["Files", "Folders"], _loaded, parent=folder)

        self.ensure_properties(["Files", "Folders"], _loaded, parent=self)
        return return_type

    def get_sharing_information(self):
        """Gets the sharing information for a folder."""
        return self.list_item_all_fields.get_sharing_information()

    def move_to(self, new_url):
        """
        Moves the folder and its contents to a new folder at the specified URL.
        This method applies only to the context of a single site.

        An exception is thrown if a folder with the same name as specified in the parameter already exists.

        :param str new_url: A string that specifies the URL for the new folder.
        """
        return_type = Folder(self.context)
        return_type.set_property("ServerRelativeUrl", new_url)
        payload = {"newUrl": new_url}
        qry = ServiceOperationQuery(self, "MoveTo", payload)
        self.context.add_query(qry)
        return return_type

    def move_to_with_parameters(self, new_relative_url, retain_editor_and_modified=False):
        """Moves the folder with files to the destination URL.

        :type new_relative_url: str
        :type retain_editor_and_modified: bool
        """
        return_type = Folder(self.context)
        return_type.set_property("ServerRelativeUrl", new_relative_url)

        def _move_folder():
            opt = MoveCopyOptions(retain_editor_and_modified_on_move=retain_editor_and_modified)
            MoveCopyUtil.move_folder(self.context, self.serverRelativeUrl, new_relative_url, opt)

        self.ensure_property("ServerRelativeUrl", _move_folder)
        return return_type

    def move_to_using_path(self, new_path):
        """
        Moves the folder and its contents to a new folder at the specified path.
        An exception is thrown if a folder with the same name as specified in the parameter already exists.

        :param str new_path: Specifies the destination path.
        """
        qry = ServiceOperationQuery(self, "MoveToUsingPath", SPResPath(new_path))
        self.context.add_query(qry)
        return self

    def share_link(self, link_kind, expiration=None):
        """Creates a tokenized sharing link for a folder based on the specified parameters and optionally
        sends an email to the people that are listed in the specified parameters.

        :param int link_kind: The kind of the tokenized sharing link to be created/updated or retrieved.
        :param datetime or None expiration: A date/time string for which the format conforms to the ISO 8601:2004(E)
            complete representation for calendar date and time of day and which represents the time and date of expiry
            for the tokenized sharing link. Both the minutes and hour value MUST be specified for the difference
            between the local and UTC time. Midnight is represented as 00:00:00. A null value indicates no expiry.
            This value is only applicable to tokenized sharing links that are anonymous access links.
        """
        return self.list_item_all_fields.share_link(link_kind, expiration)

    def unshare_link(self, link_kind, share_id=None):
        """
        Removes the specified tokenized sharing link of the folder.

        :param int link_kind: This optional value specifies the globally unique identifier (GUID) of the tokenized
            sharing link that is intended to be removed.
        :param str or None share_id: The kind of tokenized sharing link that is intended to be removed.
        """
        return self.list_item_all_fields.unshare_link(link_kind, share_id)

    def recycle(self):
        """Moves the folder to the Recycle Bin and returns the identifier of the new Recycle Bin item."""

        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle_with_parameters(self, parameters):
        """
        Moves the list folder to the Recycle Bin and returns the identifier of the new Recycle Bin item

        :type parameters: office365.sharepoint.folders.delete_parameters.FolderDeleteParameters
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
        return_type = ChangeCollection(self.context)
        qry = ServiceOperationQuery(self, "getListItemChanges", None, query, "query", return_type)
        self.context.add_query(qry)
        return return_type

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
        """
        return self.files.add(file_name, content, True)

    def copy_to(self, new_relative_url, keep_both=False, reset_author_and_created=False):
        """Copies the folder with files to the destination URL.

        :type new_relative_url: str
        :type keep_both: bool
        :type reset_author_and_created: bool
        """

        return_type = Folder(self.context)
        return_type.set_property("ServerRelativeUrl", new_relative_url)

        def _copy_folder():
            opts = MoveCopyOptions(keep_both=keep_both, reset_author_and_created_on_copy=reset_author_and_created)
            MoveCopyUtil.copy_folder(self.context, self.serverRelativeUrl, new_relative_url, opts)

        self.ensure_property("ServerRelativeUrl", _copy_folder)
        return return_type

    def copy_to_using_path(self, new_relative_path, keep_both=False, reset_author_and_created=False):
        """Copies the folder with files to the destination Path.

        :type new_relative_path: str
        :type keep_both: bool
        :type reset_author_and_created: bool
        """

        return_type = Folder(self.context)
        return_type.set_property("ServerRelativePath", new_relative_path)

        def _copy_folder():
            opts = MoveCopyOptions(keep_both=keep_both, reset_author_and_created_on_copy=reset_author_and_created)
            MoveCopyUtil.copy_folder_by_path(self.context, str(self.server_relative_path), new_relative_path,
                                             opts)

        self.ensure_property("ServerRelativePath", _copy_folder)
        return return_type

    def move_to_using_path_with_parameters(self, new_relative_path, retain_editor_and_modified=False):
        """Moves the folder with files to the destination Path.

        :param str new_relative_path: A full URL path that represents the destination folder.
        :param bool retain_editor_and_modified:
        """
        return_type = Folder(self.context)
        return_type.set_property("ServerRelativePath", SPResPath(new_relative_path))

        def _move_folder():
            opt = MoveCopyOptions(retain_editor_and_modified_on_move=retain_editor_and_modified)
            MoveCopyUtil.move_folder_by_path(self.context, self.server_relative_path.DecodedUrl, new_relative_path, opt)

        self.ensure_property("ServerRelativePath", _move_folder)
        return return_type

    @property
    def storage_metrics(self):
        """Specifies the storage-related metrics for list folders in the site"""
        return self.properties.get("StorageMetrics",
                                   StorageMetrics(self.context, ResourcePath("StorageMetrics", self.resource_path)))

    @property
    def list_item_all_fields(self):
        """Specifies the list item fields (2) values for the list item corresponding to the folder."""
        return self.properties.get("ListItemAllFields",
                                   ListItem(self.context, ResourcePath("ListItemAllFields", self.resource_path)))

    @property
    def files(self):
        """Specifies the collection of files contained in the list folder."""
        from office365.sharepoint.files.collection import FileCollection
        return self.properties.get("Files",
                                   FileCollection(self.context, ResourcePath("Files", self.resource_path)))

    @property
    def folders(self):
        """Specifies the collection of list folders contained within the list folder.
        """
        from office365.sharepoint.folders.collection import FolderCollection
        return self.properties.get("Folders",
                                   FolderCollection(self.context, ResourcePath("Folders", self.resource_path)))

    @property
    def parent_folder(self):
        """Specifies the list folder."""
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
        """
        Indicates whether the folder is enabled for WOPI default action.

        :rtype: bool or None
        """
        return self.properties.get("IsWOPIEnabled", None)

    @property
    def prog_id(self):
        """Gets the identifier (ID) of the application in which the folder was created.

        :rtype: str or None
        """
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
    def time_created(self):
        """Gets when the folder was created in UTC.

        :rtype: datetime or None
        """
        return self.properties.get("TimeCreated", None)

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
        return self.properties.get("ServerRelativePath", SPResPath())

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
        if name == "UniqueId":
            self._resource_path = self.context.web.get_folder_by_id(value).resource_path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = self.context.web.get_folder_by_server_relative_url(value).resource_path
            elif name == "ServerRelativePath":
                self._resource_path = self.context.web.get_folder_by_server_relative_path(value).resource_path
        return self
