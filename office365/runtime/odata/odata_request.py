from office365.runtime.client_object import ClientObject
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery, UpdateEntityQuery, DeleteEntityQuery, \
    ServiceOperationQuery
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_object import ClientValueObject
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_light_format import JsonLightFormat
from office365.runtime.odata.odata_metadata_level import ODataMetadataLevel


class ODataRequest(ClientRequest):

    def __init__(self, context, json_format):
        super(ODataRequest, self).__init__(context)
        self._json_format = json_format
        self._current_query = None

    def execute_request_direct(self, request):
        media_type = self.json_format.get_media_type()
        request.ensure_headers({'Content-Type': media_type, 'Accept': media_type})  # set OData format
        return super(ODataRequest, self).execute_request_direct(request)

    @property
    def current_query(self):
        return self._current_query

    @property
    def json_format(self):
        return self._json_format

    def _get_next_query(self):
        self._current_query = self._queries.pop(0)
        return self._current_query

    def build_request(self):
        qry = self._get_next_query()
        self.json_format.function_tag_name = None

        if isinstance(qry, ServiceOperationQuery):
            self.json_format.function_tag_name = qry.methodName
            if qry.static:
                request_url = self.context.serviceRootUrl + '.'.join([qry.bindingType.entityTypeName, qry.methodUrl])
            else:
                request_url = '/'.join([qry.bindingType.resourceUrl, qry.methodUrl])
        else:
            request_url = qry.bindingType.resourceUrl
        request = RequestOptions(request_url)

        # set method
        request.method = HttpMethod.Get
        if isinstance(qry, DeleteEntityQuery):
            request.method = HttpMethod.Post
        elif isinstance(qry, CreateEntityQuery) \
            or isinstance(qry, UpdateEntityQuery) \
            or isinstance(qry, ServiceOperationQuery):
            request.method = HttpMethod.Post
            if qry.parameterType is not None:
                request.data = self._normalize_payload(qry.parameterType)
        return request

    def process_response(self, response):
        result_object = self._current_query.returnType
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
        if isinstance(value, ClientObject) or isinstance(value, ClientValueObject):
            json = value.to_json()
            for k, v in json.items():
                json[k] = self._normalize_payload(v)

            if isinstance(self._json_format,
                          JsonLightFormat) and self._json_format.metadata == ODataMetadataLevel.Verbose:
                json["__metadata"] = {'type': value.entityTypeName}

            if isinstance(self._current_query, ServiceOperationQuery) and self._current_query.parameterName is not None:
                json = {self._current_query.parameterName: json}
            return json
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._normalize_payload(v)
        return value
