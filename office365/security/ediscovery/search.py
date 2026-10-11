from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.ediscovery.noncustodial_data_source import (
    EdiscoveryNoncustodialDataSource,
)
from office365.security.ediscovery.operations.add_to_review_set import (
    EdiscoveryAddToReviewSetOperation,
)
from office365.security.search.data_source import DataSource
from office365.security.search.datasourcescopes import DataSourceScopes

if TYPE_CHECKING:
    from office365.security.ediscovery.ediscovery_estimate_operation import (
        EdiscoveryEstimateOperation,
    )


class EdiscoverySearch(Entity):
    @property
    def data_source_scopes(self) -> DataSourceScopes:
        """Gets the dataSourceScopes property"""
        return self.properties.get("dataSourceScopes", DataSourceScopes.none)

    @property
    def additional_sources(self) -> EntityCollection[DataSource]:
        """Gets the additionalSources property"""
        return self.properties.get(
            "additionalSources",
            EntityCollection[DataSource](
                self.context, DataSource, ResourcePath("additionalSources", self.resource_path)
            ),
        )

    @property
    def add_to_review_set_operation(self) -> EdiscoveryAddToReviewSetOperation:
        """Gets the addToReviewSetOperation property"""
        return self.properties.get(
            "addToReviewSetOperation",
            EdiscoveryAddToReviewSetOperation(self.context, ResourcePath("addToReviewSetOperation", self.resource_path)),
        )

    @property
    def custodian_sources(self) -> EntityCollection[DataSource]:
        """Gets the custodianSources property"""
        return self.properties.get(
            "custodianSources",
            EntityCollection[DataSource](self.context, DataSource, ResourcePath("custodianSources", self.resource_path)),
        )

    @property
    def noncustodial_sources(self) -> EntityCollection[EdiscoveryNoncustodialDataSource]:
        """Gets the noncustodialSources property"""
        return self.properties.get(
            "noncustodialSources",
            EntityCollection[EdiscoveryNoncustodialDataSource](
                self.context, EdiscoveryNoncustodialDataSource, ResourcePath("noncustodialSources", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoverySearch"

    @property
    def last_estimate_statistics_operation(self) -> EdiscoveryEstimateOperation:
        """Gets the lastEstimateStatisticsOperation property"""
        from office365.security.ediscovery.ediscovery_estimate_operation import (
            EdiscoveryEstimateOperation,
        )

        return self.properties.get(
            "lastEstimateStatisticsOperation",
            EdiscoveryEstimateOperation(
                self.context, ResourcePath("lastEstimateStatisticsOperation", self.resource_path)
            ),
        )
