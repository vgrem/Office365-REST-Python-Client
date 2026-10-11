from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.directory.permissions.identity_set import IdentitySet
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.directory.protection.threatassessment.contenttype import (
        ThreatAssessmentContentType,
    )
    from office365.directory.protection.threatassessment.requests.threat_assessment_result import (
        ThreatAssessmentResult,
    )
    from office365.directory.protection.threatassessment.requestsource import (
        ThreatAssessmentRequestSource,
    )


class ThreatAssessmentRequest(Entity):
    """An abstract resource type used to represent a threat assessment request item."""

    @odata(name="createdBy")
    @property
    def created_by(self) -> IdentitySet:
        """The threat assessment request creator."""
        return self.properties.get("createdBy", IdentitySet())

    @odata(name="createdDateTime")
    @property
    def created_datetime(self) -> datetime:
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def status(self) -> Optional[str]:
        """The threat assessment status. Possible values are: pending, completed."""
        return self.properties.get("status", None)

    @odata(name="expectedAssessment")
    @property
    def expected_assessment(self) -> Optional[str]:
        """The expected assessment from submitter. Possible values: block, unblock."""
        return self.properties.get("expectedAssessment", None)

    @property
    def category(self) -> Optional[str]:
        """The threat category. Possible values: spam, phishing, malware."""
        return self.properties.get("category", None)

    @property
    def content_type(self) -> ThreatAssessmentContentType:
        """Gets the contentType property"""
        from office365.directory.protection.threatassessment.contenttype import (
            ThreatAssessmentContentType,
        )

        return self.properties.get("contentType", ThreatAssessmentContentType.mail)

    @property
    def request_source(self) -> ThreatAssessmentRequestSource:
        """Gets the requestSource property"""
        from office365.directory.protection.threatassessment.requestsource import (
            ThreatAssessmentRequestSource,
        )

        return self.properties.get("requestSource", ThreatAssessmentRequestSource.undefined)

    @property
    def results(self) -> EntityCollection[ThreatAssessmentResult]:
        """Gets the results property"""
        from office365.directory.protection.threatassessment.requests.threat_assessment_result import (
            ThreatAssessmentResult,
        )

        return self.properties.get(
            "results",
            EntityCollection[ThreatAssessmentResult](
                self.context, ThreatAssessmentResult, ResourcePath("results", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ThreatAssessmentRequest"
