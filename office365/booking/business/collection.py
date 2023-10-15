from office365.booking.business.business import BookingBusiness
from office365.entity_collection import EntityCollection


class BookingBusinessCollection(EntityCollection[BookingBusiness]):
    """"""

    def __init__(self, context, resource_path=None):
        super(BookingBusinessCollection, self).__init__(
            context, BookingBusiness, resource_path
        )

    def add(self, display_name):
        """
        Create a new Microsoft Bookings business in a tenant.
        :param str display_name: The business display name.
        """
        props = {
            "displayName": display_name,
        }
        return super(BookingBusinessCollection, self).add(**props)
