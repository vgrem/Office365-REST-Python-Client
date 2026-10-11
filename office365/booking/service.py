from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Optional

from office365.entity import Entity
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection

if TYPE_CHECKING:
    from office365.booking.chedulingpolicy import BookingSchedulingPolicy
    from office365.booking.pricetype import BookingPriceType
    from office365.booking.questionassignment import BookingQuestionAssignment
    from office365.booking.reminder import BookingReminder
    from office365.outlook.mail.location import Location
    from office365.runtime.types.duration import timedelta


class BookingService(Entity):
    """
    Represents information about a particular service provided by a bookingBusiness, such as the service name,
    price, and the staff that usually provides such service.
    """

    @property
    def additional_information(self) -> Optional[str]:
        """Additional information that is sent to the customer when an appointment is confirmed."""
        return self.properties.get("additionalInformation", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def custom_questions(self) -> ClientValueCollection[BookingQuestionAssignment]:
        """Gets the customQuestions property"""
        from office365.booking.questionassignment import BookingQuestionAssignment

        return self.properties.get(
            "customQuestions", ClientValueCollection[BookingQuestionAssignment](BookingQuestionAssignment)
        )

    @property
    def default_duration(self) -> Optional[timedelta]:
        """Gets the defaultDuration property"""
        return self.properties.get("defaultDuration", None)

    @property
    def default_location(self) -> Location:
        """Gets the defaultLocation property"""
        from office365.outlook.mail.location import Location

        return self.properties.get("defaultLocation", Location())

    @property
    def default_price(self) -> Optional[float]:
        """Gets the defaultPrice property"""
        return self.properties.get("defaultPrice", None)

    @property
    def default_price_type(self) -> BookingPriceType:
        """Gets the defaultPriceType property"""
        from office365.booking.pricetype import BookingPriceType

        return self.properties.get("defaultPriceType", BookingPriceType.undefined)

    @property
    def default_reminders(self) -> ClientValueCollection[BookingReminder]:
        """Gets the defaultReminders property"""
        from office365.booking.reminder import BookingReminder

        return self.properties.get("defaultReminders", ClientValueCollection[BookingReminder](BookingReminder))

    @property
    def description(self) -> Optional[str]:
        """Gets the description property"""
        return self.properties.get("description", None)

    @property
    def display_name(self) -> Optional[str]:
        """Gets the displayName property"""
        return self.properties.get("displayName", None)

    @property
    def is_anonymous_join_enabled(self) -> Optional[bool]:
        """Gets the isAnonymousJoinEnabled property"""
        return self.properties.get("isAnonymousJoinEnabled", None)

    @property
    def is_customer_allowed_to_manage_booking(self) -> Optional[bool]:
        """Gets the isCustomerAllowedToManageBooking property"""
        return self.properties.get("isCustomerAllowedToManageBooking", None)

    @property
    def is_hidden_from_customers(self) -> Optional[bool]:
        """Gets the isHiddenFromCustomers property"""
        return self.properties.get("isHiddenFromCustomers", None)

    @property
    def is_location_online(self) -> Optional[bool]:
        """Gets the isLocationOnline property"""
        return self.properties.get("isLocationOnline", None)

    @property
    def language_tag(self) -> Optional[str]:
        """Gets the languageTag property"""
        return self.properties.get("languageTag", None)

    @property
    def last_updated_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def maximum_attendees_count(self) -> Optional[int]:
        """Gets the maximumAttendeesCount property"""
        return self.properties.get("maximumAttendeesCount", None)

    @property
    def notes(self) -> Optional[str]:
        """Gets the notes property"""
        return self.properties.get("notes", None)

    @property
    def post_buffer(self) -> Optional[timedelta]:
        """Gets the postBuffer property"""
        return self.properties.get("postBuffer", None)

    @property
    def pre_buffer(self) -> Optional[timedelta]:
        """Gets the preBuffer property"""
        return self.properties.get("preBuffer", None)

    @property
    def scheduling_policy(self) -> BookingSchedulingPolicy:
        """Gets the schedulingPolicy property"""
        from office365.booking.chedulingpolicy import BookingSchedulingPolicy

        return self.properties.get("schedulingPolicy", BookingSchedulingPolicy())

    @property
    def sms_notifications_enabled(self) -> Optional[bool]:
        """Gets the smsNotificationsEnabled property"""
        return self.properties.get("smsNotificationsEnabled", None)

    @property
    def staff_member_ids(self) -> StringCollection:
        """Gets the staffMemberIds property"""
        return self.properties.get("staffMemberIds", StringCollection())

    @property
    def web_url(self) -> Optional[str]:
        """Gets the webUrl property"""
        return self.properties.get("webUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingService"
