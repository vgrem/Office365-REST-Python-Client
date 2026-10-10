from __future__ import annotations

from datetime import datetime
from typing import Optional

from office365.runtime.types.odata_property import odata
from office365.sharepoint.changes.token import ChangeToken
from office365.sharepoint.changes.type import ChangeType
from office365.sharepoint.entity import Entity


class Change(Entity):
    """Base class for a change. installation."""

    def __str__(self) -> str:
        return f"{self.change_type_name} {self.time:%Y-%m-%d %H:%M}"

    def __repr__(self) -> str:
        return f"{type(self).__name__}(change_type={self.change_type_name!r}, time={self.time!r})"

    @property
    def change_type_name(self) -> str:
        return self.change_type.name

    @odata(name="ChangeToken")
    @property
    def change_token(self) -> ChangeToken:
        """Returns an ChangeToken that represents the change."""
        return self.properties.get("ChangeToken", ChangeToken())

    @odata(name="ChangeType")
    @property
    def change_type(self) -> ChangeType:
        """
        Returns an SPChangeType that indicates the type of change, including adding, updating, deleting, or renaming
        changes, but also moving items away from or into lists and folders.
        """
        return self.properties.get("ChangeType", ChangeType.None_)

    @property
    def site_id(self) -> Optional[str]:
        """
        Returns the Id of the site of the changed item
        """
        return self.properties.get("SiteId", None)

    @property
    def time(self) -> datetime:
        """
        Gets a value that specifies the time that the object was modified.
        """
        return self.properties.get("Time", datetime.min)

    @property
    def relative_time(self) -> Optional[str]:
        """Gets the RelativeTime property"""
        return self.properties.get("RelativeTime", None)
