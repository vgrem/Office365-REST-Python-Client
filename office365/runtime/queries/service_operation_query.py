from office365.runtime.paths.static_service_operation import StaticServiceOperationPath
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.paths.service_operation import ServiceOperationPath


class ServiceOperationQuery(ClientQuery):
    def __init__(self, binding_type,
                 method_name=None,
                 method_params=None,
                 parameter_type=None,
                 parameter_name=None,
                 return_type=None):
        """

        :type method_params: list or dict or office365.runtime.client_value.ClientValue or None
        :type method_name: str or None
        """
        super(ServiceOperationQuery, self).__init__(binding_type.context,
                                                    binding_type,
                                                    parameter_type,
                                                    parameter_name,
                                                    return_type)
        self._method_name = method_name
        self._method_params = method_params
        self.static = False

    @property
    def resource_path(self):
        if isinstance(self, ServiceOperationQuery):
            if self.static:
                return StaticServiceOperationPath(
                    self.binding_type.entity_type_name,
                    self.method_name,
                    self.method_parameters)
            else:
                return ServiceOperationPath(
                    self.method_name,
                    self.method_parameters,
                    self.binding_type.resource_path
                )

    @property
    def method_name(self):
        return self._method_name

    @property
    def method_parameters(self):
        return self._method_params
