import json

import requests
from requests.structures import CaseInsensitiveDict

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.batch_request import ODataBatchRequest


class ODataV4BatchRequest(ODataBatchRequest):
    """ JSON batch request """

    def build_request(self, query):
        """
        Builds a batch request

        :type query: office365.runtime.queries.batch.BatchQuery
        """
        url = "{0}/$batch".format(self.context.service_root_url())
        request = RequestOptions(url)
        request.method = HttpMethod.Post
        request.ensure_header('Content-Type', "application/json")
        request.ensure_header('Accept', "application/json")
        request.data = self._prepare_payload(query)
        return request

    def process_response(self, response):
        """Parses an HTTP response.

        :type response: requests.Response
        """
        for qry, sub_response in self._extract_response(response):
            sub_response.raise_for_status()
            self.context.pending_request().add_query(qry)
            self.context.pending_request().process_response(sub_response)
            self.context.pending_request().clear()

    def _extract_response(self, response):
        """
        type batch_response: requests.Response
        """
        json_responses = response.json()
        for json_resp in json_responses["responses"]:
            resp = requests.Response()
            resp.status_code = int(json_resp['status'])
            resp.headers = CaseInsensitiveDict(json_resp['headers'])
            resp._content = json.dumps(json_resp["body"]).encode('utf-8')
            qry_id = int(json_resp["id"])
            qry = self.current_query.ordered_queries[qry_id]
            yield qry, resp

    def _prepare_payload(self, query):
        """
        Serializes a batch request body.

        :type query: office365.runtime.queries.batch.BatchQuery
        """
        requests_json = []
        for qry in query.queries:
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
