from office365.outlook.mail.messages.rules.actions import MessageRuleActions
from office365.outlook.mail.messages.rules.rule import MessageRule
from office365.outlook.mail.recipient import Recipient
from tests.graph_case import GraphTestCase


class TestMessageRules(GraphTestCase):
    target_message_rule = None  # type: MessageRule

    def test1_create_rule(self):
        actions = MessageRuleActions(
            forward_to=[Recipient.from_email("AlexW@contoso.com")],
            stop_processing_rules=True,
        )
        message_rules = (
            self.client.me.mail_folders["inbox"]
            .message_rules.add("From partner", 2, actions)
            .execute_query()
        )
        self.assertIsNotNone(message_rules.resource_path)

    def test2_list_rules(self):
        message_rules = (
            self.client.me.mail_folders["inbox"].message_rules.get().execute_query()
        )
        self.assertIsNotNone(message_rules.resource_path)
