from typing import Optional

from office365.entity import Entity


class BookingService(Entity):
    """
    Represents information about a particular service provided by a bookingBusiness, such as the service name,
    price, and the staff that usually provides such service.
    """

    @property
    def additional_information(self):
        # type: () -> Optional[str]
        """Additional information that is sent to the customer when an appointment is confirmed."""
        return self.properties.get("additionalInformation", None)
