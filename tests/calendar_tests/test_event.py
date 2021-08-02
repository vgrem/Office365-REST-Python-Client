from datetime import datetime, timedelta

from office365.calendar.event import Event
from tests import test_user_principal_name
from tests.graph_case import GraphTestCase


class TestOutlookEvent(GraphTestCase):
    target_event = None  # type: Event

    def test2_create_event(self):
        start_time = datetime.utcnow() + timedelta(days=1)
        end_time = start_time + timedelta(hours=1)
        new_event = self.client.me.events.add("Let's go for lunch",
                                              "Does mid month work for you?",
                                              start_time,
                                              end_time,
                                              [test_user_principal_name]).execute_query()
        self.assertIsNotNone(new_event.id)
        self.__class__.target_event = new_event

    def test3_list_my_events(self):
        events = self.client.me.events.get().execute_query()
        self.assertGreaterEqual(len(events), 1)

    def test4_update_event(self):
        event = self.__class__.target_event
        event.set_property("subject", "Let's go for lunch (updated)")
        event.update().execute_query()

    def test5_delete_event(self):
        event_to_delete = self.__class__.target_event
        event_to_delete.delete_object().execute_query()
        # verify
        events = self.client.me.events.get().execute_query()
        results = [e for e in events if e.id == event_to_delete.id]
        self.assertEqual(len(results), 0)
