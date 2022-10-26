from office365.runtime.odata.path_builder import ODataPathBuilder
from office365.runtime.queries.client_query import ClientQuery


class ServiceOperationQuery(ClientQuery):
    """"Service operation query"""

    def __init__(self, binding_type,
                 method_name=None,
                 method_params=None,
                 parameter_type=None,
                 parameter_name=None,
                 return_type=None,
                 is_static=False):
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
        self.static = is_static

    @property
    def url(self):
        orig_url = super(ServiceOperationQuery, self).url
        if self.static:
            normalized_name = ".".join([self.binding_type.entity_type_name, self.method_name])
            return "/".join([self.context.service_root_url(),
                             ODataPathBuilder.build(normalized_name, self._method_params)])
        else:
            return "/".join([orig_url, ODataPathBuilder.build(self._method_name, self._method_params)])

    @property
    def method_name(self):
        return self._method_name

    @property
    def method_parameters(self):
        return self._method_params
