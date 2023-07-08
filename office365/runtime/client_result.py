import copy
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
        self._value = copy.deepcopy(default_value)

    def before_execute(self, action, *args, **kwargs):
        """
        Attach an event handler which is triggered before query is submitted to server
        :param (office365.runtime.http.request_options.RequestOptions) -> None action: Event handler
        """
        self._context.before_query_execute(action, *args, **kwargs)
        return self

    def after_execute(self, action, *args, **kwargs):
        """
        Attach an event handler which is triggered after query is submitted to server
        :param (ClientResult) -> None action: Event handler
        """
        self._context.after_query_execute(action, self, *args, **kwargs)
        return self

    def set_property(self, key, value, persist_changes=False):
        """
        :type key: str
        :type value: T
        :type persist_changes: bool
        """
        from office365.runtime.client_value import ClientValue
        if isinstance(self._value, ClientValue):
            self._value.set_property(key, value, persist_changes)
        else:
            self._value = value

    @property
    def value(self):
        """Returns the value"""
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
