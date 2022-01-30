class ClientResult(object):
    """Client result"""

    def __init__(self, context, default_value=None):
        """
        Client result

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type default_value: any
        """
        self._context = context
        self._value = default_value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def context(self):
        return self._context

    def execute_query(self):
        self.context.execute_query()
        return self

    def execute_query_retry(self, max_retry=5, timeout_secs=5, success_callback=None, failure_callback=None):
        self.context.execute_query_retry(max_retry=max_retry,
                                         timeout_secs=timeout_secs,
                                         success_callback=success_callback,
                                         failure_callback=failure_callback)
        return self

