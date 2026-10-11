from __future__ import annotations

import io
import os
from datetime import datetime
from os import PathLike
from typing import IO, Optional, Union

from office365.entity import Entity
from office365.runtime.odata.v4.upload_session_request import UploadSessionRequest
from office365.runtime.operations import Progress, ProgressCallback
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.todo.attachments.task_file import TaskFileAttachment

DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024


class AttachmentSession(Entity):
    """Represents a resource that uploads large attachments to a todoTask."""

    @property
    def upload_url(self) -> Optional[str]:
        """The URL that allows uploading ranges of bytes to the attachment."""
        return self.properties.get("uploadUrl", None)

    @property
    def content(self):
        """The content streams that are uploaded."""
        return self.properties.get("content", None)

    @odata(name="expirationDateTime")
    @property
    def expiration_datetime(self) -> datetime:
        """The date and time in UTC when the upload session will expire.
        The complete file must be uploaded before this expiration time is reached."""
        return self.properties.get("expirationDateTime", datetime.min)

    @odata(name="nextExpectedRanges")
    @property
    def next_expected_ranges(self) -> StringCollection:
        """Indicates a single value {start} that represents the location in the file where the next
        upload should begin."""
        return self.properties.get("nextExpectedRanges", StringCollection())

    def upload(
        self,
        source: Union[str, PathLike, bytes, bytearray, IO],
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        progress: Optional[ProgressCallback] = None,
    ) -> TaskFileAttachment:
        """Upload a file (path, bytes, or stream) to this session and return the created attachment.

        Ranges are sent sequentially (``PUT`` with ``Content-Range``) until the whole
        file is uploaded, as required by the Microsoft Graph upload-session contract.

        Args:
            source: Path, raw bytes, or a binary stream.
            chunk_size: Maximum bytes per ``PUT`` (4 MB by default).
            progress: Optional hook invoked per chunk with a ``Progress`` snapshot.
        """
        auto_close = False
        if isinstance(source, (str, PathLike)):
            file_object: IO = open(source, "rb")
            file_size: Optional[int] = os.path.getsize(source)
            auto_close = True
        elif isinstance(source, (bytes, bytearray)):
            file_object = io.BytesIO(bytes(source))
            file_size = len(source)
        else:
            file_object = source
            file_size = None

        def _chunk_uploaded(uploaded: int) -> None:
            if callable(progress):
                progress(Progress(done=uploaded, total=file_size, stage="uploading"))

        request = UploadSessionRequest(
            file_object,
            chunk_size,
            chunk_uploaded=_chunk_uploaded,
            upload_url=self.upload_url,
            file_size=file_size,
        )
        request.transport = self.context.pending_request().transport
        try:
            request.execute_query(ClientQuery(self.context))
        finally:
            if auto_close and not file_object.closed:
                file_object.close()

        attachment = TaskFileAttachment(self.context)
        response = request.last_response
        if response is not None and response.content:
            try:
                payload = response.json()
            except ValueError:
                payload = {}
            for key, value in payload.items():
                attachment.set_property(key, value, False)
        return attachment

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttachmentSession"
