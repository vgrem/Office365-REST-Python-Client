from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.cases.operation import CaseOperation
from office365.security.ediscovery.case_member import EdiscoveryCaseMember
from office365.security.ediscovery.custodian import EdiscoveryCustodian
from office365.security.ediscovery.noncustodial_data_source import (
    EdiscoveryNoncustodialDataSource,
)
from office365.security.ediscovery.review_set import EdiscoveryReviewSet
from office365.security.ediscovery.search import EdiscoverySearch

if TYPE_CHECKING:
    from office365.security.ediscovery.ediscovery_case_settings import (
        EdiscoveryCaseSettings,
    )
    from office365.security.ediscovery.ediscovery_review_tag import (
        EdiscoveryReviewTag,
    )


class EdiscoveryCase(Entity):
    """In the context of eDiscovery, contains custodians, searches, review sets. For details, see Overview of
    Microsoft Purview eDiscovery (Premium)."""

    @property
    def operations(self) -> EntityCollection[CaseOperation]:
        """Returns a list of case caseOperation objects for this case."""
        return self.properties.get(
            "operations", EntityCollection(self.context, CaseOperation, ResourcePath("operations", self.resource_path))
        )

    @property
    def closed_by(self) -> IdentitySet:
        """Gets the closedBy property"""
        return self.properties.get("closedBy", IdentitySet())

    @property
    def closed_date_time(self) -> Optional[datetime]:
        """Gets the closedDateTime property"""
        return self.properties.get("closedDateTime", datetime.min)

    @property
    def external_id(self) -> Optional[str]:
        """Gets the externalId property"""
        return self.properties.get("externalId", None)

    @property
    def case_members(self) -> EntityCollection[EdiscoveryCaseMember]:
        """Gets the caseMembers property"""
        return self.properties.get(
            "caseMembers",
            EntityCollection[EdiscoveryCaseMember](
                self.context, EdiscoveryCaseMember, ResourcePath("caseMembers", self.resource_path)
            ),
        )

    @property
    def custodians(self) -> EntityCollection[EdiscoveryCustodian]:
        """Gets the custodians property"""
        return self.properties.get(
            "custodians",
            EntityCollection[EdiscoveryCustodian](
                self.context, EdiscoveryCustodian, ResourcePath("custodians", self.resource_path)
            ),
        )

    @odata(name="noncustodialDataSources")
    @property
    def noncustodial_data_sources(self) -> EntityCollection[EdiscoveryNoncustodialDataSource]:
        """Gets the noncustodialDataSources property"""
        return self.properties.get(
            "noncustodialDataSources",
            EntityCollection[EdiscoveryNoncustodialDataSource](
                self.context,
                EdiscoveryNoncustodialDataSource,
                ResourcePath("noncustodialDataSources", self.resource_path),
            ),
        )

    @odata(name="reviewSets")
    @property
    def review_sets(self) -> EntityCollection[EdiscoveryReviewSet]:
        """Gets the reviewSets property"""
        return self.properties.get(
            "reviewSets",
            EntityCollection[EdiscoveryReviewSet](
                self.context, EdiscoveryReviewSet, ResourcePath("reviewSets", self.resource_path)
            ),
        )

    @property
    def searches(self) -> EntityCollection[EdiscoverySearch]:
        """Gets the searches property"""
        return self.properties.get(
            "searches",
            EntityCollection[EdiscoverySearch](
                self.context, EdiscoverySearch, ResourcePath("searches", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.EdiscoveryCase"

    @property
    def settings(self) -> EdiscoveryCaseSettings:
        """Gets the settings property"""
        from office365.security.ediscovery.ediscovery_case_settings import (
            EdiscoveryCaseSettings,
        )

        return self.properties.get(
            "settings", EdiscoveryCaseSettings(self.context, ResourcePath("settings", self.resource_path))
        )

    @property
    def tags(self) -> EntityCollection[EdiscoveryReviewTag]:
        """Gets the tags property"""
        from office365.security.ediscovery.ediscovery_review_tag import (
            EdiscoveryReviewTag,
        )

        return self.properties.get(
            "tags",
            EntityCollection[EdiscoveryReviewTag](
                self.context, EdiscoveryReviewTag, ResourcePath("tags", self.resource_path)
            ),
        )
