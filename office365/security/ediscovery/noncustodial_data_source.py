from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.search.data_source import DataSource

if TYPE_CHECKING:
    from office365.security.ediscovery.ediscovery_index_operation import (
        EdiscoveryIndexOperation,
    )


class EdiscoveryNoncustodialDataSource(Entity):
    @property
    def data_source(self) -> DataSource:
        """Gets the dataSource property"""
        return self.properties.get(
            "dataSource", DataSource(self.context, ResourcePath("dataSource", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryNoncustodialDataSource"

    @property
    def last_index_operation(self) -> EdiscoveryIndexOperation:
        """Gets the lastIndexOperation property"""
        from office365.security.ediscovery.ediscovery_index_operation import (
            EdiscoveryIndexOperation,
        )

        return self.properties.get(
            "lastIndexOperation",
            EdiscoveryIndexOperation(self.context, ResourcePath("lastIndexOperation", self.resource_path)),
        )
