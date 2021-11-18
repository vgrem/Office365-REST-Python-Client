import json

import requests
from requests.structures import CaseInsensitiveDict

from office365.runtime.client_request import ClientRequest
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions


class ODataV4BatchRequest(ClientRequest):
    """ JSON batch request """

    def __init__(self, context):
        super(ODataV4BatchRequest, self).__init__(context)

    def build_request(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        url = "{0}/$batch".format(self.context.service_root_url())
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.ensure_header('Content-Type', "application/json")
        request.ensure_header('Accept', "application/json")
        request.data = self._prepare_payload()
        return request

    def process_response(self, batch_response):
        """Parses an HTTP response.

        :type batch_response: requests.Response
        """
        for query_id, resp in self._extract_response(batch_response):
            resp.raise_for_status()
            sub_qry = self.current_query.ordered_queries[query_id]
            self.context.pending_request().add_query(sub_qry)
            self.context.pending_request().process_response(resp)
        self.context.pending_request().clear()

    def _extract_response(self, batch_response):
        """
        type batch_response: requests.Response
        """
        json_responses = batch_response.json()
        for json_resp in json_responses["responses"]:
            resp = requests.Response()
            resp.status_code = int(json_resp['status'])
            resp.headers = CaseInsensitiveDict(json_resp['headers'])
            resp._content = json.dumps(json_resp["body"]).encode('utf-8')
            yield int(json_resp["id"]), resp

    def _prepare_payload(self):
        """
        Serializes a batch request body.
        """

        requests_json = []
        for qry in self.current_query.queries:
            request_id = str(len(requests_json))
            request = qry.build_request()
            requests_json.append(self._normalize_request(request, request_id))

        return {"requests": requests_json}

    def _normalize_request(self, request, _id, depends_on=None):
        """

        :type request: RequestOptions
        :type _id: str
        :type depends_on:  list[str] or None
        """
        allowed_props = ["id", "method", "headers", "url", "body"]
        request_json = dict((k, v) for k, v in vars(request).items() if v is not None and k in allowed_props)
        request_json["id"] = _id
        if depends_on is not None:
            request_json["dependsOn"] = depends_on
        request_json["url"] = request_json["url"].replace(self.context.service_root_url(), "")
        return request_json

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.batch_query.BatchQuery
        """
        return self._current_query
