from office365.runtime.client_object import ClientObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.v3.json_light_format import JsonLightFormat
from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery


class ODataRequest(ClientRequest):

    def __init__(self, context, json_format):
        """

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat
        """
        super(ODataRequest, self).__init__(context)
        self._json_format = json_format

    @property
    def json_format(self):
        return self._json_format

    def execute_request_direct(self, request):
        """

        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self.ensure_media_type(request)
        return super(ODataRequest, self).execute_request_direct(request)

    def build_request(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        self._current_query = query

        request = RequestOptions(query.url)
        self.ensure_media_type(request)
        # set method
        request.method = HttpMethod.Get
        if isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Post
        elif isinstance(query, (CreateEntityQuery, UpdateEntityQuery, ServiceOperationQuery)):
            request.method = HttpMethod.Post
            if query.parameter_type is not None:
                request.data = self._normalize_payload(query.parameter_type)
        return request

    def ensure_media_type(self, request):
        """
        :type request: RequestOptions
        """
        media_type = self.json_format.get_media_type()
        request.ensure_header('Content-Type', media_type)
        request.ensure_header('Accept', media_type)

    def process_response(self, response):
        """
        :type response: requests.Response
        """
        query = self.context.current_query
        return_type = query.return_type
        if return_type is None:
            return

        if isinstance(return_type, ClientObject):
            return_type.clear()

        if response.headers.get('Content-Type', '').lower().split(';')[0] != 'application/json':
            if isinstance(return_type, ClientResult):
                return_type.value = response.content
        else:
            if isinstance(query, ServiceOperationQuery):
                self.json_format.function_tag_name = query.method_name

            if isinstance(return_type, ClientResult):
                if isinstance(return_type.value, ClientValue) or isinstance(return_type.value, ClientObject):
                    return_type = return_type.value
            self.map_json(response.json(), return_type, self.json_format)
            self.json_format.function_tag_name = None

    def map_json(self, json, return_type, json_format=None):
        """
        :type json: any
        :type return_type: ClientValue or ClientResult  or ClientObject
        :type json_format: office365.runtime.odata.odata_json_format.ODataJsonFormat
        """
        if json_format is None:
            json_format = self.json_format

        if json and return_type is not None:
            for k, v in self._next_property(json, json_format):
                if isinstance(return_type, ClientResult):
                    return_type.value = v
                elif isinstance(return_type, ClientObjectCollection) and k == json_format.collection_next_tag_name:
                    return_type.next_request_url = v
                else:
                    return_type.set_property(k, v, False)

    def _next_property(self, json, data_format):
        """
        :type json: any
        :type data_format: office365.runtime.odata.odata_json_format.ODataJsonFormat
        """
        if isinstance(data_format, JsonLightFormat):
            json = json.get(data_format.security_tag_name, json)
            json = json.get(data_format.function_tag_name, json)

        if not isinstance(json, dict):
            yield "value", json
        else:
            next_link_url = json.get(self.json_format.collection_next_tag_name, None)
            json = json.get(data_format.collection_tag_name, json)
            if next_link_url:
                yield self.json_format.collection_next_tag_name, next_link_url

            if isinstance(json, list):
                for index, item in enumerate(json):
                    if isinstance(item, dict):
                        item = {k: v for k, v in self._next_property(item, data_format)}
                    yield index, item
            else:
                for name, value in json.items():
                    if isinstance(data_format, JsonLightFormat):
                        is_valid = name != "__metadata" and not (isinstance(value, dict) and "__deferred" in value)
                    else:
                        is_valid = "@odata" not in name

                    if is_valid:
                        if isinstance(value, dict):
                            value = {k: v for k, v in self._next_property(value, data_format)}
                        yield name, value

    def _normalize_payload(self, value):
        """
        Normalizes OData request payload

        :type value: ClientObject or ClientValue or dict or list or str
        """
        if isinstance(value, ClientObject) or isinstance(value, ClientValue):
            json = value.to_json(self._json_format)
            query = self.current_query
            if isinstance(query, ServiceOperationQuery) and query.parameter_name is not None:
                return {query.parameter_name: json}
            return json
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._normalize_payload(v)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                value[i] = self._normalize_payload(item)
        return value
