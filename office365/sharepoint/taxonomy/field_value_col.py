from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue


@dataclass(init=False)
class TaxonomyFieldValueCollection(ClientValueCollection[TaxonomyFieldValue]):
    """Represents the multi-value object for the taxonomy column."""

    def __init__(
        self,
        values: Any = None,
        _data: Optional[List[TaxonomyFieldValue]] = None,
    ):
        """Initialize the collection.

        Args:
            values: The term values (a list of :class:`TaxonomyFieldValue`) or,
                for backwards compatibility, the item type ``TaxonomyFieldValue``.
            _data: Legacy second positional argument holding the values.
        """
        if isinstance(values, type):
            # legacy form: ``TaxonomyFieldValueCollection(TaxonomyFieldValue, [tv])``
            super().__init__(values, _data)
        else:
            super().__init__(TaxonomyFieldValue, list(values) if values else None)

    def __str__(self):
        return ";#".join([str(item) for item in self._data])
