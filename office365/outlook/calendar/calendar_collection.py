from office365.outlook.calendar.calendar import Calendar
from office365.entity_collection import EntityCollection


class CalendarCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(CalendarCollection, self).__init__(context, Calendar, resource_path)

    def add(self, name):
        """Use this API to create a new calendar for a user.

        :type name: str
        :rtype: Calendar
        """
        return super(CalendarCollection, self).add(name=name)
