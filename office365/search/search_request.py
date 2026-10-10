from __future__ import annotations

from dataclasses import dataclass, field

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.search.aggregation_option import AggregationOption
from office365.search.entity_type import EntityType
from office365.search.search_alteration_options import SearchAlterationOptions
from office365.search.search_query import SearchQuery
from office365.search.sharepoint_onedrive_options import SharePointOneDriveOptions
from office365.search.sort_property import SortProperty


@dataclass
class SearchRequest(ClientValue):
    aggregationFilters: StringCollection = field(default_factory=StringCollection)
    contentSources: StringCollection = field(default_factory=StringCollection)
    enableTopResults: bool | None = None
    entityTypes: ClientValueCollection[EntityType] = field(default_factory=lambda: ClientValueCollection(EntityType))
    from_: int | None = None
    queryAlterationOptions: SearchAlterationOptions = field(default_factory=SearchAlterationOptions)
    sharePointOneDriveOptions: SharePointOneDriveOptions = field(default_factory=SharePointOneDriveOptions)
    sortProperties: ClientValueCollection[SortProperty] = field(
        default_factory=lambda: ClientValueCollection(SortProperty)
    )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchRequest"

    aggregations: ClientValueCollection[AggregationOption] = field(
        default_factory=lambda: ClientValueCollection(AggregationOption)
    )

    fields: StringCollection = field(default_factory=StringCollection)

    query: SearchQuery = field(default_factory=SearchQuery)

    region: str | None = None

    size: int | None = None
