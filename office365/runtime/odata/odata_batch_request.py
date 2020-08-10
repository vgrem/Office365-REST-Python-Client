import json
import uuid
from email import message_from_bytes
from email.message import Message

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest


def _create_boundary(prefix):
    """Creates a string that can be used as a multipart request boundary.
    :param str prefix: String to use as the start of the boundary string
    """
    return prefix + str(uuid.uuid4())


class ODataBatchRequest(ODataRequest):

    def __init__(self, context, json_format):
        """

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat
        """
        super(ODataBatchRequest, self).__init__(context, json_format)
        media_type = "multipart/mixed"
        self._current_boundary = _create_boundary("batch_")
        self._content_type = "; ".join([media_type, "boundary={0}".format(self._current_boundary)])
        self._boundary_queries = []

    def build_request(self):
        request_url = "{0}$batch".format(self.context.service_root_url)
        request = RequestOptions(request_url)
        request.method = HttpMethod.Post
        request.ensure_header('Content-Type', self._content_type)
        request.data = self._prepare_payload()
        return request

    def process_response(self, response):
        """Parses an HTTP response.

        :type response: requests.Response
        """
        for response_info in self._read_response(response):
            qry = self._boundary_queries.pop(0)
            self.map_json(response_info["content"], qry.return_type)

    def _read_response(self, response):
        """Parses a multipart/mixed response body from from the position defined by the context.

        :type response: requests.Response
        """
        content_type = response.headers['Content-Type'].encode("ascii")
        http_body = (
            b"Content-Type: "
            + content_type
            + b"\r\n\r\n"
            + response.content
        )

        message = message_from_bytes(http_body)  # type: Message
        for raw_response in message.get_payload():
            if raw_response.get_content_type() == "application/http":
                yield self._deserialize_response(raw_response)

    def _prepare_payload(self):
        """Serializes a batch request body."""
        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        main_message.set_boundary(self._current_boundary)
        for qry in self.context.get_next_query():
            self._boundary_queries.append(qry)
            part_message = Message()
            part_message.add_header("Content-Type", "application/http")
            part_message.add_header("Content-Transfer-Encoding", "binary")
            request = self.context.build_request()
            part_message.set_payload(self._serialize_request(request))
            main_message.attach(part_message)
        return main_message.as_bytes()

    @staticmethod
    def _deserialize_response(raw_response):
        response = raw_response.get_payload(decode=True)
        lines = list(filter(None, response.decode("utf-8").split("\r\n")))
        status_info, *headers_raw, content = lines
        headers = {}
        for h in headers_raw:
            kv = h.split(":")
            headers[kv[0].lower()] = kv[1]

        content = json.loads(content)
        return {
            "headers": headers,
            "content": content
        }

    @staticmethod
    def _serialize_request(request):
        """Serializes a part of a batch request to a string. A part can be either a GET request or
            a change set grouping several CUD (create, update, delete) requests.

        :type request: RequestOptions
        """
        eol = "\r\n"
        lines = ["{method} {url} HTTP/1.1".format(method=request.method, url=request.url),
                 *[':'.join(h) for h in request.headers.items()]]
        if request.data:
            lines.append(json.dumps(request.data))
        buffer = eol + eol.join(lines) + eol
        return buffer.encode('utf-8').lstrip()
