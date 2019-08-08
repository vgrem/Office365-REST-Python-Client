import requests
from office365.runtime.action_type import ActionType
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_encoder import ODataEncoder
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions
from requests import HTTPError


class ClientRequest(object):
    """Client request for Office365 ODATA/REST service"""

    def __init__(self, context):
        self.context = context
        self.__queries = []
        self.__resultObjects = {}

    def clear(self):
        self.__queries = []
        self.__resultObjects = {}

    def execute_query(self, query=None, result_object=None):
        """Submit pending request to the server"""
        if query:
            return self.execute_single_query(query, result_object)
        return self.execute_pending_queries()

    def execute_pending_queries(self):
        try:
            for query in self.__queries:
                request = self.build_request(query)
                response = self.execute_request_direct(request)
                self.process_payload_json(query, response)
        finally:
            self.clear()

    def execute_single_query(self, query, result_object=None):
        """Submit single query to the server"""
        request = self.build_request(query)
        response = self.execute_request_direct(request)
        return self.process_payload_json(query, response, result_object)

    def process_payload_json(self, query, response, result_object=None):
        payload = self.process_response_json(response)
        result_object = result_object if result_object else self.__resultObjects.get(query)
        if result_object is not None:
            result_object.map_json(payload)

        return payload

    def process_response_json(self, response):
        self.validate_response(response)

        if not response.content or response.headers.get('Content-Type', '').lower().split(';')[0] != 'application/json':
            return

        if response.headers.get('Content-Type', '').lower().split(';')[0] == 'application/json':
            payload = response.json()
        else:
            payload = None

        if payload:
            json_format = self.context.json_format
            if json_format.security_tag_name:
                payload = payload[json_format.security_tag_name]
            if json_format.collection_tag_name in payload:
                payload = {
                    "collection": payload[json_format.collection_tag_name],
                    "next": payload.get(json_format.collection_next_tag_name, None)
                }

        return payload

    def build_request(self, query):
        request = RequestOptions(query.url)
        # set json format headers
        request.set_headers(self.context.json_format.build_http_headers())
        if isinstance(self.context.json_format, JsonLightFormat):
            # set custom method headers
            if query.action_type == ActionType.DeleteEntity:
                request.set_header("X-HTTP-Method", "DELETE")
                request.set_header("IF-MATCH", '*')
            elif query.action_type == ActionType.UpdateEntity:
                request.set_header("X-HTTP-Method", "MERGE")
                request.set_header("IF-MATCH", '*')
            # set method
            if not (query.action_type == ActionType.ReadEntity or query.action_type == ActionType.GetMethod):
                request.method = HttpMethod.Post
        else:
            if query.action_type == ActionType.CreateEntity:
                request.method = HttpMethod.Post
            elif query.action_type == ActionType.UpdateEntity:
                request.method = HttpMethod.Patch
            elif query.action_type == ActionType.DeleteEntity:
                request.method = HttpMethod.Delete
        # set request payload
        if query.payload is not None:
            request.data = ODataEncoder(self.context.json_format).default(query.payload)
        return request

    def execute_request_direct(self, request_options):
        """Execute client request"""
        self.context.authenticate_request(request_options)
        if request_options.method == HttpMethod.Post:
            from office365.sharepoint.client_context import ClientContext
            if isinstance(self.context, ClientContext):
                self.context.ensure_form_digest(request_options)
            if hasattr(request_options.data, 'decode') and callable(request_options.data.decode):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth)
            elif hasattr(request_options.data, 'read') and callable(request_options.data.read):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth)
            else:
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       json=request_options.data,
                                       auth=request_options.auth)
        elif request_options.method == HttpMethod.Patch:
            result = requests.patch(url=request_options.url,
                                    headers=request_options.headers,
                                    json=request_options.data,
                                    auth=request_options.auth)
        elif request_options.method == HttpMethod.Delete:
            result = requests.delete(url=request_options.url,
                                     headers=request_options.headers,
                                     auth=request_options.auth)
        else:
            result = requests.get(url=request_options.url,
                                  headers=request_options.headers,
                                  auth=request_options.auth)
        return result

    def add_query(self, query, result_object=None):
        self.__queries.append(query)
        if result_object is not None:
            self.__resultObjects[query] = result_object

    def validate_response(self, response):
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise ClientRequestException(*e.args, response=e.response)
