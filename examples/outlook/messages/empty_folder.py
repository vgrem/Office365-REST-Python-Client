"""
Empties the mail folder

"""
from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)
client.me.mail_folders["Inbox"].empty().execute_query()
print("Inbox has been emptied")
