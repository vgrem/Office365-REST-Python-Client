from office365.calendar.calendar_collection import CalendarCollection
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
                                   CalendarCollection(self.context, ResourcePath("calendars", self.resource_path)))
