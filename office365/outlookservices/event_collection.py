from office365.outlookservices.event import Event
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery


class EventCollection(ClientObjectCollection):
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
