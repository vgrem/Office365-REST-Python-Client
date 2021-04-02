from office365.calendar.calendar import Calendar
from office365.entity_collection import EntityCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class CalendarCollection(EntityCollection):

    def __init__(self, context, resource_path=None):
        super(CalendarCollection, self).__init__(context, Calendar, resource_path)

    def add(self, name):
        """Use this API to create a new calendar for a user.

        :type name: str
        :rtype: Calendar
        """
        cal = Calendar(self.context)
        cal.set_property("Name", name)
        self.add_child(cal)
        qry = CreateEntityQuery(self, cal, cal)
        self.context.add_query(qry)
        return cal
