from __future__ import annotations

from email.message import Message
from typing import IO, Mapping, Union

from office365.directory.permissions.require_permission import require_permission
from office365.entity_collection import EntityCollection
from office365.onenote.pages.page import OnenotePage
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.mime import get_mime_type
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.batch import create_boundary
from office365.runtime.queries.client_query import ClientQuery

#: A page or attachment part: a file-like object, raw bytes, or a string of HTML.
PageSource = Union[IO, bytes, bytearray, str]

_DEFAULT_PRESENTATION_TYPE = "text/html"
_DEFAULT_ATTACHMENT_TYPE = "application/octet-stream"


def _message_to_payload(message: Message) -> bytes:
    lf = b"\n"
    crlf = b"\r\n"
    payload = message.as_bytes()
    lines = payload.split(lf)
    payload = bytes.join(crlf, lines[2:]) + crlf
    return payload


def _attach_part(message: Message, name: str, source: PageSource, default_content_type: str) -> None:
    """Attach one multipart part, reading in-memory (``bytes``/``str``) or file-like content."""
    if isinstance(source, str):
        content, file_name = source.encode("utf-8"), ""
    elif isinstance(source, (bytes, bytearray)):
        content, file_name = bytes(source), ""
    else:
        content, file_name = source.read(), (getattr(source, "name", None) or "")
    content_type, _encoding = get_mime_type(file_name)
    part = Message()
    part.add_header("Content-Type", content_type or default_content_type)
    part.add_header("Content-Disposition", f'form-data; name="{name}"')
    part.set_payload(content)
    message.attach(part)


class OnenotePageCollection(EntityCollection[OnenotePage]):
    """A collection of pages in a OneNote notebook"""

    def __init__(self, context, resource_path=None):
        super().__init__(context, OnenotePage, resource_path)

    @require_permission(
        delegated=["Notes.Create", "Notes.ReadWrite", "Notes.ReadWrite.All"], application=["Notes.ReadWrite.All"]
    )
    def add(
        self, presentation_file: PageSource, attachment_files: Mapping[str, PageSource] | None = None
    ) -> OnenotePage:
        """Create a new OneNote page.

        Args:
            presentation_file: The page HTML — a file-like object (its ``.name`` selects the MIME
                type), raw ``bytes``, or a ``str``. Falls back to ``text/html``.
            attachment_files: Optional map from the part name referenced by the HTML
                (``data-attachment="<name>"``) to file-like, ``bytes``, or ``str`` content.
        """

        return_type = OnenotePage(self.context)
        self.add_child(return_type)
        qry = ClientQuery(self.context, binding_type=self, return_type=return_type)

        def _construct_multipart_request(request: RequestOptions) -> None:
            request.method = HttpMethod.Post
            boundary = create_boundary("PageBoundary", True)
            request.set_header("Content-Type", f"multipart/form-data; boundary={boundary}")

            main_message = Message()
            main_message.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
            main_message.set_boundary(boundary)

            _attach_part(main_message, "Presentation", presentation_file, _DEFAULT_PRESENTATION_TYPE)
            for name, file in (attachment_files or {}).items():
                _attach_part(main_message, name, file, _DEFAULT_ATTACHMENT_TYPE)

            request.data = _message_to_payload(main_message)

        self.context.add_query(qry).before_execute(_construct_multipart_request)
        return return_type
