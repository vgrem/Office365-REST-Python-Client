from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.pollable import PollableOperation
from office365.security.cases.additionaldataoptions import (
    AdditionalDataOptions,
)
from office365.security.cases.itemstoinclude import ItemsToInclude
from office365.security.cloudattachmentversion import CloudAttachmentVersion
from office365.security.ediscovery.review_set import EdiscoveryReviewSet
from office365.security.search.documentversion import DocumentVersion

if TYPE_CHECKING:
    from office365.security.ediscovery.search import EdiscoverySearch
    from office365.security.report_file_metadata import ReportFileMetadata


class EdiscoveryAddToReviewSetOperation(PollableOperation, Entity):
    @property
    def additional_data_options(self) -> AdditionalDataOptions:
        """Gets the additionalDataOptions property"""
        return self.properties.get("additionalDataOptions", AdditionalDataOptions.allVersions)

    @property
    def cloud_attachment_version(self) -> CloudAttachmentVersion:
        """Gets the cloudAttachmentVersion property"""
        return self.properties.get("cloudAttachmentVersion", CloudAttachmentVersion.latest)

    @property
    def document_version(self) -> DocumentVersion:
        """Gets the documentVersion property"""
        return self.properties.get("documentVersion", DocumentVersion.latest)

    @property
    def items_to_include(self) -> ItemsToInclude:
        """Gets the itemsToInclude property"""
        return self.properties.get("itemsToInclude", ItemsToInclude.searchHits)

    @property
    def review_set(self) -> EdiscoveryReviewSet:
        """Gets the reviewSet property"""
        return self.properties.get(
            "reviewSet", EdiscoveryReviewSet(self.context, ResourcePath("reviewSet", self.resource_path))
        )

    @property
    def search(self) -> EdiscoverySearch:
        """Gets the search property"""
        return self.properties.get("search", EdiscoverySearch(self.context, ResourcePath("search", self.resource_path)))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryAddToReviewSetOperation"

    @property
    def report_file_metadata(self) -> ClientValueCollection[ReportFileMetadata]:
        """Gets the reportFileMetadata property"""
        from office365.security.report_file_metadata import ReportFileMetadata

        return self.properties.get("reportFileMetadata", ClientValueCollection[ReportFileMetadata](ReportFileMetadata))
