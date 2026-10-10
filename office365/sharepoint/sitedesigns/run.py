from __future__ import annotations

from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class SiteDesignRun(Entity):
    @property
    def site_design_id(self) -> Optional[str]:
        """"""
        return self.properties.get("SiteDesignID", None)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Utilities.WebTemplateExtensions.SiteDesignRun"

    @property
    def action_trigger(self) -> Optional[int]:
        """Gets the ActionTrigger property"""
        return self.properties.get("ActionTrigger", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def invoked_by(self) -> Optional[str]:
        """Gets the InvokedBy property"""
        return self.properties.get("InvokedBy", None)

    @property
    def site_design_title(self) -> Optional[str]:
        """Gets the SiteDesignTitle property"""
        return self.properties.get("SiteDesignTitle", None)

    @property
    def site_design_version(self) -> Optional[int]:
        """Gets the SiteDesignVersion property"""
        return self.properties.get("SiteDesignVersion", None)

    @property
    def site_id(self) -> Optional[UUID]:
        """Gets the SiteID property"""
        return self.properties.get("SiteID", None)

    @property
    def start_time(self) -> Optional[int]:
        """Gets the StartTime property"""
        return self.properties.get("StartTime", None)

    @property
    def web_id(self) -> Optional[UUID]:
        """Gets the WebID property"""
        return self.properties.get("WebID", None)
