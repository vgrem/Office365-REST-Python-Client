from datetime import datetime
from typing import Optional

from office365.entity import Entity
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


class OutlookItem(Entity):
    @property
    def change_key(self) -> Optional[str]:
        """
        Identifies the version of the item. Every time the item is changed, changeKey changes as well.
        This allows Exchange to apply changes to the correct version of the object.
        """
        return self.properties.get("ChangeKey", None)

    @odata(name="categories")
    @property
    def categories(self) -> StringCollection:
        """The categories associated with the item"""
        return self.properties.get("categories", StringCollection())

    @odata(name="createdDateTime", readonly=True)
    @property
    def created_datetime(self) -> datetime:
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get("createdDateTime", datetime.min)

    @odata(name="lastModifiedDateTime", readonly=True)
    @property
    def last_modified_datetime(self) -> datetime:
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.
        For example, midnight UTC on Jan 1, 2014 is 2014-01-01T00:00:00Z
        """
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @odata(name="createdDateTime", readonly=True)
    @property
    def created_date_time(self) -> datetime:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @odata(name="lastModifiedDateTime", readonly=True)
    @property
    def last_modified_date_time(self) -> datetime:
        """Gets the lastModifiedDateTime property"""
        return self.properties.get("lastModifiedDateTime", datetime.min)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.OutlookItem"
