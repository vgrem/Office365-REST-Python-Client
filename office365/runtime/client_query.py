from office365.runtime.odata.odata_query_options import QueryOptions
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class ClientQuery(object):
    """Client query"""

    def __init__(self, binding_type, parameter_type=None, parameter_name=None, return_type=None):
        self._binding_type = binding_type
        self._parameter_type = parameter_type
        self._parameter_name = parameter_name
        self._return_type = return_type

    @property
    def id(self):
        return id(self)

    @property
    def bindingType(self):
        return self._binding_type

    @property
    def parameterName(self):
        return self._parameter_name

    @property
    def parameterType(self):
        return self._parameter_type

    @property
    def returnType(self):
        return self._return_type


class ServiceOperationQuery(ClientQuery):
    def __init__(self, binding_type, method_name=None, method_params=None, parameter_type=None,
                 parameter_name=None, return_type=None):
        super(ServiceOperationQuery, self).__init__(binding_type, parameter_type, parameter_name, return_type)
        self._method_name = method_name
        self._method_params = method_params

    @property
    def methodUrl(self):
        return ResourcePathServiceOperation(self.methodName, self.methodParameters).to_url()

    @property
    def methodName(self):
        return self._method_name

    @property
    def methodParameters(self):
        return self._method_params


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_entity, create_info, entity_to_create):
        super(CreateEntityQuery, self).__init__(parent_entity, create_info, None, entity_to_create)


class ReadEntityQuery(ClientQuery):
    def __init__(self, entity_to_read, properties_to_include=None):
        super(ReadEntityQuery, self).__init__(entity_to_read, None, None, entity_to_read)
        if properties_to_include:
            self._query_options = QueryOptions()
            self._query_options.expand = properties_to_include
        else:
            self._query_options = entity_to_read.queryOptions

    @property
    def queryOptions(self):
        return self._query_options


class UpdateEntityQuery(ClientQuery):
    def __init__(self, entity_to_update):
        super(UpdateEntityQuery, self).__init__(entity_to_update, entity_to_update, None, None)


class DeleteEntityQuery(ClientQuery):
    def __init__(self, entity_to_delete):
        super(DeleteEntityQuery, self).__init__(entity_to_delete, None, None, None)
