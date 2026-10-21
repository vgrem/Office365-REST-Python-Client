from typing import Optional

from office365.communications.onlinemeetings.provider_type import OnlineMeetingProviderType
from office365.directory.extensions.extended_property import (
    MultiValueLegacyExtendedProperty,
    SingleValueLegacyExtendedProperty,
)
from office365.directory.permissions.require_permission import require_permission
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.email_address import EmailAddress
from office365.outlook.calendar.events.collection import EventCollection
from office365.outlook.calendar.permissions.collection import CalendarPermissionCollection
from office365.outlook.calendar.schedule.information import ScheduleInformation
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata


class Calendar(Entity):
    """
    A calendar which is a container for events. It can be a calendar for a user, or the default calendar
        of a Microsoft 365 group.
    """

    def __repr__(self):
        return self.name or self.id or self.entity_type_name

    @require_permission(
        delegated=["Calendars.Read.Shared", "Calendars.ReadWrite.Shared"], notes="No application permission"
    )
    def allowed_calendar_sharing_roles(self, user) -> ClientResult[StringCollection]:
        """Args:
        user (str): User identifier or principal name
        """
        params = {"user": user}
        return_type = ClientResult(self.context, StringCollection())
        qry = FunctionQuery(self, "allowedCalendarSharingRoles", params, return_type)
        self.context.add_query(qry)
        return return_type

    @require_permission(
        delegated=["Calendars.Read", "Calendars.ReadWrite", "Calendars.Read.Shared", "Calendars.ReadWrite.Shared"],
        application=["Calendars.Read", "Calendars.ReadWrite"],
    )
    def get_schedule(
        self, schedules, start_time, end_time, availability_view_interval=30
    ) -> ClientResult[ClientValueCollection[ScheduleInformation]]:
        """Get the free/busy availability information for a collection of users, distributions lists, or resources
        (rooms or equipment) for a specified time period.

        Args:
            end_time (datetime.datetime): The date, time, and time zone that the period ends.
            availability_view_interval (int): Represents the duration of a time slot in an availabilityView in the
              response. The default is 30 minutes, minimum is 5, maximum is 1440. Optional.
            start_time (datetime.datetime): The date, time, and time zone that the period starts.
            schedules (list[str]): A collection of SMTP addresses of users, distribution lists, or resources to get
              availability information for.
        """
        payload = {
            "schedules": schedules,
            "startTime": DateTimeTimeZone.parse(start_time),
            "endTime": DateTimeTimeZone.parse(end_time),
            "availabilityViewInterval": availability_view_interval,
        }
        return_type = ClientResult(self.context, ClientValueCollection(ScheduleInformation))
        qry = ServiceOperationQuery(self, "getSchedule", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    @odata(name="allowedOnlineMeetingProviders")
    @property
    def allowed_online_meeting_providers(self) -> StringCollection:
        """
        Represent the online meeting service providers that can be used to create online meetings in this calendar.
        Possible values are: unknown, skypeForBusiness, skypeForConsumer, teamsForBusiness.
        """
        return self.properties.get("allowedOnlineMeetingProviders", StringCollection())

    @odata(name="canEdit")
    @property
    def can_edit(self) -> Optional[bool]:
        """
        true if the user can write to the calendar, false otherwise.
        This property is true for the user who created the calendar.
        This property is also true for a user who has been shared a calendar and granted write access.
        """
        return self.properties.get("canEdit", None)

    @odata(name="canShare")
    @property
    def can_share(self) -> Optional[bool]:
        """
        true if the user has the permission to share the calendar, false otherwise.
        Only the user who created the calendar can share it.
        """
        return self.properties.get("canShare", None)

    @odata(name="canViewPrivateItems")
    @property
    def can_view_private_items(self) -> Optional[bool]:
        """
        true if the user can read calendar items that have been marked private, false otherwise.
        """
        return self.properties.get("canViewPrivateItems", None)

    @odata(name="changeKey")
    @property
    def change_key(self) -> Optional[str]:
        """
        Identifies the version of the calendar object. Every time the calendar is changed, changeKey changes as well.
        This allows Exchange to apply changes to the correct version of the object.
        """
        return self.properties.get("changeKey", None)

    @odata(name="color")
    @property
    def color(self) -> Optional[str]:
        """
        Specifies the color theme to distinguish the calendar from other calendars in a UI.
        The property values are: auto, lightBlue, lightGreen, lightOrange, lightGray, lightYellow, lightTeal,
        lightPink, lightBrown, lightRed, maxColor.
        """
        return self.properties.get("color", None)

    @odata(name="defaultOnlineMeetingProvider")
    @property
    def default_online_meeting_provider(self) -> OnlineMeetingProviderType:
        """
        The default online meeting provider for meetings sent from this calendar.
        Possible values are: unknown, skypeForBusiness, skypeForConsumer, teamsForBusiness.
        """
        return self.properties.get("defaultOnlineMeetingProvider", OnlineMeetingProviderType.unknown)

    @odata(name="name")
    @property
    def name(self) -> Optional[str]:
        """The calendar name"""
        return self.properties.get("name", None)

    @odata(name="isDefaultCalendar")
    @property
    def is_default_calendar(self) -> Optional[bool]:
        """
        true if this is the default calendar where new events are created by default, false otherwise.
        """
        return self.properties.get("isDefaultCalendar", None)

    @odata(name="isRemovable")
    @property
    def is_removable(self) -> Optional[bool]:
        """
        Indicates whether this user calendar can be deleted from the user mailbox.
        """
        return self.properties.get("isRemovable", None)

    @odata(name="isTallyingResponses")
    @property
    def is_tallying_responses(self) -> Optional[bool]:
        """
        Indicates whether this user calendar supports tracking of meeting responses.
        Only meeting invites sent from users' primary calendars support tracking of meeting responses.
        """
        return self.properties.get("isTallyingResponses", None)

    @odata(name="owner")
    @property
    def owner(self) -> EmailAddress:
        """If set, this represents the user who created or added the calendar.
        For a calendar that the user created or added, the owner property is set to the user. For a calendar shared
        with the user, the owner property is set to the person who shared that calendar with the user.
        """
        return self.properties.get("owner", EmailAddress())

    @odata(name="events", navigation=True)
    @property
    def events(self) -> EventCollection:
        """The events in the calendar. Navigation property. Read-only."""
        return self.properties.get("events", EventCollection(self.context, ResourcePath("events", self.resource_path)))

    @odata(name="calendarView", navigation=True)
    @property
    def calendar_view(self) -> EventCollection:
        """The calendar view for the calendar. Navigation property. Read-only."""
        return self.properties.get(
            "calendarView", EventCollection(self.context, ResourcePath("calendarView", self.resource_path))
        )

    @odata(name="calendarPermissions", navigation=True)
    @property
    def calendar_permissions(self) -> CalendarPermissionCollection:
        """The permissions of the users with whom the calendar is shared."""
        return self.properties.get(
            "calendarPermissions",
            CalendarPermissionCollection(self.context, ResourcePath("calendarPermissions", self.resource_path)),
        )

    @odata(name="multiValueExtendedProperties", navigation=True)
    @property
    def multi_value_extended_properties(self) -> EntityCollection[MultiValueLegacyExtendedProperty]:
        """The collection of multi-value extended properties defined for the Calendar."""
        return self.properties.get(
            "multiValueExtendedProperties",
            EntityCollection(
                self.context,
                MultiValueLegacyExtendedProperty,
                ResourcePath("multiValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="singleValueExtendedProperties", navigation=True)
    @property
    def single_value_extended_properties(self) -> EntityCollection[SingleValueLegacyExtendedProperty]:
        """The collection of single-value extended properties defined for the calendar. Read-only. Nullable."""
        return self.properties.get(
            "singleValueExtendedProperties",
            EntityCollection(
                self.context,
                SingleValueLegacyExtendedProperty,
                ResourcePath("singleValueExtendedProperties", self.resource_path),
            ),
        )

    @odata(name="hexColor")
    @property
    def hex_color(self) -> Optional[str]:
        """Gets the hexColor property"""
        return self.properties.get("hexColor", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Calendar"
