from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.pollable import PollableOperation

if TYPE_CHECKING:
    from office365.security.report_file_metadata import ReportFileMetadata


class EdiscoveryPurgeDataOperation(PollableOperation, Entity):
    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryPurgeDataOperation"

    @property
    def report_file_metadata(self) -> ClientValueCollection[ReportFileMetadata]:
        """Gets the reportFileMetadata property"""
        from office365.security.report_file_metadata import ReportFileMetadata

        return self.properties.get("reportFileMetadata", ClientValueCollection[ReportFileMetadata](ReportFileMetadata))
