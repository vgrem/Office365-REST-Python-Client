from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.booking.staff.member_base import BookingStaffMemberBase
from office365.runtime.client_value_collection import ClientValueCollection

if TYPE_CHECKING:
    from office365.booking.staffmembershipstatus import BookingStaffMembershipStatus
    from office365.booking.staffrole import BookingStaffRole
    from office365.booking.work_hours import BookingWorkHours


class BookingStaffMember(BookingStaffMemberBase):
    """Represents a staff member who provides services in a bookingBusiness.

    Staff members can be part of the Microsoft 365 tenant where the booking business is configured,
    or they can use email services from other email providers."""

    @property
    def availability_is_affected_by_personal_calendar(self) -> Optional[bool]:
        """Gets the availabilityIsAffectedByPersonalCalendar property"""
        return self.properties.get("availabilityIsAffectedByPersonalCalendar", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def email_address(self) -> Optional[str]:
        """Gets the emailAddress property"""
        return self.properties.get("emailAddress", None)

    @property
    def is_email_notification_enabled(self) -> Optional[bool]:
        """Gets the isEmailNotificationEnabled property"""
        return self.properties.get("isEmailNotificationEnabled", None)

    @property
    def last_updated_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def membership_status(self) -> BookingStaffMembershipStatus:
        """Gets the membershipStatus property"""
        from office365.booking.staffmembershipstatus import BookingStaffMembershipStatus

        return self.properties.get("membershipStatus", BookingStaffMembershipStatus.active)

    @property
    def role(self) -> BookingStaffRole:
        """Gets the role property"""
        from office365.booking.staffrole import BookingStaffRole

        return self.properties.get("role", BookingStaffRole.guest)

    @property
    def time_zone(self) -> Optional[str]:
        """Gets the timeZone property"""
        return self.properties.get("timeZone", None)

    @property
    def use_business_hours(self) -> Optional[bool]:
        """Gets the useBusinessHours property"""
        return self.properties.get("useBusinessHours", None)

    @property
    def working_hours(self) -> ClientValueCollection[BookingWorkHours]:
        """Gets the workingHours property"""
        from office365.booking.work_hours import BookingWorkHours

        return self.properties.get("workingHours", ClientValueCollection[BookingWorkHours](BookingWorkHours))

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingStaffMember"
