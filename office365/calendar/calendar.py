from office365.calendar.emailAddress import EmailAddress
from office365.calendar.event_collection import EventCollection
from office365.entity import Entity
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath


class Calendar(Entity):
    """
    A calendar which is a container for events. It can be a calendar for a user, or the default calendar
        of a Microsoft 365 group.
    """

    def update(self):
        """Updates a Calendar."""
        qry = UpdateEntityQuery(self)
        self.context.add_query(qry)
        return self

    def delete_object(self):
        """Deletes the calendar."""
        qry = DeleteEntityQuery(self)
        self.context.add_query(qry)
        self.remove_from_parent_collection()
        return self

    @property
    def name(self):
        """
        The calendar name.
        """
        return self.properties.get('name', None)

    @property
    def owner(self):
        """If set, this represents the user who created or added the calendar.
           For a calendar that the user created or added, the owner property is set to the user. For a calendar shared
           with the user, the owner property is set to the person who shared that calendar with the user.
        """
        return self.properties.get('owner', None)

    @property
    def events(self):
        """The events in the calendar. Navigation property. Read-only."""
        return self.properties.get('events',
                                   EventCollection(self.context, ResourcePath("events", self.resource_path)))

    @property
    def calendarView(self):
        """The calendar view for the calendar. Navigation property. Read-only."""
        return self.properties.get('calendarView',
                                   EventCollection(self.context, ResourcePath("calendarView", self.resource_path)))
