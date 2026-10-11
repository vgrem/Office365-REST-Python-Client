from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.runtime.types.odata_property import odata
from office365.teams.schedule.groups.group import SchedulingGroup
from office365.teams.schedule.shifts.open.change_request import OpenShiftChangeRequest
from office365.teams.schedule.shifts.shift import Shift
from office365.teams.schedule.time_off_reason import TimeOffReason

if TYPE_CHECKING:
    from office365.directory.identitygovernance.operationstatus import OperationStatus
    from office365.outlook.calendar.dayofweek import DayOfWeek
    from office365.teams.schedule.day_note import DayNote
    from office365.teams.schedule.open_shift import OpenShift
    from office365.teams.schedule.shifts.offer.request import OfferShiftRequest
    from office365.teams.schedule.swap_shifts_change_request import (
        SwapShiftsChangeRequest,
    )
    from office365.teams.schedule.time_card import TimeCard
    from office365.teams.schedule.time_clock_settings import TimeClockSettings
    from office365.teams.schedule.time_off import TimeOff
    from office365.teams.schedule.time_off_request import TimeOffRequest


class Schedule(Entity):
    """A collection of schedulingGroup objects, shift objects, timeOffReason objects,
    and timeOff objects within a team."""

    @property
    def time_zone(self) -> str | None:
        """Indicates the time zone of the shifts team using tz database format. Required."""
        return self.properties.get("timeZone", None)

    @time_zone.setter
    def time_zone(self, value):
        self.set_property("timeZone", value)

    @odata(name="openShiftChangeRequests")
    @property
    def open_shift_change_requests(self) -> EntityCollection[OpenShiftChangeRequest]:
        """The shifts in the shifts."""
        return self.properties.get(
            "openShiftChangeRequests",
            EntityCollection(
                self.context,
                OpenShiftChangeRequest,
                ResourcePath("openShiftChangeRequests", self.resource_path),
            ),
        )

    @property
    def shifts(self) -> EntityCollection[Shift]:
        """The shifts in the shifts."""
        return self.properties.get(
            "shifts",
            EntityCollection(self.context, Shift, ResourcePath("shifts", self.resource_path)),
        )

    @odata(name="schedulingGroups")
    @property
    def scheduling_groups(self) -> EntityCollection[SchedulingGroup]:
        """The logical grouping of users in the shifts (usually by role)."""
        return self.properties.get(
            "schedulingGroups",
            EntityCollection(
                self.context,
                SchedulingGroup,
                ResourcePath("schedulingGroups", self.resource_path),
            ),
        )

    @odata(name="timeOffReasons")
    @property
    def time_off_reasons(self) -> EntityCollection[TimeOffReason]:
        """The set of reasons for a time off in the schedule."""
        return self.properties.get(
            "timeOffReasons",
            EntityCollection(
                self.context,
                TimeOffReason,
                ResourcePath("timeOffReasons", self.resource_path),
            ),
        )

    @property
    def enabled(self) -> Optional[bool]:
        """Gets the enabled property"""
        return self.properties.get("enabled", None)

    @property
    def is_activities_included_when_copying_shifts_enabled(self) -> Optional[bool]:
        """Gets the isActivitiesIncludedWhenCopyingShiftsEnabled property"""
        return self.properties.get("isActivitiesIncludedWhenCopyingShiftsEnabled", None)

    @property
    def offer_shift_requests_enabled(self) -> Optional[bool]:
        """Gets the offerShiftRequestsEnabled property"""
        return self.properties.get("offerShiftRequestsEnabled", None)

    @property
    def open_shifts_enabled(self) -> Optional[bool]:
        """Gets the openShiftsEnabled property"""
        return self.properties.get("openShiftsEnabled", None)

    @property
    def provision_status(self) -> OperationStatus:
        """Gets the provisionStatus property"""
        from office365.directory.identitygovernance.operationstatus import (
            OperationStatus,
        )

        return self.properties.get("provisionStatus", OperationStatus.NotStarted)

    @property
    def provision_status_code(self) -> Optional[str]:
        """Gets the provisionStatusCode property"""
        return self.properties.get("provisionStatusCode", None)

    @property
    def start_day_of_week(self) -> DayOfWeek:
        """Gets the startDayOfWeek property"""
        from office365.outlook.calendar.dayofweek import DayOfWeek

        return self.properties.get("startDayOfWeek", DayOfWeek.sunday)

    @property
    def swap_shifts_requests_enabled(self) -> Optional[bool]:
        """Gets the swapShiftsRequestsEnabled property"""
        return self.properties.get("swapShiftsRequestsEnabled", None)

    @property
    def time_clock_enabled(self) -> Optional[bool]:
        """Gets the timeClockEnabled property"""
        return self.properties.get("timeClockEnabled", None)

    @property
    def time_clock_settings(self) -> TimeClockSettings:
        """Gets the timeClockSettings property"""
        from office365.teams.schedule.time_clock_settings import TimeClockSettings

        return self.properties.get("timeClockSettings", TimeClockSettings())

    @property
    def time_off_requests_enabled(self) -> Optional[bool]:
        """Gets the timeOffRequestsEnabled property"""
        return self.properties.get("timeOffRequestsEnabled", None)

    @property
    def workforce_integration_ids(self) -> StringCollection:
        """Gets the workforceIntegrationIds property"""
        return self.properties.get("workforceIntegrationIds", StringCollection())

    @property
    def day_notes(self) -> EntityCollection[DayNote]:
        """Gets the dayNotes property"""
        from office365.teams.schedule.day_note import DayNote

        return self.properties.get(
            "dayNotes", EntityCollection[DayNote](self.context, DayNote, ResourcePath("dayNotes", self.resource_path))
        )

    @property
    def offer_shift_requests(self) -> EntityCollection[OfferShiftRequest]:
        """Gets the offerShiftRequests property"""
        from office365.teams.schedule.shifts.offer.request import OfferShiftRequest

        return self.properties.get(
            "offerShiftRequests",
            EntityCollection[OfferShiftRequest](
                self.context, OfferShiftRequest, ResourcePath("offerShiftRequests", self.resource_path)
            ),
        )

    @property
    def open_shifts(self) -> EntityCollection[OpenShift]:
        """Gets the openShifts property"""
        from office365.teams.schedule.open_shift import OpenShift

        return self.properties.get(
            "openShifts",
            EntityCollection[OpenShift](self.context, OpenShift, ResourcePath("openShifts", self.resource_path)),
        )

    @property
    def swap_shifts_change_requests(self) -> EntityCollection[SwapShiftsChangeRequest]:
        """Gets the swapShiftsChangeRequests property"""
        from office365.teams.schedule.swap_shifts_change_request import (
            SwapShiftsChangeRequest,
        )

        return self.properties.get(
            "swapShiftsChangeRequests",
            EntityCollection[SwapShiftsChangeRequest](
                self.context, SwapShiftsChangeRequest, ResourcePath("swapShiftsChangeRequests", self.resource_path)
            ),
        )

    @property
    def time_cards(self) -> EntityCollection[TimeCard]:
        """Gets the timeCards property"""
        from office365.teams.schedule.time_card import TimeCard

        return self.properties.get(
            "timeCards",
            EntityCollection[TimeCard](self.context, TimeCard, ResourcePath("timeCards", self.resource_path)),
        )

    @property
    def time_off_requests(self) -> EntityCollection[TimeOffRequest]:
        """Gets the timeOffRequests property"""
        from office365.teams.schedule.time_off_request import TimeOffRequest

        return self.properties.get(
            "timeOffRequests",
            EntityCollection[TimeOffRequest](
                self.context, TimeOffRequest, ResourcePath("timeOffRequests", self.resource_path)
            ),
        )

    @property
    def times_off(self) -> EntityCollection[TimeOff]:
        """Gets the timesOff property"""
        from office365.teams.schedule.time_off import TimeOff

        return self.properties.get(
            "timesOff", EntityCollection[TimeOff](self.context, TimeOff, ResourcePath("timesOff", self.resource_path))
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.Schedule"
