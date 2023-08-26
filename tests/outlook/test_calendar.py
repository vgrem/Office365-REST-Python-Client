from datetime import datetime, timedelta
from typing import Optional

from office365.outlook.calendar.calendar import Calendar
from office365.outlook.calendar.email_address import EmailAddress
from tests import create_unique_name, test_user_principal_name
from tests.graph_case import GraphTestCase


class TestCalendar(GraphTestCase):
    """Tests for Calendar"""

    cal_name = create_unique_name("Volunteer")
    target_cal = None  # type: Optional[Calendar]

    @classmethod
    def setUpClass(cls):
        super(TestCalendar, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_find_my_meeting_times(self):
        result = self.client.me.find_meeting_times().execute_query()
        self.assertIsNotNone(result.value.meetingTimeSuggestions)

    def test2_get_my_schedule(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=7)
        result = self.client.me.calendar.get_schedule(schedules=[test_user_principal_name],
                                                      start_time=start_time,
                                                      end_time=end_time).execute_query()
        self.assertIsNotNone(result.value)

    def test3_list_my_cal_groups(self):
        cal_groups = self.client.me.calendar_groups.get().execute_query()
        self.assertIsNotNone(cal_groups.resource_path)

    def test4_list_my_cal_permissions(self):
        result = self.client.me.calendar.calendar_permissions.get().execute_query()
        self.assertIsNotNone(result.resource_path)

    def test5_list_my_cal_view(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=14)
        events = self.client.me.get_calendar_view(start_dt=start_time, end_dt=end_time).execute_query()
        self.assertIsNotNone(events.resource_path)

    def test6_get_my_reminder_view(self):
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=14)
        result = self.client.me.get_reminder_view(start_dt=start_time, end_dt=end_time).execute_query()
        self.assertIsNotNone(result.value)

    def test7_list_my_events(self):
        events = self.client.me.calendar.events.get().execute_query()
        self.assertIsNotNone(events.resource_path)

    def test6_get_my_calendars(self):
        cals = self.client.me.calendars.get().execute_query()
        self.assertIsNotNone(cals.resource_path)

    def test8_create_cal(self):
        new_cal = self.client.me.calendars.add(name=self.cal_name).execute_query()
        self.assertIsNotNone(new_cal.resource_path)
        self.__class__.target_cal = new_cal

    def test9_update_cal(self):
        cal_to_update = self.__class__.target_cal
        self.__class__.cal_name = self.cal_name + "_Updated"
        cal_to_update.set_property("name", self.cal_name).update().execute_query()

    def test_10_get_cal(self):
        cal_id = self.__class__.target_cal.id
        cal = self.client.me.calendars[cal_id].select(["name", "owner"]).get().execute_query()
        self.assertEqual(cal.name, self.cal_name)
        self.assertIsInstance(cal.owner, EmailAddress)

    def test_11_delete_cal(self):
        cal_to_del = self.__class__.target_cal
        cal_to_del.delete_object().execute_query()
