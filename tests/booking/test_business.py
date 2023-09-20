from office365.booking.business.business import BookingBusiness
from tests.graph_case import GraphTestCase


class TestBusiness(GraphTestCase):

    business = None  # type: BookingBusiness

    def test1_list_booking_business(self):
        result = self.client.solutions.booking_businesses.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test2_create_booking_business(self):
        result = self.client.solutions.booking_businesses.add("Fourth Coffee").execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.business = result

    #def test3_get_staff_availability(self):
    #    result = self.__class__.business.get_staff_availability().execute_query()
    #    self.assertIsNotNone(result.resource_path)

    def test4_delete_booking_business(self):
        self.__class__.business.delete_object().execute_query()
