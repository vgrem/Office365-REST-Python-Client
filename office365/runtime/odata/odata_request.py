from office365.runtime.client_object import ClientObject
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

    def execute_request_direct(self, request):
        media_type = self.json_format.get_media_type()
        request.set_headers({'Content-Type': media_type, 'Accept': media_type})  # set OData format
        return super(ODataRequest, self).execute_request_direct(request)

    @property
    def json_format(self):
        return self._json_format

    def build_request(self):
        qry = self._get_current_query()
        request = RequestOptions(qry.bindingType.resourceUrl)
        if isinstance(qry, ServiceOperationQuery):
            request.url = '/'.join([qry.bindingType.resourceUrl, qry.methodUrl])

        # set json format headers
        media_type = self.json_format.get_media_type()
        request.set_headers({'Content-Type': media_type, 'Accept': media_type})
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
        qry = self._get_current_query()
        result_object = qry.returnType

        if response.headers.get('Content-Type', '').lower().split(';')[0] != 'application/json':
            if isinstance(result_object, ClientResult):
                result_object.value = response.content
            return

        payload = response.json()
        if payload and result_object is not None:
            if self.json_format.security_tag_name:
                payload = payload[self.json_format.security_tag_name]
            if isinstance(qry, ServiceOperationQuery):
                if qry.methodName in payload:
                    payload = payload[qry.methodName]
            if self.json_format.collection_tag_name in payload:
                next_link_url = payload.get(self.json_format.collection_next_tag_name, None)
                payload = payload[self.json_format.collection_tag_name]
            result_object.map_json(payload)

    def _normalize_payload(self, value):
        if isinstance(value, ClientObject) or isinstance(value, ClientValueObject):
            json = value.to_json()
            for k, v in json.items():
                json[k] = self._normalize_payload(v)

            include_metadata = isinstance(self._json_format, JsonLightFormat) \
                               and self._json_format.metadata == ODataMetadataLevel.Verbose
            if include_metadata:
                json["__metadata"] = {'type': value.entityTypeName}
            qry = self._get_current_query()
            if isinstance(qry, ServiceOperationQuery) and qry.parameterName is not None:
                json = {qry.parameterName: json}
            return json
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._normalize_payload(v)
        return value
