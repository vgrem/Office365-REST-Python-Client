from office365.calendar.calendar import Calendar
from office365.calendar.emailAddress import EmailAddress
from tests import create_unique_name
from tests.graph_case import GraphTestCase


class TestCalendar(GraphTestCase):
    """Tests for Calendar"""

    cal_name = create_unique_name("Volunteer")
    target_cal = None  # type: Calendar

    @classmethod
    def setUpClass(cls):
        super(TestCalendar, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_user_calendars(self):
        cals = self.client.me.calendars.get().execute_query()
        self.assertIsNotNone(cals.resource_path)

    def test2_create_calendar(self):
        new_cal = self.client.me.calendars.add(self.cal_name).execute_query()
        self.assertIsNotNone(new_cal.resource_path)
        self.__class__.target_cal = new_cal

    def test3_update_calendar(self):
        cal_to_update = self.__class__.target_cal
        self.__class__.cal_name = self.cal_name + "_Updated"
        cal_to_update.set_property("name", self.cal_name).update().execute_query()

    def test4_get_calendar(self):
        cal_id = self.__class__.target_cal.id
        cal = self.client.me.calendars[cal_id].select(["name", "owner"]).get().execute_query()
        self.assertEqual(cal.name, self.cal_name)
        # self.assertIsInstance(cal.owner, EmailAddress)

    def test5_delete_calendar(self):
        cal_to_del = self.__class__.target_cal
        cal_to_del.delete_object().execute_query()
