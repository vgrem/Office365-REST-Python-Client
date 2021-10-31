from email.message import Message

from office365.runtime.compat import get_mime_type
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.batch_query import create_boundary
from office365.runtime.queries.client_query import ClientQuery


def _message_to_payload(message):
    """
    :type message: Message
    """
    eol = "\r\n"
    lines = message.as_string().splitlines()
    payload = str.join(eol, lines[2:]) + eol
    return str.encode(payload)


class OneNotePageCreateQuery(ClientQuery):

    def __init__(self, pages, presentation, files=None):
        """
        :type pages: office365.onenote.pages.page.OnenotePageCollection
        :type presentation: dict
        :type files: dict or None
        """
        super(OneNotePageCreateQuery, self).__init__(pages.context, pages)
        pages.context.before_execute(self._construct_multipart_request)
        self._presentation = presentation
        if files is None:
            files = {}
        self._files = files

    def _construct_multipart_request(self, request):
        """
        :type request: office365.runtime.http.request_options.RequestOptions
        """
        request.method = HttpMethod.Post
        boundary = create_boundary("PageBoundary", True)
        request.set_header("Content-Type", "multipart/form-data; boundary={0}".format(boundary))

        main_message = Message()
        main_message.add_header("Content-Type", "multipart/form-data; boundary={0}".format(boundary))
        main_message.set_boundary(boundary)

        presentation_type = get_mime_type(self._presentation.get("name"))
        presentation_message = Message()
        presentation_message.add_header("Content-Type", presentation_type[0])
        presentation_message.add_header("Content-Disposition", "form-data; name=\"Presentation\"")
        presentation_message.set_payload(self._presentation.get("content"))
        main_message.attach(presentation_message)

        for name, file_content in self._files.items():
            file_message = Message()
            file_message.add_header("Content-Type", "text/html")
            file_message.add_header("Content-Disposition", "form-data; name=\"{0}\"".format(name))
            file_message.set_payload(file_content)
            main_message.attach(file_message)

        request.data = _message_to_payload(main_message)

    @property
    def return_type(self):
        if self._return_type is None:
            from office365.onenote.pages.page import OnenotePage
            self._return_type = OnenotePage(self.context)
            self.binding_type.add_child(self._return_type)
        return self._return_type

