"""
Demonstrates how to send a change notification when the user receives a new mail.

https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0
"""
import datetime

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

existing_subscriptions = client.subscriptions.get().execute_query()

expires = datetime.datetime.now() + datetime.timedelta(hours=120)
notification_url = "https://webhook.azurewebsites.net/api/send/myNotifyClient"
subscription = client.subscriptions.add(
    "created",
    notification_url,
    client.me.mail_folders["Inbox"].messages.resource_path,
    expires,
).execute_query()
print(subscription)
