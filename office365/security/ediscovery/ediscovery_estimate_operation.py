from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.pollable import PollableOperation
from office365.security.cases.statisticsoptions import StatisticsOptions
from office365.security.ediscovery.search import EdiscoverySearch

if TYPE_CHECKING:
    from office365.security.report_file_metadata import ReportFileMetadata


class EdiscoveryEstimateOperation(PollableOperation, Entity):
    @property
    def indexed_item_count(self) -> Optional[int]:
        """Gets the indexedItemCount property"""
        return self.properties.get("indexedItemCount", None)

    @property
    def indexed_items_size(self) -> Optional[int]:
        """Gets the indexedItemsSize property"""
        return self.properties.get("indexedItemsSize", None)

    @property
    def mailbox_count(self) -> Optional[int]:
        """Gets the mailboxCount property"""
        return self.properties.get("mailboxCount", None)

    @property
    def site_count(self) -> Optional[int]:
        """Gets the siteCount property"""
        return self.properties.get("siteCount", None)

    @property
    def statistics_options(self) -> StatisticsOptions:
        """Gets the statisticsOptions property"""
        return self.properties.get("statisticsOptions", StatisticsOptions.includeRefiners)

    @property
    def unindexed_item_count(self) -> Optional[int]:
        """Gets the unindexedItemCount property"""
        return self.properties.get("unindexedItemCount", None)

    @property
    def unindexed_items_size(self) -> Optional[int]:
        """Gets the unindexedItemsSize property"""
        return self.properties.get("unindexedItemsSize", None)

    @property
    def search(self) -> EdiscoverySearch:
        """Gets the search property"""
        return self.properties.get("search", EdiscoverySearch(self.context, ResourcePath("search", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryEstimateOperation"

    @property
    def report_file_metadata(self) -> ClientValueCollection[ReportFileMetadata]:
        """Gets the reportFileMetadata property"""
        from office365.security.report_file_metadata import ReportFileMetadata

        return self.properties.get("reportFileMetadata", ClientValueCollection[ReportFileMetadata](ReportFileMetadata))
