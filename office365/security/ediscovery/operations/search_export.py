from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.pollable import PollableOperation
from office365.security.cases.additionaloptions import AdditionalOptions
from office365.security.cases.exportcriteria import ExportCriteria
from office365.security.cases.exportformat import ExportFormat
from office365.security.cases.exportlocation import ExportLocation
from office365.security.cloudattachmentversion import CloudAttachmentVersion
from office365.security.search.documentversion import DocumentVersion

if TYPE_CHECKING:
    from office365.security.ediscovery.search import EdiscoverySearch
    from office365.security.export_file_metadata import ExportFileMetadata


class EdiscoverySearchExportOperation(PollableOperation, Entity):
    @property
    def additional_options(self) -> AdditionalOptions:
        """Gets the additionalOptions property"""
        return self.properties.get("additionalOptions", AdditionalOptions.none)

    @property
    def cloud_attachment_version(self) -> CloudAttachmentVersion:
        """Gets the cloudAttachmentVersion property"""
        return self.properties.get("cloudAttachmentVersion", CloudAttachmentVersion.latest)

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def document_version(self) -> DocumentVersion:
        """Gets the documentVersion property"""
        return self.properties.get("documentVersion", DocumentVersion.latest)

    @property
    def export_criteria(self) -> ExportCriteria:
        """Gets the exportCriteria property"""
        return self.properties.get("exportCriteria", ExportCriteria.searchHits)

    @property
    def export_format(self) -> ExportFormat:
        """Gets the exportFormat property"""
        return self.properties.get("exportFormat", ExportFormat.pst)

    @property
    def export_location(self) -> ExportLocation:
        """Gets the exportLocation property"""
        return self.properties.get("exportLocation", ExportLocation.responsiveLocations)

    @property
    def export_single_items(self) -> Optional[bool]:
        """Gets the exportSingleItems property"""
        return self.properties.get("exportSingleItems", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoverySearchExportOperation"

    @property
    def export_file_metadata(self) -> ClientValueCollection[ExportFileMetadata]:
        """Gets the exportFileMetadata property"""
        from office365.security.export_file_metadata import ExportFileMetadata

        return self.properties.get("exportFileMetadata", ClientValueCollection[ExportFileMetadata](ExportFileMetadata))

    @property
    def search(self) -> EdiscoverySearch:
        """Gets the search property"""
        from office365.security.ediscovery.search import EdiscoverySearch

        return self.properties.get("search", EdiscoverySearch(self.context, ResourcePath("search", self.resource_path)))
