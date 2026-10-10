from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection
from office365.sharepoint.migrationcenter.service.performance.data import (
    PerformanceDataCollection,
)
from office365.sharepoint.migrationcenter.service.teams import MigrationCenterTeams

if TYPE_CHECKING:
    from office365.sharepoint.migrationcenter.agentgroup import AgentGroup
    from office365.sharepoint.migrationcenter.common.task import MigrationTask
    from office365.sharepoint.migrationcenter.deploy_status import (
        MigrationCenterDeployStatus,
    )
    from office365.sharepoint.migrationcenter.device import Device
    from office365.sharepoint.migrationcenter.service.storage import (
        MigrationCenterStorage,
    )
    from office365.sharepoint.migrationcenter.spflight import MigrationSPFlight


class MigrationCenterServices(Entity):
    """Migration center services"""

    def __init__(self, context, resource_path=None):
        if resource_path is None:
            resource_path = ResourcePath("Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationCenterServices")
        super().__init__(context, resource_path)

    @property
    def performance_data(self) -> PerformanceDataCollection:
        """"""
        return self.properties.get(
            "PerformanceData",
            PerformanceDataCollection(self.context, ResourcePath("PerformanceData", self.resource_path)),
        )

    @property
    def teams(self) -> MigrationCenterTeams:
        """"""
        return self.properties.get(
            "Teams",
            MigrationCenterTeams(self.context, ResourcePath("Teams", self.resource_path)),
        )

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.MigrationCenter.Service.MigrationCenterServices"

    @property
    def agent_groups(self) -> EntityCollection[AgentGroup]:
        """Gets the AgentGroups property"""
        from office365.sharepoint.migrationcenter.agentgroup import AgentGroup

        return self.properties.get(
            "AgentGroups",
            EntityCollection[AgentGroup](self.context, AgentGroup, ResourcePath("AgentGroups", self.resource_path)),
        )

    @property
    def deploy_status(self) -> MigrationCenterDeployStatus:
        """Gets the DeployStatus property"""
        from office365.sharepoint.migrationcenter.deploy_status import (
            MigrationCenterDeployStatus,
        )

        return self.properties.get(
            "DeployStatus", MigrationCenterDeployStatus(self.context, ResourcePath("DeployStatus", self.resource_path))
        )

    @property
    def devices(self) -> EntityCollection[Device]:
        """Gets the Devices property"""
        from office365.sharepoint.migrationcenter.device import Device

        return self.properties.get(
            "Devices", EntityCollection[Device](self.context, Device, ResourcePath("Devices", self.resource_path))
        )

    @property
    def sp_flight(self) -> MigrationSPFlight:
        """Gets the SPFlight property"""
        from office365.sharepoint.migrationcenter.spflight import MigrationSPFlight

        return self.properties.get(
            "SPFlight", MigrationSPFlight(self.context, ResourcePath("SPFlight", self.resource_path))
        )

    @property
    def storage(self) -> MigrationCenterStorage:
        """Gets the Storage property"""
        from office365.sharepoint.migrationcenter.service.storage import (
            MigrationCenterStorage,
        )

        return self.properties.get(
            "Storage", MigrationCenterStorage(self.context, ResourcePath("Storage", self.resource_path))
        )

    @property
    def tasks(self) -> EntityCollection[MigrationTask]:
        """Gets the Tasks property"""
        from office365.sharepoint.migrationcenter.common.task import MigrationTask

        return self.properties.get(
            "Tasks",
            EntityCollection[MigrationTask](self.context, MigrationTask, ResourcePath("Tasks", self.resource_path)),
        )
