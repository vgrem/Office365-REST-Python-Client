class ClientResult(object):
    """Client result"""

    def __init__(self, context, default_value=None):
        """
        Client result

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type default_value: int or str or bool or office365.runtime.client_value.ClientValue
        """
        self._context = context
        self._value = default_value

    def set_property(self, key, value, persist_changes=False):
        from office365.runtime.client_value import ClientValue
        if isinstance(self.value, ClientValue):
            self.value.set_property(key, value, persist_changes)
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def execute_query(self):
        self._context.execute_query()
        return self

    def execute_query_retry(self, max_retry=5, timeout_secs=5, success_callback=None, failure_callback=None):
        self._context.execute_query_retry(max_retry=max_retry,
                                          timeout_secs=timeout_secs,
                                          success_callback=success_callback,
                                          failure_callback=failure_callback)
        return self
