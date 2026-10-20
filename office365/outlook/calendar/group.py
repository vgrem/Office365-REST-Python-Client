from typing import Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.calendar.calendar import Calendar
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata


class CalendarGroup(Entity):
    """
    A group of user calendars.
    """

    @odata(name="name")
    @property
    def name(self) -> Optional[str]:
        """The group name"""
        return self.properties.get("name", None)

    @odata(name="classId")
    @property
    def class_id(self) -> Optional[str]:
        """The class identifier"""
        return self.properties.get("classId", None)

    @odata(name="calendars", navigation=True)
    @property
    def calendars(self) -> EntityCollection[Calendar]:
        """The calendars in the calendar group. Navigation property. Read-only. Nullable."""
        return self.properties.get(
            "calendars", EntityCollection(self.context, Calendar, ResourcePath("calendars", self.resource_path))
        )

    @odata(name="changeKey")
    @property
    def change_key(self) -> Optional[str]:
        """Gets the changeKey property"""
        return self.properties.get("changeKey", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.CalendarGroup"
