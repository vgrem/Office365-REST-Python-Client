from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath

if TYPE_CHECKING:
    from office365.common.configuration_baseline import ConfigurationBaseline
    from office365.common.configuration_drift import ConfigurationDrift
    from office365.common.configuration_monitor import ConfigurationMonitor
    from office365.common.configuration_monitoring_result import (
        ConfigurationMonitoringResult,
    )
    from office365.common.configuration_snapshot_job import ConfigurationSnapshotJob


class ConfigurationManagement(Entity):
    @property
    def configuration_drifts(self) -> EntityCollection[ConfigurationDrift]:
        """Gets the configurationDrifts property"""
        from office365.common.configuration_drift import ConfigurationDrift

        return self.properties.get(
            "configurationDrifts",
            EntityCollection[ConfigurationDrift](
                self.context, ConfigurationDrift, ResourcePath("configurationDrifts", self.resource_path)
            ),
        )

    @property
    def configuration_monitoring_results(self) -> EntityCollection[ConfigurationMonitoringResult]:
        """Gets the configurationMonitoringResults property"""
        from office365.common.configuration_monitoring_result import (
            ConfigurationMonitoringResult,
        )

        return self.properties.get(
            "configurationMonitoringResults",
            EntityCollection[ConfigurationMonitoringResult](
                self.context,
                ConfigurationMonitoringResult,
                ResourcePath("configurationMonitoringResults", self.resource_path),
            ),
        )

    @property
    def configuration_monitors(self) -> EntityCollection[ConfigurationMonitor]:
        """Gets the configurationMonitors property"""
        from office365.common.configuration_monitor import ConfigurationMonitor

        return self.properties.get(
            "configurationMonitors",
            EntityCollection[ConfigurationMonitor](
                self.context, ConfigurationMonitor, ResourcePath("configurationMonitors", self.resource_path)
            ),
        )

    @property
    def configuration_snapshot_jobs(self) -> EntityCollection[ConfigurationSnapshotJob]:
        """Gets the configurationSnapshotJobs property"""
        from office365.common.configuration_snapshot_job import ConfigurationSnapshotJob

        return self.properties.get(
            "configurationSnapshotJobs",
            EntityCollection[ConfigurationSnapshotJob](
                self.context, ConfigurationSnapshotJob, ResourcePath("configurationSnapshotJobs", self.resource_path)
            ),
        )

    @property
    def configuration_snapshots(self) -> EntityCollection[ConfigurationBaseline]:
        """Gets the configurationSnapshots property"""
        from office365.common.configuration_baseline import ConfigurationBaseline

        return self.properties.get(
            "configurationSnapshots",
            EntityCollection[ConfigurationBaseline](
                self.context, ConfigurationBaseline, ResourcePath("configurationSnapshots", self.resource_path)
            ),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.ConfigurationManagement"
