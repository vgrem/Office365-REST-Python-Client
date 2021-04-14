from office365.calendar.event import Event
from office365.entity_collection import EntityCollection
from office365.runtime.queries.create_entity_query import CreateEntityQuery


class EventCollection(EntityCollection):
    """Event's collection"""
    def __init__(self, context, resource_path=None):
        super(EventCollection, self).__init__(context, Event, resource_path)

    def add_from_json(self, event_creation_information):
        """Creates a Event resource from JSON"""
        event = Event(self.context)
        self.add_child(event)
        qry = CreateEntityQuery(self, event_creation_information, event)
        self.context.add_query(qry)
        return event
