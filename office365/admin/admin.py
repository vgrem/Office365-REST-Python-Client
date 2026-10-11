from __future__ import annotations

from typing import TYPE_CHECKING

from office365.admin.microsoft365.apps import AdminMicrosoft365Apps
from office365.admin.people.settings import PeopleAdminSettings
from office365.admin.report_settings import AdminReportSettings
from office365.admin.sharepoint.sharepoint import Sharepoint
from office365.entity import Entity
from office365.intune.servicecommunications.announcement import ServiceAnnouncement
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.admin.configuration_management import ConfigurationManagement
    from office365.admin.edge.edge import Edge
    from office365.admin.exchange.admin import ExchangeAdmin
    from office365.teams.admin_root import TeamsAdminRoot


class Admin(Entity):
    """Entity that acts as a container for administrator functionality."""

    @odata(name="microsoft365Apps")
    @property
    def microsoft365_apps(self) -> AdminMicrosoft365Apps:
        """A container for the Microsoft 365 apps admin functionality."""
        return self.properties.get(
            "microsoft365Apps",
            AdminMicrosoft365Apps(self.context, ResourcePath("microsoft365Apps", self.resource_path)),
        )

    @property
    def sharepoint(self) -> Sharepoint:
        """A container for administrative resources to manage tenant-level settings for SharePoint and OneDrive."""
        return self.properties.get(
            "sharepoint",
            Sharepoint(self.context, ResourcePath("sharepoint", self.resource_path)),
        )

    @odata(name="serviceAnnouncement")
    @property
    def service_announcement(self) -> ServiceAnnouncement:
        """A container for service communications resources. Read-only."""
        return self.properties.get(
            "serviceAnnouncement",
            ServiceAnnouncement(self.context, ResourcePath("serviceAnnouncement", self.resource_path)),
        )

    @odata(name="reportSettings")
    @property
    def report_settings(self) -> AdminReportSettings:
        """A container for administrative resources to manage reports."""
        return self.properties.get(
            "reportSettings",
            AdminReportSettings(self.context, ResourcePath("reportSettings", self.resource_path)),
        )

    @property
    def people(self) -> PeopleAdminSettings:
        """Represents a setting to control people-related admin settings in the tenant."""
        return self.properties.get(
            "people",
            PeopleAdminSettings(self.context, ResourcePath("people", self.resource_path)),
        )

    @property
    def edge(self) -> Edge:
        """Gets the edge property"""
        from office365.admin.edge.edge import Edge

        return self.properties.get("edge", Edge(self.context, ResourcePath("edge", self.resource_path)))

    @property
    def exchange(self) -> ExchangeAdmin:
        """Gets the exchange property"""
        from office365.admin.exchange.admin import ExchangeAdmin

        return self.properties.get("exchange", ExchangeAdmin(self.context, ResourcePath("exchange", self.resource_path)))

    @property
    def teams(self) -> TeamsAdminRoot:
        """Gets the teams property"""
        from office365.teams.admin_root import TeamsAdminRoot

        return self.properties.get("teams", TeamsAdminRoot(self.context, ResourcePath("teams", self.resource_path)))

    @property
    def configuration_management(self) -> ConfigurationManagement:
        """Gets the configurationManagement property"""
        from office365.admin.configuration_management import ConfigurationManagement

        return self.properties.get(
            "configurationManagement",
            ConfigurationManagement(self.context, ResourcePath("configurationManagement", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Admin"
