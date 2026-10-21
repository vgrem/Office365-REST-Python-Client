from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from requests import Response

from office365.runtime.client_object import ClientObject
from office365.runtime.client_request import ClientRequest
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.queries.client_query import ClientQuery
from office365.runtime.queries.create_entity import CreateEntityQuery
from office365.runtime.queries.delete_entity import DeleteEntityQuery
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.queries.update_entity import UpdateEntityQuery
from office365.runtime.transport.base import BaseTransport


class ODataRequest(ClientRequest):
    """Handles OData protocol specific request/response processing for API calls."""

    def __init__(
        self,
        base_url: str,
        json_format: ODataJsonFormat,
        transport: "BaseTransport | None" = None,
    ) -> None:
        """
        Initialize a new OData request processor.

        Args:
            base_url: The service base URL.
            json_format: The JSON format handler for OData serialization/deserialization
            transport: Optional shared transport (e.g. one pooled ``Session`` for
                parallel batch requests); defaults to a new ``RequestsTransport``.
        """
        super().__init__(transport=transport)
        self._base_url = base_url
        self._default_json_format = json_format
        self.beforeExecute += self._ensure_http_headers

    @property
    def json_format(self):
        """Gets the default JSON format handler."""
        return self._default_json_format

    def build_request(self, query: ClientQuery) -> RequestOptions:
        """
        Builds a request object for the specified query.

        Args:
            query: The client query to execute

        Returns:
            Configured request options
        """
        request = RequestOptions(url=query.url)
        request.method = HttpMethod.Get
        if isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Post
        elif isinstance(query, (CreateEntityQuery, UpdateEntityQuery, ServiceOperationQuery)):
            request.method = HttpMethod.Post
            if query.parameters_type is not None:
                request.data = self._build_payload(query)
        return request

    def handle_response(self, response: Response, query: ClientQuery) -> None:
        """
        Handles an HTTP response according to OData specifications.

        Args:
            response: The HTTP response
            query: The original query that generated this response
        """
        return_type = query.return_type
        if return_type is None:
            return

        if isinstance(return_type, ClientObject):
            return_type.clear_state()

        content_type = response.headers.get("Content-Type", "").lower().split(";")[0]
        is_raw_content = isinstance(query, FunctionQuery) and query.return_raw_content

        if content_type != "application/json" or is_raw_content:
            if isinstance(return_type, ClientResult):
                return_type.set_property("__value", response.content)
            return

        # A function/service operation answers under its own name in JSON Light;
        # the wrapper is an argument here, never state on the shared profile.
        wrapper = None
        if self.json_format.dialect.container is not None and isinstance(query, (ServiceOperationQuery, FunctionQuery)):
            wrapper = query.name
        try:
            self.hydrate(return_type, response.json(), wrapper=wrapper)
        except ValueError as e:
            raise ClientRequestException(str(e), response=response) from e

    def hydrate(
        self,
        target: Union[ClientValue, ClientResult, ClientObject],
        payload: Any,
        json_format: Optional[ODataJsonFormat] = None,
        wrapper: Optional[str] = None,
    ) -> None:
        """
        Hydrates a client object from a decoded JSON payload.

        Args:
            target: The target object to map data to
            payload: The decoded JSON response body
            json_format: Optional profile override
            wrapper: Key the payload is wrapped under, if the dialect wraps it
        """
        (json_format or self.json_format).hydrate(target, payload, wrapper)

    def _build_payload(self, query: ClientQuery) -> Union[Dict[str, Any], List[Any], str, bytes]:
        """
        Builds the request body for a query.

        Args:
            query: The query containing parameters to serialize

        Returns:
            The JSON body (or the raw bytes of a binary one)
        """
        # A raw binary body (file upload content) is not JSON — never decode it.
        if isinstance(query.parameters_type, (bytes, bytearray)):
            return query.parameters_type

        json = self._default_json_format.build_payload(query.parameters_type)
        if isinstance(query, ServiceOperationQuery) and query.parameters_name is not None:
            json = {query.parameters_name: json}
        return json

    def _ensure_http_headers(self, request: RequestOptions) -> None:
        """
        Ensures required OData headers are present in the request, namely:
           - The Content-Type header
           - Accept request-header field
           - The If-Match request-header field (optional)
        """
        media_type = self.json_format.media_type
        request.ensure_header("Content-Type", media_type)
        request.ensure_header("Accept", media_type)

    @property
    def service_root_url(self) -> str:
        """Get the SharePoint REST API service root URL"""
        return f"{self._base_url}/_api"
