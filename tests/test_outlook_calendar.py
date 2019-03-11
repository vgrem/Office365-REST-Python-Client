from tests.outlook_client_case import OutlookClientTestCase


class TestOutlookCalendar(OutlookClientTestCase):
    def test1_create_event(self):
        event_payload = {
            "subject": "Let's go for lunch",
            "body": {
                "contentType": "HTML",
                "content": "Does late morning work for you?"
            },
            "start": {
                "dateTime": "2017-04-15T12:00:00",
                "timeZone": "Pacific Standard Time"
            },
            "end": {
                "dateTime": "2017-04-15T14:00:00",
                "timeZone": "Pacific Standard Time"
            },
            "location": {
                "displayName": "Harry's Bar"
            },
            "attendees": [
                {
                    "emailAddress": {
                        "address": "samanthab@contoso.onmicrosoft.com",
                        "name": "Samantha Booth"
                    },
                    "type": "required"
                }
            ]
        }

        event = self.client.me.events.add_from_json(event_payload)
        self.client.execute_query()
        self.assertIsNotNone(event.properties["id"])

    def test2_get_events(self):
        events = self.client.me.events
        self.client.load(events)
        self.client.execute_query()
        self.assertGreaterEqual(len(events), 1)

    def test3_update_event(self):
        results = self.client.me.events.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            event = results[0]
            self.assertIsNotNone(event.properties["subject"])
            event.set_property("subject", "Discuss the Calendar REST API (updated)")
            event.update()
            self.client.execute_query()

    def test4_delete_event(self):
        results = self.client.me.events.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            event = results[0]
            event.delete_object()
            self.client.execute_query()
            # verify
            events = self.client.me.events
            self.client.load(events)
            self.client.execute_query()
            results = [e for e in events if e.properties["id"] == event.properties["id"]]
            self.assertEqual(len(results), 0)
