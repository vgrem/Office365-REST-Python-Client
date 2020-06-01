from tests.outlookservices.outlook_case import OutlookClientTestCase


class TestOutlookCalendar(OutlookClientTestCase):
    def test1_create_event(self):
        event_payload = {
            "Subject": "Discuss the Calendar REST API",
            "Body": {
                "ContentType": "HTML",
                "Content": "I think it will meet our requirements!"
            },
            "Start": "2014-02-02T18:00:00-08:00",
            "StartTimeZone": "Pacific Standard Time",
            "End": "2014-02-02T19:00:00-08:00",
            "EndTimeZone": "Pacific Standard Time",
            "Attendees": [
                {
                    "EmailAddress": {
                        "Address": "janets@a830edad9050849NDA1.onmicrosoft.com",
                        "Name": "Janet Schorr"
                    },
                    "Type": "Required"
                }
            ]
        }

        event = self.client.me.events.add_from_json(event_payload)
        self.client.execute_query()
        self.assertIsNotNone(event.properties["Id"])

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
            self.assertIsNotNone(event.properties["Subject"])
            event.set_property("Subject", "Discuss the Calendar REST API (updated)")
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
            results = [e for e in events if e.properties["Id"] == event.properties["Id"]]
            self.assertEqual(len(results), 0)
