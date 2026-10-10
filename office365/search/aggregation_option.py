from __future__ import annotations

from dataclasses import dataclass

from office365.runtime.client_value import ClientValue


@dataclass
class AggregationOption(ClientValue):
    """Specifies which aggregations should be returned alongside the search results.
    The maximum returned value is 100 buckets."""

    field: str | None = None

    size: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AggregationOption"
