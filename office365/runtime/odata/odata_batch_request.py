import json
import re
import uuid
from email import message_from_bytes
from email.message import Message

from office365.runtime.client_query import ReadEntityQuery
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest


def _create_boundary(prefix, compact=False):
    """Creates a string that can be used as a multipart request boundary.
    :param str prefix: String to use as the start of the boundary string
    """
    if compact:
        return prefix + str(uuid.uuid4())[:8]
    else:
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
        self._get_requests = []
        self._change_requests = []
        self._get_queries = []

    def build_request(self):
        request_url = "{0}$batch".format(self.context.service_root_url)
        request = RequestOptions(request_url)
        request.method = HttpMethod.Post
        request.ensure_header('Content-Type', self._content_type)
        request.data = self._prepare_payload().as_bytes()
        return request

    def process_response(self, response):
        """Parses an HTTP response.

        :type response: requests.Response
        """
        for response_info in self._read_response(response):
            if response_info["content"] is not None:
                qry = self._get_queries.pop(0)
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

        for qry in self.context.get_next_query():
            request = self.context.build_request()
            if isinstance(qry, ReadEntityQuery):
                self._get_requests.append(request)
                self._get_queries.append(qry)
            else:
                self._change_requests.append(request)

        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        main_message.set_boundary(self._current_boundary)

        if len(self._change_requests) > 0:
            change_set_message = Message()
            change_set_boundary = _create_boundary("changeset_", True)
            change_set_message.add_header("Content-Type", "multipart/mixed")
            change_set_message.set_boundary(change_set_boundary)

            for request in self._change_requests:
                part_message = self._serialize_request(request)
                change_set_message.attach(part_message)
            main_message.attach(change_set_message)

        for request in self._get_requests:
            part_message = self._serialize_request(request)
            main_message.attach(part_message)

        return main_message

    @staticmethod
    def _normalize_headers(headers_raw):
        return dict(kv.split(":") for kv in headers_raw)

    def _deserialize_response(self, raw_response):
        response = raw_response.get_payload(decode=True)
        lines = list(filter(None, response.decode("utf-8").split("\r\n")))
        response_status_regex = "^HTTP/1\\.\\d (\\d{3}) (.*)$"
        status_result = re.match(response_status_regex, lines[0])
        status_info = status_result.groups()

        if status_info[1] == "No Content" or len(lines) < 3:
            headers_raw = lines[1:]
            return {
                "status": status_info,
                "headers": self._normalize_headers(headers_raw),
                "content": None
            }
        else:
            *headers_raw, content = lines[1:]
            content = json.loads(content)
            return {
                "status": status_info,
                "headers": self._normalize_headers(headers_raw),
                "content": content
            }

    @staticmethod
    def _serialize_request(request):
        """Serializes a part of a batch request to a string. A part can be either a GET request or
            a change set grouping several CUD (create, update, delete) requests.

        :type request: RequestOptions
        """
        eol = "\r\n"
        method = request.method
        if "X-HTTP-Method" in request.headers:
            method = request.headers["X-HTTP-Method"]
        lines = ["{method} {url} HTTP/1.1".format(method=method, url=request.url),
                 *[':'.join(h) for h in request.headers.items()]]
        if request.data:
            lines.append(eol)
            lines.append(json.dumps(request.data))
        buffer = eol + eol.join(lines) + eol
        payload = buffer.encode('utf-8').lstrip()

        message = Message()
        message.add_header("Content-Type", "application/http")
        message.add_header("Content-Transfer-Encoding", "binary")
        message.set_payload(payload)
        return message
