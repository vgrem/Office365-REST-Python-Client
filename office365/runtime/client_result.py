class ClientResult(object):
    """Client result"""

    def __init__(self, context, default_value=None):
        """

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type default_value: any
        """
        self.context = context
        self.value = default_value

    def build_request(self):
        return self.context.build_request()

    def execute_query(self):
        self.context.execute_query()
        return self

