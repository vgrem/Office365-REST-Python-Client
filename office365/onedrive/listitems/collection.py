from typing import TYPE_CHECKING

from typing_extensions import Self

from office365.delta_collection import DeltaCollection
from office365.directory.permissions.require_permission import require_permission
from office365.onedrive.listitems.list_item import ListItem
from office365.runtime.deprecated import deprecated
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.graph_client import GraphClient


class ListItemCollection(DeltaCollection[ListItem]):
    """Represents a collection of SharePoint/OneDrive list items with enhanced query capabilities.

    Provides methods to:
    - Add new list items
    - Query items by name or path
    - Control non-indexed property query behavior

    Example:
        >>> ctx = GraphClient()
        >>> items = ctx.sites.root.lists["Orders"].items.get()
        >>> new_item = items.add(Title="New Order").execute_query()
    """

    def __init__(self, context: "GraphClient", resource_path: ResourcePath):
        super().__init__(context, ListItem, resource_path)
        """Initialize a list item collection.

        Args:
            context: GraphClient client context
            resource_path: Resource path for the collection
        """
        self._honor_nonindexed = True

    @require_permission(
        delegated=["Sites.ReadWrite.All"],
        application=["Sites.ReadWrite.All"],
        notes="Create a new list item with the specified field values",
    )
    def add(self, **kwargs):
        """Create a new list item with the specified field values.

        Args:
            **kwargs: Field values for the new item (e.g., Title="New Item")

        Returns:
            ListItem: The newly created list item (not yet executed)
        """
        payload = {"fields": kwargs}
        return super().add(**payload)

    def honor_nonindexed(self, value: bool) -> "ListItemCollection":
        """Configure whether to allow queries on non-indexed properties.

        Args:
            value: If True, allows queries that may fail due to non-indexed properties

        Returns:
            ListItemCollection: self for method chaining
        """
        self._honor_nonindexed = value
        return self

    @require_permission(
        delegated=["Sites.Read.All", "Sites.ReadWrite.All"],
        application=["Sites.Read.All", "Sites.ReadWrite.All"],
        notes="Retrieve list items from a SharePoint list",
    )
    def get(self) -> Self:
        """Retrieve a list item"""

        def _construct_request(request: RequestOptions) -> None:
            if self._honor_nonindexed:
                request.headers["Prefer"] = "HonorNonIndexedQueriesWarningMayFailRandomly"

        return super().get().before_execute(_construct_request)

    def find_by_name(self, name: str, *, required: bool = False) -> ListItem:
        """Look up a list item by its file name.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        item matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name: The file name (e.g., "Document.docx")
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"fields/FileLeafRef eq '{escape_odata_string(name)}'", required=required)

    def find_by_path(self, path: str, *, required: bool = False) -> ListItem:
        """Look up a list item by its server-relative path.

        Deferred — run with ``execute_query()``. Tolerant by default; pass
        ``required=True`` to raise on a missing or ambiguous match.

        Args:
            path: The server-relative path (e.g., "/sites/documents/Document.docx")
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"fields/FileRef eq '{escape_odata_string(path)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> ListItem:
        """Deprecated alias of :meth:`find_by_name` (strict).

        Args:
            name: The file name (e.g., "Document.docx")

        Returns:
            ListItem: The requested list item (not yet executed)
        """
        return self.find_by_name(name, required=True)

    @deprecated("Use find_by_path() instead.", version="4.0")
    def get_by_path(self, path: str) -> ListItem:
        """Deprecated alias of :meth:`find_by_path` (strict).

        Args:
            path: The server-relative path (e.g., "/sites/documents/Document.docx")

        Returns:
            ListItem: The requested list item (not yet executed)
        """
        return self.find_by_path(path, required=True)
