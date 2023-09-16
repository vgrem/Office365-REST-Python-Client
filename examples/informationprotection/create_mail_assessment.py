"""
Create a mail assessment request

"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
messages = client.me.messages.get().filter("isDraft eq false").top(1).execute_query()
result = client.information_protection.create_mail_assessment(messages[0]).execute_query()
print(result)
