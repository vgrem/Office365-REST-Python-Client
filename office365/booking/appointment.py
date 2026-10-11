from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.booking.customers.informationbase import (
        BookingCustomerInformationBase,
    )
    from office365.booking.pricetype import BookingPriceType
    from office365.booking.reminder import BookingReminder
    from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
    from office365.outlook.mail.location import Location
    from office365.runtime.types.duration import timedelta


class BookingAppointment(Entity):
    """
    Represents a business in Microsoft Bookings. This is the top level object in the Microsoft Bookings API.
    It contains business information and related business objects such as appointments, customers, services,
    and staff members.
    """

    @property
    def additional_information(self) -> Optional[str]:
        """Gets the additionalInformation property"""
        return self.properties.get("additionalInformation", None)

    @property
    def anonymous_join_web_url(self) -> Optional[str]:
        """Gets the anonymousJoinWebUrl property"""
        return self.properties.get("anonymousJoinWebUrl", None)

    @property
    def appointment_label(self) -> Optional[str]:
        """Gets the appointmentLabel property"""
        return self.properties.get("appointmentLabel", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def customer_email_address(self) -> Optional[str]:
        """Gets the customerEmailAddress property"""
        return self.properties.get("customerEmailAddress", None)

    @property
    def customer_name(self) -> Optional[str]:
        """Gets the customerName property"""
        return self.properties.get("customerName", None)

    @property
    def customer_notes(self) -> Optional[str]:
        """Gets the customerNotes property"""
        return self.properties.get("customerNotes", None)

    @property
    def customer_phone(self) -> Optional[str]:
        """Gets the customerPhone property"""
        return self.properties.get("customerPhone", None)

    @property
    def customers(self) -> ClientValueCollection[BookingCustomerInformationBase]:
        """Gets the customers property"""
        from office365.booking.customers.informationbase import (
            BookingCustomerInformationBase,
        )

        return self.properties.get(
            "customers", ClientValueCollection[BookingCustomerInformationBase](BookingCustomerInformationBase)
        )

    @property
    def customer_time_zone(self) -> Optional[str]:
        """Gets the customerTimeZone property"""
        return self.properties.get("customerTimeZone", None)

    @property
    def duration(self) -> Optional[timedelta]:
        """Gets the duration property"""
        return self.properties.get("duration", None)

    @property
    def end_date_time(self) -> DateTimeTimeZone:
        """Gets the endDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("endDateTime", DateTimeTimeZone())

    @property
    def filled_attendees_count(self) -> Optional[int]:
        """Gets the filledAttendeesCount property"""
        return self.properties.get("filledAttendeesCount", None)

    @property
    def is_customer_allowed_to_manage_booking(self) -> Optional[bool]:
        """Gets the isCustomerAllowedToManageBooking property"""
        return self.properties.get("isCustomerAllowedToManageBooking", None)

    @property
    def is_location_online(self) -> Optional[bool]:
        """Gets the isLocationOnline property"""
        return self.properties.get("isLocationOnline", None)

    @property
    def join_web_url(self) -> Optional[str]:
        """Gets the joinWebUrl property"""
        return self.properties.get("joinWebUrl", None)

    @property
    def last_updated_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def maximum_attendees_count(self) -> Optional[int]:
        """Gets the maximumAttendeesCount property"""
        return self.properties.get("maximumAttendeesCount", None)

    @property
    def opt_out_of_customer_email(self) -> Optional[bool]:
        """Gets the optOutOfCustomerEmail property"""
        return self.properties.get("optOutOfCustomerEmail", None)

    @property
    def post_buffer(self) -> Optional[timedelta]:
        """Gets the postBuffer property"""
        return self.properties.get("postBuffer", None)

    @property
    def pre_buffer(self) -> Optional[timedelta]:
        """Gets the preBuffer property"""
        return self.properties.get("preBuffer", None)

    @property
    def price(self) -> Optional[float]:
        """Gets the price property"""
        return self.properties.get("price", None)

    @property
    def price_type(self) -> BookingPriceType:
        """Gets the priceType property"""
        from office365.booking.pricetype import BookingPriceType

        return self.properties.get("priceType", BookingPriceType.undefined)

    @property
    def reminders(self) -> ClientValueCollection[BookingReminder]:
        """Gets the reminders property"""
        from office365.booking.reminder import BookingReminder

        return self.properties.get("reminders", ClientValueCollection[BookingReminder](BookingReminder))

    @property
    def self_service_appointment_id(self) -> Optional[str]:
        """Gets the selfServiceAppointmentId property"""
        return self.properties.get("selfServiceAppointmentId", None)

    @property
    def service_id(self) -> Optional[str]:
        """Gets the serviceId property"""
        return self.properties.get("serviceId", None)

    @property
    def service_location(self) -> Location:
        """Gets the serviceLocation property"""
        from office365.outlook.mail.location import Location

        return self.properties.get("serviceLocation", Location())

    @property
    def service_name(self) -> Optional[str]:
        """Gets the serviceName property"""
        return self.properties.get("serviceName", None)

    @property
    def service_notes(self) -> Optional[str]:
        """Gets the serviceNotes property"""
        return self.properties.get("serviceNotes", None)

    @property
    def sms_notifications_enabled(self) -> Optional[bool]:
        """Gets the smsNotificationsEnabled property"""
        return self.properties.get("smsNotificationsEnabled", None)

    @property
    def staff_member_ids(self) -> StringCollection:
        """Gets the staffMemberIds property"""
        return self.properties.get("staffMemberIds", StringCollection())

    @property
    def start_date_time(self) -> DateTimeTimeZone:
        """Gets the startDateTime property"""
        from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone

        return self.properties.get("startDateTime", DateTimeTimeZone())

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingAppointment"
