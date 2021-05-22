from office365.runtime.client_request import ClientRequest
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.batch_query import BatchQuery


class ODataV4BatchRequest(ClientRequest):
    """

    """

    def __init__(self, context):
        super().__init__(context)

    def build_request(self, query):
        """

        :type query: BatchQuery
        """
        url = "{0}$batch".format(self.context.service_root_url())
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.ensure_header('Content-Type', "application/json")
        request.ensure_header('Accept', "application/json")
        request.data = self._prepare_payload(query)
        return request

    def process_response(self, response, query):
        """Parses an HTTP response.

        :type response: requests.Response
        :type query: office365.runtime.queries.client_query.BatchQuery
        """
        json = response.json()
        for resp in json["responses"]:
            sub_qry = query.get(int(resp["id"]))
            self.context.pending_request().map_json(resp["body"], sub_qry.return_type)

    def _prepare_payload(self, query):
        """Serializes a batch request body.

        :type query: office365.runtime.queries.client_query.BatchQuery
        """

        requests_json = []
        for qry in query.queries:
            request = qry.build_request()
            requests_json.append(self._serialize_request(request, len(requests_json)))

        return {"requests": requests_json}

    def _serialize_request(self, request, request_no):
        allowed_props = ["id", "method", "headers", "url", "body"]
        json = dict((k, v) for k, v in vars(request).items() if v is not None and k in allowed_props)
        json["id"] = str(request_no)
        json["url"] = json["url"].replace(self.context.service_root_url(), "/")
        return json
