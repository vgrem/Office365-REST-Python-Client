from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.intune.servicecommunications.announcement_base import (
    ServiceAnnouncementBase,
)
from office365.intune.servicecommunications.health.types import (
    ServiceHealthClassificationType,
)
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.function import FunctionQuery

if TYPE_CHECKING:
    from office365.intune.servicecommunications.health.origin import ServiceHealthOrigin
    from office365.intune.servicecommunications.health.status import ServiceHealthStatus
    from office365.intune.servicecommunications.service_health_issue_post import ServiceHealthIssuePost


class ServiceHealthIssue(ServiceAnnouncementBase):
    """
    Represents a service sitehealth issue in a service.

    The service sitehealth issue can be a service incident or service advisory. For example:

       - Service incident: "Exchange mailbox service is down".
       - Service advisory: "Users may experience delays in emails reception".
    """

    @property
    def classification(self) -> ServiceHealthClassificationType:
        """The type of service health issue"""
        return self.properties.get("classification", ServiceHealthClassificationType.none)

    @property
    def feature(self) -> Optional[str]:
        """The feature name of the service issue."""
        return self.properties.get("feature", None)

    @property
    def feature_group(self) -> Optional[str]:
        """The feature group name of the service issue."""
        return self.properties.get("featureGroup", None)

    @property
    def impact_description(self) -> Optional[str]:
        """The description of the service issue impact."""
        return self.properties.get("impactDescription", None)

    def incident_report(self) -> ClientResult[bytes]:
        """
        Provide the Post-Incident Review (PIR) document of a specified service issue for tenant.

        An issue only with status of PostIncidentReviewPublished indicates that the PIR document exists for the issue.
        The operation returns an error if the specified issue doesn't exist for the tenant or if PIR document
        does not exist for the issue.
        """
        return_type = ClientResult(self.context, bytes())
        qry = FunctionQuery(self, "incidentReport", None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def is_resolved(self) -> Optional[bool]:
        """Gets the isResolved property"""
        return self.properties.get("isResolved", None)

    @property
    def origin(self) -> ServiceHealthOrigin:
        """Gets the origin property"""
        from office365.intune.servicecommunications.health.origin import (
            ServiceHealthOrigin,
        )

        return self.properties.get("origin", ServiceHealthOrigin.microsoft)

    @property
    def posts(self) -> ClientValueCollection[ServiceHealthIssuePost]:
        """Gets the posts property"""
        from office365.intune.servicecommunications.service_health_issue_post import ServiceHealthIssuePost

        return self.properties.get("posts", ClientValueCollection[ServiceHealthIssuePost](ServiceHealthIssuePost))

    @property
    def service(self) -> Optional[str]:
        """Gets the service property"""
        return self.properties.get("service", None)

    @property
    def status(self) -> ServiceHealthStatus:
        """Gets the status property"""
        from office365.intune.servicecommunications.health.status import (
            ServiceHealthStatus,
        )

        return self.properties.get("status", ServiceHealthStatus.serviceOperational)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceHealthIssue"
