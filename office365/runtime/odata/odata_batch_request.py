import json
import re
from office365.runtime.compat import message_from_bytes_or_string, message_as_bytes_or_string
from email.message import Message

from office365.runtime.client_request import ClientRequest
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.batch_query import BatchQuery, create_boundary


class ODataBatchRequest(ClientRequest):

    def __init__(self, context):
        super(ODataBatchRequest, self).__init__(context)

    def build_request(self):
        """
        Construct a OData v3 Batch request
        """
        url = "{0}/$batch".format(self.context.service_root_url())
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        media_type = "multipart/mixed"
        content_type = "; ".join([media_type, "boundary={0}".format(self.current_query.current_boundary)])
        request.ensure_header('Content-Type', content_type)
        request.data = self._prepare_payload()
        return request

    def process_response(self, response):
        """
        Parses an HTTP response.

        :type response: requests.Response
        """
        content_id = 0
        for response_info in self._read_response(response):
            if response_info["content"] is not None:
                qry = self.current_query.get(content_id)
                self.context.pending_request().map_json(response_info["content"], qry.return_type)
                content_id += 1

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

        message = message_from_bytes_or_string(http_body)  # type: Message
        for raw_response in message.get_payload():
            if raw_response.get_content_type() == "application/http":
                yield self._deserialize_response(raw_response)

    def _prepare_payload(self):
        """
        Serializes a batch request body.
        """
        main_message = Message()
        main_message.add_header("Content-Type", "multipart/mixed")
        main_message.set_boundary(self.current_query.current_boundary)

        if self.current_query.has_change_sets:
            change_set_message = Message()
            change_set_boundary = create_boundary("changeset_", True)
            change_set_message.add_header("Content-Type", "multipart/mixed")
            change_set_message.set_boundary(change_set_boundary)

            for qry in self.current_query.change_sets:
                request = qry.build_request()
                message = self._serialize_request(request)
                change_set_message.attach(message)
            main_message.attach(change_set_message)

        for qry in self.current_query.get_queries:
            request = qry.build_request()
            message = self._serialize_request(request)
            main_message.attach(message)

        return message_as_bytes_or_string(main_message)

    @staticmethod
    def _normalize_headers(headers_raw):
        headers = {}
        for header_line in headers_raw:
            k, v = header_line.split(":", 1)
            headers[k] = v
        return headers

    def _deserialize_response(self, raw_response):
        response = raw_response.get_payload(decode=True)
        lines = list(filter(None, response.decode("utf-8").split("\r\n")))
        response_status_regex = "^HTTP/1\\.\\d (\\d{3}) (.*)$"
        status_result = re.match(response_status_regex, lines[0])
        status_info = status_result.groups()

        # validate for errors
        if int(status_info[0]) >= 400:
            raise ValueError(response)

        if status_info[1] == "No Content" or len(lines) < 3:
            headers_raw = lines[1:]
            return {
                "status": status_info,
                "headers": self._normalize_headers(headers_raw),
                "content": None
            }
        else:
            headers_raw = lines[1:-1]
            content = lines[-1]
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
        lines = ["{method} {url} HTTP/1.1".format(method=method, url=request.url)] + \
                [':'.join(h) for h in request.headers.items()]
        if request.data:
            lines.append(eol)
            lines.append(json.dumps(request.data))
        raw_content = eol + eol.join(lines) + eol
        payload = raw_content.encode('utf-8').lstrip()

        message = Message()
        message.add_header("Content-Type", "application/http")
        message.add_header("Content-Transfer-Encoding", "binary")
        message.set_payload(payload)
        return message

    @property
    def current_query(self):
        """
        :rtype: BatchQuery
        """
        return self._current_query
