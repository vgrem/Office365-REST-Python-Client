from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as field_

from office365.runtime.client_value import ClientValue
from office365.search.bucket_aggregation_definition import BucketAggregationDefinition


@dataclass
class AggregationOption(ClientValue):
    """Specifies which aggregations should be returned alongside the search results.
    The maximum returned value is 100 buckets."""

    field: str | None = None

    size: int | None = None

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AggregationOption"

    bucketDefinition: BucketAggregationDefinition = field_(default_factory=BucketAggregationDefinition)
