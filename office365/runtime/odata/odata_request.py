from office365.runtime.client_object import ClientObject
from office365.runtime.client_query import CreateEntityQuery, UpdateEntityQuery, DeleteEntityQuery, \
    ServiceOperationQuery
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_object import ClientValueObject
from office365.runtime.utilities.http_method import HttpMethod
from office365.runtime.utilities.request_options import RequestOptions


class ODataRequest(ClientRequest):

    def __init__(self, context):
        super(ODataRequest, self).__init__(context)
        self.__current_query = None

    def build_request(self):
        for qry in self._queries:
            request = RequestOptions(qry.entity_type.resourceUrl)
            # set json format headers
            request.set_headers(self.context.json_format.build_http_headers())
            # set method
            request.method = HttpMethod.Get
            if isinstance(qry, CreateEntityQuery) \
                or isinstance(qry, UpdateEntityQuery) \
                or isinstance(qry, DeleteEntityQuery):
                request.method = HttpMethod.Post
            elif isinstance(qry, ServiceOperationQuery):
                request.url = '/'.join([qry.entity_type.resourceUrl, qry.method_path.segment])
                request.method = HttpMethod.Post
            # set request payload
            if qry.parameters is not None:
                request.data = self._normalize_payload(qry.parameters)
            if 'before' in self._events:
                self._events['before'](request, qry)
            self.__current_query = qry
            yield request

    def _normalize_payload(self, value):
        if isinstance(value, ClientObject) or isinstance(value, ClientValueObject):
            json = value.to_json(self.context.json_format)
            for k, v in json.items():
                json[k] = self._normalize_payload(v)
            return json
        elif isinstance(value, dict):
            for k, v in value.items():
                value[k] = self._normalize_payload(v)
            return value
        return value

    def process_response(self, response):
        result_object = self.__current_query.return_type
        if response.headers.get('Content-Type', '').lower().split(';')[0] != 'application/json':
            if isinstance(result_object, ClientResult):
                result_object.value = response.content
            return

        payload = response.json()
        if payload and result_object is not None:
            json_format = self.context.json_format
            if json_format.security_tag_name:
                payload = payload[json_format.security_tag_name]
            if json_format.collection_tag_name in payload:
                payload = {
                    "collection": payload[json_format.collection_tag_name],
                    "next": payload.get(json_format.collection_next_tag_name, None)
                }
            result_object.map_json(payload)
            if 'after' in self._events:
                self._events['after'](result_object)
