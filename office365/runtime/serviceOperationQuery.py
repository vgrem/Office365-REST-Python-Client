from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class ServiceOperationQuery(ClientQuery):
    def __init__(self, binding_type, method_name=None, method_params=None, parameter_type=None,
                 parameter_name=None, return_type=None):
        super(ServiceOperationQuery, self).__init__(binding_type, parameter_type, parameter_name, return_type)
        self._method_name = method_name
        self._method_params = method_params
        self.static = False

    @property
    def methodUrl(self):
        return ResourcePathServiceOperation(self.methodName, self.methodParameters).to_url()

    @property
    def methodName(self):
        return self._method_name

    @property
    def methodParameters(self):
        return self._method_params
