from __future__ import annotations

from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.deprecated import deprecated
from office365.runtime.odata.literals import escape_odata_string
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.groups.group import TermGroup
from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection


class TermGroupCollection(TaxonomyItemCollection[TermGroup]):
    """A collection of TermGroup (section 3.1.5.18) objects"""

    def __init__(self, context: ClientRuntimeContext, resource_path: ResourcePath | None = None):
        super().__init__(context, TermGroup, resource_path)

    def find_by_name(self, name: str, *, required: bool = False) -> TermGroup:
        """Look up the term group with the specified name.

        Deferred — run with ``execute_query()``. Tolerant by default: when no
        group matches, the returned object is left uninitialized (check
        :attr:`~office365.runtime.client_object.ClientObject.is_loaded`). Pass
        ``required=True`` to raise instead (or on an ambiguous match).

        Args:
            name (str): The name of the TermGroup.
            required (bool): Raise on a missing or ambiguous match when ``True``
        """
        return self._find_by_filter(f"name eq '{escape_odata_string(name)}'", required=required)

    @deprecated("Use find_by_name() instead.", version="4.0")
    def get_by_name(self, name: str) -> TermGroup:
        """Deprecated alias of :meth:`find_by_name` (strict).

        Args:
            name (str): The name of the TermGroup.
        """
        return self.find_by_name(name, required=True)
