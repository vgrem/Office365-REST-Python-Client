

class ClientQuery(object):
    """Client query"""

    def __init__(self, context, binding_type=None, parameter_type=None, parameter_name=None, return_type=None):
        """
        Generic query

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type binding_type: office365.runtime.client_object.ClientObject or None
        :type parameter_type: office365.runtime.client_object.ClientObject or ClientValue or dict or bytes or None
        :type parameter_name: str or None
        :type return_type: office365.runtime.client_object.ClientObject
            or office365.runtime.client_result.ClientResult or None
        """
        self._context = context
        self._binding_type = binding_type
        self._parameter_type = parameter_type
        self._parameter_name = parameter_name
        self._return_type = return_type

    def build_request(self):
        """Builds a request"""
        return self.context.build_request(self)

    def execute_query(self):
        self.context.execute_query()
        return self.return_type

    @property
    def url(self):
        if self.binding_type is not None:
            return self.binding_type.resource_url
        else:
            return self.context.service_root_url()

    @property
    def context(self):
        return self._context

    @property
    def id(self):
        return id(self)

    @property
    def binding_type(self):
        return self._binding_type

    @property
    def parameter_name(self):
        return self._parameter_name

    @property
    def parameter_type(self):
        return self._parameter_type

    @property
    def return_type(self):
        return self._return_type
