from office365.outlookservices.event import Event
from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ClientQuery


class EventCollection(ClientObjectCollection):
    """Event's collection"""

    # The object type this collection holds
    item_type = Event

    def add_from_json(self, event_creation_information):
        """Creates a Event resource from JSON"""
        event = Event(self.context)
        qry = ClientQuery.create_entry_query(self, event_creation_information)
        self.context.add_query(qry, event)
        self.add_child(event)
        return event
