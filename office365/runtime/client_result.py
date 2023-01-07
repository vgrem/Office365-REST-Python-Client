from typing import TypeVar

from office365.runtime.client_value import ClientValue

T = TypeVar("T", int, str, bytes, bool, ClientValue)


class ClientResult(object):
    """Client result"""

    def __init__(self, context, default_value=None):
        """
        Client result

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        :type default_value: T
        """
        self._context = context
        self._value = default_value

    def after_execute(self, action, *args, **kwargs):

        def _process_response(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            action(self, *args, **kwargs)

        self._context.after_execute(_process_response, True)
        return self

    def set_property(self, key, value, persist_changes=False):
        """
        :type key: str
        :type value: T
        :type persist_changes: bool
        """
        from office365.runtime.client_value import ClientValue
        if isinstance(self.value, ClientValue):
            self.value.set_property(key, value, persist_changes)
        else:
            self._value = value

    @property
    def value(self):
        return self._value

    def execute_query(self):
        """Submit request(s) to the server"""
        self._context.execute_query()
        return self

    def execute_query_retry(self, max_retry=5, timeout_secs=5, success_callback=None, failure_callback=None):
        """
        Executes the current set of data retrieval queries and method invocations and retries it if needed.
        """
        self._context.execute_query_retry(max_retry=max_retry,
                                          timeout_secs=timeout_secs,
                                          success_callback=success_callback,
                                          failure_callback=failure_callback)
        return self
