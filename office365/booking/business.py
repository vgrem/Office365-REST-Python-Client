from office365.booking.work_hours import BookingWorkHours
from office365.entity import Entity
from office365.outlook.mail.physical_address import PhysicalAddress
from office365.runtime.client_value_collection import ClientValueCollection


class BookingBusiness(Entity):
    """Represents a business in Microsoft Bookings. This is the top level object in the Microsoft Bookings API.
    It contains business information and related business objects such as appointments, customers, services,
    and staff members."""

    @property
    def address(self):
        """
        The street address of the business. The address property, together with phone and webSiteUrl, appear in the
        footer of a business scheduling page. The attribute type of physicalAddress is not supported in v1.0.
        Internally we map the addresses to the type others.
        """
        return self.properties.get("address", PhysicalAddress())

    @property
    def business_hours(self):
        """
        The hours of operation for the business.
        """
        return self.properties.get("businessHours", ClientValueCollection(BookingWorkHours))
