from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from typing_extensions import Self

from office365.booking.appointment import BookingAppointment
from office365.booking.custom_question import BookingCustomQuestion
from office365.booking.customers.base import BookingCustomerBase
from office365.booking.service import BookingService
from office365.booking.staff.availability_item import StaffAvailabilityItem
from office365.booking.staff.member_base import BookingStaffMemberBase
from office365.booking.work_hours import BookingWorkHours
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.outlook.mail.physical_address import PhysicalAddress
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.types.odata_property import odata

if TYPE_CHECKING:
    from office365.booking.chedulingpolicy import BookingSchedulingPolicy
    from office365.booking.pagesettings import BookingPageSettings


class BookingBusiness(Entity):
    """Represents a business in Microsoft Bookings. This is the top level object in the Microsoft Bookings API.
    It contains business information and related business objects such as appointments, customers, services,
    and staff members."""

    def get_staff_availability(
        self,
        staff_ids: Optional[List[str]] = None,
        start_datetime: Optional[datetime] = None,
        end_datetime: Optional[datetime] = None,
    ) -> ClientResult[ClientValueCollection[StaffAvailabilityItem]]:
        """Get the availability information of staff members of a Microsoft Bookings calendar.

        Args:
            staff_ids (list[str]): The list of staff IDs
            start_datetime (datetime.datetime):
            end_datetime (datetime.datetime):
        """
        return_type = ClientResult(self.context, ClientValueCollection(StaffAvailabilityItem))
        payload = {
            "staffIds": staff_ids,
            "startDateTime": start_datetime,
            "endDateTime": end_datetime,
        }
        qry = ServiceOperationQuery(self, "getStaffAvailability", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def publish(self) -> Self:
        """
        Make the scheduling page of a business available to external customers.

        Set the isPublished property to true, and the publicUrl property to the URL of the scheduling page.
        """
        qry = ServiceOperationQuery(
            self,
            "publish",
        )
        self.context.add_query(qry)
        return self

    @property
    def address(self) -> PhysicalAddress:
        """
        The street address of the business. The address property, together with phone and webSiteUrl, appear in the
        footer of a business scheduling page. The attribute type of physicalAddress is not supported in v1.0.
        Internally we map the addresses to the type others.
        """
        return self.properties.get("address", PhysicalAddress())

    @odata(name="businessHours")
    @property
    def business_hours(self) -> ClientValueCollection[BookingWorkHours]:
        """The hours of operation for the business."""
        return self.properties.get("businessHours", ClientValueCollection(BookingWorkHours))

    @property
    def display_name(self) -> Optional[str]:
        """
        The name of the business, which interfaces with customers. This name appears at the top of the business
        scheduling page.
        """
        return self.properties.get("displayName", None)

    @property
    def appointments(self) -> EntityCollection[BookingAppointment]:
        """All the appointments of this business. Read-only. Nullable."""
        return self.properties.get(
            "appointments",
            EntityCollection(
                self.context,
                BookingAppointment,
                ResourcePath("appointments", self.resource_path),
            ),
        )

    @odata(name="calendarView")
    @property
    def calendar_view(self) -> EntityCollection[BookingAppointment]:
        """The set of appointments of this business in a specified date range. Read-only. Nullable."""
        return self.properties.get(
            "calendarView",
            EntityCollection(
                self.context,
                BookingAppointment,
                ResourcePath("calendarView", self.resource_path),
            ),
        )

    @property
    def customers(self) -> EntityCollection[BookingCustomerBase]:
        """All the customers of this business. Read-only. Nullable."""
        return self.properties.get(
            "customers",
            EntityCollection(
                self.context,
                BookingCustomerBase,
                ResourcePath("customers", self.resource_path),
            ),
        )

    @odata(name="customQuestions")
    @property
    def custom_questions(self) -> EntityCollection[BookingCustomQuestion]:
        """All the services offered by this business. Read-only. Nullable."""
        return self.properties.get(
            "customQuestions",
            EntityCollection(
                self.context,
                BookingCustomQuestion,
                ResourcePath("customQuestions", self.resource_path),
            ),
        )

    @property
    def services(self) -> EntityCollection[BookingService]:
        """All the services offered by this business. Read-only. Nullable."""
        return self.properties.get(
            "services",
            EntityCollection(
                self.context,
                BookingService,
                ResourcePath("services", self.resource_path),
            ),
        )

    @odata(name="staffMembers")
    @property
    def staff_members(self) -> EntityCollection[BookingStaffMemberBase]:
        """The collection of open extensions defined for the message. Nullable."""
        return self.properties.get(
            "staffMembers",
            EntityCollection(
                self.context,
                BookingStaffMemberBase,
                ResourcePath("staffMembers", self.resource_path),
            ),
        )

    @property
    def booking_page_settings(self) -> BookingPageSettings:
        """Gets the bookingPageSettings property"""
        from office365.booking.pagesettings import BookingPageSettings

        return self.properties.get("bookingPageSettings", BookingPageSettings())

    @property
    def business_type(self) -> Optional[str]:
        """Gets the businessType property"""
        return self.properties.get("businessType", None)

    @property
    def created_date_time(self) -> Optional[datetime]:
        """Gets the createdDateTime property"""
        return self.properties.get("createdDateTime", datetime.min)

    @property
    def default_currency_iso(self) -> Optional[str]:
        """Gets the defaultCurrencyIso property"""
        return self.properties.get("defaultCurrencyIso", None)

    @property
    def email(self) -> Optional[str]:
        """Gets the email property"""
        return self.properties.get("email", None)

    @property
    def is_published(self) -> Optional[bool]:
        """Gets the isPublished property"""
        return self.properties.get("isPublished", None)

    @property
    def language_tag(self) -> Optional[str]:
        """Gets the languageTag property"""
        return self.properties.get("languageTag", None)

    @property
    def last_updated_date_time(self) -> Optional[datetime]:
        """Gets the lastUpdatedDateTime property"""
        return self.properties.get("lastUpdatedDateTime", datetime.min)

    @property
    def phone(self) -> Optional[str]:
        """Gets the phone property"""
        return self.properties.get("phone", None)

    @property
    def public_url(self) -> Optional[str]:
        """Gets the publicUrl property"""
        return self.properties.get("publicUrl", None)

    @property
    def scheduling_policy(self) -> BookingSchedulingPolicy:
        """Gets the schedulingPolicy property"""
        from office365.booking.chedulingpolicy import BookingSchedulingPolicy

        return self.properties.get("schedulingPolicy", BookingSchedulingPolicy())

    @property
    def web_site_url(self) -> Optional[str]:
        """Gets the webSiteUrl property"""
        return self.properties.get("webSiteUrl", None)

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.BookingBusiness"
