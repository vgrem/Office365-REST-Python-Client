from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.backuprestore.service_status import ServiceStatus
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.security.health_issue import HealthIssue
from office365.security.healthissues.deploymentstatus import DeploymentStatus
from office365.security.healthissues.sensorhealthstatus import (
    SensorHealthStatus,
)
from office365.security.healthissues.sensortype import SensorType

if TYPE_CHECKING:
    from office365.security.sensor_settings import SensorSettings


class Sensor(Entity):
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def deployment_status(self) -> DeploymentStatus:
        """Gets the deploymentStatus property"""
        return self.properties.get("deploymentStatus", DeploymentStatus.upToDate)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def domain_name(self) -> Optional[str]:
        """Gets the domainName property"""
        return self.properties.get("domainName", None)

    @property
    def health_status(self) -> SensorHealthStatus:
        """Gets the healthStatus property"""
        return self.properties.get("healthStatus", SensorHealthStatus.healthy)

    @property
    def open_health_issues_count(self) -> Optional[int]:
        """Gets the openHealthIssuesCount property"""
        return self.properties.get("openHealthIssuesCount", None)

    @property
    def sensor_type(self) -> SensorType:
        """Gets the sensorType property"""
        return self.properties.get("sensorType", SensorType.adConnectIntegrated)

    @property
    def service_status(self) -> ServiceStatus:
        """Gets the serviceStatus property"""
        return self.properties.get("serviceStatus", ServiceStatus())

    @property
    def version(self) -> Optional[str]:
        """Gets the version property"""
        return self.properties.get("version", None)

    @property
    def health_issues(self) -> EntityCollection[HealthIssue]:
        """Gets the healthIssues property"""
        return self.properties.get(
            "healthIssues",
            EntityCollection[HealthIssue](self.context, HealthIssue, ResourcePath("healthIssues", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.security.Sensor"

    @property
    def settings(self) -> SensorSettings:
        """Gets the settings property"""
        from office365.security.sensor_settings import SensorSettings

        return self.properties.get("settings", SensorSettings())
