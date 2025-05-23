from office365.booking.staff.member_base import BookingStaffMemberBase


class BookingStaffMember(BookingStaffMemberBase):
    """Represents a staff member who provides services in a bookingBusiness.

    Staff members can be part of the Microsoft 365 tenant where the booking business is configured,
    or they can use email services from other email providers."""
