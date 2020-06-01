from tests.outlookservices.outlook_case import OutlookClientTestCase


class TestOutlookMail(OutlookClientTestCase):
    def test1_create_message(self):
        message_payload = {
            "Subject": "Did you see last night's game?",
            "Importance": "Low",
            "Body": {
                "ContentType": "HTML",
                "Content": "They were <b>awesome</b>!"
            },
            "ToRecipients": [
                {
                    "EmailAddress": {
                        "Address": "katiej@a830edad9050849NDA1.onmicrosoft.com"
                    }
                }
            ]
        }

        message = self.client.me.messages.add_from_json(message_payload)
        self.client.execute_query()
        self.assertIsNotNone(message.properties["Id"])

    def test2_get_messages(self):
        messages = self.client.me.messages
        self.client.load(messages)
        self.client.execute_query()
        self.assertGreaterEqual(len(messages), 1)

    def test3_update_message(self):
        results = self.client.me.messages.top(1)
        self.client.load(results)
        self.client.execute_query()
        if len(results) == 1:
            event = results[0]
            self.assertIsNotNone(event.properties["Subject"])
            event.set_property("Subject", "Did you see last night's game?..")
            event.update()
            self.client.execute_query()

    def test4_delete_message(self):
        results = self.client.me.messages.top(1)
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
