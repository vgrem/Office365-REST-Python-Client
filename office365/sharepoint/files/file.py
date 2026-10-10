from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from pathlib import Path
from typing import (
    IO,
    TYPE_CHECKING,
    AnyStr,
    AsyncIterator,
    Callable,
    Optional,
    Union,
    cast,
    overload,
)
from urllib.parse import quote, unquote
from uuid import UUID

import requests
from requests import Response
from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.operations import Progress, ProgressCallback
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.transport.base import HeadersCallback
from office365.runtime.types.odata_property import odata
from office365.sharepoint.activities.capabilities import ActivityCapabilities
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.files.checkin_type import CheckinType
from office365.sharepoint.files.move_operations import MoveOperations
from office365.sharepoint.files.versions.collection import FileVersionCollection
from office365.sharepoint.files.versions.event import FileVersionEvent
from office365.sharepoint.folders.folder import Folder
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.pages.customized_page_status import CustomizedPageStatus
from office365.sharepoint.permissions.base_permissions import BasePermissions
from office365.sharepoint.permissions.irm.effective_settings import (
    EffectiveInformationRightsManagementSettings,
)
from office365.sharepoint.permissions.irm.file_settings import (
    InformationRightsManagementFileSettings,
)
from office365.sharepoint.principal.users.user import User
from office365.sharepoint.sharing.links.share_response import ShareLinkResponse
from office365.sharepoint.sharing.object_sharing_information import (
    ObjectSharingInformation,
)
from office365.sharepoint.types.resource_path import ResourcePath as SPResPath
from office365.sharepoint.utilities.upload_status import UploadStatus
from office365.sharepoint.utilities.wopi_frame_action import SPWOPIFrameAction
from office365.sharepoint.webparts.limited_manager import LimitedWebPartManager
from office365.sharepoint.webparts.personalization_scope import PersonalizationScope

if TYPE_CHECKING:
    from office365.runtime.converters.dataframe import DataFrameResult
    from office365.sharepoint.activities.client_response import ActivityClientResponse
    from office365.sharepoint.activities.officefileuservalueresponse import (
        OfficeFileUserValueResponse,
    )
    from office365.sharepoint.approvals.mediaserviceupdateparameters import (
        MediaServiceUpdateParameters,
    )
    from office365.sharepoint.client_context import ClientContext
    from office365.sharepoint.files.deleteparameters import FileDeleteParameters
    from office365.sharepoint.files.download_operation import DownloadOperation
    from office365.sharepoint.listitems.compliance_info import ListItemComplianceInfo
    from office365.sharepoint.webs.web import Web


class AbstractFile(Entity):
    def read(self):
        """Immediately read content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.open_binary(self.context, self.properties["ServerRelativeUrl"])
        return response.content

    def write(self, content):
        """Immediately writes content of file"""
        if not self.is_property_available("ServerRelativeUrl"):
            raise ValueError
        response = File.save_binary(self.context, self.properties["ServerRelativeUrl"], content)
        return response


def _consume_download_chunk(
    file_object: IO,
    chunk: bytes,
    bytes_read: int,
    total: Optional[int],
    chunk_downloaded: Optional[Callable[[int], None]],
    progress: Optional[ProgressCallback],
) -> int:
    """Write one downloaded chunk and report progress; returns the new byte count.

    Shared by the synchronous and asynchronous ``download_session`` loops so the
    chunk-downloaded callback, the ``progress`` snapshot and the write to the
    destination stay in lock-step.
    """
    bytes_read += len(chunk)
    if callable(chunk_downloaded):
        chunk_downloaded(bytes_read)
    if callable(progress):
        progress(Progress(done=bytes_read, total=total, stage="downloading"))
    file_object.write(chunk)
    return bytes_read


class File(AbstractFile):
    """Represents a file in a SharePoint Web site that can be a Web Part Page, an item in a document library,
    or a file in a folder."""

    def __repr__(self):
        return self.server_relative_url or self.unique_id or self.entity_type_name

    def __str__(self):
        return self.name or self.entity_type_name

    @staticmethod
    def from_url(abs_url: str) -> File:
        """Retrieves a File from absolute url

        Args:
            abs_url (str):
        """
        from office365.sharepoint.client_context import ClientContext

        ctx = ClientContext.from_url(abs_url)
        file_relative_url = abs_url.replace(ctx.base_url, "")
        return_type = ctx.web.get_file_by_server_relative_url(file_relative_url)
        return return_type

    def create_anonymous_link(self, is_edit_link: bool = False) -> ClientResult[str]:
        """Create an anonymous link which can be used to access a document without needing to authenticate.

        Args:
            is_edit_link (bool): If true, the link will allow the guest user edit privileges on the item.
        """
        return_type = ClientResult(self.context, str())

        def _file_loaded():
            from office365.sharepoint.webs.web import Web

            assert self.server_relative_url is not None
            Web.create_anonymous_link(self.context, self.server_relative_url, is_edit_link, return_type)

        self.ensure_property("ServerRelativeUrl").after_execute(lambda _: _file_loaded())
        return return_type

    def create_anonymous_link_with_expiration(
        self, expiration: datetime, is_edit_link: bool = False
    ) -> ClientResult[str]:
        """Creates and returns an anonymous link that can be used to access a document without needing to authenticate.

        Args:
            is_edit_link: If true, the link will allow the guest user edit privileges on the item. string parameters
            expiration: A date/time string for which the format conforms to the ISO 8601:2004(E) complete representation
                for calendar date and time of day, and which represents the time and date of expiry for the anonymous
                link. Both the minutes and hour value MUST be specified for the difference between the local and UTC
                time. Midnight is represented as 00:00:00.
        """
        return_type = ClientResult(self.context, str())

        def _file_loaded():
            from office365.sharepoint.webs.web import Web

            assert self.server_relative_url is not None
            Web.create_anonymous_link_with_expiration(
                self.context,
                self.server_relative_url,
                is_edit_link,
                expiration.isoformat(timespec="seconds"),
                return_type,
            )

        self.ensure_property("ServerRelativeUrl").after_execute(lambda _: _file_loaded())
        return return_type

    def get_content(self, start: Optional[int] = None) -> ClientResult[bytes]:
        """Downloads a file content.

        Args:
            start: Optional byte offset. When set, the request carries
                ``Range: bytes={start}-`` so an interrupted download can be
                resumed by appending the returned remainder.
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "$value", return_type=return_type, return_raw_content=True)
        if start:
            qry.before_execute(lambda request: request.set_header("Range", f"bytes={start}-"))
        self.context.add_query(qry)
        return return_type

    def read_dataframe(self, *, format: str = "csv", **opts) -> "DataFrameResult":  # noqa: A002
        """Read this file's **content** into a pandas DataFrame (deferred result).

        Parses the file content (CSV/XLSX/JSON/Parquet) — it does **not** export
        the file's metadata; those are plain properties (``file.name``,
        ``file.length``, ``file.time_last_modified``, ...). Run with
        ``execute_query()`` and read ``.value``:

            >>> df = file.read_dataframe().execute_query().value
        """
        from office365.runtime.converters.dataframe import (
            DataFrameResult,
            dataframe_from_bytes,
        )

        result = DataFrameResult(self.context)

        def _convert(return_type: ClientResult[bytes]) -> None:
            result.set_property("__value", dataframe_from_bytes(return_type.value, format, **opts))

        self.get_content().after_execute(_convert)
        return result

    def write_dataframe(self, df, *, format: str = "csv", index: bool = False, **opts) -> Self:  # noqa: A002
        """Write a pandas DataFrame to this file's **content** (deferred).

        Serializes the frame (CSV is UTF-8 with a BOM) and queues a
        ``SaveBinaryStream``; run with ``execute_query()``. This replaces the
        file content, not its metadata.
        """
        from office365.runtime.converters.dataframe import dataframe_to_bytes

        return self.save_binary_stream(dataframe_to_bytes(df, format, index, **opts))

    def get_exists(self) -> ClientResult[bool]:
        result = ClientResult(self.context, bool())
        result.set_property("__value", False)

        def _after_exists(_):
            result.set_property("__value", True)

        def _on_not_found(error: ClientRequestException):
            assert error.response is not None
            if error.response.status_code == HTTPStatus.NOT_FOUND:
                return
            raise error

        self.select(["Exists"]).get().after_execute(_after_exists).on_error(_on_not_found)

        return result

    def get_pre_authorized_access_url(self, expiration_hours: int) -> ClientResult[str]:
        """Returns a link for downloading the file without authentication.

        Args:
            expiration_hours (int): The number of hours until the link expires.
                If the maximum expiration time defined in the web application is less than the specified expiration
                    time, the maximum expiration time takes precedence.
        """
        return_type = ClientResult(self.context, str())
        params = {"expirationHours": expiration_hours}
        qry = FunctionQuery(self, "GetPreAuthorizedAccessUrl", params, return_type)
        self.context.add_query(qry)
        return return_type

    def get_absolute_url(self) -> ClientResult[str]:
        """Gets absolute url of a File"""
        return_type = ClientResult(self.context, str())

        def _loaded():
            return_type.set_property("__value", self.listItemAllFields.properties.get("EncodedAbsUrl"))

        self.listItemAllFields.ensure_property("EncodedAbsUrl").after_execute(lambda _: _loaded())
        return return_type

    def get_sharing_information(self) -> ObjectSharingInformation:
        """Gets the sharing information for a file."""
        return self.listItemAllFields.get_sharing_information()

    def get_user_effective_permissions(self, user: str | User) -> ClientResult[BasePermissions]:
        """Returns the user permissions for a file"""
        return self.listItemAllFields.get_user_effective_permissions(user)

    def get_wopi_frame_url(self, action: SPWOPIFrameAction = SPWOPIFrameAction.View) -> ClientResult[str]:
        """Returns the full URL to the SharePoint frame page that will initiate the specified WOPI frame action with the
        file's associated WOPI application. If there is no associated WOPI application or associated action,
        the return value is an empty string.

        Args:
            action (str): The full URL to the WOPI frame.
        """
        return_type = ClientResult(self.context, str())
        params = {"action": action.value}
        qry = ServiceOperationQuery(self, "GetWOPIFrameUrl", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def share_link(
        self,
        link_kind: int,
        expiration: Optional[datetime] = None,
        role: Optional[int] = None,
        password: Optional[str] = None,
        share_id: Optional[str] = None,
    ) -> ClientResult[ShareLinkResponse]:
        """Creates a tokenized sharing link for a file based on the specified parameters and optionally
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
            share_id: Unique identifier of an existing tokenized sharing link to retrieve and update. When omitted
                the server retrieves a matching link or creates a new one.
        """
        return self.listItemAllFields.share_link(link_kind, expiration, role, password, share_id)

    def unshare_link(self, link_kind, share_id=None) -> ListItem:
        """Removes the specified tokenized sharing link of the file.

        Args:
            link_kind (int): This optional value specifies the globally unique identifier (GUID) of the tokenized
                sharing link that is intended to be removed.
            share_id (str or None): The kind of tokenized sharing link that is intended to be removed.
        """
        return self.listItemAllFields.unshare_link(link_kind, share_id)  # type: ignore[arg-type]

    def get_image_preview_uri(self, width: int, height: int, client_type=None) -> ClientResult[str]:
        """Returns the uri where the thumbnail with the closest size to the desired can be found.
        The actual resolution of the thumbnail might not be the same as the desired values.

        Args:
            width (int): The desired width of the resolution.
            height (int): The desired height of the resolution.
            client_type (str): The client type. Used for logging.
        """
        return_type = ClientResult(self.context, str())
        payload = {"width": width, "height": height, "clientType": client_type}
        qry = ServiceOperationQuery(self, "GetImagePreviewUri", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_image_preview_url(self, width: int, height: int, client_type: Optional[str] = None) -> ClientResult[str]:
        """Returns the url where the thumbnail with the closest size to the desired can be found.
        The actual resolution of the thumbnail might not be the same as the desired values.

        Args:
            width (int): The desired width of the resolution.
            height (int): The desired height of the resolution.
            client_type (str): The client type. Used for logging.
        """
        return_type = ClientResult(self.context, str())
        payload = {"width": width, "height": height, "clientType": client_type}
        qry = ServiceOperationQuery(self, "GetImagePreviewUrl", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def delete_object(self, bypass_shared_lock: bool = False, *, ignore_missing: bool = False) -> Self:
        """Deletes the file.

        Args:
            bypass_shared_lock: Send ``Prefer: bypass-shared-lock`` so the delete
                succeeds even when the file is open for editing. Without it the
                server rejects the request with
                :class:`~office365.runtime.exceptions.FileLockedException` (HTTP 423).
            ignore_missing: When ``True``, deleting a file that no longer exists
                (HTTP 404) succeeds instead of raising.
        """
        super().delete_object(ignore_missing=ignore_missing)
        if bypass_shared_lock:
            from office365.runtime.http.prefer import prefer_bypass_shared_lock

            self.context.before_execute(prefer_bypass_shared_lock, once=True)
        return self

    def recycle(self, ignore_missing: bool = False) -> ClientResult[str]:
        """Moves the file to the Recycle Bin and returns the identifier of the new Recycle Bin item.

        Args:
            ignore_missing (bool): When True, recycling a file that no longer
                exists (HTTP 404) succeeds instead of raising.
        """
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(self, "Recycle", None, None, None, return_type)
        self.context.add_query(qry)
        self._tolerate_missing(ignore_missing)
        return return_type

    def approve(self, comment: str) -> Self:
        """Approves the file submitted for content approval with the specified comment.

        Args:
            comment (str): A string containing the comment.
        """
        qry = ServiceOperationQuery(self, "Approve", {"comment": comment})
        self.context.add_query(qry)
        return self

    def deny(self, comment: str) -> Self:
        """Denies approval for a file that was submitted for content approval.

        Args:
            comment (str): A string containing the comment.
        """
        qry = ServiceOperationQuery(self, "Deny", {"comment": comment})
        self.context.add_query(qry)
        return self

    def copyto(
        self,
        destination: Union[Folder, str],
        overwrite: bool = False,
        file_name: Optional[str] = None,
    ) -> "File":
        """Copies the file to the destination URL.

        Args:
            destination (office365.sharepoint.folders.folder.Folder or str): Specifies the destination folder or folder
                server relative url where to copy a file.
            overwrite (bool): Specifies whether a file with the same name is overwritten.
            file_name (str): A new file name
        """
        return_type = File(self.context)
        assert self.parent_collection is not None
        self.parent_collection.add_child(return_type)

        def _copyto(destination_folder: Folder) -> None:
            assert self.name is not None
            file_path = "/".join([str(destination_folder.server_relative_url), file_name or self.name])
            return_type.set_property("ServerRelativeUrl", file_path)

            params = {"strNewUrl": file_path, "boverwrite": overwrite}
            qry = ServiceOperationQuery(self, "CopyTo", params)
            self.context.add_query(qry)

        def _source_file_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativeUrl").after_execute(lambda _: _copyto(dest))
            else:
                self.context.web.ensure_folder_path(destination).after_execute(_copyto)

        self.ensure_properties(["ServerRelativeUrl", "Name"]).after_execute(lambda _: _source_file_resolved())
        return return_type

    def copyto_using_path(self, destination, overwrite=False, file_name=None):  # type: ignore[override]
        """Copies the file to the destination path. Server MUST overwrite an existing file of the same name
        if overwrite is true.

        Args:
            overwrite (bool): Specifies whether a file with the same name is overwritten.
            destination (office365.sharepoint.folders.folder.Folder or str): Specifies the destination folder or folder
                server relative url where to copy a file.
            file_name (str): New file name
        """

        return_type = File(self.context)
        assert self.parent_collection is not None
        self.parent_collection.add_child(return_type)

        def _copyto_using_path(destination_folder: Folder) -> None:
            assert self.name is not None
            file_path = "/".join([str(destination_folder.server_relative_path), file_name or self.name])
            return_type.set_property("ServerRelativePath", file_path)

            params = {"DecodedUrl": file_path, "bOverWrite": overwrite}
            qry = ServiceOperationQuery(self, "CopyToUsingPath", params)
            self.context.add_query(qry)

        def _source_file_resolved():
            if isinstance(destination, Folder):
                destination.ensure_property("ServerRelativePath").after_execute(
                    lambda _: _copyto_using_path(destination)
                )
            else:
                self.context.web.ensure_folder_path(destination).get().select(["ServerRelativePath"]).after_execute(
                    _copyto_using_path
                )

        self.ensure_properties(["ServerRelativePath", "Name"]).after_execute(lambda _: _source_file_resolved())
        return return_type

    def moveto(self, destination: Union[str, Folder], flag: int) -> Self:
        """Moves the file to the specified destination url.

        Args:
            destination (str or Folder): Specifies the existing folder or folder site relative url.
            flag (int): Specifies the kind of move operation.
        """

        def _moveto(destination_folder: Folder) -> None:
            assert self.name is not None
            file_url = "/".join([str(destination_folder.server_relative_url), self.name])

            params = {"newurl": file_url, "flags": flag}
            qry = ServiceOperationQuery(self, "moveto", params)
            self.context.add_query(qry)

            def _update_file(return_type):
                self.set_property("ServerRelativeUrl", file_url)

            self.context.after_execute(_update_file)

        def _source_file_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativeUrl").after_execute(lambda _: _moveto(dest))
            else:
                self.context.web.ensure_folder_path(destination).get().after_execute(_moveto)

        self.ensure_properties(["ServerRelativeUrl", "Name"]).after_execute(lambda _: _source_file_resolved())
        return self

    def move_to_using_path(self, destination: Union[str, Folder], flag: MoveOperations) -> Self:
        """Moves the file to the specified destination path.

        Args:
            destination (str or office365.sharepoint.folders.folder.Folder): Specifies the destination folder path or
                existing folder object
            flag (int): Specifies the kind of move operation.
        """

        def _move_to_using_path(destination_folder: Folder) -> None:
            assert self.name is not None
            file_path = "/".join([str(destination_folder.server_relative_path), self.name])
            params = {"DecodedUrl": file_path, "moveOperations": flag.value}
            qry = ServiceOperationQuery(self, "MoveToUsingPath", params)

            def _update_file(return_type: File) -> None:
                self.set_property("ServerRelativePath", file_path)

            self.context.add_query(qry).after_execute(_update_file)

        def _source_file_resolved():
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativePath").after_execute(lambda _: _move_to_using_path(dest))
            else:
                self.context.web.ensure_folder_path(destination).get().select(["ServerRelativePath"]).after_execute(
                    _move_to_using_path
                )

        self.ensure_properties(["ServerRelativePath", "Name"]).after_execute(lambda _: _source_file_resolved())
        return self

    def move_by_path(
        self,
        destination: Union[str, Folder],
        flag: MoveOperations = MoveOperations.overwrite,
    ) -> Self:
        """Moves the file to the specified destination using ``MoveCopyUtil.MoveFileByPath``.

        Unlike :meth:`move_to_using_path` (``File/MoveToUsingPath``), both paths
        travel in the request body, so deep folder structures don't hit
        SharePoint's URL length limit.

        Args:
            destination (str or office365.sharepoint.folders.folder.Folder): Specifies the
                destination folder path or an existing folder object.
            flag (MoveOperations): Specifies the kind of move operation
                (defaults to ``overwrite``).
        """
        from office365.sharepoint.utilities.move_copy_options import MoveCopyOptions
        from office365.sharepoint.utilities.move_copy_util import MoveCopyUtil

        def _move_by_path(destination_folder: Folder) -> None:
            assert self.name is not None
            assert self.server_relative_path is not None
            file_path = "/".join([str(destination_folder.server_relative_path), self.name])
            options = MoveCopyOptions(KeepBoth=flag != MoveOperations.overwrite)
            MoveCopyUtil.move_file_by_path(self.context, str(self.server_relative_path), file_path, options)

            def _update_file(_) -> None:
                self.set_property("ServerRelativePath", file_path)

            self.context.after_execute(_update_file)

        def _source_file_resolved() -> None:
            if isinstance(destination, Folder):
                dest = destination
                destination.ensure_property("ServerRelativePath").after_execute(lambda _: _move_by_path(dest))
            else:
                self.context.web.ensure_folder_path(destination).get().select(["ServerRelativePath"]).after_execute(
                    _move_by_path
                )

        self.ensure_properties(["ServerRelativePath", "Name"]).after_execute(lambda _: _source_file_resolved())
        return self

    def publish(self, comment: str) -> Self:
        """Submits the file for content approval with the specified comment.

        Args:
            comment (str): Specifies the comment.
        """
        qry = ServiceOperationQuery(self, "Publish", {"comment": comment})
        self.context.add_query(qry)
        return self

    def unpublish(self, comment: str) -> Self:
        """Removes the file from content approval or unpublishes a major version.

        Args:
            comment (str): Specifies the comment for UnPublish. Its length MUST be equal to or less than 1023.
        """
        qry = ServiceOperationQuery(self, "unpublish", {"comment": comment})
        self.context.add_query(qry)
        return self

    def check_access_and_post_view_audit_event(self) -> ClientResult[bool]:
        """"""
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(self, "CheckAccessAndPostViewAuditEvent", return_type=return_type)
        self.context.add_query(qry)
        return return_type

    def checkout(self) -> Self:
        """Checks out the file from a document library based on the check-out type."""
        qry = ServiceOperationQuery(self, "checkout")
        self.context.add_query(qry)
        return self

    def checkin(self, comment: str, checkin_type: CheckinType) -> Self:
        """Checks the file in to a document library based on the check-in type.

        Args:
            comment: comment to the new version of the file
            checkin_type: 0 (minor), or 1 (major) or 2 (overwrite) For more information on checkin types, please see
                https://docs.microsoft.com/en-us/previous-versions/office/sharepoint-csom/ee542953(v%3Doffice.15)
            checkin_type (int): Specifies the type of check-in.
        """
        params = {"comment": comment, "checkInType": checkin_type.value}
        qry = ServiceOperationQuery(self, "checkin", params)
        self.context.add_query(qry)
        return self

    def undocheckout(self) -> Self:
        """Reverts an existing checkout for the file."""
        qry = ServiceOperationQuery(self, "UndoCheckout")
        self.context.add_query(qry)
        return self

    def get_limited_webpart_manager(
        self, scope: PersonalizationScope = PersonalizationScope.User
    ) -> LimitedWebPartManager:
        """Specifies the control set used to access, modify, or add Web Parts associated with this Web Part Page and
        view.

        Args:
            scope (int): Specifies the personalization scope value that depicts how Web Parts are viewed on the Web Part
                Page.
        """
        return LimitedWebPartManager(
            self.context,
            ServiceOperationPath("GetLimitedWebPartManager", [scope.value], self.resource_path),
        )

    def open_binary_stream(self) -> ClientResult[bytes]:
        """Opens the file as a stream."""
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "OpenBinaryStream", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def save_binary_stream(self, stream: bytes) -> Self:
        """Saves the file in binary format.

        Args:
            stream (str or bytes): A stream containing the contents of the specified file.
        """
        qry = ServiceOperationQuery(self, "SaveBinaryStream", None, stream)  # type: ignore[arg-type]
        self.context.add_query(qry)
        return self

    def get_upload_status(self, upload_id: str) -> UploadStatus:
        """Gets the status of a chunk upload session.

        Args:
            upload_id (str): The upload session ID.
        """
        payload = {
            "uploadId": upload_id,
        }
        return_type = UploadStatus(self.context)
        qry = ServiceOperationQuery(self, "GetUploadStatus", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def upload_with_checksum(self, upload_id: str, checksum: str, stream: bytes) -> File:
        """Args:
        upload_id (str): The upload session ID.
        checksum (str):
        stream (bytes):
        """
        return_type = File(self.context)
        params = {"uploadId": upload_id, "checksum": checksum}
        qry = ServiceOperationQuery(self, "UploadWithChecksum", params, stream, None, return_type)
        # type: ignore[arg-type]
        self.context.add_query(qry)
        return return_type

    def cancel_upload(self, upload_id: str) -> Self:
        """Aborts the chunk upload session without saving the uploaded data. If StartUpload (section 3.2.5.64.2.1.22)
        created the file, the file will be deleted.

        Args:
            upload_id (str): The upload session ID.
        """
        payload = {
            "uploadId": upload_id,
        }
        qry = ServiceOperationQuery(self, "CancelUpload", None, payload)
        self.context.add_query(qry)
        return self

    def start_upload(self, upload_id: str, content: bytes) -> ClientResult[int]:
        """Starts a new chunk upload session and uploads the first fragment.

        Args:
            content (bytes): File content
            upload_id (str): Upload session id
        """
        return_type = ClientResult(self.context, int())
        params = {"uploadID": upload_id}
        qry = ServiceOperationQuery(self, "startUpload", params, content, None, return_type)  # type: ignore[arg-type]
        self.context.add_query(qry)
        return return_type

    def continue_upload(self, upload_id: str, file_offset: int, content: bytes) -> ClientResult[int]:
        """Continues the chunk upload session with an additional fragment. The current file content is not changed.

        Args:
            upload_id (str): Upload session id
            file_offset (int): File offset
            content (bytes): File content
        """
        return_type = ClientResult(self.context, int())
        qry = ServiceOperationQuery(
            self,
            "continueUpload",
            {
                "uploadID": upload_id,
                "fileOffset": file_offset,
            },
            content,  # type: ignore[arg-type]
            None,
            return_type,
        )
        self.context.add_query(qry)
        return return_type

    def finish_upload(self, upload_id: str, file_offset: int, content: bytes) -> Self:
        """Uploads the last file fragment and commits the file. The current file content is changed when this method
        completes.

        Args:
            upload_id (str): Upload session id
            file_offset (int): File offset
            content (bytes): File content
        """
        params = {"uploadID": upload_id, "fileOffset": file_offset}
        qry = ServiceOperationQuery(self, "finishUpload", params, content, None, self)  # type: ignore[arg-type]
        self.context.add_query(qry)
        return self

    def finish_upload_with_checksum(self, upload_id: str, file_offset: int, checksum: str, stream: bytes) -> Self:
        """Uploads the last file fragment and commits the file. The current file content is changed when this method
        completes.

        Args:
            upload_id (str): Upload session id
            file_offset (int): File offset
            checksum (str): File checksum
            stream (bytes): File content
        """
        payload = {
            "uploadID": upload_id,
            "fileOffset": file_offset,
            "checksum": checksum,
        }
        qry = ServiceOperationQuery(self, "FinishUploadWithChecksum", payload, stream, None, self)
        # type: ignore[arg-type]
        self.context.add_query(qry)
        return self

    @staticmethod
    def save_binary(context: ClientContext, server_relative_url: str, content: bytes):
        """Uploads a file"""
        try:
            decoded = unquote(server_relative_url)
        except (ValueError, AttributeError, TypeError):
            decoded = server_relative_url
        # OData literals escape embedded single quotes by doubling them (' -> '')
        decoded_server_relative_url = decoded.replace("'", "''")

        url = (
            f"{context.service_root_url}/web/getFileByServerRelativePath"
            f"(DecodedUrl='{quote(decoded_server_relative_url)}')/$value"
        )

        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.set_header("X-HTTP-Method", "PUT")
        request.data = content
        response = context.pending_request().execute_request_direct(request)
        return response

    @staticmethod
    def open_binary(context: ClientContext, server_relative_url: str) -> Response:
        """
        Returns the file object located at the specified server-relative URL.
        """
        try:
            decoded = unquote(server_relative_url)
        except (ValueError, AttributeError, TypeError):
            decoded = server_relative_url
        # OData literals escape embedded single quotes by doubling them (' -> '')
        decoded_server_relative_url = decoded.replace("'", "''")

        url = (
            f"{context.service_root_url}/web/getFileByServerRelativePath"
            f"(DecodedUrl='{quote(decoded_server_relative_url)}')/$value"
        )

        request = RequestOptions(url)
        request.method = HttpMethod.Get
        response = context.pending_request().execute_request_direct(request)
        return response

    @overload
    def download(self, file_object: IO, after_downloaded: Optional[Callable[[File], None]] = ...) -> Self: ...

    @overload
    def download(
        self,
        file_object: Union[str, Path],
        after_downloaded: Optional[Callable[[File], None]] = ...,
        *,
        overwrite: bool = ...,
        resume: bool = ...,
    ) -> "DownloadOperation": ...

    def download(
        self,
        file_object: Union[IO, str, Path],
        after_downloaded: Optional[Callable[[File], None]] = None,
        *,
        overwrite: bool = False,
        resume: bool = False,
    ) -> Union[Self, "DownloadOperation"]:
        """Download a file's content.

        Two forms:

        * **Stream** (small files): pass an open binary file object; the content
          is written when the query executes and this file is returned for
          chaining. Use :meth:`download_session` for large files.
        * **Path** (convenience): pass a ``str``/``Path`` destination and get back
          a deferred :class:`~office365.sharepoint.files.download_operation.DownloadOperation`
          that opens/writes/closes the file for you:

              >>> file.download("/tmp/a.docx").execute_query()
              >>> await file.download("/tmp/a.docx").execute_query_async()

        Args:
            file_object: Open binary stream, or a destination path.
            after_downloaded ((File) -> None): Per-file callback (invoked with
              ``self`` once the content is written).
            overwrite: Path form only — when ``False`` (default) an existing
              destination is skipped.
            resume: Path form only — when ``True`` and a smaller destination
              exists, download only the missing bytes (HTTP ``Range``) and
              append them, instead of skipping the file.
        """
        if isinstance(file_object, (str, Path)):
            from office365.sharepoint.files.download_operation import DownloadOperation

            return DownloadOperation.for_file(
                self, file_object, overwrite=overwrite, resume=resume, on_file=after_downloaded
            )

        def _save_content(return_type: ClientResult[AnyStr]) -> None:
            file_object.write(return_type.value)
            if callable(after_downloaded):
                after_downloaded(self)

        def _download_inner():
            self.get_content().after_execute(_save_content)

        self.ensure_property("ServerRelativePath").after_execute(lambda _: _download_inner())
        return self

    def download_session(
        self,
        file_object,
        chunk_downloaded=None,
        chunk_size=1024 * 1024,
        use_path=True,
        progress=None,
    ):
        """Download a file content. Use this method to download a content of a large size

        Args:
            file_object (typing.IO):
            chunk_downloaded ((int)->None or None):
            chunk_size (int):
            use_path (bool): File addressing by path flag
            progress (office365.runtime.operations.ProgressCallback): Optional hook
              invoked per chunk with a ``Progress`` snapshot (``done`` = bytes
              downloaded so far, ``total`` = content length when known).
        """

        def _download_as_stream():
            qry = ServiceOperationQuery(self, "$value")

            def _construct_request(request: RequestOptions) -> None:
                request.stream = True
                request.method = HttpMethod.Get
                if file_object.seekable():
                    file_object.seek(0)
                    file_object.truncate()

            def _process_response(response: requests.Response) -> None:
                self.context.pending_request().beforeExecute -= _construct_request
                total = int(response.headers.get("Content-Length", 0)) or None
                bytes_read = 0
                for chunk in response.iter_content(chunk_size=chunk_size):
                    bytes_read = _consume_download_chunk(
                        file_object, chunk, bytes_read, total, chunk_downloaded, progress
                    )

            self.context.add_query(qry).before_execute(_construct_request, once=False).after_execute(
                _process_response, include_response=True
            )

        if use_path:
            self.ensure_property("ServerRelativePath").after_execute(lambda _: _download_as_stream())
        else:
            self.ensure_property("ServerRelativeUrl").after_execute(lambda _: _download_as_stream())
        return self

    async def download_session_async(
        self,
        file_object: IO,
        chunk_downloaded: Optional[Callable[[int], None]] = None,
        chunk_size: int = 1024 * 1024,
        use_path: bool = True,
        progress: Optional[ProgressCallback] = None,
    ) -> Self:
        """Async twin of :meth:`download_session` that never blocks the loop.

        Streams a large file into ``file_object`` through the configured async
        transport — native when one is set (e.g.
        :class:`~office365.runtime.transport.httpx_transport.HttpxTransport`),
        otherwise a worker thread — so the event loop stays free while the body
        is transferred and the content is never buffered in memory.

        Unlike the deferred :meth:`download_session`, this is an awaitable
        coroutine: it ensures the required address property is loaded (draining
        any pending queries), sends the request and writes every chunk before it
        returns. ``chunk_downloaded`` and ``progress`` behave exactly as on the
        synchronous path.

        Args:
            file_object: An open binary file object to write into.
            chunk_downloaded: Optional ``(bytes_so_far) -> None`` callback invoked
                after each chunk.
            chunk_size: Number of bytes per chunk.
            use_path: Address the file by ``ServerRelativePath`` (default) rather
                than ``ServerRelativeUrl``.
            progress: Optional ``ProgressCallback`` invoked per chunk with a
                ``Progress`` snapshot (``done`` = bytes downloaded so far,
                ``total`` = content length when known).

        Returns:
            Self for method chaining.
        """
        pending = self.context.pending_request()
        self.ensure_property("ServerRelativePath" if use_path else "ServerRelativeUrl")
        if self.context.has_pending_request:
            await self.context.execute_query_async()

        qry = ServiceOperationQuery(self, "$value")
        request = pending.build_request(qry)
        request.stream = True
        request.method = HttpMethod.Get
        await pending.before_execute_async(request)

        if file_object.seekable():
            file_object.seek(0)
            file_object.truncate()

        total: list[Optional[int]] = [None]

        def _capture_length(headers) -> None:
            length = headers.get("Content-Length")
            total[0] = int(length) if length else None

        bytes_read = 0
        try:
            async for chunk in pending.async_transport.stream_async(
                request, chunk_size=chunk_size, on_headers=_capture_length
            ):
                bytes_read = _consume_download_chunk(
                    file_object, chunk, bytes_read, total[0], chunk_downloaded, progress
                )
        except requests.HTTPError as e:
            error = ClientRequestException.from_response(e.response)
            if pending.onError:
                pending.onError(error)
                return self
            raise error from e
        return self

    async def get_content_stream_async(
        self,
        chunk_size: int = 1024 * 1024,
        use_path: bool = True,
        on_headers: Optional[HeadersCallback] = None,
    ) -> AsyncIterator[bytes]:
        """Yield the file body in chunks without buffering it in memory.

        The streaming primitive behind :meth:`download_session_async`: it ensures
        the required address property is loaded (draining any pending queries),
        sends the ``$value`` request through the configured async transport and
        yields the body as it arrives, so the bytes can be piped straight to
        another destination without opening a local file or materialising the
        content::

            async for chunk in file.get_content_stream_async():
                await sink.send(chunk)

        Args:
            chunk_size: Number of bytes per yielded chunk.
            use_path: Address the file by ``ServerRelativePath`` (default) rather
                than ``ServerRelativeUrl``.
            on_headers: Optional callback invoked once with the response headers
                before the first chunk (e.g. to read ``Content-Length``).

        Yields:
            Successive slices of the file body.

        Raises:
            ClientRequestException: When the service returns an error status.
        """
        pending = self.context.pending_request()
        self.ensure_property("ServerRelativePath" if use_path else "ServerRelativeUrl")
        if self.context.has_pending_request:
            await self.context.execute_query_async()
        qry = ServiceOperationQuery(self, "$value")
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

    def rename(self, new_file_name: str) -> Self:
        """Rename a file

        Args:
            new_file_name (str): A new file name
        """
        item = self.listItemAllFields
        item.set_property("FileLeafRef", new_file_name)
        qry = UpdateEntityQuery(item)
        self.context.add_query(qry)
        return self

    @property
    def activity_capabilities(self) -> ActivityCapabilities:
        """"""
        return self.properties.get("ActivityCapabilities", ActivityCapabilities())

    @property
    def checkin_comment(self) -> Optional[str]:
        """Specifies the comment used when a document is checked into a document library.
        Its length MUST be equal to or less than 1023."""
        return self.properties.get("CheckInComment", None)

    @property
    def content_tag(self) -> Optional[str]:
        """Returns internal version of content, used to validate document equality for read purposes."""
        return self.properties.get("ContentTag", None)

    @property
    def author(self) -> User:
        """Specifies the user who added the file."""
        return self.properties.get("Author", User(self.context, ResourcePath("Author", self.resource_path)))

    @odata(name="CheckedOutByUser")
    @property
    def checked_out_by_user(self) -> User:
        """Gets an object that represents the user who has checked out the file."""
        return self.properties.get(
            "CheckedOutByUser",
            User(self.context, ResourcePath("CheckedOutByUser", self.resource_path)),
        )

    @property
    def check_out_type(self) -> Optional[int]:
        return self.properties.get("CheckOutType", None)

    @odata(name="ExpirationDate")
    @property
    def expiration_date(self) -> Optional[datetime]:
        """Specifies the date and time when the file expires."""
        return self.properties.get("ExpirationDate", datetime.min)

    @odata(name="VersionEvents")
    @property
    def version_events(self) -> EntityCollection[FileVersionEvent]:
        """Gets the history of events on this version object."""
        return self.properties.get(
            "VersionEvents",
            EntityCollection(
                self.context,
                FileVersionEvent,
                ResourcePath("VersionEvents", self.resource_path),
            ),
        )

    @odata(name="EffectiveInformationRightsManagementSettings")
    @property
    def effective_information_rights_management_settings(
        self,
    ) -> EffectiveInformationRightsManagementSettings:
        """
        Returns the effective Information Rights Management (IRM) settings for the file.

        A file can be IRM-protected based on the IRM settings for the file itself, based on the IRM settings for the
        list which contains the file, or based on a rule. From greatest to least, IRM settings take precedence in the
        following order: rule, list, then file.
        """
        path = ResourcePath("EffectiveInformationRightsManagementSettings", self.resource_path)
        return self.properties.get(
            "EffectiveInformationRightsManagementSettings",
            EffectiveInformationRightsManagementSettings(self.context, path),
        )

    @odata(name="InformationRightsManagementSettings")
    @property
    def information_rights_management_settings(
        self,
    ) -> InformationRightsManagementFileSettings:
        """Returns the Information Rights Management (IRM) settings for the file."""
        return self.properties.get(
            "InformationRightsManagementSettings",
            InformationRightsManagementFileSettings(
                self.context,
                ResourcePath("InformationRightsManagementSettings", self.resource_path),
            ),
        )

    @property
    def listItemAllFields(self) -> ListItem:
        """Gets a value that specifies the list item fields values for the list item corresponding to the file."""
        return self.properties.setdefault(
            "ListItemAllFields",
            ListItem(self.context, ResourcePath("listItemAllFields", self.resource_path)),
        )

    @odata(name="VersionExpirationReport")
    @property
    def version_expiration_report(self) -> FileVersionCollection:
        """"""
        return self.properties.get(
            "VersionExpirationReport",
            FileVersionCollection(
                self.context,
                ResourcePath("VersionExpirationReport", self.resource_path),
            ),
        )

    @property
    def versions(self) -> FileVersionCollection:
        """Gets a value that returns a collection of file version objects that represent the versions of the file."""
        return self.properties.get(
            "Versions",
            FileVersionCollection(self.context, ResourcePath("versions", self.resource_path)),
        )

    @odata(name="ModifiedBy")
    @property
    def modified_by(self) -> User:
        """Gets a value that returns the user who last modified the file."""
        return self.properties.get(
            "ModifiedBy",
            User(self.context, ResourcePath("ModifiedBy", self.resource_path)),
        )

    @odata(name="LockedByUser")
    @property
    def locked_by_user(self) -> User:
        """Gets a value that returns the user that owns the current lock on the file."""
        return self.properties.get(
            "LockedByUser",
            User(self.context, ResourcePath("LockedByUser", self.resource_path)),
        )

    @property
    def server_relative_url(self) -> Optional[str]:
        """Gets the relative URL of the file based on the URL for the server."""
        return self.properties.get("ServerRelativeUrl", None)

    @odata(name="ServerRelativePath")
    @property
    def server_relative_path(self) -> SPResPath:
        """Gets the server-relative Path of the list folder."""
        return self.properties.get("ServerRelativePath", SPResPath())

    @property
    def length(self) -> Optional[int]:
        """Gets the file size."""
        return int(self.properties.get("Length", 0))

    @property
    def exists(self) -> Optional[bool]:
        """Specifies whether the file exists."""
        return self.properties.get("Exists", None)

    @property
    def irm_enabled(self) -> Optional[bool]:
        """Specifies whether or not Information Rights Management (IRM) is enabled at the file level.
        A value of true indicates IRM is enabled; a value of false indicates IRM is disabled.
        """
        return self.properties.get("IrmEnabled", None)

    @property
    def level(self) -> Optional[str]:
        """Specifies the publishing level of the file."""
        return self.properties.get("Level", None)

    @property
    def linking_uri(self) -> Optional[str]:
        """Specifies the URL that is suitable for durable linking to the file."""
        return self.properties.get("LinkingUri", None)

    @property
    def name(self) -> Optional[str]:
        """Specifies the file name including the extension.
        It MUST NOT be NULL. Its length MUST be equal to or less than 260.
        """
        return self.properties.get("Name", None)

    @property
    def list_id(self) -> Optional[str]:
        """Gets the GUID that identifies the List containing the file."""
        return self.properties.get("ListId", None)

    @property
    def site_id(self) -> Optional[str]:
        """Gets the GUID that identifies the site collection containing the file."""
        return self.properties.get("SiteId", None)

    @property
    def web_id(self) -> Optional[str]:
        """Gets the GUID for the site containing the file."""
        return self.properties.get("WebId", None)

    @odata(name="TimeCreated")
    @property
    def time_created(self) -> Optional[datetime]:
        """Gets a value that specifies when the file was created."""
        return self.properties.get("TimeCreated", datetime.min)

    @odata(name="TimeLastModified")
    @property
    def time_last_modified(self) -> Optional[datetime]:
        """Specifies when the file was last modified."""
        return self.properties.get("TimeLastModified", datetime.min)

    @property
    def minor_version(self) -> Optional[int]:
        """Gets a value that specifies the minor version of the file."""
        return self.properties.get("MinorVersion", None)

    @property
    def major_version(self) -> Optional[int]:
        """Gets a value that specifies the major version of the file."""
        return self.properties.get("MajorVersion", None)

    @property
    def unique_id(self) -> Optional[str]:
        """Gets a value that specifies the a file unique identifier"""
        return self.properties.get("UniqueId", None)

    @property
    def customized_page_status(self) -> Optional[CustomizedPageStatus]:
        """Specifies the customization status of the file."""
        return self.properties.get("CustomizedPageStatus", CustomizedPageStatus.None_)

    @property
    def parent_folder(self) -> Optional[Folder]:
        """Gets the parent folder.

        Returns:
            The parent Folder object

        Raises:
            ValueError: If no parent collection exists
            TypeError: If parent is not a Folder
        """

        from office365.sharepoint.folders.folder import Folder

        if self.parent_collection is None:
            return None

        parent = self.parent_collection.parent
        if parent is None:
            return None

        if isinstance(parent, Folder):
            return cast(Folder, parent)

        raise TypeError(f"Expected parent to be Folder but got {type(parent).__name__}")

    def set_property(self, name, value, persist_changes=True):
        super().set_property(name, value, persist_changes)

        # fallback: prioritize using UniqueId
        if name == "UniqueId":
            self._resource_path = self.context.web.get_file_by_id(value).resource_path

        # alternative fallback: create a new resource path
        if self._resource_path is None:
            if name == "ServerRelativeUrl":
                self._resource_path = self.context.web.get_file_by_server_relative_url(value).resource_path
            elif name == "ServerRelativePath":
                self._resource_path = self.context.web.get_file_by_server_relative_path(value).resource_path
        return self

    @property
    def archived(self) -> Optional[bool]:
        """Gets the Archived property"""
        return self.properties.get("Archived", None)

    @property
    def check_in_comment(self) -> Optional[str]:
        """Gets the CheckInComment property"""
        return self.properties.get("CheckInComment", None)

    @property
    def compliance_info(self) -> ListItemComplianceInfo:
        """Gets the ComplianceInfo property"""
        from office365.sharepoint.listitems.compliance_info import (
            ListItemComplianceInfo,
        )

        return self.properties.get("ComplianceInfo", ListItemComplianceInfo())

    @property
    def e_tag(self) -> Optional[str]:
        """Gets the ETag property"""
        return self.properties.get("ETag", None)

    @property
    def exists_allow_throw_for_policy_failures(self) -> Optional[bool]:
        """Gets the ExistsAllowThrowForPolicyFailures property"""
        return self.properties.get("ExistsAllowThrowForPolicyFailures", None)

    @property
    def exists_with_exception(self) -> Optional[bool]:
        """Gets the ExistsWithException property"""
        return self.properties.get("ExistsWithException", None)

    @property
    def has_alternate_content_streams(self) -> Optional[bool]:
        """Gets the HasAlternateContentStreams property"""
        return self.properties.get("HasAlternateContentStreams", None)

    @property
    def linking_url(self) -> Optional[str]:
        """Gets the LinkingUrl property"""
        return self.properties.get("LinkingUrl", None)

    @property
    def page_render_type(self) -> Optional[int]:
        """Gets the PageRenderType property"""
        return self.properties.get("PageRenderType", None)

    @property
    def server_redirected_url(self) -> Optional[str]:
        """Gets the ServerRedirectedUrl property"""
        return self.properties.get("ServerRedirectedUrl", None)

    @property
    def suppress_expiration_notification(self) -> Optional[bool]:
        """Gets the SuppressExpirationNotification property"""
        return self.properties.get("SuppressExpirationNotification", None)

    @property
    def title(self) -> Optional[str]:
        """Gets the Title property"""
        return self.properties.get("Title", None)

    @property
    def ui_version(self) -> Optional[int]:
        """Gets the UIVersion property"""
        return self.properties.get("UIVersion", None)

    @property
    def ui_version_label(self) -> Optional[str]:
        """Gets the UIVersionLabel property"""
        return self.properties.get("UIVersionLabel", None)

    @property
    def vroom_drive_id(self) -> Optional[str]:
        """Gets the VroomDriveID property"""
        return self.properties.get("VroomDriveID", None)

    @property
    def vroom_item_id(self) -> Optional[str]:
        """Gets the VroomItemID property"""
        return self.properties.get("VroomItemID", None)

    @property
    def list_item_all_fields(self) -> ListItem:
        """Gets the ListItemAllFields property"""
        from office365.sharepoint.listitems.listitem import ListItem

        return self.properties.get(
            "ListItemAllFields", ListItem(self.context, ResourcePath("ListItemAllFields", self.resource_path))
        )

    @property
    def web(self) -> Web:
        """Gets the Web property"""
        from office365.sharepoint.webs.web import Web

        return self.properties.get("Web", Web(self.context, ResourcePath("Web", self.resource_path)))

    def add_client_activities(
        self, activities_stream: bytes
    ) -> ClientResult[ClientValueCollection[ActivityClientResponse]]:
        """AddClientActivities operation.

        Args:
            activities_stream (bytes):
                activitiesStream parameter
        """
        from office365.sharepoint.activities.client_response import (
            ActivityClientResponse,
        )

        return_type = ClientResult(self.context, ClientValueCollection[ActivityClientResponse]())
        qry = ServiceOperationQuery(
            self, "AddClientActivities", None, {"activitiesStream": activities_stream}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def change_content_storage_schema(self, desired_schema: str) -> ClientResult[bool]:
        """ChangeContentStorageSchema operation.

        Args:
            desired_schema (str):
                desiredSchema parameter
        """
        return_type = ClientResult(self.context, bool())
        qry = ServiceOperationQuery(
            self, "ChangeContentStorageSchema", None, {"desiredSchema": desired_schema}, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    def check_in(self, comment: str, check_in_type: int) -> Self:
        """CheckIn operation.

        Args:
            comment (str):
                comment parameter
            check_in_type (int):
                checkInType parameter
        """
        qry = ServiceOperationQuery(
            self, "CheckIn", None, {"comment": comment, "checkInType": check_in_type}, None, None
        )
        self.context.add_query(qry)
        return self

    def check_out(self) -> Self:
        """CheckOut operation."""
        qry = ServiceOperationQuery(self, "CheckOut", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def copy_to(self, str_new_url: str, bover_write: bool) -> Self:
        """CopyTo operation.

        Args:
            str_new_url (str):
                strNewUrl parameter
            bover_write (bool):
                bOverWrite parameter
        """
        qry = ServiceOperationQuery(
            self, "CopyTo", None, {"strNewUrl": str_new_url, "bOverWrite": bover_write}, None, None
        )
        self.context.add_query(qry)
        return self

    def copy_to_using_path(self, decoded_url: str, bover_write: bool) -> Self:
        """CopyToUsingPath operation.

        Args:
            decoded_url (str):
                DecodedUrl parameter
            bover_write (bool):
                bOverWrite parameter
        """
        qry = ServiceOperationQuery(
            self, "CopyToUsingPath", None, {"DecodedUrl": decoded_url, "bOverWrite": bover_write}, None, None
        )
        self.context.add_query(qry)
        return self

    def delete_with_parameters(self, parameters: FileDeleteParameters) -> Self:
        """DeleteWithParameters operation.

        Args:
            parameters (FileDeleteParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "DeleteWithParameters", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def execute_cobalt_request(self, input_stream: bytes) -> ClientResult[bytes]:
        """ExecuteCobaltRequest operation.

        Args:
            input_stream (bytes):
                inputStream parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = ServiceOperationQuery(self, "ExecuteCobaltRequest", None, {"inputStream": input_stream}, None, return_type)
        self.context.add_query(qry)
        return return_type

    @staticmethod
    def get_content_ver_from_tag(context: ClientContext, content_tag: str) -> ClientResult[int]:
        """GetContentVerFromTag operation.

        Args:
            content_tag (str):
                contentTag parameter
        """
        from office365.sharepoint.files.file import File

        return_type = ClientResult(context, int())
        qry = FunctionQuery(File(context), "GetContentVerFromTag", [content_tag], return_type)
        context.add_query(qry)
        return return_type

    def get_file_user_value(self, key: str) -> ClientResult[OfficeFileUserValueResponse]:
        """GetFileUserValue operation.

        Args:
            key (str):
                key parameter
        """
        from office365.sharepoint.activities.officefileuservalueresponse import (
            OfficeFileUserValueResponse,
        )

        return_type = ClientResult(self.context, OfficeFileUserValueResponse())
        qry = ServiceOperationQuery(self, "GetFileUserValue", None, {"key": key}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_media_service_metadata(self) -> ClientResult[MediaServiceUpdateParameters]:
        """GetMediaServiceMetadata operation."""
        from office365.sharepoint.approvals.mediaserviceupdateparameters import (
            MediaServiceUpdateParameters,
        )

        return_type = ClientResult(self.context, MediaServiceUpdateParameters())
        qry = ServiceOperationQuery(self, "GetMediaServiceMetadata", None, {}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_pre_authorized_access_url2(self, expiration_hours: int, expiration_minuites: int) -> ClientResult[str]:
        """GetPreAuthorizedAccessUrl2 operation.

        Args:
            expiration_hours (int):
                expirationHours parameter
            expiration_minuites (int):
                expirationMinuites parameter
        """
        return_type = ClientResult(self.context, str())
        qry = FunctionQuery(self, "GetPreAuthorizedAccessUrl2", [expiration_hours, expiration_minuites], return_type)
        self.context.add_query(qry)
        return return_type

    def move_to(self, new_url: str, flags: int) -> Self:
        """MoveTo operation.

        Args:
            new_url (str):
                newUrl parameter
            flags (int):
                flags parameter
        """
        qry = ServiceOperationQuery(self, "MoveTo", None, {"newUrl": new_url, "flags": flags}, None, None)
        self.context.add_query(qry)
        return self

    def open_binary_stream_with_options(self, open_options: int) -> ClientResult[bytes]:
        """OpenBinaryStreamWithOptions operation.

        Args:
            open_options (int):
                openOptions parameter
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "OpenBinaryStreamWithOptions", [open_options], return_type, return_raw_content=True)
        self.context.add_query(qry)
        return return_type

    def recycle_with_e_tag(self, etag_match: str) -> ClientResult[UUID]:
        """RecycleWithETag operation.

        Args:
            etag_match (str):
                etagMatch parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "RecycleWithETag", None, {"etagMatch": etag_match}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def recycle_with_parameters(self, parameters: FileDeleteParameters) -> ClientResult[UUID]:
        """RecycleWithParameters operation.

        Args:
            parameters (FileDeleteParameters):
                parameters parameter
        """
        return_type = ClientResult(self.context, UUID(int=0))
        qry = ServiceOperationQuery(self, "RecycleWithParameters", None, {"parameters": parameters}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_expiration_date(self, expiration_date: datetime) -> Self:
        """SetExpirationDate operation.

        Args:
            expiration_date (datetime):
                expirationDate parameter
        """
        qry = ServiceOperationQuery(self, "SetExpirationDate", None, {"expirationDate": expiration_date}, None, None)
        self.context.add_query(qry)
        return self

    def set_file_user_value(self, key: str, value: str) -> ClientResult[OfficeFileUserValueResponse]:
        """SetFileUserValue operation.

        Args:
            key (str):
                key parameter
            value (str):
                value parameter
        """
        from office365.sharepoint.activities.officefileuservalueresponse import (
            OfficeFileUserValueResponse,
        )

        return_type = ClientResult(self.context, OfficeFileUserValueResponse())
        qry = ServiceOperationQuery(self, "SetFileUserValue", None, {"key": key, "value": value}, None, return_type)
        self.context.add_query(qry)
        return return_type

    def set_media_service_metadata(self, parameters: MediaServiceUpdateParameters) -> Self:
        """SetMediaServiceMetadata operation.

        Args:
            parameters (MediaServiceUpdateParameters):
                parameters parameter
        """
        qry = ServiceOperationQuery(self, "SetMediaServiceMetadata", None, {"parameters": parameters}, None, None)
        self.context.add_query(qry)
        return self

    def undo_check_out(self) -> Self:
        """UndoCheckOut operation."""
        qry = ServiceOperationQuery(self, "UndoCheckOut", None, {}, None, None)
        self.context.add_query(qry)
        return self

    def un_publish(self, comment: str) -> Self:
        """UnPublish operation.

        Args:
            comment (str):
                comment parameter
        """
        qry = ServiceOperationQuery(self, "UnPublish", None, {"comment": comment}, None, None)
        self.context.add_query(qry)
        return self

    def update_virus_info(self, virus_status: int, virus_message: str, etag_to_check: str) -> Self:
        """UpdateVirusInfo operation.

        Args:
            virus_status (int):
                virusStatus parameter
            virus_message (str):
                virusMessage parameter
            etag_to_check (str):
                etagToCheck parameter
        """
        qry = ServiceOperationQuery(
            self,
            "UpdateVirusInfo",
            None,
            {"virusStatus": virus_status, "virusMessage": virus_message, "etagToCheck": etag_to_check},
            None,
            None,
        )
        self.context.add_query(qry)
        return self
