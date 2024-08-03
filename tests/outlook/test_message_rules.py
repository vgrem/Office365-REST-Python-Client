from office365.outlook.mail.messages.rules.rule import MessageRule
from tests.graph_case import GraphTestCase


class TestMessageRules(GraphTestCase):
    target_message_rule = None  # type: MessageRule

    def test1_list_inbox_rules(self):
        message_rules = (
            self.client.me.mail_folders["inbox"].message_rules.get().execute_query()
        )
        self.assertIsNotNone(message_rules.resource_path)
