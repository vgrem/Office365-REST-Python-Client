from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class ClientQuery(object):
    """Client query"""

    def __init__(self, entity_type, parameters=None):
        self._entity_type = entity_type
        self._parameters = parameters
        self._return_type = None

    @property
    def entity_type(self):
        return self._entity_type

    @property
    def parameters(self):
        return self._parameters

    @property
    def return_type(self):
        return self._return_type

    @return_type.setter
    def return_type(self, val):
        self._return_type = val

    @property
    def id(self):
        return id(self)


class CreateEntityQuery(ClientQuery):
    def __init__(self, parent_resource, parameters):
        super(CreateEntityQuery, self).__init__(parent_resource, parameters)


class ReadEntityQuery(ClientQuery):
    def __init__(self, entity_type):
        super(ReadEntityQuery, self).__init__(entity_type)


class UpdateEntityQuery(ClientQuery):
    def __init__(self, entity_type):
        super(UpdateEntityQuery, self).__init__(entity_type, entity_type)


class DeleteEntityQuery(ClientQuery):
    def __init__(self, entity_type):
        super(DeleteEntityQuery, self).__init__(entity_type)


class ServiceOperationQuery(ClientQuery):
    def __init__(self, entity_type, method_name, method_params=None, parameters=None):
        super(ServiceOperationQuery, self).__init__(entity_type, parameters)
        self._method_path = ResourcePathServiceOperation(method_name, method_params, entity_type.resourcePath)

    @property
    def method_path(self):
        return self._method_path

