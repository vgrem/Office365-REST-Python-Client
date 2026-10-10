from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, cast

from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata.json_format import ODataJsonFormat
from office365.runtime.types.collections import StringCollection
from office365.search.aggregation_option import AggregationOption
from office365.search.collapse_property import CollapseProperty
from office365.search.query import SearchQuery
from office365.search.result_template_option import ResultTemplateOption
from office365.search.search_alteration_options import SearchAlterationOptions
from office365.search.sharepoint_onedrive_options import SharePointOneDriveOptions
from office365.search.sort_property import SortProperty


@dataclass
class SearchRequest(ClientValue):
    """A search request formatted in a JSON blob."""

    query: SearchQuery
    aggregationFilters: StringCollection = field(default_factory=StringCollection)
    aggregations: ClientValueCollection[AggregationOption] = field(
        default_factory=lambda: ClientValueCollection(AggregationOption)
    )
    enableTopResults: bool | None = None
    size: int | None = None
    region: str | None = None
    entityTypes: list[str] | None = None
    fields: list[str] | None = None
    page_from: int | None = None
    sortProperties: ClientValueCollection[SortProperty] = field(
        default_factory=lambda: ClientValueCollection(SortProperty)
    )
    contentSources: StringCollection = field(default_factory=StringCollection)
    sharePointOneDriveOptions: SharePointOneDriveOptions = field(default_factory=SharePointOneDriveOptions)

    def to_json(self, json_format: ODataJsonFormat | None = None) -> Dict:
        json_value = cast(Dict, super().to_json(json_format))
        json_value["from"] = json_value.pop("page_from", None)
        return json_value

    from_: int | None = None

    queryAlterationOptions: SearchAlterationOptions = field(default_factory=SearchAlterationOptions)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.SearchRequest"

    collapseProperties: ClientValueCollection[CollapseProperty] = field(
        default_factory=lambda: ClientValueCollection(CollapseProperty)
    )

    resultTemplateOptions: ResultTemplateOption = field(default_factory=ResultTemplateOption)
