from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from typing_extensions import Self

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.runtime.client_object import ClientObject
    from office365.runtime.client_request import ClientRequest
    from office365.runtime.client_result import ClientResult
    from office365.runtime.client_runtime_context import ClientRuntimeContext
    from office365.runtime.client_value import ClientValue
    from office365.runtime.odata.query_options import QueryOptions

ReturnT = TypeVar("ReturnT", bound="ClientObject | ClientResult")


class ClientQuery(Generic[ReturnT]):
    """Client query"""

    def __init__(
        self,
        context: ClientRuntimeContext,
        binding_type: ClientObject | None = None,
        parameters_type: ClientObject | ClientValue | dict | str | bytes | None = None,
        parameters_name: str | None = None,
        return_type: ReturnT | None = None,
    ) -> None:
        """
        Initialize a client query

        Args:
            context: The client runtime context
            binding_type: The object this query is bound to (optional)
            parameters_type: Type of parameters (ClientObject, ClientValue, dict, or string)
            parameters_name: Name of the parameters collection (optional)
            return_type: Expected return type of the query (optional)
        """
        self._context = context
        self._binding_type = binding_type
        self._parameters_type = parameters_type
        self._parameters_name = parameters_name
        self._return_type: ReturnT | None = return_type
        # Optional permission metadata (set by ``@require_permission`` when the
        # query is built). Surfaced as an error hint when the request is denied.
        # Untyped on purpose: the runtime stays independent of the directory models.
        self._permission_requirement: Any = None
        # Queries run inside a batch by default. A query that targets an endpoint
        # the batch service doesn't accept (e.g. ``_vti_bin/listdata.svc``) sets
        # this to ``False`` so batch execution runs it on its own, in order.
        self.batchable = True

    def build_request(self) -> RequestOptions:
        """Builds a request"""
        request = self.context.pending_request().build_request(self)
        self.context.pending_request().beforeExecute(request)
        self.context.pending_request().apply_client_request_id(request)
        return request

    def execute_query(self, request: "ClientRequest") -> None:
        """Run this query via the given request.

        The base implementation delegates to the transport (sends the HTTP
        request); subclasses may override how they execute — e.g.
        ``DeferredOperationQuery`` resolves without sending a request.
        """
        request.execute_query(self)

    async def execute_query_async(self, request: "ClientRequest") -> None:
        """Async counterpart of :meth:`execute_query`."""
        await request.execute_query_async(self)

    def before_execute(self, action: Callable[[RequestOptions], None], once: bool = True) -> Self:
        """
        Attach an event handler which is triggered before query is submitted to server
        """

        self.context.pending_request().before_execute(
            action,
            once=once,
            condition=lambda: self.context.current_query is not None and self.context.current_query.id == self.id,
        )
        return self

    def on_error(self, action: Callable[[ClientRequestException], None], once: bool = True) -> Self:
        self.context.pending_request().on_error(
            action,
            once=once,
            condition=lambda: self.context.current_query is not None and self.context.current_query.id == self.id,
        )
        return self

    @property
    def url(self) -> str:
        """Builds the full request URL from the query's service root and resource path."""
        if self.binding_type is not None:
            return "".join([self.context.service_root_url, str(self.path)])
        return self.context.service_root_url

    @property
    def query_options(self) -> QueryOptions | None:
        return self.binding_type.query_options if self.binding_type is not None else None

    @property
    def path(self) -> ResourcePath | None:
        """The resource path for this query.

        Returns:
            ResourcePath of the bound object or None
        """
        if self.binding_type is not None:
            return self.binding_type.resource_path
        else:
            return None

    @property
    def context(self) -> ClientRuntimeContext:
        """The client runtime context."""
        return self._context

    @property
    def id(self) -> int:
        """The unique identifier of the query."""
        return id(self)

    @property
    def binding_type(self) -> ClientObject | None:
        """The object this query is bound to."""
        return self._binding_type

    @property
    def parameters_name(self) -> str | None:
        """Name of the parameters collection."""
        return self._parameters_name

    @property
    def parameters_type(self) -> ClientObject | ClientValue | dict | str | bytes | None:
        """Type of parameters for this query."""
        return self._parameters_type

    @property
    def permission_requirement(self) -> Any:
        """Permission metadata attached by ``@require_permission`` (or ``None``).

        Used to enrich an :class:`~office365.runtime.exceptions.AccessDeniedException`
        with the permissions the API declares, so a 403 explains what to grant.
        """
        return self._permission_requirement

    @permission_requirement.setter
    def permission_requirement(self, value: Any) -> None:
        self._permission_requirement = value

    @property
    def return_type(self) -> ReturnT | None:
        """Expected return type of this query."""
        return self._return_type
