import json
from typing import Any, Dict, Iterator, List, Optional, Tuple

from requests import Response
from requests.structures import CaseInsensitiveDict

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.request import ODataRequest
from office365.runtime.queries.batch import BatchQuery
from office365.runtime.queries.client_query import ClientQuery


class ODataV4BatchRequest(ODataRequest):
    """JSON batch request"""

    def build_request(self, query):
        # type: (BatchQuery) -> RequestOptions
        """Builds a batch request"""
        request = RequestOptions(query.url)
        request.method = HttpMethod.Post
        request.ensure_header("Content-Type", "application/json")
        request.ensure_header("Accept", "application/json")
        request.data = self._prepare_payload(query)
        return request

    def process_response(self, response, query):
        # type: (Response, BatchQuery) -> None
        """Parses an HTTP response."""
        for sub_qry, sub_resp in self._extract_response(response, query):
            sub_resp.raise_for_status()
            super(ODataV4BatchRequest, self).process_response(sub_resp, sub_qry)

    @staticmethod
    def _extract_response(response, query):
        # type: (Response, BatchQuery) -> Iterator[Tuple[ClientQuery, Response]]
        """ """
        json_responses = response.json()
        for json_resp in json_responses["responses"]:
            resp = Response()
            resp.status_code = int(json_resp["status"])
            resp.headers = CaseInsensitiveDict(json_resp["headers"])
            resp._content = json.dumps(json_resp["body"]).encode("utf-8")
            qry_id = int(json_resp["id"])
            qry = query.ordered_queries[qry_id]
            yield qry, resp

    def _prepare_payload(self, query):
        """
        Serializes a batch request body.

        :type query: office365.runtime.queries.batch.BatchQuery
        """
        requests_json = []
        for qry in query.queries:
            qry_id = str(len(requests_json))
            requests_json.append(self._normalize_request(qry, qry_id))

        return {"requests": requests_json}

    @staticmethod
    def _normalize_request(query, query_id, depends_on=None):
        # type: (ClientQuery, str, Optional[List[str]]) -> Dict[str, Any]
        """ """
        request = query.build_request()
        allowed_props = ["id", "method", "headers", "url", "body"]
        request_json = dict(
            (k, v)
            for k, v in vars(request).items()
            if v is not None and k in allowed_props
        )
        request_json["id"] = query_id
        if depends_on is not None:
            request_json["dependsOn"] = depends_on
        request_json["url"] = request_json["url"].replace(
            query.context.service_root_url(), ""
        )
        return request_json
