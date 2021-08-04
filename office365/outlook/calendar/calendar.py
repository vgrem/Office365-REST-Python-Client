from office365.outlook.calendar.calendar_permission import CalendarPermission
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.emailAddress import EmailAddress
from office365.outlook.calendar.event import Event
from office365.outlook.calendar.schedule_information import ScheduleInformation
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class Calendar(Entity):
    """
    A calendar which is a container for events. It can be a calendar for a user, or the default calendar
        of a Microsoft 365 group.
    """

    def get_schedule(self, schedules, startTime=None, endTime=None, availabilityViewInterval=30):
        """
        Get the free/busy availability information for a collection of users, distributions lists, or resources
        (rooms or equipment) for a specified time period.

        :param datetime.datetime endTime: The date, time, and time zone that the period ends.
        :param int availabilityViewInterval: Represents the duration of a time slot in an availabilityView
             in the response. The default is 30 minutes, minimum is 5, maximum is 1440. Optional.
        :param datetime.datetime startTime: The date, time, and time zone that the period starts.
        :param list[str] schedules: A collection of SMTP addresses of users, distribution lists,
            or resources to get availability information for.
        """
        payload = {
            "schedules": schedules,
            "startTime": DateTimeTimeZone.parse(startTime),
            "endTime": DateTimeTimeZone.parse(endTime),
            "availabilityViewInterval": availabilityViewInterval
        }
        result = ClientResult(self.context, ClientValueCollection(ScheduleInformation))
        qry = ServiceOperationQuery(self, "getSchedule", None, payload, None, result)
        self.context.add_query(qry)
        return result

    @property
    def can_edit(self):
        """
        true if the user can write to the calendar, false otherwise.
        This property is true for the user who created the calendar.
        This property is also true for a user who has been shared a calendar and granted write access.

        :rtype: bool or None
        """
        return self.properties.get('canEdit', None)

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
        return self.properties.get('owner', EmailAddress())

    @property
    def events(self):
        """The events in the calendar. Navigation property. Read-only."""
        return self.properties.get('events',
                                   EntityCollection(self.context, Event, ResourcePath("events", self.resource_path)))

    @property
    def calendar_view(self):
        """The calendar view for the calendar. Navigation property. Read-only."""
        return self.get_property('calendarView',
                                 EntityCollection(self.context, Event,
                                                  ResourcePath("calendarView", self.resource_path)))

    @property
    def calendar_permissions(self):
        """The permissions of the users with whom the calendar is shared."""
        return self.properties.get('calendarPermissions',
                                   EntityCollection(self.context, CalendarPermission,
                                                    ResourcePath("calendarPermissions", self.resource_path)))
