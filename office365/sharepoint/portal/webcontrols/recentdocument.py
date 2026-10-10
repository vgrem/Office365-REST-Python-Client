from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.sharepoint.entity import Entity


class RecentDocument(Entity):
    @property
    def application(self) -> Optional[str]:
        """Gets the Application property"""
        return self.properties.get("Application", None)

    @property
    def file_name(self) -> Optional[str]:
        """Gets the FileName property"""
        return self.properties.get("FileName", None)

    @property
    def icon_url(self) -> Optional[str]:
        """Gets the IconUrl property"""
        return self.properties.get("IconUrl", None)

    @property
    def is_pinned(self) -> Optional[bool]:
        """Gets the IsPinned property"""
        return self.properties.get("IsPinned", None)

    @property
    def link_location(self) -> Optional[str]:
        """Gets the LinkLocation property"""
        return self.properties.get("LinkLocation", None)

    @property
    def time_stamp(self) -> datetime:
        """Gets the TimeStamp property"""
        return self.properties.get("TimeStamp", datetime.min)

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.WebControls.RecentDocument"

    @property
    def id(self) -> Optional[int]:
        """Gets the Id property"""
        return self.properties.get("Id", None)
