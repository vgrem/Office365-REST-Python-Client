from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.search.bucket_aggregation_range import BucketAggregationRange
from office365.search.bucketaggregationsortproperty import BucketAggregationSortProperty


@dataclass
class BucketAggregationDefinition(ClientValue):
    isDescending: bool | None = None
    minimumCount: int | None = None
    prefixFilter: str | None = None
    ranges: ClientValueCollection[BucketAggregationRange] = field(
        default_factory=lambda: ClientValueCollection(BucketAggregationRange)
    )
    sortBy: BucketAggregationSortProperty = BucketAggregationSortProperty.count

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BucketAggregationDefinition"
