from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation


class ServiceOperationQuery(ClientQuery):
    def __init__(self, binding_type, method_name=None, method_params=None, parameter_type=None,
                 parameter_name=None, return_type=None):
        """

        :type method_params: list or dict or office365.runtime.clientValue.ClientValue or None
        :type method_name: str or None
        """
        super(ServiceOperationQuery, self).__init__(binding_type, parameter_type, parameter_name, return_type)
        self._method_name = method_name
        self._method_params = method_params
        self.static = False

    @property
    def method_url(self):
        return ResourcePathServiceOperation(self.method_name, self.method_parameters).to_url()

    @property
    def method_name(self):
        return self._method_name

    @property
    def method_parameters(self):
        return self._method_params
