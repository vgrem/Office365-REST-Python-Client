from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path
from typing import IO, TYPE_CHECKING, Callable, Iterable, List, Optional, Tuple, Union
from uuid import UUID

from typing_extensions import Self

from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.operations import Progress, ProgressCallback
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.types.odata_property import odata
from office365.sharepoint.changes.collection import ChangeCollection
from office365.sharepoint.changes.query import ChangeQuery
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from office365.sharepoint.entity import Entity
from office365.sharepoint.folders.delete_parameters import FolderDeleteParameters
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sharing.document_manager import DocumentSharingManager
from office365.sharepoint.sharing.links.share_response import ShareLinkResponse
from office365.sharepoint.sharing.object_sharing_information import (
    ObjectSharingInformation,
)
from office365.sharepoint.sharing.user_role_assignment import UserRoleAssignment
from office365.sharepoint.sharing.user_sharing_result import UserSharingResult
from office365.sharepoint.storagemetrics.storage_metrics import StorageMetrics
from office365.sharepoint.thresholds import SAFE_PAGE_SIZE, Limits, limit
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil

if TYPE_CHECKING:
    from office365.runtime.converters.dataframe import DataFrameResult
    from office365.sharepoint.files.collection import FileCollection
    from office365.sharepoint.files.download_operation import DownloadOperation
    from office365.sharepoint.files.file import File
    from office365.sharepoint.folders.collection import FolderCollection

_DEFAULT_CHUNK_SIZE = Limits.UPLOAD_SESSION_CHUNK.value  # simple-upload threshold / upload-session chunk


class Folder(Entity):
    """Represents a folder in a SharePoint Website."""

    def __str__(self):
        return self.name or self.entity_type_name

    def __repr__(self):
        return self.server_relative_url or self.unique_id or self.entity_type_name

    @staticmethod
    def from_url(abs_url: str):
        """Addresses a Folder by absolute url

        Args:
            abs_url (str):
        """
        from office365.sharepoint.client_context import ClientContext

        ctx = ClientContext.from_url(abs_url)
        relative_url = abs_url.replace(ctx.base_url, "")
        return ctx.web.get_folder_by_server_relative_url(relative_url)

    def download_folder_as_zip(
        self,
        download_file: Union[str, Path, IO],
        after_file_downloaded: Optional[Callable[[File], None]] = None,
        recursive: bool = True,
        include_versions: bool = False,
        progress: Optional[ProgressCallback] = None,
    ):
        """Downloads a folder into a zip file

        Args:
            download_file (str or pathlib.Path or IO): Destination zip (a path or
              a seekable file object).
            after_file_downloaded ((office365.sharepoint.files.file.File)->None): A download callback
            recursive (bool): Determines whether to traverse folders recursively
            include_versions (bool): If True, also downloads each file's version history
              into the zip under ``versions/{path}/v{label}``
            progress: Optional hook invoked per downloaded file with a
              ``Progress`` snapshot.
        """
        return MoveCopyUtil.download_folder_as_zip(
            self, download_file, after_file_downloaded, recursive, include_versions, progress
        )

    def download_folder(
        self,
        download_file: Union[str, Path, IO],
        after_file_downloaded: Optional[Callable[[File], None]] = None,
        recursive: bool = True,
        include_versions: bool = False,
        progress: Optional[ProgressCallback] = None,
    ):
        """Deprecated alias of :meth:`download_folder_as_zip`."""
        return self.download_folder_as_zip(download_file, after_file_downloaded, recursive, include_versions, progress)

    def download(
        self,
        target_dir: Union[str, Path],
        *,
        recursive: bool = True,
        overwrite: bool = False,
        resume: bool = False,
        progress: Optional[ProgressCallback] = None,
    ) -> "DownloadOperation":
        """Download this folder's files into a local directory, concurrently.

        Enumerates the folder (paged, optionally recursive) preserving the
        relative tree under ``target_dir``, then downloads the files with
        bounded concurrency and per-file retry. Returns a deferred
        :class:`~office365.sharepoint.files.download_operation.DownloadOperation`;
        drive it with ``execute_query()`` or ``await execute_query_async()``.

        Unlike :meth:`download_folder_as_zip`, this writes loose files (no zip)
        and never requires the caller to open or close destination streams.

        Args:
            target_dir: Local directory to write files into (created as needed).
            recursive: Recurse into subfolders (default ``True``).
            overwrite: When ``False`` (default) existing files are skipped, so a
              re-run resumes where it left off.
            resume: When ``True``, an existing but incomplete destination is
              completed by fetching only the missing byte range, instead of
              being skipped.
            progress: Optional hook invoked with ``Progress`` snapshots
              (``stage="scanning"`` while enumerating, ``"downloading"`` while
              transferring).

        Returns:
            A deferred bulk-download operation.
        """
        from office365.sharepoint.files.download_operation import DownloadOperation

        return DownloadOperation.for_folder(
            self, target_dir, recursive=recursive, overwrite=overwrite, resume=resume, progress=progress
        )

    def upload_folder(
        self,
        source: Union[str, Path, Iterable[Union[str, Path, Tuple[str, Union[str, Path, bytes]]]]],
        after_file_uploaded: Optional[Callable[[File], None]] = None,
        recursive: bool = True,
        progress: Optional[ProgressCallback] = None,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
    ):
        """Upload a local directory / files into this folder — sequential, deferred.

        Counterpart of :meth:`download_folder_as_zip`; see
        :meth:`MoveCopyUtil.upload_folder` for the ``source`` forms (directory,
        file, list of file paths, or ``(relative_path, content)`` pairs).

        Args:
            source: Local directory / file / file list / (path, content) pairs.
            after_file_uploaded ((office365.sharepoint.files.file.File)->None): Per-file callback.
            recursive (bool): Traverse subdirectories when ``source`` is a directory.
            progress: Optional hook invoked per uploaded file with a ``Progress`` snapshot.
            chunk_size (int): Upload-session chunk size / size threshold (bytes).

        Returns:
            The target folder (chainable).
        """
        return MoveCopyUtil.upload_folder(self, source, after_file_uploaded, recursive, progress, chunk_size)

    def upload_folder_from_zip(
        self,
        source_zip: Union[str, Path, IO],
        after_file_uploaded: Optional[Callable[[File], None]] = None,
        progress: Optional[ProgressCallback] = None,
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
    ):
        """Upload a zip archive's file/folder hierarchy into this folder.

        Counterpart of :meth:`download_folder_as_zip`; see
        :meth:`MoveCopyUtil.upload_folder_from_zip`. Entries are read in memory,
        one at a time, and uploaded at their literal relative paths (deferred).

        Args:
            source_zip (str or pathlib.Path or IO): A zip archive (path or file object).
            after_file_uploaded ((office365.sharepoint.files.file.File)->None): Per-file callback.
            progress: Optional hook invoked per uploaded file with a ``Progress`` snapshot.
            chunk_size (int): Upload-session chunk size / size threshold (bytes).

        Returns:
            The target folder (chainable).
        """
        return MoveCopyUtil.upload_folder_from_zip(self, source_zip, after_file_uploaded, progress, chunk_size)

    def get_user_effective_permissions(self, user: str | User) -> ClientResult[BasePermissions]:
        """Returns the user permissions for a folder"""
        return self.list_item_all_fields.get_user_effective_permissions(user)

    def get_folders(
        self,
        recursive: bool = False,
        progress: Optional[Callable[[Progress[Folder]], None]] = None,
    ) -> FolderCollection:
        """Retrieves folders

        Args:
            recursive (bool): Determines whether to enumerate folders recursively
            progress: Optional hook invoked per scanned folder with a
              ``Progress[Folder]`` snapshot (``done`` = folders discovered so
              far; ``items`` = the folders found in the folder just scanned).

        The fluent ``.select([...])`` / ``.expand([...])`` applied to the returned
        collection is honored on every per-folder load.
        """
        from office365.runtime.queries.deferred import DeferredOperationQuery
        from office365.sharepoint.folders.collection import FolderCollection

        return_type = FolderCollection(self.context, self.folders.resource_path, self)

        def _get_folders(parent: Folder) -> None:
            def _on_loaded(folders) -> None:
                for folder in folders:
                    return_type.add_child(folder)
                if callable(progress):
                    progress(Progress(done=len(return_type), stage="scanning", items=list(folders)))
                if recursive:
                    for folder in folders:
                        _get_folders(folder)

            child_folders = parent.folders
            return_type.query_options.apply_to(child_folders)
            if return_type.query_options.select:
                fields = sorted({"Id", "Name", "ServerRelativeUrl"} | set(return_type.query_options.select))
                child_folders.select(fields)
            child_folders.get().after_execute(_on_loaded)

        placeholder = DeferredOperationQuery(self.context)
        self.context.add_query(placeholder).after_execute(lambda _: _get_folders(self))
        return return_type

    @limit(Limits.LIST_VIEW, arg="page_size")
    def get_files(
        self,
        recursive: bool = False,
        progress: Optional[Callable[[Progress[File]], None]] = None,
        page_size: int = SAFE_PAGE_SIZE,
    ) -> FileCollection:
        """Retrieves files (paged, so it works on folders with >5,000 items).

        Args:
            recursive (bool): Determines whether to enumerate folders recursively
            progress: Optional hook invoked per scanned page with a
              ``Progress[File]`` snapshot (``done`` = files discovered so far;
              ``items`` = the files found in the page just scanned).
            page_size (int): Items per page (kept below the 5,000-item list view
              threshold so large folders are read without being throttled).

        The fluent ``.select([...])`` / ``.expand([...])`` applied to the returned
        collection is honored on every per-folder file load.
        """
        from office365.runtime.queries.deferred import DeferredOperationQuery
        from office365.sharepoint.files.collection import FileCollection

        resource_path = self.files.resource_path
        assert resource_path is not None
        return_type = FileCollection(self.context, resource_path, self)

        def _get_files(parent: Folder) -> None:
            files = parent.files
            return_type.query_options.apply_to(files)
            if return_type.query_options.select:
                fields = sorted({"Id", "Name", "ServerRelativeUrl"} | set(return_type.query_options.select))
                files.select(fields)
            seen = {"count": 0}

            def _on_files_page(col: FileCollection) -> None:
                new_files = list(col)[seen["count"] :]
                seen["count"] = len(col)
                for file in new_files:
                    return_type.add_child(file)
                if callable(progress):
                    progress(Progress(done=len(return_type), stage="scanning", items=new_files))
                if recursive and not col.has_next:
                    _scan_subfolders(parent)

            files.get_all(page_size, page_loaded=_on_files_page)

        def _scan_subfolders(parent: Folder) -> None:
            subfolders = parent.folders
            seen = {"count": 0}

            def _on_folders_page(col: "FolderCollection") -> None:
                for folder in list(col)[seen["count"] :]:
                    _get_files(folder)
                seen["count"] = len(col)

            subfolders.get_all(page_size, page_loaded=_on_folders_page)

        placeholder = DeferredOperationQuery(self.context)
        self.context.add_query(placeholder).after_execute(lambda _: _get_files(self))
        return return_type

    def get_sharing_information(self) -> ObjectSharingInformation:
        """Gets the sharing information for a folder."""
        return self.list_item_all_fields.get_sharing_information()

    def move_to(self, destination: Union[str, Folder]) -> Self:
        """Moves the folder and its contents under a new folder at the specified destination.
        This method applies only to the context of a single site.

        An exception is thrown if a folder with the same name as specified in the parameter already exists.

        Args:
            destination (str or Folder): Specifies the server relative url or an existing folder where to move a folder.
        """

        def _move_to(destination_folder: Folder) -> None:
            destination_url = "/".join([x or "" for x in [destination_folder.server_relative_url, self.name]])
            qry = ServiceOperationQuery(self, "MoveTo", {"newUrl": destination_url})

            def _update_folder(_):
                self.set_property("ServerRelativeUrl", destination_url)

            self.context.add_query(qry).after_execute(_update_folder)

        def _source_folder_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativeUrl").after_execute(lambda _: _move_to(dest))
            else:
                self.context.web.ensure_folder_path(destination).after_execute(_move_to)

        self.ensure_properties(["ServerRelativeUrl", "Name"]).after_execute(lambda _: _source_folder_resolved())
        return self

    def move_to_using_path(self, destination: Union[str, Folder]) -> Self:
        """Moves the folder and its contents to a new folder at the specified path.
        An exception is thrown if a folder with the same name as specified in the parameter already exists.

        Args:
            destination (str or Folder): Specifies the server relative url or an existing folder where to move a folder.
        """

        def _move_to_using_path(destination_folder: Folder) -> None:
            destination_path = "/".join([x or "" for x in [str(destination_folder.server_relative_path), self.name]])
            qry = ServiceOperationQuery(self, "MoveToUsingPath", {"DecodedUrl": destination_path})

            def _update_folder(url):
                self.set_property("ServerRelativePath", destination_path)

            self.context.add_query(qry).after_execute(_update_folder)

        def _source_folder_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativePath").after_execute(lambda _: _move_to_using_path(dest))
            else:
                self.context.web.ensure_folder_path(destination).after_execute(_move_to_using_path)

        self.ensure_properties(["ServerRelativePath", "Name"]).after_execute(lambda _: _source_folder_resolved())
        return self

    def move_to_using_path_with_parameters(
        self, new_relative_path: str, retain_editor_and_modified: bool = False
    ) -> Folder:
        """Moves the folder with files to the destination Path.

        Args:
            new_relative_path (str): A full URL path that represents the destination folder.
            retain_editor_and_modified (bool):
        """
        return_type = Folder(self.context)
        return_type.set_property("ServerRelativePath", SPResPath(new_relative_path))

        def _move_folder():
            opt = MoveCopyOptions(RetainEditorAndModifiedOnMove=retain_editor_and_modified)
            assert self.server_relative_path is not None
            MoveCopyUtil.move_folder_by_path(self.context, self.server_relative_path.DecodedUrl, new_relative_path, opt)

        self.ensure_property("ServerRelativePath").after_execute(lambda _: _move_folder())
        return return_type

    def share_link(
        self,
        link_kind: int,
        expiration: Optional[datetime] = None,
        role: Optional[int] = None,
        password: Optional[str] = None,
        share_id: Optional[str] = None,
    ) -> ClientResult[ShareLinkResponse]:
        """Creates a tokenized sharing link for a folder based on the specified parameters and optionally
        sends an email to the people that are listed in the specified parameters.

        Args:
            link_kind: The kind of the tokenized sharing link to be created/updated or retrieved.
            expiration: A date/time string for which the format conforms to the ISO 8601:2004(E) complete representation
                for calendar date and time of day and which represents the time and date of expiry for the tokenized
                sharing link. Both the minutes and hour value MUST be specified for the difference between the local and
                UTC time. Midnight is represented as 00:00:00. A null value indicates no expiry. This value is only
                applicable to tokenized sharing links that are anonymous access links.
            role: The role to be used for the tokenized sharing link. This is required for Flexible links and ignored
                for all other kinds.
            password: Optional password value to apply to the tokenized sharing link, if it can support password
                protection.
        """
        return self.list_item_all_fields.share_link(
            link_kind=link_kind, expiration=expiration, role=role, password=password, share_id=share_id
        )

    def unshare_link(self, link_kind: int, share_id: Optional[str] = None) -> Self:
        """Removes the specified tokenized sharing link of the folder.

        Args:
            link_kind (int): This optional value specifies the globally unique identifier (GUID) of the tokenized
                sharing link that is intended to be removed.
            share_id (str or None): The kind of tokenized sharing link that is intended to be removed.
        """
        return self.list_item_all_fields.unshare_link(link_kind, share_id)  # type: ignore[returnType]

    def recycle(self, ignore_missing: bool = False) -> ClientResult[str]:
        """Moves the folder to the Recycle Bin and returns the identifier of the new Recycle Bin item.

        Args:
            ignore_missing (bool): When True, recycling a folder that no longer
                exists (HTTP 404) succeeds instead of raising.
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        return return_type

    def recycle_with_parameters(self, parameters: FolderDeleteParameters) -> ClientResult[str]:
        """Moves the list folder to the Recycle Bin and returns the identifier of the new Recycle Bin item

        Args:
            parameters (FolderDeleteParameters):
        """
        return_type = ClientResult(self.context, str())
        payload = {"parameters": parameters}
        qry = ServiceOperationQuery(self, "RecycleWithParameters", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_changes(self, query: Optional[ChangeQuery] = None) -> ChangeCollection:
        """Returns the collection of changes from the change log that have occurred within the folder,
        based on the specified query.

        Args:
            query (ChangeQuery): Specifies which changes to return
        """
        if query is None:
            query = ChangeQuery(Folder=True)
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_list_item_changes(self, query: ChangeQuery) -> ChangeCollection:
        """Gets the collection of all changes from the change log that have occurred within the scope of the SharePoint
        folder based on the specified query.

        Args:
            query (ChangeQuery): Specifies which changes to return
        """
        return_type = ChangeCollection(self.context)
        payload = {"query": query}
        qry = ServiceOperationQuery(self, "getListItemChanges", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add(self, name: str) -> Self:
        """Adds the folder that is located under a current folder"""
        return self.folders.add(name)  # type: ignore[returnType]

    def rename(self, name: str) -> Self:
        """Rename a Folder resource"""
        item = self.list_item_all_fields
        item.set_property("Title", name)
        item.set_property("FileLeafRef", name)
        qry = UpdateEntityQuery(item)
        self.context.add_query(qry)
        return self

    def upload_file(
        self,
        relative_path: str,
        content: Union[str, bytes],
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
        progress: Optional[ProgressCallback] = None,
    ) -> File:
        """Upload content to a path relative to this folder, creating folders as needed.

        A plain ``file_name`` (no slashes) uploads directly into this folder;
        a nested ``relative_path`` ensures the parent folders first. Content is
        uploaded with the size-dispatching :meth:`FileCollection.upload_content`
        (simple upload up to ``chunk_size``, resumable session above). The
        returned :class:`File` is deferred — the caller executes it.

        Args:
            relative_path (str): File name, or a path relative to this folder,
              e.g. ``"report.pdf"`` or ``"Projects/2026/report.pdf"``.
            content (str or bytes): Specifies the binary content of the file to be added.
            chunk_size (int): Upload-session chunk size / size threshold (bytes).
            progress: Optional hook invoked with a ``Progress`` snapshot
              (``done``/``total`` in bytes) while the file uploads.
        """
        if isinstance(content, str):
            content = content.encode("utf-8")
        parts = relative_path.split("/")
        folder = self
        if len(parts) > 1:
            folder = self.ensure_folder("/".join(parts[:-1]))
        return folder.files.upload_content(content, parts[-1], chunk_size, progress)

    def ensure_file(
        self,
        relative_path: str,
        content: Union[str, bytes] = b"",
        *,
        on_conflict: str = "skip",
        chunk_size: int = _DEFAULT_CHUNK_SIZE,
    ) -> File:
        """Ensure a file exists under this folder, uploading content when needed.

        The file counterpart of :meth:`ensure_folder`: missing parent folders are
        created (via :meth:`ensure_folder`), then the leaf file is resolved —
        reusing the existing file or uploading ``content`` when absent. Fully
        deferred; run the chain with ``execute_query()`` and the returned file
        addresses the target:

            >>> folder.ensure_file("2026/Q1/report.txt", "hello").execute_query()

        Args:
            relative_path (str): File name, or a path relative to this folder,
              e.g. ``"report.txt"`` or ``"2026/Q1/report.txt"``.
            content (str or bytes): File content; ``str`` is encoded as UTF-8.
            on_conflict (str): Behaviour when the file already exists. ``"skip"``
              (default) keeps it untouched, so a re-run is a no-op and
              ``content`` is never sent; ``"replace"`` overwrites it.
            chunk_size (int): Simple-upload threshold / session chunk size (bytes).

        Returns:
            File: The target file (existing or newly uploaded).
        """
        from office365.runtime.paths.v3.entity import EntityPath
        from office365.runtime.queries.get_or_create import get_or_create
        from office365.sharepoint.files.file import File

        if on_conflict not in ("skip", "replace"):
            raise ValueError(f"on_conflict must be 'skip' or 'replace', got {on_conflict!r}")
        parts = [part for part in relative_path.replace("\\", "/").split("/") if part]
        if not parts:
            raise ValueError("Path is empty")
        name = parts[-1]
        data = content.encode("utf-8") if isinstance(content, str) else content
        parent = self.ensure_folder("/".join(parts[:-1])) if len(parts) > 1 else self
        files = parent.files
        return_type = File(self.context, EntityPath(name, files.resource_path))

        def _create_query():
            if len(data) <= chunk_size:
                return files._build_upload_query(return_type, name, data, overwrite=True)
            return files._build_upload_session_query(return_type, name, io.BytesIO(data), len(data), chunk_size)

        if on_conflict == "replace":
            self.context.add_query(_create_query())
            return return_type
        get_or_create(
            find=return_type.get,
            create_query=_create_query,
            return_type=return_type,
            on_conflict="skip",
        )
        return return_type

    def write_dataframe(
        self,
        relative_path: str,
        df,
        *,
        format: str = "csv",  # noqa: A002
        index: bool = False,
        **opts,
    ) -> File:
        """Serialize a pandas DataFrame and write it as a file (CSV/XLSX/...).

        The DataFrame counterpart of :meth:`upload_file` — it writes the frame's
        **content**, not metadata. CSV is written UTF-8 with a BOM
        (``utf-8-sig``) so Excel opens it with the columns intact;
        ``format="xlsx"`` writes a worksheet (requires the ``[excel]`` extra).
        The returned :class:`File` is deferred — the caller executes it.

        Args:
            relative_path: File name or path relative to this folder.
            df: A pandas DataFrame.
            format: ``"csv"`` (default), ``"xlsx"``/``"excel"``, ``"json"``, ...
            index: Whether to write the DataFrame index (default False).
            opts: Extra kwargs forwarded to the pandas writer.
        """
        from office365.runtime.converters.dataframe import dataframe_to_bytes

        return self.upload_file(relative_path, dataframe_to_bytes(df, format, index, **opts))

    def read_dataframe(self, relative_path: str, *, format: str = "csv", **opts) -> "DataFrameResult":  # noqa: A002
        """Read a file in this folder's **content** into a DataFrame (deferred result).

        Parses the file content (CSV/XLSX/JSON/Parquet) — not metadata. Run with
        ``execute_query()`` and read ``.value``:

            >>> df = folder.read_dataframe("stocks.csv").execute_query().value
        """
        url = f"{self.server_relative_url}/{relative_path}".replace("//", "/")
        file = self.context.web.get_file_by_server_relative_url(url)
        return file.read_dataframe(format=format, **opts)

    def update_document_sharing_info(
        self,
        user_role_assignments: List[UserRoleAssignment],
        validate_existing_permissions: Optional[bool] = None,
        additive_mode: Optional[bool] = None,
        send_server_managed_notification: Optional[bool] = None,
        custom_message: Optional[str] = None,
        include_anonymous_links_in_notification: Optional[bool] = None,
        propagate_acl: Optional[bool] = None,
    ) -> ClientResult[ClientValueCollection[UserSharingResult]]:
        """This method allows a caller with the 'ManagePermission' permission to update sharing information about a
        document to enable document sharing with a set of users. It returns an array of
        UserSharingResult (section 3.2.5.190) elements where each element contains the sharing status for each user.

        Args:
            user_role_assignments (list[UserRoleAssignment]): An array of recipients and assigned roles on the securable
                object pointed to by the resourceAddress parameter.
            validate_existing_permissions (bool): A Boolean flag indicating how to honor a requested permission for a
                user.
                If this value is "true", the protocol server will not grant the
                requested permission if a user already has sufficient permissions, and
                if this value is "false", the protocol server will grant the requested
                permission whether or not a user already has the same or more
                permissions. This parameter is applicable only when the parameter additiveMode is set to true.
            additive_mode (bool): A Boolean flag indicating whether the permission setting uses the additive or strict
                mode.
                If this value is "true", the permission setting uses the additive mode, which means
                that the specified permission will be added to the user's current list of permissions
                if it is not there already, and if this value is "false", the permission setting uses
                the strict mode, which means that the specified permission will replace the user's current permissions.
            send_server_managed_notification (bool): A Boolean flag to indicate whether or not to generate an email
                notification to each recipient in the "userRoleAssignments" array
                after the document update is completed successfully.
                If this value is "true", the protocol server will send an email
                notification if an email server is configured, and if the value is
                "false", no email notification will be sent.
            custom_message (str): A custom message to be included in the email notification.
            include_anonymous_links_in_notification (bool): A Boolean flag that indicates whether or not to include
                anonymous access links in the email notification to each
                recipient in the userRoleAssignments array after the
                document update is completed successfully.
                If the value is "true", the protocol server will include an
                anonymous access link in the email notification, and if the value is "false", no link will be included.
            propagate_acl (bool): A flag to determine if permissions SHOULD be pushed to items with unique permission.
        """
        return_type = ClientResult(self.context, ClientValueCollection(UserSharingResult))

        def _update_document_sharing_info():
            resource_address = SPResPath.create_absolute(self.context.base_url, str(self.server_relative_path))
            DocumentSharingManager.update_document_sharing_info(
                self.context,
                str(resource_address),
                user_role_assignments,
                validate_existing_permissions,
                additive_mode,
                send_server_managed_notification,
                custom_message,
                include_anonymous_links_in_notification,
                propagate_acl,
                return_type,
            )

        self.ensure_property("ServerRelativePath").after_execute(lambda _: _update_document_sharing_info())
        return return_type

    def copy_to(
        self, destination: Union[str, Folder], keep_both: bool = False, reset_author_and_created: bool = False
    ) -> Folder:
        """Copies the folder with files to the destination URL.

        Args:
            destination (str or Folder): Parent folder object or server relative folder url
            keep_both (bool): bool
            reset_author_and_created (bool):
        """
        return_type = Folder(self.context)
        assert self.parent_collection is not None
        self.parent_collection.add_child(return_type)

        def _copy_to(destination_folder: Folder) -> None:
            destination_url = "/".join([x or "" for x in [destination_folder.server_relative_url, self.name]])
            return_type.set_property("ServerRelativeUrl", destination_url)
            opts = MoveCopyOptions(KeepBoth=keep_both, ResetAuthorAndCreatedOnCopy=reset_author_and_created)
            MoveCopyUtil.copy_folder(self.context, self.server_relative_url, destination_url, opts)

        def _source_folder_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativeUrl").after_execute(lambda _: _copy_to(dest))
            else:
                self.context.web.ensure_folder_path(destination).after_execute(_copy_to)

        self.ensure_properties(["ServerRelativeUrl", "Name"]).after_execute(lambda _: _source_folder_resolved())
        return return_type

    def copy_to_using_path(
        self, destination: Union[str, Folder], keep_both: bool = False, reset_author_and_created: bool = False
    ) -> Folder:
        """Copies the folder with files to the destination Path.

        Args:
            destination (str or Folder): Parent folder object or server relative folder url
            keep_both (bool):
            reset_author_and_created (bool):
        """
        return_type = Folder(self.context)
        assert self.parent_collection is not None
        self.parent_collection.add_child(return_type)

        def _copy_folder_by_path(destination_folder: Folder) -> None:
            destination_url = "/".join([x or "" for x in [str(destination_folder.server_relative_path), self.name]])
            return_type.set_property("ServerRelativePath", destination_url)
            opts = MoveCopyOptions(KeepBoth=keep_both, ResetAuthorAndCreatedOnCopy=reset_author_and_created)
            MoveCopyUtil.copy_folder_by_path(self.context, str(self.server_relative_path), destination_url, opts)

        def _source_folder_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativePath").after_execute(lambda _: _copy_folder_by_path(dest))
            else:
                self.context.web.ensure_folder_path(destination).get().select(["ServerRelativePath"]).after_execute(
                    _copy_folder_by_path
                )

        self.ensure_properties(["ServerRelativePath", "Name"]).after_execute(lambda _: _source_folder_resolved())
        return return_type

    @odata(name="StorageMetrics")
    @property
    def storage_metrics(self) -> StorageMetrics:
        """Specifies the storage-related metrics for list folders in the site"""
        return self.properties.get(
            "StorageMetrics", StorageMetrics(self.context, ResourcePath("StorageMetrics", self.resource_path))
        )

    @odata(name="ListItemAllFields")
    @property
    def list_item_all_fields(self) -> ListItem:
        """Specifies the list item fields values for the list item corresponding to the folder."""
        return self.properties.get(
            "ListItemAllFields", ListItem(self.context, ResourcePath("ListItemAllFields", self.resource_path))
        )

    @property
    def files(self) -> FileCollection:
        """Specifies the collection of files contained in the list folder.

        A single-shot load (``ctx.load(folder, ["Files"])`` / ``.get()``) is trimmed
        at the 5,000-item list view threshold; use :meth:`get_files` (paged) for
        folders that may exceed it.
        """
        from office365.sharepoint.files.collection import FileCollection

        return self.properties.get(
            "Files", FileCollection(self.context, ResourcePath("Files", self.resource_path), self)
        )

    @property
    def folders(self) -> FolderCollection:
        """Specifies the collection of list folders contained within the list folder.

        A single-shot load (``ctx.load(folder, ["Folders"])`` / ``.get()``) is
        trimmed at the 5,000-item list view threshold; use ``folders.get_all(
        page_size=2000)`` for folders that may exceed it.
        """
        from office365.sharepoint.folders.collection import FolderCollection

        return self.properties.get(
            "Folders", FolderCollection(self.context, ResourcePath("Folders", self.resource_path), self)
        )

    def ensure_folder(self, relative_path: str) -> Folder:
        """Ensure a nested folder tree exists under this folder.

        A folder-level mirror of :meth:`Web.ensure_folder_path` — creates any
        missing intermediate folders along a path relative to this folder
        (deferred; the caller executes the query).

        Args:
            relative_path (str): Path relative to this folder, e.g. ``"Projects/2026"``.
        """
        return self.folders.ensure_by_path(relative_path)

    def ensure_folders(self, relative_paths: Iterable[str]) -> list[Folder]:
        """Ensure a set of nested folder paths under this folder — deduplicated.

        Since :meth:`ensure_folder` already creates intermediate folders for a
        nested path, only the *deepest* paths are ensured: a path that is an
        ancestor of another is covered by it. All ensures are queued as one
        deferred batch; the caller executes them in a single round-trip.

        Args:
            relative_paths (Iterable[str]): Paths relative to this folder.

        Returns:
            list[Folder]: The ensured folders.
        """
        paths = sorted(set(relative_paths))
        deepest = [path for path in paths if not any(other.startswith(f"{path}/") for other in paths if other != path)]
        return [self.ensure_folder(path) for path in deepest]

    @odata(name="ParentFolder")
    @property
    def parent_folder(self) -> Folder:
        """Specifies the list folder."""
        return self.properties.get(
            "ParentFolder", Folder(self.context, ResourcePath("ParentFolder", self.resource_path))
        )

    @property
    def name(self) -> Optional[str]:
        """Specifies the list folder name."""
        return self.properties.get("Name", None)

    @property
    def is_wopi_enabled(self) -> Optional[bool]:
        """Indicates whether the folder is enabled for WOPI default action."""
        return self.properties.get("IsWOPIEnabled", None)

    @property
    def prog_id(self) -> Optional[str]:
        """Gets the identifier (ID) of the application in which the folder was created."""
        return self.properties.get("ProgID", None)

    @property
    def unique_id(self) -> Optional[str]:
        """Gets the unique ID of the folder."""
        return self.properties.get("UniqueId", None)

    @property
    def exists(self) -> Optional[bool]:
        """Gets a Boolean value that indicates whether the folder exists."""
        return self.properties.get("Exists", None)

    @property
    def welcome_page(self) -> Optional[str]:
        """Specifies the server-relative URL for the list folder Welcome page."""
        return self.properties.get("WelcomePage", None)

    @odata(name="UniqueContentTypeOrder")
    @property
    def unique_content_type_order(self) -> ContentTypeId:
        """Specifies the content type order for the list folder."""
        return self.properties.get("UniqueContentTypeOrder", ContentTypeId())

    @odata(name="ContentTypeOrder")
    @property
    def content_type_order(self) -> ContentTypeId:
        """Specifies the content type order for the list folder."""
        return self.properties.get("ContentTypeOrder", ContentTypeId())

    @odata(name="TimeLastModified")
    @property
    def time_last_modified(self) -> Optional[datetime]:
        """Gets the last time this folder or a direct child was modified in UTC."""
        return self.properties.get("TimeLastModified", datetime.min)

    @odata(name="TimeCreated")
    @property
    def time_created(self) -> Optional[datetime]:
        """Gets when the folder was created in UTC."""
        return self.properties.get("TimeCreated", datetime.min)

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the server-relative URL of the list folder."""
        return self.properties.get("ServerRelativeUrl", None)

    @odata(name="ServerRelativePath")
    @property
    def server_relative_path(self) -> Optional[SPResPath]:
        """Gets the server-relative Path of the list folder."""
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def property_ref_name(self) -> Optional[str]:  # type: ignore[override]
        return None

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)
        if name == "UniqueId":
            self._resource_path = self.context.web.get_folder_by_id(value).resource_path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = self.context.web.get_folder_by_server_relative_url(value).resource_path
            elif name == "ServerRelativePath":
                self._resource_path = self.context.web.get_folder_by_server_relative_path(value).resource_path
        return self

    @property
    def exists_allow_throw_for_policy_failures(self) -> Optional[bool]:
        """Gets the ExistsAllowThrowForPolicyFailures property"""
        return self.properties.get("ExistsAllowThrowForPolicyFailures", None)

    @property
    def exists_with_exception(self) -> Optional[bool]:
        """Gets the ExistsWithException property"""
        return self.properties.get("ExistsWithException", None)

    @property
    def item_count(self) -> Optional[int]:
        """Gets the ItemCount property"""
        return self.properties.get("ItemCount", None)

    def add_sub_folder(self, leaf_name: str) -> Self:
        """AddSubFolder operation.

        Args:
            leaf_name (str):
                leafName parameter
        """
        qry = ServiceOperationQuery(self, "AddSubFolder", None, {"leafName": leaf_name}, None, None)
        self.context.add_query(qry)
        return self

    def add_sub_folder_using_path(self, decoded_url: str) -> Self:
        """AddSubFolderUsingPath operation.

        Args:
            decoded_url (str):
                DecodedUrl parameter
        """
        qry = ServiceOperationQuery(self, "AddSubFolderUsingPath", None, {"DecodedUrl": decoded_url}, None, None)
        self.context.add_query(qry)
        return self

    def delete_with_parameters(self, parameters: FolderDeleteParameters) -> Self:
        """DeleteWithParameters operation.

        Args:
            parameters (FolderDeleteParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "DeleteWithParameters", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def start_delete(self) -> ClientResult[UUID]:
        """StartDelete operation."""
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "StartDelete", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type
