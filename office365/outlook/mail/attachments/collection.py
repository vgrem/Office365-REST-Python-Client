from __future__ import annotations

import base64
from typing import TYPE_CHECKING, Callable, Optional

import requests

from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.outlook.mail.attachments.attachment import Attachment
from office365.outlook.mail.attachments.attachment_item import AttachmentItem
from office365.runtime.client_result import ClientResult
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.http.url import parse_query_param
from office365.runtime.odata.v4.upload_session import UploadSession
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.upload_session import UploadSessionQuery

if TYPE_CHECKING:
    from office365.graph_client import GraphClient


class AttachmentCollection(EntityCollection[Attachment]):
    """Attachment collection"""

    def __init__(self, context: GraphClient, resource_path: Optional[ResourcePath] = None) -> None:
        super().__init__(context, Attachment, resource_path)

    @require_permission(delegated=["Mail.ReadWrite"], application=["Mail.ReadWrite"])
    def add_file(
        self,
        name: str,
        content: bytes | str | None = None,
        content_type: str | None = None,
    ):
        """Build a FileAttachment and register it as a child (inline attachments).

        Use this for a draft that is about to be created. For an existing message
        use :meth:`Message.add_file_attachment`, which POSTs the file to the
        message's ``attachments`` collection instead.

        Args:
            name (str): The name of the file.
            content (str or bytes): The file content — text (str) or raw bytes.
            content_type (str or None): The content type of the attachment.

        Returns:
            The built FileAttachment.
        """
        attachment = self.create_file(name, content, content_type)
        self.add_child(attachment)
        return attachment

    def create_file(
        self,
        name: str,
        content: bytes | str | None = None,
        content_type: str | None = None,
    ):
        """Build a FileAttachment without registering it (for a direct create).

        Args:
            name (str): The name of the file.
            content (str or bytes): The file content — text (str) or raw bytes.
            content_type (str or None): The content type of the attachment.
        """
        if not content:
            raise TypeError("Content is required")
        from office365.outlook.mail.attachments.file import FileAttachment

        raw = content.encode("utf-8") if isinstance(content, str) else content
        return_type = FileAttachment(self.context)
        return_type.name = name
        return_type.content_bytes = base64.b64encode(raw)
        if content_type:
            return_type.content_type = content_type
        return return_type

    def resumable_upload(
        self,
        source_path: str,
        chunk_size: int = 1000000,
        chunk_uploaded: Callable[[int], None] | None = None,
    ):
        """Create an upload session to allow your app to upload files up to the maximum file size.
        An upload session allows your app to upload ranges of the file in sequential API requests,
        which allows the transfer to be resumed if a connection is dropped while the upload is in progress.

        Args:
            source_path (str): Local file path
            chunk_size (int): File chunk size
            chunk_uploaded ((int)->None): Upload action
        """
        from office365.outlook.mail.attachments.attachment_item import AttachmentItem
        from office365.outlook.mail.attachments.file import FileAttachment

        return_type = FileAttachment(self.context)
        self.add_child(return_type)

        qry = UploadSessionQuery(self, {"AttachmentItem": AttachmentItem.create_file(source_path)})

        def _start_upload(result: ClientResult[UploadSession]) -> None:
            with open(source_path, "rb") as local_file:
                session_request = UploadSessionRequest(local_file, chunk_size, chunk_uploaded)

                def _construct_request(request: RequestOptions) -> None:
                    auth_token = parse_query_param(request.url, "authtoken")
                    request.set_header("Authorization", f"Bearer {auth_token}")

                def _handle_response(response: requests.Response) -> None:
                    location = response.headers.get("Location", None)
                    if location is None:
                        return
                    attachment_id = location[location.find("Attachments(") + 13 : -2]
                    return_type.set_property("id", attachment_id)

                session_request.beforeExecute += _construct_request
                session_request.afterExecute += _handle_response
                session_request.execute_query(qry)

        self.context.add_query(qry).after_execute(_start_upload, execute_first=True)
        return self

    @require_permission(
        delegated=["Mail.ReadWrite"],
        application=["Mail.ReadWrite"],
        notes="Create an upload session for attaching a large file",
    )
    def create_upload_session(self, attachment_item: AttachmentItem) -> ClientResult[UploadSession]:
        """Create an upload session that allows an app to iteratively upload ranges of a file,
        so as to attach the file to the specified Outlook item. The item can be a message or event.

        Args:
            attachment_item (office365.mail.attachment_item.AttachmentItem):
        """
        qry = UploadSessionQuery(self, {"AttachmentItem": attachment_item})
        self.context.add_query(qry)
        return qry.return_type
