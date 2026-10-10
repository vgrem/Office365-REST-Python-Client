from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from office365.sharepoint.entity import Entity


class SPMachineLearningWorkItem(Entity):
    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ContentCenter.SPMachineLearningWorkItem"

    @property
    def created(self) -> Optional[datetime]:
        """Gets the Created property"""
        return self.properties.get("Created", datetime.min)

    @property
    def deliver_date(self) -> Optional[datetime]:
        """Gets the DeliverDate property"""
        return self.properties.get("DeliverDate", datetime.min)

    @property
    def error_message(self) -> Optional[str]:
        """Gets the ErrorMessage property"""
        return self.properties.get("ErrorMessage", None)

    @property
    def id_(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def status(self) -> Optional[str]:
        """Gets the Status property"""
        return self.properties.get("Status", None)

    @property
    def status_code(self) -> Optional[int]:
        """Gets the StatusCode property"""
        return self.properties.get("StatusCode", None)

    @property
    def target_server_relative_url(self) -> Optional[str]:
        """Gets the TargetServerRelativeUrl property"""
        return self.properties.get("TargetServerRelativeUrl", None)

    @property
    def target_site_id(self) -> Optional[UUID]:
        """Gets the TargetSiteId property"""
        return self.properties.get("TargetSiteId", None)

    @property
    def target_site_url(self) -> Optional[str]:
        """Gets the TargetSiteUrl property"""
        return self.properties.get("TargetSiteUrl", None)

    @property
    def target_unique_id(self) -> Optional[UUID]:
        """Gets the TargetUniqueId property"""
        return self.properties.get("TargetUniqueId", None)

    @property
    def target_web_id(self) -> Optional[UUID]:
        """Gets the TargetWebId property"""
        return self.properties.get("TargetWebId", None)

    @property
    def target_web_server_relative_url(self) -> Optional[str]:
        """Gets the TargetWebServerRelativeUrl property"""
        return self.properties.get("TargetWebServerRelativeUrl", None)

    @property
    def type_(self) -> Optional[UUID]:
        """Gets the Type property"""
        return self.properties.get("Type", None)

    @property
    def id(self) -> Optional[UUID]:
        """Gets the ID property"""
        return self.properties.get("ID", None)

    @property
    def type(self) -> Optional[UUID]:
        """Gets the Type property"""
        return self.properties.get("Type", None)
