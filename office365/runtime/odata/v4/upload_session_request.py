from __future__ import annotations

import os
from typing import IO, Callable, Optional

from requests import Response

from office365.runtime.client_request import ClientRequest
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.transport.offload import get_offload_executor, run_offloaded


class UploadSessionRequest(ClientRequest):
    """Handles file uploads in chunks using upload sessions."""

    def __init__(
        self,
        file_object: IO,
        chunk_size: int,
        chunk_uploaded: Callable[[int], None] | None = None,
        upload_url: str | None = None,
        file_size: int | None = None,
    ) -> None:
        """Initialize an upload session request.

        Args:
            file_object: The file-like object to upload
            chunk_size: Size of each upload chunk in bytes
            chunk_uploaded: Callback invoked after each chunk is uploaded
            upload_url: Explicit upload-session URL (when the session was created
              outside of an ``UploadSessionQuery``, e.g. Microsoft To Do)
            file_size: Total size override (for streams without a file descriptor)
        """
        super().__init__()
        self._file_object = file_object
        self._chunk_size = chunk_size
        self._chunk_uploaded = chunk_uploaded
        self._upload_url = upload_url
        self._file_size = file_size
        self._range_data: Optional[bytes] = None
        self.last_response: Response | None = None

    @property
    def service_root_url(self) -> str:
        return ""

    def build_request(self, query: ClientQuery) -> RequestOptions:
        """Build a request for uploading a single chunk."""
        assert self._range_data is not None
        upload_url = self._upload_url or getattr(query, "upload_session_url", None)
        assert upload_url is not None
        request = RequestOptions(upload_url)
        request.method = HttpMethod.Put
        request.set_header("Content-Length", str(len(self._range_data)))
        request.set_header(
            "Content-Range",
            f"bytes {self.range_start}-{self.range_end - 1}/{self.file_size}",
        )
        request.set_header("Accept", "*/*")
        request.data = self._range_data
        return request

    def handle_response(self, response: Response, query: ClientQuery) -> None:
        """Handle the response after uploading a chunk."""
        response.raise_for_status()
        self.last_response = response
        if callable(self._chunk_uploaded):
            self._chunk_uploaded(self.range_end)

    def execute_query(self, query: ClientQuery) -> None:
        """Execute the upload query for each chunk."""
        for chunk_data in self._read_next():
            self._range_data = chunk_data
            super().execute_query(query)

    async def execute_query_async(self, query: ClientQuery) -> None:
        """Execute the upload query for each chunk without blocking the loop.

        Async twin of :meth:`execute_query`: every chunk is read from the source
        stream on the shared offload executor and PUT through the async
        transport, so neither the disk read nor the upload stalls the event
        loop. Chunks are still uploaded sequentially, in order, as the service
        requires.
        """
        executor = get_offload_executor()
        while True:
            chunk_data = await run_offloaded(self._file_object.read, self._chunk_size, executor=executor)
            if not chunk_data:
                break
            self._range_data = chunk_data
            await super().execute_query_async(query)

    def _read_next(self):
        """Generate fixed-size chunks from the file object.

        Yields:
            bytes: Chunks of data with maximum size of self._chunk_size
        """
        while True:
            chunk = self._file_object.read(self._chunk_size)
            if not chunk:
                break
            yield chunk

    @property
    def file_size(self) -> int:
        """Get the total size of the file being uploaded."""
        if self._file_size is not None:
            return self._file_size
        try:
            return os.fstat(self._file_object.fileno()).st_size
        except (AttributeError, OSError):
            pos = self._file_object.tell()
            self._file_object.seek(0, os.SEEK_END)
            size = self._file_object.tell()
            self._file_object.seek(pos)
            return size

    @property
    def range_start(self) -> int:
        """Get the starting byte position of the current chunk."""
        if self.range_end == 0:
            return 0
        assert self._range_data is not None
        return self.range_end - len(self._range_data)

    @property
    def range_end(self) -> int:
        """Get the ending byte position of the current chunk."""
        return self._file_object.tell()
