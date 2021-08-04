from office365.entity_collection import EntityCollection
from office365.outlook.calendar.calendar import Calendar
from office365.entity import Entity
from office365.runtime.resource_path import ResourcePath


class CalendarGroup(Entity):
    """
    A group of user calendars.
    """

    @property
    def calendars(self):
        """The calendars in the calendar group. Navigation property. Read-only. Nullable."""
        return self.properties.get('calendars',
                                   EntityCollection(self.context, Calendar,
                                                    ResourcePath("calendars", self.resource_path)))
