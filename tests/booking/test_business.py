from office365.booking.business.business import BookingBusiness
from tests.decorators import requires_delegated_permission
from tests.graph_case import GraphTestCase


class TestBusiness(GraphTestCase):
    business = None  # type: BookingBusiness

    @requires_delegated_permission(
        "Bookings.Read.All",
        "Bookings.Manage.All",
        "Bookings.ReadWrite.All",
        "BookingsAppointment.ReadWrite.All",
    )
    def test1_list_booking_business(self):
        result = self.client.solutions.booking_businesses.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated_permission("Bookings.Manage.All")
    def test2_create_booking_business(self):
        result = self.client.solutions.booking_businesses.add(
            "Fourth Coffee"
        ).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.business = result

    @requires_delegated_permission(
        "Bookings.Read.All",
        "Bookings.Manage.All",
        "Bookings.ReadWrite.All",
        "BookingsAppointment.ReadWrite.All",
    )
    def test3_ensure_created(self):
        result = self.__class__.business.get().execute_query_retry()
        self.assertIsNotNone(result.resource_path)

    #def test4_get_staff_availability(self):
    #    result = self.__class__.business.get_staff_availability().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    @requires_delegated_permission("Bookings.Manage.All")
    def test5_publish(self):
        result = self.__class__.business.publish().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated_permission("Bookings.Manage.All")
    def test6_delete_booking_business(self):
        self.__class__.business.delete_object().execute_query()
