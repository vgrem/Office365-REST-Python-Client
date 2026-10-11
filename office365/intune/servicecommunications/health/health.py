from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.intune.servicecommunications.health.status import ServiceHealthStatus
    from office365.intune.servicecommunications.issues.issue import ServiceHealthIssue


class ServiceHealth(Entity):
    """Represents the sitehealth information of a service subscribed by a tenant."""

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
    def issues(self) -> EntityCollection[ServiceHealthIssue]:
        """Gets the issues property"""
        from office365.intune.servicecommunications.issues.issue import (
            ServiceHealthIssue,
        )

        return self.properties.get(
            "issues",
            EntityCollection[ServiceHealthIssue](
                self.context, ServiceHealthIssue, ResourcePath("issues", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ServiceHealth"
