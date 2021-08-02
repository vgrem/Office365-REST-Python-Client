from office365.outlook.calendar.calendar_group import CalendarGroup
from office365.entity_collection import EntityCollection


class CalendarGroupCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(CalendarGroupCollection, self).__init__(context, CalendarGroup, resource_path)
