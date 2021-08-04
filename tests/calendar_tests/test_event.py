from datetime import datetime, timedelta

from office365.outlook.calendar.event import Event
from tests import test_user_principal_name
from tests.graph_case import GraphTestCase


class TestOutlookEvent(GraphTestCase):
    target_event = None  # type: Event

    def test2_create_event(self):
        new_event = self.client.me.events.add()  # type: Event
        new_event.subject = "Let's go for lunch"
        new_event.body = "Does mid month work for you?"
        new_event.start = datetime.utcnow() + timedelta(days=1)
        new_event.end = datetime.utcnow() + timedelta(days=1) + timedelta(hours=1)
        new_event.attendees = [test_user_principal_name]
        self.client.execute_query()
        self.assertIsNotNone(new_event.id)
        self.__class__.target_event = new_event

    def test3_list_my_events(self):
        events = self.client.me.events.get().execute_query()
        self.assertGreaterEqual(len(events), 1)

    def test4_update_event(self):
        event = self.__class__.target_event
        event.subject = "Let's go for lunch (updated)"
        event.update().execute_query()

    def test5_delete_event(self):
        event_to_delete = self.__class__.target_event
        event_to_delete.delete_object().execute_query()
        # verify
        events = self.client.me.events.get().execute_query()
        results = [e for e in events if e.id == event_to_delete.id]
        self.assertEqual(len(results), 0)
