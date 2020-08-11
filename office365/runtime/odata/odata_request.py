from office365.runtime.client_object import ClientObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery, DeleteEntityQuery, UpdateEntityQuery
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


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
        Executes request directly

        :param RequestOptions request: request
        :return: requests.Response
        """
        self.ensure_media_type(request)
        return super(ODataRequest, self).execute_request_direct(request)

    def ensure_media_type(self, request):
        media_type = self.json_format.get_media_type()
        request.ensure_header('Content-Type', media_type)
        request.ensure_header('Accept', media_type)

    def build_request(self):
        qry = self.context.current_query
        self.json_format.function_tag_name = None
        if isinstance(qry, ServiceOperationQuery):
            self.json_format.function_tag_name = qry.method_name
            if qry.static:
                request_url = self.context.service_root_url + '.'.join(
                    [qry.binding_type.entity_type_name, qry.method_url])
            else:
                request_url = '/'.join([qry.binding_type.resource_url, qry.method_url])
        else:
            request_url = qry.binding_type.resource_url
        request = RequestOptions(request_url)

        # set method
        request.method = HttpMethod.Get
        if isinstance(qry, DeleteEntityQuery):
            request.method = HttpMethod.Post
        elif isinstance(qry, (CreateEntityQuery, UpdateEntityQuery, ServiceOperationQuery)):
            request.method = HttpMethod.Post
            if qry.parameter_type is not None:
                request.data = self._normalize_payload(qry.parameter_type)
        return request

    def process_response(self, response):
        """
        :type response: requests.Response
        """
        qry = self.context.current_query
        result_object = qry.return_type
        if isinstance(result_object, ClientObjectCollection):
            result_object.clear()

        if response.headers.get('Content-Type', '').lower().split(';')[0] != 'application/json':
            if isinstance(result_object, ClientResult):
                result_object.value = response.content
            return

        self.map_json(response.json(), result_object, self.json_format)

    def map_json(self, json_payload, result_object, json_format=None):
        if not json_format:
            json_format = self.json_format
        if json_payload and result_object is not None:
            for k, v in self._get_property(json_payload, json_format):
                if isinstance(result_object, ClientObjectCollection) and k == json_format.collection_next_tag_name:
                    result_object.next_request_url = v
                else:
                    result_object.set_property(k, v, False)

    def _get_property(self, json, data_format):
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
                        item = {k: v for k, v in self._get_property(item, data_format)}
                    yield index, item
            else:
                for name, value in json.items():
                    if isinstance(data_format, JsonLightFormat):
                        is_valid = name != "__metadata" and not (isinstance(value, dict) and "__deferred" in value)
                    else:
                        is_valid = "@odata" not in name

                    if is_valid:
                        if isinstance(value, dict):
                            value = {k: v for k, v in self._get_property(value, data_format)}
                        yield name, value

    def _normalize_payload(self, value):
        """
        :type value: ClientValue or ClientResult  or ClientObject
        """
        qry = self.context.current_query
        if isinstance(value, ClientValueCollection):
            if isinstance(self._json_format,
                          JsonLightFormat) and self._json_format.metadata == ODataMetadataLevel.Verbose:
                value = {"results": value.to_json()}
        elif isinstance(value, ClientObject) or isinstance(value, ClientValue):
            json = value.to_json()
            for k, v in json.items():
                json[k] = self._normalize_payload(v)

            if isinstance(self._json_format,
                          JsonLightFormat) and self._json_format.metadata == ODataMetadataLevel.Verbose:
                json[self._json_format.metadata_type_tag_name] = {'type': value.entity_type_name}

            if isinstance(qry,
                          ServiceOperationQuery) and qry.parameter_name is not None:
                json = {qry.parameter_name: json}
            return json
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._normalize_payload(v)
        return value
