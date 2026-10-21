from __future__ import annotations

from typing import TYPE_CHECKING

from requests import Response
from typing_extensions import Self

from office365.delta_collection import DeltaCollection
from office365.runtime.client_object import ClientObjectT
from office365.runtime.client_result import ClientResult
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.queries.function import FunctionQuery

if TYPE_CHECKING:
    pass


class CountCollection(DeltaCollection[ClientObjectT]):
    """
    A specialized collection that supports OData $count operations.

    This collection extends DeltaCollection with the ability to efficiently count items
    without retrieving the entire collection.

    Example:
        >>> client = GraphClient()
        >>> result = client.groups.count().execute_query()
        >>> print(result.value)
    """

    def __init__(self, context, item_type, resource_path=None, parent=None):
        super().__init__(context, item_type, resource_path, parent)
        self._consistency_level: str | None = None

    def consistency_level(self, level: str = "eventual") -> Self:
        """Set ConsistencyLevel header and ``$count=true`` for ``$count`` queries.

        The header is automatically registered when ``get()`` executes
        and cleared afterward. Only needed when ``$count`` appears in
        a ``$filter`` expression.

        Usage:
            apps = client.applications.filter("owners/$count eq 0")\\
                .consistency_level("eventual").get().execute_query()
        """
        self._consistency_level = level
        self.query_options.custom["$count"] = "true"
        return self

    def get(self) -> Self:
        super().get()
        if self._consistency_level:
            level = self._consistency_level
            self._consistency_level = None

            def _set_header(request: RequestOptions) -> None:
                request.ensure_header("ConsistencyLevel", level)

            self.context.before_execute(_set_header)
        return self

    def count(self) -> ClientResult[int]:
        """
        Executes an OData $count query to get the number of items in the collection.

        This performs a lightweight HTTP request that only returns the count,
        not the actual items. For large collections, this is significantly more
        efficient than loading all items.

        Returns:
            ClientResult[int]: A result object containing the count value

        Note:
            - Uses "eventual" consistency level for accurate counts
            - Works with server-side paging
            - Supports all existing query operations (filter, etc.)
        """
        return_type = ClientResult(self.context, int())

        def _construct_request(request: RequestOptions) -> None:
            request.headers.pop("Accept", None)
            request.ensure_header("ConsistencyLevel", "eventual")

        def _handle_response(response: Response) -> None:
            value = int(response.content.decode("utf-8"))
            return_type.set_property("__value", value)

        qry = FunctionQuery(self, "$count")
        (
            self.context.add_query(qry)
            .before_execute(_construct_request)
            .after_execute(_handle_response, include_response=True)
        )
        return return_type
