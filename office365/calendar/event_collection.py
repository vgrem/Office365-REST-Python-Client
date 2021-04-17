from office365.calendar.event import Event
from office365.entity_collection import EntityCollection


class EventCollection(EntityCollection):
    """Event's collection"""
    def __init__(self, context, resource_path=None):
        super(EventCollection, self).__init__(context, Event, resource_path)
