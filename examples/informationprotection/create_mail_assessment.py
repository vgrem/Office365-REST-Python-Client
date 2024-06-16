"""
Create a mail assessment request

"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
messages = client.me.messages.get().filter("isDraft eq false").top(1).execute_query()
result = client.information_protection.create_mail_assessment(
    messages[0]
).execute_query()
print(result)
