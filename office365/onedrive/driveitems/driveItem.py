from __future__ import annotations

import os
from datetime import datetime
from functools import partial
from io import IOBase
from os import PathLike
from os.path import isfile, join
from typing import IO, TYPE_CHECKING, AnyStr, AsyncIterator, Callable, Optional

import requests
from requests import Response
from typing_extensions import Self

from office365.delta_collection import DeltaCollection
from office365.delta_path import DeltaPath
from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.onedrive.analytics.item_analytics import ItemAnalytics
from office365.onedrive.base_item import BaseItem
from office365.onedrive.driveitems.audio import Audio
from office365.onedrive.driveitems.conflict_behavior import ConflictBehavior
from office365.onedrive.driveitems.copy_result import DriveItemCopyResult
from office365.onedrive.driveitems.geo_coordinates import GeoCoordinates
from office365.onedrive.driveitems.image import Image
from office365.onedrive.driveitems.item_preview_info import ItemPreviewInfo
from office365.onedrive.driveitems.photo import Photo
from office365.onedrive.driveitems.publication_facet import PublicationFacet
from office365.onedrive.driveitems.remote_item import RemoteItem
from office365.onedrive.driveitems.retention_label import ItemRetentionLabel
from office365.onedrive.driveitems.special_folder import SpecialFolder
from office365.onedrive.driveitems.thumbnail_set import ThumbnailSet
from office365.onedrive.driveitems.uploadable_properties import (
    DriveItemUploadableProperties,
)
from office365.onedrive.drives.recipient import DriveRecipient
from office365.onedrive.files.file import File
from office365.onedrive.files.system_info import FileSystemInfo
from office365.onedrive.folders.folder import Folder
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.internal.paths.url import UrlPath
from office365.onedrive.listitems.item_reference import ItemReference
from office365.onedrive.listitems.list_item import ListItem
from office365.onedrive.operations.pending import PendingOperations
from office365.onedrive.permissions.collection import PermissionCollection
from office365.onedrive.permissions.permission import Permission
from office365.onedrive.sensitivitylabels.assignment_method import (
    SensitivityLabelAssignmentMethod,
)
from office365.onedrive.sensitivitylabels.extract_result import (
    ExtractSensitivityLabelsResult,
)
from office365.onedrive.shares.shared import Shared
from office365.onedrive.versions.drive_item import DriveItemVersion
from office365.onedrive.workbooks.workbook import Workbook
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.v4.upload_session import UploadSession
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.runtime.operations import Progress, ProgressCallback, emit_progress
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.upload_session import UploadSessionQuery
from office365.runtime.transport.base import HeadersCallback
from office365.runtime.transport.offload import get_offload_executor, run_offloaded
from office365.runtime.types.odata_property import odata
from office365.subscriptions.collection import SubscriptionCollection

if TYPE_CHECKING:
    from office365.onedrive.driveitems.bundle import Bundle
    from office365.onedrive.driveitems.malware import Malware
    from office365.onedrive.driveitems.package import Package
    from office365.onedrive.driveitems.video import Video
    from office365.onedrive.root import Root
    from office365.search.search_result import SearchResult


class DriveItem(BaseItem):
    """The driveItem resource represents a file, folder, or other item stored in a drive. All file system objects in
    OneDrive and SharePoint are returned as driveItem resources"""

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Get metadata for a driveItem",
    )
    def get(self):
        """Retrieve drive item metadata"""
        return super().get()

    def assign_sensitivity_label(
        self,
        sensitivity_label_id: str,
        assignment_method: SensitivityLabelAssignmentMethod | None = None,
        justification_text: str | None = None,
    ):
        """Asynchronously assign a sensitivity label to a driveItem.

        Args:
            justification_text: Justification text for audit purposes, and is required when downgrading/removing a label.
            sensitivity_label_id: Required. ID of the sensitivity label to be assigned, or empty string to remove the
              sensitivity label.
            assignment_method: The assignment method of the label on the document. Indicates whether the assignment
              of the label was done automatically, standard, or as a privileged operation (the equivalent of an
              administrator operation).
        """
        payload = {
            "sensitivityLabelId": sensitivity_label_id,
            "assignmentMethod": assignment_method,
            "justificationText": justification_text,
        }
        qry = ServiceOperationQuery[DriveItem](self, "assignSensitivityLabel", None, payload, None)
        self.context.add_query(qry)
        return self

    def set_retention_label(self, name: str):
        """Apply (set) a retention label on a driveItem (files and folders). Retention labels
        don't need to be published in a retention label policy to be applied using this method.
        """
        self.retention_label.name = name
        self.retention_label.update()
        return self

    def get_files(
        self,
        recursive: bool = False,
        page_size: int | None = None,
        progress: Optional[Callable[[Progress[DriveItem]], None]] = None,
    ) -> EntityCollection[DriveItem]:
        """Retrieves files

        Args:
            recursive (bool): Determines whether to enumerate folders recursively
            page_size (int): Page size
            progress: Optional hook invoked per page with a ``Progress[DriveItem]``
              snapshot (``done`` = files discovered so far; ``items`` = the page's items).

        The fluent ``.select([...])`` / ``.expand([...])`` applied to the returned
        collection is honored on every ``children`` page the scan loads.
        """
        from office365.onedrive.driveitems.collection import DriveItemCollection
        from office365.runtime.queries.deferred import DeferredOperationQuery

        return_type = DriveItemCollection(self.context, self.resource_path)

        def _get_files(parent_drive_item: DriveItem) -> None:
            def _after_loaded(col: EntityCollection[DriveItem]) -> None:
                if col.has_next:
                    return

                for drive_item in col:
                    if drive_item.is_folder:
                        if recursive and drive_item.folder.childCount is not None and drive_item.folder.childCount > 0:
                            _get_files(drive_item)
                    else:
                        return_type.add_child(drive_item)
                if callable(progress):
                    progress(Progress(done=len(return_type), stage="scanning", items=list(col)))

            children = parent_drive_item.children
            return_type.query_options.apply_to(children)
            if return_type.query_options.select:
                fields = sorted({"folder", "id"} | set(return_type.query_options.select))
                children.select(fields)
            children.get_all(page_size=page_size, page_loaded=_after_loaded)

        placeholder = DeferredOperationQuery(self.context)
        self.context.add_query(placeholder).after_execute(lambda _: _get_files(self))
        return return_type

    def get_folders(
        self,
        recursive: bool = False,
        page_size: int | None = None,
        progress: Optional[Callable[[Progress[DriveItem]], None]] = None,
    ) -> EntityCollection[DriveItem]:
        """Retrieves folders

        Args:
            recursive (bool): Determines whether to enumerate folders recursively
            page_size (int): Page size
            progress: Optional hook invoked per page with a ``Progress[DriveItem]``
              snapshot (``done`` = folders discovered so far; ``items`` = the page's items).

        The fluent ``.select([...])`` / ``.expand([...])`` applied to the returned
        collection is honored on every ``children`` page the scan loads.
        """
        from office365.onedrive.driveitems.collection import DriveItemCollection
        from office365.runtime.queries.deferred import DeferredOperationQuery

        return_type = DriveItemCollection(self.context, self.resource_path)

        def _get_folders(parent: DriveItem) -> None:
            def _after_loaded(col: EntityCollection[DriveItem]) -> None:
                if col.has_next:
                    return

                for drive_item in col:
                    if recursive and drive_item.folder.childCount is not None and drive_item.folder.childCount > 0:
                        _get_folders(drive_item)
                    return_type.add_child(drive_item)
                if callable(progress):
                    progress(Progress(done=len(return_type), stage="scanning", items=list(col)))

            children = parent.children.filter("folder ne null")
            return_type.query_options.apply_to(children)
            if return_type.query_options.select:
                fields = sorted({"folder", "id"} | set(return_type.query_options.select))
                children.select(fields)
            children.get_all(page_size=page_size, page_loaded=_after_loaded)

        placeholder = DeferredOperationQuery(self.context)
        self.context.add_query(placeholder).after_execute(lambda _: _get_folders(self))
        return return_type

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Get a driveItem by its server-relative path",
    )
    def get_by_path(self, url_path: str) -> DriveItem:
        """Retrieve DriveItem by server relative path"""
        return DriveItem(self.context, UrlPath(url_path, self.resource_path), self.children)

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Ensure a nested folder exists in a drive",
    )
    def ensure_folder(self, url_path: str) -> DriveItem:
        """Ensure a folder exists at the given path, creating missing levels.

        Walks the path segment by segment (e.g. ``"2024/Q1/Reports"``) and, per
        level, reuses the existing folder when present or creates it otherwise.
        Fully deferred — run the chain with ``execute_query()`` and the returned
        item addresses the target folder:

            >>> folder = drive_item.ensure_folder("2024/Q1/Reports").execute_query()

        Args:
            url_path (str): Path to the folder, relative to this item.

        Returns:
            DriveItem: The target folder (existing or newly created).
        """
        names = self._split_path(url_path)
        if not names:
            raise ValueError("Path is empty")
        return_type = DriveItem(self.context)

        def _on_resolved(folder: DriveItem) -> None:
            return_type._resource_path = folder._resource_path
            return_type.copy_from(folder)

        self._resolve_path(names, _on_resolved)
        return return_type

    @staticmethod
    def _split_path(path: str) -> list[str]:
        """Split a (server-relative) path into non-empty segments."""
        return [name for name in path.replace("\\", "/").split("/") if name]

    def _resolve_path(self, names: list[str], on_resolved: Callable[[DriveItem], None]) -> None:
        """Walk and create the folders in ``names``, then call ``on_resolved`` with the resolved folder.

        Each level is resolved with a children lookup
        (``.../children?$filter=name eq '...'``) rather than path-based addressing,
        because Graph supports ``root:/path:/`` addressing but *not*
        ``items/{id}:/path:/`` for a read. Creation goes through the parent's
        ``children`` collection, so the walk works both from the drive root and
        from a folder addressed by id. The callback receives the resolved folder
        (existing or created); with no names it runs synchronously against
        ``self``.

        Args:
            names (list[str]): Folder names, relative to this item.
            on_resolved (Callable[[DriveItem], None]): Invoked with the resolved folder.
        """

        def _walk(parent: DriveItem, idx: int) -> None:
            if idx == len(names):
                on_resolved(parent)
                return

            name = names[idx]
            escaped = name.replace("'", "''")
            existing = parent.children.first_or_none(f"name eq '{escaped}'")

            def _on_checked(_) -> None:
                if existing.is_loaded:
                    _walk(existing, idx + 1)
                else:
                    created = parent.create_folder(name)
                    created.after_execute(lambda _: _walk(created, idx + 1))

            parent.children.after_execute(_on_checked)

        _walk(self, 0)

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Ensure a file exists in a drive, uploading its content when missing",
    )
    def ensure_file(self, relative_path: str, content: bytes | str = b"", *, on_conflict: str = "skip") -> DriveItem:
        """Ensure a file exists at the given path, uploading content when needed.

        The file counterpart of :meth:`ensure_folder`: missing parent folders are
        created (via :meth:`ensure_folder`), then the leaf file is resolved —
        reusing the existing file or uploading ``content`` when absent. Fully
        deferred — run the chain with ``execute_query()`` and the returned item
        addresses the target file:

            >>> file = drive_item.ensure_file("2024/Q1/placeholder.txt").execute_query()

        Args:
            relative_path (str): File name or path relative to this item, e.g.
                ``"report.txt"`` or ``"2024/Q1/report.txt"``.
            content (bytes or str): File content; ``str`` is encoded as UTF-8.
            on_conflict (str): Behaviour when the file already exists.
                ``"skip"`` (default) leaves it untouched, so a re-run is a no-op
                and ``content`` is never sent; ``"replace"`` overwrites it with
                ``content`` in a single request.

        Returns:
            DriveItem: The target file (existing or newly uploaded).
        """
        if on_conflict not in ("skip", "replace"):
            raise ValueError(f"on_conflict must be 'skip' or 'replace', got {on_conflict!r}")
        names = self._split_path(relative_path)
        if not names:
            raise ValueError("Path is empty")
        name = names[-1]
        data = content.encode("utf-8") if isinstance(content, str) else content
        return_type = DriveItem(self.context)

        def _on_resolved(parent_item: DriveItem) -> None:
            # ``items/{parent-id}:/{name}:/content`` is a valid *upload* target, so
            # the path-addressed item is fine for the PUT; only the existence read
            # must avoid ``:/`` (see ``_resolve_path``) and go through ``children``.
            return_type._resource_path = parent_item.get_by_path(name)._resource_path
            if on_conflict == "replace":
                parent_item.context.add_query(parent_item._build_upload_query(return_type, data))
                return

            escaped = name.replace("'", "''")
            existing = parent_item.children.first_or_none(f"name eq '{escaped}'")

            def _on_checked(_) -> None:
                if existing.is_loaded:
                    return_type.copy_from(existing)
                else:
                    parent_item.context.add_query(parent_item._build_upload_query(return_type, data))

            parent_item.children.after_execute(_on_checked)

        self._resolve_path(names[:-1], _on_resolved)
        return return_type

    def create_powerpoint(self, name: str) -> DriveItem:
        """Creates a PowerPoint file

        Args:
            name (str): File name
        """
        return self.upload(name, None)

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Create a sharing link for a driveItem",
    )
    def create_link(
        self,
        link_type: str,
        scope: str | None = None,
        expiration_datetime: datetime | None = None,
        password: str | None = None,
        message: str | None = None,
        retain_inherited_permissions: bool | None = None,
    ) -> Permission:
        """The createLink action will create a new sharing link if the specified link type doesn't already exist
        for the calling application. If a sharing link of the specified type already exists for the app,
        the existing sharing link will be returned.

        Args:
            link_type (str): The type of sharing link to create. Either view, edit, or embed.
            scope (str): The scope of link to create. Either anonymous or organization.
            expiration_datetime (str or datetime.datetime): A String with format of yyyy-MM-ddTHH:mm:ssZ of DateTime
              indicate the expiration time of the permission.
            password (str): The password of the sharing link that is set by the creator. Optional and OneDrive
              Personal only.
            message (str):
            retain_inherited_permissions (bool): Optional. If true (default), any existing inherited permissions
              are retained on the shared item when sharing this item for the first time. If false, all existing
              permissions are removed when sharing for the first time.
        """
        payload = {
            "type": link_type,
            "scope": scope or "",
            "message": message,
            "expirationDateTime": expiration_datetime,
            "password": password,
            "retainInheritedPermissions": retain_inherited_permissions,
        }
        return_type = Permission(self.context)
        self.permissions.add_child(return_type)
        qry = ServiceOperationQuery(self, "createLink", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Discard check out of a driveItem",
    )
    def discard_checkout(self) -> Self:
        """Discard the check out of a driveItem. This action releases a driveItem resource that was previously
        checked out. Any changes made to the item while it was checked out are discarded.

        The same user that performed the checkout must discard it. Another alternative is to use application permissions
        """
        qry = ServiceOperationQuery[DriveItem](self, "discardCheckout")
        self.context.add_query(qry)
        return self

    def delete_object(self, bypass_shared_lock: bool = False, *, ignore_missing: bool = False) -> Self:
        """Deletes the driveItem.

        Args:
            bypass_shared_lock: Send ``Prefer: bypass-shared-lock`` so the delete
                succeeds even when the item is open for editing. Without it the
                server rejects the request with
                :class:`~office365.runtime.exceptions.FileLockedException` (HTTP 423).
            ignore_missing: When ``True``, deleting an item that no longer exists
                (HTTP 404) succeeds instead of raising.
        """
        super().delete_object(ignore_missing=ignore_missing)
        if bypass_shared_lock:
            from office365.runtime.http.prefer import prefer_bypass_shared_lock

            self.context.before_execute(prefer_bypass_shared_lock, once=True)
        return self

    def extract_sensitivity_labels(
        self,
    ) -> ClientResult[ExtractSensitivityLabelsResult]:
        """
        Extract one or more sensitivity labels assigned to a drive item and update the metadata of a drive
        item with the latest details of the assigned label. In case of failure to extract the sensitivity labels
        of a file, an extraction error will be thrown with the applicable error code and message.
        """
        return_type = ClientResult(self.context, ExtractSensitivityLabelsResult())
        qry = ServiceOperationQuery(self, "extractSensitivityLabels", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Follow a driveItem",
    )
    def follow(self) -> Self:
        """Follow a driveItem."""
        qry = ServiceOperationQuery[DriveItem](self, "follow")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Unfollow a driveItem",
    )
    def unfollow(self) -> Self:
        """Unfollow a driveItem."""
        qry = ServiceOperationQuery[DriveItem](self, "unfollow")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Check out a driveItem to prevent edits by others",
    )
    def checkout(self) -> Self:
        """
        Check out a driveItem resource to prevent others from editing the document, and prevent your changes
        from being visible until the documented is checked in.
        """
        qry = ServiceOperationQuery[DriveItem](self, "checkout")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Check in a checked-out driveItem",
    )
    def checkin(self, comment: str, checkin_as: str | None = None) -> Self:
        """Check in a checked out driveItem resource, which makes the version of the document available to others.

        Args:
            comment (str): comment to the new version of the file
            checkin_as (str): The status of the document after the check-in operation is complete. Can be published or
              unspecified.
        """
        qry = ServiceOperationQuery[DriveItem](
            self, "checkin", None, {"comment": comment, "checkInAs": checkin_as or ""}
        )
        self.context.add_query(qry)
        return self

    def resumable_upload(
        self,
        source_path: str,
        chunk_size: int = 2000000,
        chunk_uploaded: Callable[[int], None] | None = None,
    ) -> DriveItem:
        """Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        To upload a file using an upload session, there are two steps:
        Create an upload session
        Upload bytes to the upload session

        Args:
            chunk_uploaded:
            source_path (str): File path
            chunk_size (int): chunk size
        """

        def _start_upload(result: Response) -> None:
            with open(source_path, "rb") as local_file:
                session_request = UploadSessionRequest(local_file, chunk_size, chunk_uploaded)
                session_request.execute_query(qry)

        file_name = os.path.basename(source_path)
        return_type = DriveItem(self.context, UrlPath(file_name, self.resource_path))

        qry = UploadSessionQuery(return_type, {"item": DriveItemUploadableProperties(name=file_name)})
        self.context.add_query(qry).after_execute(_start_upload)
        return return_type

    async def resumable_upload_async(
        self,
        source_path: str,
        chunk_size: int = 2000000,
        chunk_uploaded: Callable[[int], None] | None = None,
        progress: ProgressCallback | None = None,
    ) -> DriveItem:
        """Create an upload session and upload a large file without blocking the loop.

        Async twin of :meth:`resumable_upload` that is an awaitable coroutine: it
        creates the upload session and sends every chunk before it returns,
        instead of deferring the work to the next context execution.

        Each chunk is read from disk on the shared offload executor and PUT
        through the context's async transport (native with ``httpx``, otherwise a
        worker thread), so a multi-gigabyte upload keeps the event loop free.
        Chunks are uploaded sequentially, as the service requires.

        Args:
            source_path (str): Local file path to upload.
            chunk_size (int): Number of bytes per chunk. Graph requires a
                multiple of 320 KiB, which the default (2 MB) satisfies.
            chunk_uploaded: Optional ``(bytes_uploaded) -> None`` callback invoked
                after each accepted chunk.
            progress: Optional ``ProgressCallback`` invoked per chunk with a
                ``Progress`` snapshot (``done`` = bytes uploaded, ``total`` =
                file size).

        Returns:
            DriveItem: The uploaded item.
        """
        file_name = os.path.basename(source_path)
        return_type = DriveItem(self.context, UrlPath(file_name, self.resource_path))

        qry = UploadSessionQuery(return_type, {"item": DriveItemUploadableProperties(name=file_name)})
        self.context.add_query(qry)
        await self.context.execute_query_async()

        pending = self.context.pending_request()
        executor = get_offload_executor()
        file_size = await run_offloaded(os.path.getsize, source_path, executor=executor)

        def _on_chunk(uploaded: int) -> None:
            if callable(chunk_uploaded):
                chunk_uploaded(uploaded)
            emit_progress(progress, done=uploaded, total=file_size, stage="uploading")

        local_file: IO = await run_offloaded(open, source_path, "rb", executor=executor)
        try:
            session_request = UploadSessionRequest(local_file, chunk_size, _on_chunk)
            session_request.with_async_transport(pending.async_transport)
            try:
                await session_request.execute_query_async(qry)
            except ClientRequestException as e:
                if pending.onError:
                    pending.onError(e)
                    return return_type
                raise
        finally:
            local_file.close()
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Create an upload session for large file uploads",
    )
    def create_upload_session(self, item: DriveItemUploadableProperties) -> ClientResult[UploadSession]:
        """Creates a temporary storage location where the bytes of the file will be saved until the complete file is
        uploaded.
        """
        qry = UploadSessionQuery(self, {"item": item})
        self.context.add_query(qry)
        return qry.return_type

    def _build_upload_query(self, item: DriveItem, content: bytes | None) -> ServiceOperationQuery[DriveItem]:
        """Build (but do not queue) the ``PUT .../content`` query for ``item``.

        Shared by :meth:`upload` and :meth:`ensure_file` — the latter only queues
        it when the leaf file is missing.

        Args:
            item (DriveItem): The file that receives the content.
            content (bytes or None): The binary content to upload.
        """
        qry = ServiceOperationQuery(item, "content", None, content, None, item)

        def _modify_query(request: RequestOptions) -> None:
            request.method = HttpMethod.Put

        qry.before_execute(_modify_query)
        return qry

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Upload file content (up to 4MB)",
    )
    def upload(self, name: str, content: bytes | None = None) -> DriveItem:
        """Upload file content. Supports files up to 4MB."""

        return_type = DriveItem(self.context, UrlPath(name, self.resource_path))
        self.children.add_child(return_type)
        self.context.add_query(self._build_upload_query(return_type, content))
        return return_type

    def upload_file(self, path_or_file: str | PathLike | IOBase) -> DriveItem:
        """Uploads a file."""
        if isinstance(path_or_file, IOBase):
            return self.upload(os.path.basename(getattr(path_or_file, "name", "")), path_or_file.read())

        file_size = os.path.getsize(path_or_file)
        if file_size >= 4 * 1024 * 1024:
            return self.resumable_upload(str(path_or_file))

        with open(path_or_file, "rb") as f:
            return self.upload(os.path.basename(str(path_or_file)), f.read())

    def upload_folder(self, path: str, file_uploaded: Callable[["DriveItem"], None] | None = None) -> DriveItem:
        """Uploads a folder"""

        def _after_file_upload(return_type: DriveItem) -> None:
            if callable(file_uploaded):
                file_uploaded(return_type)

        def _upload_folder(source_path: str, target_folder: "DriveItem") -> None:
            for name in os.listdir(source_path):
                cur_path = join(source_path, name)
                if isfile(cur_path):
                    with open(cur_path, "rb") as f:
                        target_folder.upload_file(f).after_execute(_after_file_upload)
                else:
                    target_folder.create_folder(name).after_execute(partial(_upload_folder, cur_path))

        _upload_folder(path, self)
        return self

    def get_content(self, format_name: str | None = None) -> ClientResult[AnyStr]:
        """Download the contents of the primary stream (file) of a DriveItem.
        Only driveItems with the file property can be downloaded.

        Args:
            format_name (str or None):
        """
        return_type = ClientResult[AnyStr](self.context)
        action_name = "content"
        if format_name is not None:
            action_name = action_name + rf"?format={format_name}"
        qry = FunctionQuery(self, action_name, None, return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    async def get_content_stream_async(
        self,
        chunk_size: int = 1024 * 1024,
        format_name: str | None = None,
        on_headers: HeadersCallback | None = None,
    ) -> AsyncIterator[bytes]:
        """Yield the file body in chunks without buffering it in memory.

        The streaming primitive behind :meth:`download_session_async`: it sends
        the same ``/content`` request (auth, pacing and the configured async
        transport all apply) and yields the body as it arrives, so the bytes can
        be piped straight to another destination — a socket, an upload, a hash —
        without opening a local file or materialising the whole content::

            async for chunk in item.get_content_stream_async():
                await sink.send(chunk)

        Args:
            chunk_size: Number of bytes per yielded chunk.
            format_name: Optional conversion format (e.g. ``"pdf"``) requested via
                the ``/content?format=`` endpoint.
            on_headers: Optional callback invoked once with the response headers
                before the first chunk (e.g. to read ``Content-Length``).

        Yields:
            Successive slices of the file body.

        Raises:
            ClientRequestException: When the service returns an error status.
        """
        pending = self.context.pending_request()
        action_name = "content" if format_name is None else f"content?format={format_name}"
        qry = FunctionQuery(self, action_name, None, None, return_raw_content=True)
        request = pending.build_request(qry)
        request.stream = True
        request.method = HttpMethod.Get
        await pending.before_execute_async(request)
        stream = pending.async_transport.stream_async(request, chunk_size=chunk_size, on_headers=on_headers)
        try:
            async for chunk in stream:
                yield chunk
        except requests.HTTPError as e:
            raise ClientRequestException.from_response(e.response) from e
        finally:
            # Close the response when the consumer stops early (break/cancel).
            aclose = getattr(stream, "aclose", None)
            if aclose is not None:
                await aclose()

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Download the contents of a driveItem",
    )
    def download(self, file_object: IO) -> Self:
        """
        Download the contents of the primary stream (file) of a DriveItem. Only driveItems with the file property
        can be downloaded
        """

        def _save_content(return_type: ClientResult[AnyStr]) -> None:
            file_object.write(return_type.value)

        self.get_content().after_execute(_save_content)
        return self

    def download_folder(
        self,
        download_file: IO,
        after_file_downloaded: Callable[[DriveItem], None] | None = None,
        recursive: bool = True,
    ) -> DriveItem:
        """
        Download the folder content
        """
        import zipfile

        def _after_file_downloaded(drive_item: DriveItem, base_path: str | None, result: ClientResult[AnyStr]) -> None:
            with zipfile.ZipFile(download_file.name, "a", zipfile.ZIP_DEFLATED) as zf:
                zip_path = "/".join(filter(None, (base_path, drive_item.name)))
                zf.writestr(zip_path, result.value)
                if callable(after_file_downloaded):
                    after_file_downloaded(drive_item)

        def _after_folder_downloaded(children, base_path: str | None = None) -> None:
            for drive_item in children:
                if drive_item.is_file:
                    drive_item.get_content().after_execute(partial(_after_file_downloaded, drive_item, base_path))
                elif recursive:
                    next_base_path = "/".join(filter(None, (base_path, drive_item.name)))
                    _download_folder(drive_item, next_base_path)

        def _download_folder(drive_item: "DriveItem", base_path: str | None = None) -> None:
            children = drive_item.children
            processed = {"count": 0}

            def _page_loaded(col) -> None:
                # pages arrive incrementally — process only the new items
                new_items = list(col)[processed["count"] :]
                processed["count"] = len(col)
                _after_folder_downloaded(new_items, base_path)

            children.get_all(page_loaded=_page_loaded)

        _download_folder(self)
        return self

    def download_session(
        self,
        file_object: IO,
        chunk_downloaded: Callable[[int], None] | None = None,
        chunk_size: int | None = 1024 * 1024,
    ) -> Self:
        """By default, file gets downloaded immediately.
        For a large files reading the whole content of a file at once into memory should be avoided.

        This method allows to stream content into the file

        Args:
            file_object (typing.IO):
            chunk_downloaded ((int)->None or None): A callback
            chunk_size (int): The number of bytes it should read into memory.
        """

        def _construct_request(request: RequestOptions) -> None:
            request.stream = True

        def _process_response(response: requests.Response) -> None:
            bytes_read = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                bytes_read += len(chunk)
                if callable(chunk_downloaded):
                    chunk_downloaded(bytes_read)
                file_object.write(chunk)

        self.get_content().before_execute(_construct_request).after_execute(_process_response, include_response=True)
        return self

    async def download_session_async(
        self,
        file_object: IO,
        chunk_downloaded: Callable[[int], None] | None = None,
        chunk_size: int = 1024 * 1024,
        progress: ProgressCallback | None = None,
    ) -> Self:
        """Async twin of :meth:`download_session` that never blocks the loop.

        Streams a large file into ``file_object`` through the configured async
        transport — native when one is set (e.g.
        :class:`~office365.runtime.transport.httpx_transport.HttpxTransport`),
        otherwise a worker thread — so the event loop stays free while the body
        is transferred and the content is never buffered in memory.

        Unlike the deferred :meth:`download_session`, this is an awaitable
        coroutine: it sends the request and writes every chunk before it returns.

        Args:
            file_object: An open binary file object to write into.
            chunk_downloaded: Optional ``(bytes_so_far) -> None`` callback invoked
                after each chunk.
            chunk_size: Number of bytes per chunk.
            progress: Optional ``ProgressCallback`` invoked per chunk with a
                ``Progress`` snapshot (``done`` = bytes downloaded so far,
                ``total`` = content length when known).

        Returns:
            Self for method chaining.
        """
        pending = self.context.pending_request()
        qry = FunctionQuery(self, "content", None, None, return_raw_content=True)
        request = pending.build_request(qry)
        request.stream = True
        request.method = HttpMethod.Get
        await pending.before_execute_async(request)

        if file_object.seekable():
            file_object.seek(0)
            file_object.truncate()

        total: list[int | None] = [None]

        def _capture_length(headers) -> None:
            length = headers.get("Content-Length")
            total[0] = int(length) if length else None

        bytes_read = 0
        try:
            async for chunk in pending.async_transport.stream_async(
                request, chunk_size=chunk_size, on_headers=_capture_length
            ):
                bytes_read += len(chunk)
                if callable(chunk_downloaded):
                    chunk_downloaded(bytes_read)
                emit_progress(progress, done=bytes_read, total=total[0], stage="downloading")
                file_object.write(chunk)
        except requests.HTTPError as e:
            error = ClientRequestException.from_response(e.response)
            if pending.onError:
                pending.onError(error)
                return self
            raise error from e
        return self

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Create a new folder in a drive",
    )
    def create_folder(
        self,
        name: str,
        conflict_behavior: ConflictBehavior = ConflictBehavior.Rename,
    ) -> DriveItem:
        """Create a new folder or DriveItem in a Drive with a specified parent item or path.

        Args:
            name (str): Folder name
            conflict_behavior (str): query parameter to customize the behavior when a conflict occurs.
        """
        return_type = DriveItem(self.context)
        self.children.add_child(return_type)
        payload = {
            "name": name,
            "folder": {},
            "@microsoft.graph.conflictBehavior": conflict_behavior.value,
        }
        qry = CreateEntityQuery(self.children, payload, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Convert file content to a different format",
    )
    def convert(self, format_name: str) -> ClientResult[AnyStr]:
        """Converts the contents of an item in a specific format

        Args:
            format_name (str): Specify the format the item's content should be downloaded as.
        """
        return self.get_content(format_name)

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Copy a driveItem to a new parent or name",
    )
    def copy(
        self,
        name: str | None = None,
        parent: ItemReference | DriveItem | None = None,
        conflict_behavior: ConflictBehavior = ConflictBehavior.Fail,
    ) -> DriveItemCopyResult:
        """Asynchronously creates a copy of an driveItem (including any children), under a new parent item or with a
        new name.

        Microsoft Graph accepts this action with ``202 Accepted`` and returns the
        URL of an operation-status (monitor) resource. The returned
        :class:`~office365.onedrive.driveitems.copy_result.DriveItemCopyResult`
        exposes it as ``monitor_url``; use ``wait_for_item()`` /
        ``wait_for_item_async()`` to poll to completion and get the new item.

        Args:
            name (str or None): The new name for the copy. If this isn't provided, the same name will be used as the
              original.
            parent (office365.onedrive.listitems.item_reference.ItemReference or DriveItem or None): Reference
              to the parent item the copy will be created in.
            conflict_behavior (str): query parameter to customize the behavior when a conflict occurs.
              Returns location for details about how to monitor the progress of the copy, upon accepting the request.

        Returns:
            The monitor result; call ``execute_query()`` to start the copy, then
            ``wait_for_item()`` / ``wait_for_item_async()`` for the new item.
        """
        return_type = DriveItemCopyResult(self.context, self)

        def _copy(parent_reference: ItemReference) -> None:
            return_type.destination_drive_id = parent_reference.driveId

            def _create_request(request: RequestOptions) -> None:
                request.url += f"?@microsoft.graph.conflictBehavior={conflict_behavior.value}"

            def _process_response(resp: requests.Response) -> None:
                location = resp.headers.get("Location", None)
                if location is None:
                    return
                return_type.set_property("__value", location)

            payload = {"name": name, "parentReference": parent_reference}
            qry = ServiceOperationQuery(self, "copy", None, payload, None, return_type)
            self.context.add_query(qry).before_execute(_create_request).after_execute(
                _process_response, include_response=True
            )

        if isinstance(parent, DriveItem):

            def _drive_item_loaded():
                parent_reference = ItemReference(driveId=parent.parent_reference.driveId, id=parent.id)
                _copy(parent_reference)

            parent.ensure_property("parentReference").after_execute(lambda _: _drive_item_loaded())
        elif parent is not None:
            _copy(parent)
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Move a driveItem to a new parent",
    )
    def move(
        self,
        name: str | None = None,
        parent: ItemReference | DriveItem | None = None,
        conflict_behavior: ConflictBehavior = ConflictBehavior.Fail,
    ) -> DriveItem:
        """To move a DriveItem to a new parent item, your app requests to update the parentReference of the DriveItem
        to move.

        Args:
            name (str): The new name for the move. If this isn't provided, the same name will be used as the original.
            parent (ItemReference or DriveItem or None): Reference to the parent item the move will be created in.
            conflict_behavior (str): query parameter to customize the behavior when a conflict occurs.
        """

        return_type = DriveItem(self.context)
        self.children.add_child(return_type)

        def _move(parent_reference: ItemReference) -> None:
            payload = {"name": name, "parentReference": parent_reference}

            def _construct_request(request: RequestOptions) -> None:
                request.method = HttpMethod.Patch
                request.url += f"?@microsoft.graph.conflictBehavior={conflict_behavior.value}"

            qry = ServiceOperationQuery(self, "", None, payload, None, return_type)
            self.context.add_query(qry).before_execute(_construct_request)

        if isinstance(parent, DriveItem):

            def _drive_item_loaded():
                _move(ItemReference(id=parent.id))

            parent.ensure_property("parentReference").after_execute(lambda _: _drive_item_loaded())
        elif parent is not None:
            _move(parent)
        return return_type

    def rename(self, new_name: str) -> DriveItem:
        """Rename a DriveItem

        Args:
            new_name (str): The new name for the rename.
        """
        return self.move(name=new_name)

    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Search the hierarchy of items for items matching a query",
    )
    def search(self, query_text: str) -> EntityCollection["DriveItem"]:
        """Search the hierarchy of items for items matching a query. You can search within a folder hierarchy,
        a whole drive, or files shared with the current user.

        Args:
            query_text (str):
        """
        from office365.onedrive.driveitems.collection import DriveItemCollection

        return_type = DriveItemCollection(self.context, ResourcePath("items", self.resource_path))
        qry = FunctionQuery(self, "search", {"q": query_text}, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Send a sharing invitation for a driveItem",
    )
    def invite(
        self,
        recipients: list[str],
        message: str,
        require_sign_in: bool = True,
        send_invitation: bool = True,
        roles: list[str] | None = None,
        expiration_datetime: datetime | None = None,
        password: str | None = None,
        retain_inherited_permissions: bool | None = None,
    ) -> EntityCollection[Permission]:
        """Sends a sharing invitation for a driveItem.
        A sharing invitation provides permissions to the recipients and optionally
        sends them an email with a sharing link.

        Args:
            recipients (list[str]): A list of recipients for the invitation.
            message (str): A plain text formatted message that is included in the invitation.
            require_sign_in (bool): Specifies whether the recipient of the invitation is required to sign in.
            send_invitation (bool): Specifies whether an email is sent to the recipient of the invitation.
            roles (list[str]): Specify the roles that are granted to the recipients of the sharing invitation.
            expiration_datetime (datetime.datetime): The dateTime after which the permission expires.
            password (str): Password set on the invite by the creator (OneDrive Personal only).
            retain_inherited_permissions (bool): If true, existing inherited permissions are retained.
        """
        if roles is None:
            roles = ["read"]
        return_type = PermissionCollection(self.context)
        payload = {
            "requireSignIn": require_sign_in,
            "sendInvitation": send_invitation,
            "roles": roles,
            "recipients": ClientValueCollection(DriveRecipient, [DriveRecipient.from_email(r) for r in recipients]),
            "message": message,
            "expirationDateTime": (expiration_datetime.isoformat() + "Z" if expiration_datetime else None),
            "password": password,
            "retainInheritedPermissions": retain_inherited_permissions,
        }
        qry = ServiceOperationQuery(self, "invite", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_activities_by_interval(
        self,
        start_dt: datetime | None = None,
        end_dt: datetime | None = None,
        interval: str | None = None,
    ) -> EntityCollection[ItemActivityStat]:
        """Get a collection of itemActivityStats resources for the activities that took place on this resource
        within the specified time interval.

        Args:
            start_dt (datetime.datetime): The start time over which to aggregate activities.
            end_dt (datetime.datetime): The end time over which to aggregate activities.
            interval (str): The aggregation interval.
        """
        return_type = EntityCollection(self.context, ItemActivityStat, self.resource_path)

        params = {
            "startDateTime": start_dt.strftime("%m-%d-%Y") if start_dt else None,
            "endDateTime": end_dt.strftime("%m-%d-%Y") if end_dt else None,
            "interval": interval,
        }

        qry = FunctionQuery(self, "getActivitiesByInterval", params, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Permanently delete a driveItem (cannot be restored)",
    )
    def permanent_delete(self):
        """
        Permanently delete a driveItem.
        Note that if you delete items using this method, they will be permanently removed and won't be sent to the
        recycle bin. Therefore, they cannot be restored afterward. For non-permanent delete, use delete_object()
        """
        qry = ServiceOperationQuery(self, "permanentDelete")
        self.context.add_query(qry)
        return self

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Restore a deleted driveItem from the recycle bin",
    )
    def restore(self, parent_reference: ItemReference | None = None, name: str | None = None) -> DriveItem:
        """Restore a driveItem that has been deleted and is currently in the recycle bin.
        NOTE: This functionality is currently only available for OneDrive Personal.

        Args:
            name (str): Optional. The new name for the restored item. If this isn't provided, the same name will be
              used as the original.
            parent_reference (ItemReference or None): Optional. Reference to the parent item the deleted item
              will be restored to.
        """
        payload = {"name": name, "parentReference": parent_reference}
        return_type = DriveItem(self.context)
        self.children.add_child(return_type)
        qry = ServiceOperationQuery(self, "restore", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def preview(self, page: str | int, zoom: int | None = None) -> ClientResult[ItemPreviewInfo]:
        """This action allows you to obtain a short-lived embeddable URL for an item in order
        to render a temporary preview.

        Args:
            page (str or int): Optional. Page number of document to start at, if applicable. Specified as string
              for future use cases around file types such as ZIP.
            zoom (int): Optional. Zoom level to start at, if applicable.
        """
        return_type = ClientResult[ItemPreviewInfo](self.context, ItemPreviewInfo())

        def _preview():
            canonical = DriveItem(
                self.context,
                ResourcePath(
                    self.id,
                    ResourcePath("items", ResourcePath(self.parent_reference.driveId, ResourcePath("drives"))),
                ),
            )
            qry = ServiceOperationQuery(canonical, "preview", None, {"page": page, "zoom": zoom}, None, return_type)
            self.context.add_query(qry)

        self.ensure_properties(["id", "parentReference"]).after_execute(lambda _: _preview())
        return return_type

    @require_permission(
        delegated=["Files.ReadWrite", "Files.ReadWrite.All", "Sites.ReadWrite.All"],
        application=["Files.ReadWrite.All", "Sites.ReadWrite.All"],
        notes="Validate sharing permission by challenge token or password",
    )
    def validate_permission(self, challenge_token: str | None = None, password: str | None = None) -> Self:
        """ """
        payload = {"challengeToken": challenge_token, "password": password}
        qry = ServiceOperationQuery[DriveItem](self, "validatePermission", None, payload)
        self.context.add_query(qry)
        return self

    @property
    def audio(self) -> Audio:
        """Audio metadata, if the item is an audio file. Read-only."""
        return self.properties.get("audio", Audio())

    @property
    def image(self) -> Image:
        """
        Image metadata, if the item is an image. Read-only.
        """
        return self.properties.get("image", Image())

    @property
    def photo(self) -> Photo:
        """Photo metadata, if the item is a photo. Read-only."""
        return self.properties.get("photo", Photo())

    @property
    def location(self) -> GeoCoordinates:
        """Location metadata, if the item has location data"""
        return self.properties.get("location", GeoCoordinates())

    @odata(name="fileSystemInfo")
    @property
    def file_system_info(self) -> FileSystemInfo:
        """File system information on client."""
        return self.properties.get("fileSystemInfo", FileSystemInfo())

    @property
    def folder(self) -> Folder:
        """Folder metadata, if the item is a folder."""
        return self.properties.get("folder", Folder())

    @property
    def file(self) -> File:
        """File metadata, if the item is a file."""
        return self.properties.get("file", File())

    @property
    def is_folder(self) -> bool:
        """Determines whether the provided drive item is folder facet"""
        return self.is_property_available("folder")

    @property
    def is_file(self) -> bool:
        """Determines whether the provided drive item is file facet"""
        return self.is_property_available("file")

    @property
    def size(self) -> int | None:
        """File metadata, if the item is a file."""
        return self.properties.get("size", None)

    @property
    def shared(self) -> Shared:
        """Indicates that the item has been shared with others and provides information about the shared state
        of the item. Read-only."""
        return self.properties.get("shared", Shared())

    @property
    def web_dav_url(self) -> str | None:
        """WebDAV compatible URL for the item."""
        return self.properties.get("webDavUrl", None)

    @property
    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="List children of a driveItem (folder)",
    )
    def children(self) -> EntityCollection["DriveItem"]:
        """Collection containing Item objects for the immediate children of Item. Only items representing folders
        have children.
        """
        from office365.onedrive.driveitems.collection import DriveItemCollection

        return self.properties.get(
            "children",
            DriveItemCollection(self.context, ChildrenPath(self.resource_path)),
        )

    @property
    def listItem(self) -> ListItem:
        """For drives in SharePoint, the associated document library list item."""
        return self.properties.get(
            "listItem",
            ListItem(self.context, ResourcePath("listItem", self.resource_path)),
        )

    @property
    def workbook(self) -> Workbook:
        """For files that are Excel spreadsheets, accesses the workbook API to work with the spreadsheet's contents."""
        return self.properties.get(
            "workbook",
            Workbook(self.context, ResourcePath("workbook", self.resource_path)),
        )

    @property
    def pending_operations(self) -> PendingOperations:
        """If present, indicates that one or more operations that might affect the state of the driveItem are pending
        completion. Read-only."""
        return self.properties.get("pendingOperations", PendingOperations())

    @property
    def permissions(self) -> PermissionCollection:
        """The set of permissions for the item. Read-only. Nullable."""
        return self.properties.get(
            "permissions",
            PermissionCollection(self.context, ResourcePath("permissions", self.resource_path)),
        )

    @property
    def retention_label(self) -> ItemRetentionLabel:
        """Information about retention label and settings enforced on the driveItem."""
        return self.properties.setdefault(
            "retentionLabel",
            ItemRetentionLabel(self.context, ResourcePath("retentionLabel", self.resource_path)),
        )

    @property
    def publication(self) -> PublicationFacet:
        """Provides information about the published or checked-out state of an item,
        in locations that support such actions. This property is not returned by default. Read-only.
        """
        return self.properties.get("publication", PublicationFacet())

    @odata(name="remoteItem")
    @property
    def remote_item(self) -> RemoteItem:
        """Remote item data, if the item is shared from a drive other than the one being accessed. Read-only."""
        return self.properties.get("remoteItem", RemoteItem())

    @odata(name="specialFolder")
    @property
    def special_folder(self) -> SpecialFolder:
        """If the current item is also available as a special folder, this facet is returned. Read-only."""
        return self.properties.get("specialFolder", SpecialFolder())

    @property
    def versions(self) -> EntityCollection[DriveItemVersion]:
        """The list of previous versions of the item. For more info, see getting previous versions.
        Read-only. Nullable."""
        return self.properties.get(
            "versions",
            EntityCollection(
                self.context,
                DriveItemVersion,
                ResourcePath("versions", self.resource_path),
            ),
        )

    @property
    def thumbnails(self) -> EntityCollection[ThumbnailSet]:
        """Collection containing ThumbnailSet objects associated with the item. For more info, see getting thumbnails.
        Read-only. Nullable."""
        return self.properties.get(
            "thumbnails",
            EntityCollection(
                self.context,
                ThumbnailSet,
                ResourcePath("thumbnails", self.resource_path),
            ),
        )

    @property
    def analytics(self) -> ItemAnalytics:
        """Analytics about the view activities that took place on this item."""
        return self.properties.get(
            "analytics",
            ItemAnalytics(self.context, ResourcePath("analytics", self.resource_path)),
        )

    @property
    @require_permission(
        delegated=[
            "Files.Read",
            "Files.Read.All",
            "Files.ReadWrite",
            "Files.ReadWrite.All",
            "Sites.Read.All",
            "Sites.ReadWrite.All",
        ],
        application=["Files.Read.All", "Files.ReadWrite.All", "Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Track changes to a drive item and its children over time",
    )
    def delta(self) -> DeltaCollection["DriveItem"]:
        """Tracks changes to a drive item and its children over time."""
        return self.properties.get(
            "delta",
            DeltaCollection(self.context, DriveItem, DeltaPath(self.resource_path)),
        )

    @property
    def subscriptions(self) -> SubscriptionCollection:
        """The set of subscriptions on the driveItem."""
        return self.properties.get(
            "subscriptions",
            SubscriptionCollection(self.context, ResourcePath("subscriptions", self.resource_path)),
        )

    @property
    def property_ref_name(self) -> str:
        return "id"

    @property
    def bundle(self) -> Bundle:
        """Gets the bundle property"""
        from office365.onedrive.driveitems.bundle import Bundle

        return self.properties.get("bundle", Bundle())

    @property
    def content(self) -> Optional[bytes]:
        """Gets the content property"""
        return self.properties.get("content", None)

    @property
    def ctag(self) -> Optional[str]:
        """Gets the cTag property"""
        return self.properties.get("cTag", None)

    @property
    def malware(self) -> Malware:
        """Gets the malware property"""
        from office365.onedrive.driveitems.malware import Malware

        return self.properties.get("malware", Malware())

    @property
    def package(self) -> Package:
        """Gets the package property"""
        from office365.onedrive.driveitems.package import Package

        return self.properties.get("package", Package())

    @property
    def root(self) -> Root:
        """Gets the root property"""
        from office365.onedrive.root import Root

        return self.properties.get("root", Root())

    @property
    def search_result(self) -> SearchResult:
        """Gets the searchResult property"""
        from office365.search.search_result import SearchResult

        return self.properties.get("searchResult", SearchResult())

    @property
    def video(self) -> Video:
        """Gets the video property"""
        from office365.onedrive.driveitems.video import Video

        return self.properties.get("video", Video())

    @property
    def list_item(self) -> ListItem:
        """Gets the listItem property"""
        from office365.onedrive.listitems.list_item import ListItem

        return self.properties.get("listItem", ListItem(self.context, ResourcePath("listItem", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.DriveItem"
